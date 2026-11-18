import datetime
from pathlib import Path
import unittest
from unittest.mock import patch

import mysql.connector
from streamlit.testing.v1 import AppTest

import database
import reward_redemption_service
import sponsor_service
import sport_service
import workout_service


class ServiceTests(unittest.TestCase):
    def test_workout_validation_and_insert(self):
        with patch("workout_service.insert_workout") as insert:
            result = workout_service.add_workout(
                7, datetime.date(2026, 11, 16), "  Run  ", 30,
                "Scheduled", "  intervals  ",
            )

        self.assertEqual(result, (True, 'Added workout "Run".'))
        insert.assert_called_once_with(
            7, datetime.date(2026, 11, 16), "Run", 30,
            "Scheduled", "intervals",
        )

    def test_workout_rejects_invalid_duration_without_writing(self):
        with patch("workout_service.insert_workout") as insert:
            result = workout_service.add_workout(
                7, datetime.date(2026, 11, 16), "Run", 0, "Scheduled", "",
            )

        self.assertFalse(result[0])
        self.assertIn("positive whole number", result[1])
        insert.assert_not_called()

    def test_workout_update_and_delete_respect_foreign_keys(self):
        workout = {"WorkoutID": 3}
        with patch("workout_service.get_all_workouts", return_value=[workout]), \
                patch("workout_service.update_workout", return_value=1) as update:
            result = workout_service.edit_workout(
                3, 7, datetime.date(2026, 11, 16), "Run", None,
                "Completed", "",
            )

        self.assertTrue(result[0])
        update.assert_called_once()

        delete_error = mysql.connector.IntegrityError(
            "Referenced workout", errno=1451,
        )
        with patch("workout_service.get_all_workouts", return_value=[workout]), \
                patch("workout_service.delete_workout", side_effect=delete_error):
            result = workout_service.remove_workout(3)

        self.assertFalse(result[0])
        self.assertIn("referenced", result[1])

    def test_sport_duplicate_is_reported(self):
        duplicate_error = mysql.connector.IntegrityError(
            "Duplicate sport", errno=1062,
        )
        with patch("sport_service.insert_sport", side_effect=duplicate_error):
            result = sport_service.add_sport("Soccer", "Team")

        self.assertEqual(
            result, (False, "A sport with that name already exists.")
        )

    def test_sport_options_use_real_sport_ids(self):
        with patch(
            "sport_service.get_all_sports",
            return_value=[{"SportID": 3, "Name": "Soccer", "Type": "Team"}],
        ):
            result = sport_service.get_sport_options()

        self.assertEqual(result, {3: "Soccer"})

    def test_sport_edit_and_delete_handle_relationships(self):
        sport = {"SportID": 3, "Name": "Soccer", "Type": "Team"}
        with patch("sport_service.get_all_sports", return_value=[sport]), \
                patch("sport_service.update_sport", return_value=1) as update:
            result = sport_service.edit_sport(3, "Football", "Team")

        self.assertTrue(result[0])
        update.assert_called_once_with(3, "Football", "Team")

        delete_error = mysql.connector.IntegrityError(
            "Referenced sport", errno=1451,
        )
        with patch("sport_service.get_all_sports", return_value=[sport]), \
                patch("sport_service.delete_sport", side_effect=delete_error):
            result = sport_service.remove_sport(3)

        self.assertFalse(result[0])
        self.assertIn("in use", result[1])

    def test_sponsor_duplicate_company_is_reported(self):
        with patch(
            "sponsor_service.get_all_sponsors",
            return_value=[{
                "SponsorID": 1,
                "Company": "Peak Performance",
                "SponsorType": None,
                "ContactInformation": None,
            }],
        ), patch("sponsor_service.insert_sponsor") as insert:
            result = sponsor_service.add_sponsor(
                " peak performance ", "", "",
            )

        self.assertFalse(result[0])
        self.assertIn("already exists", result[1])
        insert.assert_not_called()

    def test_sponsor_edit_and_delete_handle_rewards(self):
        sponsor = {
            "SponsorID": 5,
            "Company": "Test Sponsor",
            "SponsorType": None,
            "ContactInformation": None,
        }
        with patch("sponsor_service.get_all_sponsors", return_value=[sponsor]), \
                patch("sponsor_service.update_sponsor", return_value=1) as update:
            result = sponsor_service.edit_sponsor(
                5, "New Sponsor", "", "",
            )

        self.assertTrue(result[0])
        update.assert_called_once_with(5, "New Sponsor", None, None)

        delete_error = mysql.connector.IntegrityError(
            "Referenced sponsor", errno=1451,
        )
        with patch("sponsor_service.get_all_sponsors", return_value=[sponsor]), \
                patch("sponsor_service.delete_sponsor", side_effect=delete_error):
            result = sponsor_service.remove_sponsor(5)

        self.assertFalse(result[0])
        self.assertIn("has rewards", result[1])

    def test_redemption_requires_eligibility(self):
        with patch(
            "reward_redemption_service.get_rewards_for_athlete",
            return_value=[{"RewardID": 4, "IsEligible": 0}],
        ), patch(
            "reward_redemption_service.insert_eligible_redemption"
        ) as insert:
            result = reward_redemption_service.redeem_reward(2, 4)

        self.assertFalse(result[0])
        self.assertIn("not eligible", result[1])
        insert.assert_not_called()

    def test_eligible_redemption_is_inserted_with_bound_values(self):
        with patch(
            "reward_redemption_service.get_rewards_for_athlete",
            return_value=[{"RewardID": 4, "IsEligible": 1}],
        ), patch(
            "reward_redemption_service.insert_eligible_redemption",
            return_value=1,
        ) as insert:
            result = reward_redemption_service.redeem_reward(2, 4)

        self.assertEqual(
            result, (True, "Redemption request submitted with Pending status.")
        )
        insert.assert_called_once_with(2, 4)

    def test_run_write_commits_and_closes_resources(self):
        class FakeCursor:
            rowcount = 1

            def execute(self, query, params):
                self.query = query
                self.params = params

            def close(self):
                self.closed = True

        class FakeConnection:
            def __init__(self):
                self.fake_cursor = FakeCursor()
                self.committed = False
                self.closed = False

            def cursor(self):
                return self.fake_cursor

            def commit(self):
                self.committed = True

            def rollback(self):
                raise AssertionError("Unexpected rollback")

            def close(self):
                self.closed = True

        connection = FakeConnection()
        with patch("database.get_connection", return_value=connection):
            result = database.insert_eligible_redemption(2, 4)

        self.assertEqual(result, 1)
        self.assertIn("%s", connection.fake_cursor.query)
        self.assertEqual(connection.fake_cursor.params, (2, 4, 2, 2))
        self.assertTrue(connection.committed)
        self.assertTrue(connection.fake_cursor.closed)
        self.assertTrue(connection.closed)

    def test_run_write_rolls_back_and_closes_resources_on_failure(self):
        class FakeCursor:
            closed = False

            def execute(self, query, params):
                raise RuntimeError("write failed")

            def close(self):
                self.closed = True

        class FakeConnection:
            def __init__(self):
                self.fake_cursor = FakeCursor()
                self.rolled_back = False
                self.closed = False

            def cursor(self):
                return self.fake_cursor

            def commit(self):
                raise AssertionError("Unexpected commit")

            def rollback(self):
                self.rolled_back = True

            def close(self):
                self.closed = True

        connection = FakeConnection()
        with patch("database.get_connection", return_value=connection):
            with self.assertRaisesRegex(RuntimeError, "write failed"):
                database.insert_eligible_redemption(2, 4)

        self.assertTrue(connection.rolled_back)
        self.assertTrue(connection.fake_cursor.closed)
        self.assertTrue(connection.closed)


class StreamlitPageTests(unittest.TestCase):
    def test_all_navigation_pages_render_without_database(self):
        athlete = {
            "AthleteID": 1,
            "Name": "Test Athlete",
            "Username": "test",
            "Email": "test@example.com",
            "Location": None,
            "SkillLevel": "Beginner",
        }
        workout = {
            "WorkoutID": 1,
            "AthleteID": 1,
            "Athlete": "Test Athlete",
            "ScheduledDate": datetime.date(2026, 11, 16),
            "WorkoutType": "Run",
            "Duration": 30,
            "CompletionStatus": "Scheduled",
            "TrainingNotes": None,
        }
        sport = {"SportID": 1, "Name": "Soccer", "Type": "Team"}
        sponsor = {
            "SponsorID": 1,
            "Company": "Test Sponsor",
            "SponsorType": None,
            "ContactInformation": None,
        }
        reward = {
            "RewardID": 1,
            "Description": "Water bottle",
            "PointsRequired": 10,
            "Availability": 2,
            "ExpirationDate": datetime.date(2027, 1, 1),
            "Sponsor": "Test Sponsor",
            "AthletePoints": 20,
            "IsEligible": 1,
        }
        patches = [
            patch("athlete_service.get_all_athletes", return_value=[athlete]),
            patch("achievement_service.get_all_achievements", return_value=[]),
            patch("achievement_service.get_all_sports", return_value=[sport]),
            patch("activity_service.get_all_activities", return_value=[]),
            patch("workout_service.get_all_workouts", return_value=[workout]),
            patch("sport_service.get_all_sports", return_value=[sport]),
            patch("sponsor_service.get_all_sponsors", return_value=[sponsor]),
            patch("reward_redemption_service.get_all_redemptions", return_value=[]),
            patch(
                "reward_redemption_service.get_rewards_for_athlete",
                return_value=[reward],
            ),
        ]

        with patches[0], patches[1], patches[2], patches[3], patches[4], \
                patches[5], patches[6], patches[7], patches[8]:
            app = AppTest.from_file(
                str(Path(__file__).resolve().parents[1] / "app.py")
            ).run()
            self.assertEqual(len(app.exception), 0)

            for section in (
                "Achievements", "Activities", "Workouts",
                "Sports", "Sponsors", "Reward Redemptions",
            ):
                app.sidebar.radio[0].set_value(section).run()
                self.assertEqual(
                    len(app.exception), 0,
                    f"{section} page raised an exception",
                )


if __name__ == "__main__":
    unittest.main()
