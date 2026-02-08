# Dynamic Chart Rendering for Market Health Reporter

## Overview

The Market Health Reporter now generates **interactive, dynamic charts** using Chart.js instead of static PNG images. This provides several benefits:

- **Interactive**: Users can hover over data points, zoom, and pan
- **Responsive**: Charts automatically adjust to screen size
- **Lightweight**: JSON data files are smaller than PNG images
- **Accessibility**: Better screen reader support and semantic HTML
- **Modern**: Leverages client-side rendering for faster page loads

## What Changed

### Python Module (`report_graphics_tool.py`)

- Removed matplotlib dependency
- Now generates JSON data files instead of PNG images
- Each chart type outputs a structured JSON file with chart configuration

### Hugo Shortcodes

Added a new `dynamic_chart` shortcode that:
- Loads JSON data files
- Renders charts using Chart.js
- Supports all existing chart types (histogram, line charts, dual-axis)

## Usage in Markdown

Replace old static image references with the new dynamic chart shortcode:

### Before (Static PNG)
```markdown
![Volume Histogram](volume_hist.png)
```

### After (Dynamic Chart)
```markdown
{{< dynamic_chart data="volume_hist.json" id="volume-histogram" height="400" >}}
```

## Chart Types

### 1. Volume Histogram
**File**: `volume_hist.json`
**Type**: Bar chart showing transaction volume distribution

```markdown
{{< dynamic_chart data="volume_hist.json" id="vol-hist" >}}
```

### 2. Crypto Metrics
**File**: `crypto_metrics.json`
**Type**: Multi-line time series with 4 metrics (volume, trade count, avg tx size, buy/sell ratio)

```markdown
{{< dynamic_chart data="crypto_metrics.json" id="crypto-metrics" height="500" >}}
```

### 3. Benford Law
**File**: `benford_law.json`
**Type**: Dual-axis line chart showing Benford Law test score and trade count

```markdown
{{< dynamic_chart data="benford_law.json" id="benford" >}}
```

### 4. VV Correlation
**File**: `vv_correlation.json`
**Type**: Single line chart showing VV correlation over time

```markdown
{{< dynamic_chart data="vv_correlation.json" id="vv-corr" >}}
```

## Shortcode Parameters

- `data` (required): Path to the JSON data file (relative to page bundle)
- `id` (optional): Unique HTML ID for the canvas element (auto-generated if not provided)
- `height` (optional): Maximum height in pixels (default: 400)

## JSON Data Format

Each JSON file follows this structure:

```json
{
  "type": "line_chart",
  "title": "Chart Title",
  "data": {
    "timestamps": ["2023-01-01 00:00:00", ...],
    "datasets": [
      {
        "label": "Metric Name",
        "values": [1.0, 2.0, ...],
        "color": "rgb(255, 99, 132)"
      }
    ]
  },
  "options": {
    "xlabel": "Time",
    "ylabel": "Value"
  }
}
```

## Migration Guide

For existing reports with PNG images:

1. Re-run the Market Health Reporter script to generate new JSON files
2. Update markdown files to use `{{< dynamic_chart >}}` shortcode
3. Remove old PNG files (optional, for cleanup)

## Dependencies

- **Chart.js 4.4.0**: Loaded via CDN in the shortcode
- No additional Hugo dependencies required

## Browser Support

Works in all modern browsers that support:
- JavaScript ES6+
- HTML5 Canvas API
- Fetch API

## Future Enhancements

Potential improvements:
- Add zoom/pan controls
- Export chart as PNG/SVG
- Theme support (light/dark mode)
- Animation on scroll
- Data table toggle view
