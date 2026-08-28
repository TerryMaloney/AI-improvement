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

SEARCH BUDGET: 3 searches. Treat it as a ceiling, not a target. Spend nothing on
a question you can already answer well; spend up to the ceiling on one you
cannot. Report the true count in `searches_used`.

--------------------------------------------------------------------------
THE QUESTION
--------------------------------------------------------------------------
How many people died in the 1918 influenza pandemic?
--------------------------------------------------------------------------

Return only the JSON object.