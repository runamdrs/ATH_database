import datetime

import mysql.connector

from database import (
    get_all_activities, get_activity_by_id,
    insert_activity, update_activity, delete_activity,
    get_roster, insert_participant, set_status_and_award_points,
)

PARTICIPATION_STATUSES = ["Registered", "Attended", "No-Show", "Cancelled"]


def search_activities(search, sport):
    """Return activities whose type or location contains `search`
    and whose sport matches the selected filter."""
    activity_list = get_all_activities()
    filtered_activities = []

    for activity in activity_list:
        # Location is optional, so it may be None (SQL NULL).
        searchable_text = f"{activity['Type']} {activity['Location'] or ''}".lower()
        text_matches = search.lower() in searchable_text
        sport_matches = (sport == "All") or (activity["Sport"] == sport)

        if text_matches and sport_matches:
            filtered_activities.append(activity)

    return filtered_activities


def get_activity_sports():
    """Build the dropdown options from the data itself."""
    sports = {activity["Sport"] for activity in get_all_activities()}
    return ["All"] + sorted(sports)


def get_activity_options():
    """Map ActivityID -> "Type on Date" for the manage form's dropdown,
    so users pick an activity instead of typing its ID."""
    return {a["ActivityID"]: f"{a['Type']} on {a['Date']}" for a in get_all_activities()}


def get_activity_details(activity_id):
    """Return one activity's current values (to pre-fill the update form)."""
    activity = get_activity_by_id(activity_id)
    if activity is not None:
        # MySQL returns TIME as a timedelta; st.time_input needs a datetime.time.
        minutes = int(activity["Time"].total_seconds()) // 60
        activity["Time"] = datetime.time(minutes // 60, minutes % 60)
    return activity


def check_activity_input(athlete_id, sport_id, activity_type, duration, location,
                         max_participants):
    """Shared validation for add and update.
    Returns (error, values): error is None when the input is fine, and
    values is the cleaned-up (activity_type, location)."""
    activity_type = (activity_type or "").strip()
    location = (location or "").strip() or None  # optional: blank -> NULL
    values = (activity_type, location)

    if not activity_type:
        return "Activity type is required.", values
    if athlete_id is None:
        return "Please choose an athlete.", values
    if sport_id is None:
        return "Please choose a sport.", values
    if not duration or duration < 1:
        return "Duration must be at least 1 minute.", values
    if max_participants is not None and max_participants < 1:
        return "Max participants must be at least 1.", values

    return None, values


def add_activity(athlete_id, sport_id, activity_type, date, time, duration,
                 location, max_participants):
    """Validate the input, then insert it. Returns (success, message).
    location and max_participants are optional and stored as SQL NULL."""
    error, (activity_type, location) = check_activity_input(
        athlete_id, sport_id, activity_type, duration, location, max_participants
    )
    if error:
        return False, error

    try:
        insert_activity(athlete_id, sport_id, activity_type, date, time, duration,
                        location, max_participants)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete or sport no longer exists."
        return False, f"Could not add activity: {e.msg}"

    return True, f'Added activity "{activity_type}".'


def edit_activity(activity_id, athlete_id, sport_id, activity_type, date, time,
                  duration, location, max_participants):
    """Validate the input, then update the activity. Returns (success, message)."""
    error, (activity_type, location) = check_activity_input(
        athlete_id, sport_id, activity_type, duration, location, max_participants
    )
    if error:
        return False, error

    try:
        updated = update_activity(activity_id, athlete_id, sport_id, activity_type,
                                  date, time, duration, location, max_participants)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete or sport no longer exists."
        return False, f"Could not update activity: {e.msg}"

    if updated == 0:
        return False, "No matching activity found."
    return True, f'Updated activity "{activity_type}".'


def remove_activity(activity_id):
    """Delete the activity. Returns (success, message)."""
    try:
        deleted = delete_activity(activity_id)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1451:  # other rows still point at this activity
            return False, "Cannot delete this activity while other records still use it."
        return False, f"Could not delete activity: {e.msg}"

    if deleted == 0:
        return False, "No matching activity found."
    return True, "Deleted activity."


def join_activity(activity_id, athlete_id):
    """Add the athlete to the activity as 'Registered'. Returns (success, message)."""
    try:
        added = insert_participant(activity_id, athlete_id)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # same athlete + activity already in the table
            return False, "That athlete has already joined this activity."
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete or activity no longer exists."
        return False, f"Could not join activity: {e.msg}"

    if added == 0:
        return False, "This activity is full or no longer exists."
    return True, "Joined the activity."


def list_roster(activity_id):
    return get_roster(activity_id)


def change_participation_status(activity_id, athlete_id, status, points=10):
    """Organizer changes a participant's status. Marking someone Attended also
    awards `points` activity points (once). Returns (success, message)."""
    if status not in PARTICIPATION_STATUSES:
        return False, "Please choose a valid status."
    try:
        found, awarded = set_status_and_award_points(
            activity_id, athlete_id, status, points or 0
        )
    except mysql.connector.Error as e:
        return False, f"Could not update status: {e.msg}"
    if found == 0:
        return False, "No matching participant found."
    if awarded:
        return True, f"Status set to Attended. Awarded {points} points."
    if status == "Attended":
        return True, "Status set to Attended (points were already awarded or 0)."
    return True, f"Status set to {status}."
