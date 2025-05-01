# ✈️ Aviation Emissions Compliance Register

## 📌 Overview
This project simulates and monitors flight-level CO₂ emissions from aviation operators and evaluates their compliance with the EU Emissions Trading System (EU ETS). It enables fast emissions assessments and regulatory checks, even in the absence of real-world datasets, by relying on realistic synthetic data.

---

## 🎯 Features
- Generate daily synthetic flight data with emissions and SAF blend levels
- Assess flight compliance based on EEA routing and operator status
- Store data in a structured SQLite database
- Automatically create Word and CSV reports
- Visualize emissions and compliance trends
- Maintain a growing summary log of emissions data

---
## 🧱 Tech Stack
- **Language**: Python 3
- **Data & Storage**: pandas, SQLite
- **Visualizations**: plotly, dash
- **Dashboards**: Dash with Bootstrap styling
- **Reporting**: python-docx
- **Automation**: argparse, logging

---

## 📊 Data Sources & Assumptions
- Simulated data using real-world aircraft fuel economy (Wikipedia)
- Standard emission factor: 3.16 kg CO2 per kg Jet A-1 fuel
- SAF blending assumptions: 0-50% (ASTM D7566 standards)
- Predefined European airport codes and operators

---

## 🚀 Getting Started

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Run Daily Simulation & Import
```bash
python code/main.py
python code/import_to_sqlite.py --report_date 2025-05-01
```

### 3. Use Full Pipeline Runner
Instead of running steps manually, you can run everything (data generation + import + reporting) with:

```bash
python run_all.py --report_date 2025-05-01
```
This runs:
- `main.py` to simulate flight data
- `import_to_sqlite.py` to generate and store reports

### 4. Launch Dashboard (Optional)
```bash
python code/emissions_dashboard.py
```

---

## 📂 Project File Structure
```

📁 code/
│   ├── emissions_dashboard.py
│   ├── import_to_sqlite.py
│   ├── main.py
│   ├── simulated_flight_emissions.csv
📁 config/
│   ├── data_config.json
│   ├── operators.json
📁 data/
│   ├── emissions.db
├── my_folders.py
📁 output/
│   ├── flights_2025-05-01.csv
│   ├── simulated_flight_emissions.csv
├── README.md
📁 reports/
│   📁 2025-05-01/
│   │   ├── compliance_pie.png
│   │   ├── emissions_by_aircraft.png
│   │   ├── summary.docx
│   │   ├── summary_2025-05-01.csv
│   ├── summary_log.csv
├── requirements.txt
├── run_all.py

```

---

## 📈 Outputs
- `summary_YYYY-MM-DD.csv`: Daily KPI export
- `summary.docx`: Emissions report with charts
- `summary_log.csv`: Appended daily summary for trend analysis
- PNG plots: Emissions by aircraft, compliance breakdown

---

## 🧩 Future Improvements
- Integrate real-world API data (Eurocontrol, ICAO)
- Add emissions offset calculations and cost estimations
- Deploy the dashboard online (Heroku, Streamlit Cloud)
- Email or archive daily reports automatically

---

## 👤 Author
Daniel Lee Wilkinson  
[LinkedIn](https://www.linkedin.com/in/danielleewilkinson/)

