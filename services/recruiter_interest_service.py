import mysql.connector

from db.database import (
    get_all_recruiters, get_interest_for_athlete, get_recruiter_interest,
    insert_recruiter_interest, update_recruiter_interest, delete_recruiter_interest,
)
from services.delete_summary import describe_related

# The order a recruitment usually moves through. These are the values
# already in the data; Status is a plain VARCHAR, so the list lives here.
INTEREST_STATUSES = [
    "Interested", "Contacted", "Under Review", "Offer Extended", "Declined",
]


def list_interest_for_athlete(athlete_id):
    """Return every recruiter interested in the athlete, newest first."""
    return get_interest_for_athlete(athlete_id)


def get_recruiter_options():
    """Map RecruiterID -> "Name (Organization)" for the Express interest
    dropdown, so users pick a recruiter instead of typing an ID."""
    return {
        r["RecruiterID"]: f"{r['Name']} ({r['Organization']})" if r["Organization"]
        else r["Name"]
        for r in get_all_recruiters()
    }


def get_interest_options(athlete_id):
    """Map RecruiterID -> name for the recruiters already interested in
    the athlete, so the manage form offers only rows that exist."""
    return {
        row["RecruiterID"]: row["Recruiter"]
        for row in get_interest_for_athlete(athlete_id)
    }


def get_interest_details(recruiter_id, athlete_id):
    """Return one interest's current values (to pre-fill the update form)."""
    return get_recruiter_interest(recruiter_id, athlete_id)


def check_interest_input(recruiter_id, athlete_id, status, notes):
    """Shared validation for add and update.
    Returns (error, values): error is None when the input is fine, and
    values is the cleaned-up (notes,)."""
    notes = (notes or "").strip() or None  # optional: blank -> NULL
    values = (notes,)

    if recruiter_id is None or athlete_id is None:
        return "Please choose a recruiter and an athlete.", values
    if status not in INTEREST_STATUSES:
        return "Please choose a valid status.", values

    return None, values


def express_interest(recruiter_id, athlete_id, notes):
    """Record a recruiter's interest in an athlete. It always starts as
    'Interested', dated today. Returns (success, message)."""
    status = INTEREST_STATUSES[0]
    error, (notes,) = check_interest_input(recruiter_id, athlete_id, status, notes)
    if error:
        return False, error

    try:
        insert_recruiter_interest(recruiter_id, athlete_id, status, notes)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # (RecruiterID, AthleteID) is the primary key
            return False, "That recruiter has already shown interest in this athlete."
        if e.errno == 1452:  # foreign key violation
            return False, "That recruiter or athlete no longer exists."
        return False, f"Could not add recruiter interest: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not add recruiter interest: {e.msg}"

    return True, "Added recruiter interest."


def edit_interest(recruiter_id, athlete_id, status, notes):
    """Validate the input, then update the status and notes.
    Returns (success, message)."""
    error, (notes,) = check_interest_input(recruiter_id, athlete_id, status, notes)
    if error:
        return False, error

    # Only Status and Notes change: no UNIQUE column or foreign key is
    # touched, so only the general branch is needed.
    try:
        updated = update_recruiter_interest(recruiter_id, athlete_id, status, notes)
    except mysql.connector.Error as e:
        return False, f"Could not update recruiter interest: {e.msg}"

    if updated == 0:
        return False, "No matching recruiter interest found."
    return True, f"Updated recruiter interest to {status}."


def remove_interest(recruiter_id, athlete_id):
    """Withdraw the recruiter's interest. Nothing references it, so
    nothing else goes with it. Returns (success, message)."""
    try:
        deleted = delete_recruiter_interest(recruiter_id, athlete_id)
    except mysql.connector.Error as e:
        return False, f"Could not delete recruiter interest: {e.msg}"

    if deleted["recruiter_athlete"] == 0:
        return False, "No matching recruiter interest found."
    return True, "Deleted recruiter interest." + describe_related(
        deleted, "recruiter_athlete"
    )
