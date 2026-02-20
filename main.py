import streamlit as st
import pandas as pd

st.set_page_config(page_title="Player Power Ranking", layout="wide")

st.title("⚽ Player Power Ranking (Live from GitHub)")

# Your GitHub RAW CSV URL
GITHUB_CSV = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/data/players.csv"

# Power Ranking formula
WEIGHTS = {
    "PWR": 0.35,
    "Speed": 0.20,
    "Shoot": 0.15,
    "Dribble": 0.15,
    "Pass": 0.05,
    "Defend": 0.02,
    "Explosiveness": 0.35
}

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(GITHUB_CSV)
    return df

def compute_power_ranking(row):
    return round(
        row["PWR"] * WEIGHTS["PWR"] +
        row["Speed"] * WEIGHTS["Speed"] +
        row["Shoot"] * WEIGHTS["Shoot"] +
        row["Dribble"] * WEIGHTS["Dribble"] +
        row["Pass"] * WEIGHTS["Pass"] +
        row["Defend"] * WEIGHTS["Defend"] +
        row["Explosiveness"] * WEIGHTS["Explosiveness"],
        2
    )

df = load_data()

# Compute ranking
df["Power Ranking"] = df.apply(compute_power_ranking, axis=1)

df["Rank"] = df["Power Ranking"].rank(
    ascending=False,
    method="min"
).astype(int)

df = df.sort_values("Rank")

# Filters
pos = st.sidebar.multiselect("Position", df["Pos"].unique())
rarity = st.sidebar.multiselect("Rarity", df["Rarity"].unique())

if pos:
    df = df[df["Pos"].isin(pos)]

if rarity:
    df = df[df["Rarity"].isin(rarity)]

# Heatmap
styled = df.style.background_gradient(
    subset=[
        "Power Ranking",
        "Speed",
        "Shoot",
        "Dribble",
        "Pass",
        "Defend",
        "Explosiveness"
    ],
    cmap="RdYlGn"
)

st.dataframe(styled, use_container_width=True)

st.caption("Live data from GitHub master branch")
