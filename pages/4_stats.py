import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import numpy as np

# Control panel
st.cache_data.clear() # Clear cache so updated gs spreadsheet
conn = st.connection("gsheets", type=GSheetsConnection)
control_panel = conn.read(worksheet="friends_control_panel")

# Allow picking through control panel condition
if control_panel['Display stats'][0] == 1:

    if st.button("Who got lucky in the draft?"):
        
        st.cache_data.clear() # Clear cache so updated gs spreadsheet
        chosen_df = conn.read(worksheet="friends_the_chosen_ones")
        filtered_chosen_df = chosen_df[chosen_df['round'].astype('int') <= 5]
        
        column1, column2, column3 = st.columns(3)
        with column1:
            st.write("### Chosen ones") # Chosen at random by the draft to keep their pick
            st.dataframe(chosen_df, hide_index = True)
        with column2:
            st.write("### Most chosen") # Chosen the most by the random picker
            st.dataframe(chosen_df['player_name'].value_counts())
        with column3:
            st.write("### Clutch Chosen") # Number of times chosen during the first 5 rounds in the draft
            st.dataframe(filtered_chosen_df['player_name'].value_counts())
    
        picks_df = conn.read(worksheet="friends_final_picks")
        draft_df = conn.read(worksheet="friends_final_draft")
        top_picks_df = picks_df.head(15)
        top_draft_df = draft_df.head(15)
        
        # Find draft pick value in top picks, return top picks index value 
        pick_spread_dict = {}
        for p in top_draft_df.columns:
            find_values = top_draft_df[f"{p}"]
            matching_index = top_picks_df[top_picks_df[f"{p}"].isin(find_values)].index +1
            matching_index = matching_index.tolist()
            pick_spread_dict[f"{p}"] = matching_index
    
        st.write("### Pick spread") # Which picks did you end up with?
        pick_spread_df = pd.DataFrame({ key:pd.Series(value) for key, value in pick_spread_dict.items() })
        st.dataframe(pick_spread_df)

        st.write("### Pick distance") # Difference in where you asked for a pick vs where it came?
        pick_distance_df = pick_spread_df.apply(lambda col: col - (col.index + 1))
        pick_distance_stats_df = pick_distance_df.agg(['sum', 'mean'])
        st.dataframe(pick_distance_df)
        st.dataframe(pick_distance_stats_df)

        # Picked well? Got lucky? You decide
        best_picker = pick_distance_stats_df.loc['mean'].idxmin()
        st.write(f"{best_picker}: Picked well or got lucky? You decide")


    if st.button("Who's doing well?"):
        
        st.cache_data.clear() # Clear cache so updated gs spreadsheet
        leaderboard_df = conn.read(worksheet="friends_leaderboard")
        column1, column2, column3 = st.columns(3)
        
        # Numberfy all scores so total team scores can be calculated for each user
        leaderboard_df['total'] = leaderboard_df['total'].replace(to_replace=['E', '-'], value=0)
        leaderboard_df['total'] = leaderboard_df['total'].astype('int')
        team_totals_df = leaderboard_df.groupby(['user']).agg(team_score_total=('total', 'sum'))
        
        # Calulcate how many players cut for each team    
        cut_count_df = leaderboard_df.loc[leaderboard_df['position'].isin(['CUT', 'WD', '-']), ['user', 'position']].groupby(['user']).agg(cut_count=('position', 'count'))
        
        # Calculate sum of position for each team
        positions_df = leaderboard_df.loc[:, ['fullName', 'position']]
        draft_df = conn.read(worksheet="final_draft")
        
        # For every column in the draft pick, merge the picks' positions and collate back into a dataframe, keeping draft column and positions
        positions_dict = {}
        for p in draft_df.columns:
            merged_series = pd.merge(
                draft_df[p],
                positions_df,
                left_on=[p],
                right_on=['fullName']
            )
            positions_dict[p] = merged_series['position']
        
        draftsweep_leaderboard_df = pd.DataFrame(positions_dict)
        # st.write("### Team positions")
        # st.dataframe(draftsweep_leaderboard_df)
        agg_df = draftsweep_leaderboard_df.map(lambda x: x if str(x).isdigit() else np.nan if str(x).isalpha() else np.nan if str(x) == "-" else int(str(x).strip('T'))).agg(['sum'])
        t_agg_df = agg_df.T.rename(columns={'sum' : 'team_position_total'})

        # Display team scores, positions and cut counts
        with column1:
            st.write("### Total team scores")
            st.dataframe(team_totals_df)
        
        with column2:
            st.write("### Total team position")
            st.dataframe(t_agg_df)

        with column3:
            st.write("### Total team cut counts")
            st.dataframe(cut_count_df)
        

else:
    st.write("# Waiting for picks...")
    
        