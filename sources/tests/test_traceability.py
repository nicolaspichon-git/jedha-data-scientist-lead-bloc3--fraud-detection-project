"""The traceability matrix abbreviates the kind of a requirement.

Block: B3.
Lot: B3-L8.
Competency: B3-C1.
Covers: B3-EC07.

The matrix is read column by column against B3-D0, and the Type column (Nature until 2026-11-23) held the
requirements document's own prose -- "architecturale", "documentaire,
architecturale", and once "critere d'acceptation, architectural", which is a
kind and something else at the same time. One letter per kind reads at a glance;
the point of the test is that the SAME pair always reads the same way, whatever
order the source text spells it in, and that the letters are explained in the
document rather than left to be guessed.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "TRACEABILITY.md"

_spec = importlib.util.spec_from_file_location(
    "build_traceability", ROOT / "tools" / "build_traceability.py")
bt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bt)


def test_each_kind_has_its_letter():
    """B3-D0 writes the type as letters; the matrix keeps the natures."""
    for letter in ("L", "D", "A", "F", "DM"):
        assert bt.abbreviated(letter) == letter


def test_the_order_is_the_tables_own_and_not_the_sources():
    """Two requirements of the same two kinds must not read differently because
    B3-D0 happened to spell them the other way round ("D/A", "A/D")."""
    assert bt.abbreviated("D/A") == "D, A"
    assert bt.abbreviated("A/D") == "D, A"


def test_what_is_not_a_kind_is_dropped():
    """"CA", critere d'acceptation, is a status, not a nature: the column keeps
    the nature alone."""
    assert bt.abbreviated("CA/A") == "A"


def test_an_unstated_kind_stays_empty_rather_than_guessed():
    assert bt.abbreviated("") == ""
    assert bt.abbreviated("autre chose") == ""


def test_a_split_requirement_is_counted_for_each_part_and_said():
    """B3-EC19 was split in B3-D0 into B3-EC19A and B3-EC19B. A mark on the old
    id is neither a break nor silently assigned: both parts carry it, flagged."""
    req = {"B3-EC19A": ("secrets", "A"), "B3-EC19B": ("roles", "F")}
    code = {"B3-EC19": ["fraud/config.py:3"], "B3-EC19A": ["fraud/db.py:3"]}
    assert bt.split_marks(code, req) == ["B3-EC19"]
    assert "B3-EC19" not in code
    assert code["B3-EC19A"] == ["fraud/db.py:3",
                                "fraud/config.py:3 (B3-EC19, à préciser)"]
    assert code["B3-EC19B"] == ["fraud/config.py:3 (B3-EC19, à préciser)"]


def test_the_requirements_are_read_from_b3_d0_alone():
    """No working copy of the cahier des charges any more."""
    source = (ROOT / "tools" / "build_traceability.py").read_text(encoding="utf-8")
    assert "cahier-des-charges" not in source.split('D0_DOC =')[1]
    assert not hasattr(bt, "REQUIREMENTS")


def test_the_generated_matrix_carries_nothing_but_letters():
    rows = [l for l in MATRIX.read_text(encoding="utf-8").splitlines()
            if l.startswith("| **")]
    assert rows, "the matrix holds no requirement row"
    allowed = re.compile(r"^(?:(?:L|D|A|F|DM)(?:, (?:L|D|A|F|DM))*|—)$")
    for row in rows:
        cell = row.split("|")[2].strip()
        assert allowed.match(cell), "Type column holds %r" % cell


def test_the_letters_are_explained_in_the_document():
    """A single letter in a column is unreadable without its legend, and the
    legend is generated with the table so the two cannot drift apart."""
    text = MATRIX.read_text(encoding="utf-8")
    assert bt.LEGEND in text
    for word in ("livrable", "documentaire", "architectural", "fonctionnel"):
        assert word in bt.LEGEND
