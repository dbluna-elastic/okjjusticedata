# Oklahoma Office of Juvenile Affairs
## Elasticsearch Demo Environment

### Setup Guide & Demo Walkthrough

Prepared by Elastic — June 2026

> **DEMO — Contains Simulated Data Only**

---

## Overview

This demo environment simulates the data landscape of the Oklahoma Office of Juvenile Affairs (OJA) running on Elasticsearch. It contains 2,000 synthetic youth records with associated case notes, risk assessments, and outcome data spanning January 2023 through June 2026.

All data is entirely fictional. Names, locations, and case details are randomly generated and do not represent real individuals.

---

## Data Model

The demo uses four Elasticsearch indices:

| Index | Doc Count | Description |
|-------|-----------|-------------|
| `youth_profiles` | 2,000 | Core demographic, offense, placement, and supervision data for each youth |
| `case_notes` | ~42,000 | Officer contact notes, home visits, court hearings, drug tests, incident reports |
| `assessments` | ~4,200 | Risk/needs assessment scores (YASI, SAVRY, etc.) with domain-level breakdowns |
| `outcomes` | ~900 | Discharge outcomes, recidivism tracking, program completion, services delivered |

---

## Setup Instructions

### Prerequisites

- Python 3.8+ installed
- Access to an Elasticsearch cluster (Elastic Cloud or self-managed)
- An API key or username/password with index creation and bulk write permissions
- Kibana access for dashboard import

### Step 1: Generate Mock Data

Run the data generator to create NDJSON files:

```bash
python generate_mock_data.py
```

This creates a `data/` folder with four NDJSON files. Optionally install the **faker** package first (`pip install faker`) for more varied names.

### Step 2: Load Data into Elasticsearch

Use the bulk loader script. With an API key:

```bash
python bulk_load.py --host https://your-cluster.es.cloud.io --api-key YOUR_KEY --recreate
```

Or with username/password:

```bash
python bulk_load.py --host https://your-cluster.es.cloud.io --user elastic --password PASS --recreate
```

The `--recreate` flag deletes existing indices first. Use `--verify-only` to check document counts without loading.

### Step 3: Import Kibana Dashboards

1. Open Kibana and go to **Stack Management > Saved Objects**
2. Click **Import**
3. Select **kibana_dashboards.ndjson**
4. Choose **Automatically overwrite conflicts**
5. Click **Import**

Three dashboards will be imported: Case Overview, Assessments & Outcomes, and Case Notes.

---

## Demo Walkthrough

Below is a suggested flow for walking through the demo with OJA stakeholders.

### Dashboard 1: Case Overview

**Talking Points:**

1. **Active Cases Metric:** Start with the big number. "Right now OJA can see at a glance how many youth are actively supervised." Click into the metric to show it filters in real time.
2. **Intakes Over Time:** Show the monthly intake trend. Highlight seasonality patterns. Drag to select a date range to demonstrate filtering across all panels.
3. **Demographics:** Gender and race pie charts show the population breakdown. Note the significant American Indian/Alaska Native representation reflecting Oklahoma demographics.
4. **Offense Categories:** Horizontal bar chart shows property offenses lead, consistent with national juvenile justice data. Click a bar to filter the entire dashboard.
5. **Geographic Map:** Heatmap of youth locations across Oklahoma. Zoom into Oklahoma City and Tulsa metro areas to show concentration. "This helps OJA allocate field resources."
6. **Cross-filtering:** Demonstrate clicking on a county in the donut chart and watching all other visualizations update. This is the power of Kibana — every panel is connected.

### Dashboard 2: Assessments & Outcomes

**Talking Points:**

1. **Risk Level Distribution:** Pie chart shows Low/Moderate/High/Very High breakdown. "OJA can monitor whether the system is appropriately classifying youth."
2. **Risk Score Trends:** Line chart shows average risk scores over time. "If programming is effective, we expect to see scores trending down across re-assessments."
3. **Recidivism Metrics:** Show the 6-month and 12-month recidivism rates. "This is the metric that matters most to legislators and the public."
4. **Discharge Reasons:** Bar chart shows successful completion as the leading reason. "We can track whether our completion rates are improving year over year."
5. **Length of Stay:** Histogram shows the distribution. "This helps identify if youth are staying longer than evidence-based practices recommend."

### Dashboard 3: Case Notes

**Talking Points:**

1. **Note Type Breakdown:** Shows the mix of contact types — home visits, phone contacts, court hearings, etc.
2. **Sentiment Analysis:** "Elastic can tag notes as positive, neutral, or concerning, giving supervisors an early warning system."
3. **Full-Text Search:** Switch to Discover tab. Search for "curfew violation" or "drug test positive" across all 42,000+ case notes. "This is where Elasticsearch shines — instant search across years of narrative text."

### Key Demo Moments

These are high-impact moments to emphasize during the demo:

- **Speed:** Search 42,000 case notes in under a second. Compare to searching through paper files or a legacy system.
- **Cross-filtering:** Click any element on a dashboard and watch everything else update. No reports to run, no queries to write.
- **Geographic awareness:** Show the map view and zoom into specific counties. Overlay with offense types.
- **Real-time:** "As new intake data enters the system, these dashboards update automatically. No monthly report cycle."
- **Security:** "Elasticsearch supports role-based access. A probation officer sees their caseload. A district supervisor sees their district. Central office sees statewide."

---

## Files Included

| File | Purpose |
|------|---------|
| `generate_mock_data.py` | Generates 2,000 synthetic youth records with case notes, assessments, and outcomes |
| `bulk_load.py` | Creates indices and bulk-loads NDJSON data into Elasticsearch |
| `mappings.json` | Elasticsearch index mappings for all four indices |
| `kibana_dashboards.ndjson` | Kibana saved objects: 3 dashboards, 15 visualizations, 4 index patterns |
| `data/*.ndjson` | Generated mock data files (created by generate_mock_data.py) |

---

## Troubleshooting

### Connection refused

Verify the cluster URL includes the port and protocol (e.g., https://). For Elastic Cloud, use the Elasticsearch endpoint URL, not the Kibana URL.

### Authentication error

Ensure your API key or credentials have permissions for index creation (`indices:admin/create`) and bulk indexing (`indices:data/write/bulk`).

### Dashboard shows no data

Check the time range in Kibana. The mock data spans 2023–2026, so set the time picker to "Last 3 years" or a custom range covering that period.

### Geo map not rendering

The `geo_point` field requires the Elastic Maps Service. If running on a self-managed cluster without internet, you may need to configure a local maps server.

---

## Resetting the Demo

To regenerate fresh data with different random seeds, edit the `random.seed()` value in generate_mock_data.py, then re-run:

```bash
python generate_mock_data.py
python bulk_load.py --host <URL> --api-key <KEY> --recreate
```

---

## Next Steps

After the demo, potential next steps with OJA:

- **JOLTS Integration:** Map JOLTS database fields to Elasticsearch indices. Build Logstash or Elastic Agent pipeline for real-time sync.
- **Security Model:** Design role-based access with document-level security aligned to OJA districts and caseload assignments. Address CJIS compliance requirements.
- **NLP Enrichment:** Deploy Elastic ML for real sentiment analysis on case notes, named entity recognition, and anomaly detection on intake patterns.
- **Alerting:** Set up Watcher alerts for high-risk youth missed contacts, overdue assessments, or caseload imbalances.
- **Power BI Integration:** Since OJA is already investing in Power BI, demonstrate Elasticsearch as the data backend powering their existing BI investment.
