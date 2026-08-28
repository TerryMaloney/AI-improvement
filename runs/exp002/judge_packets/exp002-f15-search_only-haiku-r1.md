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
The total global death toll of COVID-19 was approximately 7.1 million confirmed deaths as of mid-2026. However, accounting for excess mortality and underreporting, the true toll is estimated at over 8.5 million deaths. The difference reflects challenges in consistent global reporting, as many countries had incomplete death registration and varying testing protocols. Major health organizations, including the WHO, ceased requiring daily death reporting in August 2023.

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