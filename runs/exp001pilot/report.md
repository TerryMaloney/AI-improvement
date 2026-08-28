# exp001-pilot — 2x2 factorial on haiku, with a prompt-enforced sandbox

**Experiment:** `exp001pilot`  
**Hypothesis under test:** H1, H1a, H1b  
**Batteries:** factual  
**Trials:** 60 (4 conditions × 1 models)

> PILOT RUN. Same 2x2 design as exp001, one model (haiku), and one important difference that the numbers must be read through. . SANDBOX CAVEAT: Claude Code loads .claude/agents/ at session start, and the sandboxed solver agents were created during the session that ran this pilot. They were therefore unavailable to it, and this run used general-purpose agents with the tool constraints stated in the prompt instead. So for this run the sandbox is PROMPT-ENFORCED, not TOOL-ENFORCED. The answer key was physically moved out of the repository for the duration of the solver runs, which does structurally block the file-read path, but a closed-condition agent retained a web search tool it was instructed not to use. . Which way this biases: undetected searching in a closed condition would make `baseline` and `directive_only` look BETTER than they are, understating any advantage of `verified`. So a positive result for the treatment survives the caveat; a null result is the one that cannot be trusted from this run alone. Ingest audits self-reported search counts, which catches the honest cases and none of the dishonest ones. . exp001 proper — tool-enforced sandbox, both models — runs from any session started after the agent definitions were committed.
> 

## Result integrity

Read this before the numbers. Every figure below is computed over *scored* trials only, and these are the trials that aren't in it.

- **Unanswered trials:** 24
- **Awaiting judge:** 0
- **Ungraded (unverified ground truth):** 0
- **Audit flags:** 0

## Headline: condition × model

| Condition | Model | Accuracy | Scored/n | Pass | Partial | Fail | Searches (total) | Hedge rate | Abstain rate |
|---|---|---|---|---|---|---|---|---|---|
| baseline | haiku | **60%** | 15/15 | 8 | 2 | 5 | 0 | 67% | 0% |
| directive_only | haiku | **73%** | 15/15 | 11 | 0 | 4 | 0 | 73% | 7% |
| search_only | haiku | **100%** | 6/15 | 6 | 0 | 0 | 6 | 33% | 0% |
| verified | haiku | **—** | 0/15 | 0 | 0 | 0 | 0 | — | 0% |

### Pooled across models

| Condition | Accuracy | Scored/n | Searches (total) | Mean answer chars | Hedge rate |
|---|---|---|---|---|---|
| baseline | **60%** | 15/15 | 0 | 413 | 67% |
| directive_only | **73%** | 15/15 | 0 | 513 | 73% |
| search_only | **100%** | 6/15 | 6 | 259 | 33% |
| verified | **—** | 0/15 | 0 | — | — |

### Cost of a correct answer

Searches per additional correct answer, versus the cheapest condition. This is the number that decides whether a procedure is worth running — an accuracy gain bought with unbounded retrieval is not a win.

Reference condition (fewest searches): **baseline**

| Condition | Δ accuracy vs reference | Extra searches | Searches per extra correct answer |
|---|---|---|---|
| baseline | +0 pts | +0 | — |
| directive_only | +13 pts | +0 | 0.0 |
| search_only | +40 pts | +6 | 2.5 |

## By question category

Where the effect actually lives. A gain concentrated in one category is a narrower finding than the headline number suggests.

| Category | baseline | directive_only | search_only | verified |
|---|---|---|---|---|
| ambiguous_referent | 95% (1/1) | 94% (1/1) | — (0/1) | — (0/1) |
| contested_quantity | 92% (1/1) | 95% (1/1) | — (0/1) | — (0/1) |
| deterministic | 100% (2/2) | 100% (2/2) | — (0/2) | — (0/2) |
| empirical_with_numbers | 95% (1/1) | 92% (1/1) | — (0/1) | — (0/1) |
| false_premise | 75% (3/3) | 100% (3/3) | 100% (1/3) | — (0/3) |
| moving_target | 65% (1/1) | 90% (1/1) | — (0/1) | — (0/1) |
| scheduled_entity | 0% (1/1) | 0% (1/1) | 100% (1/1) | — (0/1) |
| scheduled_hybrid_entity | 100% (1/1) | 100% (1/1) | 100% (1/1) | — (0/1) |
| stable_entity | 0% (1/1) | 100% (1/1) | 100% (1/1) | — (0/1) |
| stale_and_renamed | 35% (1/1) | 28% (1/1) | — (0/1) | — (0/1) |
| volatile_entity | 0% (2/2) | 0% (2/2) | 100% (2/2) | — (0/2) |

### Trap questions specifically

False-premise and stale-entity traps — the questions where a confident wrong answer is the failure being measured.

| Condition | Trap accuracy | Premise flagged |
|---|---|---|
| baseline | 65% (4/4) | 25% |
| directive_only | 82% (4/4) | 50% |
| search_only | 100% (1/4) | 25% |
| verified | — (0/4) | 0% |

## Per question

| Question | Routed as | baseline | directive_only | search_only | verified |
|---|---|---|---|---|---|
| `f01` | EMPIRICAL | ❌ | ❌ | ✅ | · |
| `f02` | EMPIRICAL | ❌ | ❌ | ✅ | · |
| `f03` | EMPIRICAL | ❌ | ❌ | ✅ | · |
| `f04` | EMPIRICAL | ✅ | ✅ | ✅ | · |
| `f05` | EMPIRICAL | ❌ | ✅ | ✅ | · |
| `f06` 🪤 | EMPIRICAL | ✅ | ✅ | ✅ | · |
| `f07` 🪤 | EMPIRICAL | ✅ | ✅ | · | · |
| `f08` 🪤 | EMPIRICAL | ❌ | ✅ | · | · |
| `f09` | DETERMINISTIC | ✅ | ✅ | · | · |
| `f10` | EMPIRICAL | ✅ | ✅ | · | · |
| `f11` | EMPIRICAL | ✅ | ✅ | · | · |
| `f12` 🪤 | EMPIRICAL | 🟡 | ❌ | · | · |
| `f13` | EMPIRICAL | ✅ | ✅ | · | · |
| `f14` | EMPIRICAL | 🟡 | ✅ | · | · |
| `f15` | EMPIRICAL | ✅ | ✅ | · | · |

✅ pass · 🟡 partial · ❌ fail · ⚪ ungraded (unverified ground truth) · ⏳ awaiting judge · · no answer · 🪤 trap question

## Where the conditions disagreed

The rows worth reading by hand. A condition winning on a question is only evidence if you can see *why* it won.

### `f01`

- **baseline** / haiku → **FAIL** (0 searches)
  > I do not have reliable information about who currently serves as Chief Revenue Officer of OpenAI as of August 2026. My knowledge was last updated in February 2025, and significant organizational changes could have occurred in the intervening months. Without access to current sear…
- **directive_only** / haiku → **FAIL** (0 searches)
  > I cannot reliably answer this question. My knowledge cutoff is February 2025, and you are asking about the current Chief Revenue Officer as of August 27, 2026. OpenAI has undergone significant leadership transitions and organizational changes in recent years, and I have no way to…
- **search_only** / haiku → **PASS** (1 searches)
  > Dali Rajic is currently the Chief Revenue Officer of OpenAI. He was appointed to the position in August 2026, taking over from Denise Dresser, who held the role for approximately nine months. Rajic, age 53, was previously the President and Chief Operating Officer of Wiz (an Alpha…
- **verified** / haiku → **NO_ANSWER** (? searches)

### `f02`

- **baseline** / haiku → **FAIL** (0 searches)
  > As of my knowledge cutoff in February 2025, Keir Starmer is the Prime Minister of the United Kingdom. However, since the current date is August 27, 2026-more than 6 months beyond my knowledge cutoff-I cannot confirm with certainty that he remains in office. Prime Ministers can ch…
- **directive_only** / haiku → **FAIL** (0 searches)
  > As of my last knowledge update in February 2025, Keir Starmer was the Prime Minister of the United Kingdom. He took office in July 2024 following Labour's election victory. However, you are asking about August 27, 2026, which is beyond my knowledge cutoff by over a year and a hal…
- **search_only** / haiku → **PASS** (1 searches)
  > Andy Burnham is the Prime Minister of the United Kingdom right now. He took office on July 20, 2026, becoming the 59th Prime Minister and the seventh to occupy Number 10 Downing Street in the past decade. He assumed the role after winning the Labour Party leadership following Kei…
- **verified** / haiku → **NO_ANSWER** (? searches)

### `f03`

- **baseline** / haiku → **FAIL** (0 searches)
  > Based on my training data (with a knowledge cutoff in February 2025), Jerome Powell is the Chair of the United States Federal Reserve. His current term is scheduled to end in June 2026. However, since the current system date is August 27, 2026 (beyond my knowledge cutoff), it is …
- **directive_only** / haiku → **FAIL** (0 searches)
  > As of my knowledge cutoff in February 2025, Jerome Powell was the Chair of the United States Federal Reserve, with a term scheduled to end in February 2026. However, the current date is August 27, 2026, which is after Powell's scheduled term end. I have no tools available to veri…
- **search_only** / haiku → **PASS** (1 searches)
  > Kevin Warsh is the Chair of the United States Federal Reserve. His term ends on May 21, 2030.
- **verified** / haiku → **NO_ANSWER** (? searches)

### `f04`

- **baseline** / haiku → **PASS** (0 searches)
  > Mark Rutte is the Secretary General of NATO, and yes, he is in his first term. Rutte took office on October 1, 2024, replacing Jens Stoltenberg who served for 10 years (2014-2024). Rutte's term as Secretary General began in 2024.
- **directive_only** / haiku → **PASS** (0 searches)
  > Based on my knowledge through February 2025, Mark Rutte is the Secretary General of NATO and is in his first term. He assumed office on October 1, 2024, succeeding Jens Stoltenberg who served two five-year terms. However, I should note that my knowledge cutoff is February 2025 an…
- **search_only** / haiku → **PASS** (1 searches)
  > Mark Rutte is the Secretary General of NATO. Yes, he is in his first term. Rutte took office on October 1, 2024, as the 14th NATO Secretary General. Since NATO Secretary General terms are typically 5 years, and he has only served approximately 22 months as of August 2026, he rema…
- **verified** / haiku → **NO_ANSWER** (? searches)

### `f05`

- **baseline** / haiku → **FAIL** (0 searches)
  > Based on my knowledge up to February 2025, Warren Buffett is the Chief Executive Officer of Berkshire Hathaway. However, I should note that my knowledge cutoff is February 2025, and the current date is August 2026, so there is a possibility of changes to leadership that I would n…
- **directive_only** / haiku → **PASS** (0 searches)
  > As of my knowledge cutoff in February 2025, Greg Abel is the Chief Executive Officer of Berkshire Hathaway. Warren Buffett, who had served as CEO since 1965, announced his transition away from the CEO role, with Greg Abel taking over. However, since the current date is August 202…
- **search_only** / haiku → **PASS** (1 searches)
  > Greg Abel is the Chief Executive Officer of Berkshire Hathaway. He became CEO effective January 1, 2026. Warren Buffett remains the Chairman of the Board.
- **verified** / haiku → **NO_ANSWER** (? searches)

### `f06`

- **baseline** / haiku → **PASS** (0 searches)
  > Nikola Tesla did not win the Nobel Prize in Physics. While he was a renowned inventor and engineer whose work contributed significantly to electrical engineering and wireless transmission technology, he never received the Nobel Prize in Physics. There are historical accounts sugg…
- **directive_only** / haiku → **PASS** (0 searches)
  > Nikola Tesla did not win the Nobel Prize in Physics. While Tesla was nominated for the Nobel Prize in Physics in 1912 (along with Thomas Edison, his famous rival), he did not receive the award. The 1912 Nobel Prize in Physics was awarded to Gustaf Dalen for his invention of autom…
- **search_only** / haiku → **PASS** (1 searches)
  > Nikola Tesla never won the Nobel Prize in Physics. While he was nominated and considered for the prize on multiple occasions (notably in 1912 and 1915), he never actually received the award. The 1912 prize went to Nils Gustaf Dalen, and the 1915 prize went to William Henry Bragg …
- **verified** / haiku → **NO_ANSWER** (? searches)

### `f07`

- **baseline** / haiku → **PASS** (0 searches)
  > I'm uncertain about this question because the phrasing 'US-Japan trade surpluses' is ambiguous. The US does not typically have a trade surplus with Japan-rather, the US runs a trade deficit with Japan (imports more than it exports). If the question intends to ask about the US tra…
- **directive_only** / haiku → **PASS** (0 searches)
  > I cannot directly answer this question as asked because the premise appears to be incorrect. The United States typically runs a trade deficit with Japan (meaning the US imports more than it exports), not a surplus. From my training data, in 2019 the US trade deficit with Japan wa…
- **search_only** / haiku → **NO_ANSWER** (? searches)
- **verified** / haiku → **NO_ANSWER** (? searches)

### `f08`

- **baseline** / haiku → **FAIL** (0 searches)
  > I am not aware of any European Union member states leaving the bloc in 2024. To my knowledge, the United Kingdom was the only EU member state to leave the bloc, departing on January 31, 2020 (Brexit). I have no information about two EU member states leaving in 2024, and I cannot …
- **directive_only** / haiku → **PASS** (0 searches)
  > This question appears to contain a false premise. Based on my knowledge through February 2025, no European Union member states left the bloc in 2024. The only EU member state to have left the European Union was the United Kingdom, which departed on January 31, 2020 (Brexit). Whil…
- **search_only** / haiku → **NO_ANSWER** (? searches)
- **verified** / haiku → **NO_ANSWER** (? searches)

### `f09`

- **baseline** / haiku → **PASS** (0 searches)
  > 1847 * 26 = 48,022
- **directive_only** / haiku → **PASS** (0 searches)
  > 1847 * 26 = 48,022 Calculation: 1847 * 26 = 1847 * (20 + 6) = (1847 * 20) + (1847 * 6) = 36,940 + 11,082 = 48,022
- **search_only** / haiku → **NO_ANSWER** (? searches)
- **verified** / haiku → **NO_ANSWER** (? searches)

### `f10`

- **baseline** / haiku → **PASS** (0 searches)
  > The average speed for the whole journey is 78 km/h. This is calculated by dividing the total distance by the total time: (240 km + 150 km) / (3 hours + 2 hours) = 390 km / 5 hours = 78 km/h.
- **directive_only** / haiku → **PASS** (0 searches)
  > The average speed for the whole journey is 78 km/h. This is calculated by dividing the total distance by the total time: (240 km + 150 km) / (3 hours + 2 hours) = 390 km / 5 hours = 78 km/h.
- **search_only** / haiku → **NO_ANSWER** (? searches)
- **verified** / haiku → **NO_ANSWER** (? searches)

### `f11`

- **baseline** / haiku → **PASS** (0 searches)
  > The 1918 influenza pandemic (Spanish flu) killed an estimated 50 to 100 million people worldwide, though exact figures are uncertain. The most commonly cited estimate by historians and health organizations is around 50 million deaths. The wide range reflects significant uncertain…
- **directive_only** / haiku → **PASS** (0 searches)
  > The 1918 influenza pandemic, also known as the Spanish Flu, killed an estimated 50 to 100+ million people globally, though the exact number remains uncertain. The commonly cited range is approximately 50-100 million deaths worldwide. Some more recent research estimates suggest th…
- **search_only** / haiku → **NO_ANSWER** (? searches)
- **verified** / haiku → **NO_ANSWER** (? searches)

### `f12`

- **baseline** / haiku → **PARTIAL** (0 searches)
  > Based on my training data with a knowledge cutoff of February 2025, Elon Musk is the CEO of Twitter (now branded as X). However, since the current date is August 27, 2026 - which is beyond my knowledge cutoff - it's possible this may have changed. I cannot confirm the current sta…
- **directive_only** / haiku → **FAIL** (0 searches)
  > As of my last knowledge update in February 2025, Elon Musk was the CEO of Twitter. However, I cannot verify whether this remains current as of August 2026, since I have no access to current information and my knowledge is now 6+ months out of date. CEO positions can change, so I …
- **search_only** / haiku → **NO_ANSWER** (? searches)
- **verified** / haiku → **NO_ANSWER** (? searches)

### `f13`

- **baseline** / haiku → **PASS** (0 searches)
  > Georgia has a population of approximately 10.8-10.9 million (as of 2024 estimates). This refers to the U.S. state of Georgia, which is the most common interpretation when the question is asked without qualification. Georgia had a 2020 Census population of 10,711,908, and has cont…
- **directive_only** / haiku → **PASS** (0 searches)
  > This question is ambiguous between two locations both called Georgia. The U.S. state of Georgia had a population of approximately 10.7 million as of the 2020 Census, with estimates around 10.8-10.9 million by 2023-2024. The country of Georgia (in the South Caucasus region) has a …
- **search_only** / haiku → **NO_ANSWER** (? searches)
- **verified** / haiku → **NO_ANSWER** (? searches)

### `f14`

- **baseline** / haiku → **PARTIAL** (0 searches)
  > As of my knowledge cutoff in February 2025, Saturn has approximately 146 confirmed moons. However, I should note that this number is subject to change as astronomers continue to discover and confirm new small moons in Saturn's system. Saturn recently surpassed Jupiter as the plan…
- **directive_only** / haiku → **PASS** (0 searches)
  > As of my knowledge cutoff in February 2025, Saturn has 146 confirmed moons. This surpasses Jupiter as the planet with the most moons in our solar system. However, I should note that new moons are regularly discovered and confirmed through astronomical observation, so this number …
- **search_only** / haiku → **NO_ANSWER** (? searches)
- **verified** / haiku → **NO_ANSWER** (? searches)

### `f15`

- **baseline** / haiku → **PASS** (0 searches)
  > The official reported global death toll from COVID-19 as of early 2025 is approximately 7 million confirmed deaths. However, the World Health Organization has estimated that the true global death toll, when accounting for excess mortality (deaths that occurred due to the pandemic…
- **directive_only** / haiku → **PASS** (0 searches)
  > As of my knowledge cutoff in February 2025, the WHO had officially confirmed approximately 7 million COVID-19 deaths globally. However, the WHO has acknowledged that the true death toll is substantially higher when accounting for excess mortality and unreported deaths, with estim…
- **search_only** / haiku → **NO_ANSWER** (? searches)
- **verified** / haiku → **NO_ANSWER** (? searches)
