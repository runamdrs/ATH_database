import mysql.connector

from db.database import (
    get_all_points, get_point_by_id, get_workout_by_id,
    insert_point, update_point, delete_point,
)
from services.delete_summary import describe_related


def list_points():
    """Return every points record, joined with the athlete's name and the
    activity or workout it was earned for."""
    return get_all_points()


def get_point_options():
    """Map PointTransactionID -> "10 pts - Ann (Attended activity)" for the
    manage form's dropdown, so users pick a record instead of typing an ID."""
    return {
        point["PointTransactionID"]: (
            f"{point['PointsEarned']} pts - {point['Athlete']} ({point['Reason']})"
        )
        for point in get_all_points()
    }


def get_point_details(point_id):
    """Return one points record's current values (to pre-fill the update form)."""
    point = get_point_by_id(point_id)
    if point is not None:
        # DateEarned is a DATETIME; the form only edits the date part.
        point["DateEarned"] = point["DateEarned"].date()
    return point


def check_point_input(athlete_id, workout_id, points_earned, reason):
    """Shared validation for add and update.
    Returns (error, values): error is None when the input is fine, and
    values is the cleaned-up (reason,)."""
    reason = (reason or "").strip()
    values = (reason,)

    if athlete_id is None:
        return "Please choose an athlete.", values
    if not points_earned or points_earned < 1:
        return "Points must be at least 1.", values
    if not reason:
        return "Reason is required.", values
    if len(reason) > 150:  # activity_point.Reason is VARCHAR(150)
        return "Reason must be 150 characters or fewer.", values
    # The schema only checks that the workout exists, not whose it is, so
    # the rule "points for a workout go to that workout's athlete" lives here.
    if workout_id is not None:
        workout = get_workout_by_id(workout_id)
        if workout is not None and workout["AthleteID"] != athlete_id:
            return "That workout belongs to another athlete.", values

    return None, values


def add_point(athlete_id, activity_id, workout_id, points_earned, reason,
              date_earned):
    """Validate the input, then insert it. Returns (success, message).
    activity_id and workout_id are optional and stored as SQL NULL."""
    error, (reason,) = check_point_input(athlete_id, workout_id, points_earned, reason)
    if error:
        return False, error

    try:
        insert_point(athlete_id, activity_id, workout_id, points_earned, reason,
                     date_earned)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete, activity or workout no longer exists."
        return False, f"Could not add points record: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not add points record: {e.msg}"

    return True, f'Added points record "{reason}".'


def edit_point(point_id, athlete_id, activity_id, workout_id, points_earned, reason,
               date_earned):
    """Validate the input, then update the points record.
    Returns (success, message)."""
    error, (reason,) = check_point_input(athlete_id, workout_id, points_earned, reason)
    if error:
        return False, error

    try:
        updated = update_point(point_id, athlete_id, activity_id, workout_id,
                               points_earned, reason, date_earned)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete, activity or workout no longer exists."
        return False, f"Could not update points record: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not update points record: {e.msg}"

    if updated == 0:
        return False, "No matching points record found."
    return True, f'Updated points record "{reason}".'


def remove_point(point_id):
    """Delete the points record. Nothing references it, so nothing else
    goes with it. Returns (success, message)."""
    try:
        deleted = delete_point(point_id)
    except mysql.connector.Error as e:
        return False, f"Could not delete points record: {e.msg}"

    if deleted["activity_point"] == 0:
        return False, "No matching points record found."
    return True, "Deleted points record." + describe_related(deleted, "activity_point")
