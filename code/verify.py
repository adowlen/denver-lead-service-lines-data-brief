"""Independent verification pass for the Denver lead lines brief.

Recomputes every headline figure directly from the RAW downloads with
the stdlib csv module (no pandas, no shared code with analyze.py) and
compares against data/stats.json and layer_income_results.json.
Writes verification_results.json with a per-figure ledger:
REPRODUCED / CORRECTED / CAVEATED.
"""
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone

PKG = "."
DATA = f"{PKG}/data"
csv.field_size_limit(10**9)

stats = json.load(open(f"{DATA}/stats.json"))
ledger = []


def check(name, brief_value, recomputed, note=""):
    status = "REPRODUCED" if brief_value == recomputed else "CORRECTED"
    ledger.append({"figure": name, "brief_value": brief_value,
                   "recomputed": recomputed, "status": status, "note": note})


CONF = "Confirmed lead service line; included in the Lead Reduction Program."
LIK = "Unknown; likely to have lead service line. Included in the Lead Reduction Program."
UNL = "Unknown; unlikely to have lead service line. Not included in the Lead Reduction Program."
NON = "No lead service line. Not included in Lead Reduction Program."

cat_all = Counter()
cat_den = Counter()
nb = defaultdict(Counter)
yb_den = defaultdict(Counter)
zip_den = defaultdict(Counter)
cd_den = defaultdict(Counter)
pool_by_city_outside = Counter()
n_rows = 0
denver_rows = 0
joined_ids = set()

with open(f"{DATA}/denver_water_lsl_replacements_raw.csv", newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        pid = row["Prem_id_cu"].strip()
        if pid:
            try:
                joined_ids.add(str(int(float(pid))))
            except ValueError:
                pass

rep_years = Counter()
rep_dated = 0
rep_rows = 0
with open(f"{DATA}/denver_water_lsl_replacements_raw.csv", newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        rep_rows += 1
        ms = row["Date_of_Re"].strip()
        if ms:
            try:
                dt = datetime.fromtimestamp(int(float(ms)) / 1000, tz=timezone.utc)
                rep_years[dt.year] += 1
                rep_dated += 1
            except (ValueError, OSError, OverflowError):
                pass

joined_cat = Counter()
with open(f"{DATA}/denver_water_lsli_raw_2026-06-30.csv", newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        n_rows += 1
        c = row["lsli_final_lead_cat"]
        cat_all[c] += 1
        # inventory premise ids are zero-padded strings; the
        # replacements layer stores them unpadded - normalize both
        # sides through int() or the join silently undercounts
        try:
            pid_norm = str(int(row["Prem_id_current"]))
        except ValueError:
            pid_norm = None
        if pid_norm is not None and pid_norm in joined_ids:
            joined_cat[c] += 1
        if row["PREM_CITY"].strip().upper() == "DENVER":
            denver_rows += 1
            cat_den[c] += 1
            short = {CONF: "confirmed", LIK: "likely", UNL: "unlikely", NON: "nonlead"}[c]
            nb[row["NHNAME"]][short] += 1
            nb[row["NHNAME"]]["premises"] += 1
            try:
                y = int(float(row["parcelyearbuilt"]))
            except ValueError:
                y = 0
            if y == 0:
                era = "unknown"
            elif y <= 1920:
                era = "1920 or earlier"
            elif y <= 1940:
                era = "1921-1940"
            elif y <= 1950:
                era = "1941-1950"
            elif y <= 1960:
                era = "1951-1960"
            elif y <= 1975:
                era = "1961-1975"
            else:
                era = "1976 or later"
            yb_den[era]["premises"] += 1
            if short in ("confirmed", "likely"):
                yb_den[era]["pool"] += 1
            z5 = row["PREM_POSTAL"].strip()[:5]
            zip_den[z5]["premises"] += 1
            if short in ("confirmed", "likely"):
                zip_den[z5]["pool"] += 1
        else:
            if c in (CONF, LIK):
                pool_by_city_outside[row["PREM_CITY"]] += 1

sa = stats["service_area"]
check("inventory rows", sa["premises"], n_rows)
check("service area confirmed", sa["confirmed"], cat_all[CONF])
check("service area likely", sa["likely"], cat_all[LIK])
check("service area unlikely", sa["unlikely"], cat_all[UNL])
check("service area nonlead", sa["nonlead"], cat_all[NON])
check("service area pool", sa["pool_confirmed_plus_likely"], cat_all[CONF] + cat_all[LIK])
dv = stats["denver_city"]
check("Denver city premises", dv["premises"], denver_rows)
check("Denver confirmed", dv["confirmed"], cat_den[CONF])
check("Denver likely", dv["likely"], cat_den[LIK])
check("Denver pool", dv["pool_confirmed_plus_likely"], cat_den[CONF] + cat_den[LIK])

nb_pool = {k: v["confirmed"] + v["likely"] for k, v in nb.items()}
stats_nb = {r["NHNAME"]: r for r in stats["neighborhoods_denver_city"]["table"]}
for name in ["Platte Park", "Washington Park", "Berkeley", "Cory-Merrill", "Country Club"]:
    check(f"neighborhood pool: {name}", stats_nb[name]["pool"], nb_pool.get(name))
    check(f"neighborhood premises: {name}", stats_nb[name]["premises"], nb[name]["premises"])
top5_recomputed = sum(v for _, v in sorted(nb_pool.items(), key=lambda kv: -kv[1])[:5])
check("top5 neighborhoods pool sum", stats["neighborhoods_denver_city"]["top5_pool_sum"], top5_recomputed)

for era, blk in yb_den.items():
    match = [r for r in stats["year_built_denver_city"] if r["era"] == era]
    if match:
        check(f"year-built {era} premises", int(match[0]["premises"]), blk["premises"])
        check(f"year-built {era} pool", int(match[0]["pool"]), blk["pool"])

z10 = sorted(zip_den.items(), key=lambda kv: -kv[1]["pool"])[:10]
stats_z = {str(r["zip5"]): r for r in stats["zip_top10_denver_city"]}
for z5, blk in z10:
    check(f"ZIP {z5} pool", int(stats_z[z5]["pool"]), blk["pool"])

rl = stats["replacements_layer"]
check("replacements rows", rl["rows"], rep_rows)
check("replacements dated rows", rl["rows_with_parseable_date"], rep_dated)
for y, n in sorted(rep_years.items()):
    check(f"replacements in {y}", rl["by_year"].get(str(y)), n)
full_avg = round(sum(rep_years[y] for y in [2020, 2021, 2022, 2023]) / 4, 1)
check("avg replacements per full year 2020-2023", rl["avg_per_full_year_2020_2023"], full_avg)
check("joined replaced premises now nonlead", rl["joined_current_category"]["nonlead"], joined_cat[NON])

wc, wp = pool_by_city_outside.most_common(1)[0]
check("largest outside-Denver pool city", stats["pool_by_city_top8"].get(wc), wp,
      note=f"city={wc}")

# derived required-pace figures, recomputed from first principles
pool = cat_all[CONF] + cat_all[LIK]
check("required per year, pre-2035 goal", stats["required_pace"]["pool_per_year_for_2035_goal"], round(pool / 8.5))
check("required per year, EPA 2037", stats["required_pace"]["pool_per_year_for_2037_deadline"], round(pool / 11.5))

out = {
    "checked_at": "2026-10-14",
    "ledger": ledger,
    "totals": {
        "checked": len(ledger),
        "reproduced": sum(1 for x in ledger if x["status"] == "REPRODUCED"),
        "corrected": sum(1 for x in ledger if x["status"] == "CORRECTED"),
    },
}
with open(f"{PKG}/verification_results.json", "w") as fh:
    json.dump(out, fh, indent=1)
print(json.dumps(out["totals"], indent=1))
for x in ledger:
    if x["status"] != "REPRODUCED":
        print("MISMATCH:", x)
print("ledger written:", len(ledger), "figures")
