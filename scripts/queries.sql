-- =============================================================
-- TPL Stories — every query that backs a number in the slide decks.
-- Run via the geo-agent duckdb-mcp tool against the public STAC catalog at
-- https://s3-west.nrp-nautilus.io/public-data/stac/catalog.json
--
-- All intersection queries follow the "mask-before-aggregate" DPP pattern:
-- SEMI JOIN the small mask onto the global hex parquet *before* GROUP BY.
-- =============================================================

----------------------------------------------------------------
-- HEADLINE NUMBERS
----------------------------------------------------------------
SELECT
  (SELECT COUNT(*) FROM read_parquet('s3://public-tpl/landvote.parquet')) AS n_measures,
  (SELECT COUNT(*) FILTER (WHERE status IN ('Pass','Pass*'))
   FROM read_parquet('s3://public-tpl/landvote.parquet')) AS n_pass,
  (SELECT COUNT(DISTINCT state) FROM read_parquet('s3://public-tpl/landvote.parquet')) AS n_states,
  (SELECT ROUND(SUM(conservation_funds_approved)/1e9, 1)
   FROM read_parquet('s3://public-tpl/landvote.parquet')) AS cons_B,
  (SELECT ROUND(SUM(total_funds_approved)/1e9, 1)
   FROM read_parquet('s3://public-tpl/landvote.parquet')) AS total_B,
  (SELECT COUNT(*) FROM read_parquet('s3://public-tpl/conservation-almanac-2024-sites.parquet')) AS almanac_sites,
  (SELECT ROUND(SUM(acres)/1e6, 2) FROM read_parquet('s3://public-tpl/conservation-almanac-2024-sites.parquet')) AS acres_M,
  (SELECT ROUND(SUM(amount)/1e9, 1) FROM read_parquet('s3://public-tpl/conservation-almanac-2024-funding.parquet')) AS almanac_funding_B;

----------------------------------------------------------------
-- A1 — annual conservation funding approved
----------------------------------------------------------------
SELECT year,
  COUNT(*) AS n_total,
  COUNT(*) FILTER (WHERE status IN ('Pass','Pass*')) AS n_pass,
  ROUND(SUM(conservation_funds_approved)/1e9, 3) AS cons_B
FROM read_parquet('s3://public-tpl/landvote.parquet')
GROUP BY year ORDER BY year;

----------------------------------------------------------------
-- A2 — mechanism breakdown
----------------------------------------------------------------
SELECT finance_mechanism AS mechanism,
  COUNT(*) AS n,
  ROUND(100.0 * COUNT(*) FILTER (WHERE status IN ('Pass','Pass*')) / COUNT(*), 1) AS pass_pct,
  ROUND(SUM(conservation_funds_approved)/1e9, 2) AS cons_B
FROM read_parquet('s3://public-tpl/landvote.parquet')
GROUP BY finance_mechanism
ORDER BY cons_B DESC;

----------------------------------------------------------------
-- A3 — irrecoverable carbon under LandVote-approved jurisdictions
-- INTERSECTION: LandVote Pass hex × irrecoverable-carbon-2024 hex
----------------------------------------------------------------
WITH lv AS (
  SELECT DISTINCT h8, h0, state
  FROM read_parquet('s3://public-tpl/landvote/hex/h0=*/data_0.parquet')
  WHERE status IN ('Pass','Pass*')
),
c AS (
  SELECT c.h8, c.h0, AVG(c.carbon) AS carbon_avg
  FROM read_parquet('s3://public-carbon/irrecoverable-carbon-2024/hex/h0=*/data_0.parquet') c
  SEMI JOIN lv ON c.h8 = lv.h8 AND c.h0 = lv.h0
  GROUP BY c.h8, c.h0
)
SELECT lv.state, ROUND(SUM(c.carbon_avg)/1e6, 2) AS Mt
FROM lv JOIN c USING(h8, h0)
GROUP BY lv.state ORDER BY Mt DESC LIMIT 12;

----------------------------------------------------------------
-- B1 — biodiversity (NCP natural-habitat) under Almanac sites
-- INTERSECTION: Almanac sites hex × NCP biodiversity hex
----------------------------------------------------------------
WITH al AS (
  SELECT DISTINCT h8, h0, state_id
  FROM read_parquet('s3://public-tpl/conservation-almanac-2024-sites/hex/h0=*/data_0.parquet')
),
b AS (
  SELECT b.h8, b.h0, AVG(b.ncp) AS biod_avg
  FROM read_parquet('s3://public-ncp/hex/ncp_biod_nathab/h0=*/data_0.parquet') b
  SEMI JOIN al ON b.h8 = al.h8 AND b.h0 = al.h0
  GROUP BY b.h8, b.h0
)
SELECT al.state_id AS state, ROUND(AVG(b.biod_avg), 3) AS biod
FROM al JOIN b USING(h8, h0)
GROUP BY al.state_id
HAVING COUNT(DISTINCT al.h8) > 1000
ORDER BY biod DESC LIMIT 12;

----------------------------------------------------------------
-- B2 — Florida county passes since 2018
----------------------------------------------------------------
SELECT NULLIF(county,'nan') AS county, year,
  ROUND(conservation_funds_approved/1e6, 1) AS M,
  percent_yes
FROM read_parquet('s3://public-tpl/landvote.parquet')
WHERE state='FL' AND year >= 2018 AND status IN ('Pass','Pass*')
  AND county IS NOT NULL AND county != 'nan'
  AND conservation_funds_approved IS NOT NULL
ORDER BY conservation_funds_approved DESC LIMIT 12;

----------------------------------------------------------------
-- B3 — Florida Forever annual deployment
----------------------------------------------------------------
SELECT s.year,
  COUNT(DISTINCT s.tpl_id) AS n_sites,
  ROUND(SUM(s.acres)/1000, 1) AS acres_k,
  ROUND(SUM(f.amount)/1e6, 1) AS funding_M
FROM read_parquet('s3://public-tpl/conservation-almanac-2024-sites.parquet') s
JOIN read_parquet('s3://public-tpl/conservation-almanac-2024-funding.parquet') f USING(tpl_id)
WHERE f.program = 'Florida Forever' AND s.year BETWEEN 1998 AND 2021
GROUP BY s.year ORDER BY s.year;

----------------------------------------------------------------
-- C1 — pass rate by jurisdiction party
----------------------------------------------------------------
SELECT party,
  COUNT(*) AS n,
  ROUND(100.0 * COUNT(*) FILTER (WHERE status IN ('Pass','Pass*')) / COUNT(*), 1) AS pass_pct,
  ROUND(SUM(conservation_funds_approved)/1e9, 2) AS cons_B
FROM read_parquet('s3://public-tpl/landvote.parquet')
WHERE party IN ('Democrat','Republican')
GROUP BY party;

----------------------------------------------------------------
-- C2 — state pass rate vs share Republican
----------------------------------------------------------------
SELECT state,
  COUNT(*) AS n,
  ROUND(100.0 * COUNT(*) FILTER (WHERE status IN ('Pass','Pass*')) / COUNT(*), 1) AS pass_pct,
  ROUND(100.0 * COUNT(*) FILTER (WHERE party='Republican') / COUNT(*), 1) AS pct_R
FROM read_parquet('s3://public-tpl/landvote.parquet')
GROUP BY state HAVING COUNT(*) >= 20 ORDER BY pct_R DESC;

----------------------------------------------------------------
-- C3 — large recent wins in Republican-leaning jurisdictions
----------------------------------------------------------------
SELECT state,
  NULLIF(county,'nan')    AS county,
  NULLIF(municipal,'nan') AS municipal,
  year,
  ROUND(conservation_funds_approved/1e6, 1) AS M,
  percent_yes,
  finance_mechanism
FROM read_parquet('s3://public-tpl/landvote.parquet')
WHERE year >= 2018 AND status IN ('Pass','Pass*') AND party='Republican'
  AND conservation_funds_approved >= 50e6
ORDER BY conservation_funds_approved DESC LIMIT 10;

----------------------------------------------------------------
-- D — SVI quartile equity table (Almanac sites + LandVote measures)
-- INTERSECTION: Almanac/LandVote × SVI county-aggregated quartile
----------------------------------------------------------------
WITH state_name(abbr, name) AS (VALUES
  ('AL','Alabama'),('AK','Alaska'),('AZ','Arizona'),('AR','Arkansas'),('CA','California'),
  ('CO','Colorado'),('CT','Connecticut'),('DE','Delaware'),('FL','Florida'),('GA','Georgia'),
  ('HI','Hawaii'),('ID','Idaho'),('IL','Illinois'),('IN','Indiana'),('IA','Iowa'),
  ('KS','Kansas'),('KY','Kentucky'),('LA','Louisiana'),('ME','Maine'),('MD','Maryland'),
  ('MA','Massachusetts'),('MI','Michigan'),('MN','Minnesota'),('MS','Mississippi'),('MO','Missouri'),
  ('MT','Montana'),('NE','Nebraska'),('NV','Nevada'),('NH','New Hampshire'),('NJ','New Jersey'),
  ('NM','New Mexico'),('NY','New York'),('NC','North Carolina'),('ND','North Dakota'),('OH','Ohio'),
  ('OK','Oklahoma'),('OR','Oregon'),('PA','Pennsylvania'),('RI','Rhode Island'),('SC','South Carolina'),
  ('SD','South Dakota'),('TN','Tennessee'),('TX','Texas'),('UT','Utah'),('VT','Vermont'),
  ('VA','Virginia'),('WA','Washington'),('WV','West Virginia'),('WI','Wisconsin'),('WY','Wyoming')),
svi_county AS (
  SELECT STATE, COUNTY, AVG(RPL_THEMES) AS svi_avg
  FROM read_parquet('s3://public-social-vulnerability/2022/SVI2022_US_tract.parquet')
  WHERE RPL_THEMES IS NOT NULL AND RPL_THEMES >= 0
  GROUP BY STATE, COUNTY),
q AS (SELECT *, NTILE(4) OVER (ORDER BY svi_avg) AS svi_q FROM svi_county),
site_funding AS (
  SELECT tpl_id, SUM(amount) AS funding
  FROM read_parquet('s3://public-tpl/conservation-almanac-2024-funding.parquet')
  GROUP BY tpl_id),
sites_enriched AS (
  SELECT s.tpl_id, s.state_id, s.county, s.acres, COALESCE(f.funding, 0) AS funding
  FROM read_parquet('s3://public-tpl/conservation-almanac-2024-sites.parquet') s
  LEFT JOIN site_funding f USING(tpl_id)
  WHERE s.acres > 0 AND s.county IS NOT NULL),
alm AS (
  SELECT q.svi_q,
    COUNT(DISTINCT s.tpl_id) AS sites,
    ROUND(SUM(s.acres)/1e6, 2) AS acres_M,
    ROUND(SUM(s.funding)/1e9, 2) AS funding_B
  FROM sites_enriched s
  JOIN state_name n ON n.abbr = s.state_id
  JOIN q ON q.STATE = n.name AND q.COUNTY = s.county
  GROUP BY q.svi_q),
lv AS (
  SELECT q.svi_q,
    COUNT(*) AS measures,
    ROUND(100.0 * COUNT(*) FILTER (WHERE lv.status IN ('Pass','Pass*')) / COUNT(*), 1) AS pass_pct,
    ROUND(SUM(lv.conservation_funds_approved)/1e9, 2) AS cons_B
  FROM read_parquet('s3://public-tpl/landvote.parquet') lv
  JOIN state_name n ON n.abbr = lv.state
  JOIN q ON q.STATE = n.name AND q.COUNTY = lv.county
  WHERE lv.county IS NOT NULL AND lv.county != 'nan'
  GROUP BY q.svi_q)
SELECT alm.svi_q,
  CASE alm.svi_q WHEN 1 THEN 'Q1 (least vulnerable)' WHEN 2 THEN 'Q2' WHEN 3 THEN 'Q3' WHEN 4 THEN 'Q4 (most vulnerable)' END AS quartile,
  alm.sites AS almanac_sites, alm.acres_M, alm.funding_B AS almanac_funding_B,
  lv.measures AS landvote_measures, lv.pass_pct AS landvote_pass_pct, lv.cons_B AS landvote_cons_B
FROM alm JOIN lv USING(svi_q) ORDER BY alm.svi_q;

----------------------------------------------------------------
-- E1 — top 20 congressional districts by irrecoverable carbon
-- INTERSECTION: census-2024-cd hex × irrecoverable-carbon-2024 hex
----------------------------------------------------------------
WITH cd AS (
  SELECT DISTINCT h8, h0, GEOID, STATEFP, NAMELSAD
  FROM read_parquet('s3://public-census/census-2024/cd/hex/h0=*/data_0.parquet')),
c AS (
  SELECT c.h8, c.h0, AVG(c.carbon) AS c_avg
  FROM read_parquet('s3://public-carbon/irrecoverable-carbon-2024/hex/h0=*/data_0.parquet') c
  SEMI JOIN cd ON c.h8 = cd.h8 AND c.h0 = cd.h0
  GROUP BY c.h8, c.h0),
state_fp(fp, abbr) AS (VALUES
  ('01','AL'),('02','AK'),('04','AZ'),('05','AR'),('06','CA'),('08','CO'),
  ('09','CT'),('10','DE'),('12','FL'),('13','GA'),('15','HI'),('16','ID'),
  ('17','IL'),('18','IN'),('19','IA'),('20','KS'),('21','KY'),('22','LA'),
  ('23','ME'),('24','MD'),('25','MA'),('26','MI'),('27','MN'),('28','MS'),
  ('29','MO'),('30','MT'),('31','NE'),('32','NV'),('33','NH'),('34','NJ'),
  ('35','NM'),('36','NY'),('37','NC'),('38','ND'),('39','OH'),('40','OK'),
  ('41','OR'),('42','PA'),('44','RI'),('45','SC'),('46','SD'),('47','TN'),
  ('48','TX'),('49','UT'),('50','VT'),('51','VA'),('53','WA'),('54','WV'),
  ('55','WI'),('56','WY'))
SELECT s.abbr AS state, cd.NAMELSAD AS district, ROUND(SUM(c.c_avg)/1e6, 2) AS Mt
FROM cd JOIN c USING(h8, h0)
JOIN state_fp s ON s.fp = cd.STATEFP
GROUP BY s.abbr, cd.NAMELSAD ORDER BY Mt DESC LIMIT 20;

----------------------------------------------------------------
-- E2 — state irrecoverable carbon × LandVote activity (the targeting scatter)
-- INTERSECTION: census-2024-state hex × carbon hex, joined to LandVote
----------------------------------------------------------------
WITH st AS (
  SELECT DISTINCT h8, h0, STUSPS
  FROM read_parquet('s3://public-census/census-2024/state/hex/h0=*/data_0.parquet')),
c AS (
  SELECT c.h8, c.h0, AVG(c.carbon) AS c_avg
  FROM read_parquet('s3://public-carbon/irrecoverable-carbon-2024/hex/h0=*/data_0.parquet') c
  SEMI JOIN st ON c.h8 = st.h8 AND c.h0 = st.h0
  GROUP BY c.h8, c.h0),
carbon AS (
  SELECT st.STUSPS AS state, ROUND(SUM(c.c_avg)/1e6, 2) AS carbon_Mt
  FROM st JOIN c USING(h8, h0) GROUP BY st.STUSPS),
lv AS (
  SELECT state,
    COUNT(*) AS total_n,
    COUNT(*) FILTER (WHERE year >= 2020) AS recent_n,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status IN ('Pass','Pass*')) / COUNT(*), 1) AS pass_pct,
    ROUND(COALESCE(SUM(conservation_funds_approved) FILTER (WHERE year < 2020), 0)/1e6, 0) AS prior_M,
    ROUND(COALESCE(SUM(conservation_funds_approved) FILTER (WHERE year >= 2020), 0)/1e6, 0) AS recent_M
  FROM read_parquet('s3://public-tpl/landvote.parquet')
  GROUP BY state)
SELECT carbon.state, carbon.carbon_Mt,
  COALESCE(lv.total_n, 0) AS total_n,
  COALESCE(lv.recent_n, 0) AS recent_n,
  COALESCE(lv.pass_pct, 0) AS pass_pct,
  COALESCE(lv.prior_M, 0)  AS prior_M,
  COALESCE(lv.recent_M, 0) AS recent_M
FROM carbon LEFT JOIN lv USING(state)
WHERE carbon.carbon_Mt > 1
ORDER BY carbon.carbon_Mt DESC;

----------------------------------------------------------------
-- F — dormant champions detail
----------------------------------------------------------------
SELECT state,
  COUNT(*) AS total_n,
  ROUND(100.0 * COUNT(*) FILTER (WHERE status IN ('Pass','Pass*')) / COUNT(*), 1) AS pass_pct,
  MAX(year) FILTER (WHERE status IN ('Pass','Pass*')) AS last_pass_year,
  ROUND(COALESCE(SUM(conservation_funds_approved) FILTER (WHERE year < 2020), 0)/1e6, 0) AS prior_M,
  ROUND(COALESCE(SUM(conservation_funds_approved) FILTER (WHERE year >= 2020), 0)/1e6, 0) AS recent_M
FROM read_parquet('s3://public-tpl/landvote.parquet')
WHERE state IN ('GA','OK','VA','MO','MD','ME','NM','RI','CT','IA','NC','SC')
GROUP BY state ORDER BY prior_M DESC;
