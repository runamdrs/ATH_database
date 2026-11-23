import datetime

import mysql.connector

from db.database import (
    get_all_activities, get_activity_by_id,
    insert_activity, update_activity, delete_activity,
    get_roster, get_participant, insert_participant, update_participant_status,
    delete_participant,
)
from services.delete_summary import describe_related
from services.ownership import check_owner

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


def get_activity_options(athlete_id=None):
    """Map ActivityID -> "Type on Date" for the dropdowns, so users pick an
    activity instead of typing its ID. With athlete_id, only the activities
    that athlete organizes (for managing); without it, every activity (for
    joining)."""
    return {
        a["ActivityID"]: f"{a['Type']} on {a['Date']}"
        for a in get_all_activities()
        if athlete_id is None or a["AthleteID"] == athlete_id
    }


def is_organizer(activity_id, athlete_id):
    """True when athlete_id organizes the activity; only the organizer
    manages its roster."""
    activity = get_activity_by_id(activity_id)
    return activity is not None and activity["AthleteID"] == athlete_id


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
    except mysql.connector.Error as e:
        return False, f"Could not add activity: {e.msg}"

    return True, f'Added activity "{activity_type}".'


def edit_activity(activity_id, athlete_id, sport_id, activity_type, date, time,
                  duration, location, max_participants):
    """Validate the input, then update the activity. athlete_id is the
    current user, who must organize it. Returns (success, message)."""
    error, (activity_type, location) = check_activity_input(
        athlete_id, sport_id, activity_type, duration, location, max_participants
    )
    if error:
        return False, error
    error = check_owner(get_activity_by_id(activity_id), athlete_id,
                        "activity", "activities")
    if error:
        return False, error

    try:
        updated = update_activity(activity_id, athlete_id, sport_id, activity_type,
                                  date, time, duration, location, max_participants)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete or sport no longer exists."
        return False, f"Could not update activity: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not update activity: {e.msg}"

    if updated == 0:
        return False, "No matching activity found."
    return True, f'Updated activity "{activity_type}".'


def remove_activity(activity_id, athlete_id):
    """Delete the activity together with its points and participation
    entries, in one transaction, if the current user (athlete_id)
    organizes it. Returns (success, message)."""
    error = check_owner(get_activity_by_id(activity_id), athlete_id,
                        "activity", "activities")
    if error:
        return False, error

    try:
        deleted = delete_activity(activity_id)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1451:  # a table we did not account for points at it
            return False, "Cannot delete this activity while other records still use it."
        return False, f"Could not delete activity: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not delete activity: {e.msg}"

    if deleted["activity"] == 0:
        return False, "No matching activity found."
    return True, "Deleted activity." + describe_related(deleted, "activity")


def list_roster(activity_id):
    """Return everyone who joined the activity, with their status."""
    return get_roster(activity_id)


def get_participant_options(activity_id):
    """Map AthleteID -> name for everyone on the activity's roster, so the
    manage form offers only athletes who really joined."""
    return {row["AthleteID"]: row["Athlete"] for row in get_roster(activity_id)}


def get_participant_details(activity_id, athlete_id):
    """Return one participant's current values (to pre-fill the status)."""
    return get_participant(activity_id, athlete_id)


def join_activity(activity_id, athlete_id):
    """Register the athlete for the activity. Returns (success, message)."""
    if activity_id is None or athlete_id is None:
        return False, "Please choose an activity and an athlete."

    try:
        added = insert_participant(activity_id, athlete_id)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # (ActivityID, AthleteID) is the primary key
            return False, "That athlete has already joined this activity."
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete or activity no longer exists."
        return False, f"Could not join activity: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not join activity: {e.msg}"

    # The INSERT ... SELECT adds nothing when the activity is full or gone.
    if added == 0:
        return False, "This activity is full or no longer exists."
    return True, "Joined the activity."


def change_participation_status(activity_id, athlete_id, status, points, organizer_id):
    """Set a participant's status. Only the activity's organizer (the
    current user, organizer_id) may do this. Marking someone Attended also
    awards `points` Activity Points, once. Returns (success, message)."""
    if not is_organizer(activity_id, organizer_id):
        return False, "Only the organizer can change this roster."
    if status not in PARTICIPATION_STATUSES:
        return False, "Please choose a valid status."
    if points is None or points < 0:
        return False, "Points must be 0 or more."

    try:
        changed = update_participant_status(activity_id, athlete_id, status, points)
    except mysql.connector.Error as e:
        return False, f"Could not update status: {e.msg}"

    if changed["activity_participant"] == 0:
        return False, "No matching participant found."
    if changed.get("activity_point"):
        return True, f"Updated status to Attended. Awarded {points} points."
    return True, f"Updated status to {status}."


def remove_participant(activity_id, athlete_id, current_id):
    """Take the athlete off the activity. The organizer may remove anyone,
    and a participant may remove themselves (leave). Points already earned
    for it are kept. Returns (success, message)."""
    if athlete_id != current_id and not is_organizer(activity_id, current_id):
        return False, "Only the organizer can change this roster."

    try:
        deleted = delete_participant(activity_id, athlete_id)
    except mysql.connector.Error as e:
        return False, f"Could not delete participation entry: {e.msg}"

    if deleted["activity_participant"] == 0:
        return False, "No matching participation entry found."
    return True, "Deleted participation entry." + describe_related(
        deleted, "activity_participant"
    )
