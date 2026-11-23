"""Turning the {table: rows deleted} counts that database.py's delete
functions return into a sentence the user can read.

Deleting a record now takes its dependent records with it, so the
success message has to say exactly what else disappeared.
"""

# table name -> (singular, plural) as they should appear to the user
RECORD_NAMES = {
    "achievement": ("achievement", "achievements"),
    "activity": ("activity", "activities"),
    "activity_participant": ("participation entry", "participation entries"),
    "activity_point": ("points record", "points records"),
    "athlete_sport": ("sport link", "sport links"),
    "comment": ("comment", "comments"),
    "post": ("post", "posts"),
    "recruiter_athlete": ("recruiter link", "recruiter links"),
    "reward": ("reward", "rewards"),
    "reward_redemption": ("redemption", "redemptions"),
    "workout": ("workout", "workouts"),
}


def describe_related(counts, parent_table):
    """Return something like " Also deleted 3 activities and 1 workout."
    for the dependent records, or "" when there were none.

    `counts` is the {table: rows deleted} dict from a delete function,
    and `parent_table` is the record the user actually deleted, which
    is left out of the list."""
    parts = []
    for table, count in counts.items():
        if table == parent_table or not count:
            continue
        singular, plural = RECORD_NAMES.get(table, (table, table))
        parts.append(f"{count} {singular if count == 1 else plural}")

    if not parts:
        return ""
    if len(parts) == 1:
        listed = parts[0]
    else:
        listed = ", ".join(parts[:-1]) + f" and {parts[-1]}"
    return f" Also deleted {listed}."
