"""R3: multi-judge aggregation and reliability reporting.

exp001 measured the judge and found it imprecise: 67% verdict agreement on 12
paired judgements, mean |score difference| 0.133, max 0.40. That put a roughly
+/-8 accuracy-point noise floor under any judge-graded comparison at n=15 —
wide enough to swallow the directive_only result it was being used to evaluate.

A single judgement is therefore not a measurement. This module takes K
independent blind judgements per trial and reduces them to one score, while
keeping the spread so that "how much of this difference is grading noise?" stays
answerable instead of becoming a caveat.

Aggregation rules, fixed in advance:

  * SCORE   -> median of the K scores. Median, not mean, because a single judge
               reading a rubric differently should not drag the trial.
  * VERDICT -> majority. On a K-way tie with no majority the trial is marked
               DISPUTED and reported separately; it is NOT silently rounded to
               whichever verdict is convenient.
  * SPREAD  -> max-minus-min score, carried through to the report per trial and
               aggregated per condition.

A condition difference smaller than the measured noise floor is reported as
INCONCLUSIVE. That is a result, not a failure to get one.
"""

from __future__ import annotations

import json
import statistics
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

DISPUTED = "DISPUTED"


@dataclass
class AggregatedJudgement:
    trial_id: str
    verdict: str
    score: float
    k: int
    verdicts: list[str] = field(default_factory=list)
    scores: list[float] = field(default_factory=list)
    spread: float = 0.0
    unanimous: bool = False
    disputed: bool = False

    def as_detail(self) -> dict:
        return {
            "k_judges": self.k,
            "verdicts": self.verdicts,
            "scores": self.scores,
            "median_score": self.score,
            "spread": self.spread,
            "unanimous": self.unanimous,
            "disputed": self.disputed,
        }


def aggregate(trial_id: str, judgements: list[dict]) -> AggregatedJudgement:
    verdicts = [str(j["verdict"]).upper() for j in judgements]
    scores = [float(j["score"]) for j in judgements]
    counts = Counter(verdicts)
    top, n_top = counts.most_common(1)[0]
    disputed = n_top <= len(verdicts) / 2 and len(counts) > 1
    return AggregatedJudgement(
        trial_id=trial_id,
        verdict=DISPUTED if disputed else top,
        score=statistics.median(scores),
        k=len(judgements),
        verdicts=verdicts,
        scores=scores,
        spread=max(scores) - min(scores) if scores else 0.0,
        unanimous=len(counts) == 1,
        disputed=disputed,
    )


def load_multi(run_dir: Path) -> dict[str, list[dict]]:
    """Read runs/<exp>/grades_multi/<trial_id>.rN.json into per-trial lists."""
    out: dict[str, list[dict]] = {}
    d = run_dir / "grades_multi"
    if not d.exists():
        return out
    for p in sorted(d.glob("*.json")):
        trial_id = p.stem.rsplit(".r", 1)[0]
        try:
            out.setdefault(trial_id, []).append(json.loads(p.read_text()))
        except json.JSONDecodeError:
            continue
    return out


def reliability(agg: list[AggregatedJudgement]) -> dict:
    """Summary statistics over the multi-judged trials in one run."""
    multi = [a for a in agg if a.k > 1]
    if not multi:
        return {"n_multi_judged": 0}
    spreads = [a.spread for a in multi]
    return {
        "n_multi_judged": len(multi),
        "k": multi[0].k,
        "unanimous_verdict": sum(1 for a in multi if a.unanimous),
        "unanimous_rate": sum(1 for a in multi if a.unanimous) / len(multi),
        "disputed": sum(1 for a in multi if a.disputed),
        "mean_spread": statistics.mean(spreads),
        "max_spread": max(spreads),
        "spread_ge_0_20": sum(1 for s in spreads if s >= 0.20),
        "disputed_trials": [a.trial_id for a in multi if a.disputed],
    }


def noise_floor(agg: list[AggregatedJudgement], n_trials_per_condition: int) -> float:
    """Accuracy points below which a condition difference is not interpretable.

    Derived, not assumed: mean per-trial judge spread, scaled by the share of
    trials in a condition that are judge-graded. A condition where nothing is
    judge-graded has a floor of 0 from this source.
    """
    multi = [a for a in agg if a.k > 1]
    if not multi or not n_trials_per_condition:
        return 0.0
    mean_spread = statistics.mean(a.spread for a in multi)
    judged_share = len(multi) / n_trials_per_condition
    return mean_spread * judged_share
