# Geo-Agent Capability Roadmap for TPL Reports

## What We Can Already Do

These tasks use only data layers already in the app and can be demonstrated today.

### 1. District-Level Conservation Investment Summaries
**Report relevance:** Core of the Legislative District Briefing; key section of Feasibility Studies

The agent can already answer:
- "Which programs and agencies have funded land conservation in FL Senate District 21, by dollars and acres?"
- "List all conservation sites in CA Congressional District 16 with their funding sources"
- "What is the total conservation investment in MN State Senate District 10?"

**How it works:** H3 hex join between `census-2025-sldu` (or `sldl`, `cd`) and `conservation-almanac-2024`, with CTE deduplication for acres. This is essentially the Florida District 21 briefing's quantitative content -- the site list, program breakdown, and totals.

**Example output equivalent:** The Florida briefing's "Total acres acquired and dollars spent in District 21 (1998-2009): 1,149 acres; $27.98 million" and the individual site listings (Pasco Palms 116 acres/$360K, Wall Springs 128 acres/$11.4M, etc.)

### 2. Ballot Measure History, Pass Rates, and Funding Analysis
**Report relevance:** District Briefings (voter support data); Feasibility Studies (state/local ballot history tables, funding mechanism analysis)

The LandVote dataset is richer than first described -- 3,886 measures (1988-2025) with `percent_yes`, `percent_no`, `finance_mechanism` (bond, property tax, sales tax, income tax, real estate transfer tax), `total_funds_at_stake`, `total_funds_approved`, `conservation_funds_at_stake`, `conservation_funds_approved`, `party` affiliation, full `description` text, jurisdiction geometries, and H3 hex index for spatial joins.

The agent can answer:
- "What is the pass rate for conservation ballot measures in Florida by mechanism type?"
- "Which ballot measures have passed in Lake County, FL?"
- "Which congressional districts have raised the most conservation funding through ballot measures?"
- "How much total conservation funding has been approved in Florida since 1996?"
- "What's the average approval percentage for bonds vs. sales taxes vs. property taxes in [state]?"
- "Show me the full ballot text for the 2004 Lake County land conservation bond"
- "What's the total dollars at stake vs. approved across all Florida measures?"
- "Do conservation measures pass more often in Democratic or Republican jurisdictions?"

**Equivalent to:** The Lake County report's "Local Conservation Finance Mechanisms in Florida" table (Bonds: 52 passed/7 failed/88%; Sales Tax: 14/8/64%; Property Tax: 11/2/85%), the Florida briefing's "73% Yes on Amendment 1 (2014)", and the feasibility study's analysis of which finance mechanisms are most successful.

### 3. Carbon Stock Analysis by Political District
**Report relevance:** Mississippi Headwaters carbon sections; any climate-focused advocacy

The agent can answer:
- "Which congressional districts in Minnesota have the most irrecoverable carbon?"
- "What is the total carbon stock across all districts in a state?"
- "Show me the carbon layer overlaid with conservation sites in the Mississippi Headwaters region"

**Equivalent to:** The Mississippi report's "Top 5 Minnesota Counties by Forest Carbon Stocks" ranking (Itasca 105M mt, Cass 61M, etc.). County boundaries are already in the STAC catalog (`census-2024/county/hex`), so this can be done at the county level too -- just not yet wired into the app's `layers-input.json`.

### 4. Conservation + Social Vulnerability Overlay
**Report relevance:** Equity framing used across all report types; increasingly important for federal grant applications

The agent can answer:
- "Show me conservation sites that overlap socially vulnerable communities using SVI"
- "Which districts have high SVI scores AND significant conservation investment?"

### 5. Multi-Funder Site Analysis
**Report relevance:** Feasibility Studies (understanding funding partnerships); District Briefings (program attribution)

The agent can answer:
- "Who funded conservation at [specific site name]? Show all sponsors and their contributions."
- "Which sites in [county/district] received funding from multiple programs?"

**Equivalent to:** Understanding that Wall Springs received $11.4M through Florida Communities Trust (state funding matched by local funding).

### 6. Interactive Map Exploration
**Report relevance:** Visual equivalent of the maps in Appendices B and C of the Lake County report

The agent can:
- Show conservation sites colored by purchase type (FSP, ESM, FNE, OTH)
- Filter ballot measures by year, status, jurisdiction type
- Overlay carbon, SVI, and political boundaries simultaneously
- Zoom to specific regions

---

## Data Already in Our STAC Catalog But Not Yet in the App

These datasets already exist in the STAC catalog at `s3-west.nrp-nautilus.io` with H3-indexed Parquet, PMTiles, and GeoParquet assets ready to go. They just need to be wired into `layers-input.json` and referenced in the system prompt.

### 7. County Boundaries (census-2024/county)
**Effort:** Config-only -- already has PMTiles (`county.pmtiles`), GeoParquet (`county.parquet`), and H3 hex Parquet (`county/hex/h0=*/data_0.parquet`) at resolution 8.

**Unlocks:** County-level versions of every district-level query above. This is critical because most feasibility studies are county-focused (Lake County, not "Congressional District 10"). Also enables the Mississippi Headwaters multi-county carbon ranking.

**Report equivalent:** The Mississippi report's county-level carbon ranking table, and all county-scoped queries in the Lake County feasibility study.

### 8. Census Tract Boundaries (census-2024/tract)
**Effort:** Config-only -- already has PMTiles (`tract.pmtiles`), GeoParquet (`tract.parquet`), and H3 hex Parquet (`tract/hex/`) at resolution 10. ~85,000 tracts.

**Unlocks:** Fine-grained spatial analysis. Combined with SVI (which is already at tract level), enables precise equity analysis: "which census tracts in Lake County are both socially vulnerable AND lack conservation investment?"

### 9. State Boundaries (census-2024/state)
**Effort:** Config-only -- PMTiles and GeoParquet for all 56 states/territories.

**Unlocks:** Clean state outlines for framing, statewide aggregations.

### 10. PAD-US 4.1 (Protected Areas Database of the US)
**Effort:** Config-only -- already has PMTiles (`combined.pmtiles`), GeoParquet (`combined.parquet`), and H3 hex Parquet (`combined/hex/h0=*/data_0.parquet`). 656,986 protected areas with ownership type (federal, state, tribal, local, NGO, private), GAP status, IUCN classification, stewardship, and access info.

**Unlocks:**
- Land ownership breakdown ("44% private, 36.1% state, 18% federal" as in the Mississippi report)
- Gap analysis: "What areas are NOT yet protected?"
- Complete picture of ALL protected lands beyond TPL's Almanac (federal lands, state parks, easements)
- Overlap analysis: conservation investment (Almanac) vs. protection status (PAD-US)

**Report equivalent:** The Mississippi report's land ownership breakdown and any analysis of existing conservation coverage.

### 11. HydroBasins (Global Watershed Boundaries)
**Effort:** Config-only -- Level 6 PMTiles for visualization, Levels 1/3/4 as GeoParquet, Level 3 as H3 hex Parquet.

**Unlocks:** Watershed-scoped queries ("all conservation investment in the Mississippi Headwaters watershed"), water-resource-based analysis, more natural geographic units for regional studies.

**Report equivalent:** The Mississippi report's watershed-based geographic framing.

### 12. Other Catalog Collections Potentially Relevant
Several other collections in the STAC catalog could support TPL reports:
- **MOBI Species Richness** -- biodiversity justification for conservation
- **Mapping Inequality (Historical Redlining)** -- historical equity context
- **IUCN Species Richness** -- endangered species overlap with conservation areas
- **Ecoregions (WWF)** -- ecological context for regional studies
- **NCP (Nature's Contributions to People)** -- ecosystem services valuation

---

## What We Could Add with Moderate Effort

These require new data processing but use publicly available sources.

### 13. US Census Demographics (ACS Data)
**Effort:** Medium -- ACS 5-year estimates are available as tables; could be joined to county/tract geometries and hex-indexed.

**Key variables:** Population, race/ethnicity, median household income, median home value, poverty rate, owner-occupied housing rate, educational attainment.

**Unlocks:**
- Auto-generate the demographics table from the Lake County report (population 383,956, 82% White, median home value $223K, etc.)
- Demographic comparisons: county vs. state
- Income/housing data needed for bond cost-per-homeowner calculations

**Report equivalent:** The entire "Demographics" section (p. 7) of the Lake County report.

### 14. NLCD Land Use / Land Cover (and Change Detection)
**Effort:** Medium-High -- NLCD is a 30m raster from USGS, available for multiple epochs (2001-2021). Could be processed to H3 hex with land cover class and change metrics.

**Unlocks:**
- "100,000 acres converted to development from 2007-2012" statistics
- "250,000 acres converted to cropland"
- Developed land vs. population growth trends
- Identification of areas at risk of conversion

**Report equivalent:** The Mississippi report's land conversion charts (p. 14) showing developed land growth from 5% to 41%.

### 15. Florida Wildlife Corridor / State Ecological Networks
**Effort:** Medium -- State-specific datasets (Florida FEGN, state wildlife action plans). Would need to be sourced per state.

**Unlocks:**
- "112,651 acres are Opportunity Areas in the Florida Wildlife Corridor" type statistics
- Overlap analysis between corridor opportunity areas and existing conservation

**Report equivalent:** Lake County report's Florida Wildlife Corridor section and Appendix C map.

---

## What Would Be a Reach

These are either technically challenging, require non-geospatial data integration, or depend on data that isn't readily available in a standardized format.

### 16. County Financial Data (CAFR/Budget)
**Challenge:** No standardized national dataset of county revenues, expenditures, debt, or millage rates. Each county publishes its own CAFR in different formats.

**Possible approaches:**
- Census of Governments (Census Bureau) has some standardized fiscal data, but it's lagged and limited
- Could potentially partner with a fiscal data aggregator
- More realistically, this stays as manual research that the agent can't automate

**Report equivalent:** The entire "Finances" section of the Lake County report ($415.4M revenues, millage rate tables, debt schedules).

### 17. Bond Cost Calculator Tool
**Challenge:** Not a data layer problem -- needs a computational tool. Given total taxable value, interest rate, maturity, and bond amount, compute annual debt service and cost per homeowner.

**Possible approach:** Could be implemented as a custom MCP tool or as a SQL UDF in DuckDB. The math is straightforward (standard amortization formula). Would need taxable value data (from census or property appraiser).

**Report equivalent:** The Lake County bond financing estimates table ($50M at 5% for 20yr = $4M annual debt service = $21/year per homeowner).

### 18. Election / Voter Turnout Data
**Challenge:** No national standardized dataset. Each state/county Supervisor of Elections publishes differently.

**Possible approach:** MIT Election Data + Science Lab has some standardized election data. Could supplement with state-specific sources.

**Report equivalent:** The Lake County voter turnout table (Nov-22: 58%, Nov-20: 80%).

### 19. State Budget and Tax Revenue Data
**Challenge:** Non-geospatial data. State budget documents vary enormously in format.

**Possible approach:** Census Bureau's Annual Survey of State Government Finances has standardized data. Could be loaded as a reference table (not spatial).

**Report equivalent:** The Mississippi report's state budget pie charts and tax revenue analysis.

### 20. Recreation and Tourism Economic Data
**Challenge:** Multiple sources (BEA, BLS, Outdoor Industry Association, state tourism offices) with different methodologies and granularities.

**Possible approach:** BEA's Outdoor Recreation Satellite Account provides state-level data. County-level requires more specialized sources.

**Report equivalent:** The Mississippi report's recreation economy section ($16.7B, 140,000 jobs).

### 21. Water Quality Trend Data
**Challenge:** EPA Water Quality Portal (WQX) data is voluminous and requires significant processing. Time-series analysis is complex.

**Possible approach:** Could pre-compute watershed-level water quality summaries. HUC-indexed Parquet with annual nutrient loading estimates.

**Report equivalent:** The Mississippi report's nitrogen load trend chart.

### 22. Carbon Equivalency and Dollar Valuation
**Challenge:** Converting metric tons of carbon to dollar values (social cost of carbon), gasoline equivalents, homes' energy use, etc. These are computational transformations, not data layers.

**Possible approach:** Add conversion factors as constants in the system prompt or as a lookup table. Agent could compute: total_carbon * $44/ton = social_value.

**Report equivalent:** The Mississippi Forest Carbon Map infographic ($18.3B social value, $22.2B market value, 172B gallons gasoline equivalent).

### 23. Document/Report Generation
**Challenge:** The agent returns conversational text and query results. Producing formatted PDFs with charts, tables, maps, and branding is a fundamentally different capability.

**Possible approaches:**
- Export query results + map screenshots for assembly in external tools
- Integration with a report template engine (e.g., Quarto, LaTeX)
- This is likely out of scope for the geo-agent itself

---

## Recommended Priority Order

### Phase 1: Config-only -- wire existing STAC data into the app (days)
These datasets already exist in our STAC catalog with H3 hex Parquet, PMTiles, and GeoParquet. They just need entries in `layers-input.json` and references in the system prompt.

1. **County boundaries** (`census-2024/county`) -- unlocks county-scoped versions of all existing queries; most feasibility studies are county-focused
2. **State boundaries** (`census-2024/state`) -- clean state outlines, statewide aggregations
3. **Census tract boundaries** (`census-2024/tract`) -- fine-grained equity analysis with SVI
4. **PAD-US protected areas** (`padus-4-1/combined`) -- 656K protected areas with ownership, GAP status, IUCN class; completes the conservation land picture
5. **HydroBasins** (`hydrobasins`) -- watershed-scoped analysis for regional studies
6. **Carbon dollar-value conversion factors** in system prompt -- enables "social value of carbon" answers
7. **Demo district briefing workflow** -- show TPL that the agent can already produce the quantitative backbone of their most common report type

### Phase 2: New data processing (1-2 months)
8. **US Census ACS demographics** as H3-indexed Parquet -- enables demographic profiling (population, income, housing, education)
9. **NLCD land cover/change** -- enables land conversion trend analysis
10. **Legislator lookup table** -- maps district GEOIDs to current officeholders

### Phase 3: Advanced capabilities (3-6 months)
11. **Bond cost calculator** as a custom tool or SQL function
12. **Chart generation** from query results
13. **Multi-query "profile" workflows** that assemble multiple analyses into a structured summary
14. **State-specific ecological priority layers** (Florida Wildlife Corridor, etc.)

### Phase 4: Stretch goals (6+ months)
15. Census of Governments fiscal data
16. Water quality trend data (EPA WQX)
17. Recreation economy data (BEA ORSA)
18. Report template generation / PDF export

---

## Summary

The geo-agent is **already well-positioned** to produce the quantitative core of TPL's Legislative District Briefings -- conservation site listings, program breakdowns, funding totals, and ballot measure history for any state senate, assembly, or congressional district in the US. This should be demonstrated to TPL as a quick win.

A large number of additional datasets are **already in our STAC catalog** and just need to be wired into the app config: county/tract/state boundaries, PAD-US (656K protected areas with ownership data), and HydroBasins watershed boundaries. These are config-only changes that dramatically expand what the agent can do.

The **biggest remaining gaps** for feasibility studies are: (a) Census ACS demographics, (b) NLCD land cover change data, and (c) county fiscal/financial data. The first two are solvable with publicly available datasets. The third is inherently difficult due to lack of standardized national data.

The **climate/carbon analysis** capabilities are already strong and differentiate this tool from what TPL could do manually. Adding county boundaries (already in STAC) makes the carbon-by-county analysis a direct equivalent of the Mississippi Headwaters Forest Carbon Map.

The agent's greatest long-term value to TPL is **speed and consistency**: what currently takes an analyst days of manual data gathering, querying, and formatting could be reduced to a conversation.
