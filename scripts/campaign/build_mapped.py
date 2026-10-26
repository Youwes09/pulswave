"""Cases that need a new mesh: build it, map the parent state onto it with mapFields (droplets relocated by position),
decompose, and carry the injector state over."""
import glob, os, re, shutil, subprocess, sys
from dataclasses import replace

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from pulswave import build, foam

B = os.environ.get("BOXES", os.path.expanduser("~/PULSWAVE/cases/boxes"))
FOAM = ["singularity", "exec", os.path.expanduser("~/PULSWAVE/container/detonationfoam.sif")]


def sh(cwd, log, *cmd):
    with open(os.path.join(cwd, log), "w") as f:
        subprocess.run(FOAM + list(cmd), cwd=cwd, stdout=f, stderr=subprocess.STDOUT, check=True)


def mapped(src, t, dest, s, topo=None):
    build.build(s, dest)
    if topo:
        open(os.path.join(dest, "system", "topoSetDict"), "w").write(topo)
    for tool in ("blockMesh", "topoSet"):
        sh(dest, f"log.{tool}", tool)
    sh(dest, "log.createPatch", "createPatch", "-overwrite")
    sh(dest, "log.checkMesh", "checkMesh")
    shutil.copytree(os.path.join(dest, "0"), os.path.join(dest, t))
    if not os.path.isdir(os.path.join(src, t)):
        sh(src, "log.reconstructPar", "reconstructPar", "-time", t)
    sh(dest, "log.mapFields", "mapFields", src, "-consistent", "-sourceTime", t)
    sh(dest, "log.decomposePar", "decomposePar", "-force", "-time", t)
    sh(dest, "log.cellCentres", "mpirun", "--bind-to", "none", "-np", str(s.nproc), "postProcess", "-func", "writeCellCentres",
       "-parallel", "-time", t)
    state = os.path.join(src, "processor0", t, "uniform")
    for p in glob.glob(os.path.join(dest, "processor*")):
        os.makedirs(os.path.join(p, "0"), exist_ok=True)
        for c in ("C", "Cx", "Cy", "Cz"):
            shutil.move(os.path.join(p, t, c), os.path.join(p, "0", c))
        shutil.rmtree(os.path.join(p, t, "uniform"), ignore_errors=True)
        shutil.copytree(state, os.path.join(p, t, "uniform"))
    shutil.rmtree(os.path.join(dest, t))
    a, b = foam.parcels(src, t), foam.parcels(dest, t)
    print(f"parcels {len(a)} -> {len(b)}, liquid {sum(p[3] for p in a) * 1e9:.1f} -> {sum(p[3] for p in b) * 1e9:.1f} ug")
    assert len(b) == len(a) and abs(sum(p[3] for p in b) / sum(p[3] for p in a) - 1) < 1e-3


def narrow_patch():
    src, t, dest = os.path.join(B, "box_large"), "7e-05", os.path.join(B, "large_narrow_patch")
    s = replace(build.load_setup(os.path.join(B, "large_narrow")), end=2e-4, jet_windows=((70e-6, 130e-6),))
    topo = build.header("dictionary", "topoSetDict") + (
        "actions\n(\n    { name jetFaces; type faceSet; action new; source boxToFace;"
        " sourceInfo { box (0.05 -1e-6 -1) (0.0502 1e-6 1); } }\n);\n")
    mapped(src, t, dest, s, topo)
    path = os.path.join(dest, "constant", "sprayCloudProperties")
    text = open(path).read()
    pps = build.JET_PPS * s.jet_rate / (build.RHO_L * s.jet_u * build.JET_D * build.DEPTH)
    new = build.injector("jet0", build.on_patch("jet", (0.0, s.jet_u)), s.jet_rate * 1.3e-4, pps, "mass", build.ROSIN, 1.3e-4, soi=7e-5)
    text, n = re.subn(r"        jet0\n        \{.*?\n        \}\n", new, text, flags=re.S)
    assert n == 1
    open(path, "w").write(text)


def crop_fine():
    src, t, dest = os.path.join(B, "crop_grid"), "3.5e-05", os.path.join(B, "crop_fine_off")
    s = replace(build.PRESETS["crop_grid"], dx=1e-4, nproc=16, end=9e-5, write=1e-6, jet_windows=((0.0, 5e-5),))
    mapped(src, t, dest, s)


{"large_narrow_patch": narrow_patch, "crop_fine_off": crop_fine}[sys.argv[1]]()
print("built", sys.argv[1])
