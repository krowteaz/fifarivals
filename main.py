import streamlit as st
import pandas as pd

st.set_page_config(page_title="Player Power Ranking", layout="wide")

st.title("⚽ Player Power Ranking (Live from GitHub)")

# GitHub RAW CSV
GITHUB_CSV = "https://raw.githubusercontent.com/krowteaz/fifarivals/main/players.csv"


# Load CSV safely
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(GITHUB_CSV)

        numeric_cols = [
            "PWR",
            "Speed",
            "Shoot",
            "Dribble",
            "Pass",
            "Defend",
            "Explosiveness",
            "Goalkeeping"
        ]

        # Ensure numeric
        for col in numeric_cols:
            if col not in df.columns:
                df[col] = 0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        return df

    except Exception as e:
        st.error("Failed to load CSV from GitHub")
        st.code(str(e))
        return pd.DataFrame()


# Correct Power Ranking formula
def compute_power_ranking(row):

    # GK formula
    if row["Pos"] == "GK":

        power_ranking = (
            row["Goalkeeping"] * 0.45 +
            row["Defend"] * 0.15 +
            row["Pass"] * 0.10 +
            row["Explosiveness"] * 0.10 +
            row["Speed"] * 0.05 +
            row["PWR"] * 0.15
        )

    # FW, MF, DF formula
    else:

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


# Compute Power Ranking
df["Power Ranking"] = df.apply(compute_power_ranking, axis=1)


# Compute Rank
df["Rank"] = df["Power Ranking"].rank(
    ascending=False,
    method="min"
).astype(int)


# Sort by Rank
df = df.sort_values("Rank")


# Sidebar filters
st.sidebar.header("Filters")

pos_filter = st.sidebar.multiselect(
    "Position",
    sorted(df["Pos"].unique())
)

rarity_filter = st.sidebar.multiselect(
    "Rarity",
    sorted(df["Rarity"].unique())
)

if pos_filter:
    df = df[df["Pos"].isin(pos_filter)]

if rarity_filter:
    df = df[df["Rarity"].isin(rarity_filter)]


# Display columns
display_cols = [
    "Rank",
    "Power Ranking",
    "Name",
    "Pos",
    "Nationality",
    "Rarity",
    "Season",
    "PWR",
    "Speed",
    "Shoot",
    "Dribble",
    "Pass",
    "Defend",
    "Explosiveness"
]

if "Goalkeeping" in df.columns:
    display_cols.append("Goalkeeping")


# Heatmap styling
try:

    styled = df[display_cols].style.background_gradient(
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

    st.dataframe(df[display_cols], use_container_width=True)


st.caption("Live data from GitHub main branch")
