import streamlit as st
import pandas as pd

# --------------------------------------------------
# Page setup
# --------------------------------------------------
st.set_page_config(page_title="Player Power Ranking", layout="wide")

st.title("⚽ Player Power Ranking (Live from GitHub)")


# --------------------------------------------------
# CSV source
# --------------------------------------------------
GITHUB_CSV = "https://raw.githubusercontent.com/krowteaz/fifarivals/main/players.csv"


# --------------------------------------------------
# Load data
# --------------------------------------------------
@st.cache_data(ttl=60)
def load_data():

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

    for col in numeric_cols:

        if col not in df.columns:
            df[col] = 0

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

    return df


# --------------------------------------------------
# EXACT Power Ranking formula matching your table
# --------------------------------------------------
def compute_power_ranking(row):

    if row["Pos"] == "GK":

        weights = {
            "Goalkeeping": 0.40,
            "Explosiveness": 0.20,
            "Defend": 0.15,
            "Pass": 0.10,
            "Speed": 0.10,
            "PWR": 0.05
        }

        base = row["PWR"]

        bonus = (
            (row["Goalkeeping"] - base) * weights["Goalkeeping"] +
            (row["Explosiveness"] - base) * weights["Explosiveness"] +
            (row["Defend"] - base) * weights["Defend"] +
            (row["Pass"] - base) * weights["Pass"] +
            (row["Speed"] - base) * weights["Speed"]
        )

    else:

        weights = {
            "Explosiveness": 0.22,
            "Shoot": 0.18,
            "Speed": 0.14,
            "Dribble": 0.12,
            "Pass": 0.08,
            "Defend": 0.05
        }

        base = row["PWR"]

        bonus = (
            (row["Explosiveness"] - base) * weights["Explosiveness"] +
            (row["Shoot"] - base) * weights["Shoot"] +
            (row["Speed"] - base) * weights["Speed"] +
            (row["Dribble"] - base) * weights["Dribble"] +
            (row["Pass"] - base) * weights["Pass"] +
            (row["Defend"] - base) * weights["Defend"]
        )

    power_ranking = base + bonus

    return round(power_ranking, 2)


# --------------------------------------------------
# Load and compute
# --------------------------------------------------
df = load_data()

df["Power Ranking"] = df.apply(
    compute_power_ranking,
    axis=1
)


# --------------------------------------------------
# Ranking
# --------------------------------------------------
df["Rank"] = df["Power Ranking"].rank(
    ascending=False,
    method="min"
).astype(int)

df = df.sort_values("Rank")


# --------------------------------------------------
# Filters
# --------------------------------------------------
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


# --------------------------------------------------
# Display
# --------------------------------------------------
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


st.dataframe(
    styled,
    use_container_width=True
)


st.caption("Live data from GitHub main branch")
