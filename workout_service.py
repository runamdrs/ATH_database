import mysql.connector

from database import (
    delete_workout,
    get_all_workouts,
    insert_workout,
    update_workout,
)


def list_workouts():
    return get_all_workouts()


def add_workout(athlete_id, scheduled_date, workout_type, duration,
               completion_status, training_notes):
    workout_type = (workout_type or "").strip()
    completion_status = (completion_status or "").strip()
    training_notes = (training_notes or "").strip() or None

    if not athlete_id:
        return False, "Please choose an athlete."
    if not scheduled_date:
        return False, "Scheduled date is required."
    if not workout_type:
        return False, "Workout type is required."
    if len(workout_type) > 50:
        return False, "Workout type must be 50 characters or fewer."
    if duration is not None and (not isinstance(duration, int) or duration < 1):
        return False, "Duration must be a positive whole number of minutes."
    if not completion_status:
        return False, "Completion status is required."
    if len(completion_status) > 20:
        return False, "Completion status must be 20 characters or fewer."

    try:
        insert_workout(
            athlete_id, scheduled_date, workout_type, duration,
            completion_status, training_notes,
        )
    except mysql.connector.IntegrityError as error:
        if error.errno == 1452:
            return False, "That athlete no longer exists."
        return False, f"Could not add workout: {error.msg}"
    except mysql.connector.Error as error:
        return False, f"Could not add workout: {error.msg}"

    return True, f'Added workout "{workout_type}".'


def edit_workout(workout_id, athlete_id, scheduled_date, workout_type,
                 duration, completion_status, training_notes):
    workout_type = (workout_type or "").strip()
    completion_status = (completion_status or "").strip()
    training_notes = (training_notes or "").strip() or None

    if not athlete_id:
        return False, "Please choose an athlete."
    if not scheduled_date:
        return False, "Scheduled date is required."
    if not workout_type:
        return False, "Workout type is required."
    if len(workout_type) > 50:
        return False, "Workout type must be 50 characters or fewer."
    if duration is not None and (not isinstance(duration, int) or duration < 1):
        return False, "Duration must be a positive whole number of minutes."
    if not completion_status:
        return False, "Completion status is required."
    if len(completion_status) > 20:
        return False, "Completion status must be 20 characters or fewer."

    try:
        if not any(row["WorkoutID"] == workout_id for row in get_all_workouts()):
            return False, "That workout no longer exists."
        update_workout(
            workout_id, athlete_id, scheduled_date, workout_type, duration,
            completion_status, training_notes,
        )
    except mysql.connector.IntegrityError as error:
        if error.errno == 1452:
            return False, "That athlete no longer exists."
        return False, f"Could not update workout: {error.msg}"
    except mysql.connector.Error as error:
        return False, f"Could not update workout: {error.msg}"

    return True, f'Updated workout "{workout_type}".'


def remove_workout(workout_id):
    try:
        if not any(row["WorkoutID"] == workout_id for row in get_all_workouts()):
            return False, "That workout no longer exists."
        delete_workout(workout_id)
    except mysql.connector.IntegrityError as error:
        if error.errno == 1451:
            return False, "This workout is referenced by other records and cannot be deleted."
        return False, f"Could not delete workout: {error.msg}"
    except mysql.connector.Error as error:
        return False, f"Could not delete workout: {error.msg}"

    return True, "Workout deleted."
