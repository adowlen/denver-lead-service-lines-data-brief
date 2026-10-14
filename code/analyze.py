"""Analysis for the Denver lead service lines brief (2026-10-15).

Reads the raw ArcGIS downloads in data/, writes:
  data/denver_water_lsli_clean_2026-06-30.csv  (analysis fields only)
  data/stats.json                              (every figure the brief uses)

Category mapping uses Denver Water's own category strings from
lsli_final_lead_cat in the LSLI_20260630 snapshot:
  confirmed = "Confirmed lead service line; included in the Lead
              Reduction Program." (per Category_Desc this bucket holds
              lead lines AND galvanized lines that are or ever were
              downstream of a lead or unknown line, i.e. EPA's
              "galvanized requiring replacement")
  likely    = "Unknown; likely to have lead service line. Included in
              the Lead Reduction Program."
  unlikely  = "Unknown; unlikely to have lead service line. Not
              included in the Lead Reduction Program."
  nonlead   = "No lead service line. Not included in Lead Reduction
              Program."
"Program pool" = confirmed + likely (the premises enrolled in the Lead
Reduction Program per the file's own descriptions).
"""
import json
import pandas as pd

PKG = "."
DATA = f"{PKG}/data"

CATMAP = {
    "Confirmed lead service line; included in the Lead Reduction Program.": "confirmed",
    "Unknown; likely to have lead service line. Included in the Lead Reduction Program.": "likely",
    "Unknown; unlikely to have lead service line. Not included in the Lead Reduction Program.": "unlikely",
    "No lead service line. Not included in Lead Reduction Program.": "nonlead",
}

inv = pd.read_csv(f"{DATA}/denver_water_lsli_raw_2026-06-30.csv", low_memory=False)
rep = pd.read_csv(f"{DATA}/denver_water_lsl_replacements_raw.csv", low_memory=False)

stats = {}
stats["inventory_rows"] = int(len(inv))
inv["cat"] = inv["lsli_final_lead_cat"].map(CATMAP)
assert inv["cat"].notna().all(), inv.loc[inv["cat"].isna(), "lsli_final_lead_cat"].unique()
inv["in_pool"] = inv["cat"].isin(["confirmed", "likely"])
inv["is_denver_city"] = inv["PREM_CITY"].astype(str).str.strip().str.upper() == "DENVER"

# ---------- cleaned dataset ----------
clean = inv[[
    "OBJECTID", "Prem_id_current", "prem_full_addr", "PREM_CITY", "PREM_POSTAL",
    "NHNAME", "denver_district", "parcelyearbuilt", "lsli_final_lead_cat",
    "cat", "lsli_remove", "Published_Date",
]].rename(columns={"cat": "category_short"})
clean.to_csv(f"{DATA}/denver_water_lsli_clean_2026-06-30.csv", index=False)

# ---------- category totals, both scopes ----------
def cat_block(df):
    vc = df["cat"].value_counts()
    n = len(df)
    return {
        "premises": int(n),
        "confirmed": int(vc.get("confirmed", 0)),
        "likely": int(vc.get("likely", 0)),
        "unlikely": int(vc.get("unlikely", 0)),
        "nonlead": int(vc.get("nonlead", 0)),
        "pool_confirmed_plus_likely": int(df["in_pool"].sum()),
        "unknown_total": int(vc.get("likely", 0) + vc.get("unlikely", 0)),
        "shares_pct": {
            k: round(100 * int(vc.get(k, 0)) / n, 2)
            for k in ["confirmed", "likely", "unlikely", "nonlead"]
        },
        "pool_share_pct": round(100 * float(df["in_pool"].mean()), 2),
    }

stats["service_area"] = cat_block(inv)
stats["denver_city"] = cat_block(inv[inv["is_denver_city"]])
stats["outside_denver_city"] = cat_block(inv[~inv["is_denver_city"]])

# ---------- neighborhoods (Denver city premises, NHNAME) ----------
dv = inv[inv["is_denver_city"]].copy()
nb = (
    dv.groupby("NHNAME")
    .agg(
        premises=("OBJECTID", "count"),
        confirmed=("cat", lambda s: int((s == "confirmed").sum())),
        likely=("cat", lambda s: int((s == "likely").sum())),
        unlikely=("cat", lambda s: int((s == "unlikely").sum())),
        median_year_built=("parcelyearbuilt", "median"),
    )
    .reset_index()
)
nb["pool"] = nb["confirmed"] + nb["likely"]
nb["pool_share_pct"] = (100 * nb["pool"] / nb["premises"]).round(2)
nb["confirmed_share_pct"] = (100 * nb["confirmed"] / nb["premises"]).round(2)
nb = nb.sort_values("pool", ascending=False)
stats["neighborhoods_denver_city"] = {
    "count": int(len(nb)),
    "table": nb.to_dict("records"),
    "top10_by_pool": nb.head(10).to_dict("records"),
    "top10_by_pool_share_min100premises": nb[nb["premises"] >= 100]
    .sort_values("pool_share_pct", ascending=False)
    .head(10)
    .to_dict("records"),
    "top5_pool_sum": int(nb.head(5)["pool"].sum()),
    "top10_pool_sum": int(nb.head(10)["pool"].sum()),
    "neighborhoods_with_zero_pool": int((nb["pool"] == 0).sum()),
    "neighborhoods_with_pool_share_ge_25pct": int((nb["pool_share_pct"] >= 25).sum()),
}

# ---------- council districts (where the file assigns one) ----------
dv = dv.copy()
dv["district_num"] = pd.to_numeric(dv["denver_district"], errors="coerce")
dv_dist = dv[dv["district_num"].between(1, 11)].copy()
dv_dist["denver_district"] = dv_dist["district_num"].astype(int)
cd = (
    dv_dist.groupby("denver_district")
    .agg(
        premises=("OBJECTID", "count"),
        confirmed=("cat", lambda s: int((s == "confirmed").sum())),
        likely=("cat", lambda s: int((s == "likely").sum())),
    )
    .reset_index()
)
cd["pool"] = cd["confirmed"] + cd["likely"]
cd["pool_share_pct"] = (100 * cd["pool"] / cd["premises"]).round(2)
stats["council_districts"] = {
    "premises_with_district": int(len(dv_dist)),
    "premises_denver_city_total": int(len(dv)),
    "table": cd.sort_values("district" if "district" in cd else "denver_district").to_dict("records"),
}

# ---------- year built ----------
def era(y):
    if pd.isna(y) or y == 0:
        return "unknown"
    if y <= 1920:
        return "1920 or earlier"
    if y <= 1940:
        return "1921-1940"
    if y <= 1950:
        return "1941-1950"
    if y <= 1960:
        return "1951-1960"
    if y <= 1975:
        return "1961-1975"
    return "1976 or later"

for scope_name, df in [("service_area", inv), ("denver_city", dv)]:
    e = df.assign(era=df["parcelyearbuilt"].apply(era))
    g = (
        e.groupby("era")
        .agg(
            premises=("OBJECTID", "count"),
            pool=("in_pool", "sum"),
            confirmed=("cat", lambda s: int((s == "confirmed").sum())),
        )
        .reset_index()
    )
    g["pool_share_pct"] = (100 * g["pool"] / g["premises"]).round(2)
    order = ["1920 or earlier", "1921-1940", "1941-1950", "1951-1960",
             "1961-1975", "1976 or later", "unknown"]
    g["ord"] = g["era"].apply(order.index)
    stats[f"year_built_{scope_name}"] = g.sort_values("ord").drop(columns="ord").to_dict("records")

stats["year_built_coverage"] = {
    "denver_city_missing_or_zero": int(((dv["parcelyearbuilt"].isna()) | (dv["parcelyearbuilt"] == 0)).sum()),
    "denver_city_premises": int(len(dv)),
}

# ---------- ZIP codes (Denver city; file stores ZIP and ZIP+4 run
# together with no dash, so normalize to the 5-digit prefix) ----------
dv["zip5"] = dv["PREM_POSTAL"].astype(str).str.extract(r"^(\d{5})", expand=False)
z = (
    dv.groupby("zip5")
    .agg(premises=("OBJECTID", "count"), pool=("in_pool", "sum"),
         confirmed=("cat", lambda s: int((s == "confirmed").sum())))
    .reset_index()
    .sort_values("pool", ascending=False)
)
z["pool_share_pct"] = (100 * z["pool"] / z["premises"]).round(2)
stats["zip_top10_denver_city"] = z.head(10).to_dict("records")

# ---------- replacements layer: pace ----------
rep["date"] = pd.to_datetime(rep["Date_of_Re"], unit="ms", errors="coerce")
rep_valid = rep[rep["date"].notna()].copy()
rep_valid["year"] = rep_valid["date"].dt.year
by_year = rep_valid.groupby("year").size().sort_index()
stats["replacements_layer"] = {
    "rows": int(len(rep)),
    "rows_with_parseable_date": int(len(rep_valid)),
    "rows_without_date": int(len(rep) - len(rep_valid)),
    "date_min": str(rep_valid["date"].min().date()),
    "date_max": str(rep_valid["date"].max().date()),
    "by_year": {int(k): int(v) for k, v in by_year.items()},
    "distinct_lsli_id": int(rep["lsli_id"].nunique()),
    "duplicate_lsli_id_rows": int(len(rep) - rep["lsli_id"].nunique()),
}
full_years = [y for y in [2020, 2021, 2022, 2023] if y in by_year.index]
stats["replacements_layer"]["avg_per_full_year_2020_2023"] = round(
    float(by_year.loc[full_years].mean()), 1) if full_years else None
stats["replacements_layer"]["layer_ends"] = "2024-05-02 (no dated records after this in the published layer)"
stats["replacements_layer"]["by_project_top"] = {
    str(k): int(v) for k, v in rep["Replacem_1"].value_counts().head(6).items()
}
stats["replacements_layer"]["full_replacement_rows"] = int(
    rep["Replacemen"].astype(str).str.strip().eq("FULL REPLACEMENT").sum())
# consistency: current category of replaced premises still in the inventory
rep_ids_set = set(rep["Prem_id_cu"].dropna().astype(int).astype(str))
joined = inv[inv["Prem_id_current"].astype(str).isin(rep_ids_set)]
jc = joined["cat"].value_counts()
stats["replacements_layer"]["joined_current_category"] = {
    str(k): int(v) for k, v in jc.items()
}

# join replacements to inventory on premise id (numeric in rep, string in inv)
inv_ids = set(inv["Prem_id_current"].astype(str).str.strip())
rep_ids = rep["Prem_id_cu"].dropna().astype(int).astype(str)
stats["replacements_layer"]["premise_id_join"] = {
    "rep_rows_with_premise_id": int(rep_ids.shape[0]),
    "matched_to_current_inventory": int(rep_ids.isin(inv_ids).sum()),
}

# ---------- required-pace arithmetic (derived, snapshot 2026-06-30) ----------
pool_sa = stats["service_area"]["pool_confirmed_plus_likely"]
conf_sa = stats["service_area"]["confirmed"]
stats["required_pace"] = {
    "snapshot_date": "2026-06-30",
    "pool_remaining_service_area": pool_sa,
    "confirmed_remaining_service_area": conf_sa,
    "years_to_denver_water_goal_end_2034": 8.5,
    "years_to_epa_deadline_end_2037": 11.5,
    "pool_per_year_for_2035_goal": round(pool_sa / 8.5),
    "pool_per_year_for_2037_deadline": round(pool_sa / 11.5),
    "confirmed_per_year_for_2037_deadline": round(conf_sa / 11.5),
}

# concentration: where the remaining pool sits
top_city = inv[~inv["is_denver_city"]].groupby("PREM_CITY")["in_pool"].sum().sort_values(ascending=False)
stats["pool_by_city_top8"] = {str(k): int(v) for k, v in top_city.head(8).items()}
stats["pool_in_denver_city_share_pct"] = round(
    100 * stats["denver_city"]["pool_confirmed_plus_likely"] / pool_sa, 1)

# the "likely" frontier: neighborhoods where unknowns dominate the pool
nb2 = nb.copy()
nb2["likely_share_of_pool_pct"] = (100 * nb2["likely"] / nb2["pool"]).round(1)
stats["likely_frontier_top8"] = (
    nb2[nb2["pool"] >= 100].sort_values("likely", ascending=False).head(8).to_dict("records")
)
stats["denver_city_premises_in_lakewood_named_area"] = int(
    dv["NHNAME"].astype(str).str.contains("Lakewood").sum())
stats["premise_id_duplicates"] = int(inv["Prem_id_current"].duplicated().sum())

with open(f"{DATA}/stats.json", "w") as fh:
    json.dump(stats, fh, indent=1, default=str)

print(json.dumps({k: stats[k] for k in
                  ["service_area", "denver_city", "required_pace", "pool_in_denver_city_share_pct"]},
                 indent=1, default=str))
print("neighborhoods:", stats["neighborhoods_denver_city"]["count"],
      "| top5 pool sum:", stats["neighborhoods_denver_city"]["top5_pool_sum"])
print("replacements by year:", stats["replacements_layer"]["by_year"])
