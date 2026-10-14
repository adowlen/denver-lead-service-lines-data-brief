"""Layer test: does the remaining lead-pool share track neighborhood
income? Joins the brief's Denver-city ZIP table (from stats.json) to
ACS 2024 5-year median household income (table B19013) at ZCTA level,
pulled from the official Census summary file (the Census API is
key-gated). Output: layer_income_results.json.

Admission-test claim it would enable, if the data carries it: whether
the remaining program pool is concentrated in lower-income ZIP codes,
or tracks housing age rather than income.
"""
import io
import json
import urllib.request

import pandas as pd

PKG = "."
SF = ("https://www2.census.gov/programs-surveys/acs/summary_file/2024/"
      "table-based-SF/data/5YRData/acsdt5y2024-b19013.dat")

stats = json.load(open(f"{PKG}/data/stats.json"))
dv = pd.read_csv(f"{PKG}/data/denver_water_lsli_clean_2026-06-30.csv", low_memory=False)
dv = dv[dv["PREM_CITY"].astype(str).str.upper() == "DENVER"].copy()
dv["zip5"] = dv["PREM_POSTAL"].astype(str).str.extract(r"^(\d{5})", expand=False)
dv["in_pool"] = dv["category_short"].isin(["confirmed", "likely"])
z = (
    dv.groupby("zip5")
    .agg(premises=("OBJECTID", "count"), pool=("in_pool", "sum"),
         confirmed=("category_short", lambda s: int((s == "confirmed").sum())))
    .reset_index()
)
z["pool_share_pct"] = 100 * z["pool"] / z["premises"]

req = urllib.request.Request(SF, headers={"User-Agent": "machine-readable-brief/1.0"})
raw = urllib.request.urlopen(req, timeout=300).read().decode("utf-8", "replace")
acs = pd.read_csv(io.StringIO(raw), sep="|", dtype=str)
# table-based summary file columns: GEO_ID, NAME, B19013_001E ...
geo_col = [c for c in acs.columns if c.upper().startswith("GEO")][0]
est_col = [c for c in acs.columns if c.startswith("B19013_E001")][0]
acs = acs[acs[geo_col].str.startswith("860Z200US")].copy()  # summary level 860 = ZCTA
acs["zcta"] = acs[geo_col].str.extract(r"US(\d{5})$")
acs["median_hh_income"] = pd.to_numeric(acs[est_col], errors="coerce")
acs.loc[acs["median_hh_income"] < 0, "median_hh_income"] = float("nan")  # Census suppression codes
acs = acs[acs["zcta"].notna()][["zcta", "median_hh_income"]]

m = z.merge(acs, left_on="zip5", right_on="zcta", how="left")
matched = m["median_hh_income"].notna()
out = {
    "source": "ACS 2024 5-year, table B19013 (median household income), ZCTA level, official summary file acsdt5y2024-b19013.dat",
    "denver_zip5_in_inventory": int(len(z)),
    "matched_to_acs": int(matched.sum()),
    "premises_in_matched_zips": int(m.loc[matched, "premises"].sum()),
    "premises_denver_city": int(len(dv)),
}
mm = m[matched & (m["premises"] >= 100)].copy()
out["zips_used_for_correlation_min100premises"] = int(len(mm))
out["pearson_r_pool_share_vs_median_income"] = round(
    float(mm["pool_share_pct"].corr(mm["median_hh_income"])), 3)
out["pearson_r_confirmed_share_vs_median_income"] = round(
    float((100 * mm["confirmed"] / mm["premises"]).corr(mm["median_hh_income"])), 3)
# pool-weighted vs premises-weighted income picture
out["median_income_weighted_by_pool_premises"] = int(
    (mm["median_hh_income"] * mm["pool"]).sum() / mm["pool"].sum())
out["median_income_weighted_by_all_premises"] = int(
    (mm["median_hh_income"] * mm["premises"]).sum() / mm["premises"].sum())
top = mm.sort_values("pool_share_pct", ascending=False).head(5)
bot = mm.sort_values("pool_share_pct", ascending=True).head(5)
out["top5_pool_share_zips"] = top[["zip5", "premises", "pool", "pool_share_pct", "median_hh_income"]].to_dict("records")
out["bottom5_pool_share_zips"] = bot[["zip5", "premises", "pool", "pool_share_pct", "median_hh_income"]].to_dict("records")
out["table"] = mm.sort_values("pool", ascending=False)[
    ["zip5", "premises", "pool", "pool_share_pct", "median_hh_income"]].to_dict("records")

with open(f"{PKG}/layer_income_results.json", "w") as fh:
    json.dump(out, fh, indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "table"}, indent=1))
