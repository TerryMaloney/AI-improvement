"""The quarantine guarantee.

If ground truth reaches a solver, every number this lab produces is worthless
and — worse — looks fine. There are two independent defences and this file
tests both:

  1. STRUCTURAL: solver agents are declared with no filesystem tools, so they
     cannot read the answer key even if they try. Tested by reading the agent
     definitions themselves, because a frontmatter edit is exactly the kind of
     silent change that would open the hole.

  2. TEXTUAL: nothing the lab *hands* a solver contains an answer. Tested by
     generating every packet for a real experiment and searching them for every
     string in the answer key.

The router is checked separately: it consults the entity registry, which holds
cached values like an officeholder's name, and it must emit staleness verdicts
about those records without ever emitting the values.
"""

from datetime import date
from pathlib import Path

import pytest
import yaml

from epistemic.registry import seed_registry
from epistemic.router import route
from lab.battery import ground_truth_strings, load_answers, load_batteries
from lab.trials import ExperimentConfig, build_prompt

REPO = Path(__file__).resolve().parent.parent
AGENT_DIR = REPO / ".claude" / "agents"

# Tools that would let a solver reach the answer key on disk.
FORBIDDEN_SOLVER_TOOLS = {"Read", "Glob", "Grep", "Bash", "Edit", "Write", "NotebookEdit", "Agent", "Task"}

# Tools a no-tools agent may declare: they cannot read files, search, or run
# code, so declaring one is equivalent to declaring none.
INERT_TOOLS = {"TodoWrite"}

# SANDBOX BUG, found by running the agents rather than by reading them:
# `tools: []` does NOT mean "no tools" — an empty list is treated as "no
# filter", and the agent is granted EVERYTHING, including Read and Bash. Both
# closed-book solvers and the judge were declared that way and were therefore
# not sandboxed at all.
#
# The test below passed anyway, because it asked "are any forbidden tools
# listed?" and an empty list lists nothing. A check that cannot fail on the
# empty case is not a check. It now requires a non-empty declaration drawn
# only from INERT_TOOLS, which fails loudly on `tools: []`.
#
# This is the same shape as the classifier bugs in tests/test_classifier.py:
# something that read as obviously correct, was wrong in practice, and was
# only caught by running it.


def _tool_list(tools) -> list[str]:
    if not tools:
        return []
    if isinstance(tools, list):
        return [str(t).strip() for t in tools if str(t).strip()]
    return [t.strip() for t in str(tools).split(",") if t.strip()]


def _frontmatter(path: Path) -> dict:
    text = path.read_text()
    assert text.startswith("---"), f"{path.name} has no frontmatter"
    return yaml.safe_load(text.split("---", 2)[1])


class TestStructuralSandbox:
    @pytest.mark.parametrize("agent", ["solver-closed", "solver-web", "grader-judge"])
    def test_agent_definition_exists(self, agent):
        assert (AGENT_DIR / f"{agent}.md").exists()

    @pytest.mark.parametrize("agent", ["solver-closed", "solver-web", "grader-judge"])
    def test_no_solver_can_touch_the_filesystem(self, agent):
        declared = _tool_list(_frontmatter(AGENT_DIR / f"{agent}.md").get("tools"))
        assert declared, f"{agent} declares no tools, which grants all of them"
        leaked = FORBIDDEN_SOLVER_TOOLS & set(declared)
        assert not leaked, (
            f"{agent} declares {leaked}, which can read batteries/answers.yaml. "
            f"Any result produced with this agent is invalid."
        )

    @pytest.mark.parametrize("agent", ["solver-closed", "grader-judge"])
    def test_no_tools_agents_declare_an_explicit_inert_tool(self, agent):
        """`tools: []` grants every tool. These agents must declare a non-empty
        list of inert tools so the filter actually applies.

        For the judge specifically: one with search would substitute its own
        retrieval for ground truth and silently become the answer key."""
        tools = _frontmatter(AGENT_DIR / f"{agent}.md").get("tools")
        declared = _tool_list(tools)
        assert declared, (
            f"{agent} declares no tools. An empty or missing `tools:` is not a "
            f"sandbox — it grants everything. Declare an inert tool instead."
        )
        assert set(declared) <= INERT_TOOLS, (
            f"{agent} declares {set(declared) - INERT_TOOLS}, which is not inert."
        )

    def test_web_solver_has_only_web_tools(self):
        declared = set(_tool_list(_frontmatter(AGENT_DIR / "solver-web.md")["tools"]))
        assert declared == {"WebSearch", "WebFetch"}


class TestTextualQuarantine:
    def test_answer_key_yields_leak_strings(self):
        assert len(ground_truth_strings(load_answers())) > 10

    def test_no_packet_contains_any_answer(self):
        """Generate every packet for the real experiment and check them all."""
        config = ExperimentConfig.load("exp001")
        registry = seed_registry()
        asked_on = date.fromisoformat(config.asked_as_of)
        leaks = ground_truth_strings(load_answers())
        # Short and generic strings ("78", "deficit") occur innocently in
        # question text; only distinctive strings are meaningful here.
        candidates = [s for s in leaks if len(s) >= 10]
        assert candidates, "no leak candidates — the check would be vacuous"

        offenders = []
        for battery in load_batteries(config.batteries):
            for q in battery.questions:
                rt = route(q.text, asked_on=asked_on, registry=registry)
                for cond in config.conditions:
                    prompt = build_prompt(q, cond, rt, config.default_search_budget).lower()
                    for s in candidates:
                        if s.lower() in prompt:
                            offenders.append((q.id, cond.name, s[:60]))
        assert not offenders, f"answer text reached a solver packet: {offenders[:5]}"

    def test_officeholder_names_never_appear_in_packets(self):
        """The sharpest version of the same check: the cached names in the
        entity registry are the answers to five of the fifteen questions."""
        config = ExperimentConfig.load("exp001")
        registry = seed_registry()
        names = [r.value for r in registry.all() if r.value]
        assert names
        for battery in load_batteries(config.batteries):
            for q in battery.questions:
                rt = route(q.text, asked_on=date(2026, 12, 1), registry=registry)
                for cond in config.conditions:
                    prompt = build_prompt(q, cond, rt, config.default_search_budget)
                    for name in names:
                        assert name not in prompt, (
                            f"cached value {name!r} leaked into the {cond.name} packet for {q.id}"
                        )


class TestRouterDoesNotLeak:
    def test_staleness_note_describes_staleness_not_the_value(self):
        registry = seed_registry()
        rt = route(
            "Who is currently the Chief Revenue Officer of OpenAI?",
            asked_on=date(2026, 12, 1),
            registry=registry,
        )
        assert rt.staleness_notes, "expected a staleness warning for a long-stale VOLATILE entity"
        block = rt.prompt_block()
        assert "Dali Rajic" not in block
        assert "stale" in block.lower()

    def test_scheduled_note_gives_the_date_not_the_person(self):
        rt = route(
            "Who is the Chair of the United States Federal Reserve, and when does that term end?",
            asked_on=date(2026, 9, 1),
            registry=seed_registry(),
        )
        block = rt.prompt_block()
        assert "Warsh" not in block
        # The term-end date is HALF THE ANSWER to this question. An earlier
        # version of the router put it in the prompt block, which would have
        # handed the treatment condition a free point on f03 for a reason
        # unrelated to the procedure under test. The model-facing note now says
        # a fixed term exists and has not passed, without dating it.
        assert "2030" not in block
        assert "fixed term" in block

    def test_no_registry_date_appears_in_any_prompt_block(self):
        registry = seed_registry()
        dates = {
            d.isoformat()
            for r in registry.all()
            for d in (r.term_end, r.last_verified)
            if d is not None
        }
        for battery in load_batteries(["factual"]):
            for q in battery.questions:
                for as_of in (date(2026, 9, 1), date(2027, 6, 1), date(2031, 1, 1)):
                    block = route(q.text, asked_on=as_of, registry=registry).prompt_block()
                    for d in dates:
                        assert d not in block, f"registry date {d} leaked into the block for {q.id}"

    def test_route_dict_is_serialisable_for_the_audit_trail(self):
        import json

        rt = route("Who is the UK Prime Minister?", asked_on=date(2026, 9, 1), registry=seed_registry())
        json.dumps(rt.as_dict())
