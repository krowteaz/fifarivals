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
# CORRECTED Power Ranking formula (matches your second image)
# --------------------------------------------------
def compute_power_ranking(row):

    if row["Pos"] == "GK":
        # GK Formula (assuming similar structure to second image)
        power_ranking = (
            row["PWR"] * 0.40 +
            row["Goalkeeping"] * 0.25 +
            row["Explosiveness"] * 0.15 +
            row["Defend"] * 0.10 +
            row["Pass"] * 0.05 +
            row["Speed"] * 0.05
        )
    else:
        # Outfield Player Formula (matching your second image)
        power_ranking = (
            row["PWR"] * 0.25 +
            row["Speed"] * 0.15 +
            row["Shoot"] * 0.20 +
            row["Dribble"] * 0.15 +
            row["Pass"] * 0.10 +
            row["Defend"] * 0.05 +
            row["Explosiveness"] * 0.10
        )
    
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

# Display options
st.sidebar.header("Display Options")
max_rows = st.sidebar.slider(
    "Number of players to display",
    min_value=10,
    max_value=min(500, len(df)),  # Allow up to 500 players
    value=min(100, len(df)),
    step=10
)

# Apply filters
filtered_df = df.copy()
if pos_filter:
    filtered_df = filtered_df[filtered_df["Pos"].isin(pos_filter)]

if rarity_filter:
    filtered_df = filtered_df[filtered_df["Rarity"].isin(rarity_filter)]

# Show top N players
filtered_df = filtered_df.head(max_rows)


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

# Add Goalkeeping column for GK rows
if "Goalkeeping" in df.columns:
    display_cols.append("Goalkeeping")

# Display stats
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Players", len(df))
with col2:
    st.metric("Players Displayed", len(filtered_df))
with col3:
    st.metric("Max Power Ranking", f"{filtered_df['Power Ranking'].max():.2f}")

# Format the Power Ranking column to show 2 decimal places
styled = filtered_df[display_cols].style.format({
    "Power Ranking": "{:.2f}",
    "PWR": "{:.0f}",
    "Speed": "{:.0f}",
    "Shoot": "{:.0f}",
    "Dribble": "{:.0f}",
    "Pass": "{:.0f}",
    "Defend": "{:.0f}",
    "Explosiveness": "{:.0f}"
}).background_gradient(
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
    use_container_width=True,
    height=600
)


st.caption(f"Live data from GitHub main branch - Showing {len(filtered_df)} players")

# Add download button
if st.button("📥 Download Full Rankings as CSV"):
    csv = df.to_csv(index=False)
    st.download_button(
        label="Click to Download",
        data=csv,
        file_name="player_power_rankings.csv",
        mime="text/csv"
    )
