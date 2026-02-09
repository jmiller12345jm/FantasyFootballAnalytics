import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# 1. AUTHENTICATION LOGIC
def check_password():
    if "password_correct" not in st.session_state:
        st.text_input("Enter League Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter League Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    return True

def password_entered():
    if st.session_state["password"] == st.secrets["LEAGUE_PASSWORD"]:
        st.session_state["password_correct"] = True
        del st.session_state["password"]
    else:
        st.session_state["password_correct"] = False

# --- MAIN APP LOGIC ---
if check_password():
    # Grab Secrets
    LEAGUE_ID = st.secrets["LEAGUE_ID"]

    # 2. DATA LOADING FUNCTION
    @st.cache_data(ttl=600)
    def load_data(lid):
        try:
            u_resp = requests.get(f"https://api.sleeper.app/v1/league/{lid}/users", timeout=5)
            r_resp = requests.get(f"https://api.sleeper.app/v1/league/{lid}/rosters", timeout=5)
            if u_resp.status_code == 200 and r_resp.status_code == 200:
                update_time = datetime.now().strftime("%H:%M:%S")
                return u_resp.json(), r_resp.json(), update_time, None
            return None, None, None, "Sleeper API Error"
        except Exception as e:
            return None, None, None, str(e)

    # Call the data once
    users, rosters, last_update, error = load_data(LEAGUE_ID)

    # 3. SIDEBAR (The Controls)
    with st.sidebar:
        st.title("⚙️ Settings")
        st.write(f"**League ID:** {LEAGUE_ID}")
        if last_update:
            st.write(f"🕒 **Last Sync:** {last_update}")
        
        if st.button("🔄 Force Refresh"):
            st.cache_data.clear()
            st.rerun()
        
        st.divider()
        st.info("Data is cached for 10 minutes to keep the app fast.")

    # 4. MAIN PAGE (The Analysis)
    st.title("🏆 Private League Dashboard")

    if error:
        st.error(f"Couldn't load data: {error}")
    elif not rosters:
        st.warning("League found, but it appears to have no rosters yet.")
    else:
        # Build Dataframe
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

        # Visuals
        st.write("### League Standings")
        st.dataframe(df, use_container_width=True)

        st.write("### The Luck Meter")
        fig = px.scatter(
            df, x="Points For", y="Wins", text="Owner",
            size="Wins", color="Wins",
            labels={"Points For": "Total Points Scored", "Wins": "Total Wins"},
            title="Points vs. Wins (Luck Analysis)"
        )
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)

        # Villain Alert
        villain = df.sort_values(by=["Wins", "Points For"], ascending=[False, True]).iloc[0]
        st.warning(f"🚨 **League Villain Alert:** {villain['Owner']} has {villain['Wins']} wins despite their scoring!")['Wins']} wins despite their scoring!")
