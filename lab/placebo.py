"""The placebo directive — generic careful instruction, minus the mechanism.

`baseline` vs `directive_only` cannot separate "the epistemic mechanism works"
from "being given a block of serious-looking instructions works". exp001 and
exp002 ran without that control, so E4 (prompt length / placebo) has never been
excluded. This module builds the missing arm.

A placebo has to be **matched** and **inert** at the same time, and those pull
against each other:

* Matched on six axes (plan §4): word count within ±10%, same number of
  imperative bullets, same section structure, same formatting markers, comparable
  expected response effort, same register. A shorter or flimsier block does not
  control for the directive — it controls for a different, weaker thing.
* Inert: no claim types, no premise-checking, no sourcing, no verification, no
  freshness, no abstention, no calibration, no budgets.

So the placebo lives in a neighbouring domain — **how the answer is presented** —
which is serious, non-jocular, asks comparable elaboration, and has nothing to do
with how a claim is established. It is deliberately not about *reasoning* either:
"check your work" would import E2 into the control and defeat the purpose.

Two design decisions worth stating outright:

1. **No numeric quota, ever** (FD-5). The obvious way to mirror
   `SEARCH BUDGET: 2 searches` is a count of your own — "cover three angles",
   "write two paragraphs". Forbidden: exp003c measured that response length moves
   a judged score across a rubric boundary, so a length instruction in the
   placebo would manipulate the exact variable the placebo exists to hold still.
   The budget line is mirrored with inert prose of matched length instead, and
   the placebo's own word count is hit by *choosing among pre-written variants*,
   never by telling the solver about length.

2. **The shape is parsed from the real block, not hard-coded.** The placebo
   mirrors whatever `Route.prompt_block()` actually emitted for that question —
   including the freshness section when present and the routing caveats when
   present — so per-question length tracking is structural rather than average.
   If the directive changes shape, the placebo follows, and the matching tests
   fail loudly rather than drifting quietly.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

WORD_TOLERANCE = 0.10

# Vocabulary that would make the placebo an active treatment. Checked by test,
# case-insensitively, against every generated block.
# Vocabulary that would make the placebo an instruction about how much to write.
# Distinct from FORBIDDEN, which is about the epistemic mechanism: this list
# exists because exp003c measured that response length moves a judged score
# across a rubric boundary, so the placebo must not touch length at all (FD-5).
SIZE_TERMS = (
    "at least", "at most", "no more than", "no fewer", "paragraph", "word count",
    "length", "long enough", "concise", "verbose", "brief", "thorough",
    "in detail", "detailed", "comprehensive", "exhaustive",
)

FORBIDDEN = (
    "empirical", "normative", "predictive", "definitional", "deterministic",
    "claim type", "premise", "source", "verify", "verified", "verification",
    "fresh", "stale", "conflict", "budget", "independent", "evidence",
    "abstain", "calibrat", "search", "retriev", "cite", "citation", "fact-check",
)

_BULLET = re.compile(r"^- ")
_INLINE_HEADER = re.compile(r"^[A-Z][A-Z ]{2,}: \S")
_SECTION_HEADER = re.compile(r"^[A-Z][A-Z ]{2,}.*:$")


# --------------------------------------------------------------------------
# Shape of the block being mirrored
# --------------------------------------------------------------------------

@dataclass
class Segment:
    kind: str                      # "inline" | "section"
    header_has_emdash: bool = False
    n_lead_prose: int = 0
    n_bullets: int = 0
    n_trailing_prose: int = 0
    words: int = 0


@dataclass
class Shape:
    segments: list[Segment] = field(default_factory=list)
    words: int = 0

    @property
    def n_bullets(self) -> int:
        return sum(s.n_bullets for s in self.segments)


def _words(text: str) -> int:
    return len(text.split())


def parse_shape(block: str) -> Shape:
    """Read the structure of a real directive block.

    Line-based rather than clever: `Route.prompt_block()` emits one bullet per
    line and one blank line between segments, so structure is recoverable
    without guessing.
    """
    shape = Shape(words=_words(block))
    current: Segment | None = None
    for raw in block.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            continue
        if _BULLET.match(line):
            if current is None:                      # a bullet with no header
                current = Segment(kind="section")
                shape.segments.append(current)
            current.n_bullets += 1
        elif _SECTION_HEADER.match(line):
            current = Segment(kind="section", header_has_emdash="—" in line)
            shape.segments.append(current)
        elif _INLINE_HEADER.match(line):
            current = Segment(kind="inline")
            shape.segments.append(current)
        else:
            if current is None:
                current = Segment(kind="section")
                shape.segments.append(current)
            if current.n_bullets:
                current.n_trailing_prose += 1
            else:
                current.n_lead_prose += 1
        if current is not None:
            current.words += _words(line)
    return shape


# --------------------------------------------------------------------------
# Inert content pools. Every entry has short / medium / long variants so the
# generator can hit a word target by SELECTION rather than by instruction.
# --------------------------------------------------------------------------

_REGISTERS = ("EXPLANATORY", "DESCRIPTIVE", "ANALYTIC", "EXPOSITORY", "INSTRUCTIONAL")

# Every pool entry carries variants at several lengths AND variants with and
# without an em dash. Both are match axes (word count; formatting markers), and
# both must be hit by SELECTION — the generator has no other lever, because
# instructing the model about either would make the placebo a treatment (FD-5).
_LEAD = [(
    "This is an {reg} response — it is read by someone deciding what to do with it, so "
    "its shape is part of what it communicates.",
    "This is an {reg} response — it will be read once, by someone deciding what to do "
    "with it, so how it is arranged is part of what it communicates.",
    "This is an {reg} response — it will be read once, in one pass, by someone deciding "
    "what to do with it next, so the way it is arranged is not decoration but part of "
    "what it actually communicates.",
    "This is an {reg} response. It will be read once, by someone deciding what to do "
    "with it, so how it is arranged is part of what it communicates.",
)]

# Presentation craft. Nothing here changes what a correct answer contains, and
# nothing here is a reasoning aid — "check your work" would import E2 into the
# control and defeat the purpose of having one.
_BULLETS = [
    (
        "Decide who the answer is for before writing it, and keep that reader in view.",
        "Decide who the answer is for before you start writing it, and keep that reader in "
        "view while you write, rather than settling it afterwards.",
        "Decide who the answer is for before you start writing it, and hold that reader in "
        "view the whole way through; an answer written for nobody in particular tends to be "
        "arranged for the writer's convenience instead.",
        "Decide who the answer is for before you start writing it — an answer written for "
        "nobody in particular gets arranged for the writer's convenience instead.",
    ),
    (
        "Put the part that answers the question where a reader reaches it first.",
        "Put the part that actually answers the question where a reader reaches it first, "
        "ahead of the material that leads up to it.",
        "Put the part that actually answers the question where a reader reaches it first, "
        "ahead of the material that leads up to it; a reader who stops halfway should still "
        "have the thing they came for.",
        "Put the part that answers the question where a reader reaches it first — someone "
        "who stops halfway should still have the thing they came for.",
    ),
    (
        "Use one word per idea, and keep using the same word for it throughout.",
        "Use one word per idea and keep using that same word throughout; varying it for "
        "style makes a reader wonder whether the meaning varied too.",
        "Use one word per idea and keep using that same word for it all the way through the "
        "answer; varying the term for the sake of style makes a reader stop and wonder "
        "whether the meaning changed as well, which costs them more than the repetition would.",
        "Use one word per idea and keep using it — varying the term for style makes a "
        "reader stop and wonder whether the meaning varied too.",
    ),
    (
        "Keep one idea to a sentence; a sentence carrying three of them hides two.",
        "Keep roughly one idea to a sentence, because a sentence carrying three of them "
        "usually delivers one and hides the other two.",
        "Keep roughly one idea to a sentence. A sentence made to carry three of them "
        "usually delivers the first clearly and buries the other two in subordinate clauses "
        "where a reader skims past them.",
        "Keep roughly one idea to a sentence — one made to carry three usually delivers the "
        "first and buries the other two where a reader skims past them.",
    ),
    (
        "Prefer the concrete formulation where both are available.",
        "Where a concrete formulation and an abstract one both say the thing, prefer the "
        "concrete one.",
        "Where a concrete formulation and an abstract one would both say the thing "
        "accurately, prefer the concrete one; abstraction is worth its cost only when it "
        "covers cases the concrete version would miss.",
        "Prefer the concrete formulation where both would say the thing — abstraction earns "
        "its cost only when it covers cases the concrete version would miss.",
    ),
    (
        "Make the seams between the parts of the answer visible rather than implied.",
        "Make the seams between the parts of the answer visible rather than leaving a "
        "reader to infer where one part ended and the next began.",
        "Make the seams between the parts of the answer visible rather than leaving a reader "
        "to infer where one part ended and the next began; an unmarked transition is a place "
        "where attention is quietly lost.",
        "Make the seams between the parts visible rather than implied — an unmarked "
        "transition is a place where a reader's attention is quietly lost.",
    ),
    (
        "Expand shorthand the first time it appears rather than assuming it lands.",
        "Expand any shorthand the first time it appears rather than assuming it lands, "
        "since the cost of doing so is one clause.",
        "Expand any shorthand or compressed phrase the first time it appears rather than "
        "assuming it lands with this particular reader; the cost of doing so is one clause, "
        "and the cost of not doing so is everything that follows it.",
        "Expand shorthand the first time it appears — the cost of doing so is one clause, "
        "and the cost of not doing so is everything that follows it.",
    ),
    (
        "Stop when the answer is delivered instead of restating it in summary.",
        "Stop when the answer has been delivered, rather than closing with a summary that "
        "restates what was just said.",
        "Stop when the answer has actually been delivered, rather than closing with a "
        "summary that restates what the reader has just finished reading; a closing "
        "recap earns its place only when the material was hard to hold in view.",
        "Stop when the answer has been delivered — a closing recap earns its place only "
        "when the material was hard to hold in view.",
    ),
]

_NOTE_BULLETS = [
    (
        "This one has several parts; the joins between them are worth marking.",
        "This one has several parts to it, and the joins between them are worth marking "
        "explicitly rather than leaving implicit.",
        "This one has several distinct parts to it, and the joins between them are worth "
        "marking explicitly rather than leaving a reader to work out where the answer moved "
        "from one to the next.",
        "This one has several distinct parts — the joins between them are worth marking "
        "rather than leaving a reader to work out where one ended.",
    ),
    (
        "Some vocabulary here has an everyday twin; keep the sense you use steady.",
        "Some of the vocabulary here has an everyday twin, so keep whichever sense you are "
        "using steady once you have picked it.",
        "Some of the vocabulary here has an everyday twin that means something looser, so "
        "keep whichever sense you are using steady once you have picked it, rather than "
        "sliding between the two as you go.",
        "Some vocabulary here has an everyday twin that means something looser — keep "
        "whichever sense you picked steady rather than sliding between them.",
    ),
    (
        "The material has a natural order, rarely the order it occurred to you in.",
        "The material has a natural order for a reader, and it is rarely the same as the "
        "order it occurred to you in.",
        "The material has a natural order from the reader's side, and it is rarely the same "
        "as the order in which it occurred to you; rearranging afterwards costs less than a "
        "reader re-reading.",
        "The material has a natural order from the reader's side — rarely the order it "
        "occurred to you in, and rearranging costs less than a reader re-reading.",
    ),
]

_TRAILING = [(
    "Treat these as properties of the writing task rather than of the subject.",
    "Treat these as properties of the writing task rather than of the subject matter, "
    "since they shape how the answer reads and not what it contains.",
    "Treat these as properties of the writing task rather than of the subject matter. "
    "They shape how the answer reads and how easily it is used, not what it contains or "
    "what would make it right.",
    "Treat these as properties of the writing task rather than of the subject matter — "
    "they shape how the answer reads, not what it contains.",
)]

# Mirrors the directive's closing budget paragraph. Carries no number of any
# kind: a count here would manipulate response length, which exp003c showed is
# exactly the variable the placebo exists to hold still (FD-5).
_CLOSING = [(
    "ORDERING: arrange the material for the reader rather than in the order it arrived in.",
    "ORDERING: arrange the material in the order that serves a reader, not the order it "
    "arrived in while you were working it out.",
    "ORDERING: arrange the material in the order that serves a reader, rather than the "
    "order it arrived in while you were working the answer out. The two coincide less "
    "often than they seem to.",
    "ORDERING: arrange the material in the order that serves a reader, rather than the "
    "order it arrived in while you were working the answer out. The two coincide less "
    "often than they seem to, and the difference is most visible at the point where a "
    "reader would otherwise stop.",
    "ORDERING: arrange the material in the order that serves a reader — not the order it "
    "arrived in while you were working the answer out.",
    "ORDERING: arrange the material in the order that serves a reader — not the order it "
    "arrived in while you were working the answer out. The two coincide less often than "
    "they seem to, and the difference shows up at the point where a reader would stop.",
    "ORDERING: arrange the material in the order that serves a reader — not the order it "
    "arrived in while you were working the answer out. The two coincide less often than "
    "they seem to, and the difference shows up most at the point where a reader would "
    "otherwise stop reading, which is usually earlier than the writer expects.",
)]

_CAVEAT_BULLETS = [
    (
        "Register should hold level; a shift midway reads as a change of audience.",
        "Register should hold level throughout, since a shift midway through reads to a "
        "reader as a change of audience.",
        "Register should hold level throughout the answer; a shift midway through reads to a "
        "reader as a change of audience, and they will spend attention working out which of "
        "the two they are.",
        "Register should hold level throughout — a shift midway reads as a change of "
        "audience, and a reader spends attention working out which one they are.",
    ),
    (
        "Formatting is a tool for the reader, not a display of effort.",
        "Formatting is a tool for the reader's benefit rather than a display of the effort "
        "that went in.",
        "Formatting is a tool for the reader's benefit rather than a display of the effort "
        "that went into the answer; structure that does not help someone find something is "
        "just texture.",
        "Formatting is a tool for the reader rather than a display of effort — structure "
        "that does not help someone find something is just texture.",
    ),
]

_SECTION_HEADERS = {
    "first": "HOW TO PRESENT THIS ANSWER:",
    "emdash": "PRESENTATION NOTES — this answer has features worth handling deliberately:",
    "plain": "STYLE CAVEATS:",
}


# --------------------------------------------------------------------------
# Word-count matching by selection
# --------------------------------------------------------------------------

def _choose(slots: list[list[str]], target_words: int, target_emdash: int) -> list[str]:
    """Pick one variant per slot to match word count AND em-dash count.

    Two axes, not one. The first draft optimised word count alone and matched it
    on every question in both batteries while missing the em-dash count on all
    21 — the directive uses em dashes inside its bullets and the placebo did not.
    Dropping em dashes from the formatting axis would have been the easy fix and
    the wrong one: it is a visible formatting marker, and a placebo that differs
    from the directive in visible formatting is not controlling for formatting.

    Em-dash count is matched exactly and word count is matched as closely as the
    pools allow, in that priority order, because the word axis has a ±10%
    tolerance and the formatting axis does not.

    Selection is the only length control available — instructing the model about
    length is forbidden (FD-5) — so the pools carry both length variants and
    em-dash variants of each line.
    """
    # state: (words, em dashes) -> (tiebreak cost, choices)
    states: dict[tuple[int, int], tuple[int, list[str]]] = {(0, 0): (0, [])}
    for slot in slots:
        nxt: dict[tuple[int, int], tuple[int, list[str]]] = {}
        mid = (len(slot) - 1) / 2
        for (w, d), (cost, chosen) in states.items():
            for i, option in enumerate(slot):
                key = (w + _words(option), d + option.count("\u2014"))
                c = cost + int(abs(i - mid) * 2)
                prev = nxt.get(key)
                if prev is None or c < prev[0]:
                    nxt[key] = (c, chosen + [option])
        states = nxt
    best = min(
        states.items(),
        key=lambda kv: (abs(kv[0][1] - target_emdash), abs(kv[0][0] - target_words), kv[1][0]),
    )
    return best[1][1]


def _seeded(question: str, n: int) -> int:
    return int(hashlib.sha256(question.encode()).hexdigest(), 16) % n


# --------------------------------------------------------------------------
# Generation
# --------------------------------------------------------------------------

def _assemble(block: str, question: str, lead_override: str | None = None,
              header_override: str | None = None, pinned: dict[int, str] | None = None):
    """Shared body: build the plan and slots, solve the lengths, render.

    Returns (text, chosen, slot_roles) so a caller can reuse the exact variant
    choices. `pinned` fixes named slots to a given string before solving, which
    is how `A_only` reuses the placebo's carrier verbatim.
    """
    shape = parse_shape(block)
    reg = _REGISTERS[_seeded(question, len(_REGISTERS))]
    conf = 0.60 + (_seeded(question + "|c", 40) / 100.0)

    slots: list[list[str]] = []
    roles: list[str] = []
    plan: list[tuple[str, object]] = []
    bullet_cursor = note_cursor = caveat_cursor = section_index = 0

    for seg in shape.segments:
        if seg.kind == "inline":
            if section_index == 0:
                plan.append(("fixed", header_override or
                             f"RESPONSE REGISTER: {reg} (profile weight {conf:.2f})"))
            else:
                plan.append(("slot", len(slots)))
                slots.append(list(_CLOSING[0])); roles.append("closing")
        else:
            header = (
                _SECTION_HEADERS["emdash"] if seg.header_has_emdash
                else _SECTION_HEADERS["first"] if section_index <= 1
                else _SECTION_HEADERS["plain"]
            )
            lines: list[tuple[str, object]] = [("fixed", header)]
            for _ in range(seg.n_lead_prose):
                idx = len(slots)
                slots.append([lead_override] if lead_override
                             else [v.format(reg=reg) for v in _LEAD[0]])
                roles.append("lead"); lines.append(("slot", idx))
            for _ in range(seg.n_bullets):
                if seg.header_has_emdash:
                    pool = _NOTE_BULLETS[note_cursor % len(_NOTE_BULLETS)]; note_cursor += 1
                elif section_index > 1:
                    pool = _CAVEAT_BULLETS[caveat_cursor % len(_CAVEAT_BULLETS)]; caveat_cursor += 1
                else:
                    pool = _BULLETS[bullet_cursor % len(_BULLETS)]; bullet_cursor += 1
                idx = len(slots)
                slots.append(["- " + v for v in pool]); roles.append("bullet")
                lines.append(("slot", idx))
            for _ in range(seg.n_trailing_prose):
                idx = len(slots)
                slots.append(list(_TRAILING[0])); roles.append("trailing")
                lines.append(("slot", idx))
            plan.append(("section", lines))
        section_index += 1

    for idx, text in (pinned or {}).items():
        slots[idx] = [text]

    fixed = [v for kind, v in plan if kind == "fixed"]
    fixed += [v for kind, lines in plan if kind == "section" for k, v in lines if k == "fixed"]
    chosen = _choose(
        slots,
        max(shape.words - sum(_words(v) for v in fixed), 0),
        max(block.count("\u2014") - sum(v.count("\u2014") for v in fixed), 0),
    )

    def render(entry) -> str:
        kind, value = entry
        return value if kind == "fixed" else chosen[value]

    out: list[str] = []
    for kind, value in plan:
        if kind == "section":
            out.append("\n".join(render(e) for e in value))
        else:
            out.append(render((kind, value)))
    return "\n\n".join(out), chosen, roles


def build(block: str, question: str, lead_override: str | None = None,
          header_override: str | None = None) -> str:
    """Generate the placebo that mirrors `block` for `question`.

    `block` is the real `Route.prompt_block()` output for that question, so the
    placebo tracks it question by question rather than matching on average.

    `lead_override` and `header_override` exist for `A_only` and the
    `elaboration_only` compute control (lab/treatments.py), which need a
    length-matched carrier and should get it from the machinery that already
    does the matching rather than from a hand-written block.
    """
    return _assemble(block, question, lead_override, header_override)[0]


def build_reusing_carrier(block: str, question: str, lead: str, header: str) -> str:
    """Build a variant that reuses the placebo's carrier text VERBATIM.

    Why this exists, found by a test: `build(..., lead_override=...)` pins the
    lead, which changes the length budget, which makes the length solver pick
    different variants for the carrier bullets. `A_only` and
    `directive_placebo` then differed on EIGHT lines instead of two — so the
    contrast between them was "the epistemic framing, plus a redistribution of
    inert prose" rather than the framing alone.

    The fix is to pin most of the carrier and leave a few slots free to absorb
    the difference: the closing paragraph, the trailing prose where there is
    one, and the last bullet. Everything else is the placebo's text verbatim, so
    the two blocks differ on a handful of lines instead of most of them, with
    total word count, bullet count, structure and formatting markers all still
    matched exactly.
    """
    _, base_choices, roles = _assemble(block, question)
    # Slots left free to absorb the difference. The closing paragraph has the
    # widest range, but it alone is not always enough: a framing sentence with
    # no em dash where the placebo's lead had one leaves an em-dash deficit the
    # closing cannot always cover (found on U03, whose PREDICTIVE framing has
    # none and which has no trailing or caveat slot to borrow from). Freeing the
    # trailing slot and the LAST bullet gives two more degrees of freedom while
    # keeping every other bullet identical to the placebo's.
    last_bullet = max(
        (i for i, role in enumerate(roles) if role == "bullet"), default=None
    )
    free = {i for i, role in enumerate(roles) if role in ("lead", "closing", "trailing")}
    if last_bullet is not None:
        free.add(last_bullet)
    pinned = {i: base_choices[i] for i in range(len(roles)) if i not in free}
    return _assemble(block, question, lead_override=lead, header_override=header,
                     pinned=pinned)[0]


# --------------------------------------------------------------------------
# Matching measurement — used by tests and by the report's audit section
# --------------------------------------------------------------------------

def features(text: str) -> dict:
    """The measurable half of the six-axis match.

    Axes 5 (expected response effort) and 6 (perceived seriousness) are review
    items, not computable ones, and are recorded as such rather than proxied by
    a number that would look like a check without being one.
    """
    lines = [ln for ln in text.split("\n") if ln.strip()]
    return {
        "words": _words(text),
        "bullets": sum(1 for ln in lines if _BULLET.match(ln)),
        "section_headers": sum(1 for ln in lines if _SECTION_HEADER.match(ln)),
        "inline_headers": sum(1 for ln in lines if _INLINE_HEADER.match(ln)),
        "colons": text.count(":"),
        "em_dashes": text.count("—"),
        "max_indent": max((len(ln) - len(ln.lstrip()) for ln in lines), default=0),
        "paragraph_blocks": len([b for b in text.split("\n\n") if b.strip()]),
    }


def match_report(block: str, placebo: str) -> dict:
    """Axis-by-axis comparison. `ok` is the conjunction of the testable axes."""
    a, b = features(block), features(placebo)
    tol = max(1, int(round(a["words"] * WORD_TOLERANCE)))
    axes = {
        "word_count": {
            "directive": a["words"], "placebo": b["words"],
            "tolerance": tol, "ok": abs(a["words"] - b["words"]) <= tol,
        },
        "instruction_count": {
            "directive": a["bullets"], "placebo": b["bullets"],
            "ok": a["bullets"] == b["bullets"],
        },
        "structural_complexity": {
            "directive": (a["section_headers"], a["inline_headers"], a["paragraph_blocks"], a["max_indent"]),
            "placebo": (b["section_headers"], b["inline_headers"], b["paragraph_blocks"], b["max_indent"]),
            "ok": (
                a["section_headers"] == b["section_headers"]
                and a["inline_headers"] == b["inline_headers"]
                and a["paragraph_blocks"] == b["paragraph_blocks"]
                and a["max_indent"] == b["max_indent"]
            ),
        },
        "formatting_markers": {
            "directive": (a["bullets"], a["em_dashes"]),
            "placebo": (b["bullets"], b["em_dashes"]),
            "ok": a["bullets"] == b["bullets"] and a["em_dashes"] == b["em_dashes"],
        },
        "expected_response_effort": {"ok": None, "basis": "review item — plan §4"},
        "perceived_seriousness": {"ok": None, "basis": "review item — plan §4"},
    }
    leaked = sorted({w for w in FORBIDDEN if w in placebo.lower()})
    return {
        "axes": axes,
        "forbidden_terms_present": leaked,
        "ok": all(v["ok"] for v in axes.values() if v["ok"] is not None) and not leaked,
    }
