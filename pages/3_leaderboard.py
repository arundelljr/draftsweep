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
    
    if st.button("Update Leaderboards"):
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
        
        round_scores_df['Round'].map(lambda x: 
                                     'R1' if x == {'$numberInt': '1'}
                                     else 'R2' if x == {'$numberInt': '2'}
                                     else 'R3' if x == {'$numberInt': '3'}
                                     else 'R4' if x == {'$numberInt': '4'}
                                     else x)
        
        
        if len(round_scores) >= 95:
            # round_scores_df = pd.DataFrame(round_scores)
            # Pivot round scores table so all rounds appear alongside golfer
            round_scores_pivot_df = round_scores_df.pivot(index='fullName', columns='Round', values='Score')
        
        # Parse main leaderboard
        api_leaderboard_df = pd.DataFrame(api_leaderboard_json)
        web_app_columns = ['position', 'firstName', 'lastName', 'total', 'currentRoundScore', 'thru', 'isAmateur']
        web_app_leaderboard_df = api_leaderboard_df[web_app_columns]
        
        # Join first and last names
        fullNames = web_app_leaderboard_df['firstName'] + ' ' + web_app_leaderboard_df['lastName']
        web_app_leaderboard_df.insert(2, 'fullName', fullNames)
        web_app_leaderboard_df = web_app_leaderboard_df.drop(columns=['firstName', 'lastName'])

        # Create LIV golf dentification column
        web_app_leaderboard_df['isLIV'] = web_app_leaderboard_df['fullName'].isin(LIV_golfers)
        
        # Unpivot draft table so picks appear alongside user
        draft_df = conn.read(worksheet="friends_final_draft")
        melted_draft_df = draft_df.melt(var_name='user', value_name='fullName')

        # Join users and round scores alongside golfers in leaderboard
        merged_df = web_app_leaderboard_df.merge(
            melted_draft_df,
            how='left',
            on='fullName'
        )

        if len(round_scores) >= 95:
            merged_df = merged_df.merge(
                round_scores_pivot_df,
                how='left',
                on='fullName'
            )

            # Update rewards tracker
            
            # Convert to int type.
            round_scores_df.loc[round_scores_df['Score'] == 'E', ['Score']] = 0
            round_scores_df['Score'] = round_scores_df['Score'].astype('int')
            
            # Find golfers with lowest round score. Return golfer and user.
            lowest_round_scores_df = round_scores_df[round_scores_df['Score'] == round_scores_df.groupby('Round')['Score'].transform('min')]
            lowest_round_scores_df = lowest_round_scores_df.merge(
                melted_draft_df,
                how='left',
                on='fullName'
            )
            
        
        # Upload leaderboards to gsheets
        conn = st.connection("gsheets", type=GSheetsConnection)
        conn.update(data=merged_df, worksheet="friends_leaderboard")
        conn.update(data=round_scores_df, worksheet="friends_round_scores")
        
        st.write("Leaderboard Updated")


elif control_panel['Display Leaderboards'][0] == 1:

    if st.button("Show Leaderboards"):
        st.cache_data.clear() # Clear cache so updated gs spreadsheet
        leaderboard_df = conn.read(worksheet="friends_leaderboard")
        
        st.write("# The Masters Leaderboard")
        st.dataframe(leaderboard_df, hide_index=True)
        
        # Leaderboard for each team
        columns = ['position', 'fullName', 'total',	'currentRoundScore', 'thru', 'isAmateur', 'isLIV']
        d = {}
        for user in leaderboard_df['user'].unique():
            d[user] = leaderboard_df.loc[leaderboard_df['user'] == user, columns]
            st.write(f"{user}'s Leaderboard")
            st.dataframe(d[user])

else:
    st.write("# Waiting for picks...")
    st.write("Thank you to:")
    st.cache_data.clear() # Clear cache so updated gs spreadsheet
    picks_df = conn.read(worksheet="friends_final_picks")
    for col in picks_df.columns:
        st.write(col)