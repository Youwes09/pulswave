import glob, json, os, re, sys
B = os.environ.get("BOXES", os.path.expanduser("~/PULSWAVE/cases/boxes"))
def blocks(text, key):
    i = text.index(key); depth = 0; out = {}; name = None
    body = text[text.index("{", i) + 1:]
    tokens = re.finditer(r"(\w+)\s*\{|\}|(\w+)\s+([^;{}]+);", body)
    stack = []
    for m in tokens:
        if m.group(1): stack.append(m.group(1)); 
        elif m.group(0) == "}":
            if not stack: break
            stack.pop()
        elif len(stack) == 1: out.setdefault(stack[0], {})[m.group(2)] = m.group(3).strip()
    return out
def val(text, k):
    m = re.search(rf"^{k}\s+([^;]+);", text, re.M); return m.group(1) if m else None
for c in sys.argv[1:]:
    d = os.path.join(B, c); print(f"===== {c}")
    s = json.load(open(f"{d}/setup.json"))
    cd = open(f"{d}/system/controlDict").read()
    procs = sorted(glob.glob(f"{d}/processor*"))
    times = sorted((t for t in os.listdir(procs[0]) if t[0].isdigit() and t != "0"), key=float)
    t0 = times[0]; tr = float(t0)
    print(f"  setup: jet_u={s['jet_u']} jet_faces={s['jet_faces']} jet_d={s['jet_d']} jet_scale={s.get('jet_scale')} gas_wall={s.get('gas_wall')} windows={len(s['jet_windows'])} end={s['end']} write={s['write']}")
    print(f"  control: startFrom={val(cd,'startFrom')} endTime={val(cd,'endTime')} writeInterval={val(cd,'writeInterval')} | first/last save {t0} / {times[-1]} | procs {len(procs)} decomp {val(open(f'{d}/system/decomposeParDict').read(),'numberOfSubdomains')}")
    sp = open(f"{d}/constant/sprayCloudProperties").read()
    inj = blocks(sp, "injectionModels")
    st = {}
    for p in procs:
        f = f"{p}/{t0}/uniform/lagrangian/sprayCloud/sprayCloudOutputProperties"
        st[p] = blocks(open(f).read(), "injectionModel") if os.path.exists(f) else None
    states = {json.dumps(v, sort_keys=True) for v in st.values()}
    saved = st[procs[0]] or {}
    print(f"  saved injector state at {t0}: {sorted(saved)}  (identical across procs: {len(states)==1}, missing on {sum(v is None for v in st.values())})")
    jets = []
    for n, b in inj.items():
        soi, dur, m = float(b["SOI"]), float(b["duration"]), float(b["massTotal"])
        flag = ""
        ts0 = float(saved[n]["timeStep0"]) if n in saved else None
        if ts0 is not None and ts0 < tr - 1e-12 and soi + dur > ts0: flag = f"  <-- STALE timeStep0 {ts0*1e6:g} us"
        elif soi < tr - 1e-12 and soi + dur > tr - 1e-12 and n not in saved: flag = "  <-- ACTIVE, NO SAVED STATE"
        elif soi < tr - 1e-12 and n not in saved: flag = "  <-- past window, no state (check for dump)"
        if n.startswith("jet"): jets.append((soi, dur, m))
        print(f"    {n:8s} {b.get('type','?'):15s} SOI {soi*1e6:8.3f} us dur {dur*1e6:8.4f} us  rate {m/dur*1e3:8.4f} g/s  pps {b.get('parcelsPerSecond')}{flag}")
    for n in saved:
        if n not in inj: print(f"    (saved injector {n} dropped)")
    if jets:
        on = sum(dt for _, dt, _ in jets); span = max(a + b for a, b, _ in jets) - min(a for a, _, _ in jets)
        print(f"  jet: {len(jets)} windows, on {on*1e6:.3f} us over {span*1e6:.3f} us (duty {on/span:.3f}), total {sum(m for *_, m in jets)*1e9:.2f} ug")
    U = open(f"{procs[0]}/{t0}/U").read()
    for patch in ("lowerWall", "jet"):
        m = re.search(rf"{patch}\s*\{{\s*type\s+(\w+);", U); print(f"  U {patch}: {m.group(1) if m else '-'}", end="")
    print()
    l = f"{d}/log.run"
    if os.path.exists(l):
        txt = open(l, errors="ignore").read()
        steps = re.findall(r"^Time = (\S+)", txt, re.M)
        dts = [float(x) for x in re.findall(r"^deltaT = (\S+)", txt, re.M)]
        adds = [int(x) for x in re.findall(r"injector: jet\w*\s+Added (\d+)", txt)]
        print(f"  log: {len(steps)} steps, now {steps[-1] if steps else '-'}, dt min/last {min(dts) if dts else 0:.3g}/{dts[-1] if dts else 0:.3g}, max jet adds/step {max(adds) if adds else 0}, "
              f"warnings {len(re.findall('(?i)warning', txt))}, nan {len(re.findall(r'(?i)\bnan\b', txt))}, bounding {txt.count('bounding')}, fatal {txt.count('FATAL')}")
        w = re.findall(r"(?i)^.*warning.*$", txt, re.M)
        if w: print("   first warning:", w[0][:150])
