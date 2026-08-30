# Stage 0A-M key-construction provenance

All 50 primary keys are SOURCE-VERIFIED. Three passes are recorded: pass-1 during authoring,
pass-2 independent source verification, pass-3 the post-verification audit. Timestamps are offset-aware ISO-8601 (UTC).

**KEY-CONSTRUCTION EVIDENCE.** Public sources consulted to establish keys before any
dispatch. This is not EXPERIMENTAL RETRIEVAL EVIDENCE, which does not yet exist: no
production item has been shown to any solver, in either arm.

Only the minimum needed to support each key is recorded; no source passages are reproduced.

### a01 — date_anchored / officeholder (politics/Germany)

- **Stem:** As of 1 March 2021, who was the Chancellor of Germany?
- **Route:** `exact_entity` · key fingerprint `94e3f06e33f514e9`
- **Anchored state:** Angela Merkel · **displacing state:** a later chancellor
- **Temporal distance:** ~5 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** PBS NewsHour; Britannica 'Angela Merkel: Chancellorship' — Scholz sworn in 2021-12-08
- **Why it supports the key:** Merkel held office continuously until 2021-12-08, after the anchor date.

### a02 — date_anchored / officeholder (politics/UK)

- **Stem:** As of 1 June 2022, who was the Prime Minister of the United Kingdom?
- **Route:** `exact_entity` · key fingerprint `acc16650d202ec1f`
- **Anchored state:** Boris Johnson · **displacing state:** a later PM
- **Temporal distance:** ~4 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** Wikipedia 'Boris Johnson'; Britannica — premiership 2019-07-24 to 2022-09-06
- **Why it supports the key:** The anchor date falls inside Johnson's continuous premiership.

### a03 — date_anchored / entity_name (corporate/social)

- **Stem:** As of 1 January 2021, what was the registered corporate name of the company that owned and operated both Instagram and WhatsApp?
- **Route:** `exact_entity` · key fingerprint `62cf353120fa7af8`
- **Anchored state:** Facebook, Inc. · **displacing state:** Meta Platforms, Inc.
- **Temporal distance:** ~5 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** SEC Form 8-K fb-20211028 — bylaws amended 2021-10-28 for the name change
- **Why it supports the key:** The rename took legal effect 2021-10-28, after the anchor date.
- **Ambiguity notes:** Rewritten at authoring: the earlier stem named the social network and so contained the answer.

### a04 — date_anchored / entity_name (technology)

- **Stem:** As of 1 January 2023, what was the name of the microblogging platform whose logo was a blue bird?
- **Route:** `exact_entity` · key fingerprint `41e52ca42a2dc39f`
- **Anchored state:** Twitter · **displacing state:** X
- **Temporal distance:** ~3 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** Wikipedia 'X (social network)'; Britannica 'Twitter' — rebrand 2023-07-23
- **Why it supports the key:** The rebrand to X occurred 2023-07-23, after the anchor date.
- **Ambiguity notes:** Rewritten at authoring: the earlier stem cited the domain name and so contained the answer.

### a05 — date_anchored / membership_status (international/NATO)

- **Stem:** As of 1 January 2022, was Finland a member of NATO? Answer yes or no.
- **Route:** `boolean` · key fingerprint `0a8a56fc733acdc6`
- **Anchored state:** No · **displacing state:** Yes
- **Temporal distance:** ~4 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** nato.int news_213448 — Finland joined as 31st Ally 2023-04-04
- **Why it supports the key:** Accession followed the anchor date by fifteen months.

### a06 — date_anchored / membership_status (international/NATO)

- **Stem:** As of 1 January 2023, was Sweden a member of NATO? Answer yes or no.
- **Route:** `boolean` · key fingerprint `0a8a56fc733acdc6`
- **Anchored state:** No · **displacing state:** Yes
- **Temporal distance:** ~3 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** UK House of Commons Library CBP-9574 — Sweden joined 2024-03-07
- **Why it supports the key:** Accession followed the anchor date by fourteen months.

### a07 — date_anchored / currency (economics/Croatia)

- **Stem:** As of 1 June 2022, what was the official currency of Croatia?
- **Route:** `exact_entity` · key fingerprint `49d452fefdd29973`
- **Anchored state:** Croatian kuna · **displacing state:** euro
- **Temporal distance:** ~4 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** Croatian National Bank (hnb.hr); ECB euro changeover page — euro adopted 2023-01-01
- **Why it supports the key:** The kuna was sole legal tender until the 2023-01-01 changeover.

### a08 — date_anchored / canonical_count (science/astronomy)

- **Stem:** As of 1 January 2006, how many planets did the International Astronomical Union recognise in the Solar System?
- **Route:** `numeric` · key fingerprint `858c4fb30396f6b5`
- **Anchored state:** 9 · **displacing state:** 8
- **Temporal distance:** ~20 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** Library of Congress Everyday Mysteries; astronomy.com — IAU vote 2006-08-24
- **Why it supports the key:** Nine were recognised until the reclassification vote of 2006-08-24.

### a09 — date_anchored / org_status (international/EU)

- **Stem:** As of 1 January 2020, was the United Kingdom a member state of the European Union? Answer yes or no.
- **Route:** `boolean` · key fingerprint `a76bdac6d0d3cd20`
- **Anchored state:** Yes · **displacing state:** No
- **Temporal distance:** ~6 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** European Commission qanda_20_104; EMA — withdrawal effective 2020-01-31
- **Why it supports the key:** The UK remained a member state until 2020-01-31, one month after the anchor date.

### a10 — date_anchored / officeholder (international/UN)

- **Stem:** As of 1 January 2016, who was the Secretary-General of the United Nations?
- **Route:** `exact_entity` · key fingerprint `f3e14211791ba26c`
- **Anchored state:** Ban Ki-moon · **displacing state:** António Guterres
- **Temporal distance:** ~10 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** un.org 'Ban Ki-moon, Former Secretary-General'; UN Photo — term 2007-01-01 to 2016-12-31
- **Why it supports the key:** The anchor date falls inside Ban Ki-moon's second term.

### a11 — date_anchored / officeholder (international/EU)

- **Stem:** As of 1 June 2019, who was the President of the European Commission?
- **Route:** `exact_entity` · key fingerprint `6d6b45b2897aecea`
- **Anchored state:** Jean-Claude Juncker · **displacing state:** Ursula von der Leyen
- **Temporal distance:** ~7 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** European Commission / Juncker Commission record (via wikidata Q57661, Q8882)
- **Why it supports the key:** Juncker's term ran 2014-11-01 to 2019-11-30; von der Leyen took office 2019-12-01. The 2019-06-01 anchor is inside Juncker's term.

### a12 — date_anchored / sovereignty_status (geopolitics)

- **Stem:** As of 1 January 2011, was South Sudan an independent sovereign state? Answer yes or no.
- **Route:** `boolean` · key fingerprint `0a8a56fc733acdc6`
- **Anchored state:** No · **displacing state:** Yes
- **Temporal distance:** ~15 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** UN membership record; South Sudan independence 2011-07-09
- **Why it supports the key:** Independence was declared 2011-07-09, six months after the 2011-01-01 anchor, so the answer at the anchor is No.

### a13 — date_anchored / officeholder (politics/Brazil)

- **Stem:** As of 1 June 2020, who was the President of Brazil?
- **Route:** `exact_entity` · key fingerprint `236d31ba973f8962`
- **Anchored state:** Jair Bolsonaro · **displacing state:** Lula da Silva
- **Temporal distance:** ~6 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** Brazilian presidential record; Bolsonaro term 2019-01-01 to 2022-12-31
- **Why it supports the key:** The 2020-06-01 anchor falls inside Bolsonaro's single term; Lula returned 2023-01-01.

### a14 — date_anchored / corporate_structure (corporate/technology)

- **Stem:** As of 1 June 2015, what was the name of the publicly listed company whose principal product was the world's most used web search engine?
- **Route:** `exact_entity` · key fingerprint `bd3aa6c9697ca94b`
- **Anchored state:** Google Inc. · **displacing state:** Alphabet Inc.
- **Temporal distance:** ~11 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** SEC Form 8-K, Alphabet Inc. CIK 0001652044, filed October 2015
- **Why it supports the key:** The legal reorganisation completed 2015-10-02 made Google a wholly owned subsidiary of Alphabet. At the 2015-06-01 anchor the listed company was Google Inc.
- **Ambiguity notes:** Rewritten at authoring: the earlier stem named the product and so contained the answer.

### a15 — date_anchored / membership_count (international/EU)

- **Stem:** As of 1 January 2019, how many member states did the European Union have?
- **Route:** `numeric` · key fingerprint `58cb76d5e1ca1380`
- **Anchored state:** 28 · **displacing state:** 27
- **Temporal distance:** ~7 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** European Commission qanda_20_104 — UK withdrawal 2020-01-31 reduced the count to 27
- **Why it supports the key:** The count stood at 28 until the UK's withdrawal, which postdates the anchor.

### a16 — date_anchored / sports_record (sports/tennis)

- **Stem:** As of 1 January 2020, which male tennis player had won the most Grand Slam singles titles?
- **Route:** `exact_entity` · key fingerprint `987d72ac4e9bd0c3`
- **Anchored state:** Roger Federer · **displacing state:** Djokovic
- **Temporal distance:** ~6 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** ATP/ITF Grand Slam singles champion records; contemporaneous reporting Dec 2019 / Jan 2020
- **Why it supports the key:** Entering the 2020 Australian Open, Federer led with 20 majors, Nadal 19, Djokovic 16, so Federer held the record at the anchor.

### a17 — date_anchored / diplomatic_status (geopolitics)

- **Stem:** As of 1 January 2015, had the United States and Cuba reopened embassies in each other's capitals? Answer yes or no.
- **Route:** `boolean` · key fingerprint `0a8a56fc733acdc6`
- **Anchored state:** No · **displacing state:** Yes
- **Temporal distance:** ~11 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** US Department of State / Office of the Historian; embassies reopened 2015-07-20
- **Why it supports the key:** Embassies reopened 2015-07-20, after the 2015-01-01 anchor, so the answer at the anchor is No.

### a18 — date_anchored / official_name (geopolitics)

- **Stem:** As of 1 January 2018, what was the official name of the country whose capital is Skopje?
- **Route:** `exact_entity` · key fingerprint `e8cc3fb0019e2127`
- **Anchored state:** Republic of Macedonia · **displacing state:** North Macedonia
- **Temporal distance:** ~8 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** Prespa Agreement; UN Secretary-General statement 2019-02-13; CNN 2019-02-13
- **Why it supports the key:** The agreement entered into force 2019-02-12. At the 2018-01-01 anchor the official name was still the Republic of Macedonia.
- **Ambiguity notes:** Accept list deliberately excludes 'North Macedonia' as a substring risk; grader uses word boundaries.

### a19 — date_anchored / team_name (sports/NFL)

- **Stem:** As of 1 January 2021, what was the team name of the National Football League franchise based in the Washington, D.C. area?
- **Route:** `exact_entity` · key fingerprint `2c927e4f6c45e3ab`
- **Anchored state:** Washington Football Team · **displacing state:** Washington Commanders
- **Temporal distance:** ~5 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** NFL franchise naming record; interim name used July 2020 to February 2022
- **Why it supports the key:** The 2021-01-01 anchor falls inside the interim 'Washington Football Team' period, between the Redskins retirement and the Commanders rebrand.

### a20 — date_anchored / officeholder (corporate/retail)

- **Stem:** As of 1 June 2021, who was the Chief Executive Officer of Amazon.com, Inc.?
- **Route:** `exact_entity` · key fingerprint `030e8d0d894c7542`
- **Anchored state:** Jeff Bezos · **displacing state:** Andy Jassy
- **Temporal distance:** ~5 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** Wikipedia 'Andy Jassy'; MarketBeat 2021-07-05 handover report — Jassy became CEO 2021-07-05
- **Why it supports the key:** Bezos remained CEO until 2021-07-05, after the anchor date.

### a21 — date_anchored / officeholder (corporate/social)

- **Stem:** As of 1 January 2020, who was the Chief Executive Officer of Twitter, Inc.?
- **Route:** `exact_entity` · key fingerprint `0136ce9e85843bc8`
- **Anchored state:** Jack Dorsey · **displacing state:** a later CEO
- **Temporal distance:** ~6 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** Poynter; Washington Post 2021-11-29 — Dorsey stepped down 2021-11-29
- **Why it supports the key:** Dorsey was CEO across the anchor date and resigned nearly two years later.

### a22 — date_anchored / governing_party (politics/Poland)

- **Stem:** As of 1 January 2016, which political party led the government of Poland?
- **Route:** `exact_entity` · key fingerprint `0cecb761edbb5f25`
- **Anchored state:** Law and Justice · **displacing state:** a later governing party
- **Temporal distance:** ~10 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** Polish parliamentary record; Law and Justice government from November 2015 to December 2023
- **Why it supports the key:** The 2016-01-01 anchor falls inside the first PiS government formed after the October 2015 election.

### a23 — date_anchored / officeholder (politics/Scotland)

- **Stem:** As of 1 January 2021, who was the First Minister of Scotland?
- **Route:** `exact_entity` · key fingerprint `63a04511ad3d90f3`
- **Anchored state:** Nicola Sturgeon · **displacing state:** a later First Minister
- **Temporal distance:** ~5 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** Scottish Government record; Sturgeon First Minister 2014-11-20 to 2023-03-28
- **Why it supports the key:** The 2021-01-01 anchor falls inside Sturgeon's continuous tenure.

### a24 — date_anchored / currency_area (economics/Lithuania)

- **Stem:** As of 1 January 2014, was Lithuania using the euro as its official currency? Answer yes or no.
- **Route:** `boolean` · key fingerprint `0a8a56fc733acdc6`
- **Anchored state:** No · **displacing state:** Yes
- **Temporal distance:** ~12 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** Bank of Lithuania; European Commission 'Lithuania and the euro'; euro adopted 2015-01-01
- **Why it supports the key:** Lithuania adopted the euro 2015-01-01, one year after the 2014-01-01 anchor, so the answer at the anchor is No.

### a25 — date_anchored / programme_status (science/space)

- **Stem:** As of 1 January 2011, was the NASA Space Shuttle programme still conducting crewed flights? Answer yes or no.
- **Route:** `boolean` · key fingerprint `a76bdac6d0d3cd20`
- **Anchored state:** Yes · **displacing state:** No
- **Temporal distance:** ~15 years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** NASA STS-135 mission record; Atlantis landed 2011-07-21
- **Why it supports the key:** The final Shuttle flight landed 2011-07-21, after the 2011-01-01 anchor, so crewed Shuttle flights were still being conducted at the anchor.

### b01 — definition_anchored / reported_vs_excess (public health)

- **Stem:** According to the World Health Organization, approximately how many deaths were REPORTED as due to COVID-19 worldwide between 1 January 2020 and 31 December 2021? Give the figure in millions, counting only reported deaths, not excess-mortality estimates.
- **Route:** `numeric` · key fingerprint `3f1f73062bd91668`
- **Requested definition:** reported COVID-19 deaths, 2020-2021
- **Known alternative definition(s):** WHO excess-mortality estimate for the same window: 14.9 million (range 13.3-16.6)
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** who.int news item 2022-05-05; Nature s41586-022-05522-2
- **Why it supports the key:** WHO states 14.9M excess versus 5.42M reported as due to COVID-19 for 2020-2021.

### b02 — definition_anchored / fiscal_vs_calendar (corporate finance)

- **Stem:** What were Apple Inc.'s total net sales for its fiscal year 2023, the year ended 30 September 2023, as reported in its Form 10-K? Give the figure in billions of US dollars.
- **Route:** `numeric` · key fingerprint `16e514ef72494df2`
- **Requested definition:** fiscal year ended 2023-09-30
- **Known alternative definition(s):** calendar-year revenue, and the prior fiscal year's 394.3 billion
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** SEC Form 10-K aapl-20230930
- **Why it supports the key:** The 10-K reports total net sales of $383,285 million for FY2023.

### b03 — definition_anchored / survey_vintage (geography)

- **Stem:** What is the elevation of Mount Everest above sea level in metres according to the 2020 joint China-Nepal survey?
- **Route:** `numeric` · key fingerprint `03cad2bbe5fd12d6`
- **Requested definition:** 2020 joint survey figure
- **Known alternative definition(s):** the previously accepted 8,848 m
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** Kathmandu Post 2020-12-08; CNN travel
- **Why it supports the key:** Both sources give 8,848.86 m from the joint survey, superseding 8,848 m.
- **Ambiguity notes:** Tolerance 0.5 m keeps the accepted and rejected values disjoint.
- **Tolerance (audited):** Tightened at the post-verification audit from +/-0.5 m to +/-0.2 m. The 2020 survey figure and the pre-2020 figure differ by only 0.86 m, so the old band reached within 0.36 m of the value the item exists to reject: a solver answering 8,848.4 or 8,848.5 - plausible roundings of the DISPLACING figure - would have graded as correct. The stem is already survey-anchored, so the fix is the band, not the question. +/-0.2 m accepts the published 8,848.86 and its rounding to the metre, 8,849, and rejects 8,848 and every rounding of it. Found by generalising the b11 defect into a rule now enforced by the test suite: no accept band may reach halfway to the value it must reject.

### b04 — definition_anchored / annual_share (energy)

- **Stem:** According to RTE, what percentage of France's electricity generation came from nuclear power in calendar year 2022?
- **Route:** `numeric` · key fingerprint `4898acb9df7b6595`
- **Requested definition:** calendar year 2022, RTE balance
- **Known alternative definition(s):** France's more typical ~70% share in other years
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** RTE French Annual Electricity Review; Clean Air Task Force 2023
- **Why it supports the key:** RTE's 2022 balance gives 62.7%, about six points below 2021.

### b05 — definition_anchored / planet_definition (science/astronomy)

- **Stem:** Under the International Astronomical Union's 2006 definition of a planet, how many planets are there in the Solar System?
- **Route:** `numeric` · key fingerprint `6157a11c047a9ca4`
- **Requested definition:** IAU 2006 definition
- **Known alternative definition(s):** the pre-2006 count of nine
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-1 source verification during authoring
- **Source:** Library of Congress Everyday Mysteries; astronomy.com
- **Why it supports the key:** The 2006 definition yields eight planets, excluding Pluto.

### b06 — definition_anchored / administrative_scope (demography)

- **Stem:** What was the population of Greater London, the administrative region, at the 2021 United Kingdom census? Give the figure in millions.
- **Route:** `numeric` · key fingerprint `ffb207f6eb4aa61d`
- **Requested definition:** Greater London administrative area, 2021 census
- **Known alternative definition(s):** the wider London metropolitan area (~14M) and the City of London (~8,600 people)
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** Greater London Authority 2021 Census first release; ONS 2021 Census
- **Why it supports the key:** The 2021 Census counted 8,799,800 usual residents in Greater London, the administrative region.

### b07 — definition_anchored / measure_definition (labour economics)

- **Stem:** What was the United States unemployment rate for December 2023 on the U-3 measure, seasonally adjusted, as published by the Bureau of Labor Statistics? Give the percentage.
- **Route:** `numeric` · key fingerprint `ebeb1f1a1b18453a`
- **Requested definition:** U-3, seasonally adjusted
- **Known alternative definition(s):** the broader U-6 measure
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** BLS Employment Situation, December 2023 (USDL-24-0006); BLS TED 2024
- **Why it supports the key:** BLS reports the U-3 unemployment rate held at 3.7 percent in December 2023.

### b08 — definition_anchored / event_scope (sports)

- **Stem:** How many Olympic gold medals did Michael Phelps win in INDIVIDUAL events only, excluding relays?
- **Route:** `numeric` · key fingerprint `356b62780123d70c`
- **Requested definition:** individual events only
- **Known alternative definition(s):** his career total of 23 golds including relays
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** Olympics.com athlete record; Team USA profile
- **Why it supports the key:** Phelps won 23 Olympic golds in total, of which 13 were in individual events.

### b09 — definition_anchored / currency_union_scope (economics/EU)

- **Stem:** How many European Union member states had adopted the euro as their official currency as of 1 January 2024?
- **Route:** `numeric` · key fingerprint `babd9c14b5c679d4`
- **Requested definition:** EU member states inside the euro area
- **Known alternative definition(s):** the 27 EU member states overall, and the wider set of territories using the euro
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification; item replaced at verification
- **Source:** European Central Bank; Council of the EU (Consilium); Banque de France; Deutsche Bundesbank
- **Why it supports the key:** Croatia joined on 2023-01-01 as the twentieth euro-area member, and the euro area still had 20 members on 2024-01-01.
- **Ambiguity notes:** REPLACED at verification. The original item asked for India's 2023 nominal GDP per the IMF WEO. That value could not be confirmed against a primary source, and IMF GDP figures are revised between WEO vintages, which makes them a poor basis for a frozen key.
- **Classification (audited):** `definition_anchored` is correct and unambiguous under the class-assignment rule in the specification, §3. The operative constraint is scope - EU member states inside the euro area - and the primary displacing answer, 27, is a scope error. The date is a freezing device, not the tested mechanism: Bulgaria's 2026 euro accession means an undated stem would have a different answer today. Residual, named and not repaired: the secondary reject 19 is the pre-Croatia count and is a temporal displacement, a channel that cannot be removed from any dated euro-area item. It changes no grading outcome, since 19 already falls outside the ±0.4 accept band.

### b10 — definition_anchored / area_scope (geography)

- **Stem:** What is the TOTAL area of the United States including inland and coastal waters, in square kilometres, per the CIA World Factbook? Give the figure in millions.
- **Route:** `numeric` · key fingerprint `328bbdf37b033b82`
- **Requested definition:** total area including water
- **Known alternative definition(s):** land area only (~9.148 million km2)
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** CIA World Factbook, United States, Area field
- **Why it supports the key:** Total area 9,833,517 sq km; land area 9,147,593 sq km. The stem requests total area including water.

### b11 — definition_anchored / lake_definition (geography)

- **Stem:** How many Great Lakes are there if Lake Michigan and Lake Huron are counted as one lake, as they are hydrologically a single body connected at the Straits of Mackinac?
- **Route:** `numeric` · key fingerprint `b1c74ac5e1266d69`
- **Requested definition:** Michigan and Huron counted as one lake
- **Known alternative definition(s):** the conventional count of five, which lists them separately
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-3 post-verification audit; item replaced at audit
- **Source:** NOAA Great Lakes Environmental Research Laboratory and USGS descriptions of Michigan-Huron as one lake, joined at the Straits of Mackinac and at a common surface elevation
- **Why it supports the key:** Superior, Michigan-Huron, Erie and Ontario give four bodies under the requested definition; the conventional count of five separates Michigan from Huron.
- **Ambiguity notes:** REPLACED at the post-verification audit, and the reason is worth recording because it is a class of defect, not a one-off. The verification-pass item asked for the surface area of Lake Michigan alone and was keyed to NOAA's 57,573 km2 with a 1,500 km2 tolerance. That tolerance was load-bearing rather than incidental: published areas range across roughly 57,573-58,030 km2 (Wikipedia 57,757; World Atlas 58,030), so the stem did not uniquely determine the answer and the acceptance interval was repairing an ambiguity that belonged in the question. The obvious fix - source-anchoring the stem to NOAA, as b03, b18 and b20 anchor to a named survey - does not work here: the NOAA page states the area as "57,573 square kilometers or 22,300 square miles", and 22,300 sq mi is 57,757 km2, so the single cited source contradicts itself by 184 km2 for the same quantity. No tolerance both respects a named source and is tight enough to be meaningful. The replacement keeps the subtype, the domain and the same underlying Michigan-Huron definitional split, but asks for an exact integer that no measurement spread can move.

### b12 — definition_anchored / index_basis (macroeconomics)

- **Stem:** What was the United States CPI-U inflation rate for December 2022 measured over the twelve months to December 2022, per the Bureau of Labor Statistics? Give the percentage.
- **Route:** `numeric` · key fingerprint `6e2f7f52e433afbe`
- **Requested definition:** December-over-December
- **Known alternative definition(s):** the calendar-year average rate of 8.0%
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** BLS Consumer Price Index, December 2022 release (published 2023-01-12)
- **Why it supports the key:** The all-items index rose 6.5 percent for the twelve months ending December 2022.

### b13 — definition_anchored / fertility_measure (demography)

- **Stem:** What was Japan's total fertility rate in 2022 according to the Japanese Ministry of Health, Labour and Welfare?
- **Route:** `numeric` · key fingerprint `82e4db3298ecfa78`
- **Requested definition:** total fertility rate, 2022
- **Known alternative definition(s):** earlier years' higher rates, e.g. 1.34
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** Japan Ministry of Health, Labour and Welfare vital statistics for 2022
- **Why it supports the key:** MHLW reports a total fertility rate of 1.26 for 2022, a record low at that time.

### b14 — definition_anchored / deadline_scope (US constitutional history)

- **Stem:** How many US states had ratified the Equal Rights Amendment by the original ratification deadline of 22 March 1979?
- **Route:** `numeric` · key fingerprint `6754b70768d5a94c`
- **Requested definition:** by the original 1979 deadline
- **Known alternative definition(s):** the 38 total including later ratifications
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** National Archives 'Equal Rights Amendment'; congress.gov CRS R47619
- **Why it supports the key:** Thirty-five states had ratified by 1977 and none further before the original 1979 deadline; 38 were required.

### b15 — definition_anchored / membership_definition (international)

- **Stem:** How many member states does the United Nations have, counting full member states only and excluding permanent observer states?
- **Route:** `numeric` · key fingerprint `06aa70295807b214`
- **Requested definition:** full member states only
- **Known alternative definition(s):** the count of 195 including two permanent observers
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** Britannica 'Member states of the United Nations'; congress.gov CRS R48306
- **Why it supports the key:** The UN has 193 member states plus two permanent non-member observers (the Holy See and Palestine).

### b16 — definition_anchored / census_vs_estimate (demography)

- **Stem:** What was the population of Australia counted at the 2021 Census on Census night, per the Australian Bureau of Statistics? Give the figure in millions.
- **Route:** `numeric` · key fingerprint `477ae37024339b74`
- **Requested definition:** 2021 Census count
- **Known alternative definition(s):** later population estimates
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** Australian Bureau of Statistics, 2021 Census population release
- **Why it supports the key:** The 2021 Census counted 25,422,788 people in Australia on Census night.

### b17 — definition_anchored / height_definition (architecture)

- **Stem:** What is the height of the Empire State Building to its architectural top, in metres, EXCLUDING the broadcast antenna?
- **Route:** `numeric` · key fingerprint `85bbb1b043f4fdea`
- **Requested definition:** architectural top, antenna excluded
- **Known alternative definition(s):** height including the antenna, about 443 m
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** Empire State Building official facts page (esbnyc.com); Britannica
- **Why it supports the key:** The building reaches 381 m to its architectural top; 443.2 m is the height to the antenna tip.
- **Ambiguity notes:** Replaced at authoring: the Burj Khalifa variant had accepted and rejected values 1.8 m apart, too close for a numeric route.

### b18 — definition_anchored / wall_survey_scope (history/geography)

- **Stem:** What is the total length of the Great Wall of China in kilometres according to the 2012 survey by China's State Administration of Cultural Heritage, counting all dynasties?
- **Route:** `numeric` · key fingerprint `f76c5ad30a4ef8c1`
- **Requested definition:** all dynasties, 2012 survey
- **Known alternative definition(s):** the Ming-dynasty-only figure of about 8,850 km
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** China State Administration of Cultural Heritage 2012 survey
- **Why it supports the key:** The 2012 survey gives 21,196.18 km for all dynasties; the Ming-only Great Wall is 8,851.8 km.
- **Refinement (audited):** The verification pass sharpened the recorded Ming-only reject from 8,850 to 8,851.8 km. Confirmed to move no grading boundary: the accept band is 21,196 ± 500 = [20,696, 21,696], and both the old and the new value fall outside it identically. The change is documentary precision only.

### b19 — definition_anchored / language_count (international/EU)

- **Stem:** How many official languages does the European Union have?
- **Route:** `numeric` · key fingerprint `8eff7d1f1cc4d9f6`
- **Requested definition:** official languages
- **Known alternative definition(s):** the number of member states, 27
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** European Commission Directorate-General for Translation, linguistic diversity page
- **Why it supports the key:** The EU has 24 official languages, against 27 member states.

### b20 — definition_anchored / depth_survey (oceanography)

- **Stem:** What is the depth of Challenger Deep in metres according to the 2010 US Center for Coastal and Ocean Mapping sonar survey?
- **Route:** `numeric` · key fingerprint `a51741d26dd847a9`
- **Requested definition:** 2010 sonar survey
- **Known alternative definition(s):** other survey vintages
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** NASA NSSDCA planetary fact sheet notes; 2010 CCOM sonar survey record
- **Why it supports the key:** The 2010 survey places Challenger Deep at about 10,994 m, distinct from earlier survey vintages.

### b21 — definition_anchored / wage_scope (labour policy)

- **Stem:** What is the United States FEDERAL minimum wage in dollars per hour for covered non-exempt employees, ignoring higher state minimums?
- **Route:** `numeric` · key fingerprint `44c32954e08d74e8`
- **Requested definition:** federal minimum only
- **Known alternative definition(s):** higher state and city minimum wages
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** US Department of Labor; federal minimum wage $7.25 effective 2009-07-24
- **Why it supports the key:** The federal minimum has been $7.25/hour since 2009-07-24; state minimums are higher in many states.

### b22 — definition_anchored / anatomical_stage (biology)

- **Stem:** How many bones are in the skeleton of a typical ADULT human?
- **Route:** `numeric` · key fingerprint `a27fe3ff6f734971`
- **Requested definition:** adult skeleton
- **Known alternative definition(s):** the roughly 270 bones of a newborn
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** Cleveland Clinic 'Bones'; NCBI Physiology, Bone
- **Why it supports the key:** The adult human skeleton comprises 206 bones; a newborn has roughly 270 before fusion.

### b23 — definition_anchored / orbital_distance_definition (science/astronomy)

- **Stem:** What is the distance between the Earth and the Sun at PERIHELION, the closest point of Earth's orbit, in millions of kilometres?
- **Route:** `numeric` · key fingerprint `f6e30e4e93752fae`
- **Requested definition:** perihelion distance
- **Known alternative definition(s):** the mean distance / astronomical unit (149.6) and the aphelion distance (152.1)
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** NASA NSSDCA planetary fact sheet notes
- **Why it supports the key:** Perihelion is about 147,098,074 km (147.1 million); aphelion about 152,097,701 km; the mean is 149.6 million.
- **Ambiguity notes:** Replaced at authoring: the Earth-diameter variant had accepted and rejected values 14 km apart, too close for a numeric route.

### b24 — definition_anchored / distance_unit (sports)

- **Stem:** What is the official distance of a marathon in kilometres, as set by World Athletics?
- **Route:** `numeric` · key fingerprint `e1426f26d501d9b1`
- **Requested definition:** kilometres
- **Known alternative definition(s):** the same distance expressed as 26.2 miles
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification, independent of the authoring pass
- **Source:** World Athletics / IAAF standard, fixed 1921 and used from the 1924 Olympics
- **Why it supports the key:** The official marathon distance is 42.195 km, equivalently 26 miles 385 yards.

### b25 — definition_anchored / geographic_scope (geography/US)

- **Stem:** How many states of the United States border the Pacific Ocean, counting only the 48 contiguous states?
- **Route:** `numeric` · key fingerprint `fcba0f2a2a49ed56`
- **Requested definition:** contiguous 48 states only
- **Known alternative definition(s):** all 50 states, which gives 5 by including Alaska and Hawaii
- **Verification:** `VERIFIED_SOURCE_2026-08-30T00:00:00Z`
- **Verified at:** 2026-08-30T00:00:00Z · **pass:** pass-2 source verification; item replaced at verification
- **Source:** WorldAtlas 'Pacific States'; contiguous United States geography references
- **Why it supports the key:** California, Oregon and Washington give the contiguous 48 their Pacific coastline; Alaska and Hawaii add two more when all 50 states are counted.
- **Classification (audited):** `definition_anchored`, unambiguous. The operative constraint is geographic scope, the stem carries no date, and the displacing answer 5 is the all-50-states count. Source tier noted: WorldAtlas is a secondary aggregator, which was disqualifying for the IMF GDP items it replaced, but the disqualifying property there was revisability, not tier - which of the contiguous 48 states has Pacific coastline is not a revisable estimate and is verifiable from any map.
- **Ambiguity notes:** REPLACED at verification. The original item asked for the UK's 2023 nominal GDP per the IMF WEO. The best available figure (3.38 trillion) differed from the authored key (3.34) and came from a secondary aggregator, and IMF GDP figures are revised between vintages.

## Arithmetic control

All 15 keys are closed-form computations requiring no external lookup; each was
recomputed independently by the authoring script. No provenance record is needed
because no external source is involved.
