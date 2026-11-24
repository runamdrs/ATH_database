import streamlit as st

from services.athlete_service import (
    search_athletes, get_skill_levels, get_athlete_options, get_athlete_details,
    get_athlete_sport_ids, find_athlete_id, add_athlete, edit_athlete, remove_athlete,
    SKILL_LEVELS,
)
from services.achievement_service import (
    search_achievements, get_dates_earned, get_achievement_options,
    get_achievement_details, add_achievement, edit_achievement, remove_achievement,
)
from services.activity_service import (
    search_activities, get_activity_sports, get_activity_options, get_activity_details,
    add_activity, edit_activity, remove_activity,
    list_roster, get_participant_options, get_participant_details, is_organizer,
    join_activity, change_participation_status, remove_participant,
    PARTICIPATION_STATUSES,
)
from services.workout_service import (
    list_workouts, get_workout_options, get_workout_details,
    add_workout, edit_workout, remove_workout,
)
from services.sport_service import (
    list_sports, get_sport_options, get_sport_details,
    add_sport, edit_sport, remove_sport,
)
from services.sponsor_service import (
    list_sponsors, get_sponsor_options, get_sponsor_details,
    add_sponsor, edit_sponsor, remove_sponsor,
)
from services.recruiter_interest_service import (
    list_interest_for_athlete, get_recruiter_options, get_interest_options,
    get_interest_details, express_interest, edit_interest, remove_interest,
    INTEREST_STATUSES,
)
from services.post_service import (
    list_posts, get_post_options, list_comments, add_post,
    get_comment_options, get_comment_details,
    add_comment, edit_comment, remove_comment,
)
from services.point_service import (
    list_points, get_point_options, get_point_details,
    add_point, edit_point, remove_point,
)
from services.reward_redemption_service import (
    list_redemptions, list_rewards_for_athlete, redeem_reward,
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


def main():
    """Draw the whole ATH interface. app.py in the project root is the
    entry point that calls this, so the interface lives in one place
    and launching the app does not depend on this file's location."""
    st.title("ATH")
    st.write(
        "A platform where athletes build profiles, log workouts, share achievements, "
        "find people to train or play with, and earn Activity Points toward sponsor rewards."
    )

    # Simulated login: the athlete picked here is the current user. New
    # content is saved under their ID, and Manage sections only offer
    # their own records. The key keeps the choice across page changes.
    athlete_options = get_athlete_options()   # {AthleteID: "Name (@Username)"}

    # After a sign-up, log the new athlete in. A widget's value can only
    # be set before the widget is drawn, so the sign-up below leaves the
    # new ID in "login_as" and it is applied here on the next run.
    if st.session_state.get("login_as") in athlete_options:
        st.session_state["current_athlete_id"] = st.session_state.pop("login_as")
    # After deleting their own account the user is logged out, and the
    # dropdown falls back to the first athlete in the list.
    if st.session_state.pop("logged_out", False):
        st.session_state.pop("current_athlete_id", None)

    if athlete_options:
        current_id = st.sidebar.selectbox(
            "Logged in as",
            options=list(athlete_options),
            format_func=lambda athlete_id: athlete_options[athlete_id],
            key="current_athlete_id",
        )
    else:
        current_id = None
        st.sidebar.info("Create a profile under the page menu to log in.")

    section = st.sidebar.radio(
        "Browse",
        [
            "Athletes", "Achievements", "Activities", "Workouts", "Points",
            "Sports", "Sponsors", "Posts", "Reward Redemptions",
        ],
    )

    # Signing up is how a new user gets a profile, so it lives in the
    # sidebar (below the page menu), not on the Athletes page as
    # something athletes do.
    sport_options = get_sport_options()       # {SportID: "Sport name"}
    with st.sidebar.expander("New here? Create a profile",
                             expanded=not athlete_options):
        with st.form("sign_up"):
            name = st.text_input("Name")
            username = st.text_input("Username")
            email = st.text_input("Email")
            location = st.text_input("Location (optional)")
            new_skill_level = st.selectbox("Skill level", SKILL_LEVELS)
            # One athlete_sport row is saved per sport picked here.
            sport_ids = st.multiselect(
                "Sports (optional)",
                options=list(sport_options),
                format_func=lambda sport_id: sport_options[sport_id],
            )
            submitted = st.form_submit_button("Create Profile")

        if submitted:
            success, message = add_athlete(
                name, username, email, location, new_skill_level, sport_ids,
            )
            if success:
                st.session_state["login_as"] = find_athlete_id(username)
                show_result(True, message + " You are now logged in.")
            else:
                st.error(message)

    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))

    # Every page except these belongs to a user, so without anyone to
    # log in as there is nothing to show (and no content can exist yet).
    if current_id is None and section not in ("Athletes", "Sports", "Sponsors"):
        st.info("Log in from the sidebar first: create a profile there to start.")
        return

    if section == "Athletes":
        st.header("Find Athletes")

        search = st.text_input("Search by name or username")
        skill_level = st.selectbox("Skill level", get_skill_levels())

        results = search_athletes(search, skill_level)

        st.dataframe(results)
        st.write(f"{len(results)} athlete(s) found.")

        # New profiles are created from the sidebar (sign-up), so this page
        # only browses athletes and manages the logged-in athlete's own.
        st.subheader("Manage My Profile")
        # The radio sits outside the form so the form re-renders when it changes.
        mode = st.radio("Action", ["Update", "Delete"], horizontal=True, key="athlete_mode")

        if current_id is None:
            st.info("No athletes available.")
        else:
            # Users may only change their own profile, so there is no
            # picker: the profile is the one logged in from the sidebar.
            athlete_id = current_id
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
                    sport_ids = st.multiselect(
                        "Sports (optional)",
                        options=list(sport_options),
                        default=[sport_id for sport_id in get_athlete_sport_ids(athlete_id)
                                 if sport_id in sport_options],
                        format_func=lambda sport_id: sport_options[sport_id],
                        key=f"athlete_sports_{athlete_id}",
                    )
                else:
                    # Deleting an athlete also deletes everything that
                    # references them, so the checkbox spells that out.
                    st.warning(
                        "Deleting your profile also deletes your activities, "
                        "workouts, achievements, posts, comments, points, "
                        "redemptions and sport/recruiter links."
                    )
                    confirm = st.checkbox("Confirm deletion")
                submitted = st.form_submit_button(mode)

            if submitted:
                if mode == "Update":
                    show_result(*edit_athlete(
                        athlete_id, name, username, email, location, new_skill_level,
                        sport_ids,
                    ))
                elif not confirm:
                    st.warning("Please confirm deletion.")
                else:
                    success, message = remove_athlete(athlete_id)
                    if success:
                        # The account is gone, so log out (see the top of main()).
                        st.session_state["logged_out"] = True
                    show_result(success, message)

        st.subheader("Recruiter Interest")
        recruiter_options = get_recruiter_options()   # {RecruiterID: "Name (Org)"}

        if not athlete_options or not recruiter_options:
            st.info("Recruiter interest needs at least one athlete and one recruiter.")
        else:
            # Outside the forms so the list and both forms follow the athlete.
            interest_athlete_id = st.selectbox(
                "Athlete",
                options=list(athlete_options),
                format_func=lambda athlete_id: athlete_options[athlete_id],
                key="interest_athlete_id",
            )
            st.dataframe(list_interest_for_athlete(interest_athlete_id))

            # A new interest always starts as "Interested", dated today, so
            # only the recruiter and the notes are asked for.
            with st.form("express_interest"):
                recruiter_id = st.selectbox(
                    "Recruiter",
                    options=list(recruiter_options),
                    format_func=lambda recruiter_id: recruiter_options[recruiter_id],
                )
                notes = st.text_area("Notes (optional)")
                submitted = st.form_submit_button("Express Interest")

            if submitted:
                show_result(*express_interest(recruiter_id, interest_athlete_id, notes))

            st.subheader("Manage Recruiter Interest")
            # The radio sits outside the form so the form re-renders when it changes.
            mode = st.radio("Action", ["Update", "Delete"], horizontal=True,
                            key="interest_mode")
            interest_options = get_interest_options(interest_athlete_id)

            if not interest_options:
                st.info("No recruiter has shown interest in this athlete yet.")
            else:
                interest_recruiter_id = st.selectbox(
                    "Recruiter",
                    options=list(interest_options),
                    format_func=lambda recruiter_id: interest_options[recruiter_id],
                    key="manage_interest_recruiter_id",
                )
                current = get_interest_details(interest_recruiter_id, interest_athlete_id)

                with st.form("manage_interest"):
                    if mode == "Update":
                        # Both IDs in the key give every interest fresh, pre-filled widgets.
                        widget_id = f"{interest_recruiter_id}_{interest_athlete_id}"
                        new_status = st.selectbox(
                            "Status",
                            INTEREST_STATUSES,
                            index=INTEREST_STATUSES.index(current["Status"])
                            if current["Status"] in INTEREST_STATUSES else 0,
                            key=f"interest_status_{widget_id}",
                        )
                        new_notes = st.text_area("Notes (optional)",
                                                 value=current["Notes"] or "",
                                                 key=f"interest_notes_{widget_id}")
                    else:
                        # No table references recruiter_athlete, so nothing else goes.
                        confirm = st.checkbox("Confirm deletion")
                    submitted = st.form_submit_button(mode)

                if submitted:
                    if mode == "Update":
                        show_result(*edit_interest(
                            interest_recruiter_id, interest_athlete_id,
                            new_status, new_notes,
                        ))
                    elif not confirm:
                        st.warning("Please confirm deletion.")
                    else:
                        show_result(*remove_interest(
                            interest_recruiter_id, interest_athlete_id,
                        ))

    elif section == "Achievements":
        st.header("Browse Achievements")

        search = st.text_input("Search by achievement title")
        date_earned = st.selectbox("Date earned", get_dates_earned())

        results = search_achievements(search, date_earned)

        st.dataframe(results)
        st.write(f"{len(results)} achievement(s) found.")

        st.subheader("Add an Achievement")
        sport_options = get_sport_options()       # {SportID: "Sport name"}

        # New achievements belong to the logged-in athlete, so there is
        # no athlete dropdown.
        with st.form("add_achievement"):
            title = st.text_input("Title")
            description = st.text_area("Description (optional)")
            sport_id = st.selectbox(
                "Sport",
                options=[None] + list(sport_options),
                format_func=lambda sport_id: "None" if sport_id is None else sport_options[sport_id],
            )
            new_date_earned = st.date_input("Date earned")
            submitted = st.form_submit_button("Add Achievement")

        if submitted:
            show_result(*add_achievement(current_id, sport_id, title, description,
                                         new_date_earned))

        st.subheader("Manage My Achievements")
        # The radio sits outside the form so the form re-renders when it changes.
        mode = st.radio("Action", ["Update", "Delete"], horizontal=True, key="achievement_mode")
        # Only the logged-in athlete's achievements: users manage their own.
        achievement_options = get_achievement_options(current_id)   # {AchievementID: "Title"}

        if not achievement_options:
            st.info("You have no achievements yet.")
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
                    # No table references achievement, so nothing else goes.
                    confirm = st.checkbox("Confirm deletion")
                submitted = st.form_submit_button(mode)

            if submitted:
                if mode == "Update":
                    show_result(*edit_achievement(
                        achievement_id, current_id, sport_id, title, description,
                        new_date_earned,
                    ))
                elif not confirm:
                    st.warning("Please confirm deletion.")
                else:
                    show_result(*remove_achievement(achievement_id, current_id))

    elif section == "Activities":
        st.header("Browse Activities")

        search = st.text_input("Search by activity type or location")
        sport = st.selectbox("Sport", get_activity_sports())

        results = search_activities(search, sport)

        st.dataframe(results)
        st.write(f"{len(results)} activity(ies) found.")

        st.subheader("Add an Activity")
        sport_options = get_sport_options()       # {SportID: "Sport name"}

        # The logged-in athlete organizes the activities they add.
        with st.form("add_activity"):
            activity_type = st.text_input("Activity type (e.g. Soccer Practice)")
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
                current_id, sport_id, activity_type, date, time, duration,
                location, max_participants,
            ))

        st.subheader("Manage My Activities")
        # The radio sits outside the form so the form re-renders when it changes.
        mode = st.radio("Action", ["Update", "Delete"], horizontal=True, key="activity_mode")
        # Only the activities the logged-in athlete organizes.
        my_activity_options = get_activity_options(current_id)   # {ActivityID: "Type on Date"}

        if not my_activity_options:
            st.info("You are not organizing any activities yet.")
        else:
            # Outside the form so picking another activity re-fills the fields.
            activity_id = st.selectbox(
                "Activity",
                options=list(my_activity_options),
                format_func=lambda activity_id: my_activity_options[activity_id],
                key="manage_activity_id",
            )
            current = get_activity_details(activity_id)

            with st.form("manage_activity"):
                if mode == "Update":
                    # The ID in each key gives every activity fresh, pre-filled widgets.
                    activity_type = st.text_input("Activity type (e.g. Soccer Practice)",
                                                  value=current["Type"],
                                                  key=f"activity_type_{activity_id}")
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
                    st.warning(
                        "Deleting this activity also deletes its participation "
                        "entries and the points earned for it."
                    )
                    confirm = st.checkbox("Confirm deletion")
                submitted = st.form_submit_button(mode)

            if submitted:
                if mode == "Update":
                    show_result(*edit_activity(
                        activity_id, current_id, sport_id, activity_type, date, time,
                        duration, location, max_participants,
                    ))
                elif not confirm:
                    st.warning("Please confirm deletion.")
                else:
                    show_result(*remove_activity(activity_id, current_id))

        st.subheader("Join an Activity")
        activity_options = get_activity_options()   # every activity, to join
        if not activity_options:
            st.info("No activities available.")
        else:
            # Outside the form so the roster below follows the chosen activity.
            join_activity_id = st.selectbox(
                "Activity",
                options=list(activity_options),
                format_func=lambda activity_id: activity_options[activity_id],
                key="join_activity_id",
            )

            # The logged-in athlete joins as themselves.
            if st.button("Join this activity"):
                show_result(*join_activity(join_activity_id, current_id))

            st.subheader("Roster")
            st.dataframe(list_roster(join_activity_id))
            participant_options = get_participant_options(join_activity_id)

            # Only the organizer manages the roster; anyone else on it can
            # only take themselves off (leave).
            if not is_organizer(join_activity_id, current_id):
                if current_id in participant_options:
                    with st.form("leave_activity"):
                        confirm = st.checkbox("Confirm leaving this activity")
                        submitted = st.form_submit_button("Leave Activity")
                    if submitted:
                        if not confirm:
                            st.warning("Please confirm leaving.")
                        else:
                            show_result(*remove_participant(
                                join_activity_id, current_id, current_id,
                            ))
                st.caption("Only the organizer can change this roster.")
                return

            st.subheader("Manage Participants")
            # The radio sits outside the form so the form re-renders when it changes.
            mode = st.radio("Action", ["Update", "Delete"], horizontal=True,
                            key="participant_mode")

            if not participant_options:
                st.info("No one has joined this activity yet.")
            else:
                participant_id = st.selectbox(
                    "Participant",
                    options=list(participant_options),
                    format_func=lambda athlete_id: participant_options[athlete_id],
                    key="manage_participant_id",
                )
                current = get_participant_details(join_activity_id, participant_id)

                with st.form("manage_participant"):
                    if mode == "Update":
                        # Activity and athlete IDs in the key give every
                        # participant fresh, pre-filled widgets.
                        widget_id = f"{join_activity_id}_{participant_id}"
                        new_status = st.selectbox(
                            "Status",
                            PARTICIPATION_STATUSES,
                            index=PARTICIPATION_STATUSES.index(
                                current["ParticipationStatus"])
                            if current["ParticipationStatus"] in PARTICIPATION_STATUSES
                            else 0,
                            key=f"participant_status_{widget_id}",
                        )
                        # Points are only awarded once, the first time someone
                        # is marked Attended for this activity.
                        points = st.number_input("Points to award if Attended",
                                                 min_value=0, value=10, step=5,
                                                 key=f"participant_points_{widget_id}")
                    else:
                        st.warning(
                            "This takes the athlete off the activity. Points "
                            "they already earned for it are kept."
                        )
                        confirm = st.checkbox("Confirm deletion")
                    submitted = st.form_submit_button(mode)

                if submitted:
                    if mode == "Update":
                        show_result(*change_participation_status(
                            join_activity_id, participant_id, new_status, points,
                            current_id,
                        ))
                    elif not confirm:
                        st.warning("Please confirm deletion.")
                    else:
                        show_result(*remove_participant(
                            join_activity_id, participant_id, current_id,
                        ))

    elif section == "Workouts":
        st.header("Workouts")

        st.dataframe(list_workouts())

        st.subheader("Add a Workout")
        # New workouts belong to the logged-in athlete.
        with st.form("add_workout"):
            scheduled_date = st.date_input("Scheduled date")
            workout_type = st.text_input("Workout type")
            duration = st.number_input("Duration in minutes (optional)",
                                       min_value=1, value=None, step=1)
            completion_status = st.text_input("Completion status")
            training_notes = st.text_area("Training notes (optional)")
            submitted = st.form_submit_button("Add Workout")

        if submitted:
            show_result(*add_workout(
                current_id, scheduled_date, workout_type, duration,
                completion_status, training_notes,
            ))

        st.subheader("Manage My Workouts")
        # The radio sits outside the form so the form re-renders when it changes.
        mode = st.radio("Action", ["Update", "Delete"], horizontal=True, key="workout_mode")
        # Only the logged-in athlete's workouts.
        workout_options = get_workout_options(current_id)   # {WorkoutID: "date - type"}

        if not workout_options:
            st.info("You have no workouts yet.")
        else:
            # The picker is outside the form too: widgets inside a form don't
            # rerun the page, so the fields below couldn't be pre-filled with
            # the chosen workout's values. Users pick a workout, never type an ID.
            workout_id = st.selectbox(
                "Workout",
                options=list(workout_options),
                format_func=lambda workout_id: workout_options[workout_id],
                key="manage_workout_id",
            )
            current = get_workout_details(workout_id)

            with st.form("manage_workout"):
                if mode == "Update":
                    # The ID in each key gives every workout fresh, pre-filled widgets.
                    new_scheduled_date = st.date_input(
                        "Scheduled date", value=current["ScheduledDate"],
                        key=f"workout_date_{workout_id}")
                    new_workout_type = st.text_input(
                        "Workout type", value=current["WorkoutType"],
                        key=f"workout_type_{workout_id}")
                    new_duration = st.number_input(
                        "Duration in minutes (optional)", min_value=1,
                        value=current["Duration"], step=1,
                        key=f"workout_duration_{workout_id}")
                    new_completion_status = st.text_input(
                        "Completion status", value=current["CompletionStatus"],
                        key=f"workout_status_{workout_id}")
                    new_training_notes = st.text_area(
                        "Training notes (optional)",
                        value=current["TrainingNotes"] or "",
                        key=f"workout_notes_{workout_id}")
                else:
                    st.warning(
                        "Deleting this workout also deletes the points earned for it."
                    )
                    confirm = st.checkbox("Confirm deletion")
                submitted = st.form_submit_button(mode)

            if submitted:
                if mode == "Update":
                    show_result(*edit_workout(
                        workout_id, current_id, new_scheduled_date,
                        new_workout_type, new_duration, new_completion_status,
                        new_training_notes,
                    ))
                elif not confirm:
                    st.warning("Please confirm deletion.")
                else:
                    show_result(*remove_workout(workout_id, current_id))

    elif section == "Points":
        st.header("Activity Points")

        st.dataframe(list_points())

        activity_options = get_activity_options()   # {ActivityID: "Type on Date"}
        # Points for a workout go to that workout's athlete, so only the
        # logged-in athlete's own workouts are offered.
        workout_options = get_workout_options(current_id)   # {WorkoutID: "date - type"}
        # Activity and workout are optional, so both dropdowns start with None.
        activity_choices = [None] + list(activity_options)
        workout_choices = [None] + list(workout_options)

        st.subheader("Add Points")
        # New points records belong to the logged-in athlete.
        with st.form("add_point"):
            activity_id = st.selectbox(
                "For activity (optional)",
                options=activity_choices,
                format_func=lambda activity_id: "None" if activity_id is None
                else activity_options[activity_id],
            )
            workout_id = st.selectbox(
                "For workout (optional)",
                options=workout_choices,
                format_func=lambda workout_id: "None" if workout_id is None
                else workout_options[workout_id],
            )
            points_earned = st.number_input("Points", min_value=1, value=10, step=5)
            reason = st.text_input("Reason")
            date_earned = st.date_input("Date earned")
            submitted = st.form_submit_button("Add Points")

        if submitted:
            show_result(*add_point(
                current_id, activity_id, workout_id, points_earned, reason,
                date_earned,
            ))

        st.subheader("Manage My Points")
        # The radio sits outside the form so the form re-renders when it changes.
        mode = st.radio("Action", ["Update", "Delete"], horizontal=True, key="point_mode")
        # Only the logged-in athlete's points records.
        point_options = get_point_options(current_id)   # {PointTransactionID: "10 pts - ..."}

        if not point_options:
            st.info("You have no points records yet.")
        else:
            point_id = st.selectbox(
                "Points record",
                options=list(point_options),
                format_func=lambda point_id: point_options[point_id],
                key="manage_point_id",
            )
            current = get_point_details(point_id)

            with st.form("manage_point"):
                if mode == "Update":
                    # The ID in each key gives every record fresh, pre-filled widgets.
                    new_activity_id = st.selectbox(
                        "For activity (optional)",
                        options=activity_choices,
                        index=activity_choices.index(current["ActivityID"])
                        if current["ActivityID"] in activity_choices else 0,
                        format_func=lambda activity_id: "None" if activity_id is None
                        else activity_options[activity_id],
                        key=f"point_activity_{point_id}",
                    )
                    new_workout_id = st.selectbox(
                        "For workout (optional)",
                        options=workout_choices,
                        index=workout_choices.index(current["WorkoutID"])
                        if current["WorkoutID"] in workout_choices else 0,
                        format_func=lambda workout_id: "None" if workout_id is None
                        else workout_options[workout_id],
                        key=f"point_workout_{point_id}",
                    )
                    new_points_earned = st.number_input(
                        "Points", min_value=1, value=current["PointsEarned"], step=5,
                        key=f"point_points_{point_id}")
                    new_reason = st.text_input("Reason", value=current["Reason"],
                                               key=f"point_reason_{point_id}")
                    new_date_earned = st.date_input(
                        "Date earned", value=current["DateEarned"],
                        key=f"point_date_{point_id}")
                else:
                    # No table references activity_point, so nothing else goes.
                    confirm = st.checkbox("Confirm deletion")
                submitted = st.form_submit_button(mode)

            if submitted:
                if mode == "Update":
                    show_result(*edit_point(
                        point_id, current_id, new_activity_id, new_workout_id,
                        new_points_earned, new_reason, new_date_earned,
                    ))
                elif not confirm:
                    st.warning("Please confirm deletion.")
                else:
                    show_result(*remove_point(point_id, current_id))

    elif section == "Sports":
        st.header("Sports")

        st.dataframe(list_sports())

        st.subheader("Add a Sport")
        with st.form("add_sport"):
            name = st.text_input("Sport name")
            sport_type = st.text_input("Type")
            submitted = st.form_submit_button("Add Sport")

        if submitted:
            show_result(*add_sport(name, sport_type))

        st.subheader("Manage Sports")
        # The radio sits outside the form so the form re-renders when it changes.
        mode = st.radio("Action", ["Update", "Delete"], horizontal=True, key="sport_mode")
        sport_options = get_sport_options()   # {SportID: "Soccer"}

        if not sport_options:
            st.info("No sports available.")
        else:
            sport_id = st.selectbox(
                "Sport",
                options=list(sport_options),
                format_func=lambda sport_id: sport_options[sport_id],
                key="manage_sport_id",
            )
            current = get_sport_details(sport_id)

            with st.form("manage_sport"):
                if mode == "Update":
                    # The ID in each key gives every sport fresh, pre-filled widgets.
                    new_name = st.text_input("Sport name", value=current["Name"],
                                             key=f"sport_name_{sport_id}")
                    new_sport_type = st.text_input("Type", value=current["Type"],
                                                   key=f"sport_type_{sport_id}")
                else:
                    st.warning(
                        "Deleting this sport also deletes its activities, "
                        "achievements and athlete links."
                    )
                    confirm = st.checkbox("Confirm deletion")
                submitted = st.form_submit_button(mode)

            if submitted:
                if mode == "Update":
                    show_result(*edit_sport(sport_id, new_name, new_sport_type))
                elif not confirm:
                    st.warning("Please confirm deletion.")
                else:
                    show_result(*remove_sport(sport_id))

    elif section == "Sponsors":
        st.header("Sponsors")

        st.dataframe(list_sponsors())

        st.subheader("Add a Sponsor")
        with st.form("add_sponsor"):
            company = st.text_input("Company")
            sponsor_type = st.text_input("Sponsor type (optional)")
            contact_information = st.text_input("Contact information (optional)")
            submitted = st.form_submit_button("Add Sponsor")

        if submitted:
            show_result(*add_sponsor(company, sponsor_type, contact_information))

        st.subheader("Manage Sponsors")
        # The radio sits outside the form so the form re-renders when it changes.
        mode = st.radio("Action", ["Update", "Delete"], horizontal=True, key="sponsor_mode")
        sponsor_options = get_sponsor_options()   # {SponsorID: "Peak Performance"}

        if not sponsor_options:
            st.info("No sponsors available.")
        else:
            sponsor_id = st.selectbox(
                "Sponsor",
                options=list(sponsor_options),
                format_func=lambda sponsor_id: sponsor_options[sponsor_id],
                key="manage_sponsor_id",
            )
            current = get_sponsor_details(sponsor_id)

            with st.form("manage_sponsor"):
                if mode == "Update":
                    # The ID in each key gives every sponsor fresh, pre-filled widgets.
                    new_company = st.text_input("Company", value=current["Company"],
                                                key=f"sponsor_company_{sponsor_id}")
                    new_sponsor_type = st.text_input(
                        "Sponsor type (optional)",
                        value=current["SponsorType"] or "",
                        key=f"sponsor_type_{sponsor_id}")
                    new_contact_information = st.text_input(
                        "Contact information (optional)",
                        value=current["ContactInformation"] or "",
                        key=f"sponsor_contact_{sponsor_id}")
                else:
                    st.warning(
                        "Deleting this sponsor also deletes its rewards and "
                        "their redemptions."
                    )
                    confirm = st.checkbox("Confirm deletion")
                submitted = st.form_submit_button(mode)

            if submitted:
                if mode == "Update":
                    show_result(*edit_sponsor(
                        sponsor_id, new_company, new_sponsor_type,
                        new_contact_information,
                    ))
                elif not confirm:
                    st.warning("Please confirm deletion.")
                else:
                    show_result(*remove_sponsor(sponsor_id))

    elif section == "Posts":
        st.header("Posts")

        st.dataframe(list_posts())

        st.subheader("Add a Post")
        # New posts belong to the logged-in athlete.
        with st.form("add_post"):
            content = st.text_area("Content")
            media_url = st.text_input("Media URL (optional)")
            submitted = st.form_submit_button("Add Post")

        if submitted:
            show_result(*add_post(current_id, content, media_url))

        st.subheader("Comments")
        post_options = get_post_options()   # {PostID: "Author: first words"}

        if not post_options:
            st.info("No posts available.")
        else:
            # Outside the form so the comment list follows the chosen post.
            post_id = st.selectbox(
                "Post",
                options=list(post_options),
                format_func=lambda post_id: post_options[post_id],
                key="comment_post_id",
            )
            st.dataframe(list_comments(post_id))

            # The logged-in athlete comments as themselves.
            with st.form("add_comment"):
                comment_text = st.text_area("Comment")
                submitted = st.form_submit_button("Add Comment")

            if submitted:
                show_result(*add_comment(current_id, post_id, comment_text))

            st.subheader("Manage My Comments")
            # The radio sits outside the form so the form re-renders when it changes.
            mode = st.radio("Action", ["Update", "Delete"], horizontal=True,
                            key="comment_mode")
            # Only the logged-in athlete's comments on the chosen post.
            comment_options = get_comment_options(post_id, current_id)

            if not comment_options:
                st.info("You have no comments on this post.")
            else:
                comment_id = st.selectbox(
                    "Comment",
                    options=list(comment_options),
                    format_func=lambda comment_id: comment_options[comment_id],
                    key="manage_comment_id",
                )
                current = get_comment_details(comment_id)

                with st.form("manage_comment"):
                    if mode == "Update":
                        # The ID in the key gives every comment a fresh, pre-filled box.
                        new_text = st.text_area("Comment", value=current["Text"],
                                                key=f"comment_text_{comment_id}")
                    else:
                        # No table references comment, so nothing else goes.
                        confirm = st.checkbox("Confirm deletion")
                    submitted = st.form_submit_button(mode)

                if submitted:
                    if mode == "Update":
                        show_result(*edit_comment(comment_id, current_id, new_text))
                    elif not confirm:
                        st.warning("Please confirm deletion.")
                    else:
                        show_result(*remove_comment(comment_id, current_id))

    elif section == "Reward Redemptions":
        st.header("Reward Redemptions")

        redemptions = list_redemptions()
        st.dataframe(redemptions)

        # Eligibility and redemption are for the logged-in athlete only.
        rewards = list_rewards_for_athlete(current_id)
        st.subheader("My Reward Eligibility")
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
                show_result(*redeem_reward(current_id, reward_id))
        else:
            st.info("You have no currently eligible rewards.")
