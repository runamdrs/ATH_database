import mysql.connector

from database import get_all_athletes, insert_athlete

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


def add_athlete(name, username, email, location, skill_level):
    """Validate the input, then insert it. Returns (success, message)."""
    name = (name or "").strip()
    username = (username or "").strip()
    email = (email or "").strip()
    location = (location or "").strip() or None  # optional: blank -> NULL

    if not name or not username or not email:
        return False, "Name, Username and Email are required."
    if "@" not in email:
        return False, "Please enter a valid email address."
    if skill_level not in SKILL_LEVELS:
        return False, "Skill level must be Beginner, Intermediate or Advanced."

    try:
        insert_athlete(name, username, email, location, skill_level)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # duplicate value in a UNIQUE column
            return False, "That username or email is already taken."
        return False, f"Could not add athlete: {e.msg}"

    return True, f"Added athlete {name}."
