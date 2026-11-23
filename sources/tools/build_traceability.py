#!/usr/bin/env python3
"""Build the traceability matrix: requirement -> B3-D0 row -> code location.

    python tools/build_traceability.py            # writes TRACEABILITY.md
    python tools/build_traceability.py --check    # writes nothing, non-zero on a break

Block: B3.
Lot: B3-L8.
Competency: B3-C1.
Covers: B3-EC07, B3-EC28.

Why a script rather than a hand-kept table: a hand-written matrix drifts. B3-D0's
did -- eleven citations had slipped by one rank after a renumbering. The --check
mode looks BOTH WAYS:

  - does every requirement cited in B3-D0 section 0.4 exist in B3-D0 section
    0.3? (this is the check that would have caught that drift the same day)
  - does every "Covers:" mark in the code name an existing requirement?

Documentary and architectural requirements legitimately carry no code: their
absence is counted, not penalised.

Code and comments are in English; the generated document stays in French, since
it is read alongside B3-D0 and B3-D1.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # step-2/
# B3-D0 IS THE ONE SOURCE since 2026-11-23: its section 0.3 defines every
# requirement -- identifier, statement, type -- and its section 0.4 cites them.
# Until then the working copy of the cahier des charges (step-0/ws/) was read,
# because B3-D0 had renumbered B3-EC19 to B3-EC28 by one rank while the code
# and section 0.4 kept the old numbers. B3-D0 was realigned on the code; the old
# B3-EC19 became B3-EC19A (secrets) and B3-EC19B (roles).
D0_DOC = ROOT.parent / "step-0" / "fraud-project--d0-introduction.md"
SCANNED = ("fraud", "sql", "tests", "tools", "airflow", "dashboard")
# An optional capital letter: B3-EC19A and B3-EC19B are two requirements.
REQ = re.compile(r"(?<![\w-])(B3-(?:EE|EI|EC)[0-9]{2}[A-Z]?)(?![\w])")
MARK = re.compile(r"Covers:\s*(.+)")

# B3-D0 writes a type as letters joined by "/" -- "D/A", "A/D", "CA/A", "DM".
# The matrix carries them in a FIXED order, never the order of the source text:
# the same pair must always read the same way. "CA" (critere d'acceptation) is
# a status rather than a nature and is dropped, as it always was.
KINDS = (("L", "livrable"), ("D", "documentaire"), ("A", "architectural"),
         ("F", "fonctionnel"), ("DM", "démonstration"))
LEGEND = ("L = livrable, D = documentaire, A = architectural, F = fonctionnel, "
          "DM = démonstration")


def letters_of(kind: str) -> list[str]:
    """The kinds a B3-D0 type carries, in the fixed order of KINDS."""
    tokens = {t.strip().upper() for t in re.split(r"[/,]", kind or "")}
    return [short for short, _ in KINDS if short in tokens]


def abbreviated(kind: str) -> str:
    """The kinds a requirement carries, as letters. Rendering only."""
    return ", ".join(letters_of(kind))


def read(path: Path) -> str:
    return io.open(path, encoding="utf-8").read()


def defined() -> dict[str, tuple[str, str]]:
    """Requirements as B3-D0 section 0.3 defines them: id -> (statement, type).

    The tables of 0.3 do not have the same columns -- the last one has no
    "Objectif" -- so the Type column is found by its HEADER, table by table.
    """
    out = {}
    type_at = None
    body = read(D0_DOC).split("## 0.4.")[0]
    for line in body.split("\n"):
        cells = [c.strip() for c in line.split("|")]
        if line.startswith("|") and "Type" in cells and "Exigence" in cells:
            type_at = cells.index("Type")
            continue
        m = re.match(r"^\|\s*\*{0,2}(B3-(?:EE|EI|EC)[0-9]{2}[A-Z]?)\*{0,2}\s*\|",
                     line)
        if not m or type_at is None:
            continue
        text = re.sub(r"\s+", " ", cells[2]) if len(cells) > 2 else ""
        kind = cells[type_at] if len(cells) > type_at else ""
        out[m.group(1)] = (text, kind)
    return out


def split_marks(code: dict[str, list[str]], req: dict) -> list[str]:
    """A mark on a requirement B3-D0 has SPLIT: B3-EC19, now B3-EC19A and
    B3-EC19B. Counted for each part and listed, never guessed: which part a
    file covers is decided file by file, by hand. Returns the split ids."""
    split = []
    for r in list(code):
        if r in req:
            continue
        parts = sorted(k for k in req if k[:-1] == r and k[-1].isalpha())
        if not parts:
            continue
        places = code.pop(r)
        for part in parts:
            code.setdefault(part, []).extend(
                "%s (%s, à préciser)" % (p, r) for p in places)
        split.append(r)
    return split


def cited_in_d0() -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Requirement -> B3-D0 rows citing it. Live rows kept apart from struck ones."""
    body = read(D0_DOC)
    body = body.split("### 0.4.1.")[1].split("### 0.4.4.")[0]
    live: dict[str, list[str]] = {}
    struck: dict[str, list[str]] = {}
    for line in body.split("\n"):
        m = re.match(r"^\|\s*\*{0,2}~{0,2}(B3-(?:F|K|H)[0-9]{2}(?:-[0-9])?)", line)
        if not m:
            continue
        cells = line.split("|")
        target = struck if "~~" in line else live
        for r in REQ.findall(cells[-2] if len(cells) > 2 else ""):
            target.setdefault(r, []).append(m.group(1))
    return live, struck


def tagged() -> dict[str, list[str]]:
    """Requirement -> code locations, from the "Covers:" marks."""
    out: dict[str, list[str]] = {}
    for sub in SCANNED:
        for path in sorted((ROOT / sub).rglob("*")):
            if path.suffix not in (".py", ".sql"):
                continue
            lines = read(path).split("\n")
            for i, line in enumerate(lines):
                m = MARK.search(line)
                if not m:
                    continue
                scope = ""
                for prev in reversed(lines[:i]):
                    d = re.match(r"\s*(?:def|class)\s+(\w+)", prev)
                    if d:
                        scope = " " + d.group(1) + "()"
                        break
                where = "%s:%d%s" % (path.relative_to(ROOT), i + 1, scope)
                for r in REQ.findall(m.group(1)):
                    out.setdefault(r, []).append(where)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    req = defined()
    live, struck = cited_in_d0()
    code = tagged()
    split = split_marks(code, req)

    broken: list[str] = []
    for r, rows in live.items():
        if r not in req:
            broken.append("B3-D0 cites %s (row %s), which the requirements do not define"
                          % (r, ", ".join(rows)))
    for r, places in code.items():
        if r not in req:
            broken.append("code marks %s (at %s), which the requirements do not define"
                          % (r, ", ".join(places)))

    carried = sorted(set(code) & set(req))
    no_code = [r for r in sorted(req) if r not in code]
    needs_code = [r for r in no_code
                  if {"F", "L"} & set(letters_of(req[r][1]))]

    if args.check:
        for b in broken:
            print("  BROKEN  %s" % b)
        print("\n  %d requirements defined; %d carried by code; "
              "%d without code, of which %d functional or deliverable"
              % (len(req), len(carried), len(no_code), len(needs_code)))
        for r in split:
            print("  to settle: marks on %s, split in B3-D0 -- counted for each "
                  "part until decided file by file" % r)
        if broken:
            print("\n  failed: %d traceability break(s)" % len(broken))
            return 1
        print("  ok: no dangling reference either way")
        return 0

    out = ["# Matrice de traçabilité", "",
           "> Fichier **généré** par `tools/build_traceability.py`. Ne pas éditer à la main.",
           "> Les emplacements viennent des marques `Covers:` du code ; les lignes de B3-D0 de §0.4.",
           "",
           "> Type : " + LEGEND + ".",
           "",
           "| Exigence | Type | Énoncé | B3-D0 §0.4 | Code |",
           "| --- | --- | --- | --- | --- |"]
    for r in sorted(req):
        text, kind = req[r]
        rows = ", ".join(live.get(r, [])) or ("~~%s~~" % ", ".join(struck[r])
                                              if r in struck else "—")
        places = "<br/>".join("`%s`" % p for p in code.get(r, [])) or "—"
        out.append("| **%s** | %s | %s | %s | %s |"
                   % (r, abbreviated(kind) or "—", text[:118], rows, places))
    out += ["", "## Décompte", "",
            "- exigences définies : **%d**" % len(req),
            "- portées par du code : **%d**" % len(carried),
            "- sans code, de nature fonctionnelle ou livrable : **%d**" % len(needs_code),
            "- ruptures de traçabilité : **%d**" % len(broken), ""]
    if split:
        out += ["> Marques à préciser : %s, exigence scindée dans B3-D0. Ses "
                "emplacements sont comptés pour chacune de ses parties, avec la "
                "mention « à préciser », jusqu'à décision fichier par fichier."
                % ", ".join(split), ""]
    (ROOT / "TRACEABILITY.md").write_text("\n".join(out), encoding="utf-8")
    print("TRACEABILITY.md written: %d requirements, %d carried by code, %d break(s)"
          % (len(req), len(carried), len(broken)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
