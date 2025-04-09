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

    round_scores_df = conn.read(worksheet="friends_round_scores")
    # Find lowest round scores
    round_scores_df.loc[round_scores_df['Score'] == 'E', ['Score']] = 0
    round_scores_df['Score'] = round_scores_df['Score'].astype('int')
    
    # return fullName and min(Score) for each round 
    lowest_round_scores_df = round_df[round_df['Score'] == round_df.groupby('Round')['Score'].transform('min')]
    
    
    # Lowest Am: Where isAm == True, return golfer and username at min(position)
    # Lowest LIV: Where isLIV == True, return golfer and user of min(position)
    low_amateur_df = df.loc[df['isAmateur'] & (df['position'] == df['isAmateur']['position'].min()), ['position', 'fullName', 'user']]
    low_LIV_df = df.loc[df['isLIV'] & (df['position'] == df['isLIV']['position'].min()), ['position', 'fullName', 'user']]
    
    # DataFrame 


else:
    st.write("# Waiting for picks...")