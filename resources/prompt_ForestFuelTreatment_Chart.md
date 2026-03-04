# Prompt: Forest Fuel Treatment Chart Dashboard

Build a standalone single-file HTML chart dashboard for the TRPA Climate Resilience Dashboard. No build step, CDN-only dependencies.

## Stack
- **Plotly.js 2.32** via `cdn.plot.ly` — use `Plotly.react()` for all rendering
- **Calcite Components 2.13.2** for UI elements (tabs, icons, buttons, loader)
- **Lexend Deca** via Google Fonts
- **Vanilla JS** — no frameworks, no ArcGIS SDK

## Data sources (fetch both in parallel via `Promise.allSettled`)

**EIP API** — Treatment Zone data
```
https://corsproxy.io/?{encoded: https://www.laketahoeinfo.org/WebServices/GetReportedEIPIndicatorProjectAccomplishments/JSON/e17aeb86-85e3-4260-83fd-a2b32501c476/19}
```
- Filter rows where `PMSubcategoryName1 === "Treatment Zone"`
- Map `PMSubcategoryOption1` → zone name ("Community Defense Zone" → "Defense Zone")
- Group/sum `IndicatorProjectValue` by `IndicatorProjectYear` + zone

**ArcGIS Feature Service** — FuelsTx + Ownership Type data
```
https://services6.arcgis.com/1KtlSd2mklZMBKaz/ArcGIS/rest/services/Tahoe_Forest_Fuels_Tx_OFFICIAL_Public_View/FeatureServer/0/query
```
- Fields: `YEAR, ACRES, FuelsTx, Ownership_Type`
- Params: `where=ACRES>0 AND YEAR IS NOT NULL`, `resultRecordCount=5000`, `f=json`

Store each source separately (`eipRows`, `agolRows`). Switching dimensions swaps the active dataset — no re-fetching.

## Layout (single card, max-width 1100px, centered)
1. **Card header** — tree SVG icon, title "Forest Fuels Reduction", subtitle
2. **Stats strip** — 4 KPI cards: Total Acres, Peak Year, Peak Year Acres, Groups Shown. Show shimmer skeleton on load.
3. **Dimension tabs** — underline-style tab bar: `Treatment Zone | Fuels Treatment Type | Ownership Type`. Grey out + disable FuelsTx/Ownership tabs if AGOL fetch fails.
4. **Filter bar** — pill buttons for all distinct values in the active dimension. Multi-select. Reset button + Download CSV button (right-aligned).
5. **Chart** — stacked bar, year on X axis, acres on Y. Spinner overlay on load, error state with retry.
6. **Footer** — source attribution + active dimension label.

## Color palettes
```css
--j1:#01161E; --j2:#123559; --j3:#598392; --j4:#aec3b0; --j5:#eff6e0;
--mz1:#208385; --mz2:#FC9A62; --mz3:#F9C63E; --mz4:#632E5A; --mz5:#A48352; --mz6:#BCEDB8;
--zone1:#ABCD66; --zone2:#E69800; --zone3:#A87000; --zone4:#F5CA7A;
```
Each dimension uses its own palette cycle:
- Treatment Zone → zone palette (`#ABCD66`, `#E69800`, `#A87000`, `#F5CA7A`)
- Fuels Treatment Type → management zone palette (`--mz1` through `--mz6`)
- Ownership Type → jurisdiction palette (`--j2`, `--j3`, `--mz5`…)

Active pills match their bar color. Pill hover uses `--j5` background.

## Chart config (Plotly)
- `barmode: "stack"`, transparent background, `dragmode: false`
- `transition: { duration: 350, easing: "cubic-in-out" }` on dimension/filter changes
- `hovermode: "x unified"`, hover label background `#123559`, text `#eff6e0`
- X axis: category type, no grid. Y axis: `tickformat: ",.0f"`, light grid `rgba(174,195,176,.3)`
- Legend above chart: `orientation:"h"`, `y:1.02`
- `displayModeBar: false`, `responsive: true`

## Download CSV
Export currently filtered rows (all fields: Year, Category, FuelsTx, Ownership_Type, Acres).
Filename: `ForestFuelTreatment_{activeDim}_{YYYY-MM-DD}.csv`

## Cache
`localStorage`, 6-hour TTL. Serve cached data immediately, refresh in background.

## Design rules
- Font: Lexend Deca everywhere including Plotly `font.family`
- Page background: `--j5` (`#eff6e0`), card background white
- 3px top accent bar: gradient across MZ palette
- Card: `border-radius:20px`, subtle shadow, `fadeUp` animation on load
- No dark backgrounds on any element
- Stat values: `font-size:1.45rem`, `font-weight:600`, each card a different palette color
- Pills: `border-radius:20px`, `font-size:11px`, `border:1.5px solid var(--border)`
