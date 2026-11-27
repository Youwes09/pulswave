# Solver patch: species convection with the mass flux

`rhophi-species-upwind.patch` applies to detonationFoam commit 02ed90db0a17 (the container's `/opt/detonationFoam`).

The species convection scheme in `rhoYEqn_NSSpray_Sutherland.H` was constructed with the volumetric flux `phi`, but used to transport the mass flux `rhoPhi`. In the Kurganov–Noelle–Petrova flux the two can differ in sign on a face, which made the implicit species update unbounded: the n-heptane mass fraction exceeded 1 in dense near-wall cells, and N₂ (the inert remainder) was clipped at 0. The patch constructs the scheme with `rhoPhi`.

Build used for the production runs, on the run host, outside the container image:

```
apptainer exec detonationfoam.sif cp -r /opt/detonationFoam/detonationFoam_dev rhophi
patch -d rhophi/.. -p1 < rhophi-species-upwind.patch     # or edit the one line by hand
apptainer exec detonationfoam.sif bash -c "export HOME=/opt; unset USER LOGNAME; \
  source /opt/OpenFOAM/OpenFOAM-8/etc/bashrc; export FOAM_USER_APPBIN=$PWD/bin/rhophi; cd rhophi && wmake"
```

The revision runs (Nov 2026, `scripts/campaign/build_revision.py`) use the resulting `bin/rhophi/detonationFoam_V3.1`, launched inside the same container as `mpirun -np <n> <binary> -parallel`.

The same `phi`/`rhoPhi` mismatch exists in the NS_Sutherland, Euler and NS_mixtureAverage species equations, which this study does not use.
