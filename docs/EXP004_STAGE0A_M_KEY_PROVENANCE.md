# Stage 0A-M key-construction provenance

**KEY-CONSTRUCTION EVIDENCE.** Public sources consulted to establish keys before any
dispatch. This is not EXPERIMENTAL RETRIEVAL EVIDENCE, which does not yet exist: no
production item has been shown to any solver, in either arm.

Only the minimum needed to support each key is recorded; no source passages are reproduced.

### a01 — date_anchored / officeholder (politics/Germany)

- **Stem:** As of 1 March 2021, who was the Chancellor of Germany?
- **Route:** `exact_entity` · key fingerprint `94e3f06e33f514e9`
- **Anchored state:** Angela Merkel · **displacing state:** a later chancellor
- **Temporal distance:** ~5 years
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** PBS NewsHour; Britannica 'Angela Merkel: Chancellorship' — Scholz sworn in 2021-12-08
- **Why it supports the key:** Merkel held office continuously until 2021-12-08, after the anchor date.

### a02 — date_anchored / officeholder (politics/UK)

- **Stem:** As of 1 June 2022, who was the Prime Minister of the United Kingdom?
- **Route:** `exact_entity` · key fingerprint `acc16650d202ec1f`
- **Anchored state:** Boris Johnson · **displacing state:** a later PM
- **Temporal distance:** ~4 years
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** Wikipedia 'Boris Johnson'; Britannica — premiership 2019-07-24 to 2022-09-06
- **Why it supports the key:** The anchor date falls inside Johnson's continuous premiership.

### a03 — date_anchored / entity_name (corporate/social)

- **Stem:** As of 1 January 2021, what was the registered corporate name of the company that owned and operated both Instagram and WhatsApp?
- **Route:** `exact_entity` · key fingerprint `62cf353120fa7af8`
- **Anchored state:** Facebook, Inc. · **displacing state:** Meta Platforms, Inc.
- **Temporal distance:** ~5 years
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** SEC Form 8-K fb-20211028 — bylaws amended 2021-10-28 for the name change
- **Why it supports the key:** The rename took legal effect 2021-10-28, after the anchor date.
- **Ambiguity notes:** Rewritten at authoring: the earlier stem named the social network and so contained the answer.

### a04 — date_anchored / entity_name (technology)

- **Stem:** As of 1 January 2023, what was the name of the microblogging platform whose logo was a blue bird?
- **Route:** `exact_entity` · key fingerprint `41e52ca42a2dc39f`
- **Anchored state:** Twitter · **displacing state:** X
- **Temporal distance:** ~3 years
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** Wikipedia 'X (social network)'; Britannica 'Twitter' — rebrand 2023-07-23
- **Why it supports the key:** The rebrand to X occurred 2023-07-23, after the anchor date.
- **Ambiguity notes:** Rewritten at authoring: the earlier stem cited the domain name and so contained the answer.

### a05 — date_anchored / membership_status (international/NATO)

- **Stem:** As of 1 January 2022, was Finland a member of NATO? Answer yes or no.
- **Route:** `boolean` · key fingerprint `0a8a56fc733acdc6`
- **Anchored state:** No · **displacing state:** Yes
- **Temporal distance:** ~4 years
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** nato.int news_213448 — Finland joined as 31st Ally 2023-04-04
- **Why it supports the key:** Accession followed the anchor date by fifteen months.

### a06 — date_anchored / membership_status (international/NATO)

- **Stem:** As of 1 January 2023, was Sweden a member of NATO? Answer yes or no.
- **Route:** `boolean` · key fingerprint `0a8a56fc733acdc6`
- **Anchored state:** No · **displacing state:** Yes
- **Temporal distance:** ~3 years
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** UK House of Commons Library CBP-9574 — Sweden joined 2024-03-07
- **Why it supports the key:** Accession followed the anchor date by fourteen months.

### a07 — date_anchored / currency (economics/Croatia)

- **Stem:** As of 1 June 2022, what was the official currency of Croatia?
- **Route:** `exact_entity` · key fingerprint `49d452fefdd29973`
- **Anchored state:** Croatian kuna · **displacing state:** euro
- **Temporal distance:** ~4 years
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** Croatian National Bank (hnb.hr); ECB euro changeover page — euro adopted 2023-01-01
- **Why it supports the key:** The kuna was sole legal tender until the 2023-01-01 changeover.

### a08 — date_anchored / canonical_count (science/astronomy)

- **Stem:** As of 1 January 2006, how many planets did the International Astronomical Union recognise in the Solar System?
- **Route:** `numeric` · key fingerprint `858c4fb30396f6b5`
- **Anchored state:** 9 · **displacing state:** 8
- **Temporal distance:** ~20 years
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** Library of Congress Everyday Mysteries; astronomy.com — IAU vote 2006-08-24
- **Why it supports the key:** Nine were recognised until the reclassification vote of 2006-08-24.

### a09 — date_anchored / org_status (international/EU)

- **Stem:** As of 1 January 2020, was the United Kingdom a member state of the European Union? Answer yes or no.
- **Route:** `boolean` · key fingerprint `a76bdac6d0d3cd20`
- **Anchored state:** Yes · **displacing state:** No
- **Temporal distance:** ~6 years
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** European Commission qanda_20_104; EMA — withdrawal effective 2020-01-31
- **Why it supports the key:** The UK remained a member state until 2020-01-31, one month after the anchor date.

### a10 — date_anchored / officeholder (international/UN)

- **Stem:** As of 1 January 2016, who was the Secretary-General of the United Nations?
- **Route:** `exact_entity` · key fingerprint `f3e14211791ba26c`
- **Anchored state:** Ban Ki-moon · **displacing state:** António Guterres
- **Temporal distance:** ~10 years
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** un.org 'Ban Ki-moon, Former Secretary-General'; UN Photo — term 2007-01-01 to 2016-12-31
- **Why it supports the key:** The anchor date falls inside Ban Ki-moon's second term.

### a11 — date_anchored / officeholder (international/EU)

- **Stem:** As of 1 June 2019, who was the President of the European Commission?
- **Route:** `exact_entity` · key fingerprint `6d6b45b2897aecea`
- **Anchored state:** Jean-Claude Juncker · **displacing state:** Ursula von der Leyen
- **Temporal distance:** ~7 years
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING — verify against ec.europa.eu commission archive
- **Why it supports the key:** Juncker's term is understood to have run to 2019-11-30.

### a12 — date_anchored / sovereignty_status (geopolitics)

- **Stem:** As of 1 January 2011, was South Sudan an independent sovereign state? Answer yes or no.
- **Route:** `boolean` · key fingerprint `0a8a56fc733acdc6`
- **Anchored state:** No · **displacing state:** Yes
- **Temporal distance:** ~15 years
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING — verify against un.org member states admission record
- **Why it supports the key:** Independence is understood to date from 2011-07-09.

### a13 — date_anchored / officeholder (politics/Brazil)

- **Stem:** As of 1 June 2020, who was the President of Brazil?
- **Route:** `exact_entity` · key fingerprint `236d31ba973f8962`
- **Anchored state:** Jair Bolsonaro · **displacing state:** Lula da Silva
- **Temporal distance:** ~6 years
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING — verify against gov.br presidential record
- **Why it supports the key:** Bolsonaro is understood to have served 2019-01-01 to 2022-12-31.

### a14 — date_anchored / corporate_structure (corporate/technology)

- **Stem:** As of 1 June 2015, what was the name of the publicly listed company whose principal product was the world's most used web search engine?
- **Route:** `exact_entity` · key fingerprint `bd3aa6c9697ca94b`
- **Anchored state:** Google Inc. · **displacing state:** Alphabet Inc.
- **Temporal distance:** ~11 years
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING — verify against the SEC filing for the Alphabet reorganisation
- **Why it supports the key:** The Alphabet holding structure is understood to have completed 2015-10-02.
- **Ambiguity notes:** Rewritten at authoring: the earlier stem named the product and so contained the answer.

### a15 — date_anchored / membership_count (international/EU)

- **Stem:** As of 1 January 2019, how many member states did the European Union have?
- **Route:** `numeric` · key fingerprint `58cb76d5e1ca1380`
- **Anchored state:** 28 · **displacing state:** 27
- **Temporal distance:** ~7 years
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** European Commission qanda_20_104 — UK withdrawal 2020-01-31 reduced the count to 27
- **Why it supports the key:** The count stood at 28 until the UK's withdrawal, which postdates the anchor.

### a16 — date_anchored / sports_record (sports/tennis)

- **Stem:** As of 1 January 2020, which male tennis player had won the most Grand Slam singles titles?
- **Route:** `exact_entity` · key fingerprint `987d72ac4e9bd0c3`
- **Anchored state:** Roger Federer · **displacing state:** Djokovic
- **Temporal distance:** ~6 years
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING — verify against ATP/ITF record tables
- **Why it supports the key:** Federer is understood to have led with 20 at the anchor date.

### a17 — date_anchored / diplomatic_status (geopolitics)

- **Stem:** As of 1 January 2015, had the United States and Cuba reopened embassies in each other's capitals? Answer yes or no.
- **Route:** `boolean` · key fingerprint `0a8a56fc733acdc6`
- **Anchored state:** No · **displacing state:** Yes
- **Temporal distance:** ~11 years
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING — verify against state.gov
- **Why it supports the key:** Embassies are understood to have reopened 2015-07-20.

### a18 — date_anchored / official_name (geopolitics)

- **Stem:** As of 1 January 2018, what was the official name of the country whose capital is Skopje?
- **Route:** `exact_entity` · key fingerprint `e8cc3fb0019e2127`
- **Anchored state:** Republic of Macedonia · **displacing state:** North Macedonia
- **Temporal distance:** ~8 years
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING — verify against the Prespa Agreement entry into force
- **Why it supports the key:** The renaming is understood to have taken effect in February 2019.
- **Ambiguity notes:** Accept list deliberately excludes 'North Macedonia' as a substring risk; grader uses word boundaries.

### a19 — date_anchored / team_name (sports/NFL)

- **Stem:** As of 1 January 2021, what was the team name of the National Football League franchise based in the Washington, D.C. area?
- **Route:** `exact_entity` · key fingerprint `2c927e4f6c45e3ab`
- **Anchored state:** Washington Football Team · **displacing state:** Washington Commanders
- **Temporal distance:** ~5 years
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING — verify against an NFL franchise record
- **Why it supports the key:** The interim name is understood to have run July 2020 to February 2022.

### a20 — date_anchored / officeholder (corporate/retail)

- **Stem:** As of 1 June 2021, who was the Chief Executive Officer of Amazon.com, Inc.?
- **Route:** `exact_entity` · key fingerprint `030e8d0d894c7542`
- **Anchored state:** Jeff Bezos · **displacing state:** Andy Jassy
- **Temporal distance:** ~5 years
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** Wikipedia 'Andy Jassy'; MarketBeat 2021-07-05 handover report — Jassy became CEO 2021-07-05
- **Why it supports the key:** Bezos remained CEO until 2021-07-05, after the anchor date.

### a21 — date_anchored / officeholder (corporate/social)

- **Stem:** As of 1 January 2020, who was the Chief Executive Officer of Twitter, Inc.?
- **Route:** `exact_entity` · key fingerprint `0136ce9e85843bc8`
- **Anchored state:** Jack Dorsey · **displacing state:** a later CEO
- **Temporal distance:** ~6 years
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** Poynter; Washington Post 2021-11-29 — Dorsey stepped down 2021-11-29
- **Why it supports the key:** Dorsey was CEO across the anchor date and resigned nearly two years later.

### a22 — date_anchored / governing_party (politics/Poland)

- **Stem:** As of 1 January 2016, which political party led the government of Poland?
- **Route:** `exact_entity` · key fingerprint `0cecb761edbb5f25`
- **Anchored state:** Law and Justice · **displacing state:** a later governing party
- **Temporal distance:** ~10 years
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING — verify against a Polish government or Sejm source
- **Why it supports the key:** Law and Justice is understood to have governed from November 2015 to December 2023.

### a23 — date_anchored / officeholder (politics/Scotland)

- **Stem:** As of 1 January 2021, who was the First Minister of Scotland?
- **Route:** `exact_entity` · key fingerprint `63a04511ad3d90f3`
- **Anchored state:** Nicola Sturgeon · **displacing state:** a later First Minister
- **Temporal distance:** ~5 years
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING — verify against gov.scot
- **Why it supports the key:** Sturgeon is understood to have served 2014-11-20 to 2023-03-28.

### a24 — date_anchored / currency_area (economics/Lithuania)

- **Stem:** As of 1 January 2014, was Lithuania using the euro as its official currency? Answer yes or no.
- **Route:** `boolean` · key fingerprint `0a8a56fc733acdc6`
- **Anchored state:** No · **displacing state:** Yes
- **Temporal distance:** ~12 years
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING — verify against ecb.europa.eu changeover pages
- **Why it supports the key:** Lithuania is understood to have adopted the euro on 2015-01-01.

### a25 — date_anchored / programme_status (science/space)

- **Stem:** As of 1 January 2011, was the NASA Space Shuttle programme still conducting crewed flights? Answer yes or no.
- **Route:** `boolean` · key fingerprint `a76bdac6d0d3cd20`
- **Anchored state:** Yes · **displacing state:** No
- **Temporal distance:** ~15 years
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING — verify against nasa.gov STS-135 record
- **Why it supports the key:** The final Shuttle mission is understood to have landed 2011-07-21, after the anchor date.

### b01 — definition_anchored / reported_vs_excess (public health)

- **Stem:** According to the World Health Organization, approximately how many deaths were REPORTED as due to COVID-19 worldwide between 1 January 2020 and 31 December 2021? Give the figure in millions, counting only reported deaths, not excess-mortality estimates.
- **Route:** `numeric` · key fingerprint `3f1f73062bd91668`
- **Requested definition:** reported COVID-19 deaths, 2020-2021
- **Known alternative definition(s):** WHO excess-mortality estimate for the same window: 14.9 million (range 13.3-16.6)
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** who.int news item 2022-05-05; Nature s41586-022-05522-2
- **Why it supports the key:** WHO states 14.9M excess versus 5.42M reported as due to COVID-19 for 2020-2021.

### b02 — definition_anchored / fiscal_vs_calendar (corporate finance)

- **Stem:** What were Apple Inc.'s total net sales for its fiscal year 2023, the year ended 30 September 2023, as reported in its Form 10-K? Give the figure in billions of US dollars.
- **Route:** `numeric` · key fingerprint `16e514ef72494df2`
- **Requested definition:** fiscal year ended 2023-09-30
- **Known alternative definition(s):** calendar-year revenue, and the prior fiscal year's 394.3 billion
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** SEC Form 10-K aapl-20230930
- **Why it supports the key:** The 10-K reports total net sales of $383,285 million for FY2023.

### b03 — definition_anchored / survey_vintage (geography)

- **Stem:** What is the elevation of Mount Everest above sea level in metres according to the 2020 joint China-Nepal survey?
- **Route:** `numeric` · key fingerprint `b18c88a43c33b7c9`
- **Requested definition:** 2020 joint survey figure
- **Known alternative definition(s):** the previously accepted 8,848 m
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** Kathmandu Post 2020-12-08; CNN travel
- **Why it supports the key:** Both sources give 8,848.86 m from the joint survey, superseding 8,848 m.
- **Ambiguity notes:** Tolerance 0.5 m keeps the accepted and rejected values disjoint.

### b04 — definition_anchored / annual_share (energy)

- **Stem:** According to RTE, what percentage of France's electricity generation came from nuclear power in calendar year 2022?
- **Route:** `numeric` · key fingerprint `4898acb9df7b6595`
- **Requested definition:** calendar year 2022, RTE balance
- **Known alternative definition(s):** France's more typical ~70% share in other years
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** RTE French Annual Electricity Review; Clean Air Task Force 2023
- **Why it supports the key:** RTE's 2022 balance gives 62.7%, about six points below 2021.

### b05 — definition_anchored / planet_definition (science/astronomy)

- **Stem:** Under the International Astronomical Union's 2006 definition of a planet, how many planets are there in the Solar System?
- **Route:** `numeric` · key fingerprint `6157a11c047a9ca4`
- **Requested definition:** IAU 2006 definition
- **Known alternative definition(s):** the pre-2006 count of nine
- **Verification:** `VERIFIED_WEB_2026-08-30`
- **Source:** Library of Congress Everyday Mysteries; astronomy.com
- **Why it supports the key:** The 2006 definition yields eight planets, excluding Pluto.

### b06 — definition_anchored / administrative_scope (demography)

- **Stem:** What was the population of Greater London, the administrative region, at the 2021 United Kingdom census? Give the figure in millions.
- **Route:** `numeric` · key fingerprint `ffb207f6eb4aa61d`
- **Requested definition:** Greater London administrative area, 2021 census
- **Known alternative definition(s):** the wider London metropolitan area (~14M) and the City of London (~8,600 people)
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against ons.gov.uk 2021 census tables
- **Why it supports the key:** 

### b07 — definition_anchored / measure_definition (labour economics)

- **Stem:** What was the United States unemployment rate for December 2023 on the U-3 measure, seasonally adjusted, as published by the Bureau of Labor Statistics? Give the percentage.
- **Route:** `numeric` · key fingerprint `ebeb1f1a1b18453a`
- **Requested definition:** U-3, seasonally adjusted
- **Known alternative definition(s):** the broader U-6 measure
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against bls.gov Employment Situation, January 2024 release
- **Why it supports the key:** 

### b08 — definition_anchored / event_scope (sports)

- **Stem:** How many Olympic gold medals did Michael Phelps win in INDIVIDUAL events only, excluding relays?
- **Route:** `numeric` · key fingerprint `356b62780123d70c`
- **Requested definition:** individual events only
- **Known alternative definition(s):** his career total of 23 golds including relays
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against olympics.com athlete record
- **Why it supports the key:** 

### b09 — definition_anchored / nominal_vs_ppp (macroeconomics)

- **Stem:** What was India's nominal gross domestic product in calendar year 2023 in current US dollars, per the IMF World Economic Outlook? Give the figure in trillions.
- **Route:** `numeric` · key fingerprint `db9dc63238932105`
- **Requested definition:** nominal, current US dollars
- **Known alternative definition(s):** GDP measured at purchasing power parity (~14.6 trillion)
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against imf.org WEO database
- **Why it supports the key:** 

### b10 — definition_anchored / area_scope (geography)

- **Stem:** What is the TOTAL area of the United States including inland and coastal waters, in square kilometres, per the CIA World Factbook? Give the figure in millions.
- **Route:** `numeric` · key fingerprint `328bbdf37b033b82`
- **Requested definition:** total area including water
- **Known alternative definition(s):** land area only (~9.148 million km2)
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against cia.gov World Factbook
- **Why it supports the key:** 

### b11 — definition_anchored / lake_definition (geography)

- **Stem:** What is the surface area of Lake Michigan alone, excluding Lake Huron, in square kilometres?
- **Route:** `numeric` · key fingerprint `70dd2217522b0efc`
- **Requested definition:** Lake Michigan alone
- **Known alternative definition(s):** the combined Michigan-Huron body (~117,400 km2)
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against NOAA Great Lakes fact sheet
- **Why it supports the key:** 

### b12 — definition_anchored / index_basis (macroeconomics)

- **Stem:** What was the United States CPI-U inflation rate for December 2022 measured over the twelve months to December 2022, per the Bureau of Labor Statistics? Give the percentage.
- **Route:** `numeric` · key fingerprint `6e2f7f52e433afbe`
- **Requested definition:** December-over-December
- **Known alternative definition(s):** the calendar-year average rate of 8.0%
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against bls.gov CPI release
- **Why it supports the key:** 

### b13 — definition_anchored / fertility_measure (demography)

- **Stem:** What was Japan's total fertility rate in 2022 according to the Japanese Ministry of Health, Labour and Welfare?
- **Route:** `numeric` · key fingerprint `82e4db3298ecfa78`
- **Requested definition:** total fertility rate, 2022
- **Known alternative definition(s):** earlier years' higher rates, e.g. 1.34
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against mhlw.go.jp vital statistics
- **Why it supports the key:** 

### b14 — definition_anchored / deadline_scope (US constitutional history)

- **Stem:** How many US states had ratified the Equal Rights Amendment by the original ratification deadline of 22 March 1979?
- **Route:** `numeric` · key fingerprint `6754b70768d5a94c`
- **Requested definition:** by the original 1979 deadline
- **Known alternative definition(s):** the 38 total including later ratifications
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against congress.gov or archives.gov
- **Why it supports the key:** 

### b15 — definition_anchored / membership_definition (international)

- **Stem:** How many member states does the United Nations have, counting full member states only and excluding permanent observer states?
- **Route:** `numeric` · key fingerprint `06aa70295807b214`
- **Requested definition:** full member states only
- **Known alternative definition(s):** the count of 195 including two permanent observers
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against un.org member states page
- **Why it supports the key:** 

### b16 — definition_anchored / census_vs_estimate (demography)

- **Stem:** What was the population of Australia counted at the 2021 Census on Census night, per the Australian Bureau of Statistics? Give the figure in millions.
- **Route:** `numeric` · key fingerprint `477ae37024339b74`
- **Requested definition:** 2021 Census count
- **Known alternative definition(s):** later population estimates
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against abs.gov.au 2021 Census
- **Why it supports the key:** 

### b17 — definition_anchored / height_definition (architecture)

- **Stem:** What is the height of the Empire State Building to its architectural top, in metres, EXCLUDING the broadcast antenna?
- **Route:** `numeric` · key fingerprint `85bbb1b043f4fdea`
- **Requested definition:** architectural top, antenna excluded
- **Known alternative definition(s):** height including the antenna, about 443 m
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against ctbuh.org
- **Why it supports the key:** 
- **Ambiguity notes:** Replaced at authoring: the Burj Khalifa variant had accepted and rejected values 1.8 m apart, too close for a numeric route.

### b18 — definition_anchored / wall_survey_scope (history/geography)

- **Stem:** What is the total length of the Great Wall of China in kilometres according to the 2012 survey by China's State Administration of Cultural Heritage, counting all dynasties?
- **Route:** `numeric` · key fingerprint `c2f264c5cab42858`
- **Requested definition:** all dynasties, 2012 survey
- **Known alternative definition(s):** the Ming-dynasty-only figure of about 8,850 km
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against the 2012 SACH survey report
- **Why it supports the key:** 

### b19 — definition_anchored / language_count (international/EU)

- **Stem:** How many official languages does the European Union have?
- **Route:** `numeric` · key fingerprint `8eff7d1f1cc4d9f6`
- **Requested definition:** official languages
- **Known alternative definition(s):** the number of member states, 27
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against europa.eu
- **Why it supports the key:** 

### b20 — definition_anchored / depth_survey (oceanography)

- **Stem:** What is the depth of Challenger Deep in metres according to the 2010 US Center for Coastal and Ocean Mapping sonar survey?
- **Route:** `numeric` · key fingerprint `a51741d26dd847a9`
- **Requested definition:** 2010 sonar survey
- **Known alternative definition(s):** other survey vintages
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against the CCOM/NOAA survey record
- **Why it supports the key:** 

### b21 — definition_anchored / wage_scope (labour policy)

- **Stem:** What is the United States FEDERAL minimum wage in dollars per hour for covered non-exempt employees, ignoring higher state minimums?
- **Route:** `numeric` · key fingerprint `44c32954e08d74e8`
- **Requested definition:** federal minimum only
- **Known alternative definition(s):** higher state and city minimum wages
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against dol.gov
- **Why it supports the key:** 

### b22 — definition_anchored / anatomical_stage (biology)

- **Stem:** How many bones are in the skeleton of a typical ADULT human?
- **Route:** `numeric` · key fingerprint `a27fe3ff6f734971`
- **Requested definition:** adult skeleton
- **Known alternative definition(s):** the roughly 270 bones of a newborn
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against a standard anatomical reference
- **Why it supports the key:** 

### b23 — definition_anchored / orbital_distance_definition (science/astronomy)

- **Stem:** What is the distance between the Earth and the Sun at PERIHELION, the closest point of Earth's orbit, in millions of kilometres?
- **Route:** `numeric` · key fingerprint `f6e30e4e93752fae`
- **Requested definition:** perihelion distance
- **Known alternative definition(s):** the mean distance / astronomical unit (149.6) and the aphelion distance (152.1)
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against a NASA planetary fact sheet
- **Why it supports the key:** 
- **Ambiguity notes:** Replaced at authoring: the Earth-diameter variant had accepted and rejected values 14 km apart, too close for a numeric route.

### b24 — definition_anchored / distance_unit (sports)

- **Stem:** What is the official distance of a marathon in kilometres, as set by World Athletics?
- **Route:** `numeric` · key fingerprint `e1426f26d501d9b1`
- **Requested definition:** kilometres
- **Known alternative definition(s):** the same distance expressed as 26.2 miles
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against worldathletics.org
- **Why it supports the key:** Unit-anchored rather than definition-conflicted; retained for unit-scope diversity.

### b25 — definition_anchored / gdp_year_basis (macroeconomics)

- **Stem:** What was the nominal gross domestic product of the United Kingdom in calendar year 2023 in current US dollars, per the IMF World Economic Outlook? Give the figure in trillions.
- **Route:** `numeric` · key fingerprint `afe8477548d944af`
- **Requested definition:** nominal, current US dollars, 2023
- **Known alternative definition(s):** PPP-based and other-year figures
- **Verification:** `PENDING_INDEPENDENT_VERIFICATION`
- **Source:** PENDING - verify against imf.org WEO database
- **Why it supports the key:** 

## Arithmetic control

All 15 keys are closed-form computations requiring no external lookup; each was
recomputed independently by the authoring script. No provenance record is needed
because no external source is involved.
