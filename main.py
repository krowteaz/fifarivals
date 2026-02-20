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
# Load data - EXACTLY as it exists in the CSV
# --------------------------------------------------
@st.cache_data(ttl=60)
def load_data():

    df = pd.read_csv(GITHUB_CSV)

    # Only convert numeric columns, don't modify any values
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
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


# --------------------------------------------------
# Load data - NO CALCULATIONS, just use what's in the CSV
# --------------------------------------------------
df = load_data()

# Check if there's already a Power Ranking column in the CSV
if "Power Ranking" not in df.columns:
    # If not, check if there's a PWR column to use as fallback
    if "PWR" in df.columns:
        df["Power Ranking"] = df["PWR"]
    else:
        df["Power Ranking"] = 0
        st.warning("No Power Ranking or PWR column found in CSV")


# --------------------------------------------------
# Ranking based on existing Power Ranking values
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

if "Pos" in df.columns:
    pos_filter = st.sidebar.multiselect(
        "Position",
        sorted(df["Pos"].unique())
    )
else:
    pos_filter = []

if "Rarity" in df.columns:
    rarity_filter = st.sidebar.multiselect(
        "Rarity",
        sorted(df["Rarity"].unique())
    )
else:
    rarity_filter = []

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
# Display - SHOW EXACT CSV VALUES
# --------------------------------------------------
# Determine which columns to display (only those that exist in the CSV)
available_cols = ["Rank", "Power Ranking"] if "Power Ranking" in filtered_df.columns else ["Rank"]
available_cols.extend([col for col in ["Name", "Pos", "Nationality", "Rarity", "Season", "PWR", 
                                        "Speed", "Shoot", "Dribble", "Pass", "Defend", "Explosiveness", "Goalkeeping"]
                      if col in filtered_df.columns])

display_cols = available_cols

# Display stats
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Players", len(df))
with col2:
    st.metric("Players Displayed", len(filtered_df))
with col3:
    if len(filtered_df) > 0 and "Power Ranking" in filtered_df.columns:
        st.metric("Max Power Ranking", f"{filtered_df['Power Ranking'].max():.2f}")
    else:
        st.metric("Max Power Ranking", "N/A")

# Show raw data from CSV
st.subheader("📊 Raw Data from CSV (Exact Values)")

if len(filtered_df) > 0:
    # Create format dictionary for numeric columns
    format_dict = {}
    for col in filtered_df.columns:
        if col in ["PWR", "Speed", "Shoot", "Dribble", "Pass", "Defend", "Explosiveness", "Goalkeeping", "Power Ranking"]:
            if col in filtered_df.columns:
                format_dict[col] = "{:.2f}" if col == "Power Ranking" else "{:.0f}"
    
    # Style the dataframe
    if format_dict:
        styled = filtered_df[display_cols].style.format(format_dict)
        
        # Add gradient only if Power Ranking exists
        if "Power Ranking" in filtered_df.columns:
            styled = styled.background_gradient(
                subset=["Power Ranking"],
                cmap="RdYlGn"
            )
    else:
        styled = filtered_df[display_cols]

    st.dataframe(
        styled,
        use_container_width=True,
        height=600
    )
    
    # Show first few rows to verify
    st.subheader("🔍 First 5 Rows (Verify CSV Content)")
    st.dataframe(filtered_df.head(5), use_container_width=True)
    
else:
    st.warning("No players match the selected filters")

# Show column names to help debug
with st.expander("📋 CSV Column Names"):
    st.write(list(df.columns))

st.caption(f"Live data from GitHub main branch - Showing EXACT values from CSV")

# Add download button for raw data
if st.button("📥 Download Raw CSV Data"):
    csv = df.to_csv(index=False)
    st.download_button(
        label="Click to Download",
        data=csv,
        file_name="raw_player_data.csv",
        mime="text/csv"
    )
