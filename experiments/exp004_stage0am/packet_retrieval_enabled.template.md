You are answering ONE question as part of a controlled evaluation.

Answer it as well as you can. Then return your response as a single JSON object
matching this schema, and nothing else — no preamble, no markdown fence, no
commentary outside the JSON:

{
  "answer": "<your full answer, as you would give it to the person who asked>",
  "confidence": "<high | medium | low>",
  "abstained": <true if you declined to give a substantive answer, else false>
}

TOOLS: you have WebSearch and WebFetch as external-information tools. You may use
them if you judge it useful, and you may decline to use them.

Answer the question exactly as asked. If the question specifies a date, a
definition, a scope or a unit, answer for what the question specifies.

--------------------------------------------------------------------------
THE QUESTION
--------------------------------------------------------------------------
{QUESTION}
--------------------------------------------------------------------------

Return only the JSON object.
