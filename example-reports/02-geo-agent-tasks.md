# Geo-Agent Tasks Relevant to TPL Reports

This document maps the data needs identified in TPL's reports to tasks that the geo-agent could perform -- either with current data layers or with additional datasets.

---

## Current Geo-Agent Capabilities

The TPL geo-agent currently has:
- **Conservation Almanac 2024** -- site-level conservation transactions (site name, acreage, funding amount, program, owner, year, state, county) as both PMTiles and H3-indexed Parquet
- **LandVote ballot measures** -- 3,886 conservation ballot measures (1988-2025) with jurisdiction geometry, year, status (Pass/Fail/Pass*), percent_yes/percent_no, finance_mechanism (property tax, bond, sales tax, income tax, real estate transfer tax, other), total_funds_at_stake, total_funds_approved, conservation_funds_at_stake, conservation_funds_approved, party affiliation, purpose, full ballot description text, and notes. Available as GeoParquet, PMTiles, H3 hex Parquet, and raw CSV.
- **Carbon layers** -- irrecoverable, vulnerable, and manageable carbon (2024 rasters + H3 hex Parquet)
- **Social Vulnerability Index (SVI) 2022** -- county and tract level
- **Political boundaries** -- Congressional Districts (2024), State Assembly Districts (2025), State Senate Districts (2025) as PMTiles + H3 hex Parquet
- **Global Wetlands (GLWD)** -- wetland type classification raster
- **DuckDB SQL query tool** -- joins across all H3-indexed datasets

---

## Task Category 1: Legislative District Briefings

These are the most directly addressable report type. The geo-agent can already generate most of the quantitative content.

### Tasks the agent CAN do now:

| Task | How | Data Source |
|---|---|---|
| List all conservation sites in a state senate/assembly/congressional district | H3 join between political boundary hex and Almanac hex | census-2025-sldu/sldl + conservation-almanac-2024 |
| Break down funding by program within a district | GROUP BY program after H3 join | conservation-almanac-2024 |
| Total acres protected and dollars spent in a district | CTE for deduplicated acres + SUM(amount) | conservation-almanac-2024 |
| Show specific project details (site name, acreage, funding, program, owner) | Direct query on Almanac flat parquet with ILIKE | conservation-almanac-2024 |
| Show ballot measure results for jurisdictions within a district's geography | Query LandVote with state/county filters | landvote |
| Map conservation sites in a district | show_layer + set_filter on Almanac PMTiles | Almanac PMTiles |
| Map the legislative district boundary | show_layer on census boundary | census PMTiles |
| Overlay carbon data on a district | show_layer for carbon + H3 join for totals | carbon hex + census hex |
| Overlay social vulnerability on conservation sites | show SVI + Almanac layers; H3 join for stats | SVI + Almanac |

### Tasks that NEED additional data or features:

| Task | What's Missing | Priority |
|---|---|---|
| District-level ballot measure vote counts (e.g., "125,089 Yes votes") | LandVote has `percent_yes`/`percent_no` and `total_funds_approved` but raw vote counts (number of yes/no ballots) are not in the dataset. The Florida briefing's "125,089 Yes votes" would require a separate election results source. | Medium |
| Identify the legislator for a district (name, party) | No legislator database; would need a lookup table mapping district GEOID to current representative | Medium |
| Auto-generate a formatted one-page brief | No document/report generation capability; agent returns text/tables only | Low (out of scope for agent) |

---

## Task Category 2: Local Feasibility Study Components

### Tasks the agent CAN do now:

| Task | How | Data Source |
|---|---|---|
| Total conservation spending in a county over time | Filter Almanac by county, aggregate by year | conservation-almanac-2024 |
| List conservation sites acquired in a county with acreage and funding | Direct query filtered by county | conservation-almanac-2024 |
| Show which programs/agencies funded conservation in a county | GROUP BY program, owner, owner_type | conservation-almanac-2024 |
| Ballot measure history for a county | Query LandVote filtered by county/state | landvote |
| Count passed vs. failed measures by finance mechanism | GROUP BY finance_mechanism, status | landvote |
| Map conserved lands in a county | Filter Almanac PMTiles to county | Almanac PMTiles |
| Carbon stock analysis for a county | H3 join between county boundary hex and carbon hex | carbon hex + county hex (available, needs app config) |
| Social vulnerability overlay with conservation sites | H3 join between SVI and Almanac | SVI + Almanac |
| Statewide ballot measure pass rates | Aggregate LandVote by state and mechanism type | landvote |
| Total conservation funds approved by county/state | SUM(conservation_funds_approved) grouped by geography | landvote |
| Bond vs. sales tax vs. property tax success rates by state | GROUP BY state, finance_mechanism with pass/fail counts | landvote |
| Dollars at stake vs. approved (funding gap analysis) | Compare total_funds_at_stake to total_funds_approved | landvote |
| Political context of ballot measures (party affiliation) | GROUP BY party, status to show pass rates by political leaning | landvote |
| Full ballot measure text/description lookup | Query `description` field for specific measures | landvote |
| Time series of conservation funding approved by year | GROUP BY year, SUM(conservation_funds_approved) | landvote |

### Tasks that NEED additional data:

| Task | What's Missing | Priority |
|---|---|---|
| **Demographics table** (population, race, housing, income, education, health) | US Census ACS/QuickFacts data. Could be added as an H3-indexed dataset or queried via Census API. | **High** |
| **County financial data** (revenues, expenditures, debt, millage rates, taxable value) | County CAFR/ACFR data. No standard national dataset exists; would need state-specific sources or a curated database. | **High** (but hard) |
| **Bond cost calculator** (given taxable value, interest rate, maturity, compute annual debt service and cost per homeowner) | A computational tool, not a dataset. Could be implemented as a custom function or agent behavior. | **Medium** |
| **County-level political boundaries** (for H3 joins) | Census county boundaries exist in STAC catalog (`census-2024/county/hex`); just need to wire into `layers-input.json` and system prompt. | **High** (config-only) |
| **Election/voter turnout data** (registered voters, ballots cast, turnout %) | County Supervisor of Elections data. Not standardized nationally. | Medium |
| **Wildlife corridor / ecological network data** (e.g., Florida Wildlife Corridor opportunity areas) | State-specific ecological priority datasets. Florida FEGN, state wildlife action plans. | Medium |
| **Property acquisition inventories** with individual parcel details | Often county-managed data not in Almanac (e.g., Lake County's 2004 referendum acquisitions) | Low |
| **Water quality data** (nutrient loads, impaired waters) | EPA/state environmental agency data (e.g., 303(d) impaired waters list) | Medium |

---

## Task Category 3: Regional Climate & Finance Feasibility Study Components

### Tasks the agent CAN do now:

| Task | How | Data Source |
|---|---|---|
| **Carbon stock totals for a multi-county region** | H3 join between county boundaries and carbon hex, summed across counties | carbon hex + county hex (available, needs app config) |
| **Rank counties by carbon stock** | Same join, GROUP BY county, ORDER BY total carbon DESC | carbon hex + county hex (available, needs app config) |
| **Identify conservation sites in high-carbon areas** | H3 join between Almanac and carbon hex with threshold filter | Almanac + carbon hex |
| **Conservation spending trends over time for a region** | Filter Almanac by relevant counties, GROUP BY year | conservation-almanac-2024 |
| **Map carbon layers overlaid with conservation sites** | show_layer for both; visual comparison | Almanac PMTiles + carbon COG |
| **Wetland coverage in a region** | show_layer for GLWD + visual analysis | GLWD raster |
| **Cross-reference SVI with carbon and conservation** | Multi-way H3 join (SVI + carbon + Almanac) | All three hex datasets |
| **Ballot measure history for counties in a watershed** | LandVote filtered by multiple counties | landvote |

### Tasks that NEED additional data:

| Task | What's Missing | Priority |
|---|---|---|
| **Forest carbon by county with social/market value** | Need county boundaries as H3 hex. Carbon data exists but need dollar-value conversion factors (social cost of carbon). Could add as a computed column or lookup. | **High** |
| **Land use/land cover change data** (conversion trends) | NLCD (National Land Cover Database) or similar time-series LULC data as H3-indexed layers. Critical for showing "100,000 acres converted to development" type statistics. | **High** |
| **Water quality trend data** (nitrogen loads, nutrient concentrations) | EPA STORET/WQX data, state pollution control agency data. Would need time-series capability. | Medium |
| **State budget/fiscal data** (revenues by source, expenditures by category, debt capacity) | No standard geospatial dataset. Would be better served by a reference database or document retrieval system. | Low (not geospatial) |
| **Recreation/tourism economic data** (spending, jobs, tax revenue by region) | BEA, BLS, or state tourism office data. Partially geospatial (by county). | Medium |
| **Carbon market/pricing data** (RGGI auction results, offset prices) | Non-geospatial reference data. Better as a knowledge base than a map layer. | Low |
| **Land ownership / land cover classification** (% private, state, federal) | PAD-US already in STAC catalog (`padus-4-1/combined` with H3 hex); just needs app config. NLCD for land cover would need new processing. | **High** (PAD-US is config-only) |
| **Population projections** | State demographic center data. Not standardized. | Low |
| **Watershed boundaries** | HydroBasins already in STAC catalog with H3 hex Parquet (Level 3) and PMTiles (Level 6). Just needs app config. | Medium (config-only) |

---

## Task Category 4: Cross-Cutting Analytical Tasks

These are tasks that span all report types and represent the highest-value agent capabilities:

### District/Region Profiling Queries
- "Give me a conservation investment profile for [district/county/region]" -- combining Almanac funding, ballot measures, carbon, and SVI into a single summary
- "Which programs have invested the most in [area], by dollars and acres?"
- "How does conservation investment in [District A] compare to [District B]?"
- "What conservation sites in [district] overlap with high social vulnerability tracts?"

### Temporal Analysis
- "How has conservation spending in [county] changed over time?" (year-over-year trends)
- "What ballot measures have been on the ballot in [state] since [year]?"
- "What's the success rate of bonds vs. sales taxes vs. property taxes in [state]?"

### Spatial Overlay Analysis
- "Where are the highest-carbon areas with the least conservation protection?"
- "Show me socially vulnerable communities with conservation sites nearby"
- "Which congressional districts have the most irrecoverable carbon AND the least conservation investment?"

### Comparative Analysis
- "Rank all state senate districts in [state] by total conservation investment"
- "Which counties in [state] have never passed a conservation ballot measure?"
- "Compare carbon stocks across congressional districts in [state]"

---

## Feature Enhancements for the Geo-Agent

Beyond new data layers, these agent capabilities would help with report generation:

1. **Chart/table generation:** The agent returns text and SQL results, but reports need formatted tables and charts. A chart rendering capability (even simple bar/line charts from query results) would be transformative.

2. **Multi-query workflows:** A "district profile" command that runs a sequence of queries (Almanac summary, ballot measures, carbon overlay, SVI overlay) and assembles the results.

3. **Export capability:** Ability to export query results as CSV/JSON for further processing, or to generate formatted report sections.

4. **Geocoding/place lookup:** Convert place names ("Lake County, FL") to appropriate geographic filters without requiring the user to know FIPS codes or district identifiers.

5. **Comparative framing:** Automatically provide context (state averages, national rankings) when reporting a single jurisdiction's statistics.
