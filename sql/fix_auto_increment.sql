-- ---------------------------------------------------------------
-- Giving every single-column primary key an AUTO_INCREMENT.
--
-- WHY: the tables were created without it, so the app cannot insert
-- into them at all - MySQL answers
--     Field 'SportID' doesn't have a default value       (errno 1364)
-- because an INSERT that does not name the primary key has no value
-- to put there. AUTO_INCREMENT makes MySQL supply the next number,
-- which is what every INSERT in database.py relies on.
--
-- The junction tables (activity_participant, athlete_sport,
-- recruiter_athlete) are deliberately NOT here. Their primary keys
-- are composite and both halves come from the dropdowns, so there is
-- nothing for MySQL to generate.
--
-- WHY THE FOREIGN KEYS COME OUT AND GO BACK IN: MySQL refuses to
-- alter a column that a foreign key points at (errno 1833), and that
-- is every parent table below. The usual shortcut is to switch
-- FOREIGN_KEY_CHECKS off for the session, but that turns the whole
-- integrity check off while it runs. Dropping each constraint by name
-- and adding it back with the same definition keeps enforcement on
-- throughout, and re-adding re-validates the rows, so a broken
-- reference would fail loudly here instead of slipping through.
--
-- BEFORE YOU RUN IT: take a backup. backup_before_auto_increment.sql
-- in this folder is one, taken 2026-11-20.
-- IF A STEP FAILS PARTWAY: run restore_foreign_keys.sql, which puts
-- all ten constraints back, then start again.
--
-- The statements are safe to run twice: a column that already has
-- AUTO_INCREMENT is left as it is. No row is read or changed.
-- ---------------------------------------------------------------


-- 1. Release the ten foreign keys that point at the tables below.

ALTER TABLE achievement       DROP FOREIGN KEY achievement_ibfk_2;
ALTER TABLE activity          DROP FOREIGN KEY activity_ibfk_2;
ALTER TABLE activity_participant DROP FOREIGN KEY activity_participant_ibfk_1;
ALTER TABLE activity_point    DROP FOREIGN KEY activity_point_ibfk_2;
ALTER TABLE activity_point    DROP FOREIGN KEY activity_point_ibfk_3;
ALTER TABLE athlete_sport     DROP FOREIGN KEY athlete_sport_ibfk_2;
ALTER TABLE comment           DROP FOREIGN KEY comment_ibfk_2;
ALTER TABLE recruiter_athlete DROP FOREIGN KEY recruiter_athlete_ibfk_1;
ALTER TABLE reward            DROP FOREIGN KEY reward_ibfk_1;
ALTER TABLE reward_redemption DROP FOREIGN KEY reward_redemption_ibfk_2;


-- 2. Add the AUTO_INCREMENT. The last three already have it; repeating
--    them costs nothing and keeps this file complete for a fresh database.

ALTER TABLE activity          MODIFY ActivityID         INT NOT NULL AUTO_INCREMENT;
ALTER TABLE workout           MODIFY WorkoutID          INT NOT NULL AUTO_INCREMENT;
ALTER TABLE sport             MODIFY SportID            INT NOT NULL AUTO_INCREMENT;
ALTER TABLE sponsor           MODIFY SponsorID          INT NOT NULL AUTO_INCREMENT;
ALTER TABLE post              MODIFY PostID             INT NOT NULL AUTO_INCREMENT;
ALTER TABLE reward            MODIFY RewardID           INT NOT NULL AUTO_INCREMENT;
ALTER TABLE recruiter         MODIFY RecruiterID        INT NOT NULL AUTO_INCREMENT;
ALTER TABLE comment           MODIFY CommentID          INT NOT NULL AUTO_INCREMENT;
ALTER TABLE activity_point    MODIFY PointTransactionID INT NOT NULL AUTO_INCREMENT;
ALTER TABLE reward_redemption MODIFY RedemptionID       INT NOT NULL AUTO_INCREMENT;


-- 3. Put the ten constraints back, exactly as they were.

ALTER TABLE achievement ADD CONSTRAINT achievement_ibfk_2
    FOREIGN KEY (SportID) REFERENCES sport (SportID)
    ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE activity ADD CONSTRAINT activity_ibfk_2
    FOREIGN KEY (SportID) REFERENCES sport (SportID)
    ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE activity_participant ADD CONSTRAINT activity_participant_ibfk_1
    FOREIGN KEY (ActivityID) REFERENCES activity (ActivityID)
    ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE activity_point ADD CONSTRAINT activity_point_ibfk_2
    FOREIGN KEY (ActivityID) REFERENCES activity (ActivityID)
    ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE activity_point ADD CONSTRAINT activity_point_ibfk_3
    FOREIGN KEY (WorkoutID) REFERENCES workout (WorkoutID)
    ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE athlete_sport ADD CONSTRAINT athlete_sport_ibfk_2
    FOREIGN KEY (SportID) REFERENCES sport (SportID)
    ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE comment ADD CONSTRAINT comment_ibfk_2
    FOREIGN KEY (PostID) REFERENCES post (PostID)
    ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE recruiter_athlete ADD CONSTRAINT recruiter_athlete_ibfk_1
    FOREIGN KEY (RecruiterID) REFERENCES recruiter (RecruiterID)
    ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE reward ADD CONSTRAINT reward_ibfk_1
    FOREIGN KEY (SponsorID) REFERENCES sponsor (SponsorID)
    ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE reward_redemption ADD CONSTRAINT reward_redemption_ibfk_2
    FOREIGN KEY (RewardID) REFERENCES reward (RewardID)
    ON DELETE NO ACTION ON UPDATE NO ACTION;


-- ---------------------------------------------------------------
-- 4. Check it worked. Every row of the first query should read YES,
--    and the second should still report 20.
-- ---------------------------------------------------------------

SELECT c.TABLE_NAME,
       c.COLUMN_NAME,
       CASE WHEN c.EXTRA = 'auto_increment' THEN 'YES' ELSE 'no' END AS AutoIncrement
FROM information_schema.COLUMNS c
JOIN information_schema.TABLES t
  ON t.TABLE_SCHEMA = c.TABLE_SCHEMA
 AND t.TABLE_NAME = c.TABLE_NAME
WHERE c.TABLE_SCHEMA = DATABASE()
  AND c.COLUMN_KEY = 'PRI'
  AND t.TABLE_TYPE = 'BASE TABLE'
  AND c.TABLE_NAME NOT IN ('activity_participant', 'athlete_sport',
                           'recruiter_athlete')
ORDER BY c.TABLE_NAME;

SELECT COUNT(*) AS ForeignKeyColumns
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = DATABASE()
  AND REFERENCED_TABLE_NAME IS NOT NULL;
