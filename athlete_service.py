import mysql.connector

from database import (
    get_all_athletes, get_athlete_by_id, insert_athlete, update_athlete, delete_athlete,
)

SKILL_LEVELS = ["Beginner", "Intermediate", "Advanced"]


def search_athletes(search, skill_level):
    """Return athletes whose name or username contains `search`
    and whose skill level matches the selected filter."""
    athlete_list = get_all_athletes()
    filtered_athletes = []

    for athlete in athlete_list:
        searchable_text = f"{athlete['Name']} {athlete['Username']}".lower()
        name_matches = search.lower() in searchable_text
        skill_matches = (skill_level == "All") or (athlete["SkillLevel"] == skill_level)

        if name_matches and skill_matches:
            filtered_athletes.append(athlete)

    return filtered_athletes


def get_skill_levels():
    """Build the dropdown options from the data itself."""
    levels = {athlete["SkillLevel"] for athlete in get_all_athletes()}
    return ["All"] + sorted(levels)


def get_athlete_options():
    """Map AthleteID -> "Name (@Username)" for the achievement form's
    dropdown, so users pick a real athlete instead of typing an ID."""
    return {a["AthleteID"]: f"{a['Name']} (@{a['Username']})" for a in get_all_athletes()}


def get_athlete_details(athlete_id):
    """Return one athlete's current values (to pre-fill the update form)."""
    return get_athlete_by_id(athlete_id)


def check_athlete_input(name, username, email, location, skill_level):
    """Shared validation for add and update.
    Returns (error, values): error is None when the input is fine, and
    values is the cleaned-up (name, username, email, location)."""
    name = (name or "").strip()
    username = (username or "").strip()
    email = (email or "").strip()
    location = (location or "").strip() or None  # optional: blank -> NULL
    values = (name, username, email, location)

    if not name or not username or not email:
        return "Name, Username and Email are required.", values
    if "@" not in email:
        return "Please enter a valid email address.", values
    if skill_level not in SKILL_LEVELS:
        return "Skill level must be Beginner, Intermediate or Advanced.", values

    return None, values


def add_athlete(name, username, email, location, skill_level):
    """Validate the input, then insert it. Returns (success, message)."""
    error, (name, username, email, location) = check_athlete_input(
        name, username, email, location, skill_level
    )
    if error:
        return False, error

    try:
        insert_athlete(name, username, email, location, skill_level)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # duplicate value in a UNIQUE column
            return False, "That username or email is already taken."
        return False, f"Could not add athlete: {e.msg}"

    return True, f"Added athlete {name}."


def edit_athlete(athlete_id, name, username, email, location, skill_level):
    """Validate the input, then update the athlete. Returns (success, message)."""
    error, (name, username, email, location) = check_athlete_input(
        name, username, email, location, skill_level
    )
    if error:
        return False, error

    try:
        updated = update_athlete(athlete_id, name, username, email, location, skill_level)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # duplicate value in a UNIQUE column
            return False, "That username or email is already taken."
        return False, f"Could not update athlete: {e.msg}"

    if updated == 0:
        return False, "No matching athlete found."
    return True, f"Updated athlete {name}."


def remove_athlete(athlete_id):
    """Delete the athlete. Returns (success, message)."""
    try:
        deleted = delete_athlete(athlete_id)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1451:  # other rows still point at this athlete
            return False, ("Cannot delete this athlete while they still have "
                           "achievements or activities.")
        return False, f"Could not delete athlete: {e.msg}"

    if deleted == 0:
        return False, "No matching athlete found."
    return True, "Deleted athlete."
