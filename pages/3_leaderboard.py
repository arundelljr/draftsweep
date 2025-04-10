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
        
        round_scores_df.loc[round_scores_df['Round'] == {'$numberInt': '1'}, ['Round']] = 1
        round_scores_df.loc[round_scores_df['Round'] == {'$numberInt': '2'}, ['Round']] = 2
        round_scores_df.loc[round_scores_df['Round'] == {'$numberInt': '3'}, ['Round']] = 3
        round_scores_df.loc[round_scores_df['Round'] == {'$numberInt': '4'}, ['Round']] = 4
        
        
        if len(round_scores) > 95:
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

        if len(round_scores) > 95:
            rounds_merged_df = merged_df.merge(
                round_scores_pivot_df,
                how='left',
                on='fullName'
            )

            # Update rewards tracker
            # Find lowest round scores
            round_scores_df.loc[round_scores_df['Score'] == 'E', ['Score']] = 0
            round_scores_df['Score'] = round_scores_df['Score'].astype('int')
        
            # return fullName and min(Score) for each round 
            lowest_round_scores_df = round_scores_df[round_scores_df['Score'] == round_scores_df.groupby('Round')['Score'].transform('min')]
            lowest_round_scores_df = lowest_round_scores_df.merge(
                melted_draft_df,
                how='left',
                on='fullName'
            )
        
        # Lowest Am: Where isAm == True, return golfer and username at min(position)
        # Lowest LIV: Where isLIV == True, return golfer and user of min(position)
        # low_am_df = merged_df.loc[merged_df['isAmateur'] & (merged_df['position'] == merged_df['isAmateur']['position'].min()), ['position', 'fullName', 'user']]
        # low_LIV_df = merged_df.loc[merged_df['isLIV'] & (merged_df['position'] == merged_df['isLIV']['position'].min()), ['position', 'fullName', 'user']]

        # Upload leaderboards to gsheets
        conn = st.connection("gsheets", type=GSheetsConnection)
        conn.create(data=merged_df, worksheet="friends_leaderboard")
        conn.create(data=round_scores_df, worksheet="friends_round_scores")
        # conn.create(data=lowest_round_scores_df, worksheet="friends_lowest_round_scores")
        # conn.create(data=low_am_df, worksheet="friends_low_am")
        # conn.create(data=low_LIV_df, worksheet="friends_low_LIV")
        st.write("Leaderboard Updated")


elif control_panel['Display Leaderboards'][0] == 1:

    if st.button("Show Leaderboard"):
        st.cache_data.clear() # Clear cache so updated gs spreadsheet
        leaderboard_df = conn.read(worksheet="friends_leaderboard")
        
        st.write("# The Masters Leaderboard")
        st.dataframe(leaderboard_df, hide_index=True)

else:
    st.write("# Waiting for picks...")
    st.write("Thank you to:")
    st.cache_data.clear() # Clear cache so updated gs spreadsheet
    picks_df = conn.read(worksheet="friends_final_picks")
    for col in picks_df.columns:
        st.write(col)