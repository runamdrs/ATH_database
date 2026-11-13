import streamlit as st

from athlete_service import search_athletes, get_skill_levels
from achievement_service import search_achievements, get_dates_earned

st.title("ATH")
st.write(
    "A platform where athletes build profiles, log workouts, share achievements, "
    "find people to train or play with, and earn Activity Points toward sponsor rewards."
)

section = st.sidebar.radio("Browse", ["Athletes", "Achievements"])

if section == "Athletes":
    st.header("Find Athletes")

    search = st.text_input("Search by name or username")
    skill_level = st.selectbox("Skill level", get_skill_levels())

    results = search_athletes(search, skill_level)

    st.dataframe(results)
    st.write(f"{len(results)} athlete(s) found.")

elif section == "Achievements":
    st.header("Browse Achievements")

    search = st.text_input("Search by achievement title")
    date_earned = st.selectbox("Date earned", get_dates_earned())

    results = search_achievements(search, date_earned)

    st.dataframe(results)
    st.write(f"{len(results)} achievement(s) found.")
