import glob
import json
import math
import os
import shutil
from dataclasses import asdict, dataclass, replace

from . import foam

TEMPLATE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "template")
DEPTH = 2e-3
AFR = 15.139
RHO_L = 680.0
D_DROP = 1e-5
N_PER_PARCEL = 10
JET_X, JET_D, JET_PPS = 0.05, 0.5e-3, 7.21e8
JET_U = {0.1: 19.24, 0.5: 43.01, 1.0: 60.83, 2.0: 86.02}
MW = {"NXC7H16": 100.204, "O2": 31.998, "N2": 28.014}
SPECIES = ("NXC7H16", "O2", "N2", "CO2", "H2O", "Ydefault")


def premixed(phi):
    m = {"NXC7H16": phi * MW["NXC7H16"], "O2": 11 * MW["O2"], "N2": 41.36 * MW["N2"]}
    total = sum(m.values())
    return {k: v / total for k, v in m.items()}


@dataclass
class Setup:
    lx: float
    ly: float
    end: float
    write: float
    nproc: int
    T: float = 697.0
    p: float = 2.855e4
    u: float = 2535.0
    wedge: float = 27.0
    phi_vapor: float = 0.0
    spray: bool = True
    jet_u: float = 0.0
    jet_windows: tuple = ()
    wall: str = "rebound"
    dx: float = 0.2e-3
    jet_faces: int = 2
    jet_d: float = JET_D
    jet_scale: float = 1.0

    @property
    def jet_rate(self):
        return RHO_L * self.jet_u * self.jet_d * DEPTH * self.jet_faces / 2 * self.jet_scale

    @property
    def U(self):
        a = math.radians(self.wedge)
        return self.u * math.cos(a), -self.u * math.sin(a)

    @property
    def Y(self):
        return premixed(self.phi_vapor) if self.phi_vapor else {"NXC7H16": 0.0, "O2": 0.232, "N2": 0.768}

    @property
    def duration(self):
        return max(3e-4, self.end)


PRESETS = {
    "paper_j1": Setup(0.25, 0.1, 2.5e-4, 5e-6, 16, jet_u=JET_U[1.0]),
    "paper_nojet": Setup(0.25, 0.1, 1.5e-4, 5e-6, 16),
    "crop_jet": Setup(0.08, 0.015, 5e-5, 2e-6, 8, jet_u=JET_U[1.0]),
    "crop_nojet": Setup(0.06, 0.015, 6e-5, 5e-6, 8),
    "crop_vapor": Setup(0.1, 0.016, 1.5e-4, 5e-6, 8, phi_vapor=1.0, spray=False),
    "guo_phi1": Setup(0.06, 0.02, 8e-5, 4e-6, 8, T=298.0, p=101325.0, u=2900.0, wedge=30.0, phi_vapor=1.0, spray=False),
    "box_small": Setup(0.09, 0.035, 8e-5, 5e-6, 8, jet_u=JET_U[1.0]),
    "box_large": Setup(0.12, 0.045, 8e-5, 5e-6, 8, jet_u=JET_U[1.0]),
    "guo_phi02": Setup(0.06, 0.02, 8e-5, 4e-6, 8, T=298.0, p=101325.0, u=2900.0, wedge=30.0, phi_vapor=0.2, spray=False),
    "crop_grid": Setup(0.1, 0.025, 5e-5, 5e-6, 8, jet_u=JET_U[1.0]),
    "crop_grid_fine": Setup(0.1, 0.025, 5e-5, 5e-6, 8, jet_u=JET_U[1.0], dx=0.15e-3),
    "crop_grid_d1": Setup(0.1, 0.025, 5e-5, 5e-6, 8, jet_u=JET_U[1.0], jet_d=1e-3),
}


def pulse_windows(f, duty, t0, t1):
    n = math.ceil((t1 - t0) * f - 1e-9)
    return tuple((t0 + k / f, duty / f) for k in range(n))


def header(cls, obj, loc=None):
    where = f'    location    "{loc}";\n' if loc else ""
    return f"FoamFile\n{{\n    version     2.0;\n    format      ascii;\n    class       {cls};\n{where}    object      {obj};\n}}\n\n"


def block_mesh(s):
    nx, ny = round(s.lx / s.dx), round(s.ly / s.dx)
    v = " ".join(f"({x} {y} {z})" for z in (-DEPTH / 2, DEPTH / 2) for x, y in ((0, 0), (s.lx, 0), (s.lx, s.ly), (0, s.ly)))
    return header("dictionary", "blockMeshDict") + f"""convertToMeters 1;

vertices ( {v} );

blocks ( hex (0 1 2 3 4 5 6 7) ({nx} {ny} 1) simpleGrading (1 1 1) );

edges ();

boundary
(
    inflow        {{ type patch; faces ((0 3 7 4)); }}
    outflow       {{ type patch; faces ((1 2 6 5)); }}
    lowerWall     {{ type wall;  faces ((0 1 5 4)); }}
    upperBoundary {{ type patch; faces ((3 2 6 7)); }}
    frontAndBack  {{ type empty; faces ((0 3 2 1) (4 7 6 5)); }}
);

mergePatchPairs ();
"""


def jet_patch(s):
    h = s.jet_d / 2 - 1e-7
    topo = header("dictionary", "topoSetDict") + f"""actions
(
    {{
        name    jetFaces;
        type    faceSet;
        action  new;
        source  boxToFace;
        sourceInfo {{ box ({JET_X - h} -1e-6 -1) ({JET_X + h} 1e-6 1); }}
    }}
);
"""
    create = header("dictionary", "createPatchDict") + """pointSync false;

patches
(
    {
        name            jet;
        patchInfo       { type wall; }
        constructFrom   set;
        set             jetFaces;
    }
);
"""
    return topo, create


def field(name, dims, value, s, cls="volScalarField", wall="zeroGradient"):
    walls = ["lowerWall"] + (["jet"] if s.jet_u else [])
    bc = [f"    inflow        {{ type fixedValue; value uniform {value}; }}",
          f"    upperBoundary {{ type fixedValue; value uniform {value}; }}",
          "    outflow       { type zeroGradient; }"]
    bc += [f"    {w:13s} {{ type {wall}; }}" for w in walls]
    bc += ["    frontAndBack  { type empty; }"]
    return header(cls, name, "0") + f"dimensions      {dims};\n\ninternalField   uniform {value};\n\nboundaryField\n{{\n" + "\n".join(bc) + "\n}\n"


def initial(s):
    ux, uy = s.U
    Y = s.Y
    out = {
        "T": field("T", "[0 0 0 1 0 0 0]", s.T, s),
        "p": field("p", "[1 -1 -2 0 0 0 0]", s.p, s),
        "U": field("U", "[0 1 -1 0 0 0 0]", f"({ux:.3f} {uy:.3f} 0)", s, "volVectorField", "slip"),
    }
    for sp in SPECIES:
        out[sp] = field(sp, "[0 0 0 0 0 0 0]", f"{Y.get(sp, 0.0):.6f}", s)
    return out


def on_patch(patch, U0):
    return ["type            patchInjection;", f"patchName       {patch};", f"U0              ({U0[0]:.3f} {U0[1]:.3f} 0);"]


def on_face(x, width, u):
    return ["type            coneInjection;", f"position        ({x:g} 1e-05 0);", "direction       (0 1 0);",
            "thetaInner      0;", "thetaOuter      0;", "injectionMethod disc;", "dInner          0;",
            f"dOuter          {width:g};", "flowType        constantVelocity;", f"Umag            {u:g};"]


def injector(name, where, mass, pps, basis, size, duration, soi=0):
    lines = where + [
        f"SOI             {soi:g};",
        f"duration        {duration:g};",
        f"massTotal       {mass:.6g};",
        f"parcelBasisType {basis};",
    ]
    if basis == "fixed":
        lines.append(f"nParticle       {N_PER_PARCEL};")
    lines += [f"parcelsPerSecond {pps:.6g};", "flowRateProfile constant 1;", f"sizeDistribution {{ {size} }}"]
    return f"        {name}\n        {{\n" + "".join(f"            {line}\n" for line in lines) + "        }\n"


FIXED = f"type fixedValue; fixedValueDistribution {{ value {D_DROP:g}; }}"
ROSIN = "type RosinRammler; RosinRammlerDistribution { minValue 1e-6; maxValue 3e-5; d 1e-5; n 3; }"


def parcel_mass():
    return N_PER_PARCEL * RHO_L * math.pi / 6 * D_DROP ** 3


def fuel_rate(s, un, length):
    return s.p / (287.0 * s.T) * un * length * DEPTH / AFR


def injectors(s, first=0):
    ux, uy = s.U
    out = []
    if s.spray:
        for name, patch, un, length in (("inflow", "inflow", ux, s.ly), ("upper", "upperBoundary", -uy, s.lx)):
            rate = fuel_rate(s, un, length)
            out.append(injector(name, on_patch(patch, (ux, uy)), rate * s.duration, rate / parcel_mass(), "fixed", FIXED, s.duration))
    if s.jet_u:
        windows = s.jet_windows or ((0.0, s.duration),)
        where = on_patch("jet", (0.0, s.jet_u)) if s.jet_faces == 2 else on_face(JET_X + s.dx / 2, s.dx, s.jet_u)
        pps = JET_PPS * s.jet_rate / (RHO_L * s.jet_u * JET_D * DEPTH)
        for i, (t0, dt) in enumerate(windows, first):
            name = "jet" if t0 == 0 else f"jet{i}"
            out.append(injector(name, where, s.jet_rate * dt, pps, "mass", ROSIN, dt, soi=t0))
    if not out:
        mass = RHO_L * JET_U[1.0] * JET_D * DEPTH * s.duration
        out.append(injector("dormant", on_patch("lowerWall", (0.0, JET_U[1.0])), mass, JET_PPS, "mass", ROSIN, s.duration, soi=1))
    return "".join(out)


def spray_cloud(s, first=0):
    return header("dictionary", "sprayCloudProperties", "constant") + """solution
{
    active          true;
    coupled         true;
    transient       yes;
    cellValueSourceCorrection on;
    maxCo           0.3;
    sourceTerms
    {
        schemes
        {
            rho             explicit 1;
            U               explicit 1;
            Yi              explicit 1;
            h               explicit 1;
        }
    }
    interpolationSchemes
    {
        rho             cell;
        U               cellPoint;
        thermo:mu       cell;
        T               cell;
        Cp              cell;
        kappa           cell;
        p               cell;
    }
    integrationSchemes
    {
        U               Euler;
        T               analytical;
    }
}

constantProperties
{
    T0              300;
    rho0            """ + f"{RHO_L:g}" + """;
    Cp0             2240;
    constantVolume  false;
}

subModels
{
    particleForces
    {
        sphereDrag;
    }

    injectionModels
    {
""" + injectors(s, first) + """    }

    dispersionModel none;
    patchInteractionModel standardWallInteraction;
    heatTransferModel RanzMarshall;
    compositionModel singlePhaseMixture;
    phaseChangeModel liquidEvaporationBoil;
    surfaceFilmModel none;
    atomizationModel none;
    breakupModel    PilchErdman;
    stochasticCollisionModel none;
    radiation       off;

    standardWallInteractionCoeffs { type """ + s.wall + """; }
    RanzMarshallCoeffs { BirdCorrection true; }
    singlePhaseMixtureCoeffs { phases ( liquid { NXC7H16 1; } ); }
    liquidEvaporationBoilCoeffs { enthalpyTransfer enthalpyDifference; activeLiquids ( NXC7H16 ); }
    PilchErdmanCoeffs { B1 0.75; B2 0.348; }
}

cloudFunctions
{}
"""


def control(s, application="detonationFoam_V3.1"):
    return header("dictionary", "controlDict", "system") + f"""application     {application};
startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         {s.end:g};
deltaT          1e-9;
writeControl    adjustableRunTime;
writeInterval   {s.write:g};
purgeWrite      0;
writeFormat     ascii;
writePrecision  6;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;
adjustTimeStep  yes;
maxCo           0.3;
maxDeltaT       1e-7;
"""


def decompose(n):
    return header("dictionary", "decomposeParDict", "system") + f"numberOfSubdomains {n};\n\nmethod          scotch;\n"


def write(dest, files):
    for rel, txt in files.items():
        path = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").write(txt)


def build(s, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    for sub in ("constant", "system"):
        shutil.copytree(os.path.join(TEMPLATE, sub), os.path.join(dest, sub))
    files = {"system/blockMeshDict": block_mesh(s), "system/controlDict": control(s),
             "system/decomposeParDict": decompose(s.nproc), "constant/sprayCloudProperties": spray_cloud(s)}
    if s.jet_u:
        files["system/topoSetDict"], files["system/createPatchDict"] = jet_patch(s)
    files.update({f"0/{k}": v for k, v in initial(s).items()})
    files["setup.json"] = json.dumps(asdict(s), indent=1)
    write(dest, files)


def load_setup(case):
    d = json.load(open(os.path.join(case, "setup.json")))
    d["jet_windows"] = tuple(tuple(w) for w in d["jet_windows"])
    return Setup(**d)


def branch(src, dest, time, drop_jet_liquid=False, **changes):
    parent = load_setup(src)
    s = replace(parent, **changes)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    for sub in ("constant", "system"):
        shutil.copytree(os.path.join(src, sub), os.path.join(dest, sub))
    for part in glob.glob(os.path.join(src, "processor*")):
        name = os.path.basename(part)
        for sub in ("constant", "0", time):
            shutil.copytree(os.path.join(part, sub), os.path.join(dest, name, sub))
        cloud = os.path.join(dest, name, time, "lagrangian", "sprayCloud")
        if drop_jet_liquid and os.path.exists(os.path.join(cloud, "position0")):
            foam.filter_cloud(cloud, [not (abs(x - JET_X) <= parent.jet_d and y < 1e-4) for x, y, _ in foam.injected_at(cloud)])
    write(dest, {"constant/sprayCloudProperties": spray_cloud(s, len(parent.jet_windows)), "system/controlDict": control(s),
                 "setup.json": json.dumps(asdict(s), indent=1)})
    return s


def build_ignition(dest, T, p=2.8e5, phi=1.0, end=4e-4):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(os.path.join(TEMPLATE, "ignition"), dest)
    os.makedirs(os.path.join(dest, "constant"))
    for f in ("reactions", "speciesThermo", "chemistryProperties"):
        shutil.copy(os.path.join(TEMPLATE, "constant", f), os.path.join(dest, "constant", f))
    fractions = " ".join(f"{k} {v:.4f};" for k, v in premixed(phi).items())
    single = "boundaryField\n{\n    boundary { type empty; }\n}\n"
    zero = {
        f: header("volScalarField", f, "0") + f"dimensions      {dims};\n\ninternalField   uniform {val:g};\n\n" + single
        for f, dims, val in (("T", "[0 0 0 1 0 0 0]", T), ("p", "[1 -1 -2 0 0 0 0]", p), ("Ydefault", "[0 0 0 0 0 0 0]", 1))
    }
    write(dest, {
        **{f"0/{k}": v for k, v in zero.items()},
        "constant/initialConditions": header("dictionary", "initialConditions", "constant")
        + f"constantProperty pressure;\nfractionBasis   mass;\nfractions       {{ {fractions} }};\np               {p:g};\nT               {T:g};\n",
        "constant/thermophysicalProperties": header("dictionary", "thermophysicalProperties", "constant")
        + "thermoType\n{\n    type            heRhoThermo;\n    mixture         multiComponentMixture;\n    transport       sutherland;\n"
        "    thermo          janaf;\n    energy          sensibleEnthalpy;\n    equationOfState perfectGas;\n    specie          specie;\n}\n\n"
        '#include "speciesThermo"\n\ninertSpecie     N2;\n',
        "system/controlDict": header("dictionary", "controlDict", "system")
        + f"application     chemFoam;\nstartFrom       startTime;\nstartTime       0;\nstopAt          endTime;\nendTime         {end:g};\n"
        f"deltaT          1e-9;\nmaxDeltaT       2e-7;\nadjustTimeStep  on;\nwriteControl    adjustableRunTime;\nwriteInterval   {end:g};\n"
        "purgeWrite      0;\nwriteFormat     ascii;\nwriteCompression off;\ntimeFormat      general;\ntimePrecision   6;\nrunTimeModifiable yes;\n",
    })
