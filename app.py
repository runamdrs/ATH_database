import streamlit as st

from athlete_service import (
    search_athletes, get_skill_levels, get_athlete_options, add_athlete, SKILL_LEVELS,
)
from achievement_service import (
    search_achievements, get_dates_earned, get_sport_options, add_achievement,
)
from activity_service import search_activities, get_activity_sports, add_activity

st.title("ATH")
st.write(
    "A platform where athletes build profiles, log workouts, share achievements, "
    "find people to train or play with, and earn Activity Points toward sponsor rewards."
)


def show_result(success, message):
    """On success, remember the message and rerun so the table above
    refreshes with the new row. (st.success before st.rerun would be
    wiped out by the rerun, so the message is shown on the next run.)"""
    if success:
        st.session_state["flash"] = message
        st.rerun()
    else:
        st.error(message)


section = st.sidebar.radio("Browse", ["Athletes", "Achievements", "Activities"])

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

if section == "Athletes":
    st.header("Find Athletes")

    search = st.text_input("Search by name or username")
    skill_level = st.selectbox("Skill level", get_skill_levels())

    results = search_athletes(search, skill_level)

    st.dataframe(results)
    st.write(f"{len(results)} athlete(s) found.")

    st.subheader("Add an Athlete")
    with st.form("add_athlete"):
        name = st.text_input("Name")
        username = st.text_input("Username")
        email = st.text_input("Email")
        location = st.text_input("Location (optional)")
        new_skill_level = st.selectbox("Skill level", SKILL_LEVELS)
        submitted = st.form_submit_button("Add Athlete")

    if submitted:
        show_result(*add_athlete(name, username, email, location, new_skill_level))

elif section == "Achievements":
    st.header("Browse Achievements")

    search = st.text_input("Search by achievement title")
    date_earned = st.selectbox("Date earned", get_dates_earned())

    results = search_achievements(search, date_earned)

    st.dataframe(results)
    st.write(f"{len(results)} achievement(s) found.")

    st.subheader("Add an Achievement")
    athlete_options = get_athlete_options()   # {AthleteID: "Name (@Username)"}
    sport_options = get_sport_options()       # {SportID: "Sport name"}

    with st.form("add_achievement"):
        title = st.text_input("Title")
        description = st.text_area("Description (optional)")
        # The dropdown shows names but returns the AthleteID, so only
        # athletes that really exist can be chosen (foreign key safe).
        athlete_id = st.selectbox(
            "Athlete",
            options=list(athlete_options),
            format_func=lambda athlete_id: athlete_options[athlete_id],
        )
        sport_id = st.selectbox(
            "Sport",
            options=[None] + list(sport_options),
            format_func=lambda sport_id: "None" if sport_id is None else sport_options[sport_id],
        )
        new_date_earned = st.date_input("Date earned")
        submitted = st.form_submit_button("Add Achievement")

    if submitted:
        show_result(*add_achievement(athlete_id, sport_id, title, description, new_date_earned))

elif section == "Activities":
    st.header("Browse Activities")

    search = st.text_input("Search by activity type or location")
    sport = st.selectbox("Sport", get_activity_sports())

    results = search_activities(search, sport)

    st.dataframe(results)
    st.write(f"{len(results)} activity(ies) found.")

    st.subheader("Add an Activity")
    athlete_options = get_athlete_options()   # {AthleteID: "Name (@Username)"}
    sport_options = get_sport_options()       # {SportID: "Sport name"}

    with st.form("add_activity"):
        activity_type = st.text_input("Activity type (e.g. Soccer Practice)")
        # Dropdowns show names but return real IDs (foreign key safe).
        athlete_id = st.selectbox(
            "Organized by",
            options=list(athlete_options),
            format_func=lambda athlete_id: athlete_options[athlete_id],
        )
        # SportID is NOT NULL for activities, so there is no "None" option.
        sport_id = st.selectbox(
            "Sport",
            options=list(sport_options),
            format_func=lambda sport_id: sport_options[sport_id],
        )
        date = st.date_input("Date")
        time = st.time_input("Start time")
        duration = st.number_input("Duration (minutes)", min_value=1, value=60, step=5)
        location = st.text_input("Location (optional)")
        # value=None leaves the box empty, which is stored as NULL.
        max_participants = st.number_input(
            "Max participants (optional)", min_value=1, value=None, step=1
        )
        submitted = st.form_submit_button("Add Activity")

    if submitted:
        show_result(*add_activity(
            athlete_id, sport_id, activity_type, date, time, duration,
            location, max_participants,
        ))
