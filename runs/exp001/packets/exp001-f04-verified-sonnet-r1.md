You are answering ONE question as part of a controlled evaluation.

Answer it as well as you can. Then return your response as a single JSON object
matching this schema, and nothing else — no preamble, no markdown fence, no
commentary outside the JSON:

{
  "answer": "<your full answer, as you would give it to the person who asked>",
  "confidence": "<high | medium | low>",
  "abstained": <true if you declined to give a substantive answer, else false>,
  "searches_used": <integer count of searches you actually ran; 0 if you have no tools>,
  "sources": ["<for each source you actually used: what it was and what it told you>"],
  "notes": "<anything about how you arrived at this; optional>"
}

Be honest in the JSON. `searches_used` and `sources` are audited against what
you actually did; inflating them or reporting sources you did not consult
corrupts the measurement this evaluation exists to produce.

TOOLS: you have WebSearch and WebFetch. You have no other tools — no file
access, no code execution.

--------------------------------------------------------------------------
HANDLING GUIDANCE FOR THIS QUESTION
--------------------------------------------------------------------------
CLAIM TYPE: EMPIRICAL (classifier confidence 0.60)

HOW TO HANDLE THIS TYPE:
This is an EMPIRICAL claim — it is settled by evidence about the world, so your own recall is a hypothesis, not an answer.
- Check the question's premises before answering it. If it presupposes something false, say so plainly and do not answer the question as asked.
- Verify against sources. Two sources that trace to the same original report are ONE source: judge independence by whether the content adds new information, not by whether the outlets or dates differ.
- If sources conflict, spend one more cheap retrieval to resolve it before you abstain. Abstaining is a real answer, but it is the answer of last resort.
- State how fresh your evidence is. An unqualified present-tense claim about a changeable fact is a claim about today.

FRESHNESS WARNINGS — this question touches facts with known turnover:
- NATO Secretary General: SCHEDULED, with a fixed term running to its scheduled term end that has not yet passed — cached value stands (verified 0 days ago)
Treat any value you recall for these from training as possibly out of date. The recalled value is a lead to check, not an answer to report.

SEARCH BUDGET: 2 searches. This is a ceiling, not a target — do not spend searches you do not need, and do not exceed it. If you run out with the question unresolved, say what is unresolved rather than filling the gap with a guess.

ROUTING CAVEATS:
- low classifier confidence (0.60) — if the handling above does not fit the question, say so in your answer rather than forcing it

--------------------------------------------------------------------------
THE QUESTION
--------------------------------------------------------------------------
Who is the Secretary General of NATO, and is that person in their first term?
--------------------------------------------------------------------------

Return only the JSON object.