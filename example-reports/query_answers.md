# TPL App — Example Query Answers

Each example query from the welcome screen, with expected tool calls and answers.

---

## Q1: Charlotte County, Florida — conservation sites and programs

> *"What conservation sites have been protected in Charlotte County, Florida, and which programs funded them?"*

**Expected tool calls: ~4**
`get_dataset` (almanac) · `query` · `zoom_to` · `toggle_layer`

### Conservation Almanac sites — Charlotte County, FL

| Site | Acres | Year | Program | Type |
|------|-------|------|---------|------|
| Babcock Ranch - MSKP III Inc. | 67,619 | 2006 | Florida Forever | Fee simple |
| Prairie Creek Preserve | 1,603 | 2008 | Conservation Charlotte Program | Fee simple |
| Charlotte Harbor Flatwoods - Bond | 669 | 2015 | Florida Forever | Fee simple |
| Charlotte Flatwoods Environmental Park | 483 | 1998 | General capital funds / Florida Forever | Fee simple |
| Deep Creek Preserve | 450 | 2008 | Conservation Charlotte Program | Fee simple |
| Shell Creek Preserve | 373 | 2008 | Conservation Charlotte Program | Fee simple |
| Biscayne Trust Conservation Easement | 178 | 2004 | Donation | Easement |

### Programs summary

| Program | Sites | Total acres |
|---------|-------|-------------|
| Florida Forever | 27 | 70,506 |
| Conservation Charlotte Program | 5 | 2,530 |
| General capital funds | 6 | 1,231 |
| FL Communities Trust | 8 | 211 |

**Answer:** Charlotte County's conservation portfolio is overwhelmingly shaped by one program: Florida Forever, which funded 70,506 acres including the massive Babcock Ranch acquisition in 2006. A local program — Conservation Charlotte — added preserves at Prairie Creek, Deep Creek, and Shell Creek. The 40 sites span 1998 to 2020.

---

## Q2: Haywood County, North Carolina — carbon and conserved land

> *"Where does irrecoverable carbon overlap with conserved land in Haywood County, North Carolina?"*

**Expected tool calls: ~6**
`get_dataset` ×2 (almanac, carbon) · `query` · `zoom_to` · `toggle_layer` ×2

### Conservation Almanac sites — Haywood County, NC (Blue Ridge)

| Site | Acres | Year | Program | Type |
|------|-------|------|---------|------|
| Allens Creek - Waynesville Watershed | 7,348 | 2005 | NC Land and Water Fund | Easement |
| NC Wildlife Resources / Lake Logan | 4,374 | 1999 | Clean Water Management Trust Fund | Fee simple |
| Lake Logan | 3,251 | 2000 | NC Land and Water Fund | Easement |
| Rough Creek Watershed | 874 | 2003 | NC Land and Water Fund | Easement |
| Indian Creek | 775 | 2017 | NC Land and Water Fund | Easement |
| Conservation Fund (PSG1001) | 608 | 2002 | LWCF | Fee simple (federal) |
| Carpenter Branch - Sheepback Mt | 565 | 2017 | NC Land and Water Fund | Easement |

35 sites · 22,359 acres · 6 programs · Active 1999–2021

**Answer:** Haywood County sits in the southern Appalachians where the carbon raster shows dense irrecoverable carbon in the forested mountain slopes. Toggling both layers reveals strong overlap — the NC Land and Water Fund (the dominant program here) has protected large watershed easements in exactly the carbon-rich forested headwaters. The Allens Creek and Lake Logan acquisitions alone cover 15,000 acres of high-carbon Blue Ridge forest. Federal LWCF and Clean Water Trust matching dollars amplify the state investment.

---

## Q3: Chester County, Pennsylvania — programs and largest sites

> *"What programs have funded the largest conservation sites in Chester County, Pennsylvania?"*

**Expected tool calls: ~4**
`get_dataset` (almanac) · `query` · `zoom_to` · `toggle_layer`

### Largest conservation sites — Chester County, PA

| Site | Acres | Year | Program | Type |
|------|-------|------|---------|------|
| Springlawn Corridor | 731 | 2009 | Bond Funds | Fee simple |
| Paradise Farms Easement | 341 | 2004 | Bond Funds + Growing Greener | Easement |
| (parcel 3246) | 325 | 2007 | Farmland Preservation Program | Easement |
| (parcel 3349) | 268 | 2007 | Farmland Preservation Program | Easement |
| Sonoco Property | 238 | 2006 | Bond Funds | Fee simple |
| Unionville Barrens | 195 | 2008 | Growing Greener | Fee simple |

### Programs summary

377 sites · 19,770 acres · 8 programs

| Program | Role |
|---------|------|
| Bond Funds | Largest fee-simple purchases (Springlawn, Sonoco) |
| Growing Greener (Environmental Stewardship Fund) | State match for local acquisitions and easements |
| Farmland Preservation Program | Conservation easements on working farms |
| LWCF | Federal match for key parcels |

**Answer:** Chester County's 377 conservation sites are funded through a mix of local bond money, Pennsylvania's Growing Greener state fund, and the Farmland Preservation Program. The largest sites (Springlawn Corridor, Paradise Farms) used bond funds, often layered with Growing Greener matching grants. The county's distinctive pattern is farmland easements — the Farmland Preservation Program protects working agricultural land through purchased development rights, a different model from the fee-simple purchases that dominate in Florida.

---

## Q4: Colorado conservation funding since 2020

> *"Which Colorado counties have passed the most conservation funding since 2020?"*

**Expected tool calls: ~4**
`get_dataset` (landvote) · `query` · `zoom_to` · `set_filter`

### All passed measures, Colorado 2020–2025

| County | Jurisdiction | Year | Approved ($M) | Mechanism |
|--------|-------------|------|---------------|-----------|
| Adams County | (county) | 2020 | $200M | Sales tax |
| Larimer County | Fort Collins | 2025 | $181M | Sales tax |
| Boulder County | (county) | 2025 | $150M | Sales tax |
| El Paso County | Colorado Springs | 2023 | $144M | Sales tax |
| Arapahoe County | (county) | 2021 | $112M | Sales tax |
| Douglas County | (county) | 2022 | $109M | Sales tax |
| Boulder / Weld | Longmont | 2024 | $100M each | Sales tax |
| La Plata County | Durango | 2025 | $90M | Sales tax |
| Grand County | (county) | 2023 | $67M | Sales tax |
| *(14 smaller measures)* | | 2020–2025 | $284M | Mixed |

**Total: $1.54B across 24 measures**

**Answer:** 24 Colorado conservation measures have passed since 2020, totaling $1.54B — almost entirely through sales taxes. Adams County leads ($200M), followed by Larimer/Fort Collins ($181M), Boulder ($150M), and El Paso/Colorado Springs ($144M). The Colorado Springs passage in 2023 is notable: voters rejected the same measure in 2021 and came back to approve it two years later.

---

## Q5: Monmouth County, NJ — conservation and social vulnerability

> *"Are Monmouth County, NJ's conservation investments reaching vulnerable coastal communities? Show ballot measures alongside social vulnerability scores."*

**Expected tool calls: ~6**
`get_dataset` ×2 (landvote, svi-2022) · `query` ×2 · `zoom_to` · `toggle_layer`

### Passed ballot measures since 2017 (all property tax)

| Year | Jurisdiction | Approved ($M) | Purpose |
|------|-------------|---------------|---------|
| 2025 | (county) | $253.8M | Open space, farmland, watershed protection |
| 2025 | Manasquan Borough | $8.3M | Open space, recreation |
| 2025 | Little Silver Borough | $2.3M | Open space, farmland |
| 2024 | Middletown Township | $30.2M | Watershed protection, farmland |
| 2024 | Wall Township | $17.0M | Farmland, recreation |
| 2023 | Howell Township | $16.9M | Open space, farmland |
| 2023 | Colts Neck Township | $8.6M | Open space, farmland |
| 2022 | Freehold Township | $13.7M | Open space, farmland, watershed |
| 2021 | Holmdel Township | $8.6M | Open space, watershed, farmland |
| 2020 | Middletown Township | $22.7M | Open space, floodplain protection |
| 2017 | (county) | $280.0M | Open space, parks, watershed, farmland |
| 2017 | Ocean Township | $8.4M | Open space, parks |

**Total since 2017: $673M across 13 measures**

### SVI — Monmouth County (county level)

| Overall SVI | Socioeconomic | Household | Minority Status | Housing/Transport |
|-------------|---------------|-----------|-----------------|-------------------|
| 0.21 (low) | 0.20 | 0.13 | **0.62** | 0.33 |

**Answer:** Monmouth County has passed conservation measures every single year since 2017 — $673M total, all via property tax. The county's overall SVI of 0.21 is low, but the minority status sub-score of 0.62 reveals significant underlying disparity. Switching to the tract-level SVI layer shows where high-vulnerability communities are located within the county — the key question is whether the township-level investments (Middletown, Freehold, Howell) are landing near those tracts or concentrating in lower-vulnerability areas.
