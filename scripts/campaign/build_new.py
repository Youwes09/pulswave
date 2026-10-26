import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from pulswave import build

B = os.environ.get("BOXES", os.path.expanduser("~/PULSWAVE/cases/boxes"))


def phase(f, duty, anchor, t, end):
    """Pulse windows of a train that started at `anchor`, clipped to start no earlier than the restart time t."""
    out, k = [], 0
    while True:
        s = anchor + k / f
        e = s + duty / f
        k += 1
        if s >= end - 1e-12:
            return tuple(out)
        if e > t + 1e-12:
            out.append((max(s, t), e - max(s, t)))


OFF_CROP = ((0.0, 5e-5),)
JOBS = {
    "large_f80k_rep": ("large_f80k_long", "0.000125", dict(end=2e-4, jet_windows=phase(80e3, 0.5, 120e-6, 125e-6, 2e-4))),
    "box_large_rep": ("box_large", "0.000125", dict(end=1.65e-4)),
    "crop_off_fric": ("crop_grid", "2e-05", dict(end=9e-5, jet_windows=OFF_CROP, wall="rebound; e 0.3; mu 0.5")),
    "crop_off_stick": ("crop_grid", "2e-05", dict(end=9e-5, jet_windows=OFF_CROP, wall="stick")),
    "large_f20k_200": ("large_f20k", "0.000145", dict(end=2e-4, jet_windows=phase(20e3, 0.5, 70e-6, 145e-6, 2e-4))),
    "large_f40k_200": ("large_f40k", "0.000145", dict(end=2e-4, jet_windows=phase(40e3, 0.5, 70e-6, 145e-6, 2e-4))),
    "large_f30k_200": ("large_f30k", "0.000145", dict(end=2e-4, jet_windows=phase(30e3, 0.5, 70e-6, 145e-6, 2e-4))),
    "large_off_hr": ("box_large_200", "0.000165", dict(end=1.95e-4, write=5e-7, jet_windows=((0.0, 165e-6),))),
    "crop_d25_120k": ("crop_grid", "5e-05", dict(end=9e-5, jet_windows=build.pulse_windows(120e3, 0.25, 50e-6, 90e-6))),
    "crop_d375_100k": ("crop_grid", "5e-05", dict(end=9e-5, jet_windows=build.pulse_windows(100e3, 0.375, 50e-6, 90e-6))),
    "crop_f80k_130": ("crop_f80k", "9e-05", dict(end=1.3e-4, jet_windows=phase(80e3, 0.5, 50e-6, 90e-6, 1.3e-4))),
    "crop_off_np1": ("crop_grid", "2e-05", dict(end=9e-5, jet_windows=OFF_CROP)),
    "crop_off_20": ("crop_grid", "2e-05", dict(end=9e-5, jet_windows=OFF_CROP)),
}


def dense_parcels(case):
    """First build of crop_off_np1: ten times the freestream parcels and four times the jet's. It overflowed the injector's
    int32 parcel rate; the run used the hand-edited 3x/4x set-up described in README.md."""
    path = os.path.join(case, "constant", "sprayCloudProperties")
    text = open(path).read()

    def fix(m):
        block = m.group(0).replace("nParticle       10;", "nParticle       1;")
        return re.sub(r"parcelsPerSecond (\S+);", lambda p: f"parcelsPerSecond {float(p.group(1)) * 10:.6g};", block)

    text, n = re.subn(r"\n        (inflow|upper)\n        \{.*?\n        \}", fix, text, flags=re.S)
    assert n == 2
    jet = lambda m: re.sub(r"parcelsPerSecond (\S+);", lambda p: f"parcelsPerSecond {float(p.group(1)) * 4:.6g};", m.group(0))
    text, n = re.subn(r"\n        jet\w*\n        \{.*?\n        \}", jet, text, flags=re.S)
    assert n == 1
    open(path, "w").write(text)


for name in sys.argv[1:] or [j for j in JOBS if j != "large_off_hr"]:
    src, t, changes = JOBS[name]
    s = build.branch(os.path.join(B, src), os.path.join(B, name), t, **changes)
    if name == "crop_off_np1":
        dense_parcels(os.path.join(B, name))
    print(f"{name}: from {src} at {float(t) * 1e6:g} us to {s.end * 1e6:g} us, windows {len(s.jet_windows)}")
