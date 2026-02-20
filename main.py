import streamlit as st
import pandas as pd

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Player Power Ranking",
    layout="wide"
)

st.title("⚽ Player Power Ranking (Live from GitHub)")


# --------------------------------------------------
# GitHub CSV source
# --------------------------------------------------
GITHUB_CSV = "https://raw.githubusercontent.com/krowteaz/fifarivals/main/players.csv"


# --------------------------------------------------
# Load data safely with caching
# --------------------------------------------------
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

        # Ensure numeric columns exist and are numeric
        for col in numeric_cols:

            if col not in df.columns:
                df[col] = 0

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).fillna(0)

        return df

    except Exception as e:

        st.error("Failed to load GitHub CSV")
        st.code(str(e))

        return pd.DataFrame()


# --------------------------------------------------
# Exact Power Ranking formula matching Excel
# --------------------------------------------------
def compute_power_ranking(row):

    # Goalkeeper formula
    if row["Pos"] == "GK":

        power_ranking = (
            row["Goalkeeping"] * 0.55 +
            row["Explosiveness"] * 0.15 +
            row["Defend"] * 0.10 +
            row["Pass"] * 0.08 +
            row["Speed"] * 0.07 +
            row["PWR"] * 0.05
        )

    # Field player formula (FW, MF, DF)
    else:

        power_ranking = (
            row["Explosiveness"] * 0.30 +
            row["Shoot"] * 0.22 +
            row["Speed"] * 0.18 +
            row["Dribble"] * 0.15 +
            row["Pass"] * 0.08 +
            row["Defend"] * 0.04 +
            row["PWR"] * 0.03
        )

    return round(power_ranking, 2)


# --------------------------------------------------
# Load data
# --------------------------------------------------
df = load_data()

if df.empty:
    st.stop()


# --------------------------------------------------
# Compute Power Ranking
# --------------------------------------------------
df["Power Ranking"] = df.apply(
    compute_power_ranking,
    axis=1
)


# --------------------------------------------------
# Compute Rank
# --------------------------------------------------
df["Rank"] = df["Power Ranking"].rank(
    ascending=False,
    method="min"
).astype(int)


# --------------------------------------------------
# Sort by rank
# --------------------------------------------------
df = df.sort_values("Rank")


# --------------------------------------------------
# Sidebar filters
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
# Columns to display
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
    "Explosiveness",
    "Goalkeeping"
]


# Only show columns that exist
display_cols = [
    col for col in display_cols if col in df.columns
]


# --------------------------------------------------
# Display table with heatmap
# --------------------------------------------------
try:

    styled = df[display_cols].style.background_gradient(
        subset=[
            col for col in [
                "Power Ranking",
                "Speed",
                "Shoot",
                "Dribble",
                "Pass",
                "Defend",
                "Explosiveness",
                "Goalkeeping"
            ] if col in df.columns
        ],
        cmap="RdYlGn"
    )

    st.dataframe(
        styled,
        use_container_width=True
    )

except:

    st.dataframe(
        df[display_cols],
        use_container_width=True
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------
st.caption("Live data from GitHub main branch")
