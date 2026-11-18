import streamlit as st

from athlete_service import (
    search_athletes, get_skill_levels, get_athlete_options, get_athlete_details,
    add_athlete, edit_athlete, remove_athlete, SKILL_LEVELS,
)
from achievement_service import (
    search_achievements, get_dates_earned, get_sport_options, get_achievement_options,
    get_achievement_details, add_achievement, edit_achievement, remove_achievement,
)
from activity_service import (
    search_activities, get_activity_sports, get_activity_options, get_activity_details,
    add_activity, edit_activity, remove_activity,
)

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

    st.subheader("Manage Athletes")
    # The radio sits outside the form so the form re-renders when it changes.
    mode = st.radio("Action", ["Update", "Delete"], horizontal=True, key="athlete_mode")
    athlete_options = get_athlete_options()   # {AthleteID: "Name (@Username)"}

    if not athlete_options:
        st.info("No athletes available.")
    else:
        # The picker is outside the form too: widgets inside a form don't
        # rerun the page, so the fields below couldn't be pre-filled with
        # the chosen athlete's values. Users pick a name, never type an ID.
        athlete_id = st.selectbox(
            "Athlete",
            options=list(athlete_options),
            format_func=lambda athlete_id: athlete_options[athlete_id],
            key="manage_athlete_id",
        )
        current = get_athlete_details(athlete_id)

        with st.form("manage_athlete"):
            if mode == "Update":
                # The ID in each key gives every athlete fresh, pre-filled widgets.
                name = st.text_input("Name", value=current["Name"],
                                     key=f"athlete_name_{athlete_id}")
                username = st.text_input("Username", value=current["Username"],
                                         key=f"athlete_username_{athlete_id}")
                email = st.text_input("Email", value=current["Email"],
                                      key=f"athlete_email_{athlete_id}")
                location = st.text_input("Location (optional)", value=current["Location"] or "",
                                         key=f"athlete_location_{athlete_id}")
                new_skill_level = st.selectbox(
                    "Skill level",
                    SKILL_LEVELS,
                    index=SKILL_LEVELS.index(current["SkillLevel"])
                    if current["SkillLevel"] in SKILL_LEVELS else 0,
                    key=f"athlete_skill_{athlete_id}",
                )
            else:
                confirm = st.checkbox("Confirm deletion")
            submitted = st.form_submit_button(mode)

        if submitted:
            if mode == "Update":
                show_result(*edit_athlete(
                    athlete_id, name, username, email, location, new_skill_level,
                ))
            elif not confirm:
                st.warning("Please confirm deletion.")
            else:
                show_result(*remove_athlete(athlete_id))

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

    st.subheader("Manage Achievements")
    # The radio sits outside the form so the form re-renders when it changes.
    mode = st.radio("Action", ["Update", "Delete"], horizontal=True, key="achievement_mode")
    achievement_options = get_achievement_options()   # {AchievementID: "Title"}

    if not achievement_options:
        st.info("No achievements available.")
    else:
        # Outside the form so picking another achievement re-fills the fields.
        achievement_id = st.selectbox(
            "Achievement",
            options=list(achievement_options),
            format_func=lambda achievement_id: achievement_options[achievement_id],
            key="manage_achievement_id",
        )
        current = get_achievement_details(achievement_id)
        sport_choices = [None] + list(sport_options)

        with st.form("manage_achievement"):
            if mode == "Update":
                # The ID in each key gives every achievement fresh, pre-filled widgets.
                title = st.text_input("Title", value=current["Title"],
                                      key=f"achievement_title_{achievement_id}")
                description = st.text_area("Description (optional)",
                                           value=current["Description"] or "",
                                           key=f"achievement_description_{achievement_id}")
                athlete_id = st.selectbox(
                    "Athlete",
                    options=list(athlete_options),
                    index=list(athlete_options).index(current["AthleteID"]),
                    format_func=lambda athlete_id: athlete_options[athlete_id],
                    key=f"achievement_athlete_{achievement_id}",
                )
                sport_id = st.selectbox(
                    "Sport",
                    options=sport_choices,
                    index=sport_choices.index(current["SportID"])
                    if current["SportID"] in sport_choices else 0,
                    format_func=lambda sport_id: "None" if sport_id is None else sport_options[sport_id],
                    key=f"achievement_sport_{achievement_id}",
                )
                new_date_earned = st.date_input("Date earned", value=current["DateEarned"],
                                                key=f"achievement_date_{achievement_id}")
            else:
                confirm = st.checkbox("Confirm deletion")
            submitted = st.form_submit_button(mode)

        if submitted:
            if mode == "Update":
                show_result(*edit_achievement(
                    achievement_id, athlete_id, sport_id, title, description, new_date_earned,
                ))
            elif not confirm:
                st.warning("Please confirm deletion.")
            else:
                show_result(*remove_achievement(achievement_id))

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

    st.subheader("Manage Activities")
    # The radio sits outside the form so the form re-renders when it changes.
    mode = st.radio("Action", ["Update", "Delete"], horizontal=True, key="activity_mode")
    activity_options = get_activity_options()   # {ActivityID: "Type on Date"}

    if not activity_options:
        st.info("No activities available.")
    else:
        # Outside the form so picking another activity re-fills the fields.
        activity_id = st.selectbox(
            "Activity",
            options=list(activity_options),
            format_func=lambda activity_id: activity_options[activity_id],
            key="manage_activity_id",
        )
        current = get_activity_details(activity_id)

        with st.form("manage_activity"):
            if mode == "Update":
                # The ID in each key gives every activity fresh, pre-filled widgets.
                activity_type = st.text_input("Activity type (e.g. Soccer Practice)",
                                              value=current["Type"],
                                              key=f"activity_type_{activity_id}")
                athlete_id = st.selectbox(
                    "Organized by",
                    options=list(athlete_options),
                    index=list(athlete_options).index(current["AthleteID"]),
                    format_func=lambda athlete_id: athlete_options[athlete_id],
                    key=f"activity_athlete_{activity_id}",
                )
                sport_id = st.selectbox(
                    "Sport",
                    options=list(sport_options),
                    index=list(sport_options).index(current["SportID"]),
                    format_func=lambda sport_id: sport_options[sport_id],
                    key=f"activity_sport_{activity_id}",
                )
                date = st.date_input("Date", value=current["Date"],
                                     key=f"activity_date_{activity_id}")
                time = st.time_input("Start time", value=current["Time"],
                                     key=f"activity_time_{activity_id}")
                duration = st.number_input("Duration (minutes)", min_value=1,
                                           value=current["Duration"], step=5,
                                           key=f"activity_duration_{activity_id}")
                location = st.text_input("Location (optional)", value=current["Location"] or "",
                                         key=f"activity_location_{activity_id}")
                max_participants = st.number_input(
                    "Max participants (optional)", min_value=1,
                    value=current["MaxParticipants"], step=1,
                    key=f"activity_max_{activity_id}",
                )
            else:
                confirm = st.checkbox("Confirm deletion")
            submitted = st.form_submit_button(mode)

        if submitted:
            if mode == "Update":
                show_result(*edit_activity(
                    activity_id, athlete_id, sport_id, activity_type, date, time,
                    duration, location, max_participants,
                ))
            elif not confirm:
                st.warning("Please confirm deletion.")
            else:
                show_result(*remove_activity(activity_id))
