import mysql.connector

from db.database import (
    get_all_achievements, get_all_sports, get_achievement_by_id,
    insert_achievement, update_achievement, delete_achievement,
)
from services.delete_summary import describe_related


def search_achievements(search, date_earned):
    """Return achievements whose title contains `search`
    and that were earned on the selected date."""
    achievement_list = get_all_achievements()
    filtered_achievements = []

    for achievement in achievement_list:
        title_matches = search.lower() in achievement["Title"].lower()
        # str() because MySQL returns DateEarned as a datetime.date,
        # while the dropdown value is a string.
        date_matches = (date_earned == "All") or (str(achievement["DateEarned"]) == date_earned)

        if title_matches and date_matches:
            filtered_achievements.append(achievement)

    return filtered_achievements


def get_dates_earned():
    """Build the dropdown options from the data itself."""
    dates = {str(a["DateEarned"]) for a in get_all_achievements()}
    return ["All"] + sorted(dates)


def get_sport_options():
    """Map SportID -> sport name for the achievement form's dropdown."""
    return {s["SportID"]: s["Name"] for s in get_all_sports()}


def get_achievement_options():
    """Map AchievementID -> title for the manage form's dropdown,
    so users pick an achievement instead of typing its ID."""
    return {a["AchievementID"]: a["Title"] for a in get_all_achievements()}


def get_achievement_details(achievement_id):
    """Return one achievement's current values (to pre-fill the update form)."""
    return get_achievement_by_id(achievement_id)


def check_achievement_input(athlete_id, title, description):
    """Shared validation for add and update.
    Returns (error, values): error is None when the input is fine, and
    values is the cleaned-up (title, description)."""
    title = (title or "").strip()
    description = (description or "").strip() or None
    values = (title, description)

    if not title:
        return "Title is required.", values
    if athlete_id is None:
        return "Please choose an athlete.", values

    return None, values


def add_achievement(athlete_id, sport_id, title, description, date_earned):
    """Validate the input, then insert it. Returns (success, message).
    sport_id may be None, which is stored as SQL NULL."""
    error, (title, description) = check_achievement_input(athlete_id, title, description)
    if error:
        return False, error

    try:
        insert_achievement(athlete_id, sport_id, title, description, date_earned)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete or sport no longer exists."
        return False, f"Could not add achievement: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not add achievement: {e.msg}"

    return True, f'Added achievement "{title}".'


def edit_achievement(achievement_id, athlete_id, sport_id, title, description,
                     date_earned):
    """Validate the input, then update the achievement. Returns (success, message)."""
    error, (title, description) = check_achievement_input(athlete_id, title, description)
    if error:
        return False, error

    try:
        updated = update_achievement(achievement_id, athlete_id, sport_id, title,
                                     description, date_earned)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete or sport no longer exists."
        return False, f"Could not update achievement: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not update achievement: {e.msg}"

    if updated == 0:
        return False, "No matching achievement found."
    return True, f'Updated achievement "{title}".'


def remove_achievement(achievement_id):
    """Delete the achievement. Returns (success, message)."""
    try:
        deleted = delete_achievement(achievement_id)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1451:  # other rows still point at this achievement
            return False, "Cannot delete this achievement while other records still use it."
        return False, f"Could not delete achievement: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not delete achievement: {e.msg}"

    if deleted["achievement"] == 0:
        return False, "No matching achievement found."
    return True, "Deleted achievement." + describe_related(deleted, "achievement")
