"""Execute the already-frozen EXP005-EPI Generator C confirmation plan.

This driver was added after the provisional semantic reimplementation outcome.
It does not define or tune any scientific quantity: it reads the frozen plan,
invokes the already-committed generator/controller runner, and applies the frozen
thresholds verbatim.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from lab.exp005_epi_crv import benchmark_c
from lab.exp005_epi_worlds_c import generate_adversarial_world


DEFAULT_PLAN = Path("experiments/exp005_epi/generator_c_confirmation_plan.json")


def decide(result: dict, plan: dict) -> dict:
    t = plan["thresholds"]
    primary = result["paired"]["crv_minus_udu_net_gain"]
    weighted = result["paired"]["crv_minus_udu_weighted_epistemic_gain"]
    unweighted = result["paired"]["crv_minus_udu_unweighted_epistemic_gain"]
    crv = result["summary"]["crv_net"]
    udu = result["summary"]["udu_net"]

    checks = {
        "primary_mean_difference": (
            primary["mean_difference"] >= t["primary_minimum_mean_difference"]
        ),
        "primary_ci_lower": (
            primary["normal_approx_95_ci"][0]
            > t["primary_normal_approx_95_ci_lower_must_exceed"]
        ),
        "weighted_epistemic_difference": (
            weighted["mean_difference"]
            >= t["weighted_epistemic_gain_difference_minimum"]
        ),
        "unweighted_epistemic_noninferiority": (
            unweighted["mean_difference"]
            >= t["unweighted_epistemic_gain_difference_noninferiority_margin"]
        ),
        "absolute_net_harm": (
            crv["net_harm_rate"] <= t["crv_net_harm_rate_absolute_max"]
        ),
        "relative_net_harm": (
            crv["net_harm_rate"]
            <= udu["net_harm_rate"] + t["crv_net_harm_rate_margin_over_udu_max"]
        ),
    }

    if all(checks.values()):
        decision = "PASS"
    elif crv["mean_weighted_net_gain"] > udu["mean_weighted_net_gain"]:
        decision = "AMBER"
    else:
        decision = "FAIL_KILL_CRV_V1"

    no_op_subclaim = (
        "REALIZED"
        if crv["early_stop_rate"] >= t["no_op_realization_rate_for_no_op_subclaim"]
        else "WITHHELD"
    )
    return {
        "decision": decision,
        "checks": checks,
        "no_op_subclaim": no_op_subclaim,
    }


def run(plan_path: Path = DEFAULT_PLAN) -> dict:
    plan = json.loads(plan_path.read_text())
    if plan.get("status") != "FROZEN_BEFORE_GENERATOR_C_CONTROLLER_OUTCOMES":
        raise RuntimeError("refusing to run against a non-frozen Generator C plan")
    result = benchmark_c(
        generate_adversarial_world,
        n_worlds=int(plan["n_worlds"]),
        root_seed=int(plan["root_seed"]),
        max_budget=int(plan["max_budget"]),
    )
    return {
        "status": "EXACT_COMMITTED_RUNNER_EXECUTION",
        "plan": str(plan_path),
        "plan_status": plan["status"],
        "result": result,
        "frozen_decision": decide(result, plan),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    artifact = run(args.plan)
    text = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
