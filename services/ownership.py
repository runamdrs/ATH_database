"""The simulated login: the athlete picked in the sidebar is the current
user, and users may only change or delete their own content.

The UI only offers the current user's records, but the services check
again before every update and delete, so the rule holds even if a
form is changed or a record moves to someone else in the meantime.
"""


def check_owner(record, athlete_id, singular, plural):
    """Return an error message, or None when `athlete_id` owns `record`.

    `record` is the dict a get_<thing>_by_id() returned (None when no
    such record exists); its AthleteID column says who owns it."""
    if record is None:
        return f"No matching {singular} found."
    if record["AthleteID"] != athlete_id:
        return f"You can only change your own {plural}."
    return None
