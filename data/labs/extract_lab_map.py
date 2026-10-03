#!/usr/bin/env python3
"""Extract the QGSS26 lab/exercise map from the installed official grader.

Author: Mauro Risonho de Paula Assumpção
Date Created: Not recorded
Date Updated: 2026-10-03
Short Description: Extract grader exercise declarations into a local lab map.
Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
License: MIT

The grader package (qc_grader.challenges.qgss_2026) declares one module per lab
and one `grade_<lab>_<exercise>` function per exercise. This script reflects over
those declarations and writes an accurate map to data/labs/lab_map.json.

Regenerate after upgrading the grader:
    .conda/bin/python data/labs/extract_lab_map.py
"""

from __future__ import annotations

import ast
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "labs" / "lab_map.json"


def grader_dir() -> pathlib.Path:
    import qc_grader.challenges.qgss_2026 as m

    return pathlib.Path(m.__file__).parent


def signature(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> list[dict[str, str]]:
    params = []
    for a in fn.args.args:
        params.append(
            {
                "name": a.arg,
                "annotation": ast.unparse(a.annotation) if a.annotation else "",
            }
        )
    return params


def main() -> None:
    base = grader_dir()
    labs: dict[str, list[dict[str, object]]] = {}

    for path in sorted(base.glob("lab*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        exercises = []
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not node.name.startswith("grade_"):
                continue
            exercises.append(
                {
                    "grader": node.name,
                    "exercise": node.name.removeprefix(f"grade_{path.stem}_"),
                    "params": signature(node),
                }
            )
        labs[path.stem] = exercises

    payload = {
        "challenge": "qgss_2026",
        "grader_module": "qc_grader.challenges.qgss_2026",
        "labs": labs,
        "totals": {lab: len(ex) for lab, ex in labs.items()},
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    total = sum(len(e) for e in labs.values())
    print(f"labs={len(labs)} exercises={total}")
    for lab, ex in labs.items():
        print(f"  {lab}: {', '.join(e['exercise'] for e in ex)}")
    print(f"output -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
