# Round-1 judge verdicts (general-purpose agent, prompt-enforced tool constraint)

These 12 verdicts were produced during the first pilot pass, before the
purpose-built `grader-judge` agent was registered. They used `general-purpose`
subagents under a prompt-level "use no tools" instruction; harness-observed
`tool_uses` was 0 for every one of them.

They are preserved, not discarded. All 23 judged trials were subsequently
re-judged under the tool-enforced `grader-judge` sandbox so the whole judged
set sits in one regime.

Because 12 of the same (question, standard, response) triples were judged
twice, this archive doubles as a direct TEST-RETEST RELIABILITY measurement on
the judge — which is the evidence H-judge asks for. The comparison is reported
in the exp001 report under "Judge reliability".
