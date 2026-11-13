from database import get_all_athletes


def search_athletes(search, skill_level):
    """Return athletes whose name or username contains `search`
    and whose skill level matches the selected filter."""
    athlete_list = get_all_athletes()
    filtered_athletes = []

    for athlete in athlete_list:
        searchable_text = f"{athlete['Name']} {athlete['Username']}".lower()
        name_matches = search.lower() in searchable_text
        skill_matches = (skill_level == "All") or (athlete["SkillLevel"] == skill_level)

        if name_matches and skill_matches:
            filtered_athletes.append(athlete)

    return filtered_athletes


def get_skill_levels():
    """Build the dropdown options from the data itself."""
    levels = {athlete["SkillLevel"] for athlete in get_all_athletes()}
    return ["All"] + sorted(levels)
