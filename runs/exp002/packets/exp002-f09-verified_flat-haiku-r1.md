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
CLAIM TYPE: DETERMINISTIC (classifier confidence 0.90)

HOW TO HANDLE THIS TYPE:
This is DETERMINISTIC — computable from what the question already gives you.
- Compute it. Do not search.
- Show the steps so the arithmetic is checkable.
- If the computation turns out to need a fact you do not have, STOP: the routing was wrong and this is actually an empirical question. Say so instead of guessing the missing input.

SEARCH BUDGET: 3 searches. This is a ceiling, not a target — do not spend searches you do not need, and do not exceed it. If you run out with the question unresolved, say what is unresolved rather than filling the gap with a guess.

--------------------------------------------------------------------------
THE QUESTION
--------------------------------------------------------------------------
What is 1847 * 26?
--------------------------------------------------------------------------

Return only the JSON object.