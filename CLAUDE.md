# US Energy Data Platform

## Project Overview
Public-facing data platform making US energy data accessible. Based on Hannah Ritchie's proposal (Feb 2026). Phase 1: $200K / 6 months.

## Tech Stack
- **Frontend**: SvelteKit 5 + TypeScript + Tailwind CSS v4 + Cloudflare adapter
- **Charts**: D3 (d3-scale, d3-shape, d3-geo, d3-array, d3-format, d3-interpolate) + Svelte reactive SVG
- **Maps**: d3-geo + topojson-client + us-atlas (AlbersUSA projection)
- **Typography**: Google Fonts — Instrument Serif (display), DM Sans (body), JetBrains Mono (mono)
- **Data Pipeline**: Python (requests + pandas) → static JSON → site/static/data/
- **Hosting**: Cloudflare Pages (free tier)
- **CI/CD**: GitHub Actions (build + scheduled weekly EIA data updates)

## Repository Structure
```
us-energy-data/
├── pipeline/              # Python data pipeline (venv in .venv/)
│   ├── src/fetch/         # EIA API fetchers (electricity.py, fuels.py)
│   ├── src/transform/     # Data cleaning → chart-ready JSON (prices, demand, generation, fuels, reliability)
│   ├── src/export.py      # Write JSON to site/static/data/
│   └── src/main.py        # Entry point — runs all 5 pipelines
├── site/                  # SvelteKit frontend
│   ├── src/lib/components/charts/  # LineChart, BarChart, Scatter, ChoroplethMap, ChartWrapper, Tooltip
│   ├── src/lib/components/ui/      # Dropdown
│   ├── src/lib/components/layout/  # Nav, Footer
│   ├── src/lib/stores/chartConfig.ts  # URL ↔ chart state sync
│   ├── src/lib/utils/     # colors, formatting, download helpers, states (FIPS mapping)
│   ├── src/lib/types/     # chart.ts, data.ts
│   └── src/routes/        # Homepage + 5 topic pages with +page.ts loaders
│       ├── prices/        # LineChart (national trends) + ChoroplethMap (state prices)
│       ├── demand/        # LineChart (consumption trends) + BarChart (top 10 states)
│       ├── generation/    # BarChart (by source) + LineChart (share trends) + ChoroplethMap (renewable share)
│       ├── fuels/         # LineChart (production trends) + BarChart (top producing states)
│       └── reliability/   # LineChart (SAIDI trend) + Scatter (SAIDI vs SAIFI) [sample data]
├── .env                   # EIA_API_KEY (not committed)
└── .env.example           # EIA_API_KEY placeholder
```

## Current Status: Sprint 2 Complete (Design Overhaul)
### Sprint 0 (scaffold)
- [x] Git repo + monorepo structure
- [x] SvelteKit project scaffolded, builds successfully
- [x] Tailwind CSS v4 with custom design tokens
- [x] 4 chart components: LineChart, BarChart, Scatter, ChoroplethMap
- [x] ChartWrapper with title, source link, CSV/PNG download, responsive container
- [x] URL state management store (chartConfig.ts)
- [x] Responsive nav with mobile hamburger menu
- [x] Homepage with 5 section cards

### Sprint 1 (real data + all pages)
- [x] EIA API key configured
- [x] Python venv setup (pipeline/.venv/)
- [x] 5 data pipelines: prices, demand, generation, fuels, reliability
- [x] 17 JSON data files generated in site/static/data/
- [x] Prices page: real EIA data, line chart + state choropleth map
- [x] Demand page: consumption line chart + top 10 states bar chart
- [x] Generation page: source bar chart + share trend lines + renewable share map
- [x] Fuels page: production trends + top producing states
- [x] Reliability page: SAIDI trend + SAIDI vs SAIFI scatter (sample data)
- [x] +page.ts data loaders for all 5 pages
- [x] us-atlas TopoJSON for ChoroplethMap (states-10m.json)
- [x] Compact SI number formatting (formatCompact) for large axis values
- [x] Production build passes (Cloudflare adapter)

### Sprint 2 (design overhaul)
- [x] Brand identity: deep navy (#0f2b44) + warm orange (#e86c3a) + off-white (#fafaf8) palette
- [x] Typography: Instrument Serif (headlines), DM Sans (body), JetBrains Mono (data) via Google Fonts
- [x] Dark navy Nav with serif site name, pill-shaped active states
- [x] 3-column navy Footer with brand tagline, section nav, about links
- [x] Homepage hero: serif headline "Understanding America's Energy" + 3 key stats in accent orange
- [x] Homepage cards: color-coded left borders, SVG icons, hover lift animation
- [x] LineChart: end-of-line labels, hover crosshair + dots, improved axes (13px, warmer colors)
- [x] BarChart: hover dimming, multi-color legend, crisp edges, improved axes
- [x] Scatter: hover point enlargement + label, white stroke separation, improved axes
- [x] ChoroplethMap: state abbreviation labels, cream-to-navy color scale (d3-interpolate), centered legend with "No data" swatch, hover borders
- [x] ChartWrapper: serif chart titles, styled CSV/PNG icon buttons
- [x] Dropdown: custom-styled select with chevron icon, accent focus ring
- [x] Tooltip: boundary detection (flips when near edge), fade-slide entrance transition
- [x] Fuels page: indexed Y-axis (base year = 100) for "All Fuels" cross-fuel comparison
- [x] All topic pages: palette migrated from Tailwind gray defaults to brand token classes
- [x] Page transitions: fade on route change via {#key} block
- [x] Dark mode: CSS custom property overrides via prefers-color-scheme media query
- [x] Rotated Y-axis labels removed from all chart types (units in subtitle instead)
- [x] FIPS_TO_ABBR mapping added to utils/states.ts
- [x] Production build passes (Cloudflare adapter)

## Next: Sprint 3 — Full Proposal Coverage
Goal: close all remaining gaps against the Hannah Ritchie proposal (Feb 2026).
Reference: `/Users/skarl/Desktop/Data Explorer Hannah /US Energy Data Platform Proposal (HR, Feb2026).docx`

### 3a. Missing Charts — Prices & Bills (2 new charts)
- [ ] Household electricity bills: nominal + inflation-adjusted (line chart). Pipeline: multiply avg price × avg consumption from EIA retail-sales data; CPI adjustment via BLS API or static CPI table.
- [ ] Prices vs. electricity mix scatter: state-level scatterplot (x = renewable share or fuel mix metric, y = avg retail price). Data: join state prices with state generation mix.

### 3b. Missing Charts — Electricity Demand (2 new charts)
- [ ] Per-capita electricity demand (line chart). Pipeline: Census population data (annual state estimates) → divide total consumption by population. Toggle: national + state-level.
- [ ] Load growth (line chart or bar chart). Pipeline: year-over-year % change in total consumption. National + state-level.

### 3c. Missing Charts — Generation & Resources (5 new charts)
- [ ] Carbon intensity of electricity (line chart). Pipeline: EIA CO2 emissions from electricity generation ÷ total generation (kg CO2/MWh). API: `/electricity/electric-power-operational-data/data` with data[]=co2-emissions or `/environment/` endpoints.
- [ ] Installed capacity by source (bar chart, horizontal). Pipeline: EIA capacity data → `/electricity/operating-generator-capacity/data`. Grouped by fuel type.
- [ ] Capacity additions and retirements over time (stacked bar or grouped bar). Pipeline: EIA planned/retired generators data. Positive bars = additions, negative = retirements, grouped by fuel type.
- [ ] Energy storage capacity and deployment (line or bar chart). Pipeline: EIA battery storage data → `/electricity/operating-generator-capacity/data` filtered to battery storage.
- [ ] Capacity factors by technology over time (line chart). Pipeline: generation ÷ (capacity × 8760 hours). Per source: wind, solar, nuclear, gas, coal.

### 3d. Missing Charts — Fossil Fuels (2 new charts)
- [ ] Fuel consumption for power generation (line chart). Pipeline: EIA `/electricity/electric-power-operational-data/data` with data[]=consumption-for-eg. By fuel type over time.
- [ ] Imports and exports (line or grouped bar). Pipeline: EIA petroleum imports/exports + natural gas trade data. Show net position over time.

### 3e. Missing Charts — Reliability (1 new chart + real data)
- [ ] Real FERC/EIA-861 reliability data: replace sample SAIDI/SAIFI with actual EIA-861 reliability metrics. Source: EIA-861 annual electric power industry report or IEEE 1366 data.
- [ ] Reliability vs. prices/load/mix scatter: state-level scatterplot (x = SAIDI or SAIFI, y = avg price or renewable share). Exploratory cross-cutting analysis.

### 3f. Interactivity — State Multi-Select
- [ ] State-level multi-select toggling for line charts: allow users to add/remove specific states (e.g., TX, CA, NY) as overlaid series on any line chart. Dropdown or search-select UI component. URL state preserved (e.g., `?states=TX,CA,NY`).
- [ ] State comparison across all sections: prices, demand, generation share, fuel production where state data exists.

### 3g. Chart Annotations & Context
- [ ] Each chart accompanied by concise explanatory text: "What is being shown? Why does it matter? Key caveats?" (per proposal). Audit all existing charts for completeness; add missing context.
- [ ] Definitions and units documented at chart level (tooltip or expandable info icon).
- [ ] Methodological notes where relevant (e.g., CPI adjustment method, capacity factor calculation).

### 3h. Infrastructure & Reliability
- [ ] GitHub Actions CI: automated build on push, deploy to Cloudflare Pages.
- [ ] Scheduled weekly data updates: GitHub Actions cron job runs pipeline, commits new JSON, triggers rebuild.
- [ ] Data archiving: snapshot all source data in repo (or separate storage) to protect against federal API changes/retraction. Pipeline should cache raw API responses.
- [ ] Responsive chart width: pass ResizeObserver width from ChartWrapper to chart components so tick density adapts to screen size.
- [ ] Homepage hero stats pulled dynamically from data JSON files (not hardcoded).

### 3i. Responsive & Cross-Browser Testing
- [ ] Mobile layout testing: nav hamburger, chart readability, tooltip usability, map zoom/pan on touch.
- [ ] Tablet layout testing: chart sizing, card grid, dropdown usability.
- [ ] Cross-browser testing: Chrome, Safari, Firefox, Edge.
- [ ] Accessibility: ARIA labels on chart SVGs, keyboard navigation for dropdowns/toggles, screen reader support for chart data.

### 3j. Data Sources to Add (Pipeline Expansion)
New EIA API endpoints needed:
- [ ] CO2 emissions: `/electricity/electric-power-operational-data/data` (data[]=co2-emissions) or `/environment/` endpoints
- [ ] Capacity: `/electricity/operating-generator-capacity/data`
- [ ] Battery storage: same capacity endpoint filtered to energy_source_code=BA
- [ ] Fuel consumption for generation: `/electricity/electric-power-operational-data/data` (data[]=consumption-for-eg)
- [ ] Petroleum trade: `/petroleum/move/imp/data` and `/petroleum/move/exp/data`
- [ ] Natural gas trade: `/natural-gas/move/` endpoints
- [ ] Census population: Census Bureau API (annual state population estimates)
- [ ] CPI data: BLS API or static CPI-U annual table for inflation adjustment
- [ ] EIA-861 reliability: download and parse annual EIA-861 CSV files

### Sprint 3 Chart Inventory (when complete)
| Section | Charts (current) | Charts (target) | New |
|---|---|---|---|
| Prices & Bills | 2 | 4 | +2 |
| Electricity Demand | 2 | 4 | +2 |
| Generation & Resources | 3 | 8 | +5 |
| Fossil Fuels | 2 | 4 | +2 |
| Reliability & Outages | 2 | 4 | +2 |
| **Total** | **11** | **24** | **+13** |

## Key Architecture Decisions
- **Pipeline and site are decoupled**: Python pipeline → JSON → SvelteKit prebuild. Site never calls EIA API at runtime.
- **URL is single source of truth** for chart state: `/prices?state=TX,CA&sector=residential`
- **Static JSON per chart** in site/static/data/ (10-200KB each). No database, no API server.
- **D3 as utility library only** (scales, shapes, geo, interpolate). Svelte handles all DOM rendering via reactive SVG.
- **Editorial page design**: Serif headlines (Instrument Serif) → explanatory intro → chart sections with warm alternating backgrounds → source attribution + icon download buttons
- **Brand-first color system**: Custom @theme tokens (bg-primary, text-accent, bg-surface-alt, etc.) replace default Tailwind gray/blue palette. All components use token-based classes.
- **Chart UX pattern**: End-of-line labels on line charts, hover crosshair + dots, no rotated Y-axis labels (units in chart subtitle instead)
- **Fuels indexing**: "All Fuels" view uses index (base year = 100) to fairly compare fuels with different units

## Data Pipeline
```bash
# Activate venv and run pipeline (fetches from EIA API, generates JSON)
cd us-energy-data/pipeline && source .venv/bin/activate && python -m src.main
```

### EIA API Endpoints Used
- **Prices**: `/electricity/retail-sales/data` (data[]=price, facets: RES/COM/IND)
- **Demand**: `/electricity/retail-sales/data` (data[]=sales, facets: RES/COM/IND)
- **Generation**: `/electricity/electric-power-operational-data/data` (data[]=generation, facets: fuel types)
- **Coal**: `/coal/mine-production/data` (data[]=production)
- **Natural Gas**: `/natural-gas/prod/whv/data` (data[]=value, facets: process=VGM)
- **Crude Oil**: `/petroleum/crd/crpdn/data` (data[]=value, facets: process=FPF)
- **Reliability**: No API — curated sample data

## Data Sources
- Primary: EIA API v2 (https://api.eia.gov/v2/) — electricity prices, demand, generation, capacity, fuels, emissions, trade
- Secondary: EIA-861 annual report — reliability metrics (SAIDI/SAIFI)
- Census Bureau API — annual state population estimates (for per-capita calculations)
- BLS CPI-U — inflation adjustment for household electricity bills
- API key registration: https://www.eia.gov/opendata/register.php

## Dev Commands
```bash
# Frontend dev server
cd us-energy-data/site && npm run dev

# Production build
cd us-energy-data/site && npm run build

# Run data pipeline (requires EIA_API_KEY in .env)
cd us-energy-data/pipeline && source .venv/bin/activate && python -m src.main
```

## 5 Topic Sections (current → target)
1. **Prices & Bills** — retail prices by sector (line) + state prices (choropleth) | TARGET: + household bills + price-vs-mix scatter
2. **Electricity Demand** — consumption by sector (line) + top 10 states (bar) | TARGET: + per-capita demand + load growth
3. **Generation & Resources** — by source (bar) + share trends (line) + renewable share (choropleth) | TARGET: + carbon intensity + capacity + additions/retirements + storage + capacity factors
4. **Fossil Fuels** — production trends (line) + top producing states (bar) | TARGET: + fuel consumption for generation + imports/exports
5. **Reliability & Outages** — SAIDI trend (line) + SAIDI vs SAIFI (scatter) [sample data] | TARGET: + real EIA-861 data + reliability-vs-prices scatter

## Chart Types
- LineChart.svelte — time series
- BarChart.svelte — comparisons / rankings (vertical or horizontal)
- Scatter.svelte — exploratory (2-variable)
- ChoroplethMap.svelte — state-level geographic

## Design Tokens (defined in app.css @theme)
### Brand Palette
- Primary: `#0f2b44` (deep navy — nav, footer, headings), light: `#1a3f5c`, dark: `#091c2e`
- Accent: `#e86c3a` (warm orange — CTAs, stats, active states), light: `#f09060`, dark: `#c85a2e`
- Surface: `#fafaf8` (warm off-white body bg), alt: `#f3f2ef` (section bands), card: `#ffffff`
- Border: `#e5e2dc` (warm border), light: `#efecea`
- Text: `#1a1a2e` (body), secondary: `#5a6270`, muted: `#8a919c`

### Chart Colors
- #2166ac (blue), #e86c3a (orange), #1b9e77 (teal), #984ea3 (purple), #e7a02f (gold), #a6611a (brown), #666666 (gray), #e31a1c (red)
- Energy source colors defined in utils/colors.ts
- Choropleth: cream-to-navy gradient via d3-interpolate (`#fef9ef` → `#0f2b44`)

### Typography
- Display/headlines: `--font-display` = Instrument Serif (serif)
- Body/UI: `--font-sans` = DM Sans
- Monospace/data: `--font-mono` = JetBrains Mono
- Utility class: `.font-display` for serif headlines

### Tailwind Usage
All custom tokens generate Tailwind utilities automatically (Tailwind v4 @theme):
`bg-primary`, `text-accent`, `bg-surface-alt`, `border-border`, `text-text-secondary`, etc.

### Dark Mode
Supported via `@media (prefers-color-scheme: dark)` with CSS custom property overrides in app.css.

## Dependencies (site/package.json)
### Runtime
- d3-array, d3-format, d3-geo, d3-interpolate, d3-scale, d3-shape, d3-time-format
- topojson-client, us-atlas

### Dev
- @sveltejs/adapter-cloudflare, @sveltejs/kit, svelte 5, tailwindcss 4, vite 6, typescript 5
- d3-scale-chromatic (for fallback color scales)
- @types/d3-* (type definitions for all D3 modules)
