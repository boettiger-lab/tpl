# TPL App — Example Query Answers

Each example query from the welcome screen, with expected tool calls and answers.

---

## Q1: Austin's 30-year conservation bond campaign

> *"Which federal programs have matched Austin's conservation bond funds in Travis County, TX, and how many acres have been protected?"*

**Expected tool calls: ~7**
`get_dataset` ×2 (landvote, conservation-almanac) · `query` ×2 · `zoom_to` · `toggle_layer` · `set_filter`

### Ballot measures by decade — Travis County, TX

| Decade | Measures | Passed | Approved ($M) |
|--------|----------|--------|---------------|
| 1990s  | 7        | 6      | $167M         |
| 2000s  | 9        | 9      | $194M         |
| 2010s  | 5        | 5      | $347M         |
| 2020s  | 2        | 2      | $206M         |
| **Total** | **23** | **22** | **$914M** |

### Conservation Almanac sites funded in Travis County

| Program | Sites | Avg acres | Active |
|---------|-------|-----------|--------|
| Bond Funds | 20 | 270 ac | 1998–2008 |
| Land and Water Conservation Fund (LWCF) | 8 | 299 ac | 1999–2008 |
| General Appropriations | 2 | 22 ac | 2004 |

**Story:** Austin voters have passed conservation bonds in every decade since 1992 — 22 of 23 measures approved. Those bond dollars unlocked federal LWCF matching funds, together protecting 28 sites including multiple parcels of the Balcones Canyonlands National Wildlife Refuge.

---

## Q2: King County, WA — conservation investment growth

> *"How has conservation investment grown in King County, WA from 2007 to the 2025 measure — and what new priorities appeared?"*

**Expected tool calls: ~4**
`get_dataset` · `query` · `zoom_to` · `set_filter`

### All passed measures, King County WA

| Year | Jurisdiction | Approved ($M) | Notes |
|------|-------------|---------------|-------|
| 1988 | Issaquah | $0.6M | |
| 1989 | (county) | $117.6M | |
| 2000 | Seattle | $31.0M | |
| 2006–2008 | Shoreline, Issaquah, Bellevue, Seattle | $76.2M | |
| 2007 | (county) | $84.0M | |
| 2012–2014 | Kirkland, Issaquah, Seattle Park District | $85.7M | |
| 2019 | (county) | $145.5M | |
| 2022 | Bellevue + (county) | $470.0M | |
| **2025** | **(county)** | **$625.3M** | **First to name equity + climate** |

**Total: $1.64B across 18 measures**

**Story:** Conservation investment in King County has grown 7× in under 20 years — from $84M in 2007 to $625M in 2025. The 2025 measure is the first to explicitly name equity and climate resilience alongside the traditional open space and trails priorities, signaling a new template for Pacific Northwest campaigns.

---

## Q3: Florida watershed protection wave (2020–2024)

> *"Which Florida counties passed conservation funding for watershed protection between 2020 and 2024, and how much did each approve?"*

**Expected tool calls: ~4**
`get_dataset` · `query` · `zoom_to` · `set_filter`

### Florida watershed measures, 2020–2024 (all passed)

| County | Year | Mechanism | Approved ($M) |
|--------|------|-----------|---------------|
| Collier County | 2020 | Property tax | $287M |
| Alachua County | 2022 | Sales tax | $246M |
| Polk County | 2022 | Property tax | $200M |
| Martin County | 2024 | Sales tax | $183M |
| Brevard County | 2022 | Property tax | $159M |
| Volusia County | 2020 | Property tax | $147M |
| Pasco County | 2022 | Sales tax | $140M |
| Manatee County | 2020 | Property tax | $108M |
| Osceola County | 2024 | Bond | $70M |
| Indian River County | 2022 | Bond | $50M |
| Lake County | 2024 | Bond | $50M |
| Clay County | 2024 | Bond | $45M |
| Nassau County | 2022 | Bond | $30M |
| **Total** | | | **$1.71B** |

**Story:** 13 Florida counties approved $1.71B for watershed protection in just four years — every single measure passed. Florida's statewide conservation ballot pass rate since 2010 is 93%, the highest of any large state. This pattern spans the state from the Panhandle (Nassau) to the Keys corridor (Collier), spanning both red and blue counties.

---

## Q4: Colorado's conservation sales tax surge

> *"Which Colorado counties are driving the conservation surge since 2020 — from Colorado Springs to Fort Collins to Durango?"*

**Expected tool calls: ~4**
`get_dataset` · `query` · `zoom_to` · `set_filter`

### Colorado passed measures, 2020–2025

| County | Jurisdiction | Year | Approved ($M) | Mechanism |
|--------|-------------|------|---------------|-----------|
| Adams County | (county) | 2020 | $200M | Sales tax |
| Larimer County | Fort Collins | 2025 | $181M | Sales tax |
| Boulder County | (county) | 2025 | $150M | Sales tax |
| El Paso County | Colorado Springs | 2023 | $144M | Sales tax |
| Arapahoe County | (county) | 2021 | $112M | Sales tax |
| Douglas County | (county) | 2022 | $109M | Sales tax |
| Boulder County | Longmont | 2024 | $100M | Sales tax |
| Weld County | Longmont | 2024 | $100M | Sales tax |
| La Plata County | Durango | 2025 | $90M | Sales tax |
| Grand County | (county) | 2023 | $67M | Sales tax |
| Boulder County | (county) | 2023 | $54M | Sales tax |
| Jefferson County | Lakewood | 2024 | $54M | Other |
| *(8 smaller measures)* | | 2020–2022 | $176M | Mixed |
| **Total** | | | **$1.54B** | |

**Story:** Colorado has passed $1.54B in conservation funding since 2020, almost entirely through sales taxes — a broadly popular mechanism that has won in every corner of the state, from mountain resort towns (Aspen, Durango) to Front Range suburbs (Fort Collins, Colorado Springs, Longmont). Colorado Springs' 2023 passage is notable: voters rejected the same measure in 2021, then came back and approved $144M two years later.

---

## Q5: Monmouth County, NJ — conservation investment and social vulnerability

> *"Are Monmouth County, NJ's conservation investments reaching vulnerable coastal communities? Show ballot measures alongside social vulnerability scores."*

**Expected tool calls: ~6**
`get_dataset` ×2 (landvote, svi-2022) · `query` ×2 · `zoom_to` · `toggle_layer`

### Monmouth County ballot measures since 2017 (all passed, all property tax)

| Year | Jurisdiction | Approved ($M) | Purpose |
|------|-------------|---------------|---------|
| 2025 | (county) | $253.8M | Open space, farmland, watershed protection |
| 2025 | Manasquan Borough | $8.3M | Open space, recreation |
| 2025 | Little Silver Borough | $2.3M | Open space, farmland, recreation |
| 2024 | Middletown Township | $30.2M | Watershed protection, farmland |
| 2024 | Wall Township | $17.0M | Farmland, recreation |
| 2024 | Atlantic Highlands Borough | $2.1M | Open space, parks |
| 2023 | Howell Township | $16.9M | Open space, farmland |
| 2023 | Colts Neck Township | $8.6M | Open space, farmland |
| 2022 | Freehold Township | $13.7M | Open space, farmland, watershed |
| 2021 | Holmdel Township | $8.6M | Open space, farmland |
| 2020 | Middletown Township | $22.7M | Open space, farmland, floodplain |
| 2017 | (county) | $280.0M | Open space, parks, watershed, farmland |
| 2017 | Ocean Township | $8.4M | Open space, parks |
| **Total** | | **$673M** | |

### Monmouth County SVI (2022, county level)

| Overall SVI | Socioeconomic | Household | Minority Status | Housing/Transport |
|-------------|---------------|-----------|-----------------|-------------------|
| 0.21 (low) | 0.20 | 0.13 | **0.62** | 0.33 |

**Story:** Monmouth County voters have passed conservation measures every single year since 2017 — $673M total, all via property tax. The county's overall SVI of 0.21 looks low, but the minority status sub-score of 0.62 reveals significant underlying disparity. Toggling to the tract-level SVI layer surfaces which specific townships have high vulnerability — a critical question for whether farmland and open space investments are landing near the communities most exposed to coastal flooding and development pressure.
