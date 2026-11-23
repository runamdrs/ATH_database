-- Re-creates every foreign key that fix_auto_increment touches.
-- Written before the change; run it only if a step failed partway.

ALTER TABLE `achievement` ADD CONSTRAINT `achievement_ibfk_2` FOREIGN KEY (`SportID`) REFERENCES `sport` (`SportID`) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE `activity` ADD CONSTRAINT `activity_ibfk_2` FOREIGN KEY (`SportID`) REFERENCES `sport` (`SportID`) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE `activity_participant` ADD CONSTRAINT `activity_participant_ibfk_1` FOREIGN KEY (`ActivityID`) REFERENCES `activity` (`ActivityID`) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE `activity_point` ADD CONSTRAINT `activity_point_ibfk_2` FOREIGN KEY (`ActivityID`) REFERENCES `activity` (`ActivityID`) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE `activity_point` ADD CONSTRAINT `activity_point_ibfk_3` FOREIGN KEY (`WorkoutID`) REFERENCES `workout` (`WorkoutID`) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE `athlete_sport` ADD CONSTRAINT `athlete_sport_ibfk_2` FOREIGN KEY (`SportID`) REFERENCES `sport` (`SportID`) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE `comment` ADD CONSTRAINT `comment_ibfk_2` FOREIGN KEY (`PostID`) REFERENCES `post` (`PostID`) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE `recruiter_athlete` ADD CONSTRAINT `recruiter_athlete_ibfk_1` FOREIGN KEY (`RecruiterID`) REFERENCES `recruiter` (`RecruiterID`) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE `reward` ADD CONSTRAINT `reward_ibfk_1` FOREIGN KEY (`SponsorID`) REFERENCES `sponsor` (`SponsorID`) ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE `reward_redemption` ADD CONSTRAINT `reward_redemption_ibfk_2` FOREIGN KEY (`RewardID`) REFERENCES `reward` (`RewardID`) ON DELETE NO ACTION ON UPDATE NO ACTION;
