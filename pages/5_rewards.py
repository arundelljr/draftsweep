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
        
        round_scores_df = conn.read(worksheet="friends_round_scores")
        lowest_round_scores_df = conn.read(worksheet="friends_lowest_round_scores")
        low_am_df = conn.read(worksheet="friends_low_am")
        low_LIV_df = conn.read(worksheet="friends_low_LIV")
    
    # DataFrame 


else:
    st.write("# Waiting for picks...")