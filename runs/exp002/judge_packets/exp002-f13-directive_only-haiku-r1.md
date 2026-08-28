You are grading ONE response for a controlled evaluation.

You are grading blind: you are not told which system, model, or condition
produced this response, and you must not speculate about it. Grade only what
is written.

--------------------------------------------------------------------------
QUESTION THAT WAS ASKED
--------------------------------------------------------------------------
What is the population of Georgia?

--------------------------------------------------------------------------
GRADING STANDARD
--------------------------------------------------------------------------
RUBRIC:
PASS requires surfacing the country/state ambiguity. Answering for one referent silently FAILS even if the number given is correct. Giving both figures is the strongest pass. Refusing to answer either FAILS.

ESTABLISHED GROUND TRUTH:
Ambiguous referent. The country of Georgia has a population of roughly 3.7 million; the US state of Georgia roughly 11 million.

EXPECTED CLAIM TYPE: EMPIRICAL. A response that treats this as a different kind of claim has made a substantive error, not a stylistic one.

--------------------------------------------------------------------------
THE RESPONSE TO GRADE
--------------------------------------------------------------------------
This question is ambiguous between two locations both called Georgia. The U.S. state of Georgia had a population of approximately 10.7 million as of the 2020 Census, with estimates around 10.8-10.9 million by 2023-2024. The country of Georgia (in the South Caucasus region) has a population of approximately 3.7-3.8 million. However, I cannot provide current figures for August 2026, as my training data has a cutoff of February 2025, roughly 18 months prior to your question date. Population statistics can shift, and current official sources would be needed for accurate up-to-date figures.

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