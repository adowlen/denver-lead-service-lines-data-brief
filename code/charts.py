"""Charts for the Denver lead service lines brief - Machine Readable
brand palette. Every figure is drawn from data/stats.json (analyze.py)
and layer_income_results.json, and carries its scope and source on the
graphic. Text uses plain hyphens only.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

CHARCOAL = "#23221F"
PAPER = "#F1E7DA"
AMBER = "#E8A33D"
TEAL = "#2AA198"
AMBER_DIM = "#8A6420"
TEAL_DIM = "#1E6E68"
GRID = "#4A453C"
TEXT = "#F1E7DA"
TEXT_DIM = "#B8AE9C"

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # package root (this file lives in code/)
OUT = os.path.join(HERE, "charts")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": CHARCOAL,
    "axes.facecolor": CHARCOAL,
    "axes.edgecolor": GRID,
    "axes.labelcolor": TEXT,
    "text.color": TEXT,
    "xtick.color": TEXT_DIM,
    "ytick.color": TEXT_DIM,
    "grid.color": GRID,
    "grid.alpha": 0.5,
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.titlecolor": TEXT,
})

s = json.load(open(os.path.join(HERE, "data", "stats.json")))
inc = json.load(open(os.path.join(HERE, "layer_income_results.json")))
SRC = "Source: Denver Water Lead Service Line Inventory (LCRR snapshot, June 30, 2026), pulled Oct 14, 2026."
SRC_REP = "Source: Denver Water Lead Service Line Replacements layer (ArcGIS), pulled Oct 14, 2026."
SRC_SHORT = "Source: Denver Water LSL Inventory (June 30, 2026 snapshot), pulled Oct 14, 2026."


def save(fig, name, rect_bottom=0.0):
    fig.tight_layout(rect=[0, rect_bottom, 1, 1])
    fig.savefig(os.path.join(OUT, name), dpi=150, facecolor=CHARCOAL)
    plt.close(fig)
    print("saved", name)


def footnote(fig, text):
    fig.text(0.012, 0.014, text, fontsize=8.5, color=TEXT_DIM, va="bottom")


# 1. Category composition, service area vs City of Denver
fig, ax = plt.subplots(figsize=(10, 4.4))
scopes = [("City and County of Denver", s["denver_city"]), ("Denver Water service area", s["service_area"])]
cats = [("confirmed", AMBER, "Confirmed lead (incl. galvanized requiring replacement)"),
        ("likely", TEAL, "Unknown - likely lead"),
        ("unlikely", TEAL_DIM, "Unknown - unlikely lead"),
        ("nonlead", "#55504A", "Non-lead")]
for yi, (label, blk) in enumerate(scopes):
    left = 0
    for key, color, _ in cats:
        v = blk[key]
        ax.barh(yi, v, left=left, color=color, edgecolor="none")
        left += v
ax.set_yticks([0, 1])
ax.set_yticklabels([lbl for lbl, _ in scopes], fontsize=11)
ax.set_xlim(0, 311491)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.set_xlabel("premises in the June 30, 2026 inventory")
ax.set_title("What the inventory says about 311,491 service lines", pad=12)
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, c, _ in cats]
fig.legend(handles, [lbl for _, _, lbl in cats], loc="lower center", bbox_to_anchor=(0.5, 0.085),
           ncol=2, frameon=False, fontsize=9.5)
footnote(fig, "Service area: 11,400 confirmed, 10,026 likely, 14,667 unlikely, 275,398 non-lead. City: 10,822 confirmed,\n7,953 likely, 13,711 unlikely, 154,803 non-lead. Pool: 21,426 (6.9%) area; 18,775 (10.0%) city. " + SRC_SHORT)
save(fig, "category_composition.png", rect_bottom=0.24)

# 2. Top neighborhoods by remaining pool (stacked confirmed / likely)
nb = s["neighborhoods_denver_city"]["table"][:12][::-1]
fig, ax = plt.subplots(figsize=(10, 6.4))
ax.barh([r["NHNAME"] for r in nb], [r["confirmed"] for r in nb], color=AMBER, edgecolor="none", label="Confirmed lead (incl. GRR)")
ax.barh([r["NHNAME"] for r in nb], [r["likely"] for r in nb], left=[r["confirmed"] for r in nb], color=TEAL, edgecolor="none", label="Unknown - likely lead")
for i, r in enumerate(nb):
    ax.text(r["pool"] * 1.015, i, f"{r['pool']:,}  ({r['pool_share_pct']:.1f}% of premises)", va="center", fontsize=9, color=TEXT)
ax.set_xlim(0, max(r["pool"] for r in nb) * 1.22)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.set_xlabel("premises in the Lead Reduction Program pool (confirmed + likely)")
ax.set_title("Where the remaining lead pool sits: top 12 Denver neighborhoods")
ax.legend(loc="lower right", frameon=False, fontsize=9.5)
footnote(fig, "Scope: City and County of Denver premises (187,289); neighborhood as recorded in Denver Water's file.\nThe top 5 neighborhoods hold 5,868 pool premises, 31.3% of the city's pool. " + SRC_SHORT)
save(fig, "neighborhood_pool.png", rect_bottom=0.08)

# 3. Highest pool shares (neighborhoods with at least 500 premises)
big = [r for r in s["neighborhoods_denver_city"]["table"] if r["premises"] >= 500]
big = sorted(big, key=lambda r: r["pool_share_pct"], reverse=True)[:10][::-1]
fig, ax = plt.subplots(figsize=(10, 5.6))
ax.barh([r["NHNAME"] for r in big], [r["pool_share_pct"] for r in big], color=AMBER, edgecolor="none")
for i, r in enumerate(big):
    ax.text(r["pool_share_pct"] * 1.015, i, f"{r['pool_share_pct']:.1f}%  ({r['pool']:,} of {r['premises']:,})", va="center", fontsize=9, color=TEXT)
ax.set_xlim(0, max(r["pool_share_pct"] for r in big) * 1.25)
ax.set_xlabel("share of the neighborhood's premises in the program pool (confirmed + likely lead)")
ax.set_title("Where the pool share runs highest: up to two in three premises")
footnote(fig, "Neighborhoods with at least 500 inventoried premises, City and County of Denver scope. Citywide pool share: 10.0%.\n" + SRC)
save(fig, "neighborhood_share.png", rect_bottom=0.08)

# 4. Pool share by parcel year built (the pre-1951 cliff)
yb = s["year_built_denver_city"]
yb = [r for r in yb if r["era"] != "unknown"]
fig, ax = plt.subplots(figsize=(10, 5.2))
ax.bar([r["era"] for r in yb], [r["pool_share_pct"] for r in yb], color=AMBER, edgecolor="none", width=0.62)
for i, r in enumerate(yb):
    ax.text(i, r["pool_share_pct"] + 0.6, f"{r['pool_share_pct']:.1f}%\n({r['pool']:,} of {r['premises']:,})", ha="center", fontsize=9, color=TEXT)
ax.set_ylim(0, 30)
ax.set_ylabel("share of premises in the program pool (confirmed + likely)")
ax.set_xlabel("parcel year built (Denver Water inventory field)")
ax.set_title("Lead follows the age of the house: the pre-1951 cliff")
footnote(fig, "Scope: City and County of Denver premises with a recorded year built (179,307 of 187,289). Denver Water advises that homes built\nbefore 1951 are more likely to have a lead service line. " + SRC)
save(fig, "year_built.png", rect_bottom=0.09)

# 5. Replacement pace vs required pace
by = {int(k): v for k, v in s["replacements_layer"]["by_year"].items()}
years = sorted(by)
fig, ax = plt.subplots(figsize=(10, 5.4))
ax.bar([str(y) for y in years], [by[y] for y in years], color=TEAL, edgecolor="none", width=0.6)
for i, y in enumerate(years):
    ax.text(i, by[y] + 180, f"{by[y]:,}", ha="center", fontsize=10, color=TEXT)
req = s["required_pace"]
ax.axhline(req["pool_per_year_for_2035_goal"], color=AMBER, linestyle="--", linewidth=1.6)
ax.axhline(req["pool_per_year_for_2037_deadline"], color=PAPER, linestyle=":", linewidth=1.4)
ax.text(4.45, req["pool_per_year_for_2035_goal"] + 260, "needed per year from mid-2026 to clear the pool\nby Denver Water's pre-2035 goal: 2,521", fontsize=9.5, color=AMBER, ha="right")
ax.text(4.45, req["pool_per_year_for_2037_deadline"] - 780, "needed per year to clear the pool by the EPA\nend-of-2037 deadline: 1,863", fontsize=9.5, color=TEXT, ha="right")
ax.set_ylim(0, 8400)
ax.set_ylabel("dated replacements in the layer")
ax.set_title("Replacement pace: the recorded rate runs ahead of the required rate")
footnote(fig, "2024 bar covers Jan 1 to May 2 only; the published layer holds no later dated records. Full-year average 2020-2023:\n5,609 per year. Required rates are derived arithmetic from the 21,426-premises pool in the June 30, 2026 inventory. " + SRC_REP)
save(fig, "replacements_pace.png", rect_bottom=0.1)

# 6. Income layer: pool share vs ZCTA median household income
tab = inc["table"]
fig, ax = plt.subplots(figsize=(10, 5.6))
ax.scatter([r["median_hh_income"] for r in tab], [r["pool_share_pct"] for r in tab],
           s=[max(28, r["premises"] / 160) for r in tab], color=AMBER, alpha=0.82, edgecolor="none")
for r in tab:
    if r["zip5"] in ("80210", "80209", "80207", "80216"):
        ax.annotate(r["zip5"], (r["median_hh_income"], r["pool_share_pct"]),
                    textcoords="offset points", xytext=(7, 5), fontsize=9.5, color=TEXT)
ax.set_xlabel("median household income, ACS 2024 5-year (ZCTA)")
ax.set_ylabel("share of premises in the program pool (%)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${int(x/1000)}k"))
ax.set_title("The remaining pool does not sit in Denver's lowest-income ZIP codes")
footnote(fig, "One point per ZIP code with at least 100 inventoried premises (32 ZIPs); point size grows with premises. Correlation +0.30.\nZIP-level view only: it describes ZIP codes, not the households on any given street. Sources: inventory (above) and Census ACS 2024 5-year B19013.")
save(fig, "income_scatter.png", rect_bottom=0.09)

print("charts done")
