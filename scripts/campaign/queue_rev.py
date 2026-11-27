"""Revision run queue: keeps the host's cores busy with the jobs in queue_rev.json, without supervision.

Each job: {"name", "ranks", "needs": [case, time] or [case, "End"] or null}. A job is built (scripts/campaign/build_revision.py)
when its parent condition is met and launched when enough cores are free. Before launch it must pass the injector audit;
three minutes after launch its log is checked for errors and for steps. Every action goes to ~/queue_rev.log.
Cancel: touch ~/queue.cancel. Edit the job list by writing a new queue_rev.json; it is re-read every cycle.
Usage: nohup setsid python3 scripts/campaign/queue_rev.py > /dev/null 2>&1 &
"""
import json, os, re, subprocess, time

HOME = os.path.expanduser("~")
B = os.path.join(HOME, "PULSWAVE", "cases", "boxes")
REPO = os.path.join(HOME, "pulswave_repo")
BIN = os.path.join(HOME, "solver", "bin", "rhophi", "detonationFoam_V3.1")
CORES = os.cpu_count()
LOG = os.path.join(HOME, "queue_rev.log")
STATE = os.path.join(HOME, "queue_rev.state.json")


def log(msg):
    with open(LOG, "a") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S UTC ", time.gmtime()) + msg + "\n")


def mpiruns():
    """(cwd, ranks) of every running mpirun ... -parallel (cmdline ends with a NUL, so drop empty fields)."""
    out = []
    for pid in os.listdir("/proc"):
        if pid.isdigit():
            try:
                cmd = [c for c in open(f"/proc/{pid}/cmdline").read().split("\0") if c]
                cwd = os.readlink(f"/proc/{pid}/cwd")
            except OSError:
                continue
            if len(cmd) > 4 and os.path.basename(cmd[0]) == "mpirun" and "-np" in cmd and cmd[-1] == "-parallel":
                out.append((cwd, int(cmd[cmd.index("-np") + 1])))
    return out


def used_cores():
    return sum(n for _, n in mpiruns())


def running(case):
    return any(os.path.basename(cwd) == case for cwd, _ in mpiruns())


def done(case):
    p = os.path.join(B, case, "log.run")
    return os.path.exists(p) and re.search(r"^End\s*$", open(p, errors="ignore").read(), re.M) is not None


def ready(needs):
    if not needs:
        return True
    case, when = needs
    return done(case) if when == "End" else os.path.isdir(os.path.join(B, case, "processor0", when))


def audit_ok(case):
    saves = [t for t in os.listdir(os.path.join(B, case, "processor0")) if re.fullmatch(r"[0-9.e+-]+", t) and t != "0"]
    if not saves:  # a fresh case from uniform freestream has no injector state to audit
        return True, "fresh case"
    out = subprocess.run(["python3", "scripts/campaign/audit.py", case], cwd=REPO, capture_output=True, text=True,
                         env={**os.environ, "BOXES": B}).stdout
    good = ("identical across procs: True, missing on 0" in out and "STALE" not in out and "NO SAVED STATE" not in out
            and re.search(r"procs (\d+) decomp \1\b", out))
    return bool(good), out


import sys
if "--count" in sys.argv:
    print("cores in use:", used_cores(), [(os.path.basename(c), n) for c, n in mpiruns()][:40]); sys.exit()
state = json.load(open(STATE)) if os.path.exists(STATE) else {}
log(f"queue started, {CORES} cores")
while not os.path.exists(os.path.join(HOME, "queue.cancel")):
    jobs = json.load(open(os.path.join(REPO, "scripts", "campaign", "queue_rev.json")))
    for j in jobs:
        name, st = j["name"], state.get(j["name"], "pending")
        if st in ("launched", "running") and not running(name) and time.time() - state.get(name + ".t", 0) > 60:
            if done(name):
                state[name] = "done"; log(f"{name} finished")
            else:
                state[name] = "error"; log(f"ERROR {name} stopped without End (crash?): see log.run")
            continue
        if st == "running":
            continue
        if st == "launched":
            # post-launch check after three minutes
            lr = os.path.join(B, name, "log.run")
            if os.path.exists(lr) and time.time() - os.path.getmtime(os.path.join(B, name, "system", "controlDict")) > 0:
                txt = open(lr, errors="ignore").read()
                if re.search(r"FOAM FATAL|Segmentation|floating point exception\)", txt):
                    log(f"ERROR in {name}: see log.run"); state[name] = "error"
                elif time.time() - state.get(name + ".t", time.time()) > 180:
                    steps = len(re.findall(r"^Time = ", txt, re.M))
                    log(f"{name}: {steps} steps after 3 min" + ("" if steps > 3 else " (SLOW OR STUCK)")); state[name] = "running"
            continue
        if st != "pending" or not ready(j.get("needs")):
            continue
        if running(name) or done(name):
            state[name] = "running" if running(name) else "done"
            log(f"{name} already {state[name]}, not launched again")
            continue
        if not os.path.isdir(os.path.join(B, name)):
            r = subprocess.run(["python3", "scripts/campaign/build_revision.py", name], cwd=REPO, capture_output=True, text=True)
            if r.returncode:
                log(f"build failed {name}: {r.stderr.strip()[-300:]}"); state[name] = "build-failed"; continue
            log(f"built {r.stdout.strip()[-200:]}")
        if used_cores() + j["ranks"] > CORES:
            break  # strict priority: wait for cores rather than let smaller, later jobs take them
        ok, out = audit_ok(name)
        if not ok:
            log(f"audit failed, held {name}:\n{out[-600:]}"); state[name] = "audit-failed"; continue
        subprocess.run([os.path.join(HOME, "launch.sh"), os.path.join(B, name), BIN], capture_output=True)
        state[name], state[name + ".t"] = "launched", time.time()
        log(f"launched {name} on {j['ranks']} ranks (cores in use before: {used_cores()})")
        time.sleep(20)
    json.dump(state, open(STATE, "w"), indent=1)
    time.sleep(60)
log("cancelled")
