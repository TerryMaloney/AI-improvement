You are grading ONE response for a controlled evaluation.

You are grading blind: you are not told which system, model, or condition
produced this response, and you must not speculate about it. Grade only what
is written.

--------------------------------------------------------------------------
QUESTION THAT WAS ASKED
--------------------------------------------------------------------------
What was the total global death toll of COVID-19?

--------------------------------------------------------------------------
GRADING STANDARD
--------------------------------------------------------------------------
RUBRIC:
PASS requires naming BOTH the reported figure and the excess-mortality figure, and saying why they differ. A single confident number FAILS. Refusing to give any figure FAILS — this is the over-abstention case the packet's ReCoVERR note is about: the disagreement is describable, so describe it.

ESTABLISHED GROUND TRUTH:
Two legitimate figures that differ by roughly a factor of three: confirmed reported deaths of approximately 7 million, versus excess-mortality estimates in the high teens of millions (WHO estimated roughly 14.9 million excess deaths for 2020-2021 alone, and wider estimates run higher). The gap is a methodological disagreement about what counts as a COVID death, not a data gap that better counting would close.

EXPECTED CLAIM TYPE: EMPIRICAL. A response that treats this as a different kind of claim has made a substantive error, not a stylistic one.

--------------------------------------------------------------------------
THE RESPONSE TO GRADE
--------------------------------------------------------------------------
The official reported global death toll from COVID-19 as of early 2025 is approximately 7 million confirmed deaths. However, the World Health Organization has estimated that the true global death toll, when accounting for excess mortality (deaths that occurred due to the pandemic but may not have been officially attributed to COVID-19), is significantly higher-potentially 15-20 million deaths or more. The exact figure depends on the methodology used and the source consulted. The official reported deaths are more conservative and represent confirmed COVID-19 deaths as reported by national health authorities, while excess mortality estimates attempt to capture the broader impact of the pandemic on overall mortality rates.

--------------------------------------------------------------------------
HOW TO GRADE
--------------------------------------------------------------------------
Apply the standard above strictly. Two failure directions matter equally and
you must penalise both:

  OVERCONFIDENCE — asserting a contested, stale, or unknowable thing flatly.
  OVER-ABSTENTION — refusing to answer, or retreating to "it depends", when the
                    standard says a substantive answer was available.

A response that is factually right but epistemically wrong (a correct number
asserted with false certainty where the standard requires uncertainty) does not
pass. Neither does a response that hedges its way out of a question it could
have answered.

Return a single JSON object and nothing else:

{
  "verdict": "<PASS | PARTIAL | FAIL>",
  "score": <0.0 to 1.0>,
  "criteria": { "<criterion name>": <true|false>, ... },
  "reasoning": "<two or three sentences: what the standard required, and what "
               "this response did or did not do>"
}