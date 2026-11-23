import mysql.connector

from database import delete_sport, get_all_sports, insert_sport, update_sport


def list_sports():
    return get_all_sports()


def get_sport_options():
    return {sport["SportID"]: sport["Name"] for sport in get_all_sports()}


def get_sport_types():
    types = {sport["Type"] for sport in get_all_sports()}
    return ["All"] + sorted(types)


def search_sports(search="", sport_type="All"):
    search = (search or "").lower()
    return [
        sport for sport in get_all_sports()
        if search in f'{sport["Name"]} {sport["Type"]}'.lower()
        and (sport_type == "All" or sport["Type"] == sport_type)
    ]


def add_sport(name, sport_type):
    name = (name or "").strip()
    sport_type = (sport_type or "").strip()

    if not name:
        return False, "Sport name is required."
    if len(name) > 50:
        return False, "Sport name must be 50 characters or fewer."
    if not sport_type:
        return False, "Sport type is required."
    if len(sport_type) > 50:
        return False, "Sport type must be 50 characters or fewer."

    try:
        insert_sport(name, sport_type)
    except mysql.connector.IntegrityError as error:
        if error.errno == 1062:
            return False, "A sport with that name already exists."
        return False, f"Could not add sport: {error.msg}"
    except mysql.connector.Error as error:
        return False, f"Could not add sport: {error.msg}"

    return True, f'Added sport "{name}".'


def edit_sport(sport_id, name, sport_type):
    name = (name or "").strip()
    sport_type = (sport_type or "").strip()

    if not name:
        return False, "Sport name is required."
    if len(name) > 50:
        return False, "Sport name must be 50 characters or fewer."
    if not sport_type:
        return False, "Sport type is required."
    if len(sport_type) > 50:
        return False, "Sport type must be 50 characters or fewer."

    try:
        if not any(row["SportID"] == sport_id for row in get_all_sports()):
            return False, "That sport no longer exists."
        update_sport(sport_id, name, sport_type)
    except mysql.connector.IntegrityError as error:
        if error.errno == 1062:
            return False, "A sport with that name already exists."
        return False, f"Could not update sport: {error.msg}"
    except mysql.connector.Error as error:
        return False, f"Could not update sport: {error.msg}"

    return True, f'Updated sport "{name}".'


def remove_sport(sport_id):
    try:
        if not any(row["SportID"] == sport_id for row in get_all_sports()):
            return False, "That sport no longer exists."
        delete_sport(sport_id)
    except mysql.connector.IntegrityError as error:
        if error.errno == 1451:
            return False, "This sport is in use and cannot be deleted."
        return False, f"Could not delete sport: {error.msg}"
    except mysql.connector.Error as error:
        return False, f"Could not delete sport: {error.msg}"

    return True, "Sport deleted."
