import streamlit as st
from streamlit_gsheets import GSheetsConnection
import requests
import pandas as pd
from entry_list.entry_list import LIV_golfers

# Control panel
st.cache_data.clear() # Clear cache so updated gs spreadsheet
conn = st.connection("gsheets", type=GSheetsConnection)
control_panel = conn.read(worksheet="family_control_panel")

# Allow picking through control panel condition
if control_panel['Request Leaderboard'][0] == 1:
    
    if st.button("Request Leaderboard"):
        st.cache_data.clear() # Clear cache so updated gs spreadsheet
        # API info
        url = st.secrets['api']['leaderboard_url']
        
        querystring = st.secrets['api']['masters']
        
        headers = {
        	"x-rapidapi-key": st.secrets['api']['key'],
        	"x-rapidapi-host": st.secrets['api']['host']
        }
        
        response = requests.get(url, headers=headers, params=querystring)
        
        response_json = response.json()

        # Leaderboard dataframe creation
        api_leaderboard_json = response_json["leaderboardRows"]
        api_leaderboard_df = pd.DataFrame(api_leaderboard_json)
        web_app_columns = ['position', 'firstName', 'lastName', 'total', 'currentRoundScore', 'thru', 'isAmateur']
        web_app_leaderboard_df = api_leaderboard_df[web_app_columns]
        
        # Join names
        fullNames = web_app_leaderboard_df['firstName'] + ' ' + web_app_leaderboard_df['lastName']
        web_app_leaderboard_df.insert(2, 'fullName', fullNames)
        web_app_leaderboard_df.drop(columns=['firstName', 'lastName'], inplace=True)

        # Create LIV golf dentification column
        web_app_leaderboard_df['isLIV'] = web_app_leaderboard_df['fullName'].isin(LIV_golfers)
        
        # Merge on users alongside their picks
        draft_df = conn.read(worksheet="family_final_draft")
        
        # Unpivot draft table so picks appear alongside user
        melted_draft_df = draft_df.melt(var_name='user', value_name='fullName')
        
        # Join users alongside their picks in leaderboard
        merged_df = web_app_leaderboard_df.merge(
            melted_draft_df,
            how='left',
            on='fullName'
        )
        
        # Upload leaderboard to gsheets
        conn = st.connection("gsheets", type=GSheetsConnection)
        conn.create(data=merged_df, worksheet="family_leaderboard")
        st.write("Leaderboard Updated")


elif control_panel['Display Leaderboards'][0] == 1:

    if st.button("Show Leaderboard"):
        st.cache_data.clear() # Clear cache so updated gs spreadsheet
        leaderboard_df = conn.read(worksheet="family_leaderboard")
        
        st.write("# The Masters Leaderboard")
        st.dataframe(leaderboard_df, hide_index=True)

else:
    st.write("# Waiting for picks...")