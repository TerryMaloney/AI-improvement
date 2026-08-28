"""exp003c — judge phrasing / length / format calibration.

This module measures the INSTRUMENT, not the system under test. It authors no
model outputs: the stimuli in `batteries/judge_calibration_v1.yaml` are fixed
answer texts written so that, within an item, every variant asserts the same
facts with the same correctness.

Why that matters more than it looks: because content is constant within an item,
any error in that item's rubric or ground truth applies equally to all its
variants and cancels in the within-item contrast. The calibration does not
depend on the author having written *correct* rubrics, only *consistent* ones.

The packets are built with the production `lab.grading.JUDGE_TEMPLATE`, because
the point is to calibrate the judging protocol exp003a/b will actually use.
Each judge sees ONE answer, blind: no variant label, no siblings, no hint that a
comparison exists. "Winner" is computed here from scores; no judge is asked to
pick one.

Known prior art (JudgeSense-style prompt-sensitivity work, verbosity/position
bias literature). This is an obligation exp001 and exp002 skipped, not a finding.
"""

from __future__ import annotations

import json
import re
import statistics
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from lab.grading import JUDGE_TEMPLATE, _HEDGE_RE, _PREMISE_RE, numbers_in

REPO_ROOT = Path(__file__).resolve().parent.parent
STIMULI_PATH = REPO_ROOT / "batteries" / "judge_calibration_v1.yaml"
RUNS_DIR = REPO_ROOT / "runs"

_BULLET_RE = re.compile(r"^\s*-\s+", re.M)
_HEADER_RE = re.compile(r"^[A-Z][A-Z ]{2,}$", re.M)


@dataclass
class Stimulus:
    item: str
    variant: str
    axis: str
    family: list[str]
    content_correct: bool
    question: str
    ground_truth: str
    rubric: str
    text: str
    fmt: str
    length: str

    @property
    def sid(self) -> str:
        return f"{self.item}.{self.variant}"

    def features(self) -> dict:
        t = self.text
        return {
            "chars": len(t),
            "words": len(t.split()),
            "lines": len([ln for ln in t.splitlines() if ln.strip()]),
            "bullets": len(_BULLET_RE.findall(t)),
            "headers": len(_HEADER_RE.findall(t)),
            "hedge_terms": sorted({m.group(0).lower() for m in _HEDGE_RE.finditer(t)}),
            "premise_terms": sorted({m.group(0).lower() for m in _PREMISE_RE.finditer(t)}),
            "numbers": sorted(set(numbers_in(t))),
        }


def load_stimuli(path: Path = STIMULI_PATH) -> list[Stimulus]:
    raw = yaml.safe_load(path.read_text())
    out: list[Stimulus] = []
    for item in raw["items"]:
        for vname, v in item["variants"].items():
            out.append(
                Stimulus(
                    item=item["id"],
                    variant=vname,
                    axis=item["axis"],
                    family=list(item.get("family") or []),
                    content_correct=bool(item["content_correct"]),
                    question=item["question"].strip(),
                    ground_truth=str(item["ground_truth"]).strip(),
                    rubric=str(item["judge_rubric"]).strip(),
                    text=str(v["text"]).strip(),
                    fmt=v["format"],
                    length=v["length"],
                )
            )
    return out


def load_items(path: Path = STIMULI_PATH) -> dict:
    raw = yaml.safe_load(path.read_text())
    return {i["id"]: i for i in raw["items"]}


def build_standard(s: Stimulus) -> str:
    """The GRADING STANDARD block, built the way production builds it."""
    return "\n\n".join(
        [
            "RUBRIC:\n" + s.rubric,
            "ESTABLISHED GROUND TRUTH:\n" + s.ground_truth,
        ]
    )


def build_packet(s: Stimulus) -> str:
    return JUDGE_TEMPLATE.format(
        question=s.question, standard=build_standard(s), answer=s.text
    )


def prepare(run_dir: Path, replicates: int = 3) -> dict:
    """Write one blind judge packet per (stimulus, replicate)."""
    packets = run_dir / "judge_packets"
    packets.mkdir(parents=True, exist_ok=True)
    (run_dir / "grades").mkdir(parents=True, exist_ok=True)

    stimuli = load_stimuli()
    manifest = []
    for s in stimuli:
        packet = build_packet(s)
        for r in range(1, replicates + 1):
            jid = f"{s.sid}.r{r}"
            (packets / f"{jid}.md").write_text(packet)
            manifest.append(
                {
                    "judgment_id": jid,
                    "item": s.item,
                    "variant": s.variant,
                    "replicate": r,
                    # metadata below is for ANALYSIS ONLY and is never in the packet
                    "axis": s.axis,
                    "content_correct": s.content_correct,
                    "format": s.fmt,
                    "length": s.length,
                    "features": s.features(),
                    "prompt": packet,
                }
            )
    (run_dir / "judge_manifest.json").write_text(
        json.dumps(
            {
                "experiment": "exp003c",
                "kind": "judge_calibration",
                "dispatches": len(manifest),
                "judge_model": "sonnet",
                "judge_saw_reasoning": False,
                "how_to_run": (
                    "Spawn `grader-judge` (model=sonnet) once per entry, pass `prompt` "
                    "verbatim, one item per agent, and write the returned JSON plus the "
                    "dispatch telemetry to grades/<judgment_id>.json."
                ),
                "judgments": manifest,
            },
            indent=2,
        )
    )
    return {"stimuli": len(stimuli), "dispatches": len(manifest), "run_dir": str(run_dir)}


# --------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------

@dataclass
class Judgement:
    item: str
    variant: str
    replicate: int
    score: float
    verdict: str
    axis: str
    content_correct: bool
    fmt: str
    length: str
    words: int
    chars: int
    tokens: int | None = None
    latency_ms: int | None = None
    judge_model: str = "sonnet"
    judge_saw_reasoning: bool = False
    raw: dict = field(default_factory=dict)


def load_judgements(run_dir: Path) -> list[Judgement]:
    man = json.loads((run_dir / "judge_manifest.json").read_text())
    meta = {j["judgment_id"]: j for j in man["judgments"]}
    out: list[Judgement] = []
    for p in sorted((run_dir / "grades").glob("*.json")):
        jid = p.stem
        m = meta.get(jid)
        if m is None:
            continue
        d = json.loads(p.read_text())
        out.append(
            Judgement(
                item=m["item"],
                variant=m["variant"],
                replicate=m["replicate"],
                score=float(d["score"]),
                verdict=str(d["verdict"]).upper(),
                axis=m["axis"],
                content_correct=m["content_correct"],
                fmt=m["format"],
                length=m["length"],
                words=m["features"]["words"],
                chars=m["features"]["chars"],
                tokens=d.get("judge_tokens"),
                latency_ms=d.get("judge_latency_ms"),
                raw=d,
            )
        )
    return out


def variant_means(js: list[Judgement]) -> dict[tuple[str, str], list[float]]:
    out: dict[tuple[str, str], list[float]] = {}
    for j in js:
        out.setdefault((j.item, j.variant), []).append(j.score)
    return out


def analyse(js: list[Judgement]) -> dict:
    """Compute exactly the pre-registered quantities. No others feed the bands."""
    by_variant = variant_means(js)
    mean_of = {k: statistics.mean(v) for k, v in by_variant.items()}
    spread_of = {k: (max(v) - min(v)) for k, v in by_variant.items()}

    twobytwo = [j for j in js if j.axis == "length_x_format"]

    def _delta(subset: list[Judgement], key, a: str, b: str) -> float | None:
        """Paired within-item delta: mean over items of (mean|a - mean|b)."""
        per_item: dict[str, dict[str, list[float]]] = {}
        for j in subset:
            per_item.setdefault(j.item, {}).setdefault(key(j), []).append(j.score)
        diffs = [
            statistics.mean(d[a]) - statistics.mean(d[b])
            for d in per_item.values()
            if a in d and b in d
        ]
        return statistics.mean(diffs) if diffs else None

    delta_length = _delta(twobytwo, lambda j: j.length, "verbose", "concise")
    delta_format = _delta(twobytwo, lambda j: j.fmt, "directive", "prose")
    correct = [j for j in twobytwo if j.content_correct]
    incorrect = [j for j in twobytwo if not j.content_correct]
    delta_len_correct = _delta(correct, lambda j: j.length, "verbose", "concise")
    delta_len_incorrect = _delta(incorrect, lambda j: j.length, "verbose", "concise")

    term_items = sorted({j.item for j in js if j.axis in ("terminology", "hedge_vocabulary")})
    range_term_by_item = {}
    for it in term_items:
        vals = [m for (i, _v), m in mean_of.items() if i == it]
        range_term_by_item[it] = max(vals) - min(vals) if vals else 0.0
    range_terminology = max(range_term_by_item.values()) if range_term_by_item else 0.0

    sigma_judge = statistics.mean(spread_of.values()) if spread_of else 0.0

    # within-item variant range across ALL items, for the noise-floor check
    item_ranges = {}
    for it in sorted({j.item for j in js}):
        vals = [m for (i, _v), m in mean_of.items() if i == it]
        item_ranges[it] = max(vals) - min(vals) if vals else 0.0
    mean_item_range = statistics.mean(item_ranges.values()) if item_ranges else 0.0

    return {
        "n_judgements": len(js),
        "delta_length": delta_length,
        "delta_format": delta_format,
        "delta_length_correct": delta_len_correct,
        "delta_length_incorrect": delta_len_incorrect,
        "range_terminology": range_terminology,
        "range_terminology_by_item": range_term_by_item,
        "sigma_judge": sigma_judge,
        "mean_item_range": mean_item_range,
        "item_ranges": item_ranges,
        "variant_means": {f"{i}.{v}": m for (i, v), m in sorted(mean_of.items())},
        "variant_spreads": {f"{i}.{v}": s for (i, v), s in sorted(spread_of.items())},
    }


def band(a: dict) -> dict:
    """Apply the PRE-REGISTERED bands. Thresholds live in
    experiments/exp003c_judge_calibration.yaml and are duplicated here only so
    the code can be tested; the YAML is the record of when they were fixed."""
    dl = abs(a["delta_length"] or 0.0)
    df = abs(a["delta_format"] or 0.0)
    rt = a["range_terminology"]
    worst = max(dl, df)

    if worst >= 0.15 or rt >= 0.20:
        b = "RED"
    elif worst >= 0.05 or rt >= 0.10:
        b = "AMBER"
    else:
        b = "GREEN"

    checks = []
    dlc = a["delta_length_correct"] or 0.0
    dli = a["delta_length_incorrect"] or 0.0
    rescues = dli >= 0.15 and abs(dlc) < 0.05
    if rescues:
        b = "RED"
        checks.append(
            "verbosity_rescues_errors TRIGGERED: delta_length on incorrect content "
            f"{dli:+.3f} while on correct content {dlc:+.3f} — band forced to RED."
        )
    else:
        checks.append(
            f"verbosity_rescues_errors not triggered (incorrect {dli:+.3f}, correct {dlc:+.3f})."
        )

    noisy = a["sigma_judge"] >= a["mean_item_range"]
    if noisy:
        checks.append(
            f"judge_noise_floor TRIGGERED: sigma_judge {a['sigma_judge']:.3f} >= mean "
            f"within-item variant range {a['mean_item_range']:.3f}. K rises to 3 for all "
            "judged trials in exp003a; the K=1-with-audit-sample rule is withdrawn."
        )
    else:
        checks.append(
            f"judge_noise_floor not triggered (sigma_judge {a['sigma_judge']:.3f} < mean "
            f"within-item variant range {a['mean_item_range']:.3f})."
        )

    return {"band": b, "worst_delta": worst, "range_terminology": rt, "checks": checks,
            "verbosity_rescues_errors": rescues, "judge_noise_floor": noisy}
