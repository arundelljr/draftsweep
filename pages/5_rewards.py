import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import numpy as np

# Control panel
st.cache_data.clear() # Clear cache so updated gs spreadsheet
conn = st.connection("gsheets", type=GSheetsConnection)
control_panel = conn.read(worksheet="friends_control_panel")

# Allow picking through control panel condition
if control_panel['Display rewards'][0] == 1:

    if st.button("Show the Winners"):
        st.cache_data.clear() # Clear cache so updated gs spreadsheet

        leaderboard_df = conn.read(worksheet="friends_leaderboard")
        round_scores_df = conn.read(worksheet="friends_round_scores")

        # Update rewards tracker
        
        # Numberfy all scores so total team scores can be calculated for each user
        leaderboard_df['total'] = leaderboard_df['total'].replace(to_replace=['E', '-'], value=0)
        leaderboard_df['total'] = leaderboard_df['total'].astype('int')
    
        # Numberfy all positions
        leaderboard_df['position'] = leaderboard_df['position'].map(lambda x: x if str(x).isdigit() else np.nan if str(x).isalpha() else np.nan if str(x) == "-" else int(str(x).strip('T')))
        
        # Calculate rewards

        # where leaderboard_df['position'] == 1 return all 'golfer' and 'user'
        winner_df = leaderboard_df.loc[leaderboard_df['position'] == 1, ['fullName', 'user']]
        st.write("Winner")
        st.dataframe(winner_df)
        # if leaderboard_df['position'] == 2 return all 'golfer' and 'user' else return np.nan
        second_df = leaderboard_df.loc[leaderboard_df['position'] == 2, ['fullName', 'user']]
        st.write("Second")
        st.dataframe(second_df)

        # Find golfers with lowest round score. Return golfer and user.
        lowest_round_scores_df = round_scores_df[round_scores_df['Score'] == round_scores_df.groupby('Round')['Score'].transform('min')]
        st.write("Lowest round scores")
        st.dataframe(lowest_round_scores_df)
        
        # where leaderboard_df['R1'] == .min() return all 'golfer' and 'user'
        #if 'R1' in leaderboard_df.columns:
         #   leaderboard_df['R1'] = leaderboard_df['R1'].astype('int')
          #  low_R1_df = leaderboard_df.loc[leaderboard_df['R1'] == leaderboard_df['R1'].min(), ['fullName', 'user']]
           # st.write("Lowest R1")
            #st.dataframe(low_R1_df)
        # where leaderboard_df['R2'] == .min() return all 'golfer' and 'user'
        #if 'R2' in leaderboard_df.columns:
         #   leaderboard_df['R2'] = leaderboard_df['R2'].astype('int')
          #  low_R2_df = leaderboard_df.loc[leaderboard_df['R2'] == leaderboard_df['R2'].min(), ['fullName', 'user']]
           # st.write("Lowest R2")
            #st.dataframe(low_R2_df)
        # where leaderboard_df['R3'] == .min() return all 'golfer' and 'user'
        #if 'R3' in leaderboard_df.columns:
         #   leaderboard_df['R3'] = leaderboard_df['R3'].astype('int')
          #  low_R3_df = leaderboard_df.loc[leaderboard_df['R3'] == leaderboard_df['R3'].min(), ['fullName', 'user']]
           # st.write("Lowest R3")
            #st.dataframe(low_R3_df)
        # where leaderboard_df['R4'] == .min() return all 'golfer' and 'user'
        #if 'R4' in leaderboard_df.columns:
         #   leaderboard_df['R4'] = leaderboard_df['R4'].astype('int')
          #  low_R4_df = leaderboard_df.loc[leaderboard_df['R4'] == leaderboard_df['R4'].min(), ['fullName', 'user']]
           # st.write("Lowest R4")
            #st.dataframe(low_R4_df)
        
        # where isAmateur & leaderboard_df['position'] == .min() return all 'golfer' and 'user'
        low_am_position = leaderboard_df.loc[leaderboard_df['isAmateur'], 'position'].min()
        low_am_df = leaderboard_df.loc[leaderboard_df['isAmateur'] & (leaderboard_df['position'] == low_am_position), ['fullName', 'user']]
        st.write("Lowest Amateur")
        st.dataframe(low_am_df)

        # where isLIV & leaderboard_df['position'] == .min() return all 'golfer' and 'user'
        low_LIV_position = leaderboard_df.loc[leaderboard_df['isLIV'], 'position'].min()
        low_LIV_df = leaderboard_df.loc[leaderboard_df['isLIV'] & (leaderboard_df['position'] == low_LIV_position), ['fullName', 'user']]
        st.write("Lowest LIV")
        st.dataframe(low_LIV_df)

    # DataFrame 


else:
    st.write("# Waiting for picks...")
    st.write("Thank you to:")
    st.cache_data.clear() # Clear cache so updated gs spreadsheet
    picks_df = conn.read(worksheet="friends_final_picks")
    for col in picks_df.columns:
        st.write(col)




#
# rewards_dict = {
#            'category' : ['1st', '2nd', 'lowest R1', 'lowest R2', 'lowest R3', 'lowest R4', 'lowest Amateur', 'lowest LIV'],
#            'golfers' : ['-', '-', '-', '-', '-', '-', '-', '-'], 
#            'users' : ['-', '-', '-', '-', '-', '-', '-', '-'], 
#            'money' : [80, 20, 10, 10, 10, 10, 10, 10]
#}

#rewards_dict = {
#            '1st' : [], 
#            '2nd' : [], 
#            'lowest R1' : [], 
#            'lowest R2': [], 
#            'lowest R3' : [], 
#            'lowest R4' : [], 
#            'lowest Amateur' : [], 
#            'lowest LIV' : []
#}


        
