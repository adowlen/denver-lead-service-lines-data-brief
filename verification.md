# Verification

Analysis code: `code/analyze.py` (pandas). Independent verification:
`code/verify.py`, a separate pass over the raw downloads using only
the stdlib csv module, written separately from the analysis code,
with its own grouping logic. Layer code: `code/layer_income.py`,
verified inside `verification_results.json` reporting
(ledger: `verification_results.json` at package root).

## Methods checklist (brief-writing standards, section 3)

**Base rates and exposure.** Every count in the brief is paired with
its denominator: neighborhood counts with the neighborhood's total
premises, pool shares with citywide and service-area shares, ZIP
figures with ZIP premises, district figures with district premises.
The two scopes (service area 311,491 premises; City and County of
Denver 187,289) are defined in the brief and never mixed inside a
single figure. Where a raw count would mislead (Wheat Ridge's pool is
large because its housing is old, and most of it is unconfirmed), the
composition is stated next to the count.

**Causality direction.** The brief makes no causal claims. The
year-built finding is stated as co-occurrence ("the pool follows the
year the house was built") and is paired with Denver Water's own
published guidance that pre-1951 homes are more likely to have lead
lines; no direction of causation beyond the file's co-occurrence is
asserted. The pace section compares a recorded average to required
arithmetic averages and states both as arithmetic, not as a forecast.

**Category or definition changes inside the window.** Material, and
disclosed in the brief. In October 2024, when the federal rule took
effect, Denver Water streamlined its public inventory display from
four categories to three and moved about 17,000 properties formerly
shown as unlikely-lead into the Unknown category (Denver Water's own
article, fetched live). This brief uses the inventory file's own four
category strings from the June 30, 2026 snapshot, not the public map's
three display categories; counts here are therefore not comparable to
counts published under earlier groupings, and the brief says so. The
confirmed category follows the file's own Category_Desc, which folds
galvanized-requiring-replacement lines into confirmed; that matches
the EPA definition of the replacement obligation. No trend claim is
made across the definition change.

**Time windows.** The inventory is a single snapshot dated June 30,
2026 (layer published July 8, 2026). The replacements layer's dated
records run January 1, 2020 to May 2, 2024, about 26 months before
the snapshot. The brief's data window line states both ends. No
figure mixes the two windows except the join consistency check, which
is labeled as such, and the required-pace arithmetic, which is
labeled derived. The ACS income layer is the 2024 5-year release
(2020-2024) and is labeled with that vintage wherever it appears.

**Join match rates.** Three joins were made.
(1) Replacements to inventory on premise ID: the inventory stores
premise IDs as zero-padded strings and the replacements layer stores
them unpadded; joining on the raw strings silently undercounts. With
both sides normalized through integer conversion, 23,949 of the
replacements layer's 24,013 premise-ID rows (99.7 percent) match a
premise in the current inventory. The verification pass caught the
padding trap independently and now normalizes both sides.
(2) ZIP to ACS ZCTA median income: 47 of 62 five-digit ZIP strings in
the city scope matched a ZCTA record; matched ZIPs cover 187,253 of
187,289 city premises (99.98 percent). Unmatched strings are ZIP+4
artifacts and non-residential ZIPs with few premises.
(3) No premise-level demographic join was attempted or needed.

**Small numbers.** Neighborhood shares are computed for all 126 named
areas in the city scope, but the brief's share ranking leads with
areas of 900 or more premises, and the charts restrict share rankings
to areas with at least 500 premises; counts are always printed next
to shares so a small base is visible. District 11's zero is a
structural zero (post-1990s development at the far northeast), not a
small-sample artifact; its premises count (18,713 with district
assignment) is printed. The income correlation uses only ZIP codes
with at least 100 inventoried premises (32 ZIPs).

**Official definitions.** Categories are Denver Water's own strings
from the federal Lead and Copper Rule inventory framework; the
confirmed category's galvanized component is documented in the file's
own Category_Desc and matches EPA's galvanized-requiring-replacement
definition in the LCRI FAQ. "Lead Reduction Program" is Denver Water's
program name. The mandate figures (baseline inventory due November 1,
2027; 10 percent minimum cumulative-average replacement rate; all
lead and GRR lines replaced by the end of 2037 under Colorado's
implementation; unknowns identified by the deadline) come only from
EPA and CDPHE official pages, fetched live and quoted in sources.md.
Denver Water's program figures (26,000 plus replaced as of July 1,
2024; 60,000 to 64,000 total estimate; finish before 2035) come only
from denverwater.org pages, fetched live, and are attributed to the
utility in the brief rather than stated as this brief's measurements.

## Independent verification ledger

Every headline figure was recomputed from the raw downloads in the
separate stdlib pass (`code/verify.py`). Full ledger in
`verification_results.json`.

| Group | Checked | Reproduced | Corrected | Caveated |
|---|---|---|---|---|
| Inventory totals, both scopes | 10 | 10 | 0 | 0 |
| Neighborhood pools and premises (top 5 areas, premise counts) | 11 | 11 | 0 | 0 |
| Year-built era table (premises and pool, 7 eras) | 14 | 14 | 0 | 0 |
| Top-10 ZIP pools | 10 | 10 | 0 | 0 |
| Replacements layer (rows, dated rows, by-year, full-year average) | 9 | 9 | 0 | 0 |
| Join consistency (replaced premises now non-lead) | 1 | 1 | 0 | 0 |
| Outside-Denver pool leader (Wheat Ridge) | 1 | 1 | 0 | 0 |
| Derived required-pace figures | 2 | 2 | 0 | 0 |
| **Total** | **57** | **57** | **0** | **0** |

One process correction is recorded for honesty: the first run of the
verification pass reported the join figure as 21,566 against the
analysis pass's 23,942. The discrepancy was traced to zero-padded
premise IDs in the inventory (the verifier's bug, not the analysis's):
with both sides normalized, the two passes agree exactly at 23,942 of
23,949. The final ledger above reflects the corrected verifier.

Figures carried as CAVEATED rather than reproduced, by construction:
the current (2025-2026) replacement rate, which no public dataset in
the package measures (the published layer ends May 2, 2024); and any
comparison of today's category counts to counts published before the
October 2024 category streamlining. Both caveats are printed in the
brief itself, not only here.

## Layering admission test (standards, section 7)

**Layer considered:** Census ACS 2024 5-year median household income
(table B19013) by ZCTA, joined to the inventory at ZIP code level.

**The one-sentence claim it enables, which the brief could not make
without it:** At ZIP code level, Denver's remaining lead pool is not
concentrated in its lowest-income ZIP codes; pool share correlates
positively with median household income (+0.30) because the pool
tracks pre-1951 housing, and the average pool premise sits in a
higher-income ZIP code than the average premise ($110,615 against
$100,977, weighted medians).

**Verdict: ADMITTED**, as Finding 7, with the ecological limit printed
in the brief: ZIP codes, not households; current incomes, not the
incomes of the households that will schedule each replacement.

**Layers considered and cut:** (1) A tenure layer (renter share by
ZCTA) - the plausible claim about landlord access slowing
replacements cannot be measured from this file, which has no tenure
field, and a ZIP-level tenure correlation would invite a causal
reading the data cannot support. (2) A racial-demographics layer -
the inventory carries no demographic fields, the ZIP-level join would
be purely ecological, and no specific claim requiring it survived the
one-sentence test once the income result was in. Both cuts are
documented here per the standards.

## Reviewer notes

**Claims most likely to be challenged:**

- **"Ahead of the required pace."** The arithmetic is solid but the
  replacements layer ends May 2, 2024, so no one outside Denver Water
  can state the 2025-2026 rate from public data. A Denver Water
  reviewer could respond that the rate has since changed in either
  direction; the brief pre-empts this by attributing the recorded
  rate to its window and naming the layer's end as a finding in
  itself. The pace chart title ("the recorded rate runs ahead of the
  required rate") makes the same claim in miniature and may be the
  first thing challenged; the chart footnote carries the window.
- **The program pool as the obligation.** The pool (confirmed plus
  likely) is this brief's construct, built from Denver Water's own
  "Included in the Lead Reduction Program" labels. The strict federal
  replacement obligation covers confirmed lead and GRR lines; the
  likely lines are an identification obligation until investigated.
  The brief keeps the two halves visible in every stacked figure so
  the construct cannot be mistaken for a regulatory category, and
  Finding 4 is devoted to the split.
- **Wheat Ridge.** A suburban distributor area holding 82.3 percent of
  the outside-city pool, at a 27.5 percent pool share and 86.4
  percent unconfirmed, will surprise readers who think of the program
  as a Denver story. The figures reproduce cleanly; the open question
  is administrative (how distributor-area investigations are
  scheduled), which the brief does not speculate about.
- **Country Club at the top of the share ranking.** Its 68.3 percent
  is mostly unconfirmed (692 likely against 134 confirmed). The brief
  prints both numbers together; a chart reader who sees only the
  68.3 percent bar could overstate what is known about that
  neighborhood, which is why the share chart's footnote and Finding 4
  exist.

**Checks not completed:**

- No comparison was made against Denver Water's separate public
  dashboard totals for replacements after May 2024, because the
  dashboard is a web view, not a downloadable dataset; the official
  "26,000 plus as of July 1, 2024" figure from denverwater.org is used
  as the attributed program claim instead.
- Premise-level deduplication was not performed: the inventory holds
  91 duplicate premise ID values on distinct records (OBJECTIDs are
  unique). The brief counts premises as the file records them; if
  Denver Water confirms the duplicates are data errors, headline
  counts would move by at most 91 (0.03 percent).
- The 7 replaced premises that still carry a lead-family category
  were not adjudicated; the file does not say whether they are
  partial-segment replacements or records awaiting update.
- The `lsli_remove` flag is zero on all 311,491 rows in this
  snapshot, so it cannot be used to identify already-removed lines
  inside the inventory; replacement status was measured from the
  replacements layer instead.

**Findings that surprised me:**

- How suburban the tail of the program is: the outside-city pool is
  essentially one city, Wheat Ridge, and it is almost entirely
  unconfirmed.
- The two-geographies split inside Denver: the south-central
  neighborhoods (Platte Park, Washington Park, Rosedale) are
  confirmation-complete and waiting on construction, while Country
  Club, Park Hill and the University Hills area are still mostly
  unexamined lines. The same pool number means different work in
  different places.
- The income result ran against the usual environmental-burden
  expectation at ZIP level, for a mechanical reason: Denver's oldest
  housing, which is where the lead is, now sits in some of its
  highest-income ZIP codes.
- District 11 recording exactly zero pool premises, and District 6
  holding 4,532 pool premises (25.0 percent of the 18,150 pool
  premises the file assigns to a district), is a cleaner political
  map than the neighborhood table.
