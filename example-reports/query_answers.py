"""
Run all 5 example queries against the NRP S3 parquet files using DuckDB.
Answers what each chat example should produce when run in the app.
"""

import duckdb

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("SET s3_endpoint = 's3-west.nrp-nautilus.io';")
con.execute("SET s3_use_ssl = true;")
con.execute("SET s3_url_style = 'path';")

LANDVOTE = "read_parquet('s3://public-tpl/landvote.parquet')"
ALMANAC  = "read_parquet('s3://public-tpl/conservation-almanac-2024.parquet')"
SVI      = "read_parquet('s3://public-social-vulnerability/2022/SVI2022_US_county.parquet')"


def run(label, sql):
    print(f"\n--- {label} ---")
    rel = con.execute(sql)
    cols = [d[0] for d in rel.description]
    rows = rel.fetchall()
    # simple columnar print
    widths = [max(len(str(c)), max((len(str(r[i])) for r in rows), default=0)) for i, c in enumerate(cols)]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*cols))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(fmt.format(*[str(v) for v in row]))
    return rows


# ---------------------------------------------------------------------------
# Q1 — Travis County, TX: Austin's 30-year bond campaign + LWCF acquisitions
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("Q1: Austin's 30-year conservation bond campaign (Travis County, TX)")
print("    Expected tool calls: ~7")
print("    (get_dataset ×2, query ×2, zoom_to, toggle_layer, set_filter)")
print("=" * 70)

run("Ballot measures by decade", f"""
    SELECT
        CASE WHEN year < 2000 THEN '1990s'
             WHEN year < 2010 THEN '2000s'
             WHEN year < 2020 THEN '2010s'
             ELSE '2020s' END AS decade,
        COUNT(*) AS measures,
        SUM(CASE WHEN status = 'Pass' THEN 1 ELSE 0 END) AS passed,
        ROUND(SUM(conservation_funds_approved) / 1e6, 0) AS approved_M
    FROM {LANDVOTE}
    WHERE state = 'TX' AND county = 'Travis County'
    GROUP BY 1 ORDER BY 1
""")

run("LWCF + Bond-funded sites (Conservation Almanac)", f"""
    SELECT program, COUNT(DISTINCT tpl_id) AS sites,
        ROUND(SUM(acres) / COUNT(DISTINCT tpl_id)) AS avg_acres,
        MIN(year) AS first_year, MAX(year) AS last_year
    FROM {ALMANAC}
    WHERE state = 'Texas' AND county = 'Travis County'
      AND program NOT IN ('n/a', 'nan') AND program IS NOT NULL
    GROUP BY program ORDER BY sites DESC
""")


# ---------------------------------------------------------------------------
# Q2 — King County, WA: escalating conservation investment 2007–2025
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("Q2: King County, WA — conservation investment growth 2007–2025")
print("    Expected tool calls: ~4")
print("    (get_dataset, query, zoom_to, set_filter)")
print("=" * 70)

rows = run("All passed measures by year", f"""
    SELECT year,
        COALESCE(NULLIF(municipal, ''), '(county)') AS jurisdiction,
        ROUND(conservation_funds_approved / 1e6, 1) AS approved_M,
        REPLACE(REPLACE(purpose, 'Open space, parks, wildlife habitat, watershed protection, trails, recreation', 'open space, parks, wildlife, trails'), 'equity, climate', '+ equity + climate') AS purpose_short
    FROM {LANDVOTE}
    WHERE state = 'WA' AND county = 'King County' AND status = 'Pass'
    ORDER BY year
""")
total = sum(r[2] for r in rows if r[2])
print(f"\n  TOTAL: ${total:.0f}M across {len(rows)} measures (2007–2025)")


# ---------------------------------------------------------------------------
# Q3 — Florida watershed counties 2020–2024
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("Q3: Florida watershed protection ballot measures 2020–2024")
print("    Expected tool calls: ~4")
print("    (get_dataset, query, zoom_to, set_filter)")
print("=" * 70)

rows = run("Passed measures for watershed protection", f"""
    SELECT county, year, finance_mechanism,
        ROUND(conservation_funds_approved / 1e6, 1) AS approved_M
    FROM {LANDVOTE}
    WHERE state = 'FL' AND year BETWEEN 2020 AND 2024
      AND status = 'Pass' AND purpose LIKE '%watershed%'
    ORDER BY conservation_funds_approved DESC
""")
total = sum(r[3] for r in rows if r[3])
print(f"\n  TOTAL: ${total:.0f}M across {len(rows)} counties (2020–2024)")


# ---------------------------------------------------------------------------
# Q4 — Colorado conservation surge since 2020
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("Q4: Colorado conservation ballot measures 2020–2025")
print("    Expected tool calls: ~4")
print("    (get_dataset, query, zoom_to, set_filter)")
print("=" * 70)

rows = run("All passed measures since 2020", f"""
    SELECT county, COALESCE(NULLIF(municipal, ''), '(county)') AS jurisdiction,
        year, ROUND(conservation_funds_approved / 1e6, 1) AS approved_M,
        finance_mechanism
    FROM {LANDVOTE}
    WHERE state = 'CO' AND year >= 2020 AND status = 'Pass'
    ORDER BY conservation_funds_approved DESC NULLS LAST
""")
total = sum(r[3] for r in rows if r[3])
print(f"\n  TOTAL: ${total:.0f}M across {len(rows)} measures (2020–2025)")


# ---------------------------------------------------------------------------
# Q5 — Monmouth County, NJ: ballot measures + SVI equity overlay
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("Q5: Monmouth County, NJ — conservation investment vs. social vulnerability")
print("    Expected tool calls: ~6")
print("    (get_dataset ×2, query ×2, zoom_to, toggle_layer)")
print("=" * 70)

rows = run("Passed measures since 2017", f"""
    SELECT year, COALESCE(NULLIF(municipal, ''), '(county)') AS jurisdiction,
        finance_mechanism,
        ROUND(conservation_funds_approved / 1e6, 1) AS approved_M,
        purpose
    FROM {LANDVOTE}
    WHERE state = 'NJ' AND county = 'Monmouth County'
      AND year >= 2017 AND status = 'Pass'
    ORDER BY year DESC
""")
total = sum(r[3] for r in rows if r[3])
print(f"\n  TOTAL since 2017: ${total:.0f}M")

run("SVI across Monmouth County (county-level)", f"""
    SELECT COUNTY, STATE,
        ROUND(RPL_THEMES, 3) AS overall_svi,
        ROUND(RPL_THEME1, 3) AS socioeconomic,
        ROUND(RPL_THEME2, 3) AS household,
        ROUND(RPL_THEME3, 3) AS minority_status,
        ROUND(RPL_THEME4, 3) AS housing_transport
    FROM {SVI}
    WHERE COUNTY = 'Monmouth County' AND STATE = 'New Jersey'
""")
