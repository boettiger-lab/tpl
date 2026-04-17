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
    widths = [max(len(str(c)), max((len(str(r[i])) for r in rows), default=0))
              for i, c in enumerate(cols)]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*cols))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print(fmt.format(*[str(v) for v in row]))
    return rows


# ---------------------------------------------------------------------------
# Q1 — Charlotte County, FL: conservation sites and programs (Almanac)
# ---------------------------------------------------------------------------
print("=" * 70)
print("Q1: What conservation sites have been protected in Charlotte County,")
print("    Florida, and which programs funded them?")
print("    Tool calls: ~4  (get_dataset, query, zoom_to, toggle_layer)")
print("=" * 70)

run("Top sites by acreage", f"""
    SELECT site, ROUND(acres) AS acres, year, program, purchase_type
    FROM {ALMANAC}
    WHERE state = 'Florida' AND county = 'Charlotte County'
      AND program IS NOT NULL AND program NOT IN ('n/a','nan')
    ORDER BY acres DESC NULLS LAST
    LIMIT 12
""")

run("Programs summary", f"""
    SELECT program, COUNT(DISTINCT tpl_id) AS sites,
        ROUND(SUM(DISTINCT acres)) AS total_acres,
        MIN(year) AS first_year, MAX(year) AS last_year
    FROM {ALMANAC}
    WHERE state = 'Florida' AND county = 'Charlotte County'
      AND program IS NOT NULL AND program NOT IN ('n/a','nan')
    GROUP BY program ORDER BY total_acres DESC NULLS LAST
""")


# ---------------------------------------------------------------------------
# Q2 — Haywood County, NC: carbon + conserved land (Almanac + Carbon)
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("Q2: Where does irrecoverable carbon overlap with conserved land in")
print("    Haywood County, North Carolina?")
print("    Tool calls: ~6  (get_dataset x2, query, zoom_to, toggle_layer x2)")
print("=" * 70)

run("Conservation sites (Blue Ridge watersheds)", f"""
    SELECT site, ROUND(acres) AS acres, year, program, purchase_type, owner_type
    FROM {ALMANAC}
    WHERE state = 'North Carolina' AND county = 'Haywood County'
    ORDER BY acres DESC NULLS LAST
    LIMIT 12
""")

run("Programs summary", f"""
    SELECT program, COUNT(DISTINCT tpl_id) AS sites,
        ROUND(SUM(DISTINCT acres)) AS total_acres
    FROM {ALMANAC}
    WHERE state = 'North Carolina' AND county = 'Haywood County'
      AND program IS NOT NULL AND program NOT IN ('n/a','nan')
    GROUP BY program ORDER BY total_acres DESC NULLS LAST
""")


# ---------------------------------------------------------------------------
# Q3 — Chester County, PA: programs and largest sites (Almanac)
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("Q3: What programs have funded the largest conservation sites in")
print("    Chester County, Pennsylvania?")
print("    Tool calls: ~4  (get_dataset, query, zoom_to, toggle_layer)")
print("=" * 70)

run("Largest sites", f"""
    SELECT site, ROUND(acres) AS acres, year, program, purchase_type
    FROM {ALMANAC}
    WHERE state = 'Pennsylvania' AND county = 'Chester County'
      AND program IS NOT NULL AND program NOT IN ('n/a','nan')
    ORDER BY acres DESC NULLS LAST
    LIMIT 12
""")

run("Programs summary", f"""
    SELECT program, COUNT(DISTINCT tpl_id) AS sites,
        ROUND(SUM(DISTINCT acres)) AS total_acres
    FROM {ALMANAC}
    WHERE state = 'Pennsylvania' AND county = 'Chester County'
      AND program IS NOT NULL AND program NOT IN ('n/a','nan')
    GROUP BY program ORDER BY total_acres DESC NULLS LAST
""")


# ---------------------------------------------------------------------------
# Q4 — Colorado: conservation ballot measures since 2020 (LandVote)
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("Q4: Which Colorado counties have passed the most conservation")
print("    funding since 2020?")
print("    Tool calls: ~4  (get_dataset, query, zoom_to, set_filter)")
print("=" * 70)

rows = run("All passed measures since 2020", f"""
    SELECT county,
        COALESCE(NULLIF(municipal, ''), '(county)') AS jurisdiction,
        year,
        ROUND(conservation_funds_approved / 1e6, 1) AS approved_M,
        finance_mechanism
    FROM {LANDVOTE}
    WHERE state = 'CO' AND year >= 2020 AND status = 'Pass'
    ORDER BY conservation_funds_approved DESC NULLS LAST
""")
total = sum(r[3] for r in rows if r[3])
print(f"\n  TOTAL: ${total:.0f}M across {len(rows)} measures")


# ---------------------------------------------------------------------------
# Q5 — Monmouth County, NJ: ballot measures + SVI (LandVote + SVI)
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("Q5: Are Monmouth County, NJ's conservation investments reaching")
print("    vulnerable coastal communities?")
print("    Tool calls: ~6  (get_dataset x2, query x2, zoom_to, toggle_layer)")
print("=" * 70)

rows = run("Passed measures since 2017", f"""
    SELECT year,
        COALESCE(NULLIF(municipal, ''), '(county)') AS jurisdiction,
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

run("SVI — Monmouth County (county level)", f"""
    SELECT COUNTY, STATE,
        ROUND(RPL_THEMES, 3) AS overall_svi,
        ROUND(RPL_THEME1, 3) AS socioeconomic,
        ROUND(RPL_THEME2, 3) AS household,
        ROUND(RPL_THEME3, 3) AS minority_status,
        ROUND(RPL_THEME4, 3) AS housing_transport
    FROM {SVI}
    WHERE COUNTY = 'Monmouth County' AND STATE = 'New Jersey'
""")
