import streamlit as st
import pandas as pd
import numpy as np

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
# DEBUG: Let's try different formulas to find the match
# --------------------------------------------------
def compute_power_ranking_v1(row):
    """Original formula from your first image (base + bonus)"""
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
    return round(base + bonus, 2)

def compute_power_ranking_v2(row):
    """Weighted average formula"""
    if row["Pos"] == "GK":
        return round(
            row["PWR"] * 0.40 +
            row["Goalkeeping"] * 0.25 +
            row["Explosiveness"] * 0.15 +
            row["Defend"] * 0.10 +
            row["Pass"] * 0.05 +
            row["Speed"] * 0.05, 2
        )
    else:
        return round(
            row["PWR"] * 0.25 +
            row["Speed"] * 0.15 +
            row["Shoot"] * 0.20 +
            row["Dribble"] * 0.15 +
            row["Pass"] * 0.10 +
            row["Defend"] * 0.05 +
            row["Explosiveness"] * 0.10, 2
        )

def compute_power_ranking_v3(row):
    """Another possible formula - different weights"""
    if row["Pos"] == "GK":
        return round(
            row["PWR"] * 0.35 +
            row["Goalkeeping"] * 0.30 +
            row["Explosiveness"] * 0.15 +
            row["Defend"] * 0.10 +
            row["Pass"] * 0.05 +
            row["Speed"] * 0.05, 2
        )
    else:
        return round(
            row["PWR"] * 0.20 +
            row["Speed"] * 0.15 +
            row["Shoot"] * 0.25 +
            row["Dribble"] * 0.15 +
            row["Pass"] * 0.10 +
            row["Defend"] * 0.05 +
            row["Explosiveness"] * 0.10, 2
        )

def compute_power_ranking_v4(row):
    """Average of top stats formula"""
    if row["Pos"] == "GK":
        top_stats = sorted([
            row["Goalkeeping"], row["Explosiveness"], 
            row["Defend"], row["PWR"]
        ], reverse=True)[:3]
        return round(sum(top_stats) / 3, 2)
    else:
        top_stats = sorted([
            row["Shoot"], row["Speed"], row["Dribble"],
            row["Explosiveness"], row["PWR"]
        ], reverse=True)[:3]
        return round(sum(top_stats) / 3, 2)


# --------------------------------------------------
# Load and compute with ALL formulas for comparison
# --------------------------------------------------
df = load_data()

# Calculate all versions
df["PR_v1"] = df.apply(compute_power_ranking_v1, axis=1)
df["PR_v2"] = df.apply(compute_power_ranking_v2, axis=1)
df["PR_v3"] = df.apply(compute_power_ranking_v3, axis=1)
df["PR_v4"] = df.apply(compute_power_ranking_v4, axis=1)

# For now, use v2 as the main one (you can change this after debugging)
df["Power Ranking"] = df["PR_v2"]


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

# Formula selector for debugging
st.sidebar.header("Debug Options")
formula_version = st.sidebar.selectbox(
    "Power Ranking Formula",
    ["v1 (Original)", "v2 (Weighted Avg)", "v3 (Alt Weights)", "v4 (Top 3 Avg)"]
)

# Update which formula to display based on selection
if formula_version == "v1 (Original)":
    df["Power Ranking"] = df["PR_v1"]
elif formula_version == "v2 (Weighted Avg)":
    df["Power Ranking"] = df["PR_v2"]
elif formula_version == "v3 (Alt Weights)":
    df["Power Ranking"] = df["PR_v3"]
else:
    df["Power Ranking"] = df["PR_v4"]

# Re-rank based on selected formula
df["Rank"] = df["Power Ranking"].rank(ascending=False, method="min").astype(int)
df = df.sort_values("Rank")

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

# Add debug columns to see all formula versions
debug_cols = ["PR_v1", "PR_v2", "PR_v3", "PR_v4"]

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
    st.metric("Current Formula", formula_version)

# Create comparison table
if len(filtered_df) > 0:
    # Format all numeric columns
    format_dict = {
        "Power Ranking": "{:.2f}",
        "PWR": "{:.0f}",
        "Speed": "{:.0f}",
        "Shoot": "{:.0f}",
        "Dribble": "{:.0f}",
        "Pass": "{:.0f}",
        "Defend": "{:.0f}",
        "Explosiveness": "{:.0f}",
        "PR_v1": "{:.2f}",
        "PR_v2": "{:.2f}",
        "PR_v3": "{:.2f}",
        "PR_v4": "{:.2f}"
    }
    
    # Let user choose which columns to display
    show_debug = st.checkbox("Show all formula versions for comparison", value=False)
    
    if show_debug:
        display_with_debug = display_cols + debug_cols
    else:
        display_with_debug = display_cols
    
    styled = filtered_df[display_with_debug].style.format(format_dict).background_gradient(
        subset=[col for col in ["Power Ranking", "Speed", "Shoot", "Dribble", "Pass", "Defend", "Explosiveness"] 
                if col in display_with_debug],
        cmap="RdYlGn"
    )

    st.dataframe(
        styled,
        use_container_width=True,
        height=600
    )
    
    # Show sample comparison for top players
    st.subheader("🔍 Formula Comparison for Top Players")
    comparison_df = filtered_df.head(10)[["Name", "Pos", "PR_v1", "PR_v2", "PR_v3", "PR_v4"]].copy()
    st.dataframe(comparison_df.style.format("{:.2f}"), use_container_width=True)
    
else:
    st.warning("No players match the selected filters")

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
