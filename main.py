import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import minimize

# --------------------------------------------------
# Page setup
# --------------------------------------------------
st.set_page_config(page_title="Player Power Ranking", layout="wide")

st.title("⚽ Player Power Ranking (Live from GitHub)")
st.subheader("📊 Reverse Engineered Formula")


# --------------------------------------------------
# CSV source
# --------------------------------------------------
GITHUB_CSV = "https://raw.githubusercontent.com/krowteaz/fifarivals/main/players.csv"


# --------------------------------------------------
# Known data from your image
# --------------------------------------------------
KNOWN_DATA = [
    {"name": "Luis Diaz", "PWR": 100, "Speed": 100, "Shoot": 99, "Dribble": 99, "Pass": 91, "Defend": 70, "Explosiveness": 101, "target": 101.41},
    {"name": "Mohamed Salah", "PWR": 100, "Speed": 98, "Shoot": 99, "Dribble": 97, "Pass": 97, "Defend": 75, "Explosiveness": 98, "target": 100.94},
    {"name": "Erling Haaland", "PWR": 100, "Speed": 99, "Shoot": 102, "Dribble": 96, "Pass": 81, "Defend": 83, "Explosiveness": 90, "target": 100.05},
    {"name": "Cristiano Ronaldo", "PWR": 100, "Speed": 95, "Shoot": 102, "Dribble": 98, "Pass": 78, "Defend": 76, "Explosiveness": 90, "target": 100.05},
    {"name": "Lionel Messi", "PWR": 100, "Speed": 91, "Shoot": 100, "Dribble": 100, "Pass": 102, "Defend": 76, "Explosiveness": 92, "target": 99.58},
    {"name": "Bukayo Saka", "PWR": 99, "Speed": 95, "Shoot": 97, "Dribble": 98, "Pass": 94, "Defend": 78, "Explosiveness": 97, "target": 99.48},
    {"name": "Harry Kane", "PWR": 99, "Speed": 85, "Shoot": 104, "Dribble": 96, "Pass": 100, "Defend": 71, "Explosiveness": 95, "target": 99.11},
    {"name": "Viktor Gyökeres", "PWR": 97, "Speed": 99, "Shoot": 96, "Dribble": 93, "Pass": 87, "Defend": 79, "Explosiveness": 95, "target": 98.13}
]


# --------------------------------------------------
# Reverse engineer weights using optimization
# --------------------------------------------------
def find_optimal_weights():
    """Use optimization to find weights that best match known data"""
    
    def objective(weights):
        """
        weights = [w_pwr, w_speed, w_shoot, w_dribble, w_pass, w_defend, w_explosiveness]
        """
        total_error = 0
        for player in KNOWN_DATA:
            calculated = (
                player["PWR"] * weights[0] +
                player["Speed"] * weights[1] +
                player["Shoot"] * weights[2] +
                player["Dribble"] * weights[3] +
                player["Pass"] * weights[4] +
                player["Defend"] * weights[5] +
                player["Explosiveness"] * weights[6]
            )
            error = (calculated - player["target"]) ** 2
            total_error += error
        return total_error
    
    # Initial guess - all weights equal
    initial_weights = [0.2, 0.1, 0.15, 0.1, 0.1, 0.05, 0.3]
    
    # Bounds: weights should be positive
    bounds = [(0, 1) for _ in range(7)]
    
    # Optimize
    result = minimize(objective, initial_weights, bounds=bounds, method='L-BFGS-B')
    
    return result.x


# Find optimal weights
optimal_weights = find_optimal_weights()

# Display the found weights
st.sidebar.header("🔍 Reverse Engineered Weights")
st.sidebar.write("Based on your 8 players:")
st.sidebar.write(f"PWR: {optimal_weights[0]:.3f}")
st.sidebar.write(f"Speed: {optimal_weights[1]:.3f}")
st.sidebar.write(f"Shoot: {optimal_weights[2]:.3f}")
st.sidebar.write(f"Dribble: {optimal_weights[3]:.3f}")
st.sidebar.write(f"Pass: {optimal_weights[4]:.3f}")
st.sidebar.write(f"Defend: {optimal_weights[5]:.3f}")
st.sidebar.write(f"Explosiveness: {optimal_weights[6]:.3f}")
st.sidebar.write(f"Total: {sum(optimal_weights):.3f}")


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
# Power Ranking formula with optimized weights
# --------------------------------------------------
def compute_power_ranking(row):
    if row["Pos"] == "GK":
        # For goalkeepers, use a simpler formula
        power_ranking = (
            row["PWR"] * 0.4 +
            row["Goalkeeping"] * 0.3 +
            row["Explosiveness"] * 0.3
        )
    else:
        power_ranking = (
            row["PWR"] * optimal_weights[0] +
            row["Speed"] * optimal_weights[1] +
            row["Shoot"] * optimal_weights[2] +
            row["Dribble"] * optimal_weights[3] +
            row["Pass"] * optimal_weights[4] +
            row["Defend"] * optimal_weights[5] +
            row["Explosiveness"] * optimal_weights[6]
        )
    
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
# Verification Table
# --------------------------------------------------
st.header("✅ Formula Verification")

# Create verification dataframe
verification_data = []
for player in KNOWN_DATA:
    player_row = df[df["Name"] == player["name"]]
    if not player_row.empty:
        calculated = player_row["Power Ranking"].values[0]
        verification_data.append({
            "Player": player["name"],
            "Calculated": calculated,
            "Target": player["target"],
            "Difference": calculated - player["target"],
            "Match": abs(calculated - player["target"]) < 0.1
        })

if verification_data:
    verification_df = pd.DataFrame(verification_data)
    
    # Style the verification table
    def color_difference(val):
        if abs(val) < 0.1:
            return 'background-color: #90EE90'
        elif abs(val) < 0.5:
            return 'background-color: #FFFF99'
        else:
            return 'background-color: #FFB6C6'
    
    styled_verification = verification_df.style.format({
        "Calculated": "{:.2f}",
        "Target": "{:.2f}",
        "Difference": "{:+.2f}"
    }).applymap(color_difference, subset=["Difference"])
    
    st.dataframe(styled_verification, use_container_width=True)
    
    # Calculate accuracy
    matches = verification_df["Match"].sum()
    accuracy = (matches / len(verification_df)) * 100
    st.metric("Accuracy on known players", f"{accuracy:.1f}%")
    
    # Show the formula used
    st.info(f"""
    **Formula used:**
    PWR × {optimal_weights[0]:.3f} + 
    Speed × {optimal_weights[1]:.3f} + 
    Shoot × {optimal_weights[2]:.3f} + 
    Dribble × {optimal_weights[3]:.3f} + 
    Pass × {optimal_weights[4]:.3f} + 
    Defend × {optimal_weights[5]:.3f} + 
    Explosiveness × {optimal_weights[6]:.3f}
    = **{sum(optimal_weights):.3f} total multiplier**
    """)


# --------------------------------------------------
# Main Display
# --------------------------------------------------
st.header("📊 Player Power Rankings")

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
    
else:
    st.warning("No players match the selected filters")

st.caption(f"Live data from GitHub main branch - Using reverse engineered weights")

# Add download button
if st.button("📥 Download Full Rankings as CSV"):
    csv = df.to_csv(index=False)
    st.download_button(
        label="Click to Download",
        data=csv,
        file_name="player_power_rankings.csv",
        mime="text/csv"
    )
