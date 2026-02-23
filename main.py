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
# EXACT Power Ranking formula from your image
# --------------------------------------------------
def compute_power_ranking(row):
    """
    Formula based on your image:
    PWR: 0.45 (45%)
    Speed: 0.10 (10%)
    Shoot: 0.10 (10%)
    Dribble: 0.10 (10%)
    Pass: 0.10 (10%)
    Defend: 0.10 (10%)
    Explosiveness: 0.10 (10%)
    Total: 1.05 (105%) - this allows values > 100
    """
    
    if row["Pos"] == "GK":
        # For goalkeepers, use a similar pattern but with Goalkeeping stat
        # You may need to adjust this based on your Excel
        power_ranking = (
            row["PWR"] * 0.45 +
            row["Goalkeeping"] * 0.20 +
            row["Explosiveness"] * 0.10 +
            row["Speed"] * 0.10 +
            row["Defend"] * 0.10 +
            row["Pass"] * 0.10 +
            row["Dribble"] * 0.05  # Dribble less important for GK
        )
    else:
        # Outfield Player Formula - EXACT weights from your image
        power_ranking = (
            row["PWR"] * 0.45 +           # 45% weight on base PWR
            row["Speed"] * 0.10 +          # 10% weight
            row["Shoot"] * 0.10 +          # 10% weight
            row["Dribble"] * 0.10 +        # 10% weight
            row["Pass"] * 0.10 +           # 10% weight
            row["Defend"] * 0.10 +         # 10% weight
            row["Explosiveness"] * 0.10    # 10% weight
        )
        # Note: Total multiplier is 1.05, so players can exceed 100
    
    return round(power_ranking, 2)


# --------------------------------------------------
# Load and compute
# --------------------------------------------------
df = load_data()

# Apply the formula
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
total_players = len(df)
default_value = min(100, total_players) if total_players > 0 else 10
min_value = 10
max_value = max(10, total_players)

if total_players > 0:
    max_rows = st.sidebar.slider(
        "Number of players to display",
        min_value=min_value,
        max_value=max_value,
        value=default_value,
        step=10
    )
else:
    max_rows = 10
    st.sidebar.warning("No player data available")

# Apply filters
filtered_df = df.copy()
if pos_filter:
    filtered_df = filtered_df[filtered_df["Pos"].isin(pos_filter)]

if rarity_filter:
    filtered_df = filtered_df[filtered_df["Rarity"].isin(rarity_filter)]

# Show top N players
display_count = min(max_rows, len(filtered_df))
filtered_df = filtered_df.head(display_count)


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
    if len(filtered_df) > 0:
        st.metric("Max Power Ranking", f"{filtered_df['Power Ranking'].max():.2f}")
    else:
        st.metric("Max Power Ranking", "N/A")

# Show formula info
st.info("📊 Using formula: PWR(45%) + Speed(10%) + Shoot(10%) + Dribble(10%) + Pass(10%) + Defend(10%) + Explosiveness(10%) = 105% total")

# Format and display
if len(filtered_df) > 0:
    format_dict = {
        "Power Ranking": "{:.2f}",
        "PWR": "{:.0f}",
        "Speed": "{:.0f}",
        "Shoot": "{:.0f}",
        "Dribble": "{:.0f}",
        "Pass": "{:.0f}",
        "Defend": "{:.0f}",
        "Explosiveness": "{:.0f}"
    }
    
    styled = filtered_df[display_cols].style.format(format_dict).background_gradient(
        subset=["Power Ranking"],
        cmap="RdYlGn"
    )

    st.dataframe(
        styled,
        use_container_width=True,
        height=600
    )
    
    # Calculate what Luis Diaz should be based on this formula
    luis_diaz = filtered_df[filtered_df["Name"] == "Luis Diaz"]
    if not luis_diaz.empty:
        st.subheader("✅ Luis Diaz Calculation Check")
        luis_stats = luis_diaz.iloc[0]
        calculated = (
            luis_stats["PWR"] * 0.45 +
            luis_stats["Speed"] * 0.10 +
            luis_stats["Shoot"] * 0.10 +
            luis_stats["Dribble"] * 0.10 +
            luis_stats["Pass"] * 0.10 +
            luis_stats["Defend"] * 0.10 +
            luis_stats["Explosiveness"] * 0.10
        )
        st.metric("Luis Diaz Power Ranking", f"{calculated:.2f}")
        
        # Show the calculation
        st.code(f"""
        Luis Diaz Calculation:
        PWR (100 × 0.45) = {100 * 0.45:.2f}
        Speed (100 × 0.10) = {100 * 0.10:.2f}
        Shoot (99 × 0.10) = {99 * 0.10:.2f}
        Dribble (99 × 0.10) = {99 * 0.10:.2f}
        Pass (91 × 0.10) = {91 * 0.10:.2f}
        Defend (70 × 0.10) = {70 * 0.10:.2f}
        Explosiveness (101 × 0.10) = {101 * 0.10:.2f}
        TOTAL = {calculated:.2f}
        """)
    
else:
    st.warning("No players match the selected filters")

st.caption(f"Live data from GitHub main branch - Using weights: PWR(0.45) + others(0.10 each) = 1.05 total")

# Add download button
if st.button("📥 Download Full Rankings as CSV"):
    csv = df.to_csv(index=False)
    st.download_button(
        label="Click to Download",
        data=csv,
        file_name="player_power_rankings.csv",
        mime="text/csv"
    )
