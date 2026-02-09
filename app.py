import streamlit as st
import pandas as pd
import requests
import plotly.express as px

def check_password():
    """Returns True if the user had the correct password."""
    if "password_correct" not in st.session_state:
        # First run, show the input
        st.text_input("Enter League Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Password was wrong, show input again
        st.text_input("Enter League Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        # Password was correct
        return True

def password_entered():
    """Checks whether a password entered by the user is correct."""
    if st.session_state["password"] == st.secrets["LEAGUE_PASSWORD"]:
        st.session_state["password_correct"] = True
        del st.session_state["password"]  # don't store password
    else:
        st.session_state["password_correct"] = False

# --- MAIN APP LOGIC ---
if check_password():
    st.title("🏆 Private League Dashboard")
    # All your Sleeper API and Analysis code goes here!
    # Use st.secrets["LEAGUE_ID"] instead of hardcoding it.



    st.title("My Fantasy League Dashboard")

# 1. Use your actual League ID here
LEAGUE_ID = "YOUR_LEAGUE_ID" 

@st.cache_data
def load_data(lid):
    try:
        # Fetch Users
        u_resp = requests.get(f"https://api.sleeper.app/v1/league/{lid}/users", timeout=5)
        # Fetch Rosters
        r_resp = requests.get(f"https://api.sleeper.app/v1/league/{lid}/rosters", timeout=5)
        
        if u_resp.status_code != 200 or r_resp.status_code != 200:
            return None, None, f"Sleeper API error (Status: {u_resp.status_code})"
            
        return u_resp.json(), r_resp.json(), None
    except Exception as e:
        return None, None, str(e)

# Run the loader
users, rosters, error = load_data(LEAGUE_ID)

if error:
    st.error(f"Couldn't load data: {error}")
    st.info("Check if your League ID is correct and you have internet access.")
elif not rosters:
    st.warning("League found, but it appears to have no rosters yet.")
else:
    # 2. Build the display data
    user_map = {u['user_id']: u['display_name'] for u in users}
    
    stats = []
    for r in rosters:
        stats.append({
            "Owner": user_map.get(r['owner_id'], "Unknown"),
            "Wins": r['settings'].get('wins', 0),
            "Losses": r['settings'].get('losses', 0),
            "Points For": r['settings'].get('fpts', 0)
        })

    df = pd.DataFrame(stats)
    st.write("### League Standings")
    st.dataframe(df, use_container_width=True)


    st.write("### The Luck Meter")
st.write("Who is winning despite their team, and who is losing despite their points?")

# Create a scatter plot
fig = px.scatter(
    df, 
    x="Points For", 
    y="Wins", 
    text="Owner",
    size="Wins",
    color="Wins",
    labels={"Points For": "Total Points Scored", "Wins": "Total Wins"},
    title="Points vs. Wins (Luck Analysis)"
)

# Adjust the text so it's not on top of the dots
fig.update_traces(textposition='top center')

# Draw a "Leaguewide Average" line (Optional but cool)
avg_points = df["Points For"].mean()
fig.add_vline(x=avg_points, line_dash="dash", line_color="red", annotation_text="Avg Points")

st.plotly_chart(fig, use_container_width=True)

# 4. The "Villain" Shoutout
villain = df.sort_values(by=["Wins", "Points For"], ascending=[False, True]).iloc[0]
st.warning(f"🚨 **League Villain Alert:** {villain['Owner']} has {villain['Wins']} wins despite their scoring!")