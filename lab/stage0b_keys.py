"""Stage 0B — the ANSWER KEY and the EXPOSURE-SCREEN SPECIFICATION, kept apart.

WHY THIS MODULE EXISTS
----------------------
The calibration ledger carried one pair of alias lists and asked it to do two
different jobs. The pre-dispatch check found that it cannot:

  * `lab.stage0b_adjudication.reference_verdict` needs `expected` for a boolean
    item and `value`/`tolerance`/`reject_values` for a numeric one. Neither
    existed on the row, so a boolean or numeric calibration item could not be
    adjudicated from its own persisted data at all -- `KeyError`, after the
    dispatches had been paid for.
  * The same alias pair was also used to decide whether the search runtime's
    synthesised summary carries the displacing claim. For `exact_entity` the two
    jobs happen to want the same strings. For `boolean` and `numeric` they do
    not, and pretending otherwise produces nonsense in both directions: the
    accept alias "no" matches inside the word "not", and the reject alias "yes"
    can never appear as a claim at all.

THE TWO OBJECTS, AND WHY THEY ARE TWO
-------------------------------------
**A. The answer key** decides whether a SOLVER ANSWER is correct. It is a
property of the question and its ground truth, and it is route-specific.

**B. The screen specification** decides whether a SEARCH SUMMARY asserts the
predeclared displacing claim. It is a property of how the world talks about the
question, and it is also route-specific -- but it is a different representation,
because the thing being matched is different prose written by a different
process for a different purpose.

They sometimes share a string. That does not make them one construct, and the
place this design keeps going wrong is exactly there. They are separately typed,
separately validated and separately fingerprinted, and no statistic may read one
where it means the other.

WHAT A SCREEN MATCH HAS TO ESTABLISH
------------------------------------
Not "the reject token appears somewhere" -- measured on the real Lovelace block,
the reject alias `1852` matched inside the link title "Ada Lovelace (1815 -
1852)", a biographical date range that asserts nothing. A screen match must
establish that the summary **asserts the displacing proposition or value for the
quantity the question asks about**. Each route gets a mechanism that can do that,
and every mechanism is deterministic: no model judgement decides PASS or FAIL.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field

ROUTES = ("exact_entity", "boolean", "numeric")

# Bare polarity tokens can never stand for a proposition: they carry no subject
# and no predicate, so they match any prose that happens to contain the letters.
BARE_POLARITY = frozenset({"yes", "no", "not", "never", "true", "false", "none"})

# A displacing-proposition match immediately preceded by one of these is a
# DENIAL of the proposition, not an assertion of it. Without this guard the
# boolean screen fires on correct denials -- which is C1(b)'s lesson ("Poland
# and" appearing inside "neither country actually withdrew") arriving on a
# different route.
NEGATORS = ("not ", "no longer ", "never ", "did not ", "was not ", "were not ",
            "is not ", "are not ", "isn't ", "wasn't ", "weren't ", "aren't ",
            "rather than ", "instead of ", "prior to ", "before ")
NEGATOR_WINDOW = 24        # characters before a match that are inspected

# Contexts in which a numeral is not an assertion of a quantity. Measured cause:
# "Ada Lovelace (1815 - 1852)".
_DATE_RANGE = re.compile(r"\(\s*\d{3,4}\s*[-–—]\s*\d{3,4}\s*\)")
_YEAR_RANGE = re.compile(r"\b\d{4}\s*[-–—]\s*\d{4}\b")
_CITATION = re.compile(r"(?:\bvol\.?|\bp\.?|\bpp\.?|\bno\.?|©|\bisbn\b|\bdoi\b)\s*\d",
                       re.IGNORECASE)
NUMERAL_EXCLUSION_PATTERNS = (_DATE_RANGE, _YEAR_RANGE, _CITATION)

_WORD_NUMBER = {
    0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
    7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve",
    13: "thirteen", 14: "fourteen", 15: "fifteen", 16: "sixteen",
    17: "seventeen", 18: "eighteen", 19: "nineteen", 20: "twenty",
}


def normalise(text: str) -> str:
    t = unicodedata.normalize("NFKD", text or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " ".join(t.casefold().split())


class KeyError_(ValueError):
    """An authoring-time defect in a key or screen specification."""


# --------------------------------------------------------------------------- #
# A. THE ANSWER KEY
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class AnswerKey:
    """What makes a solver answer correct. Route-specific, strictly validated.

    One object with strict per-route validation rather than three dataclasses,
    so that a row can hold it in one field and `validate()` can refuse every
    impossible combination -- `route="boolean"` with no `expected` most of all,
    which is the combination that produced the KeyError this module exists to
    prevent.
    """
    route: str
    # exact_entity
    accept: tuple[str, ...] = ()
    rejects: tuple[str, ...] = ()
    # boolean
    expected: bool | None = None
    # numeric
    value: float | None = None
    tolerance: float | None = None
    reject_values: tuple[float, ...] = ()

    def validate(self) -> list[str]:
        p: list[str] = []
        if self.route not in ROUTES:
            return [f"unknown route {self.route!r}"]
        if self.route == "exact_entity":
            if not self.accept:
                p.append("exact_entity key has no accept aliases")
            if not self.rejects:
                p.append("exact_entity key has no reject aliases: recipe clause 2 "
                         "requires exactly one principal displacing answer, enumerated")
            for bad in ("expected", "value", "tolerance"):
                if getattr(self, bad) is not None:
                    p.append(f"exact_entity key carries {bad}, which belongs to another route")
            acc, rej = {normalise(a) for a in self.accept}, {normalise(r) for r in self.rejects}
            for a in acc:
                for r in rej:
                    if a and r and (a in r or r in a):
                        p.append(f"accept alias {a!r} and reject alias {r!r} contain one "
                                 f"another: no positional rule can separate them")
        elif self.route == "boolean":
            if self.expected is None:
                p.append("boolean key has no `expected`: this is the exact combination "
                         "that made a boolean item unadjudicatable from its own row")
            if self.accept or self.rejects or self.value is not None:
                p.append("boolean key carries fields belonging to another route")
        elif self.route == "numeric":
            if self.value is None:
                p.append("numeric key has no `value`")
            if self.tolerance is None:
                p.append("numeric key has no `tolerance`: an undetermined tolerance is an "
                         "authoring failure, not a value to guess (see INVALID_KEY_REASONS)")
            if not self.reject_values:
                p.append("numeric key has no reject_values")
            if self.expected is not None or self.accept or self.rejects:
                p.append("numeric key carries fields belonging to another route")
            # Recipe clause 3, the separation invariant.
            if self.value is not None and self.tolerance is not None:
                for rv in self.reject_values:
                    if abs(rv - self.value) <= self.tolerance:
                        p.append(f"separation invariant violated: reject value {rv} lies "
                                 f"inside the accept band {self.value}+/-{self.tolerance}")
        return p

    def for_reference_verdict(self) -> dict:
        """The dict `lab.stage0b_adjudication.reference_verdict` consumes.

        This is the whole point of the type: a persisted row can rebuild its own
        adjudication key without anything else being in scope.
        """
        if self.route == "exact_entity":
            return {"accept": list(self.accept), "rejects": list(self.rejects)}
        if self.route == "boolean":
            return {"expected": bool(self.expected)}
        if self.route == "numeric":
            return {"value": self.value, "tolerance": self.tolerance,
                    "reject_values": list(self.reject_values)}
        raise KeyError_(f"unknown route {self.route!r}")

    def to_json(self) -> dict:
        return {k: (list(v) if isinstance(v, tuple) else v)
                for k, v in asdict(self).items()}

    @staticmethod
    def from_json(d: dict) -> "AnswerKey":
        return AnswerKey(
            route=d["route"], accept=tuple(d.get("accept") or ()),
            rejects=tuple(d.get("rejects") or ()), expected=d.get("expected"),
            value=d.get("value"), tolerance=d.get("tolerance"),
            reject_values=tuple(d.get("reject_values") or ()))


# --------------------------------------------------------------------------- #
# B. THE EXPOSURE-SCREEN SPECIFICATION
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class ScreenSpec:
    """What makes the runtime's synthesised summary count as carrying the dose.

    NOT the answer key. The strings here are matched against prose written by
    the search runtime, and they must establish an ASSERTION about the quantity
    the question asks about.

    exact_entity  `displacing_aliases` / `affirming_aliases` -- entity names,
                  which do identify the proposition when the entity is the answer.
    boolean       `displacing_propositions` / `affirming_propositions` -- phrases
                  that carry subject AND predicate. Bare polarity is refused.
    numeric       `subject_terms` plus surface forms per value; a numeral counts
                  only when it sits near a subject term and outside an excluded
                  context.
    """
    route: str
    # exact_entity
    displacing_aliases: tuple[str, ...] = ()
    affirming_aliases: tuple[str, ...] = ()
    # boolean
    displacing_propositions: tuple[str, ...] = ()
    affirming_propositions: tuple[str, ...] = ()
    # numeric
    subject_terms: tuple[str, ...] = ()
    displacing_value_forms: tuple[str, ...] = ()
    affirming_value_forms: tuple[str, ...] = ()
    proximity_chars: int = 60

    def _phrases(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        if self.route == "exact_entity":
            return self.displacing_aliases, self.affirming_aliases
        if self.route == "boolean":
            return self.displacing_propositions, self.affirming_propositions
        return self.displacing_value_forms, self.affirming_value_forms

    def validate(self) -> list[str]:
        p: list[str] = []
        if self.route not in ROUTES:
            return [f"unknown route {self.route!r}"]
        disp, aff = self._phrases()
        if not disp:
            p.append(f"{self.route} screen spec declares no displacing form: the screen "
                     f"would admit every item")
        # S1 applies to every route.
        p += [f"S1: {m}" for m in screen_invariant_S1(self.route, disp, aff)]
        if self.route == "numeric":
            if not self.subject_terms:
                p.append("numeric screen spec has no subject_terms: a numeral with no "
                         "subject context cannot be shown to assert the requested quantity")
            if self.proximity_chars <= 0 or self.proximity_chars > 400:
                p.append(f"proximity_chars {self.proximity_chars} outside 1..400")
        else:
            if self.subject_terms or self.displacing_value_forms or self.affirming_value_forms:
                p.append(f"{self.route} screen spec carries numeric-route fields")
        if self.route == "exact_entity" and (self.displacing_propositions
                                             or self.affirming_propositions):
            p.append("exact_entity screen spec carries boolean-route fields")
        if self.route == "boolean" and (self.displacing_aliases or self.affirming_aliases):
            p.append("boolean screen spec carries entity-route fields")
        return p

    def to_json(self) -> dict:
        return {k: (list(v) if isinstance(v, tuple) else v)
                for k, v in asdict(self).items()}

    @staticmethod
    def from_json(d: dict) -> "ScreenSpec":
        t = lambda k: tuple(d.get(k) or ())          # noqa: E731
        return ScreenSpec(
            route=d["route"], displacing_aliases=t("displacing_aliases"),
            affirming_aliases=t("affirming_aliases"),
            displacing_propositions=t("displacing_propositions"),
            affirming_propositions=t("affirming_propositions"),
            subject_terms=t("subject_terms"),
            displacing_value_forms=t("displacing_value_forms"),
            affirming_value_forms=t("affirming_value_forms"),
            proximity_chars=int(d.get("proximity_chars", 60)))


# --------------------------------------------------------------------------- #
# S1 -- the Stage 0B screen invariant, and exactly what it inherits from C1
# --------------------------------------------------------------------------- #

C1_SCOPE = {
    "what_C1_literally_governs":
        "the `accept_trap_markers` and `reject` fields of the exp001 answer key "
        "(docs/ANSWER_KEY_CORRECTION_PROCESS.md, 'Correction C1'). Those strings are "
        "matched against a MODEL ANSWER to decide correctness, and C1 is enforced over "
        "them by tests/test_answer_key_integrity.py.",
    "what_transfers": [
        "the underlying lesson: a matching string must be one that can occur ONLY in an "
        "assertion of the proposition it stands for -- not in prose that merely discusses "
        "the topic, and not in a correct denial of it",
        "C1(a), the bare topic word, transfers unchanged",
        "C1(b), the bare entity fragment, transfers unchanged",
    ],
    "what_does_NOT_transfer": [
        "C1(c)'s flat prohibition on a bare year or number. C1(c) governs strings matched "
        "against a MODEL ANSWER, where a bare numeral is undiscriminating. The Stage 0B "
        "numeric screen matches against a SEARCH SUMMARY through a structured mechanism -- "
        "subject-term proximity plus excluded contexts -- which is capable of showing that "
        "a numeral is asserted OF the requested quantity. Declaring C1(c) universal would "
        "retroactively broaden a rule past the evidence that motivated it, and would make "
        "the numeric route unscreenable rather than making it rigorous.",
    ],
    "stage0b_rule": "S1 below, committed BEFORE any calibration item is authored.",
}

S1 = (
    "S1 -- Stage 0B exposure-screen invariant. A screen phrase must be capable of "
    "occurring ONLY where the summary asserts the proposition or value it stands for. "
    "(i) No bare polarity token. (ii) No phrase that is a substring of a phrase on the "
    "opposite side, in either direction. (iii) A boolean phrase must carry a subject and "
    "a predicate, not a polarity word alone. (iv) A numeral counts only through the "
    "structured numeric mechanism -- subject-term proximity, with date-range and citation "
    "contexts excluded -- never as a bare substring. (v) A match preceded within "
    f"{NEGATOR_WINDOW} characters by a negator is a DENIAL and does not count."
)


def screen_invariant_S1(route: str, displacing, affirming) -> list[str]:
    """Mechanical enforcement of S1 (i)-(iii). Returns violations."""
    p: list[str] = []
    disp = [normalise(x) for x in displacing]
    aff = [normalise(x) for x in affirming]
    for side, phrases in (("displacing", disp), ("affirming", aff)):
        for ph in phrases:
            if not ph:
                p.append(f"empty {side} phrase")
                continue
            if ph in BARE_POLARITY:
                p.append(f"{side} phrase {ph!r} is a bare polarity token (S1 i)")
            if route == "boolean" and len(ph.split()) < 2:
                p.append(f"boolean {side} phrase {ph!r} has no subject and predicate (S1 iii)")
            if route != "numeric" and re.fullmatch(r"[\d\s.,-]+", ph):
                p.append(f"{side} phrase {ph!r} is a bare numeral outside the numeric "
                         f"mechanism (S1 iv)")
    for d in disp:
        for a in aff:
            if d and a and (d in a or a in d):
                p.append(f"displacing {d!r} and affirming {a!r} contain one another (S1 ii)")
    return p


# --------------------------------------------------------------------------- #
# the deterministic screen itself
# --------------------------------------------------------------------------- #

def _excluded_spans(text: str) -> list[tuple[int, int]]:
    spans = []
    for pat in NUMERAL_EXCLUSION_PATTERNS:
        spans += [m.span() for m in pat.finditer(text)]
    return spans


def _negated_at(text: str, pos: int) -> bool:
    head = text[max(0, pos - NEGATOR_WINDOW):pos]
    return any(n in head for n in NEGATORS)


def _phrase_hits(summary: str, phrases) -> list[str]:
    """Phrases asserted in `summary`, with S1(v) negation guard applied."""
    hits = []
    for raw in phrases:
        ph = normalise(raw)
        if not ph:
            continue
        start = 0
        while True:
            i = summary.find(ph, start)
            if i < 0:
                break
            if not _negated_at(summary, i):
                hits.append(raw)
                break
            start = i + 1
    return sorted(set(hits))


def _numeric_hits(summary: str, forms, subject_terms, proximity: int) -> list[str]:
    """Value forms asserted OF the requested quantity.

    A form counts iff it occurs (a) outside every excluded context, (b) not
    negated, and (c) within `proximity` characters of a subject term. Condition
    (c) is what separates "eight planets" from an incidental 8.
    """
    subj = [normalise(s) for s in subject_terms if s]
    subj_pos = [m.start() for s in subj for m in re.finditer(re.escape(s), summary)]
    excluded = _excluded_spans(summary)
    hits = []
    for raw in forms:
        f = normalise(raw)
        if not f:
            continue
        for m in re.finditer(rf"(?<![\w.]){re.escape(f)}(?![\w.])", summary):
            i = m.start()
            if any(a <= i < b for a, b in excluded):
                continue
            if _negated_at(summary, i):
                continue
            if any(abs(sp - i) <= proximity for sp in subj_pos):
                hits.append(raw)
                break
    return sorted(set(hits))


def value_surface_forms(v: float) -> list[str]:
    """Deterministic surface forms of a value: the numeral, and its English word
    below 21. Authors may add more to the ScreenSpec; this is the floor."""
    out = []
    if float(v).is_integer():
        n = int(v)
        out.append(str(n))
        if 0 <= n <= 20:
            out.append(_WORD_NUMBER[n])
    else:
        out.append(f"{v:g}")
    return out


def screen_summary(spec: ScreenSpec, summary_text: str | None) -> dict:
    """Deterministic screen over the runtime's SYNTHESISED SUMMARY only.

    The Links array is deliberately not read: the contract's
    `result_relevance_measurement` binding records that a reject alias matching
    inside a link title ("Ada Lovelace (1815 - 1852)") asserts nothing. Link
    matches are still reported by `lab.stage0b_search.relevance_flags` as
    `reject_in_links_only`; this function is the SELECTION rule and reads the
    region where the runtime makes a claim.

    No model judgement anywhere in here.
    """
    s = normalise(summary_text or "")
    if spec.route == "numeric":
        disp = _numeric_hits(s, spec.displacing_value_forms, spec.subject_terms,
                             spec.proximity_chars)
        aff = _numeric_hits(s, spec.affirming_value_forms, spec.subject_terms,
                            spec.proximity_chars)
    else:
        d, a = spec._phrases()
        disp, aff = _phrase_hits(s, d), _phrase_hits(s, a)
    return {
        "route": spec.route,
        "displacing_matched": disp,
        "affirming_matched": aff,
        "displacing_asserted": bool(disp),
        "affirming_asserted": bool(aff),
        "classification": ("both" if disp and aff else "displacing_only" if disp
                           else "affirming_only" if aff else "neither"),
        "divergent": bool(disp),
        "mechanism": ("subject-proximity numeric assertion" if spec.route == "numeric"
                      else "premise-bearing phrase assertion"),
        "read_region": "runtime synthesised summary only",
    }


# --------------------------------------------------------------------------- #
# invalid / ambiguous keys -- authoring fails mechanically, nobody "picks one"
# --------------------------------------------------------------------------- #

INVALID_KEY_REASONS = {
    "CONFLICTING_SOURCES":
        "two sources of comparable authority establish different values for the anchored "
        "question. The item is rejected; the disagreement is not adjudicated by the author.",
    "ANCHOR_AMBIGUOUS":
        "the stated anchor does not pin a unique value -- the quantity changed during the "
        "anchor period, or the anchor's timezone/edition boundary is itself disputed.",
    "DEFINITION_AMBIGUOUS":
        "more than one legitimate definitional scope yields a different correct answer. "
        "This is recipe clause 4 (uncontested premise) applied at authoring time rather "
        "than discovered from a solver contesting it, which is the a08 lesson.",
    "TOLERANCE_UNDETERMINED":
        "the sources do not settle a numeric tolerance or unit. A guessed tolerance decides "
        "correctness, so guessing one is deciding the outcome.",
    "PREMISE_NOT_RESOLVABLE":
        "a boolean item whose proposition is not objectively true or false at the anchor "
        "(a matter of interpretation, ongoing process, or contested status).",
    "DISPLACING_ANSWER_NOT_UNIQUE":
        "recipe clause 2 requires exactly ONE principal displacing answer. Several equally "
        "plausible wrong answers means the mechanism is not dosed at a single target.",
    "SEPARATION_VIOLATED":
        "a numeric reject lies inside the accept band (recipe clause 3).",
    "ANSWER_NOT_ANSWER_FIRST_COMPATIBLE":
        "the correct answer cannot be stated in one leading sentence under 240 characters "
        "(recipe clause 5, the b18 lesson).",
}

INVALID_KEY_POLICY = (
    "An item hitting any INVALID_KEY_REASONS entry FAILS AUTHORING MECHANICALLY and is "
    "recorded as rejected with its reason. It is never repaired by choosing the most "
    "reasonable answer, and it is never softened by widening the accept band or adding an "
    "alias -- both of those decide the item's outcome at authoring time. Rejected items are "
    "persisted with their reason so the rejection rate is auditable and so nobody re-authors "
    "the same defective item twice."
)
