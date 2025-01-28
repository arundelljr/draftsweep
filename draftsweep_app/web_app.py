import streamlit as st
import pandas as pd
import requests
import numpy as np
import random
from streamlit_gsheets import GSheetsConnection

# Tournament entry list - this will be generated thorugh APIs

all_golfers = ['Nick Taylor', 'Nico Echavarria', 'J.J. Spaun', 'Stephan Jaeger', 'Eric Cole', 'Jackson Suber', 'Adam Schenk', 'Patrick Fishburn', 'Keegan Bradley', 'Jesper Svensson', 'Nick Dunlap', 'Paul Peterson', 'Russell Henley', 'Lee Hodges', 'Harry Hall', 'Hideki Matsuyama', 'Webb Simpson', 'Alex Smalley', 'Denny McCarthy', 'Gary Woodland', 'C.T. Pan', 'Sam Ryder', 'Mark Hubbard', 'Zach Johnson', 'Mac Meissner', 'Kensei Hirata', 'Matt Kuchar', 'Lucas Glover', 'Brian Harman', 'Adam Svensson', 'Brice Garnett', 'Sepp Straka', 'Andrew Putnam', 'Erik van Rooyen', 'Bud Cauley', 'Keith Mitchell', 'Nate Lashley', 'Vincent Norrman', 'Justin Lower', 'Kurt Kitayama', 'Sahith Theegala', 'Henrik Norlander', 'James Hahn', 'Ryan Gerard', 'Taylor Pendrith', 'Tom Hoge', 'Kevin Roy', 'Ben Griffin', 'Jeremy Paul', 'David Lipsky', 'Frankie Capan III', 'Maverick McNealy', 'Kevin Streelman', 'Brandt Snedeker', 'Thomas Detry', 'Chan Kim', 'Robert MacIntyre', 'Ben Kohles', 'Rico Hoey', 'Charley Hoffman', 'Ben Martin', 'Adam Hadwin', 'Sam Stevens', 'Thomas Rosenmueller', 'Matt McCarty', 'Taylor Montgomery', 'Tom Kim', 'Ryo Hisatsune', 'Ben Silverman', 'Cristobal Del Solar', 'Greyson Sigg', 'Doug Ghim', 'Luke List', 'Taylor Dickson', 'Vince Whaley', 'Aaron Baddeley', 'Brendon Todd', 'Billy Horschel', 'Patton Kizzire', 'Chad Ramey', 'Michael Kim', 'RJ Manke', 'David Skinns', 'Andrew Novak', 'Carson Young', 'Austin Eckroat', 'Byeong Hun An', 'J.T. Poston', 'Si Woo Kim', 'Jacob Bridgeman', 'Daniel Berger', 'Max McGreevy', 'Rafael Campos', 'Davis Thompson', 'Cam Davis', 'Emiliano Grillo', 'Corey Conners', 'Luke Clanton', 'Takumi Kanaya', 'Kaito Onishi', 'Steven Fisk', 'Patrick Rodgers', 'Alejandro Tosti', 'Braden Thornberry', 'Joel Dahmen', 'Ryan Palmer', 'Matti Schmid', 'Kevin Velo', 'Ricky Castillo', 'William Mouw', 'Noah Goodwin', 'Isaiah Salinda', 'Chris Kirk', 'Chris Gotterup', 'Nick Hardy', 'Mason Andersen', 'Danny Walker', 'Kris Ventura', 'Trevor Cone', 'Gavin Cohen', 'Harris English', 'Camilo Villegas', 'Rikuya Hoshino', 'Joe Highsmith', 'Yuta Sugiura', 'Tyler Loree', 'Will Gordon', 'Aldrich Potgieter', 'Quade Cummins', 'John Pak', 'Taylor Moore', 'Lanto Griffin', 'Ben Polland', 'Harry Higgs', 'K.H. Lee', 'Chandler Phillips', 'Seamus Power', 'Mao Matsuyama', 'Mackenzie Hughes', 'Peter Malnati', 'Kelly Welsh', 'Brian Campbell', 'Tim Widing']

st.header("Sony Open in Hawaii Draftsweep!")

name = st.text_input("Name")

column1, column2, column3 = st.columns(3)


with column1:
    pick1 = st.selectbox("Pick 1", all_golfers)
    pick2 = st.selectbox("Pick 2", all_golfers)
    pick3 = st.selectbox("Pick 3", all_golfers)
    pick4 = st.selectbox("Pick FORE!", all_golfers)
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

user = [name]
top_picks = [pick1, pick2, pick3, pick4, pick5, pick6, pick7, pick8, pick9, pick10, pick11, pick12, pick13, pick14, pick15]

def random_picks(all_golfers, top_picks, total_left):
    available_golfers = list(set(all_golfers) - set(top_picks))
    random_selected = random.sample(available_golfers, total_left)
    return top_picks + random_selected
    
total_left = len(all_golfers) - len(top_picks)  # For example, if you need 15 total picks and have 10 top picks

# Randomly fill out rest out team
final_draft = random_picks(all_golfers, top_picks, total_left)
# Write final team as Pandas DataFrame for draft process
df = pd.DataFrame(final_draft, columns=user)

if len(set(top_picks)) != 15:
    st.write("### So nice you've picked him twice? Well that's not allowed, go back and re-pick!")
else:
    st.write(f"### Big {pick1} fan are we? Great picks!")
    st.write("We've filled out the rest for you - hope you like 'em!")
    
    column4, column5 = st.columns([0.33, 0.67])

    with column4:
        st.dataframe(df, width=225)
    
    with column5:
        if st.button("Save Picks"):
            conn = st.connection("gsheets", type=GSheetsConnection)
            conn.create(worksheet=name, data=df)
            st.success("Picks Saved")

    


