# Market Health Reporter 🌰

Automated market health reports with dynamic Chart.js graphs and LLM-generated interpretations.

## Features

- 📊 Visual charts showing metric trends
- 🧠 AI-powered interpretations of market movements
- 🌰 Chestnut-approved design
- 📱 Responsive layout with interactive charts

## Usage

2. Run the generator: `python generate_report.py`
3. Serve the site: `hugo server -D`

The reports will include dynamic Chart.js graphs and AI-generated interpretations.

## Configuration

metrics:
  - id: "unique_metric_id"
    name: "Metric Display Name"
    data:
      labels: ["date1", "date2", "date3"]
      values: [value1, value2, value3]
    interpretation: "AI-generated explanation of what this metric means"
    spike_threshold: 1.5
    spike_detected: true
