"""Classifier tests, including the two bugs the design session found.

The two regression classes at the top are the point of this file. Both bugs
had the same shape — an over-eager arithmetic detector routing an empirical
question to "compute, don't search" and skipping verification — and both were
found by running the classifier against real questions, not by reading it.
If either regresses, false-premise traps silently stop being verified.
"""

import pytest

from epistemic.classifier import ClaimType, classify_claim


class TestBug1HyphenIsNotMinus:
    """A bare '-' used to match the arithmetic detector, so any hyphenated
    word routed the question to DETERMINISTIC."""

    @pytest.mark.parametrize(
        "question",
        [
            "What is the difference between the 2019 and 2021 US-Japan trade surpluses?",
            "Will the entity-hazard TTL bucketing hold on 20 more untested entities?",
            "Is evidence-lineage independence the same as statistical independence?",
            "What were the terms of the 2015 Iran-P5+1 nuclear agreement?",
            "How large was the 1998 Russia-Asia financial contagion?",
        ],
    )
    def test_hyphenated_words_do_not_route_deterministic(self, question):
        assert classify_claim(question).claim_type is not ClaimType.DETERMINISTIC

    def test_the_original_trap_question_routes_empirical(self):
        c = classify_claim(
            "What is the difference between the 2019 and 2021 US-Japan trade surpluses?"
        )
        assert c.claim_type is ClaimType.EMPIRICAL

    def test_date_range_is_not_subtraction(self):
        assert classify_claim("What happened during 1918-1920?").claim_type is not ClaimType.DETERMINISTIC


class TestBug2HowManyIsNotArithmetic:
    """'how many' plus a year read as arithmetic, because the year looked like
    a digit operand."""

    @pytest.mark.parametrize(
        "question",
        [
            "How many people died in the 1918 influenza pandemic?",
            "How many countries joined the EU in 2004?",
            "How many moons does Saturn have?",
            "How many times was FDR elected in 1932 and after?",
        ],
    )
    def test_how_many_questions_are_empirical(self, question):
        assert classify_claim(question).claim_type is ClaimType.EMPIRICAL


class TestRealArithmeticStillDetected:
    """The fix must not be so cautious that it never fires — a classifier that
    routes everything EMPIRICAL is safe and useless."""

    @pytest.mark.parametrize(
        "question",
        [
            "What is 1847 * 26?",
            "What is 145 + 892?",
            "What is 1000 / 8?",
            "What is 12 divided by 4?",
            "Calculate the total cost of 12 items at 45 each.",
            "What is 15 % of 240?",
        ],
    )
    def test_arithmetic_routes_deterministic(self, question):
        assert classify_claim(question).claim_type is ClaimType.DETERMINISTIC


class TestSafeDefault:
    def test_unknown_question_defaults_to_empirical(self):
        c = classify_claim("Flurgle the wibbet of Zanzibar?")
        assert c.claim_type is ClaimType.EMPIRICAL

    def test_default_is_never_deterministic(self):
        """The asymmetry that both bug fixes rest on: a wrong EMPIRICAL costs a
        search, a wrong DETERMINISTIC costs a wrong answer."""
        for q in ["", "?", "Tell me about it.", "What about 2020?"]:
            assert classify_claim(q).claim_type is not ClaimType.DETERMINISTIC

    def test_entity_signal_demotes_deterministic(self):
        c = classify_claim("What is 5 + 5, according to Professor Smith in Belgium?")
        assert c.claim_type is ClaimType.EMPIRICAL
        assert c.demoted_from is ClaimType.DETERMINISTIC

    def test_demotion_is_recorded_not_silent(self):
        c = classify_claim("Who computed 12 * 12 for the Apollo program?")
        assert c.claim_type is ClaimType.EMPIRICAL
        assert any("demoted" in r for r in c.reasons)


class TestAbstractBatteryTypes:
    """The six questions from packet §6 must classify as the packet says."""

    @pytest.mark.parametrize(
        "question,expected",
        [
            ("Should the deterministic layer be built before the LLM-judge layer?", ClaimType.NORMATIVE),
            ("Real current-events questions vs. formal benchmarks — which should this project use now?", ClaimType.NORMATIVE),
            ("Will this system outperform a well-prompted frontier model at comparable cost?", ClaimType.PREDICTIVE),
            ("Will the entity-hazard TTL bucketing hold on 20 more untested entities?", ClaimType.PREDICTIVE),
            ("Is evidence-lineage independence the same as statistical independence?", ClaimType.DEFINITIONAL),
            ("What counts as 'wasted' verification cost?", ClaimType.DEFINITIONAL),
        ],
    )
    def test_abstract_questions(self, question, expected):
        assert classify_claim(question).claim_type is expected


class TestDefinitionalVsEmpirical:
    def test_difference_between_concepts_is_definitional(self):
        assert classify_claim(
            "What is the difference between precision and recall?"
        ).claim_type is ClaimType.DEFINITIONAL

    def test_difference_between_dated_quantities_is_empirical(self):
        """A definitional route would skip the premise check a trap needs."""
        assert classify_claim(
            "What is the difference between the 2019 and 2021 trade deficits?"
        ).claim_type is ClaimType.EMPIRICAL


class TestClassificationMetadata:
    def test_confidence_drops_when_multiple_types_fire(self):
        c = classify_claim("Should we predict that this will work?")
        assert c.confidence < 0.9

    def test_signals_are_auditable(self):
        c = classify_claim("What is 1847 * 26?")
        assert c.signals["DETERMINISTIC"]
        assert c.as_dict()["claim_type"] == "DETERMINISTIC"
