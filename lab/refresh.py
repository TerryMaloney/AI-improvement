"""What needs re-verifying before it can be trusted.

Handoff packet §5 applies the project's own TTL rule to the project's own
facts, and observes that nothing was re-checked when the packet was written.
This module is that check, automated: it reports every entity past its TTL and
every answer-key entry whose status is not `verified`, so "we should re-verify
that" becomes a command instead of an intention.

It deliberately does NOT go and search. Refreshing is an action with a cost and
a judgement call about what is worth checking; this tells you what the queue
is, and the operator (or the run-experiment skill) works it.
"""

from __future__ import annotations

from datetime import date

from epistemic.registry import EntityRegistry, seed_registry
from lab.battery import SCORABLE_STATUSES, load_answers


def refresh_queue(as_of: date | None = None, registry: EntityRegistry | None = None) -> dict:
    as_of = as_of or date.today()
    registry = registry if registry is not None else seed_registry()

    entities = [
        {
            "key": rec.key,
            "description": rec.description,
            "bucket": rec.bucket.value,
            "last_verified": rec.last_verified.isoformat() if rec.last_verified else None,
            "age_days": rec.age_days(as_of),
            "reason": reason,
            "threshold_calibrated": rec.threshold_is_calibrated,
        }
        for rec, reason in registry.needing_reverification(as_of)
    ]

    key = load_answers().get("answers", {})
    unverified = [
        {
            "question_id": qid,
            "status": entry.get("status"),
            "verified_as_of": entry.get("verified_as_of"),
            "notes": (entry.get("notes") or "").strip(),
            "source": (entry.get("source") or "").strip(),
        }
        for qid, entry in key.items()
        if entry.get("status") not in SCORABLE_STATUSES
    ]

    return {
        "as_of": as_of.isoformat(),
        "entities_needing_reverification": entities,
        "answers_not_scorable": unverified,
        "blocking": bool(unverified),
    }


def render(queue: dict) -> str:
    lines = [f"Refresh queue as of {queue['as_of']}", ""]

    ents = queue["entities_needing_reverification"]
    lines.append(f"ENTITIES PAST TTL ({len(ents)})")
    if not ents:
        lines.append("  (none)")
    for e in ents:
        calib = "" if e["threshold_calibrated"] else "  [threshold uncalibrated]"
        lines.append(f"  - {e['key']}: {e['reason']}{calib}")
    lines.append("")

    ans = queue["answers_not_scorable"]
    lines.append(f"ANSWER-KEY ENTRIES NOT SCORABLE ({len(ans)})")
    if not ans:
        lines.append("  (none)")
    for a in ans:
        note = f" — {a['notes']}" if a["notes"] else ""
        lines.append(f"  - {a['question_id']}: status={a['status']}"
                     f"{' verified_as_of=' + a['verified_as_of'] if a.get('verified_as_of') else ''}{note}")
    lines.append("")

    if queue["blocking"]:
        lines.append(
            "These questions will report as UNGRADED until their ground truth is verified\n"
            "and answers.yaml is updated with status: verified. That refusal is deliberate:\n"
            "scoring against unverified ground truth produces a number that looks measured\n"
            "and isn't."
        )
    else:
        lines.append("All answer-key entries are scorable.")
    return "\n".join(lines)
