"""Lab CLI.

    python -m lab prepare  <exp>          generate trial packets + manifest
    python -m lab status   <exp>          how far along a run is
    python -m lab ingest   <exp>          load solver answers, run the audit
    python -m lab grade    <exp>          deterministic grading + judge packets
    python -m lab ingest-judgments <exp>  load judge verdicts
    python -m lab report   <exp>          write runs/<exp>/report.md
    python -m lab compare  <exp> <exp>…   cross-experiment table
    python -m lab refresh                 what needs re-verifying
    python -m lab route    "<question>"   inspect the layer's routing on one question
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from lab.trials import RUNS_DIR, ExperimentConfig, prepare


def _run_dir(exp: str) -> Path:
    d = RUNS_DIR / exp
    if not d.exists():
        sys.exit(f"no run directory for {exp!r} — run `python -m lab prepare {exp}` first")
    return d


def cmd_prepare(args) -> None:
    config = ExperimentConfig.load(args.experiment)
    result = prepare(config)
    print(json.dumps(result, indent=2))
    print(f"\nManifest: {config.run_dir() / 'manifest.json'}")
    print("Next: run the solver agents per docs/lab_manual.md, then `python -m lab ingest "
          f"{config.id}`.")


def cmd_status(args) -> None:
    from lab.store import Store

    run_dir = _run_dir(args.experiment)
    store = Store(run_dir / "results.db")
    trials = store.trials()
    answered = store.answered_ids()
    graded = store.graded_ids()
    store.close()
    missing = [t["trial_id"] for t in trials if t["trial_id"] not in answered]
    print(f"trials:   {len(trials)}")
    print(f"answered: {len(answered)}")
    print(f"graded:   {len(graded)}")
    if missing:
        print(f"\nmissing answers ({len(missing)}):")
        for m in missing[: args.limit]:
            print(f"  {m}")
        if len(missing) > args.limit:
            print(f"  … and {len(missing) - args.limit} more")


def cmd_ingest(args) -> None:
    from lab.ingest import ingest

    result = ingest(_run_dir(args.experiment))
    print(json.dumps(result, indent=2))
    if result["audit_flags"]:
        print("\nAUDIT FLAGS PRESENT — read these before trusting any number from this run.")


def cmd_grade(args) -> None:
    from lab.grading import grade_experiment
    from lab.store import Store

    run_dir = _run_dir(args.experiment)
    store = Store(run_dir / "results.db")
    batteries = store.config().get("batteries", [])
    store.close()
    result = grade_experiment(run_dir, batteries)
    print(json.dumps({k: v for k, v in result.items() if k != "judge_packets"}, indent=2))
    if result["judge_packets"]:
        print(f"\n{len(result['judge_packets'])} trial(s) need a judge.")
        print(f"Manifest: {run_dir / 'judge_manifest.json'}")


def cmd_ingest_judgments(args) -> None:
    from lab.grading import ingest_judgments

    print(json.dumps(ingest_judgments(_run_dir(args.experiment)), indent=2))


def cmd_report(args) -> None:
    from lab.report import write_report

    path = write_report(_run_dir(args.experiment))
    print(f"wrote {path}")


def cmd_compare(args) -> None:
    from lab.report import compare

    print(compare([_run_dir(e) for e in args.experiments]))


def cmd_refresh(args) -> None:
    from lab.refresh import refresh_queue, render

    queue = refresh_queue(date.fromisoformat(args.as_of) if args.as_of else None)
    print(render(queue))
    if args.json:
        print("\n" + json.dumps(queue, indent=2))


def cmd_route(args) -> None:
    from epistemic.registry import seed_registry
    from epistemic.router import route

    rt = route(
        args.question,
        asked_on=date.fromisoformat(args.as_of) if args.as_of else None,
        registry=seed_registry(),
    )
    print(json.dumps(rt.as_dict(), indent=2))
    print("\n--- prompt block that would be injected ---\n")
    print(rt.prompt_block())


def cmd_egress_probe(args) -> None:
    """Record an egress observation made by the orchestrator.

    This command does not perform the probe, and that is deliberate. The lab's
    Python has no network tools; the probe is performed by the operator session
    that actually holds WebSearch and WebFetch, and this writes down what it saw.
    A `--detail` string describing the observed behaviour is required, so the
    artefact carries evidence and not just two booleans.
    """
    from lab.states import EGRESS_PROBE_PATH, EgressStatus

    status = EgressStatus(
        web_search=args.search == "ok",
        web_fetch=args.fetch == "ok",
        probed_at=(args.as_of or datetime.now(timezone.utc).isoformat(timespec="seconds")),
        detail=args.detail,
    )
    EGRESS_PROBE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = status.as_dict()
    EGRESS_PROBE_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    dated = EGRESS_PROBE_PATH.parent / f"probe-{status.probed_at[:10]}.json"
    dated.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))
    print(f"\nwrote {EGRESS_PROBE_PATH} and {dated}")


def cmd_placebo(args) -> None:
    """Show the directive and its placebo side by side, with the match report."""
    from epistemic.registry import seed_registry
    from epistemic.router import route
    from lab.placebo import build, match_report

    rt = route(
        args.question,
        asked_on=date.fromisoformat(args.as_of) if args.as_of else None,
        registry=seed_registry(),
    )
    block = rt.prompt_block()
    placebo = build(block, args.question)
    print("--- directive ---\n"); print(block)
    print("\n--- placebo ---\n"); print(placebo)
    print("\n--- six-axis match ---\n")
    print(json.dumps(match_report(block, placebo), indent=2, default=str))


def cmd_spec(args) -> None:
    """Render a battery's frozen specification document."""
    from lab.battery import load_answers, load_battery
    from lab.spec import render_specification

    battery = load_battery(args.battery)
    text = render_specification(battery, load_answers().get("answers", {}))
    if args.write:
        out = Path("docs") / f"{battery.id.upper()}_SPECIFICATION.md"
        out.write_text(text + "\n")
        print(f"wrote {out} ({len(text.splitlines())} lines)")
    else:
        print(text)


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="lab", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    for name, fn, needs_exp in [
        ("prepare", cmd_prepare, True),
        ("ingest", cmd_ingest, True),
        ("grade", cmd_grade, True),
        ("ingest-judgments", cmd_ingest_judgments, True),
        ("report", cmd_report, True),
    ]:
        sp = sub.add_parser(name)
        if needs_exp:
            sp.add_argument("experiment")
        sp.set_defaults(func=fn)

    sp = sub.add_parser("status")
    sp.add_argument("experiment")
    sp.add_argument("--limit", type=int, default=20)
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("compare")
    sp.add_argument("experiments", nargs="+")
    sp.set_defaults(func=cmd_compare)

    sp = sub.add_parser("refresh")
    sp.add_argument("--as-of", default=None)
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_refresh)

    sp = sub.add_parser("route")
    sp.add_argument("question")
    sp.add_argument("--as-of", default=None)
    sp.set_defaults(func=cmd_route)

    sp = sub.add_parser("egress-probe")
    sp.add_argument("--search", choices=["ok", "blocked"], required=True)
    sp.add_argument("--fetch", choices=["ok", "blocked"], required=True)
    sp.add_argument("--detail", required=True,
                    help="what was actually observed — the evidence behind the two flags")
    sp.add_argument("--as-of", default=None)
    sp.set_defaults(func=cmd_egress_probe)

    sp = sub.add_parser("spec")
    sp.add_argument("battery")
    sp.add_argument("--write", action="store_true")
    sp.set_defaults(func=cmd_spec)

    sp = sub.add_parser("placebo")
    sp.add_argument("question")
    sp.add_argument("--as-of", default=None)
    sp.set_defaults(func=cmd_placebo)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
