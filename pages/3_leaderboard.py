import streamlit as st
from streamlit_gsheets import GSheetsConnection
import requests
import pandas as pd
from entry_list.entry_list import LIV_golfers

# Control panel
st.cache_data.clear() # Clear cache so updated gs spreadsheet
conn = st.connection("gsheets", type=GSheetsConnection)
control_panel = conn.read(worksheet="friends_control_panel")

# Allow picking through control panel condition
if control_panel['Update Leaderboard'][0] == 1:
    
    if st.button("Update Leaderboard"):
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

        # Parse main leaderboard
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
        draft_df = conn.read(worksheet="friends_final_draft")
        
        # Unpivot draft table so picks appear alongside user
        melted_draft_df = draft_df.melt(var_name='user', value_name='fullName')
        
        # Join users alongside their picks in leaderboard
        merged_df = web_app_leaderboard_df.merge(
            melted_draft_df,
            how='left',
            on='fullName'
        )

        # Parse round data
        # Lowest R1, lowest R2, lowest R3, lowest R4: Input from gssheets or Leaderboard or if today is thursday get min(currentRoundScore)
        round_scores = [
            {
            'fullName' : player['firstName'] + ' ' + player['lastName'],
            'Round' : rounds['roundId'],
            'Score' : rounds['scoreToPar']
            }
            for player in api_leaderboard_json
            for rounds in player['rounds']
        ]
        
        round_scores_df = pd.DataFrame(round_scores)
        
        # Upload leaderboards to gsheets
        conn = st.connection("gsheets", type=GSheetsConnection)
        conn.create(data=merged_df, worksheet="friends_leaderboard")
        conn.create(data=round_scores_df, worksheet="friends_round_scores")
        st.write("Leaderboard Updated")


elif control_panel['Display Leaderboards'][0] == 1:

    if st.button("Show Leaderboard"):
        st.cache_data.clear() # Clear cache so updated gs spreadsheet
        leaderboard_df = conn.read(worksheet="friends_leaderboard")
        
        st.write("# The Masters Leaderboard")
        st.dataframe(leaderboard_df, hide_index=True)

else:
    st.write("# Waiting for picks...")