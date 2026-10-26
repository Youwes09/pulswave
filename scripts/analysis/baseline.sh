#!/usr/bin/env bash
# Baseline state of the reduced-domain reference near the jet, and of the pocket after switch-off.
# Usage: scripts/analysis/baseline.sh <boxes dir>   (run inside `nix develop`)
set -euo pipefail
B=$1
py() { python -m pulswave "$@"; }
for t in 7e-05 8e-05; do
    echo "== nearjet box_large $t"; py nearjet "$B/box_large" "$t"
    echo "== pocket box_large $t"; py pocket "$B/box_large" "$t"
done
for t in 7.5e-05 8.5e-05 9.5e-05; do
    echo "== pocket large_off $t"; py pocket "$B/large_off" "$t"
done
echo "== theory timescales, near-wall gas upstream of the jet at 70 us"
py theory timescales --T 1156 --p 2.74 --u 2081 --fuel 0.0864 --o2 0.2096
echo "== frozen state behind the jet shock at the pressure ratios of the front at y = 1-4 mm, 70 us (fronts/box_large.json)"
python scripts/analysis/jet_shock.py 1156 2.74 0.0864 0.2096 6.1 6.6 7.3 8.9
