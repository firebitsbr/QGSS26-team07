"""
Validate all QGSS 2026 lab exercises and bonuses.

Two-part strategy:
  1. check_progress() → official IBM server status (authoritative source)
  2. Locally rerun exercises without a QPU → verify the current solutions
     Exercises passed on the server but requiring hardware → ✅ [server]

Author: Mauro Risonho de Paula Assumpção
Date Created: Not recorded
Date Updated: 2026-10-03
Short Description: Validate QGSS 2026 lab exercises locally and against the official grader.
Development Method: Human mental calculations and paper-and-pencil work, assisted by GitHub Copilot and Claude available at the time of the event.
License: MIT

Usage:  ./.conda/bin/python run_all_labs.py
"""

from __future__ import annotations

import contextlib
import io
import re
import sys
from pathlib import Path

import networkx as nx
import numpy as np
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeFez, FakeTorino

sys.path.insert(0, str(Path(__file__).parent / "data/labs/solutions"))
import lab0_solutions as l0
import lab1_solutions as l1
import lab2_solutions as l2
import lab3_solutions as l3
import lab4a_solutions as l4a
import lab4b_solutions as l4b
import lab4c_solutions as l4c

from qc_grader.challenges.qgss_2026 import check_progress
from qc_grader.challenges.qgss_2026.lab0 import (
    grade_lab0_ex1, grade_lab0_ex2, grade_lab0_ex3, grade_lab0_ex4,
)
from qc_grader.challenges.qgss_2026.lab1 import (
    grade_lab1_ex1, grade_lab1_ex2, grade_lab1_ex3, grade_lab1_ex4,
    grade_lab1_ex5, grade_lab1_ex6, grade_lab1_ex7,
)
from qc_grader.challenges.qgss_2026.lab2 import (
    grade_lab2_ex1, grade_lab2_ex2, grade_lab2_ex3, grade_lab2_ex4,
    grade_lab2_ex5, grade_lab2_ex6, grade_lab2_ex7,
)
from qc_grader.challenges.qgss_2026.lab3 import grade_lab3_ex1
from qc_grader.challenges.qgss_2026.lab4a import grade_lab4a_ex1, grade_lab4a_ex2
from qc_grader.challenges.qgss_2026.lab4b import (
    grade_lab4b_ex1a, grade_lab4b_ex1b,
    grade_lab4b_ex2a, grade_lab4b_ex2b,
    grade_lab4b_ex3a, grade_lab4b_ex3b, grade_lab4b_ex3c,
    grade_lab4b_ex4a, grade_lab4b_ex4b, grade_lab4b_ex4c, grade_lab4b_ex4d,
)
from qc_grader.challenges.qgss_2026.lab4c import (
    grade_lab4c_ex1a, grade_lab4c_ex1b,
    grade_lab4c_ex2a, grade_lab4c_ex2b,
    grade_lab4c_ex3a, grade_lab4c_ex3b,
    grade_lab4c_ex4,
)

# ---------------------------------------------------------------------------
# Step 1: official server status
# ---------------------------------------------------------------------------

_pbuf = io.StringIO()
with contextlib.redirect_stdout(_pbuf):
    check_progress()
_progress_text = _pbuf.getvalue()

_server: dict[str, float] = {}
_current_lab = ""
for _line in _progress_text.splitlines():
    _m = re.search(r'Lab "([^"]+)"', _line)
    if _m:
        _current_lab = _m.group(1)
    _mx = re.search(r"✅\s+(\w+)\s+—\s+score\s+([\d.]+)", _line)
    if _mx and _current_lab:
        _server[f"{_current_lab}_{_mx.group(1)}"] = float(_mx.group(2))

_total_server = len(_server)

# ---------------------------------------------------------------------------
# Step 2: local rerun
# ---------------------------------------------------------------------------

RESULTS: list[tuple[str, str, str]] = []


def _call(func, *args) -> tuple[bool | None, str]:
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            func(*args)
        out = buf.getvalue()
    except Exception as exc:
        return None, str(exc)[:100]
    for ln in out.splitlines():
        s = ln.strip()
        if "Congratulations" in s or "🎉" in s or "Correct!" in s:
            return True, s[:100]
        if "Not quite" in s or "incorrect" in s.lower():
            return False, s[:100]
    return None, out.strip()[:80]


def run(name: str, func, *args) -> None:
    passed, msg = _call(func, *args)
    score = _server.get(name)
    if passed is True:
        note = "locally re-verified"
        RESULTS.append((name, "PASS", note))
    elif score is not None:
        RESULTS.append((name, "PASS", f"server  score={score}"))
    else:
        RESULTS.append((name, "FAIL" if passed is False else "UNKNOWN", msg))


def server_only(name: str) -> None:
    score = _server.get(name)
    if score is not None:
        RESULTS.append((name, "PASS", f"server  score={score}"))
    else:
        RESULTS.append((name, "UNKNOWN", "no server data"))


# ===========================================================================
# LAB 0
# ===========================================================================

run("lab0_ex1", grade_lab0_ex1)

_qc_h = l0.ex2_hadamard_circuit()
_qc_h.measure_all()
run("lab0_ex2", grade_lab0_ex2,
    AerSimulator().run(_qc_h, shots=1024).result().get_counts())

run("lab0_ex3", grade_lab0_ex3, 0.0)
run("lab0_ex4", grade_lab0_ex4, Statevector(l0.ex4_six_qubit_state()))

# ===========================================================================
# LAB 1
# ===========================================================================

run("lab1_ex1", grade_lab1_ex1, l1.ex1_bell_01_10())
run("lab1_ex2", grade_lab1_ex2, {"a": 3, "b": 3})
run("lab1_ex3", grade_lab1_ex3, l1.ex3_ghz16_depth5())
run("lab1_ex4", grade_lab1_ex4, l1.ex4_bridge_ghz3())
run("lab1_ex5", grade_lab1_ex5, l1.ex5_ghz5_line_depth4())
run("lab1_ex6", grade_lab1_ex6, l1.ex6_ghz7_heavy_hex())

_torino_g = nx.from_edgelist(list(FakeTorino().coupling_map))
run("lab1_ex7", grade_lab1_ex7, l1.ex7_ghz_bfs(_torino_g, n=64, center=25))

# ===========================================================================
# LAB 2
# ===========================================================================

_fez = FakeFez()
run("lab2_ex1", grade_lab2_ex1, list(_fez.operation_names), list(_fez.coupling_map))
run("lab2_ex2", grade_lab2_ex2, l2.repeated_x_circuit)
run("lab2_ex3", grade_lab2_ex3, l2.repeated_x_meas_x_circuit)
run("lab2_ex4", grade_lab2_ex4, {
    "X error": {"bit-flip sensitive": True,  "phase-flip sensitive": False},
    "Y error": {"bit-flip sensitive": True,  "phase-flip sensitive": True},
    "Z error": {"bit-flip sensitive": False, "phase-flip sensitive": True},
})
run("lab2_ex5", grade_lab2_ex5,
    list(range(120)), ["h", "cx", "swap"],
    lambda c: sum(1 for i in c.data if i.operation.name == "swap"))
run("lab2_ex6", grade_lab2_ex6, l2.dynamic_ghz_circuit)
run("lab2_ex7", grade_lab2_ex7,
    lambda c: l2.quantum_circuit_params(c), l2.dynamic_ghz_circuit)

# ===========================================================================
# LAB 3
# ===========================================================================

run("lab3_ex1", grade_lab3_ex1, l3.ex1_options_dict())
server_only("lab3_ex2")
server_only("lab3_ex3")
server_only("lab3_ex4")
server_only("lab3_ex5")

# ===========================================================================
# LAB 4a
# ===========================================================================

run("lab4a_ex1", grade_lab4a_ex1, l4a.criterion_1, l4a.criterion_2)
run("lab4a_ex2", grade_lab4a_ex2, l4a.energy_fe4s4, l4a.expectation_value_loschmidt_echo)

# ===========================================================================
# LAB 4b
# ===========================================================================

_pg6 = l4b.build_partition_graph([3, 5, 7, 9, 11, 13])
run("lab4b_ex1a", grade_lab4b_ex1a, _pg6)
_ham6, _circ6 = l4b.ex1_hamiltonian_and_circuit(_pg6)
run("lab4b_ex1b", grade_lab4b_ex1b, _ham6, _circ6)

_sv1, _sv2 = l4b.ex2_sampler_options(1000)
run("lab4b_ex2a", grade_lab4b_ex2a, _sv1)
run("lab4b_ex2b", grade_lab4b_ex2b, _sv2)
server_only("lab4b_ex2c")
server_only("lab4b_ex2d")
server_only("lab4b_ex2")

_pce_h, _pce_c, _pce_enc = l4b.ex3_hamiltonian_and_circuit(160, layers=2)
_nx3, _ny3, _nz3 = l4b.pce_node_lists(160)
run("lab4b_ex3a", grade_lab4b_ex3a, l4b.reduce_qubits_with_pce, _nx3, _ny3, _nz3)
run("lab4b_ex3b", grade_lab4b_ex3b, _pce_enc[0], _pce_enc[1], _pce_enc[2])
run("lab4b_ex3c", grade_lab4b_ex3c, _pce_h, _pce_c)

_eopt = l4b.ex4_estimator_options(1000)
run("lab4b_ex4a", grade_lab4b_ex4a, _eopt["No EM"])
run("lab4b_ex4b", grade_lab4b_ex4b, _eopt["TREX"])
run("lab4b_ex4c", grade_lab4b_ex4c, _eopt["ZNE"])
run("lab4b_ex4d", grade_lab4b_ex4d, _eopt["PEC"])
server_only("lab4b_ex4")
server_only("lab4b_exbonus")

# ===========================================================================
# LAB 4c
# ===========================================================================

run("lab4c_ex1a", grade_lab4c_ex1a, l4c.alpha_beta_indices_nh)
run("lab4c_ex1b", grade_lab4c_ex1b,
    l4c.initial_layout, l4c.alpha_beta_indices_nh, l4c.ex1b_seed)

_raw_bs = np.random.default_rng(7).integers(0, 2, (2000, 52)).astype(bool)
run("lab4c_ex2a", grade_lab4c_ex2a, l4c.reshape_bitstring, _raw_bs)
run("lab4c_ex2b", grade_lab4c_ex2b, l4c.hamming_weight)
run("lab4c_ex3a", grade_lab4c_ex3a, l4c.weight_flip_0_to_1)
run("lab4c_ex3b", grade_lab4c_ex3b, l4c.recover_configurations)
run("lab4c_ex4",  grade_lab4c_ex4,  l4c.ref_ci_strings)
server_only("lab4c_exbonus")

# ===========================================================================
# Report
# ===========================================================================

ICONS = {"PASS": "✅", "FAIL": "❌", "UNKNOWN": "❓", "ERROR": "🔴"}

print()
print("=" * 72)
print("  QGSS 2026 — Labs e Bônus")
print(f"  Servidor oficial IBM:  {_total_server}/49 aprovados  |  score total: "
      f"{sum(_server.values()):.1f}")
print("=" * 72)

_cur = ""
for name, status, note in RESULTS:
    _lab = "_".join(name.split("_")[:2])
    if _lab != _cur:
        print()
        _cur = _lab
    icon = ICONS.get(status, "?")
    print(f"  {icon} {name:<22} {status:<8}  [{note}]")

_totals = {s: sum(1 for _, st, _ in RESULTS if st == s)
           for s in ("PASS", "FAIL", "UNKNOWN", "ERROR")}
print()
print("=" * 72)
print(f"  PASS {_totals['PASS']}  |  FAIL {_totals['FAIL']}  |"
      f"  UNKNOWN/ERROR {_totals['UNKNOWN'] + _totals['ERROR']}")
print("=" * 72)
