import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from pathlib import Path
import sqlite3
import traceback

# === Load data from SQLite ===
db_path = Path(__file__).resolve().parent.parent / "data" / "emissions.db"
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT * FROM flights", conn)
conn.close()

# Convert and clean types
df["date"] = pd.to_datetime(df["date"])
df["in_eea"] = df["in_eea"].astype(bool)
df["verified"] = df["verified"].astype(bool)
df["operator_compliant"] = df["operator_compliant"].astype(bool)

# === Dash app setup ===
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Emissions Compliance Dashboard"

# === Layout ===
app.layout = dbc.Container(
    [
        html.H1("Emissions Compliance Dashboard", className="my-4 text-center"),
        # Filters
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Select Operator:", className="fw-bold"),
                        dcc.Dropdown(
                            options=[
                                {"label": op, "value": op}
                                for op in ["All"] + sorted(df["operator_name"].unique())
                            ],
                            value="All",
                            id="operator-dropdown",
                        ),
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        html.Label("Select Date Range:", className="fw-bold"),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=df["date"].min(),
                            max_date_allowed=df["date"].max(),
                            start_date=df["date"].min(),
                            end_date=df["date"].max(),
                        ),
                    ],
                    width=8,
                ),
            ],
            className="mb-4",
        ),
        # KPI Cards
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Total Flights", className="card-title"),
                                html.H2(id="kpi-flights", className="card-text"),
                            ]
                        )
                    )
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("EEA Coverage", className="card-title"),
                                html.H2(id="kpi-eea", className="card-text"),
                            ]
                        )
                    )
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Verified Reports", className="card-title"),
                                html.H2(id="kpi-verified", className="card-text"),
                            ]
                        )
                    )
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Total CO₂ (t)", className="card-title"),
                                html.H2(id="kpi-emissions", className="card-text"),
                            ]
                        )
                    )
                ),
            ],
            className="mb-4",
        ),
        # Charts
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="emissions-by-aircraft"), width=6),
                dbc.Col(dcc.Graph(id="compliance-pie"), width=6),
            ]
        ),
    ],
    fluid=True,
)


# === Callback ===
@app.callback(
    Output("kpi-flights", "children"),
    Output("kpi-eea", "children"),
    Output("kpi-verified", "children"),
    Output("kpi-emissions", "children"),
    Output("emissions-by-aircraft", "figure"),
    Output("compliance-pie", "figure"),
    Input("operator-dropdown", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_dashboard(selected_operator, start_date, end_date):
    try:
        # Filter by operator and date range
        df_filtered = df.copy()
        if selected_operator != "All":
            df_filtered = df_filtered[df_filtered["operator_name"] == selected_operator]
        df_filtered = df_filtered[
            (df_filtered["date"] >= pd.to_datetime(start_date))
            & (df_filtered["date"] <= pd.to_datetime(end_date))
        ]

        # KPIs
        kpi_flights = len(df_filtered)
        kpi_eea = (
            f"{df_filtered['in_eea'].mean() * 100:.1f}%"
            if not df_filtered.empty
            else "0.0%"
        )
        kpi_verified = (
            f"{df_filtered['verified'].mean() * 100:.1f}%"
            if not df_filtered.empty
            else "0.0%"
        )
        kpi_emissions = f"{df_filtered['co2_emissions_kg'].sum() / 1000:.1f}"

        # Emissions by aircraft bar chart
        fig1 = px.bar(
            df_filtered.groupby("aircraft_type")["co2_emissions_kg"]
            .sum()
            .reset_index(),
            x="aircraft_type",
            y="co2_emissions_kg",
            title="CO₂ Emissions by Aircraft Type",
            labels={"co2_emissions_kg": "CO₂ (kg)"},
        )

        # Compliance pie chart
        if df_filtered["operator_compliant"].nunique() > 1:
            fig2 = px.pie(
                df_filtered,
                names="operator_compliant",
                title="Compliance Status Distribution",
                hole=0.4,
                labels={True: "Compliant", False: "Non-Compliant"},
            )
        else:
            fig2 = px.pie(
                names=["Only one class"],
                values=[1],
                title="Compliance Status Distribution",
                hole=0.4,
            )

        return kpi_flights, kpi_eea, kpi_verified, kpi_emissions, fig1, fig2

    except Exception as e:
        print("⚠️ Callback failed:")
        traceback.print_exc()
        fig_empty = px.bar(x=["Error"], y=[0], title="Error generating plot")
        return "Error", "Error", "Error", "Error", fig_empty, fig_empty


# === Run the app ===
if __name__ == "__main__":
    app.run(debug=True)

server = app.server
