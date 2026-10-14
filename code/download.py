"""Download the Denver Water lead service line inventory (LCRR) and the
Lead Service Line Replacements layer from the Denver Water ArcGIS org
(services.arcgis.com/czCXlxn6hYtK4vdg).

Inventory: LRP_Inventory_LCRR_DEMO / layer 0 (LSLI_20260630 snapshot).
Replacements: Lead_Service_Line_Replacements / layer 6.

Paginated pull ordered by OBJECTID, server count re-confirmed before
download. Raw JSON attributes are written to CSV verbatim; the cleaned
copy keeps analysis fields only (no contact fields exist in either
layer - fields are premise address, premise/tap IDs, category, parcel
year built, neighborhood, city, ZIP).
"""
import csv
import json
import sys
import urllib.parse
import urllib.request

BASE = "https://services.arcgis.com/czCXlxn6hYtK4vdg/arcgis/rest/services"
PAGE = 2000


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "machine-readable-brief/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def server_count(service, layer):
    url = f"{BASE}/{service}/FeatureServer/{layer}/query?where=1%3D1&returnCountOnly=true&f=json"
    return fetch(url)["count"]


def download(service, layer, out_csv):
    total = server_count(service, layer)
    print(f"{service}/{layer}: server count = {total:,}")
    rows = []
    offset = 0
    while True:
        params = {
            "where": "1=1",
            "outFields": "*",
            "orderByFields": "OBJECTID ASC",
            "resultOffset": offset,
            "resultRecordCount": PAGE,
            "returnGeometry": "false",
            "f": "json",
        }
        url = f"{BASE}/{service}/FeatureServer/{layer}/query?" + urllib.parse.urlencode(params)
        data = fetch(url)
        feats = data.get("features", [])
        if not feats:
            break
        rows.extend(f["attributes"] for f in feats)
        offset += len(feats)
        print(f"  {offset:,}/{total:,}", flush=True)
        if len(feats) < PAGE:
            break
    assert len(rows) == total, f"downloaded {len(rows)} != server count {total}"
    fields = list(rows[0].keys())
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out_csv}: {len(rows):,} rows, fields: {fields}")
    return rows


if __name__ == "__main__":
    out_dir = sys.argv[1]
    download("LRP_Inventory_LCRR_DEMO", 0, f"{out_dir}/denver_water_lsli_raw_2026-06-30.csv")
    download("Lead_Service_Line_Replacements", 6, f"{out_dir}/denver_water_lsl_replacements_raw.csv")
