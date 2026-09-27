#!/usr/bin/env bash
set -euo pipefail

case_dir=$(realpath "$1")
sif=${SIF:-$HOME/PULSWAVE/container/detonationfoam.sif}
foam="singularity exec $sif"
cd "$case_dir"

$foam blockMesh > log.blockMesh
if [ -f system/topoSetDict ]; then
    $foam topoSet > log.topoSet
    $foam createPatch -overwrite > log.createPatch
fi
$foam checkMesh > log.checkMesh

n=$(awk '/numberOfSubdomains/ {gsub(";", ""); print $2}' system/decomposeParDict)
$foam decomposePar -force > log.decomposePar
$foam mpirun --bind-to none -np "$n" postProcess -func writeCellCentres -parallel -time 0 > log.cellCentres

setsid nohup $foam mpirun --bind-to none -np "$n" detonationFoam_V3.1 -parallel > log.run 2>&1 < /dev/null &
echo "launched $case_dir on $n ranks"
