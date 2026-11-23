import datetime
from contextlib import ExitStack
from pathlib import Path
import unittest
from unittest.mock import patch

import mysql.connector
from streamlit.testing.v1 import AppTest

from db import database
from services import activity_service
from services import athlete_service
from services import delete_summary
from services import point_service
from services import post_service
from services import recruiter_interest_service
from services import reward_redemption_service
from services import sponsor_service
from services import sport_service
from services import workout_service


class ServiceTests(unittest.TestCase):
    def test_workout_validation_and_insert(self):
        with patch("services.workout_service.insert_workout") as insert:
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
        with patch("services.workout_service.insert_workout") as insert:
            result = workout_service.add_workout(
                7, datetime.date(2026, 11, 16), "Run", 0, "Scheduled", "",
            )

        self.assertFalse(result[0])
        self.assertIn("positive whole number", result[1])
        insert.assert_not_called()

    def test_workout_update_and_delete_respect_foreign_keys(self):
        workout = {"WorkoutID": 3}
        with patch(
            "services.workout_service.get_all_workouts", return_value=[workout]
        ), patch(
            "services.workout_service.update_workout", return_value=1
        ) as update:
            result = workout_service.edit_workout(
                3, 7, datetime.date(2026, 11, 16), "Run", None,
                "Completed", "",
            )

        self.assertTrue(result[0])
        update.assert_called_once()

        delete_error = mysql.connector.IntegrityError(
            "Referenced workout", errno=1451,
        )
        with patch(
            "services.workout_service.get_all_workouts", return_value=[workout]
        ), patch(
            "services.workout_service.delete_workout", side_effect=delete_error
        ):
            result = workout_service.remove_workout(3)

        self.assertFalse(result[0])
        self.assertIn("referenced", result[1])

    def test_sport_duplicate_is_reported(self):
        duplicate_error = mysql.connector.IntegrityError(
            "Duplicate sport", errno=1062,
        )
        with patch("services.sport_service.insert_sport", side_effect=duplicate_error):
            result = sport_service.add_sport("Soccer", "Team")

        self.assertEqual(
            result, (False, "A sport with that name already exists.")
        )

    def test_sport_options_use_real_sport_ids(self):
        with patch(
            "services.sport_service.get_all_sports",
            return_value=[{"SportID": 3, "Name": "Soccer", "Type": "Team"}],
        ):
            result = sport_service.get_sport_options()

        self.assertEqual(result, {3: "Soccer"})

    def test_sport_edit_and_delete_handle_relationships(self):
        sport = {"SportID": 3, "Name": "Soccer", "Type": "Team"}
        with patch("services.sport_service.get_all_sports", return_value=[sport]), \
                patch("services.sport_service.update_sport", return_value=1) as update:
            result = sport_service.edit_sport(3, "Football", "Team")

        self.assertTrue(result[0])
        update.assert_called_once_with(3, "Football", "Team")

        delete_error = mysql.connector.IntegrityError(
            "Referenced sport", errno=1451,
        )
        with patch("services.sport_service.get_all_sports", return_value=[sport]), \
                patch("services.sport_service.delete_sport", side_effect=delete_error):
            result = sport_service.remove_sport(3)

        self.assertFalse(result[0])
        self.assertIn("in use", result[1])

    def test_sponsor_duplicate_company_is_reported(self):
        with patch(
            "services.sponsor_service.get_all_sponsors",
            return_value=[{
                "SponsorID": 1,
                "Company": "Peak Performance",
                "SponsorType": None,
                "ContactInformation": None,
            }],
        ), patch("services.sponsor_service.insert_sponsor") as insert:
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
        with patch(
            "services.sponsor_service.get_all_sponsors", return_value=[sponsor]
        ), patch(
            "services.sponsor_service.update_sponsor", return_value=1
        ) as update:
            result = sponsor_service.edit_sponsor(
                5, "New Sponsor", "", "",
            )

        self.assertTrue(result[0])
        update.assert_called_once_with(5, "New Sponsor", None, None)

        delete_error = mysql.connector.IntegrityError(
            "Referenced sponsor", errno=1451,
        )
        with patch(
            "services.sponsor_service.get_all_sponsors", return_value=[sponsor]
        ), patch(
            "services.sponsor_service.delete_sponsor", side_effect=delete_error
        ):
            result = sponsor_service.remove_sponsor(5)

        self.assertFalse(result[0])
        self.assertIn("has rewards", result[1])

    def test_redemption_requires_eligibility(self):
        with patch(
            "services.reward_redemption_service.get_rewards_for_athlete",
            return_value=[{"RewardID": 4, "IsEligible": 0}],
        ), patch(
            "services.reward_redemption_service.insert_eligible_redemption"
        ) as insert:
            result = reward_redemption_service.redeem_reward(2, 4)

        self.assertFalse(result[0])
        self.assertIn("not eligible", result[1])
        insert.assert_not_called()

    def test_eligible_redemption_is_inserted_with_bound_values(self):
        with patch(
            "services.reward_redemption_service.get_rewards_for_athlete",
            return_value=[{"RewardID": 4, "IsEligible": 1}],
        ), patch(
            "services.reward_redemption_service.insert_eligible_redemption",
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
        with patch("db.database.get_connection", return_value=connection):
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
        with patch("db.database.get_connection", return_value=connection):
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
        with patch("db.database.get_connection", return_value=connection):
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
        with patch("db.database.get_connection", return_value=connection):
            with self.assertRaises(mysql.connector.Error):
                database.delete_athlete(7)

        self.assertFalse(connection.committed)
        self.assertTrue(connection.rolled_back)
        self.assertTrue(connection.closed)
        self.assertTrue(connection.fake_cursor.closed)

    def test_activity_and_sponsor_deletes_clear_their_dependents(self):
        connection = RecordingConnection()
        with patch("db.database.get_connection", return_value=connection):
            database.delete_activity(3)
        self.assertEqual(
            connection.tables(),
            ["activity_point", "activity_participant", "activity"],
        )

        connection = RecordingConnection()
        with patch("db.database.get_connection", return_value=connection):
            database.delete_sponsor(5)
        self.assertEqual(
            connection.tables(), ["reward_redemption", "reward", "sponsor"]
        )

    def test_missing_athlete_is_reported_instead_of_a_success(self):
        counts = {"activity": 0, "workout": 0, "athlete": 0}
        with patch("services.athlete_service.delete_athlete", return_value=counts):
            result = athlete_service.remove_athlete(999)

        self.assertEqual(result, (False, "No matching athlete found."))

    def test_success_message_lists_what_else_was_deleted(self):
        counts = {
            "activity_point": 4, "activity_participant": 0, "comment": 1,
            "post": 0, "activity": 2, "workout": 0, "achievement": 0,
            "athlete_sport": 0, "recruiter_athlete": 0,
            "reward_redemption": 0, "athlete": 1,
        }
        with patch("services.athlete_service.delete_athlete", return_value=counts):
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


class AthleteSportTests(unittest.TestCase):
    def test_new_athlete_and_sports_are_saved_in_one_transaction(self):
        connection = RecordingConnection()
        with patch("db.database.get_connection", return_value=connection):
            database.insert_athlete("Ann", "ann", "ann@example.com", None,
                                    "Beginner", [2, 5])

        queries = [query for query, _ in connection.statements]
        self.assertIn("INSERT INTO athlete ", queries[0])
        # The links point at the athlete MySQL just created.
        self.assertEqual(len(queries), 3)
        for query in queries[1:]:
            self.assertIn("LAST_INSERT_ID()", query)
        self.assertEqual([params for _, params in connection.statements[1:]],
                         [(2,), (5,)])
        self.assertTrue(connection.committed)

    def test_updating_an_athlete_replaces_their_sports(self):
        connection = RecordingConnection()
        with patch("db.database.get_connection", return_value=connection):
            database.update_athlete(7, "Ann", "ann", "ann@example.com", None,
                                    "Beginner", [3])

        queries = [query for query, _ in connection.statements]
        self.assertIn("UPDATE athlete", queries[0])
        self.assertIn("DELETE FROM athlete_sport", queries[1])
        self.assertIn("INSERT INTO athlete_sport", queries[2])
        self.assertEqual(connection.statements[2][1], (7, 3))
        self.assertTrue(connection.committed)

    def test_edit_reports_a_missing_athlete(self):
        with patch("services.athlete_service.update_athlete",
                   return_value={"athlete": 0, "athlete_sport": 0}):
            result = athlete_service.edit_athlete(
                999, "Ann", "ann", "ann@example.com", "", "Beginner", [1],
            )
        self.assertEqual(result, (False, "No matching athlete found."))


class ActivityParticipantTests(unittest.TestCase):
    def test_full_activity_cannot_be_joined(self):
        with patch("services.activity_service.insert_participant", return_value=0):
            result = activity_service.join_activity(3, 7)
        self.assertEqual(result, (False, "This activity is full or no longer exists."))

    def test_joining_twice_is_reported(self):
        duplicate = mysql.connector.IntegrityError(msg="dup", errno=1062)
        with patch("services.activity_service.insert_participant",
                   side_effect=duplicate):
            success, message = activity_service.join_activity(3, 7)
        self.assertFalse(success)
        self.assertEqual(message, "That athlete has already joined this activity.")

    def test_attended_awards_points_in_the_same_transaction(self):
        connection = RecordingConnection()
        with patch("db.database.get_connection", return_value=connection):
            changed = database.update_participant_status(3, 7, "Attended", 10)

        queries = [query for query, _ in connection.statements]
        self.assertIn("UPDATE activity_participant", queries[0])
        self.assertIn("INSERT INTO activity_point", queries[1])
        self.assertIn("NOT EXISTS", queries[1])
        self.assertTrue(connection.committed)
        self.assertEqual(changed, {"activity_participant": 1, "activity_point": 1})

    def test_other_statuses_award_nothing(self):
        connection = RecordingConnection()
        with patch("db.database.get_connection", return_value=connection):
            database.update_participant_status(3, 7, "No-Show", 10)
        self.assertEqual(len(connection.statements), 1)

    def test_status_messages(self):
        with patch("services.activity_service.update_participant_status",
                   return_value={"activity_participant": 1, "activity_point": 1}):
            self.assertEqual(
                activity_service.change_participation_status(3, 7, "Attended", 10),
                (True, "Updated status to Attended. Awarded 10 points."),
            )
        with patch("services.activity_service.update_participant_status",
                   return_value={"activity_participant": 0}):
            self.assertEqual(
                activity_service.change_participation_status(3, 7, "No-Show", 10),
                (False, "No matching participant found."),
            )
        self.assertEqual(
            activity_service.change_participation_status(3, 7, "Lost", 10),
            (False, "Please choose a valid status."),
        )


    def test_removing_a_participant(self):
        connection = RecordingConnection()
        with patch("db.database.get_connection", return_value=connection):
            database.delete_participant(3, 7)
        self.assertEqual(connection.tables(), ["activity_participant"])
        self.assertEqual(connection.statements[0][1], (3, 7))

        with patch("services.activity_service.delete_participant",
                   return_value={"activity_participant": 0}):
            self.assertEqual(
                activity_service.remove_participant(3, 99),
                (False, "No matching participation entry found."),
            )


class RecruiterInterestTests(unittest.TestCase):
    def test_new_interest_starts_as_interested_with_cleaned_notes(self):
        with patch("services.recruiter_interest_service.insert_recruiter_interest") \
                as insert_interest:
            result = recruiter_interest_service.express_interest(2, 7, "   ")
        self.assertEqual(result, (True, "Added recruiter interest."))
        # Blank notes are stored as NULL; the date is CURDATE() in the SQL.
        insert_interest.assert_called_once_with(2, 7, "Interested", None)

    def test_second_interest_from_the_same_recruiter_is_reported(self):
        duplicate = mysql.connector.IntegrityError(msg="dup", errno=1062)
        with patch("services.recruiter_interest_service.insert_recruiter_interest",
                   side_effect=duplicate):
            result = recruiter_interest_service.express_interest(2, 7, "")
        self.assertEqual(
            result,
            (False, "That recruiter has already shown interest in this athlete."),
        )

    def test_status_must_be_one_of_the_known_values(self):
        self.assertEqual(
            recruiter_interest_service.edit_interest(2, 7, "Hired", ""),
            (False, "Please choose a valid status."),
        )
        with patch("services.recruiter_interest_service.update_recruiter_interest",
                   return_value=0):
            self.assertEqual(
                recruiter_interest_service.edit_interest(2, 7, "Contacted", ""),
                (False, "No matching recruiter interest found."),
            )

    def test_withdrawing_interest_is_one_bound_statement(self):
        connection = RecordingConnection()
        with patch("db.database.get_connection", return_value=connection):
            deleted = database.delete_recruiter_interest(2, 7)
        self.assertEqual(connection.tables(), ["recruiter_athlete"])
        self.assertEqual(connection.statements[0][1], (2, 7))
        self.assertTrue(connection.committed)
        self.assertEqual(deleted, {"recruiter_athlete": 1})


class PointTests(unittest.TestCase):
    def test_point_validation_and_insert(self):
        today = datetime.date(2026, 11, 23)
        self.assertEqual(point_service.add_point(1, None, None, 0, "Bonus", today),
                         (False, "Points must be at least 1."))
        self.assertEqual(point_service.add_point(1, None, None, 5, "  ", today),
                         (False, "Reason is required."))
        with patch("services.point_service.insert_point") as insert_point:
            result = point_service.add_point(1, None, None, 5, "  Bonus  ", today)
        self.assertEqual(result, (True, 'Added points record "Bonus".'))
        insert_point.assert_called_once_with(1, None, None, 5, "Bonus", today)

    def test_workout_points_must_go_to_that_workouts_athlete(self):
        with patch("services.point_service.get_workout_by_id",
                   return_value={"WorkoutID": 2, "AthleteID": 8}), \
             patch("services.point_service.insert_point") as insert_point:
            result = point_service.add_point(1, None, 2, 5, "Run", None)
        self.assertEqual(result, (False, "That workout belongs to another athlete."))
        insert_point.assert_not_called()

    def test_point_edit_and_delete_report_missing_records(self):
        with patch("services.point_service.update_point", return_value=0):
            self.assertEqual(
                point_service.edit_point(99, 1, None, None, 5, "Bonus", None),
                (False, "No matching points record found."),
            )
        with patch("services.point_service.delete_point",
                   return_value={"activity_point": 1}):
            self.assertEqual(point_service.remove_point(1),
                             (True, "Deleted points record."))


class PostTests(unittest.TestCase):
    def test_post_validation_and_insert(self):
        self.assertEqual(post_service.add_post(1, "   ", ""),
                         (False, "Post content is required."))
        with patch("services.post_service.insert_post") as insert_post:
            result = post_service.add_post(1, "  Great run!  ", "  ")
        self.assertEqual(result, (True, "Added post."))
        # Text is trimmed and an empty optional URL is stored as NULL.
        insert_post.assert_called_once_with(1, "Great run!", None)

    def test_comment_edit_and_delete(self):
        self.assertEqual(post_service.edit_comment(1, "  "),
                         (False, "Comment text is required."))
        with patch("services.post_service.update_comment", return_value=0):
            self.assertEqual(post_service.edit_comment(99, "Hi"),
                             (False, "No matching comment found."))
        with patch("services.post_service.delete_comment",
                   return_value={"comment": 1}):
            self.assertEqual(post_service.remove_comment(1),
                             (True, "Deleted comment."))

    def test_deleting_a_comment_is_one_bound_statement(self):
        connection = RecordingConnection()
        with patch("db.database.get_connection", return_value=connection):
            database.delete_comment(4)
        self.assertEqual(connection.tables(), ["comment"])
        self.assertEqual(connection.statements[0][1], (4,))
        self.assertTrue(connection.committed)

    def test_comment_on_a_deleted_post_is_reported(self):
        missing = mysql.connector.IntegrityError(msg="fk", errno=1452)
        with patch("services.post_service.insert_comment", side_effect=missing):
            result = post_service.add_comment(1, 99, "Nice")
        self.assertEqual(result, (False, "That athlete or post no longer exists."))


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
        post = {
            "PostID": 1,
            "Athlete": "Test Athlete",
            "Content": "First post",
            "DateCreated": datetime.datetime(2026, 11, 16, 9, 0),
            "MediaURL": None,
            "Comments": 1,
        }
        recruiter = {
            "RecruiterID": 1, "Name": "Sam Scout", "Organization": None,
            "Email": "sam@example.com",
        }
        interest = {
            "RecruiterID": 1, "AthleteID": 1, "Recruiter": "Sam Scout",
            "Organization": None, "InterestDate": datetime.date(2026, 11, 20),
            "Status": "Contacted", "Notes": None,
        }
        comment = {
            "CommentID": 1, "AthleteID": 1, "PostID": 1, "Athlete": "Test Athlete",
            "Text": "Nice!", "DateCreated": datetime.datetime(2026, 11, 16, 10, 0),
        }
        activity_row = {
            "ActivityID": 1, "AthleteID": 1, "Sport": "Soccer", "Type": "Practice",
            "Date": datetime.date(2026, 11, 20), "Time": "09:00", "Duration": 60,
            "Location": None, "MaxParticipants": None,
        }
        activity = {
            "ActivityID": 1, "AthleteID": 1, "SportID": 1, "Type": "Practice",
            "Date": datetime.date(2026, 11, 20),
            "Time": datetime.timedelta(hours=9), "Duration": 60,
            "Location": None, "MaxParticipants": None,
        }
        participant = {
            "ActivityID": 1, "AthleteID": 1, "Athlete": "Test Athlete",
            "JoinDate": datetime.date(2026, 11, 16),
            "ParticipationStatus": "Registered",
        }
        point = {
            "PointTransactionID": 1, "AthleteID": 1, "Athlete": "Test Athlete",
            "ActivityID": 1, "WorkoutID": None, "Activity": "Practice",
            "Workout": None, "PointsEarned": 10, "Reason": "Attended activity",
            "DateEarned": datetime.datetime(2026, 11, 20, 11, 0),
        }
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
            patch("services.athlete_service.get_all_athletes", return_value=[athlete]),
            patch("services.athlete_service.get_athlete_by_id", return_value=athlete),
            patch("services.athlete_service.get_sport_ids_for_athlete", return_value=[1]),
            patch("services.post_service.get_all_posts", return_value=[post]),
            patch("services.recruiter_interest_service.get_all_recruiters",
                  return_value=[recruiter]),
            patch("services.recruiter_interest_service.get_interest_for_athlete",
                  return_value=[interest]),
            patch("services.recruiter_interest_service.get_recruiter_interest",
                  return_value=interest),
            patch("services.post_service.get_comments_for_post", return_value=[comment]),
            patch("services.post_service.get_comment_by_id", return_value=comment),
            # A fresh copy per call, like the database: get_activity_details
            # converts Time in place.
            patch("services.activity_service.get_activity_by_id",
                  side_effect=lambda activity_id: dict(activity)),
            patch("services.activity_service.get_roster", return_value=[participant]),
            patch("services.activity_service.get_participant", return_value=participant),
            patch("services.point_service.get_all_points", return_value=[point]),
            patch("services.point_service.get_point_by_id",
                  side_effect=lambda point_id: dict(point)),
            patch("services.achievement_service.get_all_achievements", return_value=[]),
            patch("services.achievement_service.get_all_sports", return_value=[sport]),
            patch("services.activity_service.get_all_activities",
                  side_effect=lambda: [dict(activity_row)]),
            patch("services.workout_service.get_all_workouts", return_value=[workout]),
            patch("services.workout_service.get_workout_by_id", return_value=workout),
            patch("services.sport_service.get_all_sports", return_value=[sport]),
            patch("services.sport_service.get_sport_by_id", return_value=sport),
            patch("services.sponsor_service.get_all_sponsors", return_value=[sponsor]),
            patch("services.sponsor_service.get_sponsor_by_id", return_value=sponsor),
            patch(
                "services.reward_redemption_service.get_all_redemptions",
                return_value=[],
            ),
            patch(
                "services.reward_redemption_service.get_rewards_for_athlete",
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
                "Achievements", "Activities", "Workouts", "Points",
                "Sports", "Sponsors", "Posts", "Reward Redemptions",
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
                ("Points", "point_mode"), ("Posts", "comment_mode"),
                ("Activities", "participant_mode"), ("Athletes", "interest_mode"),
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
