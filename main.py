import streamlit as st
import pandas as pd

st.set_page_config(page_title="Player Power Ranking", layout="wide")

st.title("⚽ Player Power Ranking (Live from GitHub)")

# GitHub RAW CSV URL
GITHUB_CSV = "https://raw.githubusercontent.com/krowteaz/fifarivals/main/players.csv"


# Load data safely
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(GITHUB_CSV)

        # Ensure numeric columns are numeric
        numeric_cols = [
            "PWR",
            "Speed",
            "Shoot",
            "Dribble",
            "Pass",
            "Defend",
            "Explosiveness"
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        return df

    except Exception as e:
        st.error("Failed to load GitHub CSV")
        st.code(str(e))
        return pd.DataFrame()


# Correct formula that matches game Power Ranking
def compute_power_ranking(row):

    power_ranking = (
        row["Speed"] * 0.15 +
        row["Shoot"] * 0.19 +
        row["Dribble"] * 0.17 +
        row["Pass"] * 0.10 +
        row["Defend"] * 0.04 +
        row["Explosiveness"] * 0.25 +
        row["PWR"] * 0.10
    )

    return round(power_ranking, 2)


# Load data
df = load_data()

if df.empty:
    st.stop()


# Compute ranking
df["Power Ranking"] = df.apply(compute_power_ranking, axis=1)

df["Rank"] = df["Power Ranking"].rank(
    ascending=False,
    method="min"
).astype(int)

df = df.sort_values("Rank")


# Sidebar filters
st.sidebar.header("Filters")

pos = st.sidebar.multiselect(
    "Position",
    sorted(df["Pos"].dropna().unique())
)

rarity = st.sidebar.multiselect(
    "Rarity",
    sorted(df["Rarity"].dropna().unique())
)


if pos:
    df = df[df["Pos"].isin(pos)]

if rarity:
    df = df[df["Rarity"].isin(rarity)]


# Heatmap styling with fallback
try:

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

except Exception:

    st.dataframe(df, use_container_width=True)


st.caption("Live data from GitHub main branch")



