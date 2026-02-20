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

    if row["Pos"] == "GK":

        core_avg = (
            row["Goalkeeping"] +
            row["Defend"] +
            row["Pass"] +
            row["Explosiveness"] +
            row["Speed"]
        ) / 5

        bonus = (
            (row["Goalkeeping"] - core_avg) * 0.35 +
            (row["Defend"] - core_avg) * 0.10 +
            (row["Explosiveness"] - core_avg) * 0.15
        )

    else:

        core_avg = (
            row["Speed"] +
            row["Shoot"] +
            row["Dribble"] +
            row["Pass"] +
            row["Defend"] +
            row["Explosiveness"]
        ) / 6

        bonus = (
            (row["Shoot"] - core_avg) * 0.25 +
            (row["Explosiveness"] - core_avg) * 0.30 +
            (row["Speed"] - core_avg) * 0.15
        )

    power_ranking = core_avg + bonus

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



