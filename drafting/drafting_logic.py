import streamlit as st
import pandas as pd
import numpy as np
import random
from streamlit_gsheets import GSheetsConnection

def complete_draft(df):

    """
    
    The function follows a series of steps for each row:
        Step 1: Identify priority picks in row. 
        Step 2: Delete repeated priority picks in the rows below
        Step 3: Shift cells up, filling empty cells
        Step 4: Identify priority duplicates in row. 
        Break: Continue to next row if no duplicates found.
        Step 5: If duplicates, choose at random who keeps priority pick.
        Step 6: Shift cells up, deleting empty cells.
        Repeat: Repeat steps for row until Break condition is satisfied.
        
    """

    
    the_chosen_ones = [] # Create empty list to store 'chosen' players from step 5

    for row_index in range(len(df)): # For each row
        if row_index > len(df) - 1: # Stop when all rows processed
            break
        while True: # Ensure processing until Break condition satisfied
            
            #Step 1
            priority_values = set(df.iloc[row_index]) # Lock in priority picks
            
            # Step 2
            df.loc[row_index + 1:] = df.loc[row_index + 1:].map(lambda x: np.nan if x in priority_values else x) # Replace repeated priority pick values with NaN in rows below
            
            # Step 3
            df = df.apply(lambda col: col.dropna().reset_index(drop=True).reindex(df.index), axis=0) # For each column: push NaNs to bottom of dataframe
            df.dropna(how="all", inplace=True) # Remove NaN rows
        
            # Step 4
            row_values = df.iloc[row_index].value_counts() # Count priority row values
            duplicate_values = row_values[row_values > 1].index # Assess for duplicates
        
            # Break condition: Move onto next row if no duplicates
            if len(duplicate_values) == 0:
                break
        
            # Step 5
            for value in duplicate_values: 
                columns_to_modify = [col for col in df.columns if df.at[row_index, col] == value] # Identify columns containing duplicate
                the_chosen_one = columns_to_modify.pop(random.randint(0, len(columns_to_modify) - 1)) # Random choice to keep priority pick
                the_chosen_ones.append([str(row_index+1), the_chosen_one]) # Record the 'chosen' one in list
                
                # Step 6
                df.loc[row_index, columns_to_modify] = np.nan # Remove priority picks from other columns
                df[columns_to_modify] = df[columns_to_modify].apply(lambda col: col.dropna().reset_index(drop=True).reindex(df.index))
        
    # Repeat

    st.dataframe(df)
    
    st.cache_data.clear()
    conn = st.connection("gsheets", type=GSheetsConnection)
    conn.create(data=df, worksheet="test_final_draft") # Add final draft to gsheet
    
    chosen_df = pd.DataFrame(the_chosen_ones, columns=['round', 'player_name'])
    conn.create(data=chosen_df, worksheet="the_chosen_ones") # Add 'chosen ones' to gsheet