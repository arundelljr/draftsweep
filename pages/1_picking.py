import streamlit as st
import pandas as pd
import numpy as np
import random
import requests
from streamlit_gsheets import GSheetsConnection
from entry_list.entry_list import all_golfers
from drafting.drafting_logic import complete_draft

# Control panel
conn = st.connection("gsheets", type=GSheetsConnection)
control_panel = conn.read(worksheet="friends_control_panel")


# Allow picking through control panel condition
if control_panel['Picking'][0] == 1:
    
    # Tournament entry list - this will be generated thorugh APIs
    
    st.header("Choose your top 15 picks below")
    
    name = st.text_input("Name")
    
    column1, column2, column3 = st.columns(3)
    
    
    with column1:
        pick1 = st.selectbox("Pick 1", all_golfers)
        pick2 = st.selectbox("Pick 2", all_golfers)
        pick3 = st.selectbox("Pick 3", all_golfers)
        pick4 = st.selectbox("Pick FORE", all_golfers)
        pick5 = st.selectbox("Pick 5", all_golfers)
    
    with column2:
        pick6 = st.selectbox("Pick 6", all_golfers)
        pick7 = st.selectbox("Pick 7", all_golfers)
        pick8 = st.selectbox("Pick 8", all_golfers)
        pick9 = st.selectbox("Pick 9", all_golfers)
        pick10 = st.selectbox("Pick 10", all_golfers)
    
    with column3:
        pick11 = st.selectbox("Pick 11", all_golfers)
        pick12 = st.selectbox("Pick 12", all_golfers)
        pick13 = st.selectbox("Pick 13", all_golfers)
        pick14 = st.selectbox("Pick 14", all_golfers)
        pick15 = st.selectbox("Pick 15", all_golfers)
    
    user_name = [name]
    top_picks = [pick1, pick2, pick3, pick4, pick5, pick6, pick7, pick8, pick9, pick10, pick11, pick12, pick13, pick14, pick15]
    
    def random_picks(all_golfers, top_picks, total_left):
        available_golfers = list(set(all_golfers) - set(top_picks))
        random_selected = random.sample(available_golfers, total_left)
        return top_picks + random_selected
        
    total_left = len(all_golfers) - len(top_picks)  # For example, if you need 15 total picks and have 10 top picks
    
    # Randomly fill out rest out team
    final_picks = random_picks(all_golfers, top_picks, total_left)
    # Write final team as Pandas DataFrame for draft process
    final_picks_df = pd.DataFrame(final_picks, columns=user_name)
    
    if len(set(top_picks)) != 15:
        st.write("### So nice you've picked him twice? Well that's not allowed, go back and re-pick!")
    else:
        st.write(f"### Big {pick1} fan are we? Great picks!")
        
        if st.button("Save Picks"):
            st.cache_data.clear() # Clear cache so updated gs spreadsheet
            google_sheets_df = conn.read(worksheet="friends_final_picks")
            next_column_index = len(google_sheets_df.columns) # Index number of new column
            google_sheets_df.insert(next_column_index, f'{name}', final_picks) # Use insert method to add new column
            conn.update(data=google_sheets_df, worksheet="friends_final_picks") # Save changes
            st.success("Picks Saved")
            st.write("We filled the rest out for you - have a look")
            st.dataframe(final_picks_df, width=225)
            

# Allow drafting through control panel
elif control_panel['Drafting'][0] == 1:
    if st.button("Complete Draft"):
        st.cache_data.clear() # Clear cache so reading updated gs spreadsheet
        final_picks = conn.read(worksheet="friends_final_picks")
        df = pd.DataFrame(final_picks)
        complete_draft(df, "friends_final_draft", "friends_the_chosen_ones")
        
else:
    st.write("# Check out the final draft, leaderboards and stats!")




