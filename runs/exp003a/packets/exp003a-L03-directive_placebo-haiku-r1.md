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

TOOLS: you have none. No search, no browsing, no files. Answer from what you
already know.

If you do not know, or your knowledge may be out of date, say that in the
answer rather than producing a plausible-sounding guess. A clearly-flagged "I
am not confident, and here is why" is a better answer here than a confident
wrong one — but refusing to engage with a question you could reasonably address
is also a failure. Set `searches_used` to 0.

--------------------------------------------------------------------------
HANDLING GUIDANCE FOR THIS QUESTION
--------------------------------------------------------------------------
RESPONSE REGISTER: EXPLANATORY (profile weight 0.90)

HOW TO PRESENT THIS ANSWER:
This is an EXPLANATORY response — it will be read once, in one pass, by someone deciding what to do with it next, so the way it is arranged is not decoration but part of what it actually communicates.
- Decide who the answer is for before you start writing it, and keep that reader in view while you write, rather than settling it afterwards.
- Put the part that actually answers the question where a reader reaches it first, ahead of the material that leads up to it.
- Use one word per idea and keep using it — varying the term for style makes a reader stop and wonder whether the meaning varied too.
- Keep roughly one idea to a sentence, because a sentence carrying three of them usually delivers one and hides the other two.

ORDERING: arrange the material in the order that serves a reader — not the order it arrived in while you were working the answer out.

STYLE CAVEATS:
- Register should hold level throughout the answer; a shift midway through reads to a reader as a change of audience, and they will spend attention working out which of the two they are.

--------------------------------------------------------------------------
THE QUESTION
--------------------------------------------------------------------------
Which protein makes the blood of a horseshoe crab blue?
--------------------------------------------------------------------------

Return only the JSON object.