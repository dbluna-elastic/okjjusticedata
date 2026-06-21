const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, PageNumber, PageBreak, LevelFormat } = require("docx");

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

function headerCell(text, width) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: { fill: "1B3A5C", type: ShadingType.CLEAR },
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })]
  });
}

function cell(text, width) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, font: "Arial", size: 20 })] })]
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: "1B3A5C" },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "2E75B6" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "333333" },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers2", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers3", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers4", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "bullets2", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "bullets3", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [
    // TITLE PAGE
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      children: [
        new Paragraph({ spacing: { before: 3600 }, children: [] }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 200 },
          children: [new TextRun({ text: "Oklahoma Office of Juvenile Affairs", size: 48, bold: true, font: "Arial", color: "1B3A5C" })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 400 },
          children: [new TextRun({ text: "Elasticsearch Demo Environment", size: 36, font: "Arial", color: "2E75B6" })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 200 },
          children: [new TextRun({ text: "Setup Guide & Demo Walkthrough", size: 28, font: "Arial", color: "555555" })]
        }),
        new Paragraph({ spacing: { before: 1200 }, children: [] }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Prepared by Elastic", size: 22, font: "Arial", color: "777777" })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "June 2026", size: 22, font: "Arial", color: "777777" })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 200 },
          children: [new TextRun({ text: "DEMO — Contains Simulated Data Only", size: 20, bold: true, font: "Arial", color: "CC0000" })]
        }),
      ]
    },

    // MAIN CONTENT
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [new TextRun({ text: "OJA Elasticsearch Demo — Setup & Walkthrough", italics: true, size: 18, color: "999999", font: "Arial" })]
          })]
        })
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "Page ", size: 18, font: "Arial" }), new TextRun({ children: [PageNumber.CURRENT], size: 18, font: "Arial" })]
          })]
        })
      },
      children: [
        // OVERVIEW
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Overview")] }),
        new Paragraph({ spacing: { after: 200 }, children: [new TextRun("This demo environment simulates the data landscape of the Oklahoma Office of Juvenile Affairs (OJA) running on Elasticsearch. It contains 2,000 synthetic youth records with associated case notes, risk assessments, and outcome data spanning January 2023 through June 2026.")] }),
        new Paragraph({ spacing: { after: 200 }, children: [new TextRun("All data is entirely fictional. Names, locations, and case details are randomly generated and do not represent real individuals.")] }),

        // DATA MODEL
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Data Model")] }),
        new Paragraph({ spacing: { after: 200 }, children: [new TextRun("The demo uses four Elasticsearch indices:")] }),

        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2200, 1200, 5960],
          rows: [
            new TableRow({ children: [headerCell("Index", 2200), headerCell("Doc Count", 1200), headerCell("Description", 5960)] }),
            new TableRow({ children: [cell("youth_profiles", 2200), cell("2,000", 1200), cell("Core demographic, offense, placement, and supervision data for each youth", 5960)] }),
            new TableRow({ children: [cell("case_notes", 2200), cell("~42,000", 1200), cell("Officer contact notes, home visits, court hearings, drug tests, incident reports", 5960)] }),
            new TableRow({ children: [cell("assessments", 2200), cell("~4,200", 1200), cell("Risk/needs assessment scores (YASI, SAVRY, etc.) with domain-level breakdowns", 5960)] }),
            new TableRow({ children: [cell("outcomes", 2200), cell("~900", 1200), cell("Discharge outcomes, recidivism tracking, program completion, services delivered", 5960)] }),
          ]
        }),

        // SETUP
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Setup Instructions")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Prerequisites")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("Python 3.8+ installed")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("Access to an Elasticsearch cluster (Elastic Cloud or self-managed)")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("An API key or username/password with index creation and bulk write permissions")] }),
        new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 200 }, children: [new TextRun("Kibana access for dashboard import")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Step 1: Generate Mock Data")] }),
        new Paragraph({ spacing: { after: 100 }, children: [new TextRun("Run the data generator to create NDJSON files:")] }),
        new Paragraph({
          spacing: { after: 200 },
          shading: { fill: "F5F5F5", type: ShadingType.CLEAR },
          children: [new TextRun({ text: "python generate_mock_data.py", font: "Courier New", size: 20 })]
        }),
        new Paragraph({ spacing: { after: 200 }, children: [new TextRun("This creates a "), new TextRun({ text: "data/", bold: true }), new TextRun(" folder with four NDJSON files. Optionally install the "), new TextRun({ text: "faker", bold: true }), new TextRun(" package first ("), new TextRun({ text: "pip install faker", font: "Courier New", size: 20 }), new TextRun(") for more varied names.")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Step 2: Load Data into Elasticsearch")] }),
        new Paragraph({ spacing: { after: 100 }, children: [new TextRun("Use the bulk loader script. With an API key:")] }),
        new Paragraph({
          spacing: { after: 100 },
          shading: { fill: "F5F5F5", type: ShadingType.CLEAR },
          children: [new TextRun({ text: "python bulk_load.py --host https://your-cluster.es.cloud.io --api-key YOUR_KEY --recreate", font: "Courier New", size: 18 })]
        }),
        new Paragraph({ spacing: { after: 100 }, children: [new TextRun("Or with username/password:")] }),
        new Paragraph({
          spacing: { after: 200 },
          shading: { fill: "F5F5F5", type: ShadingType.CLEAR },
          children: [new TextRun({ text: "python bulk_load.py --host https://your-cluster.es.cloud.io --user elastic --password PASS --recreate", font: "Courier New", size: 18 })]
        }),
        new Paragraph({ spacing: { after: 200 }, children: [new TextRun("The "), new TextRun({ text: "--recreate", font: "Courier New", size: 20 }), new TextRun(" flag deletes existing indices first. Use "), new TextRun({ text: "--verify-only", font: "Courier New", size: 20 }), new TextRun(" to check document counts without loading.")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Step 3: Import Kibana Dashboards")] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("Open Kibana and go to "), new TextRun({ text: "Stack Management > Saved Objects", bold: true })] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("Click "), new TextRun({ text: "Import", bold: true })] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("Select "), new TextRun({ text: "kibana_dashboards.ndjson", bold: true })] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("Choose "), new TextRun({ text: "Automatically overwrite conflicts", bold: true })] }),
        new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 200 }, children: [new TextRun("Click "), new TextRun({ text: "Import", bold: true })] }),
        new Paragraph({ spacing: { after: 200 }, children: [new TextRun("Three dashboards will be imported: Case Overview, Assessments & Outcomes, and Case Notes.")] }),

        // PAGE BREAK
        new Paragraph({ children: [new PageBreak()] }),

        // DEMO WALKTHROUGH
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Demo Walkthrough")] }),
        new Paragraph({ spacing: { after: 200 }, children: [new TextRun("Below is a suggested flow for walking through the demo with OJA stakeholders.")] }),

        // Dashboard 1
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Dashboard 1: Case Overview")] }),
        new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Talking Points:", bold: true })] }),
        new Paragraph({ numbering: { reference: "numbers2", level: 0 }, children: [new TextRun({ text: "Active Cases Metric: ", bold: true }), new TextRun("Start with the big number. \"Right now OJA can see at a glance how many youth are actively supervised.\" Click into the metric to show it filters in real time.")] }),
        new Paragraph({ numbering: { reference: "numbers2", level: 0 }, children: [new TextRun({ text: "Intakes Over Time: ", bold: true }), new TextRun("Show the monthly intake trend. Highlight seasonality patterns. Drag to select a date range to demonstrate filtering across all panels.")] }),
        new Paragraph({ numbering: { reference: "numbers2", level: 0 }, children: [new TextRun({ text: "Demographics: ", bold: true }), new TextRun("Gender and race pie charts show the population breakdown. Note the significant American Indian/Alaska Native representation reflecting Oklahoma demographics.")] }),
        new Paragraph({ numbering: { reference: "numbers2", level: 0 }, children: [new TextRun({ text: "Offense Categories: ", bold: true }), new TextRun("Horizontal bar chart shows property offenses lead, consistent with national juvenile justice data. Click a bar to filter the entire dashboard.")] }),
        new Paragraph({ numbering: { reference: "numbers2", level: 0 }, children: [new TextRun({ text: "Geographic Map: ", bold: true }), new TextRun("Heatmap of youth locations across Oklahoma. Zoom into Oklahoma City and Tulsa metro areas to show concentration. \"This helps OJA allocate field resources.\"")] }),
        new Paragraph({ numbering: { reference: "numbers2", level: 0 }, spacing: { after: 200 }, children: [new TextRun({ text: "Cross-filtering: ", bold: true }), new TextRun("Demonstrate clicking on a county in the donut chart and watching all other visualizations update. This is the power of Kibana — every panel is connected.")] }),

        // Dashboard 2
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Dashboard 2: Assessments & Outcomes")] }),
        new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Talking Points:", bold: true })] }),
        new Paragraph({ numbering: { reference: "numbers3", level: 0 }, children: [new TextRun({ text: "Risk Level Distribution: ", bold: true }), new TextRun("Pie chart shows Low/Moderate/High/Very High breakdown. \"OJA can monitor whether the system is appropriately classifying youth.\"")] }),
        new Paragraph({ numbering: { reference: "numbers3", level: 0 }, children: [new TextRun({ text: "Risk Score Trends: ", bold: true }), new TextRun("Line chart shows average risk scores over time. \"If programming is effective, we expect to see scores trending down across re-assessments.\"")] }),
        new Paragraph({ numbering: { reference: "numbers3", level: 0 }, children: [new TextRun({ text: "Recidivism Metrics: ", bold: true }), new TextRun("Show the 6-month and 12-month recidivism rates. \"This is the metric that matters most to legislators and the public.\"")] }),
        new Paragraph({ numbering: { reference: "numbers3", level: 0 }, children: [new TextRun({ text: "Discharge Reasons: ", bold: true }), new TextRun("Bar chart shows successful completion as the leading reason. \"We can track whether our completion rates are improving year over year.\"")] }),
        new Paragraph({ numbering: { reference: "numbers3", level: 0 }, spacing: { after: 200 }, children: [new TextRun({ text: "Length of Stay: ", bold: true }), new TextRun("Histogram shows the distribution. \"This helps identify if youth are staying longer than evidence-based practices recommend.\"")] }),

        // Dashboard 3
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Dashboard 3: Case Notes")] }),
        new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Talking Points:", bold: true })] }),
        new Paragraph({ numbering: { reference: "numbers4", level: 0 }, children: [new TextRun({ text: "Note Type Breakdown: ", bold: true }), new TextRun("Shows the mix of contact types — home visits, phone contacts, court hearings, etc.")] }),
        new Paragraph({ numbering: { reference: "numbers4", level: 0 }, children: [new TextRun({ text: "Sentiment Analysis: ", bold: true }), new TextRun("\"Elastic can tag notes as positive, neutral, or concerning, giving supervisors an early warning system.\"")] }),
        new Paragraph({ numbering: { reference: "numbers4", level: 0 }, spacing: { after: 200 }, children: [new TextRun({ text: "Full-Text Search: ", bold: true }), new TextRun("Switch to Discover tab. Search for \"curfew violation\" or \"drug test positive\" across all 42,000+ case notes. \"This is where Elasticsearch shines — instant search across years of narrative text.\"")] }),

        // KEY DEMO MOMENTS
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Key Demo Moments")] }),
        new Paragraph({ spacing: { after: 100 }, children: [new TextRun("These are high-impact moments to emphasize during the demo:")] }),
        new Paragraph({ numbering: { reference: "bullets2", level: 0 }, children: [new TextRun({ text: "Speed: ", bold: true }), new TextRun("Search 42,000 case notes in under a second. Compare to searching through paper files or a legacy system.")] }),
        new Paragraph({ numbering: { reference: "bullets2", level: 0 }, children: [new TextRun({ text: "Cross-filtering: ", bold: true }), new TextRun("Click any element on a dashboard and watch everything else update. No reports to run, no queries to write.")] }),
        new Paragraph({ numbering: { reference: "bullets2", level: 0 }, children: [new TextRun({ text: "Geographic awareness: ", bold: true }), new TextRun("Show the map view and zoom into specific counties. Overlay with offense types.")] }),
        new Paragraph({ numbering: { reference: "bullets2", level: 0 }, children: [new TextRun({ text: "Real-time: ", bold: true }), new TextRun("\"As new intake data enters the system, these dashboards update automatically. No monthly report cycle.\"")] }),
        new Paragraph({ numbering: { reference: "bullets2", level: 0 }, spacing: { after: 200 }, children: [new TextRun({ text: "Security: ", bold: true }), new TextRun("\"Elasticsearch supports role-based access. A probation officer sees their caseload. A district supervisor sees their district. Central office sees statewide.\"")] }),

        // PAGE BREAK
        new Paragraph({ children: [new PageBreak()] }),

        // FILES
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Files Included")] }),

        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3500, 5860],
          rows: [
            new TableRow({ children: [headerCell("File", 3500), headerCell("Purpose", 5860)] }),
            new TableRow({ children: [cell("generate_mock_data.py", 3500), cell("Generates 2,000 synthetic youth records with case notes, assessments, and outcomes", 5860)] }),
            new TableRow({ children: [cell("bulk_load.py", 3500), cell("Creates indices and bulk-loads NDJSON data into Elasticsearch", 5860)] }),
            new TableRow({ children: [cell("mappings.json", 3500), cell("Elasticsearch index mappings for all four indices", 5860)] }),
            new TableRow({ children: [cell("kibana_dashboards.ndjson", 3500), cell("Kibana saved objects: 3 dashboards, 15 visualizations, 4 index patterns", 5860)] }),
            new TableRow({ children: [cell("data/*.ndjson", 3500), cell("Generated mock data files (created by generate_mock_data.py)", 5860)] }),
          ]
        }),

        new Paragraph({ spacing: { before: 400 }, children: [] }),

        // TROUBLESHOOTING
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Troubleshooting")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Connection refused")] }),
        new Paragraph({ spacing: { after: 200 }, children: [new TextRun("Verify the cluster URL includes the port and protocol (e.g., https://). For Elastic Cloud, use the Elasticsearch endpoint URL, not the Kibana URL.")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Authentication error")] }),
        new Paragraph({ spacing: { after: 200 }, children: [new TextRun("Ensure your API key or credentials have permissions for index creation (indices:admin/create) and bulk indexing (indices:data/write/bulk).")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Dashboard shows no data")] }),
        new Paragraph({ spacing: { after: 200 }, children: [new TextRun("Check the time range in Kibana. The mock data spans 2023–2026, so set the time picker to \"Last 3 years\" or a custom range covering that period.")] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("Geo map not rendering")] }),
        new Paragraph({ spacing: { after: 200 }, children: [new TextRun("The geo_point field requires the Elastic Maps Service. If running on a self-managed cluster without internet, you may need to configure a local maps server.")] }),

        // RESET
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Resetting the Demo")] }),
        new Paragraph({ spacing: { after: 100 }, children: [new TextRun("To regenerate fresh data with different random seeds, edit the "), new TextRun({ text: "random.seed()", font: "Courier New", size: 20 }), new TextRun(" value in generate_mock_data.py, then re-run:")] }),
        new Paragraph({
          spacing: { after: 100 },
          shading: { fill: "F5F5F5", type: ShadingType.CLEAR },
          children: [new TextRun({ text: "python generate_mock_data.py", font: "Courier New", size: 20 })]
        }),
        new Paragraph({
          spacing: { after: 200 },
          shading: { fill: "F5F5F5", type: ShadingType.CLEAR },
          children: [new TextRun({ text: "python bulk_load.py --host <URL> --api-key <KEY> --recreate", font: "Courier New", size: 20 })]
        }),

        // NEXT STEPS
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Next Steps")] }),
        new Paragraph({ spacing: { after: 100 }, children: [new TextRun("After the demo, potential next steps with OJA:")] }),
        new Paragraph({ numbering: { reference: "bullets3", level: 0 }, children: [new TextRun({ text: "JOLTS Integration: ", bold: true }), new TextRun("Map JOLTS database fields to Elasticsearch indices. Build Logstash or Elastic Agent pipeline for real-time sync.")] }),
        new Paragraph({ numbering: { reference: "bullets3", level: 0 }, children: [new TextRun({ text: "Security Model: ", bold: true }), new TextRun("Design role-based access with document-level security aligned to OJA districts and caseload assignments. Address CJIS compliance requirements.")] }),
        new Paragraph({ numbering: { reference: "bullets3", level: 0 }, children: [new TextRun({ text: "NLP Enrichment: ", bold: true }), new TextRun("Deploy Elastic ML for real sentiment analysis on case notes, named entity recognition, and anomaly detection on intake patterns.")] }),
        new Paragraph({ numbering: { reference: "bullets3", level: 0 }, children: [new TextRun({ text: "Alerting: ", bold: true }), new TextRun("Set up Watcher alerts for high-risk youth missed contacts, overdue assessments, or caseload imbalances.")] }),
        new Paragraph({ numbering: { reference: "bullets3", level: 0 }, spacing: { after: 200 }, children: [new TextRun({ text: "Power BI Integration: ", bold: true }), new TextRun("Since OJA is already investing in Power BI, demonstrate Elasticsearch as the data backend powering their existing BI investment.")] }),
      ]
    }
  ]
});

Packer.toBuffer(doc).then(buffer => {
  const outPath = process.argv[2] || "OJA_Elasticsearch_Demo_Walkthrough.docx";
  fs.writeFileSync(outPath, buffer);
  console.log("Created: " + outPath);
});
