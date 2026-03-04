# Prompt: Forest Fuel Treatment Dashboard (Map + Chart)

## Context

I'm building interactive data visualizations for the Lake Tahoe Climate Resilience Dashboard at climate.laketahoeinfo.org. The data lives in an ArcGIS Online WebMap with portal item ID `0303bdff0aa04b628f8a60a8c72c53a1`. I need two standalone HTML embeds — one map page and one chart page — that share the same filters, styles, and data source.

---

## Stack

- **ArcGIS JS SDK 4.29** (AMD via `js.arcgis.com/4.29/`) for service queries
- **ArcGIS Map Components 4.29** (`arcgis-map-components.esm.js`) for the map page — use `<arcgis-map>` web component with `<arcgis-zoom>`, `<arcgis-home>`, `<arcgis-fullscreen>`, `<arcgis-legend>`, `<arcgis-bookmarks>`, `<arcgis-expand>`
- **Calcite Components 2.13.2** for UI shell, panel, slider, icons, loader, action
- **Plotly.js 2.32** (`Plotly.react()`) for all charts on the chart page
- **Lexend Deca** (Google Fonts) as the sole typeface
- No React, no build tools — pure HTML/CSS/JS

## Load order (critical — avoids multipleDefine error)
1. Calcite `type="module"`
2. ArcGIS SDK CSS `<link>`
3. ArcGIS AMD `<script src="https://js.arcgis.com/4.29/">` — synchronous
4. Map components `<script type="module">` — ES module, naturally deferred
5. App `<script type="module">` — uses `arcgisViewReadyChange` event, no `require()`

For the **chart page**, use `require(["esri/WebMap"], ...)` normally — no map components needed there.

---

## Color Palettes

```js
const MZ = ["#208385","#FC9A62","#F9C63E","#632E5A","#A48352","#BCEDB8"]; // management zones
const JX = ["#01161E","#123559","#598392","#aec3b0","#598392","#eff6e0"]; // jurisdictions
```

CSS variables:
```css
--j1:#01161E; --j2:#123559; --j3:#598392; --j4:#aec3b0; --j5:#eff6e0;
--mz1:#208385; --mz2:#FC9A62; --mz3:#F9C63E; --mz4:#632E5A; --mz5:#A48352; --mz6:#BCEDB8;
--brand: var(--j2);
--border: var(--j4);
--muted: var(--j3);
```

---

## Layer Schema (key fields)

| Field | Type | Description |
|---|---|---|
| `YEAR` | Integer | Treatment year |
| `ACRES` | Double | Area treated |
| `FuelsTx` | String | Fuels treatment type |
| `Ownership_Type` | String | Land ownership category |
| `OBJECTID_1` | OID | Record ID |

---

## File 1: Map Page

### Layout
- `<calcite-shell>` with `<calcite-shell-panel slot="panel-start" display-mode="dock">` at 300px
- `<arcgis-map item-id="...">` fills the content area
- No top navigation bar

### Map widgets
- `<arcgis-zoom>`, `<arcgis-home>`, `<arcgis-fullscreen>` at `top-left`
- `<arcgis-expand expanded position="top-right">` wrapping `<arcgis-legend>`
- `<arcgis-expand position="bottom-left">` wrapping `<arcgis-bookmarks>`

### Filter panel
1. **Year range** — `<calcite-slider>` with two handles. min=2020, max=queried from `MAX(YEAR)`. Set all attributes via JS after `customElements.whenDefined("calcite-slider")`. Use `calciteSliderInput`. Show year badges above.
2. **FuelsTx pills** — query distinct values, render as `<button class="pill">` toggles colored with MZ palette via `data-ci`.
3. **Ownership_Type pills** — same pattern with JX palette.
4. Reset action in panel header.
5. Stats footer (feature count + total acres) pinned to bottom.

### Behavior
- Build `definitionExpression` WHERE clause combining year range + selected pills
- On filter: `queryExtent()` then `view.goTo(extent.expand(1.15), {duration:600})`
- 280ms debounce on slider

---

## File 2: Chart Page

### Layout
- Two-column CSS grid: `260px sidebar | 1fr main`
- Sidebar: same filters as map page
- Main: title + toggle row, then 2-row chart grid

### Charts (all Plotly.react)
1. **Horizontal bar** (full width) — ACRES by active dimension (FuelsTx or Ownership_Type), DESC, colored with MZ/JX palette
2. **Line chart** — ACRES by YEAR, always shown regardless of toggle
3. **Donut chart** — same dimension as bar, share of total acres

### Toggle
- "Fuels Treatment" / "Ownership Type" buttons switch `chartDim` and re-query all charts

### Data loading
- `require(["esri/WebMap"], fn)` — load same portal item, get `layers.getItemAt(0)`
- Loading overlay with `calcite-loader` until ready

---

## Shared UX

- Pills are `<button>` elements NOT `calcite-chip` — avoids web component selection state issues
- `.pill.on` CSS class drives selected state
- Year badges above slider show live values
- All Plotly: `displayModeBar:false`, `responsive:true`, `plot_bgcolor:"white"`, font `"Lexend Deca, sans-serif"`
- No background color overrides on Calcite panel or header elements
