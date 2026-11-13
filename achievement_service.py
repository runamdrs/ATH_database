from database import get_all_achievements


def search_achievements(search, date_earned):
    """Return achievements whose title contains `search`
    and that were earned on the selected date."""
    achievement_list = get_all_achievements()
    filtered_achievements = []

    for achievement in achievement_list:
        title_matches = search.lower() in achievement["Title"].lower()
        # str() because MySQL returns DateEarned as a datetime.date,
        # while the dropdown value is a string.
        date_matches = (date_earned == "All") or (str(achievement["DateEarned"]) == date_earned)

        if title_matches and date_matches:
            filtered_achievements.append(achievement)

    return filtered_achievements


def get_dates_earned():
    """Build the dropdown options from the data itself."""
    dates = {str(a["DateEarned"]) for a in get_all_achievements()}
    return ["All"] + sorted(dates)
