import mysql.connector

from database import (
    get_all_workouts, get_workout_by_id,
    insert_workout, update_workout, delete_workout,
)
from delete_summary import describe_related


def list_workouts():
    """Return every workout, already joined with its athlete's name."""
    return get_all_workouts()


def get_workout_athletes():
    athletes = {row["Athlete"] for row in get_all_workouts()}
    return ["All"] + sorted(athletes)


def get_workout_statuses():
    statuses = {row["CompletionStatus"] for row in get_all_workouts()}
    return ["All"] + sorted(statuses)


def search_workouts(search="", athlete="All", completion_status="All"):
    search = (search or "").lower()
    results = []
    for row in get_all_workouts():
        searchable_text = " ".join([
            str(row["Athlete"] or ""),
            str(row["WorkoutType"] or ""),
            str(row["TrainingNotes"] or ""),
            str(row["CompletionStatus"] or ""),
        ]).lower()
        athlete_matches = athlete == "All" or row["Athlete"] == athlete
        status_matches = (
            completion_status == "All"
            or row["CompletionStatus"] == completion_status
        )
        if search in searchable_text and athlete_matches and status_matches:
            results.append(row)
    return results


def get_workout_options():
    """Map WorkoutID -> "2026-11-16 - Run (Alex Morgan)" for the manage
    form's dropdown, so users pick a workout instead of typing an ID."""
    return {
        workout["WorkoutID"]: (
            f"{workout['ScheduledDate']} - {workout['WorkoutType']} "
            f"({workout['Athlete']})"
        )
        for workout in get_all_workouts()
    }


def get_workout_details(workout_id):
    """Return one workout's current values (to pre-fill the update form)."""
    return get_workout_by_id(workout_id)


def check_workout_input(athlete_id, scheduled_date, workout_type, duration,
                        completion_status, training_notes):
    """Shared validation for add and update.
    Returns (error, values): error is None when the input is fine, and
    values is the cleaned-up (workout_type, completion_status,
    training_notes)."""
    workout_type = (workout_type or "").strip()
    completion_status = (completion_status or "").strip()
    training_notes = (training_notes or "").strip() or None  # optional: blank -> NULL
    values = (workout_type, completion_status, training_notes)

    if athlete_id is None:
        return "Please choose an athlete.", values
    if not scheduled_date:
        return "Scheduled date is required.", values
    if not workout_type:
        return "Workout type is required.", values
    if len(workout_type) > 50:
        return "Workout type must be 50 characters or fewer.", values
    if duration is not None and (not isinstance(duration, int) or duration < 1):
        return "Duration must be a positive whole number of minutes.", values
    if not completion_status:
        return "Completion status is required.", values
    if len(completion_status) > 20:
        return "Completion status must be 20 characters or fewer.", values

    return None, values


def add_workout(athlete_id, scheduled_date, workout_type, duration,
                completion_status, training_notes):
    """Validate the input, then insert it. Returns (success, message)."""
    error, (workout_type, completion_status, training_notes) = check_workout_input(
        athlete_id, scheduled_date, workout_type, duration,
        completion_status, training_notes,
    )
    if error:
        return False, error

    try:
        insert_workout(athlete_id, scheduled_date, workout_type, duration,
                       completion_status, training_notes)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete no longer exists."
        return False, f"Could not add workout: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not add workout: {e.msg}"

    return True, f'Added workout "{workout_type}".'


def edit_workout(workout_id, athlete_id, scheduled_date, workout_type,
                 duration, completion_status, training_notes):
    """Validate the input, then update the workout. Returns (success, message)."""
    error, (workout_type, completion_status, training_notes) = check_workout_input(
        athlete_id, scheduled_date, workout_type, duration,
        completion_status, training_notes,
    )
    if error:
        return False, error

    try:
        updated = update_workout(workout_id, athlete_id, scheduled_date,
                                 workout_type, duration, completion_status,
                                 training_notes)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete no longer exists."
        return False, f"Could not update workout: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not update workout: {e.msg}"

    if updated == 0:
        return False, "No matching workout found."
    return True, f'Updated workout "{workout_type}".'


def remove_workout(workout_id):
    """Delete the workout together with the points earned for it,
    in one transaction. Returns (success, message)."""
    try:
        deleted = delete_workout(workout_id)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1451:  # a table we did not account for points at it
            return False, "This workout is referenced by other records and cannot be deleted."
        return False, f"Could not delete workout: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not delete workout: {e.msg}"

    if deleted["workout"] == 0:
        return False, "No matching workout found."
    return True, "Deleted workout." + describe_related(deleted, "workout")
