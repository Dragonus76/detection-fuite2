import json

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import folium
import plotly.express as px

# Sensor metadata with positions around Casablanca
SENSORS = [
    {"name": "Sensor_A", "district": "Maarif", "lat": 33.589886, "lon": -7.603869},
    {"name": "Sensor_B", "district": "Sidi Belyout", "lat": 33.604355, "lon": -7.611380},
    {"name": "Sensor_C", "district": "Anfa", "lat": 33.580426, "lon": -7.642234},
]

DATA_FILE = "data_log.txt"


def load_css():
    """Load custom CSS for a consistent theme."""
    try:
        with open("static/streamlit.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def load_data() -> pd.DataFrame:
    """Load sensor readings from DATA_FILE and assign sensors."""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Assign sensors sequentially so each has some data
    names = [s["name"] for s in SENSORS]
    df["sensor"] = [names[i % len(names)] for i in range(len(df))]
    df["district"] = df["sensor"].map({s["name"]: s["district"] for s in SENSORS})
    return df


def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    """Filter dataframe based on sidebar selections."""
    st.sidebar.header("Filtres")
    districts = st.sidebar.multiselect(
        "District", df["district"].unique().tolist(), default=df["district"].unique().tolist()
    )
    sensors = st.sidebar.multiselect(
        "Capteur", df[df["district"].isin(districts)]["sensor"].unique().tolist(),
        default=df[df["district"].isin(districts)]["sensor"].unique().tolist(),
    )

    min_date = df["timestamp"].dt.date.min()
    max_date = df["timestamp"].dt.date.max()
    start_date, end_date = st.sidebar.date_input(
        "Plage de dates", [min_date, max_date], min_value=min_date, max_value=max_date
    )

    mask = (
        df["district"].isin(districts)
        & df["sensor"].isin(sensors)
        & (df["timestamp"].dt.date >= start_date)
        & (df["timestamp"].dt.date <= end_date)
    )
    return df[mask]


def draw_map(df: pd.DataFrame):
    """Display a Leaflet map with sensor markers."""
    st.subheader("Carte des capteurs")
    m = folium.Map(location=[33.589886, -7.603869], zoom_start=12)
    latest = df.sort_values("timestamp").groupby("sensor").tail(1)
    for sensor in SENSORS:
        folium.Marker(
            [sensor["lat"], sensor["lon"]],
            popup=f"{sensor['name']} ({sensor['district']})",
        ).add_to(m)
    st_folium(m, width=700, height=500)

    st.write("Dernières mesures")
    st.dataframe(latest[["timestamp", "sensor", "debit", "pression", "niveau_eau"]].reset_index(drop=True))


def draw_charts(df: pd.DataFrame):
    """Display dynamic charts using Plotly."""
    st.subheader("Évolution des mesures")
    fig = px.line(
        df,
        x="timestamp",
        y=["debit", "pression", "niveau_eau"],
        color="sensor",
        labels={"value": "Valeur", "timestamp": "Temps", "variable": "Mesure"},
    )
    st.plotly_chart(fig, use_container_width=True)


def main():
    st.title("Surveillance des fuites - Casablanca")
    load_css()
    df = load_data()
    filtered = filter_data(df)
    draw_map(filtered)
    draw_charts(filtered)


if __name__ == "__main__":
    main()
