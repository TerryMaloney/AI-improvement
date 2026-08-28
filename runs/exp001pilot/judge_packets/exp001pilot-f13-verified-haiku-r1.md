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
The population of Georgia depends on which Georgia you're asking about: the U.S. state of Georgia has a population of approximately 11,401,288 (2026), making it the 8th most populated state. The country of Georgia (in the Caucasus region) has a population of approximately 3,804,642 (2026). If referring to the U.S. state, the population is approximately 11.4 million.

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