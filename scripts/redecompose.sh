#!/usr/bin/env bash
# Re-split a decomposed case at one time with the simple method, to change the cloud's random-number sequence.
set -euo pipefail
case_dir=$(realpath "$1"); time=$2; split=${3:-"4 2 1"}
foam="singularity exec ${SIF:-$HOME/PULSWAVE/container/detonationfoam.sif}"
cd "$case_dir"
$foam reconstructPar -time "$time" > log.reconstructPar
mv processor0/"$time"/uniform uniform.keep
rm -rf processor*
n=$(( ${split// /*} ))
sed -i -e "/^simpleCoeffs/d" -e "s/^numberOfSubdomains .*/numberOfSubdomains $n;/" -e "s/^method .*/method          simple;\nsimpleCoeffs { n ($split); delta 0.001; }/" system/decomposeParDict
$foam decomposePar -force -time "$time" > log.redecompose
rm -rf "$time"
$foam mpirun --bind-to none -np "$n" postProcess -func writeCellCentres -parallel -time "$time" > log.cellCentres
for p in processor*; do
    mkdir -p "$p/0" && for c in C Cx Cy Cz; do mv "$p/$time/$c" "$p/0/"; done
    rm -rf "$p/$time/uniform" && cp -r uniform.keep "$p/$time/uniform"
done
rm -rf uniform.keep
