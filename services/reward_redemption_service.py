import mysql.connector

from db.database import (
    get_all_redemptions,
    get_rewards_for_athlete,
    insert_eligible_redemption,
)


def list_redemptions():
    """Return every redemption, joined with its athlete, reward and
    sponsor so the table shows names instead of IDs."""
    return get_all_redemptions()


def list_rewards_for_athlete(athlete_id):
    """Return every reward with this athlete's points and whether they
    are eligible for it."""
    return get_rewards_for_athlete(athlete_id)


def redeem_reward(athlete_id, reward_id):
    """Check the reward is still eligible, then record the redemption.
    Returns (success, message)."""
    if not athlete_id:
        return False, "Please choose an athlete."
    if not reward_id:
        return False, "Please choose an eligible reward."

    try:
        if not any(
            reward["RewardID"] == reward_id and reward["IsEligible"]
            for reward in get_rewards_for_athlete(athlete_id)
        ):
            return False, (
                "This reward is not eligible. The athlete must have enough "
                "Activity Points, the reward must be in stock, and it must "
                "not be expired."
            )
        if not insert_eligible_redemption(athlete_id, reward_id):
            return False, (
                "Eligibility changed before the redemption was saved. "
                "Refresh the reward list and try again."
            )
    except mysql.connector.IntegrityError as e:
        if e.errno == 1452:  # foreign key violation
            return False, "That athlete or reward no longer exists."
        return False, f"Could not save redemption: {e.msg}"
    except mysql.connector.Error as e:
        return False, f"Could not save redemption: {e.msg}"

    return True, "Redemption request submitted with Pending status."
