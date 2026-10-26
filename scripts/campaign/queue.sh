#!/usr/bin/env bash
# Usage: scripts/campaign/queue.sh <case>...  Launch the cases in order as cores free up; a case that is not built or fails its audit is dropped and logged.
set -o pipefail
cd "$(dirname "$0")/../.."
B=${BOXES:-~/PULSWAVE/cases/boxes}
order="$*"
used() { pgrep -af "^/usr/bin/mpirun --bind-to none -np" | awk '{s+=$6} END {print s+0}'; }
ranks() { awk '/numberOfSubdomains/ {gsub(";", ""); print $2}' $B/$1/system/decomposeParDict; }
ok() {
    [ -f $B/$1/setup.json ] && out=$(python3 scripts/campaign/audit.py $1) || return 1
    grep -q "identical across procs: True, missing on 0" <<< "$out" && ! grep -q "STALE\|NO SAVED STATE" <<< "$out" &&
        grep -q "procs \([0-9]*\) decomp \1$" <<< "$out"
}
while :; do
    [ -f ~/queue.cancel ] && { echo "$(date -u) cancelled"; exit; }
    [ -z "$order" ] && { echo "$(date -u) all launched"; exit; }
    rest=""; launched=0
    for c in $order; do
        if [ $launched = 0 ] && [ -f $B/$c/system/decomposeParDict ] && [ $(( $(used) + $(ranks $c) )) -le 32 ]; then
            if ok $c; then scripts/run.sh --restart $B/$c; echo "$(date -u) started $c"; else echo "$(date -u) audit failed, dropped $c"; fi
            launched=1
        else
            [ $launched = 0 ] && [ -f $B/$c/system/decomposeParDict ] && launched=2
            rest="$rest $c"
        fi
    done
    order=$(echo $rest)
    [ $launched = 1 ] && sleep 60 || sleep 120
done
