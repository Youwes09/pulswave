"""Consistency checks on a manuscript source: citations, bibliography order, labels and references.

Usage: python scripts/checks/check_tex.py paper/manuscriptv2.tex
Exits non-zero if any check fails.
"""
import re
import sys

src = open(sys.argv[1]).read()
body, _, bib = src.partition(r"\begin{thebibliography}")
body = re.sub(r"(?<!\\)%.*", "", body)
fail = 0


def report(ok, msg):
    global fail
    print(("ok    " if ok else "FAIL  ") + msg)
    fail += not ok


cites = []
for m in re.finditer(r"\\(?:cite|onlinecite|citep|citet)\{([^}]*)\}", body):
    for k in m.group(1).split(","):
        k = k.strip()
        if k not in cites:
            cites.append(k)
items = re.findall(r"\\bibitem\{([^}]*)\}", bib)

missing = [k for k in cites if k not in items]
unused = [k for k in items if k not in cites]
dups = sorted({k for k in items if items.count(k) > 1})
report(not missing, f"every citation has a bibitem ({len(cites)} cited) {missing or ''}")
report(not unused, f"every bibitem is cited ({len(items)} items) {unused or ''}")
report(not dups, f"no duplicate bibitems {dups or ''}")

if "--fix-order" in sys.argv and not missing and not dups:
    head, _, rest = bib.partition(r"\bibitem")
    entries = [e for e in re.split(r"(?=\\bibitem\{)", r"\bibitem" + rest) if e.strip()]
    tail = entries[-1].split(r"\end{thebibliography}")
    entries[-1] = tail[0]
    by_key = {re.match(r"\\bibitem\{([^}]*)\}", e).group(1): e.rstrip() + "\n\n" for e in entries}
    new_bib = head + "".join(by_key[k] for k in cites) + r"\end{thebibliography}" + tail[1]
    open(sys.argv[1], "w").write(src.partition(r"\begin{thebibliography}")[0] + r"\begin{thebibliography}" + new_bib)
    print("bibliography reordered by first citation; rerun to check")
    sys.exit(0)

order = [k for k in items if k in cites]
first_bad = next((i for i, (a, b) in enumerate(zip(order, cites)) if a != b), None)
report(first_bad is None, "bibliography follows order of first citation"
       + ("" if first_bad is None else f": item {first_bad + 1} is {order[first_bad]}, first cited there is {cites[first_bad]}"))

labels = re.findall(r"\\label\{([^}]*)\}", body)
refs = set(re.findall(r"\\(?:ref|eqref|autoref)\{([^}]*)\}", body))
report(not [r for r in refs if r not in labels], f"every \\ref has a label {[r for r in refs if r not in labels] or ''}")
report(len(labels) == len(set(labels)), "labels are unique")
unref = [l for l in labels if l not in refs and l.split(":")[0] in ("fig", "tab")]
report(not unref, f"every figure and table label is referenced {unref or ''}")

figs = re.findall(r"\\label\{(fig:[^}]*)\}", body)
first_ref = {f: body.find("ref{" + f + "}") for f in figs}
seq = sorted(figs, key=lambda f: first_ref[f] if first_ref[f] >= 0 else 1e12)
report(seq == figs, "figures are first referenced in the order they appear" + ("" if seq == figs else f": {seq}"))

report(not re.search(r"\\begin\{enumerate\}", body.split(r"\section{Conclusions}")[-1].split(r"\begin{acknowledgments}")[0]),
       "conclusions are not a numbered list (AE comment 1)")
for pat, msg in ((r"N\$_2\$ is then negative", "no claim that N2 goes negative"), (r"five faces", "no 'five faces' (1 mm jet is four)"),
                 (r"at least 1899", "no 'at least 1899 us'")):
    report(not re.search(pat, body), msg)

sys.exit(1 if fail else 0)
