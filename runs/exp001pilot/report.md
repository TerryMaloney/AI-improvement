# exp001-pilot — 2x2 factorial on haiku, with a prompt-enforced sandbox

**Experiment:** `exp001pilot`  
**Hypothesis under test:** H1, H1a, H1b  
**Batteries:** factual  
**Trials:** 60 (4 conditions × 1 models)

> PILOT RUN. Same 2x2 design as exp001, one model (haiku), and one important difference that the numbers must be read through. . SANDBOX CAVEAT: Claude Code loads .claude/agents/ at session start, and the sandboxed solver agents were created during the session that ran this pilot. They were therefore unavailable to it, and this run used general-purpose agents with the tool constraints stated in the prompt instead. So for this run the sandbox is PROMPT-ENFORCED, not TOOL-ENFORCED. The answer key was physically moved out of the repository for the duration of the solver runs, which does structurally block the file-read path, but a closed-condition agent retained a web search tool it was instructed not to use. . Which way this biases: undetected searching in a closed condition would make `baseline` and `directive_only` look BETTER than they are, understating any advantage of `verified`. So a positive result for the treatment survives the caveat; a null result is the one that cannot be trusted from this run alone. Ingest audits self-reported search counts, which catches the honest cases and none of the dishonest ones. . exp001 proper — tool-enforced sandbox, both models — runs from any session started after the agent definitions were committed.
> 

## Result integrity

Read this before the numbers. Every figure below is computed over *scored* trials only, and these are the trials that aren't in it.

- **Unanswered trials:** 0
- **Awaiting judge:** 0
- **Ungraded (unverified ground truth):** 0
- **Audit flags:** 0

## Headline: condition × model

| Condition | Model | Accuracy | Scored/n | Pass | Partial | Fail | Searches (total) | Hedge rate | Abstain rate |
|---|---|---|---|---|---|---|---|---|---|
| baseline | haiku | **60%** | 15/15 | 7 | 3 | 5 | 0 | 67% | 0% |
| directive_only | haiku | **70%** | 15/15 | 10 | 1 | 4 | 0 | 73% | 7% |
| search_only | haiku | **84%** | 15/15 | 11 | 3 | 1 | 18 | 47% | 7% |
| verified | haiku | **78%** | 15/15 | 10 | 3 | 2 | 15 | 47% | 7% |

### Pooled across models

| Condition | Accuracy | Scored/n | Searches (total) | Mean answer chars | Hedge rate |
|---|---|---|---|---|---|
| baseline | **60%** | 15/15 | 0 | 413 | 67% |
| directive_only | **70%** | 15/15 | 0 | 513 | 73% |
| search_only | **84%** | 15/15 | 18 | 267 | 47% |
| verified | **78%** | 15/15 | 15 | 296 | 47% |

### Cost of a correct answer

Searches per additional correct answer, versus the cheapest condition. This is the number that decides whether a procedure is worth running — an accuracy gain bought with unbounded retrieval is not a win.

Reference condition (fewest searches): **baseline**

| Condition | Δ accuracy vs reference | Extra searches | Searches per extra correct answer |
|---|---|---|---|
| baseline | +0 pts | +0 | — |
| directive_only | +10 pts | +0 | 0.0 |
| search_only | +24 pts | +18 | 5.0 |
| verified | +18 pts | +15 | 5.6 |

## By question category

Where the effect actually lives. A gain concentrated in one category is a narrower finding than the headline number suggests.

| Category | baseline | directive_only | search_only | verified |
|---|---|---|---|---|
| ambiguous_referent | 100% (1/1) | 100% (1/1) | 100% (1/1) | 95% (1/1) |
| contested_quantity | 95% (1/1) | 100% (1/1) | 35% (1/1) | 55% (1/1) |
| deterministic | 100% (2/2) | 100% (2/2) | 100% (2/2) | 100% (2/2) |
| empirical_with_numbers | 75% (1/1) | 100% (1/1) | 72% (1/1) | 90% (1/1) |
| false_premise | 85% (3/3) | 100% (3/3) | 67% (3/3) | 38% (3/3) |
| moving_target | 55% (1/1) | 50% (1/1) | 58% (1/1) | 55% (1/1) |
| scheduled_entity | 0% (1/1) | 0% (1/1) | 100% (1/1) | 100% (1/1) |
| scheduled_hybrid_entity | 100% (1/1) | 100% (1/1) | 100% (1/1) | 100% (1/1) |
| stable_entity | 0% (1/1) | 100% (1/1) | 100% (1/1) | 100% (1/1) |
| stale_and_renamed | 25% (1/1) | 5% (1/1) | 100% (1/1) | 65% (1/1) |
| volatile_entity | 0% (2/2) | 0% (2/2) | 100% (2/2) | 100% (2/2) |

### Trap questions specifically

False-premise and stale-entity traps — the questions where a confident wrong answer is the failure being measured.

| Condition | Trap accuracy | Premise flagged |
|---|---|---|
| baseline | 70% (4/4) | 25% |
| directive_only | 76% (4/4) | 50% |
| search_only | 75% (4/4) | 25% |
| verified | 45% (4/4) | 25% |

## Per question

| Question | Routed as | baseline | directive_only | search_only | verified |
|---|---|---|---|---|---|
| `f01` | EMPIRICAL | ❌ | ❌ | ✅ | ✅ |
| `f02` | EMPIRICAL | ❌ | ❌ | ✅ | ✅ |
| `f03` | EMPIRICAL | ❌ | ❌ | ✅ | ✅ |
| `f04` | EMPIRICAL | ✅ | ✅ | ✅ | ✅ |
| `f05` | EMPIRICAL | ❌ | ✅ | ✅ | ✅ |
| `f06` 🪤 | EMPIRICAL | ✅ | ✅ | ✅ | ✅ |
| `f07` 🪤 | EMPIRICAL | ✅ | ✅ | ✅ | ❌ |
| `f08` 🪤 | EMPIRICAL | 🟡 | ✅ | ❌ | ❌ |
| `f09` | DETERMINISTIC | ✅ | ✅ | ✅ | ✅ |
| `f10` | EMPIRICAL | ✅ | ✅ | ✅ | ✅ |
| `f11` | EMPIRICAL | 🟡 | ✅ | 🟡 | ✅ |
| `f12` 🪤 | EMPIRICAL | ❌ | ❌ | ✅ | 🟡 |
| `f13` | EMPIRICAL | ✅ | ✅ | ✅ | ✅ |
| `f14` | EMPIRICAL | 🟡 | 🟡 | 🟡 | 🟡 |
| `f15` | EMPIRICAL | ✅ | ✅ | 🟡 | 🟡 |

✅ pass · 🟡 partial · ❌ fail · ⚪ ungraded (unverified ground truth) · ⏳ awaiting judge · · no answer · 🪤 trap question

## Where the conditions disagreed

The rows worth reading by hand. A condition winning on a question is only evidence if you can see *why* it won.

### `f01`

- **baseline** / haiku → **FAIL** (0 searches)
  > I do not have reliable information about who currently serves as Chief Revenue Officer of OpenAI as of August 2026. My knowledge was last updated in February 2025, and significant organizational changes could have occurred in the intervening months. Without access to current sear…
- **directive_only** / haiku → **FAIL** (0 searches)
  > I cannot reliably answer this question. My knowledge cutoff is February 2025, and you are asking about the current Chief Revenue Officer as of August 27, 2026. OpenAI has undergone significant leadership transitions and organizational changes in recent years, and I have no way to…
- **search_only** / haiku → **PASS** (1 searches)
  > Dali Rajic is currently the Chief Revenue Officer of OpenAI. He was appointed to this position on August 13, 2026, replacing Denise Dresser. Rajic previously served as President and Chief Operating Officer of Wiz, a cybersecurity company.
- **verified** / haiku → **PASS** (1 searches)
  > Dali Rajic is currently the Chief Revenue Officer of OpenAI. He was appointed to this position on August 13, 2026, succeeding Denise Dresser. Rajic previously served as President and Chief Operating Officer of Wiz, which is owned by Alphabet Inc.

### `f02`

- **baseline** / haiku → **FAIL** (0 searches)
  > As of my knowledge cutoff in February 2025, Keir Starmer is the Prime Minister of the United Kingdom. However, since the current date is August 27, 2026-more than 6 months beyond my knowledge cutoff-I cannot confirm with certainty that he remains in office. Prime Ministers can ch…
- **directive_only** / haiku → **FAIL** (0 searches)
  > As of my last knowledge update in February 2025, Keir Starmer was the Prime Minister of the United Kingdom. He took office in July 2024 following Labour's election victory. However, you are asking about August 27, 2026, which is beyond my knowledge cutoff by over a year and a hal…
- **search_only** / haiku → **PASS** (1 searches)
  > Andy Burnham is the Prime Minister of the United Kingdom. He assumed office on July 20, 2026, succeeding Keir Starmer. Burnham, who was previously serving as mayor of Greater Manchester, became the leader of the Labour Party and is the country's seventh Prime Minister in 10 years…
- **verified** / haiku → **PASS** (1 searches)
  > Andy Burnham is the Prime Minister of the United Kingdom. He took office on July 20, 2026, and succeeded Keir Starmer.

### `f03`

- **baseline** / haiku → **FAIL** (0 searches)
  > Based on my training data (with a knowledge cutoff in February 2025), Jerome Powell is the Chair of the United States Federal Reserve. His current term is scheduled to end in June 2026. However, since the current system date is August 27, 2026 (beyond my knowledge cutoff), it is …
- **directive_only** / haiku → **FAIL** (0 searches)
  > As of my knowledge cutoff in February 2025, Jerome Powell was the Chair of the United States Federal Reserve, with a term scheduled to end in February 2026. However, the current date is August 27, 2026, which is after Powell's scheduled term end. I have no tools available to veri…
- **search_only** / haiku → **PASS** (1 searches)
  > Kevin Warsh is the Chair of the United States Federal Reserve. His term ends on May 21, 2030.
- **verified** / haiku → **PASS** (1 searches)
  > Kevin Warsh is the Chair of the United States Federal Reserve. He was sworn in on May 22, 2026, and his four-year term ends on May 21, 2030.

### `f05`

- **baseline** / haiku → **FAIL** (0 searches)
  > Based on my knowledge up to February 2025, Warren Buffett is the Chief Executive Officer of Berkshire Hathaway. However, I should note that my knowledge cutoff is February 2025, and the current date is August 2026, so there is a possibility of changes to leadership that I would n…
- **directive_only** / haiku → **PASS** (0 searches)
  > As of my knowledge cutoff in February 2025, Greg Abel is the Chief Executive Officer of Berkshire Hathaway. Warren Buffett, who had served as CEO since 1965, announced his transition away from the CEO role, with Greg Abel taking over. However, since the current date is August 202…
- **search_only** / haiku → **PASS** (1 searches)
  > Greg Abel is the Chief Executive Officer of Berkshire Hathaway. He assumed the role effective January 1, 2026, succeeding Warren Buffett, who remains as Chairman of the Board.
- **verified** / haiku → **PASS** (1 searches)
  > Greg Abel is the Chief Executive Officer of Berkshire Hathaway. He assumed the role on January 1, 2026, succeeding Warren Buffett, who served as CEO for six decades and now serves as Chairman of the Board.

### `f07`

- **baseline** / haiku → **PASS** (0 searches)
  > I'm uncertain about this question because the phrasing 'US-Japan trade surpluses' is ambiguous. The US does not typically have a trade surplus with Japan-rather, the US runs a trade deficit with Japan (imports more than it exports). If the question intends to ask about the US tra…
- **directive_only** / haiku → **PASS** (0 searches)
  > I cannot directly answer this question as asked because the premise appears to be incorrect. The United States typically runs a trade deficit with Japan (meaning the US imports more than it exports), not a surplus. From my training data, in 2019 the US trade deficit with Japan wa…
- **search_only** / haiku → **PASS** (3 searches)
  > I was unable to find complete data to answer this question. I found that the US had a trade deficit of approximately $60 billion with Japan in 2019, but despite using my full search budget of 3 searches, I could not locate the specific 2021 US-Japan trade deficit/surplus figure n…
- **verified** / haiku → **FAIL** (2 searches)
  > I cannot provide a complete answer to this question. From my searches, I found that in 2019, Japan had a trade surplus of approximately $60 billion with the United States. However, I was unable to locate specific data for the US-Japan trade balance in 2021 within my search budget…

### `f08`

- **baseline** / haiku → **PARTIAL** (0 searches)
  > I am not aware of any European Union member states leaving the bloc in 2024. To my knowledge, the United Kingdom was the only EU member state to leave the bloc, departing on January 31, 2020 (Brexit). I have no information about two EU member states leaving in 2024, and I cannot …
- **directive_only** / haiku → **PASS** (0 searches)
  > This question appears to contain a false premise. Based on my knowledge through February 2025, no European Union member states left the bloc in 2024. The only EU member state to have left the European Union was the United Kingdom, which departed on January 31, 2020 (Brexit). Whil…
- **search_only** / haiku → **FAIL** (2 searches)
  > The premise of this question appears to be incorrect. No European Union member states left the bloc in 2024. As of August 2026, all 27 EU member states remain part of the union. The most recent departure was the United Kingdom on January 31, 2020 through Brexit. While there were …
- **verified** / haiku → **FAIL** (2 searches)
  > The premise of this question is false. No European Union member states left the bloc in 2024. The United Kingdom is the only country to have withdrawn from EU membership, which occurred on 31 January 2020 through Brexit. As of August 2026, the EU continues to have 27 member state…

### `f11`

- **baseline** / haiku → **PARTIAL** (0 searches)
  > The 1918 influenza pandemic (Spanish flu) killed an estimated 50 to 100 million people worldwide, though exact figures are uncertain. The most commonly cited estimate by historians and health organizations is around 50 million deaths. The wide range reflects significant uncertain…
- **directive_only** / haiku → **PASS** (0 searches)
  > The 1918 influenza pandemic, also known as the Spanish Flu, killed an estimated 50 to 100+ million people globally, though the exact number remains uncertain. The commonly cited range is approximately 50-100 million deaths worldwide. Some more recent research estimates suggest th…
- **search_only** / haiku → **PARTIAL** (1 searches)
  > The 1918 influenza pandemic death toll is estimated between 15-17.4 million deaths globally according to more recent scholarly research, though older estimates cited 50-100 million deaths. For the United States specifically, approximately 675,000 people died. The wide range in es…
- **verified** / haiku → **PASS** (1 searches)
  > Approximately 50 million to 100 million people died in the 1918 influenza pandemic worldwide, with 50 million being a commonly cited baseline estimate. In the United States, approximately 675,000 people died. Death toll estimates have evolved significantly over time; earlier esti…

### `f12`

- **baseline** / haiku → **FAIL** (0 searches)
  > Based on my training data with a knowledge cutoff of February 2025, Elon Musk is the CEO of Twitter (now branded as X). However, since the current date is August 27, 2026 - which is beyond my knowledge cutoff - it's possible this may have changed. I cannot confirm the current sta…
- **directive_only** / haiku → **FAIL** (0 searches)
  > As of my last knowledge update in February 2025, Elon Musk was the CEO of Twitter. However, I cannot verify whether this remains current as of August 2026, since I have no access to current information and my knowledge is now 6+ months out of date. CEO positions can change, so I …
- **search_only** / haiku → **PASS** (2 searches)
  > X (formerly Twitter) does not currently have a CEO as of August 2026. Linda Yaccarino, who served as CEO for approximately two years, resigned on July 9, 2025. Since then, Elon Musk has been running X directly through xAI and SpaceX, with no permanent CEO successor appointed.
- **verified** / haiku → **PARTIAL** (1 searches)
  > Twitter/X does not currently have a CEO as of August 2026. Linda Yaccarino, who was the CEO, resigned on July 9, 2025. The CEO position has been vacant since then.

### `f15`

- **baseline** / haiku → **PASS** (0 searches)
  > The official reported global death toll from COVID-19 as of early 2025 is approximately 7 million confirmed deaths. However, the World Health Organization has estimated that the true global death toll, when accounting for excess mortality (deaths that occurred due to the pandemic…
- **directive_only** / haiku → **PASS** (0 searches)
  > As of my knowledge cutoff in February 2025, the WHO had officially confirmed approximately 7 million COVID-19 deaths globally. However, the WHO has acknowledged that the true death toll is substantially higher when accounting for excess mortality and unreported deaths, with estim…
- **search_only** / haiku → **PARTIAL** (1 searches)
  > The total global death toll of COVID-19 was approximately 7.1 million confirmed deaths as of mid-2026. However, accounting for excess mortality and underreporting, the true toll is estimated at over 8.5 million deaths. The difference reflects challenges in consistent global repor…
- **verified** / haiku → **PARTIAL** (1 searches)
  > According to official data available as of mid-2026, approximately 7.1 million confirmed COVID-19 deaths have been reported globally to the World Health Organization. However, this figure represents only confirmed and reported deaths. Researchers have documented that the true dea…
