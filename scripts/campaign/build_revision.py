"""Build the revision runs (Nov 2026) on the fixed solver (container/patches) from the original parent states.

Each job in JOBS branches a parent case at a save with pulswave.build.branch; the jobs in SPECIAL need a new mesh or a
clean start. Every case then gets revision_settings.py: ODE tolerances absTol 1e-10, relTol 1e-3, ascii saves every 1 us.
Jet settings match the original runs (their setup.json). Jobs must be named, so a running case is never rebuilt.
Usage (run host): BOXES=~/PULSWAVE/cases/boxes python3 scripts/campaign/build_revision.py job [job ...]
"""
import glob, os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from pulswave import build, foam

B = os.environ.get("BOXES", os.path.expanduser("~/PULSWAVE/cases/boxes"))
HERE = os.path.dirname(os.path.abspath(__file__))
pw = build.pulse_windows
C0, R0 = 50e-6, 70e-6  # branch times: crop, reduced domain

JOBS = {
    # crop (0.2 mm), from crop_grid at 50 us; used only up to 40 us after the change (docs/experiments.md, revision runs)
    "r_crop_cont":      ("crop_grid", "5e-05", dict(end=1.3e-4), {}),
    "r_crop_off":       ("crop_grid", "5e-05", dict(end=1.0e-4, jet_windows=((0.0, C0),)), {}),
    "r_crop_f80k":      ("crop_grid", "5e-05", dict(end=1.3e-4, jet_windows=pw(80e3, 0.5, C0, 1.3e-4)), {}),
    "r_crop_q120k":     ("crop_grid", "5e-05", dict(end=1.0e-4, jet_windows=pw(120e3, 0.25, C0, 1.0e-4)), {}),
    "r_crop_f60k":      ("crop_grid", "5e-05", dict(end=1.3e-4, jet_windows=pw(60e3, 0.5, C0, 1.3e-4)), {}),
    "r_crop_f50k":      ("crop_grid", "5e-05", dict(end=1.3e-4, jet_windows=pw(50e3, 0.5, C0, 1.3e-4)), {}),
    "r_crop_f20k_long": ("crop_grid", "5e-05", dict(end=4.0e-4, jet_windows=pw(20e3, 0.5, C0, 4.0e-4)), {}),
    "r_crop_f40k_d75":  ("crop_grid", "5e-05", dict(end=1.3e-4, jet_windows=pw(40e3, 0.75, C0, 1.3e-4)), {}),
    "r_crop_d375_100k": ("crop_grid", "5e-05", dict(end=1.0e-4, jet_windows=pw(100e3, 0.375, C0, 1.0e-4)), {}),
    "r_crop_q160k":     ("crop_grid", "5e-05", dict(end=1.0e-4, jet_windows=pw(160e3, 0.25, C0, 1.0e-4)), {}),
    "r_crop_q80k":      ("crop_grid", "5e-05", dict(end=1.0e-4, jet_windows=pw(80e3, 0.25, C0, 1.0e-4)), {}),
    "r_crop_cut":       ("crop_grid", "5e-05", dict(end=1.0e-4, jet_windows=((0.0, C0),), drop_wall_liquid=0.0525), {}),
    "r_crop_d1_off":    ("crop_grid_d1", "5e-05", dict(end=1.0e-4, jet_windows=((0.0, C0),)), {}),
    # crop wall treatments: droplet friction, stick and escape walls, no-slip gas wall
    "r_crop_fric":      ("crop_grid", "2e-05", dict(end=1.0e-4, jet_windows=((0.0, C0),), wall="rebound; e 0.3; mu 0.5"), {}),
    "r_crop_stick":     ("crop_grid", "2e-05", dict(end=1.0e-4, jet_windows=((0.0, C0),), wall="stick"), {}),
    "r_crop_esc_cont":  ("crop_grid", "2e-05", dict(end=1.0e-4, wall="escape"), {}),
    "r_crop_esc_off":   ("crop_grid", "2e-05", dict(end=1.0e-4, jet_windows=((0.0, C0),), wall="escape"), {}),
    "r_crop_noslip":    ("crop_grid", "3e-05", dict(end=1.0e-4, jet_windows=((3e-05, 2e-05),), gas_wall="noSlip"), {}),
    # time step and chemistry tolerances: Courant 0.15, and the solver's default ODE tolerances over the hold
    "r_crop_off_co15":  ("crop_grid", "5e-05", dict(end=1.0e-4, jet_windows=((0.0, C0),)), {"maxCo": "0.15"}),
    "r_crop_f80k_co15": ("crop_grid", "5e-05", dict(end=1.0e-4, jet_windows=pw(80e3, 0.5, C0, 1.0e-4)), {"maxCo": "0.15"}),
    "r_crop_off_tolctl": ("crop_grid", "5e-05", dict(end=7.0e-5, jet_windows=((0.0, C0),)), {"tol": ("1e-15", "1e-4")}),
    # crop realizations: restarts from 40 and 45 us, so the droplet models' random sequence restarts at a different time
    "r_crop_off_s45":   ("crop_grid", "4.5e-05", dict(end=1.0e-4, jet_windows=((0.0, C0),)), {}),
    "r_crop_off_s40":   ("crop_grid", "4e-05", dict(end=1.0e-4, jet_windows=((0.0, C0),)), {}),
    "r_crop_f80k_s45":  ("crop_grid", "4.5e-05", dict(end=1.3e-4, jet_windows=((0.0, C0),) + pw(80e3, 0.5, C0, 1.3e-4)), {}),
    "r_crop_f80k_s40":  ("crop_grid", "4e-05", dict(end=1.3e-4, jet_windows=((0.0, C0),) + pw(80e3, 0.5, C0, 1.3e-4)), {}),
    "r_crop_q120k_s45": ("crop_grid", "4.5e-05", dict(end=1.0e-4, jet_windows=((0.0, C0),) + pw(120e3, 0.25, C0, 1.0e-4)), {}),
    "r_crop_q120k_s40": ("crop_grid", "4e-05", dict(end=1.0e-4, jet_windows=((0.0, C0),) + pw(120e3, 0.25, C0, 1.0e-4)), {}),
    # crop grids: 0.15 mm (3-face jet, per-area flux 1.11x nominal) from crop_grid_fine, and 0.1 mm from r_f10_cont, at 50 us
    "r_f15_off":        ("crop_grid_fine", "5e-05", dict(end=1.0e-4, jet_windows=((0.0, C0),)), {}),
    "r_f15_f80k":       ("crop_grid_fine", "5e-05", dict(end=1.3e-4, jet_windows=pw(80e3, 0.5, C0, 1.3e-4)), {}),
    "r_f10_off":        ("r_f10_cont", "5e-05", dict(end=1.0e-4, jet_windows=((0.0, C0),)), {}),
    "r_f10_f80k":       ("r_f10_cont", "5e-05", dict(end=1.3e-4, jet_windows=pw(80e3, 0.5, C0, 1.3e-4)), {}),
    "r_f10_q120k":      ("r_f10_cont", "5e-05", dict(end=1.0e-4, jet_windows=pw(120e3, 0.25, C0, 1.0e-4)), {}),
    "r_f10_f40k":       ("r_f10_cont", "5e-05", dict(end=1.3e-4, jet_windows=pw(40e3, 0.5, C0, 1.3e-4)), {}),
    # reduced domain (0.2 mm), from box_large at 70 us
    "r_box_ref":        ("box_large", "7e-05", dict(end=2.0e-4), {}),
    "r_box_off":        ("box_large", "7e-05", dict(end=2.0e-4, jet_windows=((0.0, R0),)), {}),
    "r_box_dry":        ("box_large", "7e-05", dict(end=1.3e-4, jet_windows=((0.0, R0),), drop_jet_liquid=True), {}),
    "r_box_reon":       ("box_large", "7e-05", dict(end=2.0e-4, jet_windows=((95e-6, 2.0e-4 - 95e-6),)), {}),
    "r_box_f80k":       ("box_large", "7e-05", dict(end=2.0e-4, jet_windows=pw(80e3, 0.5, R0, 2.0e-4)), {}),
    "r_box_f60k":       ("box_large", "7e-05", dict(end=2.0e-4, jet_windows=pw(60e3, 0.5, R0, 2.0e-4)), {}),
    "r_box_f50k":       ("box_large", "7e-05", dict(end=2.0e-4, jet_windows=pw(50e3, 0.5, R0, 2.0e-4)), {}),
    "r_box_f40k":       ("box_large", "7e-05", dict(end=2.0e-4, jet_windows=pw(40e3, 0.5, R0, 2.0e-4)), {}),
    "r_box_f30k":       ("box_large", "7e-05", dict(end=2.0e-4, jet_windows=pw(30e3, 0.5, R0, 2.0e-4)), {}),
    "r_box_f20k":       ("box_large", "7e-05", dict(end=2.0e-4, jet_windows=pw(20e3, 0.5, R0, 2.0e-4)), {}),
    "r_box_q120k":      ("box_large", "7e-05", dict(end=2.0e-4, jet_windows=pw(120e3, 0.25, R0, 2.0e-4)), {}),
    "r_box_half":       ("box_large", "7e-05", dict(end=2.0e-4, jet_u=30.415, jet_windows=((R0, 2.0e-4 - R0),)), {}),
    "r_box_j05":        ("box_large", "7e-05", dict(end=2.0e-4, jet_u=43.01, jet_windows=((R0, 2.0e-4 - R0),)), {}),
    "r_box_cone":       ("box_large", "7e-05", dict(end=2.0e-4, jet_faces=1, jet_windows=((R0, 2.0e-4 - R0),)), {}),
    "r_box_off165":     ("r_box_ref", "0.000165", dict(end=1.95e-4, jet_windows=((0.0, 165e-6),)), {}),
    # extensions to 350 us; the inherited inflow and upper injectors end at 300 us, so they are lengthened (names and state kept)
    "r_box_f80k_ext":   ("r_box_f80k", "0.0002", dict(end=3.5e-4, jet_windows=pw(80e3, 0.5, R0, 3.5e-4)), {"extend_injectors": 3.6e-4}),
    "r_box_ref_ext":    ("r_box_ref", "0.0002", dict(end=3.5e-4), {"extend_injectors": 3.6e-4}),
    "r_box_f20k_ext":   ("r_box_f20k", "0.0002", dict(end=3.5e-4, jet_windows=pw(20e3, 0.5, R0, 3.5e-4)), {"extend_injectors": 3.6e-4}),
    "r_box_f30k_ext":   ("r_box_f30k", "0.0002", dict(end=3.5e-4, jet_windows=pw(30e3, 0.5, R0, 3.5e-4)), {"extend_injectors": 3.6e-4}),
    # perturbed starts: pulsing begins 1-5 us later, from the reference's saves, to test whether the outcome depends on the start
    "r_box_f80k_p71":   ("r_box_ref", "7.1e-05", dict(end=2.0e-4, jet_windows=((0.0, 71e-6),) + pw(80e3, 0.5, 71e-6, 2.0e-4)), {}),
    "r_box_f80k_p73":   ("r_box_ref", "7.3e-05", dict(end=2.0e-4, jet_windows=((0.0, 73e-6),) + pw(80e3, 0.5, 73e-6, 2.0e-4)), {}),
    "r_box_f20k_p75":   ("r_box_ref", "7.5e-05", dict(end=3.5e-4, jet_windows=((0.0, 75e-6),) + pw(20e3, 0.5, 75e-6, 3.5e-4)),
                         {"extend_injectors": 3.6e-4}),
    # default ODE tolerances (1e-15, 1e-4) over the 80 kHz loss: near-wall burning fades from 145 us and the base leaves at 155 us
    "r_box_f80k_tolctl": ("r_box_f80k", "0.00014", dict(end=1.75e-4, jet_windows=pw(80e3, 0.5, R0, 1.75e-4)), {"tol": ("1e-15", "1e-4")}),
    # lowest frequency: 50 us off-time, more than three times the hold after switch-off
    "r_box_f10k":       ("box_large", "7e-05", dict(end=3.0e-4, jet_windows=pw(10e3, 0.5, R0, 3.0e-4)), {}),
    # reduced domain on 0.15 mm (mapped at 70 us by f15box_cont); branched once its base has settled (see experiments.md)
    "r_f15box_f80k":    ("r_f15box_cont", "9e-05", dict(end=2.0e-4, jet_windows=pw(80e3, 0.5, 9e-5, 2.0e-4)), {}),
    # the reduced domain cut to the crop's height, 120 x 25 mm (mapped at 70 us by low_box)
    "r_low_f80k":       ("r_low_cont", "7e-05", dict(end=2.0e-4, jet_windows=pw(80e3, 0.5, R0, 2.0e-4)), {}),
}


def set_maxco(case, co):
    for rel in ("system/controlDict", "constant/sprayCloudProperties"):
        p = os.path.join(case, rel)
        s, n = re.subn(r"^(\s*)maxCo(\s+)\S+;", rf"\g<1>maxCo\g<2>{co};", open(p).read(), flags=re.M)
        assert n >= 1, f"maxCo not found in {p}"
        open(p, "w").write(s)


def settings(dest, write="1e-6"):
    subprocess.run([sys.executable, os.path.join(HERE, "revision_settings.py"), dest, "--reltol", "1e-3", "--write", write],
                   check=True, stdout=subprocess.DEVNULL)


def f10_cont():
    """0.1 mm continuous crop, mapped from the 0.2 mm crop at 35 us (16 ranks); its 50 us save is the branch point."""
    from dataclasses import replace
    sys.argv = sys.argv[:1] + ["crop_fine_off"]  # build_mapped dispatches on argv; only its mapped() is used here
    import importlib.util
    spec = importlib.util.spec_from_file_location("bm", os.path.join(HERE, "build_mapped.py"))
    src = open(os.path.join(HERE, "build_mapped.py")).read().rsplit("\n{", 1)[0]  # drop the dispatch at the end
    ns = {"__file__": os.path.join(HERE, "build_mapped.py")}
    exec(compile(src, "build_mapped.py", "exec"), ns)
    s = replace(build.PRESETS["crop_grid"], dx=1e-4, nproc=16, end=1.3e-4, write=1e-6, jet_windows=())
    dest = os.path.join(B, "r_f10_cont")
    ns["mapped"](os.path.join(B, "crop_grid"), "3.5e-05", dest, s)
    settings(dest)
    print("r_f10_cont: mapped to 0.1 mm at 35 us, continuous to 130 us, 16 ranks")


def full_clean():
    """Full 250 x 100 mm domain, J = 1, from uniform freestream (no mapping), 32 ranks, saves every 5 us."""
    from dataclasses import replace
    dest = os.path.join(B, "r_full_j1")
    s = replace(build.PRESETS["paper_j1"], nproc=32, end=1.5e-4, write=5e-6)
    build.build(s, dest)
    settings(dest, write="5e-6")
    foam = ["apptainer", "exec", os.path.expanduser("~/PULSWAVE/container/detonationfoam.sif")]
    for cmd in (["blockMesh"], ["topoSet"], ["createPatch", "-overwrite"], ["checkMesh"], ["decomposePar", "-force"]):
        with open(os.path.join(dest, "log." + cmd[0]), "w") as f:
            subprocess.run(foam + cmd, cwd=dest, stdout=f, stderr=subprocess.STDOUT, check=True)
    with open(os.path.join(dest, "log.cellCentres"), "w") as f:
        subprocess.run(foam + ["mpirun", "--bind-to", "none", "-np", "32", "postProcess", "-func", "writeCellCentres",
                               "-parallel", "-time", "0"], cwd=dest, stdout=f, stderr=subprocess.STDOUT, check=True)
    print("r_full_j1: full domain from uniform freestream, 32 ranks, to 150 us")


def mapped_box(dest_name, s, t="7e-05", sub=False):
    """Map box_large at t onto the mesh of setup s (finer grid, or the lower 120 x 25 mm part with sub=True) with mapFields,
    droplets relocated by position, injector state carried over; then the revision settings."""
    import shutil
    src, dest = os.path.join(B, "box_large"), os.path.join(B, dest_name)
    bm = open(os.path.join(HERE, "build_mapped.py")).read().rsplit("\n{", 1)[0]
    ns = {"__file__": os.path.join(HERE, "build_mapped.py")}
    exec(compile(bm, "build_mapped.py", "exec"), ns)
    if not sub:
        ns["mapped"](src, t, dest, s)
    else:  # different domain: non-consistent mapping; the top keeps the target's freestream values, as in the crop
        build.build(s, dest)
        for tool in ("blockMesh", "topoSet"):
            ns["sh"](dest, f"log.{tool}", tool)
        ns["sh"](dest, "log.createPatch", "createPatch", "-overwrite")
        ns["sh"](dest, "log.checkMesh", "checkMesh")
        open(os.path.join(dest, "system", "mapFieldsDict"), "w").write(build.header("dictionary", "mapFieldsDict")
            + "patchMap ( inflow inflow lowerWall lowerWall outflow outflow jet jet );\ncuttingPatches ( );\n")
        if not os.path.isdir(os.path.join(src, t)):
            ns["sh"](src, "log.reconstructPar", "reconstructPar", "-time", t)
        # a scratch copy of the source state with the parcels above the target removed (mapFields searches the whole
        # mesh for every parcel it cannot place, which takes hours); the source case itself is never modified
        tmp = os.path.join(B, "zsrc_" + dest_name)
        shutil.rmtree(tmp, ignore_errors=True)
        for sub in ("constant", "system", t):
            shutil.copytree(os.path.join(src, sub), os.path.join(tmp, sub))
        ns["sh"](tmp, "log.cellCentres", "postProcess", "-func", "writeCellCentres", "-time", t)
        os.makedirs(os.path.join(tmp, "0"))
        shutil.move(os.path.join(tmp, t, "C"), os.path.join(tmp, "0", "C"))
        for c in ("Cx", "Cy", "Cz"):
            os.remove(os.path.join(tmp, t, c))
        cloud = os.path.join(tmp, t, "lagrangian", "sprayCloud")
        foam.filter_cloud(cloud, [y < s.ly for _, y in foam.parcel_xy(tmp, cloud)])
        # mapFields maps only fields that already exist in the target, and a new case has only the main species:
        # give every other scalar field of the source a placeholder (from Ydefault) so that it is mapped as well
        shutil.copytree(os.path.join(dest, "0"), os.path.join(dest, t))
        tmpl = open(os.path.join(dest, t, "Ydefault")).read()
        skip = {"Qdot", "rho", "magGradrho", "muEff", "maxp", "Ydefault"}
        for f in os.listdir(os.path.join(tmp, t)):
            fp = os.path.join(tmp, t, f)
            if (os.path.isfile(fp) and f not in skip and not os.path.exists(os.path.join(dest, t, f))
                    and "class       volScalarField;" in open(fp).read(800)):
                open(os.path.join(dest, t, f), "w").write(re.sub(r"object\s+Ydefault;", f"object      {f};", tmpl))
        ns["sh"](dest, "log.mapFields", "mapFields", tmp, "-sourceTime", t)
        mapped_names = set(re.findall(r"interpolating (\w+)", open(os.path.join(dest, "log.mapFields")).read()))
        want = {f for f in os.listdir(os.path.join(tmp, t)) if os.path.isfile(os.path.join(tmp, t, f)) and f not in skip}
        assert want <= mapped_names, f"fields not mapped: {sorted(want - mapped_names)}"
        nmap = len(mapped_names)
        ns["sh"](dest, "log.decomposePar", "decomposePar", "-force", "-time", t)
        ns["sh"](dest, "log.cellCentres", "mpirun", "--bind-to", "none", "-np", str(s.nproc), "postProcess", "-func",
                 "writeCellCentres", "-parallel", "-time", t)
        state = os.path.join(src, "processor0", t, "uniform")
        for pr in glob.glob(os.path.join(dest, "processor*")):
            os.makedirs(os.path.join(pr, "0"), exist_ok=True)
            for c in ("C", "Cx", "Cy", "Cz"):
                shutil.move(os.path.join(pr, t, c), os.path.join(pr, "0", c))
            shutil.rmtree(os.path.join(pr, t, "uniform"), ignore_errors=True)
            shutil.copytree(state, os.path.join(pr, t, "uniform"))
        shutil.rmtree(os.path.join(dest, t))
        print(f"mapped {nmap} fields")
        a = [q for q in foam.parcels(src, t) if q[1] < s.ly]
        b = foam.parcels(dest, t)
        print(f"parcels below y = {s.ly * 1e3:g} mm {len(a)} -> {len(b)}, liquid {sum(q[3] for q in a) * 1e9:.1f} -> {sum(q[3] for q in b) * 1e9:.1f} ug")
        assert abs(len(b) / len(a) - 1) < 0.01 and abs(sum(q[3] for q in b) / sum(q[3] for q in a) - 1) < 0.01
        shutil.rmtree(tmp)
    settings(dest)


def f15box_cont():
    from dataclasses import replace
    s = replace(build.PRESETS["box_large"], dx=0.15e-3, nproc=24, end=2.0e-4, write=1e-6, jet_windows=())
    mapped_box("r_f15box_cont", s)
    print("r_f15box_cont: reduced domain mapped to 0.15 mm at 70 us, continuous to 200 us, 24 ranks")


def low_box(name, windows):
    from dataclasses import replace
    s = replace(build.PRESETS["box_large"], ly=0.025, nproc=8, end=2.0e-4, write=1e-6, jet_windows=windows)
    mapped_box(name, s, sub=True)
    print(f"{name}: lower 120 x 25 mm of the reduced domain, mapped at 70 us, to 200 us, {len(windows) or 'continuous'} windows")


def extend_injectors(case, duration):
    """Lengthen every injector whose window ends before `duration` and that started at t = 0 (inflow, upper, continuous jet),
    scaling its massTotal with the duration so the rate is unchanged. Names and saved state are kept."""
    p = os.path.join(case, "constant", "sprayCloudProperties")
    text = open(p).read()

    def fix(m):
        b = m.group(0)
        if not all(re.search(rf"{k}\s+\S+;", b) for k in ("SOI", "duration", "massTotal")):
            return b  # not an injector block
        soi, dur, mass = (float(re.search(rf"{k}\s+(\S+);", b).group(1)) for k in ("SOI", "duration", "massTotal"))
        if soi != 0.0 or dur >= duration:
            return b
        b = re.sub(r"duration\s+\S+;", f"duration        {duration:g};", b)
        return re.sub(r"massTotal\s+\S+;", f"massTotal       {mass * duration / dur:.6g};", b)
    new, n = re.subn(r"        \w+\n        \{.*?\n        \}\n", fix, text, flags=re.S)
    assert n >= 1, "no blocks found"
    open(p, "w").write(new)


def patch_narrow():
    """Half-width jet with patch injection on the remapped one-face mesh (as large_narrow_patch), from box_large at 70 us."""
    from dataclasses import replace
    src = open(os.path.join(HERE, "build_mapped.py")).read().rsplit("\n{", 1)[0]
    ns = {"__file__": os.path.join(HERE, "build_mapped.py")}
    exec(compile(src, "build_mapped.py", "exec"), ns)
    dest = os.path.join(B, "r_box_patch")
    s = replace(build.load_setup(os.path.join(B, "box_large")), jet_faces=1, end=2e-4, jet_windows=((70e-6, 130e-6),))
    topo = build.header("dictionary", "topoSetDict") + (
        "actions\n(\n    { name jetFaces; type faceSet; action new; source boxToFace;"
        " sourceInfo { box (0.05 -1e-6 -1) (0.0502 1e-6 1); } }\n);\n")
    ns["mapped"](os.path.join(B, "box_large"), "7e-05", dest, s, topo)
    path = os.path.join(dest, "constant", "sprayCloudProperties")
    text = open(path).read()
    pps = build.JET_PPS * s.jet_rate / (build.RHO_L * s.jet_u * build.JET_D * build.DEPTH)
    newj = build.injector("jet0", build.on_patch("jet", (0.0, s.jet_u)), s.jet_rate * 1.3e-4, pps, "mass", build.ROSIN, 1.3e-4, soi=7e-5)
    text, n = re.subn(r"        jet0\n        \{.*?\n        \}\n", newj, text, flags=re.S)
    assert n == 1
    open(path, "w").write(text)
    settings(dest)
    print("r_box_patch: half-width patch jet on the remapped mesh, from box_large at 70 us to 200 us")


SPECIAL = {"r_f10_cont": f10_cont, "r_full_j1": full_clean, "r_box_patch": patch_narrow, "r_f15box_cont": f15box_cont,
           "r_low_cont": lambda: low_box("r_low_cont", ())}


if len(sys.argv) < 2:
    sys.exit("name the jobs to build; building all would overwrite running cases. Jobs: " + " ".join(list(JOBS) + list(SPECIAL)))
for name in sys.argv[1:]:
    if name in SPECIAL:
        SPECIAL[name]()
        continue
    src, t, changes, extra = JOBS[name]
    changes = dict(changes)
    drop = changes.pop("drop_jet_liquid", False)
    s = build.branch(os.path.join(B, src), os.path.join(B, name), t, drop_jet_liquid=drop, **changes)
    dest = os.path.join(B, name)
    if "tol" in extra:
        subprocess.run([sys.executable, os.path.join(HERE, "revision_settings.py"), dest, "--abstol", extra["tol"][0],
                        "--reltol", extra["tol"][1]], check=True, stdout=subprocess.DEVNULL)
    else:
        settings(dest)
    if "extend_injectors" in extra:
        extend_injectors(dest, extra["extend_injectors"])
    if "maxCo" in extra:
        set_maxco(dest, extra["maxCo"])
    print(f"{name}: from {src} at {float(t) * 1e6:g} us to {s.end * 1e6:g} us, jet_u {s.jet_u}, windows {len(s.jet_windows)}"
          + "".join(f", {k} {v}" for k, v in extra.items()) + (", jet liquid dropped" if drop else ""))
