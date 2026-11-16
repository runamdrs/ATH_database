import mysql.connector

from database import get_all_activities, insert_activity


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


def add_activity(athlete_id, sport_id, activity_type, date, time, duration,
                 location, max_participants):
    """Validate the input, then insert it. Returns (success, message).
    location and max_participants are optional and stored as SQL NULL."""
    activity_type = (activity_type or "").strip()
    location = (location or "").strip() or None  # optional: blank -> NULL

    if not activity_type:
        return False, "Activity type is required."
    if athlete_id is None:
        return False, "Please choose an athlete."
    if sport_id is None:
        return False, "Please choose a sport."
    if not duration or duration < 1:
        return False, "Duration must be at least 1 minute."
    if max_participants is not None and max_participants < 1:
        return False, "Max participants must be at least 1."

    try:
        insert_activity(athlete_id, sport_id, activity_type, date, time, duration,
                        location, max_participants)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete or sport no longer exists."
        return False, f"Could not add activity: {e.msg}"

    return True, f'Added activity "{activity_type}".'
