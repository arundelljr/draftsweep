import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Control panel
st.cache_data.clear() # Clear cache so updated gs spreadsheet
conn = st.connection("gsheets", type=GSheetsConnection)
control_panel = conn.read(worksheet="friends_control_panel")

# Allow picking through control panel condition
if control_panel['Display picks and draft'][0] == 1:
            
    if st.button("Show picks and drafts"):
        st.cache_data.clear() # Clear cache so updated gs spreadsheet
        picks_df = conn.read(worksheet="friends_final_picks")
        draft_df = conn.read(worksheet="friends_final_draft")
        st.write("### Final Draft")
        st.dataframe(draft_df)
        st.write("### Original Picks")
        st.dataframe(picks_df)
else:
    st.write("# Waiting for picks...")
    st.write("Thank you to:")
    st.cache_data.clear() # Clear cache so updated gs spreadsheet
    picks_df = conn.read(worksheet="friends_final_picks")
    for col in picks_df.columns:
        st.write(col)