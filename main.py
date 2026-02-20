import streamlit as st
import pandas as pd

# --------------------------------------------------
# Page setup
# --------------------------------------------------
st.set_page_config(page_title="Player Power Ranking", layout="wide")

st.title("⚽ Player Power Ranking (Live from GitHub)")
st.subheader("🔧 Manual Weight Tuning Mode")


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
# Sidebar - Manual Weight Controls
# --------------------------------------------------
st.sidebar.header("🎛️ Manual Weight Tuning")

# Create sliders for each weight
st.sidebar.subheader("Stat Weights (must sum to 1.00)")

w_pwr = st.sidebar.slider("PWR Weight", 0.0, 1.0, 0.25, 0.01)
w_speed = st.sidebar.slider("Speed Weight", 0.0, 1.0, 0.10, 0.01)
w_shoot = st.sidebar.slider("Shoot Weight", 0.0, 1.0, 0.15, 0.01)
w_dribble = st.sidebar.slider("Dribble Weight", 0.0, 1.0, 0.10, 0.01)
w_pass = st.sidebar.slider("Pass Weight", 0.0, 1.0, 0.08, 0.01)
w_defend = st.sidebar.slider("Defend Weight", 0.0, 1.0, 0.05, 0.01)
w_explosiveness = st.sidebar.slider("Explosiveness Weight", 0.0, 1.0, 0.27, 0.01)

# Calculate total
total_weight = w_pwr + w_speed + w_shoot + w_dribble + w_pass + w_defend + w_explosiveness
st.sidebar.metric("Total Weight", f"{total_weight:.2f}")

if abs(total_weight - 1.0) > 0.01:
    st.sidebar.warning(f"Weights should sum to 1.00 (currently {total_weight:.2f})")

# Baseline adjustment
st.sidebar.subheader("Baseline Adjustment")
baseline = st.sidebar.slider("Baseline Subtract", 0, 20, 0, 1)
multiplier = st.sidebar.slider("Multiplier", 0.8, 1.2, 1.0, 0.01)


# --------------------------------------------------
# Power Ranking formula with manual weights
# --------------------------------------------------
def compute_power_ranking(row):
    if row["Pos"] == "GK":
        # Simple GK formula for now
        return round(row["PWR"] * 0.4 + row["Goalkeeping"] * 0.6, 2)
    else:
        # Apply manual weights
        power = (
            row["PWR"] * w_pwr +
            row["Speed"] * w_speed +
            row["Shoot"] * w_shoot +
            row["Dribble"] * w_dribble +
            row["Pass"] * w_pass +
            row["Defend"] * w_defend +
            row["Explosiveness"] * w_explosiveness
        )
        
        # Apply baseline adjustment and multiplier
        power = (power - baseline) * multiplier
        
        return round(power, 2)


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
# Target Values Display
# --------------------------------------------------
st.sidebar.header("🎯 Target Values")
target_values = {
    "Luis Diaz": 101.41,
    "Mohamed Salah": 100.94,
    "Erling Haaland": 100.05,
    "Cristiano Ronaldo": 100.05,
    "Lionel Messi": 99.58,
    "Bukayo Saka": 99.48,
    "Harry Kane": 99.11,
    "Viktor Gyökeres": 98.13
}

for player, target in target_values.items():
    player_data = df[df["Name"] == player]
    if not player_data.empty:
        current = player_data["Power Ranking"].values[0]
        diff = current - target
        color = "green" if abs(diff) < 0.1 else "red"
        st.sidebar.markdown(f"**{player}**: {current:.2f} vs {target} (<span style='color:{color}'>{diff:+.2f}</span>)", unsafe_allow_html=True)


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
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Players", len(df))
with col2:
    st.metric("Players Displayed", len(filtered_df))
with col3:
    if len(filtered_df) > 0:
        st.metric("Max Power Ranking", f"{filtered_df['Power Ranking'].max():.2f}")
    else:
        st.metric("Max Power Ranking", "N/A")
with col4:
    st.metric("Current Weights Total", f"{total_weight:.2f}")

# Main display
if len(filtered_df) > 0:
    # Highlight Luis Diaz and other target players
    def highlight_targets(row):
        if row['Name'] in target_values:
            return ['background-color: #90EE90'] * len(row)
        return [''] * len(row)
    
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
    
    styled = filtered_df[display_cols].style.format(format_dict).apply(highlight_targets, axis=1).background_gradient(
        subset=["Power Ranking"],
        cmap="RdYlGn"
    )

    st.dataframe(
        styled,
        use_container_width=True,
        height=600
    )
    
    # Show current vs target for top players
    st.subheader("🎯 Current vs Target Values")
    comparison_data = []
    for player, target in target_values.items():
        player_row = df[df["Name"] == player]
        if not player_row.empty:
            comparison_data.append({
                "Player": player,
                "Current": player_row["Power Ranking"].values[0],
                "Target": target,
                "Difference": player_row["Power Ranking"].values[0] - target
            })
    
    if comparison_data:
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(
            comparison_df.style.format({
                "Current": "{:.2f}",
                "Target": "{:.2f}",
                "Difference": "{:+.2f}"
            }).background_gradient(subset=["Difference"], cmap="RdYlGn_r"),
            use_container_width=True
        )
    
else:
    st.warning("No players match the selected filters")

st.caption("Adjust the weights in the sidebar until the values match your Excel file exactly!")

# Add download button
if st.button("📥 Download Current Rankings"):
    csv = df.to_csv(index=False)
    st.download_button(
        label="Click to Download",
        data=csv,
        file_name="player_power_rankings.csv",
        mime="text/csv"
    )
