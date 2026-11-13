from database import get_all_achievements

def search_achievements(search, date_earned):
    achievement_list = get_all_achievements()
    filtered_achievements = []

    for achievement in achievement_list:
        title_matches = search.lower() in achievement["title"].lower()
        date_matches = date_earned == achievement["date_earned"]

        if title_matches and date_matches:
            filtered_achievements.append(achievement)

    return filtered_achievements
        