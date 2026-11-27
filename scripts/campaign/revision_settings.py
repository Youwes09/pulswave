"""Apply the revision run settings to a built or branched case and record them in its revision.json.

  - Chemistry ODE tolerances absTol 1e-10 (solver default about 1e-15) and relTol as given (default 1e-4, production
    1e-3). absTol alone changed the fields by less than 0.07% over a 10 us restart; with relTol 1e-3 the base was
    unchanged and the fields within 0.4% over 75-85 us. r_crop_off_tolctl checks the hold phase at the default tolerances.
  - ascii output, which the analysis scripts parse.
  - Output interval (default 1 us).
The runs use the patched solver (container/patches), launched as `mpirun -np <n> <binary> -parallel` in the container.
Usage: python scripts/campaign/revision_settings.py <case> [--abstol 1e-10] [--reltol 1e-4] [--write 1e-6]
"""
import argparse, json, os, re

ap = argparse.ArgumentParser()
ap.add_argument("case")
ap.add_argument("--reltol", default="1e-4")
ap.add_argument("--abstol", default="1e-10")
ap.add_argument("--write", default="1e-6")
a = ap.parse_args()

chem = os.path.join(a.case, "constant", "chemistryProperties")
s = open(chem).read()
body = f"odeCoeffs\n{{\n    solver          seulex;\n    absTol          {a.abstol};\n    relTol          {a.reltol};\n}}"
s, n = re.subn(r"odeCoeffs\s*\{[^}]*\}", body, s)
assert n == 1, "odeCoeffs block not found exactly once"
open(chem, "w").write(s)

ctl = os.path.join(a.case, "system", "controlDict")
c = open(ctl).read()
c, n1 = re.subn(r"^writeFormat\s+\S+;", "writeFormat     ascii;", c, flags=re.M)
c, n2 = re.subn(r"^writeInterval\s+\S+;", f"writeInterval   {a.write};", c, flags=re.M)
assert n1 == 1 and n2 == 1, "writeFormat/writeInterval not found"
open(ctl, "w").write(c)

# kept out of setup.json, which build.load_setup turns into a Setup and must hold only Setup fields
json.dump({"solver": "rhophi", "absTol": a.abstol, "relTol": a.reltol, "writeFormat": "ascii", "write": a.write},
          open(os.path.join(a.case, "revision.json"), "w"), indent=1)
print(f"{a.case}: absTol {a.abstol}, relTol {a.reltol}, ascii, write {a.write}, solver rhophi")
