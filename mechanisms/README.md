# Mechanism

Liu, Hewson, Chen & Pitsch (2004) skeletal n-heptane mechanism: 44 species, 112 reactions. This is the mechanism arXiv:2506.15247 and arXiv:2202.04987 use.

| File | Use |
|---|---|
| `chem.inp` | Chemkin reactions, as received |
| `therm.dat` | Chemkin NASA-7 thermo, as received except the header line is changed to `THERMO ALL` |
| `transportProperties` | Sutherland transport input for `chemkinToFoam` |
| `nHeptane.yaml` | Cantera version of the same mechanism, used by `python -m pulswave theory` |

## Regenerating the derived files

The OpenFOAM files `template/constant/reactions` and `template/constant/speciesThermo` are generated from these inputs. Regenerating them reproduces the committed files byte for byte.

Run this inside the container, from any case directory with a `system/` folder:

```
chemkinToFoam mechanisms/chem.inp mechanisms/therm.dat mechanisms/transportProperties constant/reactions constant/speciesThermo
```

The Cantera file is generated with Cantera 3.2.0:

```
ck2yaml --input=chem.inp --thermo=therm.dat --output=nHeptane.yaml
```

## Checks

`python -m pulswave theory thermo` compares every species' cp and h in `speciesThermo` against Cantera from 300 to 2500 K. The largest difference is 0.000%.
