import mysql.connector

from database import get_all_achievements, get_all_sports, insert_achievement


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


def add_achievement(athlete_id, sport_id, title, description, date_earned):
    """Validate the input, then insert it. Returns (success, message).
    sport_id may be None, which is stored as SQL NULL."""
    title = (title or "").strip()
    description = (description or "").strip() or None

    if not title:
        return False, "Title is required."
    if athlete_id is None:
        return False, "Please choose an athlete."

    try:
        insert_achievement(athlete_id, sport_id, title, description, date_earned)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete or sport no longer exists."
        return False, f"Could not add achievement: {e.msg}"

    return True, f'Added achievement "{title}".'
