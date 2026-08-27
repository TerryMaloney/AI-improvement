"""Grading: deterministic first, judge only where deterministic can't reach.

Order is deliberate and mirrors the system under test — "deterministic checks
first; LLM-judge fallback" is the packet's own defence against verifier
regress. A judge that grades what a string comparison could have graded is an
expensive way to add variance.

Three verdicts a trial can end in *without* being scored, all of them real
outcomes rather than errors:

  UNGRADED     the answer key entry is `stale` or `unverified`. We refuse to
               score against ground truth we have not checked. This is the
               single most important line in the module: a lab that grades
               against a guess manufactures a number that looks measured.
  NEEDS_JUDGE  deterministic grading was attempted and could not decide.
  NO_ANSWER    the trial was never run or the solver returned nothing parseable.

BLIND GRADING: judge packets contain the question, the rubric, and the answer.
They never contain the condition name, the model name, or the trial id, so a
judge cannot know whether it is grading a treatment or a control.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from lab.battery import Battery, Question, load_answers, load_batteries, scorable
from lab.store import Store

PASS, FAIL, PARTIAL = "PASS", "FAIL", "PARTIAL"
UNGRADED, NEEDS_JUDGE, NO_ANSWER = "UNGRADED", "NEEDS_JUDGE", "NO_ANSWER"

SCORE = {PASS: 1.0, PARTIAL: 0.5, FAIL: 0.0}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "").lower()
    text = re.sub(r"[‘’“”]", "'", text)
    return re.sub(r"\s+", " ", text).strip()


_NUMBER_RE = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


def numbers_in(text: str) -> list[float]:
    out = []
    for m in _NUMBER_RE.finditer(text or ""):
        try:
            out.append(float(m.group(0).replace(",", "")))
        except ValueError:
            pass
    return out


# Conduct signals, computed for every answer regardless of verdict. These are
# how "did the procedure change the *shape* of the answer" gets measured even
# on questions where correctness is unscorable.
_HEDGE_RE = re.compile(
    r"\b(?:as of|may have changed|might have changed|i'?m not certain|not certain|"
    r"uncertain|estimates? (?:range|vary)|approximately|roughly|verify|check a current|"
    r"my (?:training|knowledge) (?:data|cutoff)|could be out of date|subject to change)\b",
    re.I,
)
_PREMISE_RE = re.compile(
    r"\b(?:false premise|incorrect premise|premise (?:is|of the question is) (?:false|incorrect|mistaken)|"
    r"the question (?:assumes|presupposes)|did not (?:happen|occur|win)|never (?:won|happened|occurred|left))\b",
    re.I,
)


@dataclass
class GradeResult:
    verdict: str
    score: float | None
    method: str
    grader: str
    detail: dict = field(default_factory=dict)


def conduct_signals(answer_text: str, payload: dict) -> dict:
    t = answer_text or ""
    return {
        "answer_chars": len(t),
        "hedged": bool(_HEDGE_RE.search(t)),
        "flagged_premise": bool(_PREMISE_RE.search(t)),
        "abstained": bool(payload.get("abstained")),
        "searches_used": payload.get("searches_used"),
        "source_count": len(payload.get("sources") or []),
    }


# --------------------------------------------------------------------------
# Deterministic graders
# --------------------------------------------------------------------------

def grade_contains_any(answer: str, entry: dict) -> GradeResult:
    norm = normalize(answer)
    accept = [normalize(a) for a in entry.get("accept", []) if a]
    if not accept:
        return GradeResult(NEEDS_JUDGE, None, "contains_any", "deterministic",
                           {"reason": "no accept strings in answer key"})
    hit = next((a for a in accept if a and a in norm), None)
    if hit is None:
        return GradeResult(FAIL, 0.0, "contains_any", "deterministic",
                           {"reason": "no accepted value found in answer"})
    also = [normalize(a) for a in entry.get("also_expect", []) if a]
    missing = [a for a in also if a not in norm]
    if missing:
        return GradeResult(PARTIAL, 0.5, "contains_any", "deterministic",
                           {"matched": hit, "missing_required_detail": missing})
    return GradeResult(PASS, 1.0, "contains_any", "deterministic", {"matched": hit})


def grade_trap_detected(answer: str, entry: dict) -> GradeResult:
    norm = normalize(answer)
    for bad in entry.get("reject", []):
        if normalize(bad) in norm:
            return GradeResult(FAIL, 0.0, "trap_detected", "deterministic",
                               {"reason": f"answer contains rejected content: {bad!r}"})
    markers = [normalize(m) for m in entry.get("accept_trap_markers", [])]
    hit = next((m for m in markers if m and m in norm), None)
    if hit:
        return GradeResult(PASS, 1.0, "trap_detected", "deterministic", {"matched_marker": hit})
    # The model may have rejected the premise in wording the marker list does
    # not cover. Escalating is honest; scoring FAIL here would penalise
    # vocabulary rather than reasoning.
    return GradeResult(NEEDS_JUDGE, None, "trap_detected", "deterministic",
                       {"reason": "no known trap marker matched; needs a judge to decide "
                                  "whether the premise was rejected in other words"})


def grade_numeric(answer: str, entry: dict, grading: dict) -> GradeResult:
    truth = entry.get("ground_truth")
    if not isinstance(truth, (int, float)):
        return GradeResult(NEEDS_JUDGE, None, "numeric", "deterministic",
                           {"reason": "ground truth is not numeric"})
    tol = float(grading.get("tolerance", 0))
    found = numbers_in(answer)
    rejects = [float(b) for b in (entry.get("reject_values") or [])]

    # A tolerance wide enough to reach a distractor silently disables the
    # distractor check and scores the trap answer as correct. That is how f10
    # ("77.5 km/h", tolerance 0.5, truth 78) passed in the first version of
    # this grader — caught by tests/test_pipeline.py, not by reading the code.
    # Refuse the configuration instead of producing a wrong number from it.
    swallowed = [b for b in rejects if abs(b - float(truth)) <= tol]
    if swallowed:
        return GradeResult(
            UNGRADED, None, "numeric", "deterministic",
            {"reason": f"grading misconfigured: tolerance {tol} reaches distractor value(s) "
                       f"{swallowed} around ground truth {truth}, so the distractor check "
                       f"cannot fire. Tighten `tolerance` in the battery file."},
        )

    for bad in rejects:
        if any(abs(n - float(bad)) <= tol for n in found) and not any(
            abs(n - float(truth)) <= tol for n in found
        ):
            return GradeResult(FAIL, 0.0, "numeric", "deterministic",
                               {"reason": f"answer gives the distractor value {bad}",
                                "numbers_found": found})
    if any(abs(n - float(truth)) <= tol for n in found):
        return GradeResult(PASS, 1.0, "numeric", "deterministic", {"numbers_found": found})
    return GradeResult(FAIL, 0.0, "numeric", "deterministic",
                       {"reason": "correct value not present", "numbers_found": found})


DETERMINISTIC_METHODS = {"contains_any", "trap_detected", "numeric"}


def grade_deterministically(question: Question, entry: dict | None, answer: str) -> GradeResult:
    if entry is None:
        return GradeResult(UNGRADED, None, "none", "deterministic",
                           {"reason": f"no answer-key entry for {question.id}"})
    if not scorable(entry):
        return GradeResult(
            UNGRADED, None, "none", "deterministic",
            {"reason": f"ground truth status is {entry.get('status')!r} — refusing to score "
                       f"against unverified ground truth. Run `python -m lab refresh`."},
        )
    method = question.grading_method
    if method == "contains_any":
        return grade_contains_any(answer, entry)
    if method == "trap_detected":
        return grade_trap_detected(answer, entry)
    if method == "numeric":
        return grade_numeric(answer, entry, question.grading)
    return GradeResult(NEEDS_JUDGE, None, method, "deterministic",
                       {"reason": "question is judge-graded by design"})


# --------------------------------------------------------------------------
# Judge packets
# --------------------------------------------------------------------------

JUDGE_TEMPLATE = """You are grading ONE response for a controlled evaluation.

You are grading blind: you are not told which system, model, or condition
produced this response, and you must not speculate about it. Grade only what
is written.

--------------------------------------------------------------------------
QUESTION THAT WAS ASKED
--------------------------------------------------------------------------
{question}

--------------------------------------------------------------------------
GRADING STANDARD
--------------------------------------------------------------------------
{standard}

--------------------------------------------------------------------------
THE RESPONSE TO GRADE
--------------------------------------------------------------------------
{answer}

--------------------------------------------------------------------------
HOW TO GRADE
--------------------------------------------------------------------------
Apply the standard above strictly. Two failure directions matter equally and
you must penalise both:

  OVERCONFIDENCE — asserting a contested, stale, or unknowable thing flatly.
  OVER-ABSTENTION — refusing to answer, or retreating to "it depends", when the
                    standard says a substantive answer was available.

A response that is factually right but epistemically wrong (a correct number
asserted with false certainty where the standard requires uncertainty) does not
pass. Neither does a response that hedges its way out of a question it could
have answered.

Return a single JSON object and nothing else:

{{
  "verdict": "<PASS | PARTIAL | FAIL>",
  "score": <0.0 to 1.0>,
  "criteria": {{ "<criterion name>": <true|false>, ... }},
  "reasoning": "<two or three sentences: what the standard required, and what "
               "this response did or did not do>"
}}"""


def build_judge_standard(question: Question, entry: dict | None, conduct: dict | None) -> str:
    parts: list[str] = []
    if question.correct_handling:
        parts.append("CORRECT HANDLING:\n" + question.correct_handling)
    if entry:
        if entry.get("judge_rubric"):
            parts.append("RUBRIC:\n" + entry["judge_rubric"].strip())
        gt = entry.get("ground_truth")
        if gt and scorable(entry):
            parts.append("ESTABLISHED GROUND TRUTH:\n" + str(gt).strip())
        elif not scorable(entry):
            parts.append(
                "GROUND TRUTH: not established in this repo for this question. Grade ONLY "
                "the epistemic conduct described above — do NOT assert a factual answer of "
                "your own and grade against it."
            )
        if entry.get("status") == "rubric_only" and conduct:
            parts.append(
                "CONDUCT CRITERIA (apply all four, and report each in `criteria`):\n"
                + "\n".join(f"- {k}: {v.strip()}" for k, v in conduct.items())
            )
    if question.expected_claim_type:
        parts.append(
            f"EXPECTED CLAIM TYPE: {question.expected_claim_type}. A response that treats this "
            f"as a different kind of claim has made a substantive error, not a stylistic one."
        )
    return "\n\n".join(parts) if parts else "Grade for accuracy and epistemic honesty."


def write_judge_packet(
    run_dir: Path, trial_id: str, question: Question, entry: dict | None, answer: str, conduct: dict | None
) -> Path:
    packet = JUDGE_TEMPLATE.format(
        question=question.text,
        standard=build_judge_standard(question, entry, conduct),
        answer=answer.strip() or "(the response was empty)",
    )
    path = run_dir / "judge_packets" / f"{trial_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(packet)
    return path


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def grade_experiment(run_dir: Path, battery_names: list[str]) -> dict:
    """Grade every answered trial deterministically; emit judge packets for the
    rest. Returns a summary dict."""
    store = Store(run_dir / "results.db")
    answers_key = load_answers()
    entries = answers_key.get("answers", {})
    conduct_criteria = answers_key.get("conduct_criteria", {})

    questions: dict[str, Question] = {}
    for b in load_batteries(battery_names):
        for q in b.questions:
            questions[q.id] = q

    summary = {"graded": 0, "needs_judge": 0, "ungraded": 0, "no_answer": 0, "judge_packets": []}
    judge_manifest = []

    for row in store.joined():
        trial_id = row["trial_id"]
        q = questions.get(row["question_id"])
        if q is None:
            continue
        raw = store.conn.execute(
            "SELECT raw_json, answer_text FROM answers WHERE trial_id=?", (trial_id,)
        ).fetchone()
        if raw is None or not (raw["answer_text"] or "").strip():
            store.save_grade(trial_id, NO_ANSWER, None, "none", "deterministic",
                             {"reason": "no answer recorded for this trial"})
            summary["no_answer"] += 1
            continue

        answer_text = raw["answer_text"]
        payload = json.loads(raw["raw_json"] or "{}")
        entry = entries.get(row["question_id"])
        result = grade_deterministically(q, entry, answer_text)
        detail = dict(result.detail)
        detail["conduct"] = conduct_signals(answer_text, payload)

        if result.verdict == NEEDS_JUDGE:
            path = write_judge_packet(run_dir, trial_id, q, entry, answer_text, conduct_criteria)
            detail["judge_packet"] = str(path.relative_to(run_dir))
            judge_manifest.append({"trial_id": trial_id, "judge_packet": str(path), "prompt": path.read_text()})
            summary["needs_judge"] += 1
        elif result.verdict == UNGRADED:
            summary["ungraded"] += 1
        else:
            summary["graded"] += 1

        store.save_grade(trial_id, result.verdict, result.score, result.method, result.grader, detail)

    if judge_manifest:
        (run_dir / "judge_manifest.json").write_text(
            json.dumps(
                {
                    "count": len(judge_manifest),
                    "grades_dir": str(run_dir / "grades"),
                    "how_to_run": (
                        "For each entry: spawn the `grader-judge` agent, pass `prompt` verbatim, "
                        "and write the returned JSON to <grades_dir>/<trial_id>.json. Then run "
                        "`python -m lab ingest-judgments <exp>`."
                    ),
                    "judgments": judge_manifest,
                },
                indent=2,
            )
        )
    summary["judge_packets"] = [j["trial_id"] for j in judge_manifest]
    store.close()
    return summary


def ingest_judgments(run_dir: Path) -> dict:
    """Load judge verdicts written to runs/<exp>/grades/*.json."""
    store = Store(run_dir / "results.db")
    loaded, skipped = 0, []
    for path in sorted((run_dir / "grades").glob("*.json")):
        trial_id = path.stem
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            skipped.append(f"{trial_id}: unparseable JSON ({e})")
            continue
        verdict = str(payload.get("verdict", "")).upper()
        if verdict not in SCORE:
            skipped.append(f"{trial_id}: unknown verdict {verdict!r}")
            continue
        score = payload.get("score")
        score = float(score) if isinstance(score, (int, float)) else SCORE[verdict]
        prior = store.conn.execute(
            "SELECT detail_json FROM grades WHERE trial_id=?", (trial_id,)
        ).fetchone()
        detail = json.loads(prior["detail_json"]) if prior and prior["detail_json"] else {}
        detail["judge"] = payload
        store.save_grade(trial_id, verdict, score, "judge", "grader-judge", detail)
        loaded += 1
    store.close()
    return {"loaded": loaded, "skipped": skipped}
