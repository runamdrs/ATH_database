import datetime
from contextlib import ExitStack
from pathlib import Path
import unittest
from unittest.mock import patch

import mysql.connector
from streamlit.testing.v1 import AppTest

import athlete_service
import database
import delete_summary
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


class RecordingConnection:
    """Stands in for a MySQL connection and remembers every statement,
    so the tests can check what ran, in which order, and whether the
    transaction was committed or rolled back."""

    def __init__(self, fail_on=None, rowcount=1):
        self.statements = []
        self.committed = False
        self.rolled_back = False
        self.closed = False
        self.fail_on = fail_on
        self.rowcount = rowcount
        connection = self

        class RecordingCursor:
            rowcount = 0
            closed = False

            def execute(self, query, params):
                connection.statements.append((query, params))
                if connection.fail_on and connection.fail_on in query:
                    raise mysql.connector.Error("statement failed")
                self.rowcount = connection.rowcount

            def close(self):
                self.closed = True

        self.fake_cursor = RecordingCursor()

    def cursor(self, dictionary=False):
        return self.fake_cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True

    def tables(self):
        """The table each recorded DELETE targeted, in order."""
        return [
            query.split("DELETE FROM", 1)[1].split()[0]
            for query, _ in self.statements
            if "DELETE FROM" in query
        ]


class CascadingDeleteTests(unittest.TestCase):
    def test_deleting_an_athlete_removes_children_first_in_one_transaction(self):
        connection = RecordingConnection()
        with patch("database.get_connection", return_value=connection):
            deleted = database.delete_athlete(7)

        tables = connection.tables()
        # The athlete goes last, after everything that references them.
        self.assertEqual(tables[-1], "athlete")
        for child in ("activity_point", "activity_participant", "comment",
                      "post", "activity", "workout", "achievement",
                      "athlete_sport", "recruiter_athlete", "reward_redemption"):
            self.assertIn(child, tables)
            self.assertLess(tables.index(child), tables.index("athlete"),
                            f"{child} must be deleted before the athlete")
        # activity_point references activities and workouts, so it has to
        # go before both of them.
        self.assertLess(tables.index("activity_point"), tables.index("activity"))
        self.assertLess(tables.index("activity_point"), tables.index("workout"))
        self.assertLess(tables.index("comment"), tables.index("post"))

        # One transaction for the whole chain, and every value is bound.
        self.assertTrue(connection.committed)
        self.assertFalse(connection.rolled_back)
        self.assertTrue(connection.closed)
        self.assertTrue(connection.fake_cursor.closed)
        for query, params in connection.statements:
            self.assertIn("%s", query)
            self.assertTrue(all(value == 7 for value in params))
        self.assertEqual(deleted["athlete"], 1)

    def test_failed_child_delete_rolls_the_whole_chain_back(self):
        # The athlete's own DELETE fails, so the child deletes that
        # already ran must not be committed.
        connection = RecordingConnection(fail_on="DELETE FROM athlete WHERE")
        with patch("database.get_connection", return_value=connection):
            with self.assertRaises(mysql.connector.Error):
                database.delete_athlete(7)

        self.assertFalse(connection.committed)
        self.assertTrue(connection.rolled_back)
        self.assertTrue(connection.closed)
        self.assertTrue(connection.fake_cursor.closed)

    def test_activity_and_sponsor_deletes_clear_their_dependents(self):
        connection = RecordingConnection()
        with patch("database.get_connection", return_value=connection):
            database.delete_activity(3)
        self.assertEqual(
            connection.tables(),
            ["activity_point", "activity_participant", "activity"],
        )

        connection = RecordingConnection()
        with patch("database.get_connection", return_value=connection):
            database.delete_sponsor(5)
        self.assertEqual(
            connection.tables(), ["reward_redemption", "reward", "sponsor"]
        )

    def test_missing_athlete_is_reported_instead_of_a_success(self):
        counts = {"activity": 0, "workout": 0, "athlete": 0}
        with patch("athlete_service.delete_athlete", return_value=counts):
            result = athlete_service.remove_athlete(999)

        self.assertEqual(result, (False, "No matching athlete found."))

    def test_success_message_lists_what_else_was_deleted(self):
        counts = {
            "activity_point": 4, "activity_participant": 0, "comment": 1,
            "post": 0, "activity": 2, "workout": 0, "achievement": 0,
            "athlete_sport": 0, "recruiter_athlete": 0,
            "reward_redemption": 0, "athlete": 1,
        }
        with patch("athlete_service.delete_athlete", return_value=counts):
            success, message = athlete_service.remove_athlete(7)

        self.assertTrue(success)
        self.assertEqual(
            message,
            "Deleted athlete. Also deleted 4 points records, 1 comment "
            "and 2 activities.",
        )

    def test_no_dependents_means_no_extra_sentence(self):
        self.assertEqual(
            delete_summary.describe_related({"achievement": 1}, "achievement"), ""
        )


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
            patch("athlete_service.get_athlete_by_id", return_value=athlete),
            patch("achievement_service.get_all_achievements", return_value=[]),
            patch("achievement_service.get_all_sports", return_value=[sport]),
            patch("activity_service.get_all_activities", return_value=[]),
            patch("workout_service.get_all_workouts", return_value=[workout]),
            patch("workout_service.get_workout_by_id", return_value=workout),
            patch("sport_service.get_all_sports", return_value=[sport]),
            patch("sport_service.get_sport_by_id", return_value=sport),
            patch("sponsor_service.get_all_sponsors", return_value=[sponsor]),
            patch("sponsor_service.get_sponsor_by_id", return_value=sponsor),
            patch("reward_redemption_service.get_all_redemptions", return_value=[]),
            patch(
                "reward_redemption_service.get_rewards_for_athlete",
                return_value=[reward],
            ),
        ]

        with ExitStack() as stack:
            for active_patch in patches:
                stack.enter_context(active_patch)

            # The default 3s timeout is tight on a cold run, where the
            # first script run also imports Streamlit and pandas.
            app = AppTest.from_file(
                str(Path(__file__).resolve().parents[1] / "app.py"),
                default_timeout=30,
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

            # Every page offers the same Update/Delete choice, and picking
            # Delete must show a confirmation instead of deleting at once.
            for section, radio_key in (
                ("Athletes", "athlete_mode"), ("Workouts", "workout_mode"),
                ("Sports", "sport_mode"), ("Sponsors", "sponsor_mode"),
            ):
                app.sidebar.radio[0].set_value(section).run()
                app.radio(key=radio_key).set_value("Delete").run()
                self.assertEqual(
                    len(app.exception), 0,
                    f"{section} delete mode raised an exception",
                )
                self.assertTrue(
                    any("Confirm deletion" in box.label for box in app.checkbox),
                    f"{section} delete mode has no confirmation checkbox",
                )


if __name__ == "__main__":
    unittest.main()
