import streamlit as st

from athlete_service import (
    search_athletes, get_skill_levels, get_athlete_options, add_athlete, SKILL_LEVELS,
)
from achievement_service import (
    search_achievements, get_dates_earned, add_achievement,
)
from activity_service import search_activities, get_activity_sports, add_activity
from workout_service import list_workouts, add_workout, edit_workout, remove_workout
from sport_service import list_sports, get_sport_options, add_sport, edit_sport, remove_sport
from sponsor_service import list_sponsors, add_sponsor, edit_sponsor, remove_sponsor
from reward_redemption_service import (
    list_redemptions, list_rewards_for_athlete, redeem_reward,
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


section = st.sidebar.radio(
    "Browse",
    [
        "Athletes", "Achievements", "Activities", "Workouts",
        "Sports", "Sponsors", "Reward Redemptions",
    ],
)

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

elif section == "Workouts":
    st.header("Workouts")

    workouts = list_workouts()
    st.dataframe(workouts)

    athlete_options = get_athlete_options()
    if not athlete_options:
        st.warning("Add an athlete before creating a workout.")
    else:
        st.subheader("Add a Workout")
        with st.form("add_workout"):
            athlete_id = st.selectbox(
                "Athlete",
                options=list(athlete_options),
                format_func=lambda value: athlete_options[value],
            )
            scheduled_date = st.date_input("Scheduled date")
            workout_type = st.text_input("Workout type")
            duration = st.number_input(
                "Duration in minutes (optional)",
                min_value=1,
                value=None,
                step=1,
            )
            completion_status = st.text_input("Completion status")
            training_notes = st.text_area("Training notes (optional)")
            submitted = st.form_submit_button("Add Workout")

        if submitted:
            show_result(*add_workout(
                athlete_id, scheduled_date, workout_type, duration,
                completion_status, training_notes,
            ))

    if workouts:
        workout_options = {
            row["WorkoutID"]: (
                f'{row["ScheduledDate"]} - {row["WorkoutType"]} '
                f'({row["Athlete"]})'
            )
            for row in workouts
        }
        selected_workout_id = st.selectbox(
            "Select a workout to edit or delete",
            options=list(workout_options),
            format_func=lambda value: workout_options[value],
        )
        selected_workout = next(
            row for row in workouts if row["WorkoutID"] == selected_workout_id
        )

        st.subheader("Edit Workout")
        with st.form("edit_workout"):
            edit_athlete_id = st.selectbox(
                "Athlete",
                options=list(athlete_options),
                index=list(athlete_options).index(selected_workout["AthleteID"]),
                format_func=lambda value: athlete_options[value],
            )
            edit_scheduled_date = st.date_input(
                "Scheduled date", value=selected_workout["ScheduledDate"]
            )
            edit_workout_type = st.text_input(
                "Workout type", value=selected_workout["WorkoutType"]
            )
            edit_duration = st.number_input(
                "Duration in minutes (optional)",
                min_value=1,
                value=selected_workout["Duration"],
                step=1,
            )
            edit_completion_status = st.text_input(
                "Completion status", value=selected_workout["CompletionStatus"]
            )
            edit_training_notes = st.text_area(
                "Training notes (optional)",
                value=selected_workout["TrainingNotes"] or "",
            )
            submitted = st.form_submit_button("Save Workout")

        if submitted:
            show_result(*edit_workout(
                selected_workout_id, edit_athlete_id, edit_scheduled_date,
                edit_workout_type, edit_duration, edit_completion_status,
                edit_training_notes,
            ))

        st.subheader("Delete Workout")
        with st.form("delete_workout"):
            confirm_delete = st.checkbox(
                "I understand this workout will be deleted if no records depend on it."
            )
            submitted = st.form_submit_button("Delete Workout")

        if submitted:
            if confirm_delete:
                show_result(*remove_workout(selected_workout_id))
            else:
                st.error("Confirm the deletion before continuing.")

elif section == "Sports":
    st.header("Sports")

    sports = list_sports()
    st.dataframe(sports)

    st.subheader("Add a Sport")
    with st.form("add_sport"):
        name = st.text_input("Sport name")
        sport_type = st.text_input("Type")
        submitted = st.form_submit_button("Add Sport")

    if submitted:
        show_result(*add_sport(name, sport_type))

    if sports:
        sport_options = get_sport_options()
        selected_sport_id = st.selectbox(
            "Select a sport to edit or delete",
            options=list(sport_options),
            format_func=lambda value: sport_options[value],
        )
        selected_sport = next(
            row for row in sports if row["SportID"] == selected_sport_id
        )

        st.subheader("Edit Sport")
        with st.form("edit_sport"):
            edit_name = st.text_input("Sport name", value=selected_sport["Name"])
            edit_type = st.text_input("Type", value=selected_sport["Type"])
            submitted = st.form_submit_button("Save Sport")

        if submitted:
            show_result(*edit_sport(selected_sport_id, edit_name, edit_type))

        st.subheader("Delete Sport")
        with st.form("delete_sport"):
            confirm_delete = st.checkbox(
                "I understand this sport can only be deleted if it is not in use."
            )
            submitted = st.form_submit_button("Delete Sport")

        if submitted:
            if confirm_delete:
                show_result(*remove_sport(selected_sport_id))
            else:
                st.error("Confirm the deletion before continuing.")

elif section == "Sponsors":
    st.header("Sponsors")

    sponsors = list_sponsors()
    st.dataframe(sponsors)

    st.subheader("Add a Sponsor")
    with st.form("add_sponsor"):
        company = st.text_input("Company")
        sponsor_type = st.text_input("Sponsor type (optional)")
        contact_information = st.text_input("Contact information (optional)")
        submitted = st.form_submit_button("Add Sponsor")

    if submitted:
        show_result(*add_sponsor(company, sponsor_type, contact_information))

    if sponsors:
        sponsor_options = {
            row["SponsorID"]: row["Company"] for row in sponsors
        }
        selected_sponsor_id = st.selectbox(
            "Select a sponsor to edit or delete",
            options=list(sponsor_options),
            format_func=lambda value: sponsor_options[value],
        )
        selected_sponsor = next(
            row for row in sponsors if row["SponsorID"] == selected_sponsor_id
        )

        st.subheader("Edit Sponsor")
        with st.form("edit_sponsor"):
            edit_company = st.text_input(
                "Company", value=selected_sponsor["Company"]
            )
            edit_sponsor_type = st.text_input(
                "Sponsor type (optional)",
                value=selected_sponsor["SponsorType"] or "",
            )
            edit_contact_information = st.text_input(
                "Contact information (optional)",
                value=selected_sponsor["ContactInformation"] or "",
            )
            submitted = st.form_submit_button("Save Sponsor")

        if submitted:
            show_result(*edit_sponsor(
                selected_sponsor_id, edit_company, edit_sponsor_type,
                edit_contact_information,
            ))

        st.subheader("Delete Sponsor")
        with st.form("delete_sponsor"):
            confirm_delete = st.checkbox(
                "I understand this sponsor can only be deleted if no rewards depend on it."
            )
            submitted = st.form_submit_button("Delete Sponsor")

        if submitted:
            if confirm_delete:
                show_result(*remove_sponsor(selected_sponsor_id))
            else:
                st.error("Confirm the deletion before continuing.")

elif section == "Reward Redemptions":
    st.header("Reward Redemptions")

    redemptions = list_redemptions()
    st.dataframe(redemptions)

    athlete_options = get_athlete_options()
    if not athlete_options:
        st.warning("Add an athlete before submitting a redemption request.")
    else:
        athlete_id = st.selectbox(
            "Athlete",
            options=list(athlete_options),
            format_func=lambda value: athlete_options[value],
        )
        rewards = list_rewards_for_athlete(athlete_id)
        st.subheader("Reward eligibility")
        st.dataframe(rewards)
        st.caption(
            "Eligibility checks points, stock, and expiration. Submitting a "
            "request does not deduct points or reduce reward availability."
        )

        eligible_rewards = [
            reward for reward in rewards if reward["IsEligible"]
        ]
        if eligible_rewards:
            reward_options = {
                reward["RewardID"]: (
                    f'{reward["Description"]} — {reward["PointsRequired"]} '
                    f'points (sponsored by {reward["Sponsor"]})'
                )
                for reward in eligible_rewards
            }
            with st.form("redeem_reward"):
                reward_id = st.selectbox(
                    "Eligible reward",
                    options=list(reward_options),
                    format_func=lambda value: reward_options[value],
                )
                submitted = st.form_submit_button("Request Redemption")

            if submitted:
                show_result(*redeem_reward(athlete_id, reward_id))
        else:
            st.info("This athlete has no currently eligible rewards.")
