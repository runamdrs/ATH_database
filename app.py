import streamlit as st
from achievement_service import search_achievements

st.title("Social Media App")
st.write("Welcome to the Social Media App!")

st.header("Search Anime")

search = st.text_input("Enter an anime title")

if st.button("Search"):
    st.write("Searching for:",search)

date_earned = st.selectbox(
    "Select a date earned", 
    ["2024-01-01", "2024-01-02", "2024-01-03"]
    )

filtered_achievements = search_achievements(search, date_earned)

import mysql.connector
from database import get_connection

if st.button("Test Connection"):
    try:
        connection = get_connection()
        st.write("Connected to the database")
        connection.close()
    except mysql.connector.Error as error:
        st.error(f"Connection Failed: {error}")