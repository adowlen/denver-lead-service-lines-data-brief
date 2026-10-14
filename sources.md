# Sources - every figure in the brief, named

Pulled October 14, 2026. No figure in the brief comes from anywhere
else, and the brief carries no figure that is not listed here.

## Primary data (machine-readable pulls, this package)

- **Denver Water Lead Service Line Inventory, snapshot LSLI_20260630**
  (Denver Open Data / ArcGIS service `LRP_Inventory_LCRR_DEMO`,
  FeatureServer layer 0, hosted at services.arcgis.com/czCXlxn6hYtK4vdg).
  Server-side count re-confirmed at pull: **311,491 premises**;
  snapshot date June 30, 2026; layer Published_Date field reads
  2026-07-08 for all rows. Archived in this package as
  `data/denver_water_lsli_raw_2026-06-30.csv`; pull code in
  `code/download.py`.
  - Category counts (the file's own strings in `lsli_final_lead_cat`):
    confirmed 11,400; unknown-likely 10,026; unknown-unlikely 14,667;
    non-lead 275,398. The confirmed category's own description
    (`Category_Desc`) states it includes galvanized steel that is or
    ever was downstream of a lead line or currently downstream of an
    unknown line - EPA's galvanized requiring replacement definition.
  - City scope (`PREM_CITY` = DENVER): 187,289 premises; confirmed
    10,822; likely 7,953; unlikely 13,711; non-lead 154,803; pool
    18,775 (10.02 percent).
  - Neighborhood, council district, ZIP and parcel-year-built figures:
    group counts from the same file, computed in `code/analyze.py`,
    stored in `data/stats.json`, independently recomputed in
    `code/verify.py` (57 figures, all reproduced).
  - Wheat Ridge: 7,941 premises; pool 2,182 (296 confirmed, 1,886
    likely). Littleton: 48,217 premises, 97 pool. Lakewood: 28,780 /
    147. Englewood: 7,492 / 114. Edgewater: 1,405 / 105.
- **Denver Water Lead Service Line Replacements layer**
  (`Lead_Service_Line_Replacements`, FeatureServer layer 6, same
  ArcGIS organization). **24,748 records**; 24,746 with a parseable
  replacement date; dated records run January 1, 2020 to **May 2,
  2024** (the layer holds no later dated records). By year: 2020,
  5,533; 2021, 4,848; 2022, 5,150; 2023, 6,906; 2024 (Jan 1 to May 2),
  2,309. Full-year average 2020-2023: 5,609. By project tag: ALSLR
  PROGRAM 17,387; ALSLR PROGRAM (DW) 335; WATER MAIN REPLACEMENT
  3,038; EMERGENCY REPAIRS 1,668; THIRD PARTY 1,303. Records marked
  FULL REPLACEMENT: 22,536. Archived as
  `data/denver_water_lsl_replacements_raw.csv`.
  - Join check: 23,949 of the layer's premise IDs appear in the June
    30, 2026 inventory; 23,942 of those premises are now classified
    non-lead; 7 carry a lead-family category (5 likely, 1 unlikely,
    1 confirmed).

## Mandate and program facts (official pages only, fetched live)

- **EPA, Lead and Copper Rule Improvements - Frequently Asked
  Questions for States and Public Water Systems** (epa.gov, PDF,
  October 2024). Baseline service line inventory due **November 1,
  2027**. Mandatory full replacement of all lead and galvanized
  requiring replacement (GRR) service lines under the system's
  control; national minimum replacement rate of at least 10 percent,
  assessed as a cumulative average, equating to a **10-year
  replacement deadline**; states must require an earlier deadline
  where feasible. All unknown-material lines must be **identified by
  the replacement deadline**. GRR defined as galvanized line that is
  or ever was downstream of a lead line, or is currently downstream
  of a lead status unknown line. Lead action level 0.010 mg/L (10
  ppb) from November 1, 2027.
- **Colorado Department of Public Health and Environment, Lead and
  Copper Rule page** (cdphe.colorado.gov/lcr, read October 14,
  2026): LCRI finalized October 30, 2024 and takes effect November 1,
  2027; Colorado systems must replace lead and GRR lines **by the end
  of 2037**; action level lowered from 15 ppb to 10 ppb.
- **Denver Water, "Denver Water ready for new federal rules on lead"**
  (denverwater.org, TAP article, read in full October 14, 2026):
  Lead Reduction Program launched 2020; **more than 26,000
  customer-owned lead service lines replaced as of July 1** (article
  context 2024); Denver Water **expects to finish replacing all lead
  service lines before 2035**; total lead lines now estimated at
  **60,000 to 64,000**, revised down from an initial estimate of
  64,000 to 84,000; about 312,000 service lines system-wide;
  replacements at no direct cost to customers; replacements coincide
  with planned water main and street projects; about $76 million in
  federal infrastructure funding received at the end of 2022; the
  public inventory categories were streamlined from four to three in
  the October 2024 federal rule transition, moving about 17,000
  properties formerly shown as unlikely-lead into the Unknown
  category on the public map.
- **Denver Water, "Top 10 things to know about Denver Water's Lead
  Reduction Program"** (denverwater.org, read in full October 14,
  2026): program replaces up to 64,000 customer-owned lead service
  lines **by 2035** at no direct cost to the customer; **homes built
  before 1951 are more likely to have a lead service line**; the
  water Denver Water delivers is lead-free; filters provided to
  program customers.

## Income layer (one added dataset - see verification.md for the
layering admission test)

- **Census Bureau, American Community Survey 2024 5-year estimates,
  table B19013 (median household income)**, ZCTA level, from the
  official table-based summary file `acsdt5y2024-b19013.dat`
  (www2.census.gov). The Census API redirected keyless queries, so the
  official summary file was used directly, as in the October 14
  Nashville package. Match: 47 of the 62 five-digit ZIP strings in
  the city scope, covering 187,253 of 187,289 city premises. Across
  the 32 ZIP codes with at least 100 inventoried premises, the
  correlation between pool share of premises and median household
  income is +0.30; for confirmed share alone, +0.40. Pool-weighted
  median ZCTA income $110,615; premises-weighted $100,977. Computed
  in `code/layer_income.py`; results in `layer_income_results.json`.

## What is NOT a source for anything in the brief

- Denver Water's public-facing map and dashboard pages were used only
  to locate the underlying ArcGIS layers and to confirm the category
  wording; every count comes from the layers themselves.
- Secondary coverage (trade press, neighborhood association pages)
  was read for orientation and is not cited for any figure.
- No figure is carried over from the lead as originally banked
  (311,491 premises was re-derived from the live layer before use).
