import mysql.connector

from db.database import (
    get_all_sports, get_sport_by_id,
    insert_sport, update_sport, delete_sport,
)
from services.delete_summary import describe_related


def list_sports():
    """Return every sport, ordered by name."""
    return get_all_sports()


def get_sport_options():
    """Map SportID -> name for the sport form's dropdown, so users pick
    a sport instead of typing an ID."""
    return {sport["SportID"]: sport["Name"] for sport in get_all_sports()}


def get_sport_details(sport_id):
    """Return one sport's current values (to pre-fill the update form)."""
    return get_sport_by_id(sport_id)


def check_sport_input(name, sport_type):
    """Shared validation for add and update.
    Returns (error, values): error is None when the input is fine, and
    values is the cleaned-up (name, sport_type)."""
    name = (name or "").strip()
    sport_type = (sport_type or "").strip()
    values = (name, sport_type)

    if not name:
        return "Sport name is required.", values
    if len(name) > 50:
        return "Sport name must be 50 characters or fewer.", values
    if not sport_type:
        return "Sport type is required.", values
    if len(sport_type) > 50:
        return "Sport type must be 50 characters or fewer.", values

    return None, values


def add_sport(name, sport_type):
    """Validate the input, then insert it. Returns (success, message)."""
    error, (name, sport_type) = check_sport_input(name, sport_type)
    if error:
        return False, error

    try:
        insert_sport(name, sport_type)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # sport.Name is UNIQUE in the schema
            return False, "A sport with that name already exists."
        return False, f"Could not add sport: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not add sport: {e.msg}"

    return True, f'Added sport "{name}".'


def edit_sport(sport_id, name, sport_type):
    """Validate the input, then update the sport. Returns (success, message)."""
    error, (name, sport_type) = check_sport_input(name, sport_type)
    if error:
        return False, error

    try:
        updated = update_sport(sport_id, name, sport_type)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # sport.Name is UNIQUE in the schema
            return False, "A sport with that name already exists."
        return False, f"Could not update sport: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not update sport: {e.msg}"

    if updated == 0:
        return False, "No matching sport found."
    return True, f'Updated sport "{name}".'


def remove_sport(sport_id):
    """Delete the sport together with its activities, achievements and
    athlete links, in one transaction. Returns (success, message)."""
    try:
        deleted = delete_sport(sport_id)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1451:  # a table we did not account for points at it
            return False, "This sport is in use and cannot be deleted."
        return False, f"Could not delete sport: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not delete sport: {e.msg}"

    if deleted["sport"] == 0:
        return False, "No matching sport found."
    return True, "Deleted sport." + describe_related(deleted, "sport")
