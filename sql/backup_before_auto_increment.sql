-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: ath
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `ath`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `ath` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `ath`;

--
-- Table structure for table `achievement`
--

DROP TABLE IF EXISTS `achievement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `achievement` (
  `AchievementID` int NOT NULL AUTO_INCREMENT,
  `AthleteID` int NOT NULL,
  `SportID` int DEFAULT NULL,
  `Title` varchar(100) NOT NULL,
  `Description` text,
  `DateEarned` date DEFAULT NULL,
  PRIMARY KEY (`AchievementID`),
  KEY `AthleteID` (`AthleteID`),
  KEY `SportID` (`SportID`),
  CONSTRAINT `achievement_ibfk_1` FOREIGN KEY (`AthleteID`) REFERENCES `athlete` (`AthleteID`),
  CONSTRAINT `achievement_ibfk_2` FOREIGN KEY (`SportID`) REFERENCES `sport` (`SportID`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `achievement`
--

LOCK TABLES `achievement` WRITE;
/*!40000 ALTER TABLE `achievement` DISABLE KEYS */;
INSERT INTO `achievement` VALUES (1,1,1,'Tournament Top 10','Finished in the top ten at a golf tournament.','2026-10-10'),(2,2,2,'Team MVP','Recognized for outstanding basketball performance.','2026-09-25'),(3,3,3,'Scoring Leader','Led the team in goals during the season.','2026-10-05'),(4,4,4,'Personal Best','Achieved a personal best in the 100-meter freestyle.','2026-10-12'),(5,5,5,'Sprint Record','Set a new personal record in the 100-meter sprint.','2026-10-15'),(6,6,6,'Conference Doubles Finalist','Reached the doubles final at the regional collegiate tournament.','2026-09-19'),(7,6,9,'Clean and Jerk Personal Best','Lifted a personal best of 72 kg in the clean and jerk.','2026-11-04'),(8,7,2,'All-Conference Guard','Named to the all-conference team as a starting guard.','2026-03-14'),(9,7,5,'Indoor 200m Season Best','Recorded a season best of 22.4 seconds in the indoor 200m.','2026-02-07'),(10,8,7,'Team Captain','Selected as team captain for the volleyball season.','2026-08-22'),(11,9,4,'First 1500m Finish','Completed a 1500m freestyle event for the first time.','2026-10-11'),(12,10,3,'Golden Boot','Finished the season as the leading scorer in the league.','2026-05-30'),(13,10,8,'5K Personal Record','Set a personal record of 18:42 in a 5K road race.','2026-09-27'),(14,11,2,'Most Improved Player','Recognized as the most improved player on the roster.','2026-04-18'),(15,12,6,'Beginner Clinic Graduate','Completed the eight week introductory tennis clinic.','2026-10-17'),(16,13,5,'Regional 400m Champion','Won the regional championship in the 400m.','2026-05-09'),(17,13,9,'Back Squat Milestone','Reached a 180 kg back squat in training.','2026-10-02'),(18,14,7,'Digs Leader','Led the team in defensive digs for the season.','2026-06-06'),(19,15,8,'Trail Marathon Finisher','Finished a 42 km mountain trail marathon.','2026-10-03'),(20,16,3,'Defensive Player of the Year','Named defensive player of the year in the conference.','2026-06-20'),(21,16,6,'Club Ladder Champion','Finished first in the club tennis ladder.','2026-09-12'),(22,17,1,'First Tournament Entry','Completed a first competitive golf tournament.','2026-10-23'),(23,18,10,'Century Ride','Completed a 100 mile road cycling event.','2026-08-15'),(24,19,5,'State Sprint Champion','Won the state championship in the 100m sprint.','2026-05-23'),(25,19,2,'Dual Sport Letter','Earned varsity letters in both track and basketball.','2026-06-01');
/*!40000 ALTER TABLE `achievement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `activity`
--

DROP TABLE IF EXISTS `activity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity` (
  `ActivityID` int NOT NULL,
  `AthleteID` int NOT NULL,
  `SportID` int NOT NULL,
  `Type` varchar(50) NOT NULL,
  `Date` date NOT NULL,
  `Time` time NOT NULL,
  `Duration` int NOT NULL,
  `Location` varchar(150) DEFAULT NULL,
  `MaxParticipants` int DEFAULT NULL,
  PRIMARY KEY (`ActivityID`),
  KEY `AthleteID` (`AthleteID`),
  KEY `SportID` (`SportID`),
  CONSTRAINT `activity_ibfk_1` FOREIGN KEY (`AthleteID`) REFERENCES `athlete` (`AthleteID`),
  CONSTRAINT `activity_ibfk_2` FOREIGN KEY (`SportID`) REFERENCES `sport` (`SportID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity`
--

LOCK TABLES `activity` WRITE;
/*!40000 ALTER TABLE `activity` DISABLE KEYS */;
INSERT INTO `activity` VALUES (1,1,1,'Golf Practice','2026-10-20','09:00:00',90,'Campus Golf Course',10),(2,2,2,'Basketball Training','2026-10-21','15:00:00',60,'University Gym',15),(3,3,3,'Soccer Practice','2026-10-21','16:30:00',75,'Soccer Field',22),(4,4,4,'Swimming Session','2026-10-22','08:00:00',45,'Campus Pool',12),(5,5,5,'Track Workout','2026-10-22','17:00:00',60,'University Track',20),(6,6,6,'Tennis Doubles Session','2026-10-24','10:00:00',90,'Hickory Tennis Center',4),(7,7,2,'Pickup Basketball','2026-10-25','18:00:00',120,'Downtown Rec Center',10),(8,8,7,'Volleyball Scrimmage','2026-10-26','14:00:00',90,'Raleigh Sports Complex',12),(9,10,3,'Soccer Small-Sided Game','2026-10-27','17:00:00',60,'Atlanta Midtown Field',14),(10,13,5,'Interval Track Session','2026-10-28','06:30:00',75,'Greenville Track',8),(11,15,8,'Long Trail Run','2026-10-29','07:00:00',110,'Blue Ridge Trailhead',12),(12,18,10,'Group Road Ride','2026-10-30','08:00:00',150,'Nashville Greenway',10),(13,19,5,'Sprint Mechanics Clinic','2026-10-31','16:00:00',90,'Atlanta Track Club',16),(14,1,1,'Short Game Practice','2026-11-01','09:30:00',60,'Campus Golf Course',6),(15,16,3,'Soccer Conditioning','2026-11-02','17:30:00',70,'Charlotte Soccer Park',18),(16,9,4,'Open Water Technique','2026-11-03','07:30:00',50,'Durham Aquatic Center',8),(17,11,2,'Shooting Drills','2026-11-03','19:00:00',60,'Savannah Community Gym',8),(18,6,9,'Olympic Lift Technique','2026-11-04','17:00:00',80,'Hickory Strength Lab',6),(19,1,6,'Tennis Ladder Match','2026-11-07','10:00:00',90,'Hickory Tennis Center',4),(20,7,2,'Pickup Basketball','2026-11-08','18:00:00',120,'Downtown Rec Center',10),(21,13,9,'Max Strength Session','2026-11-09','16:00:00',75,'Greenville Strength Lab',6),(22,15,8,'Tempo Trail Run','2026-11-10','07:00:00',80,'Blue Ridge Trailhead',12),(23,10,3,'Soccer Skills Clinic','2026-11-12','17:00:00',90,'Atlanta Midtown Field',20),(24,8,7,'Volleyball Open Gym','2026-11-14','13:00:00',120,'Raleigh Sports Complex',12),(25,18,10,'Endurance Ride','2026-11-16','08:00:00',180,'Nashville Greenway',10),(26,19,5,'Relay Handoff Practice','2026-11-18','16:30:00',60,'Atlanta Track Club',16),(27,3,3,'Soccer Friendly Match','2026-11-21','15:00:00',90,'Atlanta Midtown Field',22),(28,5,5,'Track Recovery Jog','2026-11-24','17:00:00',45,'University Track',20),(29,2,2,'Basketball Skills Session','2026-12-02','15:00:00',60,'University Gym',15),(30,6,6,'Winter Tennis Clinic','2026-12-10','11:00:00',120,'Hickory Tennis Center',8);
/*!40000 ALTER TABLE `activity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `activity_participant`
--

DROP TABLE IF EXISTS `activity_participant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity_participant` (
  `ActivityID` int NOT NULL,
  `AthleteID` int NOT NULL,
  `JoinDate` date NOT NULL,
  `ParticipationStatus` varchar(20) NOT NULL,
  PRIMARY KEY (`ActivityID`,`AthleteID`),
  KEY `AthleteID` (`AthleteID`),
  CONSTRAINT `activity_participant_ibfk_1` FOREIGN KEY (`ActivityID`) REFERENCES `activity` (`ActivityID`),
  CONSTRAINT `activity_participant_ibfk_2` FOREIGN KEY (`AthleteID`) REFERENCES `athlete` (`AthleteID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity_participant`
--

LOCK TABLES `activity_participant` WRITE;
/*!40000 ALTER TABLE `activity_participant` DISABLE KEYS */;
INSERT INTO `activity_participant` VALUES (1,1,'2026-10-18','Registered'),(1,12,'2026-10-18','Attended'),(1,17,'2026-10-13','Attended'),(2,2,'2026-10-19','Attended'),(2,7,'2026-10-17','Attended'),(2,11,'2026-10-09','Cancelled'),(2,15,'2026-10-11','Attended'),(2,19,'2026-10-17','Attended'),(3,3,'2026-10-19','Attended'),(3,10,'2026-10-12','Attended'),(3,14,'2026-10-16','Attended'),(3,16,'2026-10-10','Attended'),(4,4,'2026-10-20','Registered'),(4,9,'2026-10-15','Attended'),(4,18,'2026-10-15','Attended'),(5,2,'2026-10-19','Attended'),(5,5,'2026-10-20','Attended'),(5,13,'2026-10-17','Attended'),(5,19,'2026-10-14','Attended'),(6,1,'2026-10-13','Attended'),(6,6,'2026-10-14','Attended'),(6,8,'2026-10-17','Attended'),(7,2,'2026-10-22','Attended'),(7,7,'2026-10-14','Cancelled'),(7,11,'2026-10-15','Attended'),(7,15,'2026-10-13','Attended'),(7,17,'2026-10-15','Attended'),(7,19,'2026-10-13','Attended'),(8,3,'2026-10-15','Attended'),(8,8,'2026-10-19','Attended'),(8,14,'2026-10-23','Attended'),(8,16,'2026-10-18','Attended'),(9,3,'2026-10-24','Attended'),(9,10,'2026-10-21','Attended'),(9,16,'2026-10-18','Attended'),(9,19,'2026-10-25','Attended'),(10,2,'2026-10-23','Attended'),(10,5,'2026-10-16','No Show'),(10,13,'2026-10-22','Cancelled'),(10,19,'2026-10-23','Attended'),(11,5,'2026-10-25','Attended'),(11,9,'2026-10-19','Attended'),(11,15,'2026-10-26','Attended'),(11,18,'2026-10-21','Attended'),(12,4,'2026-10-28','Attended'),(12,14,'2026-10-21','Attended'),(12,18,'2026-10-20','Attended'),(13,2,'2026-10-23','No Show'),(13,5,'2026-10-26','Attended'),(13,13,'2026-10-28','Attended'),(13,15,'2026-10-28','No Show'),(13,19,'2026-10-21','No Show'),(14,1,'2026-10-21','Attended'),(14,17,'2026-10-21','Attended'),(15,3,'2026-10-22','Attended'),(15,10,'2026-10-30','Attended'),(15,11,'2026-10-30','Attended'),(15,14,'2026-10-28','Attended'),(15,16,'2026-10-29','Attended'),(16,4,'2026-10-28','Attended'),(16,9,'2026-10-25','Attended'),(16,18,'2026-10-22','Attended'),(17,2,'2026-10-27','Attended'),(17,7,'2026-11-01','Attended'),(17,11,'2026-10-28','Attended'),(18,6,'2026-10-30','Attended'),(18,12,'2026-10-29','Attended'),(18,13,'2026-11-02','Attended'),(19,1,'2026-10-28','Registered'),(19,6,'2026-11-04','Registered'),(19,8,'2026-10-29','Registered'),(19,12,'2026-10-27','Registered'),(20,2,'2026-11-05','Registered'),(20,7,'2026-11-04','Registered'),(20,11,'2026-10-28','Registered'),(20,19,'2026-10-27','Registered'),(21,6,'2026-11-04','Registered'),(21,9,'2026-11-04','Registered'),(21,13,'2026-11-03','Registered'),(22,5,'2026-11-07','Registered'),(22,9,'2026-10-31','Registered'),(22,12,'2026-11-08','Registered'),(22,15,'2026-11-05','Registered'),(22,18,'2026-10-31','Registered'),(23,3,'2026-11-02','Registered'),(23,10,'2026-11-10','Registered'),(23,11,'2026-11-07','Registered'),(23,14,'2026-10-31','Registered'),(23,16,'2026-11-07','Registered'),(23,19,'2026-11-06','Registered'),(24,3,'2026-11-04','Registered'),(24,8,'2026-11-06','Registered'),(24,14,'2026-11-08','Registered'),(24,16,'2026-11-10','Registered'),(25,4,'2026-11-10','Registered'),(25,9,'2026-11-05','Registered'),(25,14,'2026-11-08','Registered'),(25,18,'2026-11-04','Registered'),(26,2,'2026-11-06','Registered'),(26,5,'2026-11-06','Registered'),(26,13,'2026-11-12','Registered'),(26,19,'2026-11-09','Registered'),(27,3,'2026-11-14','Registered'),(27,10,'2026-11-16','Registered'),(27,16,'2026-11-13','Registered'),(29,2,'2026-11-30','Registered'),(29,7,'2026-11-23','Registered'),(29,11,'2026-11-25','Registered');
/*!40000 ALTER TABLE `activity_participant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `activity_point`
--

DROP TABLE IF EXISTS `activity_point`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activity_point` (
  `PointTransactionID` int NOT NULL AUTO_INCREMENT,
  `AthleteID` int NOT NULL,
  `ActivityID` int DEFAULT NULL,
  `WorkoutID` int DEFAULT NULL,
  `PointsEarned` int NOT NULL,
  `Reason` varchar(150) NOT NULL,
  `DateEarned` datetime NOT NULL,
  PRIMARY KEY (`PointTransactionID`),
  KEY `AthleteID` (`AthleteID`),
  KEY `ActivityID` (`ActivityID`),
  KEY `WorkoutID` (`WorkoutID`),
  CONSTRAINT `activity_point_ibfk_1` FOREIGN KEY (`AthleteID`) REFERENCES `athlete` (`AthleteID`),
  CONSTRAINT `activity_point_ibfk_2` FOREIGN KEY (`ActivityID`) REFERENCES `activity` (`ActivityID`),
  CONSTRAINT `activity_point_ibfk_3` FOREIGN KEY (`WorkoutID`) REFERENCES `workout` (`WorkoutID`)
) ENGINE=InnoDB AUTO_INCREMENT=135 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity_point`
--

LOCK TABLES `activity_point` WRITE;
/*!40000 ALTER TABLE `activity_point` DISABLE KEYS */;
INSERT INTO `activity_point` VALUES (1,1,1,1,100,'Golf practice and strength training','2026-10-20 11:00:00'),(2,2,2,2,80,'Basketball training and conditioning','2026-10-21 16:00:00'),(3,3,3,3,100,'Soccer practice and strength training','2026-10-21 18:00:00'),(4,4,4,4,50,'Swimming session participation','2026-10-22 09:00:00'),(5,5,5,5,90,'Track practice and speed training','2026-10-22 18:00:00'),(6,17,1,NULL,45,'Attended group activity: Golf Practice','2026-10-20 09:00:00'),(7,12,1,NULL,45,'Attended group activity: Golf Practice','2026-10-20 09:00:00'),(8,7,2,NULL,30,'Attended group activity: Basketball Training','2026-10-21 15:00:00'),(9,19,2,NULL,30,'Attended group activity: Basketball Training','2026-10-21 15:00:00'),(10,15,2,NULL,30,'Attended group activity: Basketball Training','2026-10-21 15:00:00'),(11,10,3,NULL,38,'Attended group activity: Soccer Practice','2026-10-21 16:30:00'),(12,16,3,NULL,38,'Attended group activity: Soccer Practice','2026-10-21 16:30:00'),(13,14,3,NULL,38,'Attended group activity: Soccer Practice','2026-10-21 16:30:00'),(14,9,4,NULL,23,'Attended group activity: Swimming Session','2026-10-22 08:00:00'),(15,18,4,NULL,23,'Attended group activity: Swimming Session','2026-10-22 08:00:00'),(16,13,5,NULL,30,'Attended group activity: Track Workout','2026-10-22 17:00:00'),(17,19,5,NULL,30,'Attended group activity: Track Workout','2026-10-22 17:00:00'),(18,2,5,NULL,30,'Attended group activity: Track Workout','2026-10-22 17:00:00'),(19,6,6,NULL,45,'Attended group activity: Tennis Doubles Session','2026-10-24 10:00:00'),(20,1,6,NULL,45,'Attended group activity: Tennis Doubles Session','2026-10-24 10:00:00'),(21,8,6,NULL,45,'Attended group activity: Tennis Doubles Session','2026-10-24 10:00:00'),(22,2,7,NULL,60,'Attended group activity: Pickup Basketball','2026-10-25 18:00:00'),(23,11,7,NULL,60,'Attended group activity: Pickup Basketball','2026-10-25 18:00:00'),(24,19,7,NULL,60,'Attended group activity: Pickup Basketball','2026-10-25 18:00:00'),(25,15,7,NULL,60,'Attended group activity: Pickup Basketball','2026-10-25 18:00:00'),(26,17,7,NULL,60,'Attended group activity: Pickup Basketball','2026-10-25 18:00:00'),(27,8,8,NULL,45,'Attended group activity: Volleyball Scrimmage','2026-10-26 14:00:00'),(28,14,8,NULL,45,'Attended group activity: Volleyball Scrimmage','2026-10-26 14:00:00'),(29,3,8,NULL,45,'Attended group activity: Volleyball Scrimmage','2026-10-26 14:00:00'),(30,16,8,NULL,45,'Attended group activity: Volleyball Scrimmage','2026-10-26 14:00:00'),(31,10,9,NULL,30,'Attended group activity: Soccer Small-Sided Game','2026-10-27 17:00:00'),(32,3,9,NULL,30,'Attended group activity: Soccer Small-Sided Game','2026-10-27 17:00:00'),(33,16,9,NULL,30,'Attended group activity: Soccer Small-Sided Game','2026-10-27 17:00:00'),(34,19,9,NULL,30,'Attended group activity: Soccer Small-Sided Game','2026-10-27 17:00:00'),(35,19,10,NULL,38,'Attended group activity: Interval Track Session','2026-10-28 06:30:00'),(36,2,10,NULL,38,'Attended group activity: Interval Track Session','2026-10-28 06:30:00'),(37,15,11,NULL,55,'Attended group activity: Long Trail Run','2026-10-29 07:00:00'),(38,5,11,NULL,55,'Attended group activity: Long Trail Run','2026-10-29 07:00:00'),(39,9,11,NULL,55,'Attended group activity: Long Trail Run','2026-10-29 07:00:00'),(40,18,11,NULL,55,'Attended group activity: Long Trail Run','2026-10-29 07:00:00'),(41,18,12,NULL,75,'Attended group activity: Group Road Ride','2026-10-30 08:00:00'),(42,4,12,NULL,75,'Attended group activity: Group Road Ride','2026-10-30 08:00:00'),(43,14,12,NULL,75,'Attended group activity: Group Road Ride','2026-10-30 08:00:00'),(44,13,13,NULL,45,'Attended group activity: Sprint Mechanics Clinic','2026-10-31 16:00:00'),(45,5,13,NULL,45,'Attended group activity: Sprint Mechanics Clinic','2026-10-31 16:00:00'),(46,1,14,NULL,30,'Attended group activity: Short Game Practice','2026-11-01 09:30:00'),(47,17,14,NULL,30,'Attended group activity: Short Game Practice','2026-11-01 09:30:00'),(48,16,15,NULL,35,'Attended group activity: Soccer Conditioning','2026-11-02 17:30:00'),(49,10,15,NULL,35,'Attended group activity: Soccer Conditioning','2026-11-02 17:30:00'),(50,3,15,NULL,35,'Attended group activity: Soccer Conditioning','2026-11-02 17:30:00'),(51,14,15,NULL,35,'Attended group activity: Soccer Conditioning','2026-11-02 17:30:00'),(52,11,15,NULL,35,'Attended group activity: Soccer Conditioning','2026-11-02 17:30:00'),(53,9,16,NULL,25,'Attended group activity: Open Water Technique','2026-11-03 07:30:00'),(54,4,16,NULL,25,'Attended group activity: Open Water Technique','2026-11-03 07:30:00'),(55,18,16,NULL,25,'Attended group activity: Open Water Technique','2026-11-03 07:30:00'),(56,11,17,NULL,30,'Attended group activity: Shooting Drills','2026-11-03 19:00:00'),(57,7,17,NULL,30,'Attended group activity: Shooting Drills','2026-11-03 19:00:00'),(58,2,17,NULL,30,'Attended group activity: Shooting Drills','2026-11-03 19:00:00'),(59,6,18,NULL,40,'Attended group activity: Olympic Lift Technique','2026-11-04 17:00:00'),(60,13,18,NULL,40,'Attended group activity: Olympic Lift Technique','2026-11-04 17:00:00'),(61,12,18,NULL,40,'Attended group activity: Olympic Lift Technique','2026-11-04 17:00:00'),(62,1,NULL,7,30,'Completed planned workout: Technique Session','2026-09-05 20:00:00'),(63,1,NULL,8,38,'Completed planned workout: Mobility and Recovery','2026-10-07 20:00:00'),(64,1,NULL,9,33,'Completed planned workout: Endurance Training','2026-09-27 20:00:00'),(65,1,NULL,10,33,'Completed planned workout: Strength Training','2026-10-19 20:00:00'),(66,2,NULL,14,28,'Completed planned workout: Mobility and Recovery','2026-10-07 20:00:00'),(67,3,NULL,16,48,'Completed planned workout: Speed Training','2026-11-01 20:00:00'),(68,3,NULL,17,48,'Completed planned workout: Technique Session','2026-10-13 20:00:00'),(69,3,NULL,18,28,'Completed planned workout: Strength Training','2026-10-23 20:00:00'),(70,3,NULL,19,33,'Completed planned workout: Interval Training','2026-09-15 20:00:00'),(71,3,NULL,20,38,'Completed planned workout: Strength Training','2026-09-23 20:00:00'),(72,4,NULL,21,43,'Completed planned workout: Mobility and Recovery','2026-09-25 20:00:00'),(73,4,NULL,22,30,'Completed planned workout: Mobility and Recovery','2026-10-20 20:00:00'),(74,5,NULL,24,45,'Completed planned workout: Conditioning','2026-09-24 20:00:00'),(75,5,NULL,25,28,'Completed planned workout: Core Stability','2026-09-13 20:00:00'),(76,5,NULL,26,30,'Completed planned workout: Speed Training','2026-09-09 20:00:00'),(77,6,NULL,28,33,'Completed planned workout: Conditioning','2026-09-05 20:00:00'),(78,6,NULL,29,43,'Completed planned workout: Endurance Training','2026-11-04 20:00:00'),(79,6,NULL,30,40,'Completed planned workout: Interval Training','2026-10-31 20:00:00'),(80,6,NULL,31,48,'Completed planned workout: Speed Training','2026-10-14 20:00:00'),(81,6,NULL,32,48,'Completed planned workout: Mobility and Recovery','2026-09-23 20:00:00'),(82,6,NULL,34,28,'Completed planned workout: Speed Training','2026-09-20 20:00:00'),(83,7,NULL,37,40,'Completed planned workout: Conditioning','2026-10-14 20:00:00'),(84,7,NULL,38,33,'Completed planned workout: Technique Session','2026-10-19 20:00:00'),(85,7,NULL,39,45,'Completed planned workout: Conditioning','2026-09-08 20:00:00'),(86,7,NULL,40,33,'Completed planned workout: Conditioning','2026-10-26 20:00:00'),(87,8,NULL,42,43,'Completed planned workout: Conditioning','2026-09-08 20:00:00'),(88,8,NULL,43,28,'Completed planned workout: Endurance Training','2026-09-07 20:00:00'),(89,8,NULL,44,40,'Completed planned workout: Conditioning','2026-11-02 20:00:00'),(90,9,NULL,46,30,'Completed planned workout: Endurance Training','2026-10-09 20:00:00'),(91,9,NULL,47,28,'Completed planned workout: Endurance Training','2026-09-15 20:00:00'),(92,10,NULL,49,33,'Completed planned workout: Technique Session','2026-10-27 20:00:00'),(93,10,NULL,50,28,'Completed planned workout: Core Stability','2026-09-18 20:00:00'),(94,10,NULL,51,48,'Completed planned workout: Interval Training','2026-10-02 20:00:00'),(95,10,NULL,52,40,'Completed planned workout: Technique Session','2026-10-29 20:00:00'),(96,10,NULL,53,45,'Completed planned workout: Endurance Training','2026-10-22 20:00:00'),(97,10,NULL,54,35,'Completed planned workout: Endurance Training','2026-10-15 20:00:00'),(98,11,NULL,56,48,'Completed planned workout: Speed Training','2026-09-12 20:00:00'),(99,11,NULL,57,43,'Completed planned workout: Core Stability','2026-10-18 20:00:00'),(100,11,NULL,58,28,'Completed planned workout: Core Stability','2026-11-02 20:00:00'),(101,12,NULL,59,35,'Completed planned workout: Strength Training','2026-10-20 20:00:00'),(102,12,NULL,60,43,'Completed planned workout: Conditioning','2026-09-19 20:00:00'),(103,13,NULL,62,30,'Completed planned workout: Technique Session','2026-09-12 20:00:00'),(104,13,NULL,63,43,'Completed planned workout: Mobility and Recovery','2026-10-19 20:00:00'),(105,13,NULL,64,45,'Completed planned workout: Mobility and Recovery','2026-10-17 20:00:00'),(106,13,NULL,66,30,'Completed planned workout: Strength Training','2026-09-27 20:00:00'),(107,13,NULL,67,38,'Completed planned workout: Strength Training','2026-09-24 20:00:00'),(108,13,NULL,68,48,'Completed planned workout: Endurance Training','2026-10-16 20:00:00'),(109,13,NULL,69,45,'Completed planned workout: Mobility and Recovery','2026-10-28 20:00:00'),(110,14,NULL,71,33,'Completed planned workout: Technique Session','2026-11-01 20:00:00'),(111,14,NULL,72,30,'Completed planned workout: Interval Training','2026-09-11 20:00:00'),(112,14,NULL,73,30,'Completed planned workout: Interval Training','2026-09-07 20:00:00'),(113,14,NULL,74,40,'Completed planned workout: Interval Training','2026-10-06 20:00:00'),(114,15,NULL,76,33,'Completed planned workout: Speed Training','2026-10-28 20:00:00'),(115,15,NULL,77,30,'Completed planned workout: Interval Training','2026-10-29 20:00:00'),(116,15,NULL,78,45,'Completed planned workout: Technique Session','2026-10-27 20:00:00'),(117,15,NULL,79,38,'Completed planned workout: Speed Training','2026-10-07 20:00:00'),(118,15,NULL,80,40,'Completed planned workout: Technique Session','2026-10-23 20:00:00'),(119,16,NULL,82,45,'Completed planned workout: Speed Training','2026-10-04 20:00:00'),(120,16,NULL,83,35,'Completed planned workout: Conditioning','2026-10-04 20:00:00'),(121,16,NULL,85,33,'Completed planned workout: Interval Training','2026-09-29 20:00:00'),(122,16,NULL,86,48,'Completed planned workout: Endurance Training','2026-09-29 20:00:00'),(123,17,NULL,87,43,'Completed planned workout: Technique Session','2026-10-22 20:00:00'),(124,18,NULL,89,38,'Completed planned workout: Mobility and Recovery','2026-10-12 20:00:00'),(125,18,NULL,90,38,'Completed planned workout: Strength Training','2026-10-31 20:00:00'),(126,18,NULL,91,35,'Completed planned workout: Technique Session','2026-10-26 20:00:00'),(127,18,NULL,92,30,'Completed planned workout: Technique Session','2026-09-08 20:00:00'),(128,19,NULL,94,28,'Completed planned workout: Technique Session','2026-10-26 20:00:00'),(129,19,NULL,95,28,'Completed planned workout: Technique Session','2026-09-28 20:00:00'),(130,19,NULL,96,45,'Completed planned workout: Mobility and Recovery','2026-10-03 20:00:00'),(131,19,NULL,97,35,'Completed planned workout: Core Stability','2026-09-18 20:00:00'),(132,19,NULL,99,40,'Completed planned workout: Interval Training','2026-09-14 20:00:00'),(133,19,NULL,101,33,'Completed planned workout: Conditioning','2026-09-16 20:00:00'),(134,19,NULL,102,40,'Completed planned workout: Conditioning','2026-10-12 20:00:00');
/*!40000 ALTER TABLE `activity_point` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `athlete`
--

DROP TABLE IF EXISTS `athlete`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `athlete` (
  `AthleteID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Username` varchar(50) NOT NULL,
  `Email` varchar(150) NOT NULL,
  `Location` varchar(100) DEFAULT NULL,
  `SkillLevel` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`AthleteID`),
  UNIQUE KEY `Username` (`Username`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `athlete`
--

LOCK TABLES `athlete` WRITE;
/*!40000 ALTER TABLE `athlete` DISABLE KEYS */;
INSERT INTO `athlete` VALUES (1,'Alex Morgan','alexmorgan','alex.morgan@example.com','Hickory, NC','Advanced'),(2,'Jordan Lee','jordanlee','jordan.lee@example.com','Charlotte, NC','Intermediate'),(3,'Taylor Smith','taylorsmith','taylor.smith@example.com','Atlanta, GA','Advanced'),(4,'Chris Davis','chrisdavis','chris.davis@example.com','Columbia, SC','Beginner'),(5,'Sam Wilson','samwilson','sam.wilson@example.com','Greenville, SC','Intermediate'),(6,'Maya Patel','mayapatel','maya.patel@example.com','Hickory, NC','Advanced'),(7,'Ethan Brooks','ethanbrooks','ethan.brooks@example.com','Charlotte, NC','Advanced'),(8,'Olivia Reed','oliviareed','olivia.reed@example.com','Raleigh, NC','Intermediate'),(9,'Lucas Hayes','lucashayes','lucas.hayes@example.com','Durham, NC','Beginner'),(10,'Sofia Ramirez','sofiaramirez','sofia.ramirez@example.com','Atlanta, GA','Advanced'),(11,'Noah Bennett','noahbennett','noah.bennett@example.com','Savannah, GA','Intermediate'),(12,'Ava Collins','avacollins','ava.collins@example.com','Hickory, NC','Beginner'),(13,'Liam Foster','liamfoster','liam.foster@example.com','Greenville, SC','Advanced'),(14,'Emma Clarke','emmaclarke','emma.clarke@example.com','Columbia, SC','Intermediate'),(15,'Mason Price','masonprice','mason.price@example.com','Asheville, NC','Intermediate'),(16,'Isabella Nunez','isabellanunez','isabella.nunez@example.com','Charlotte, NC','Advanced'),(17,'Jacob Turner','jacobturner','jacob.turner@example.com','Knoxville, TN','Beginner'),(18,'Harper Quinn','harperquinn','harper.quinn@example.com','Nashville, TN','Intermediate'),(19,'Daniel Okafor','danielokafor','daniel.okafor@example.com','Atlanta, GA','Advanced'),(20,'Riley Nguyen','rileynguyen','riley.nguyen@example.com','Hickory, NC','Beginner');
/*!40000 ALTER TABLE `athlete` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `athlete_portfolio`
--

DROP TABLE IF EXISTS `athlete_portfolio`;
/*!50001 DROP VIEW IF EXISTS `athlete_portfolio`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `athlete_portfolio` AS SELECT 
 1 AS `AthleteID`,
 1 AS `Name`,
 1 AS `Username`,
 1 AS `Location`,
 1 AS `SkillLevel`,
 1 AS `SportCount`,
 1 AS `AchievementCount`,
 1 AS `CompletedWorkouts`,
 1 AS `TotalTrainingMinutes`,
 1 AS `ActivitiesAttended`,
 1 AS `TotalActivityPoints`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `athlete_sport`
--

DROP TABLE IF EXISTS `athlete_sport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `athlete_sport` (
  `AthleteID` int NOT NULL,
  `SportID` int NOT NULL,
  PRIMARY KEY (`AthleteID`,`SportID`),
  KEY `SportID` (`SportID`),
  CONSTRAINT `athlete_sport_ibfk_1` FOREIGN KEY (`AthleteID`) REFERENCES `athlete` (`AthleteID`),
  CONSTRAINT `athlete_sport_ibfk_2` FOREIGN KEY (`SportID`) REFERENCES `sport` (`SportID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `athlete_sport`
--

LOCK TABLES `athlete_sport` WRITE;
/*!40000 ALTER TABLE `athlete_sport` DISABLE KEYS */;
INSERT INTO `athlete_sport` VALUES (1,1),(17,1),(2,2),(7,2),(11,2),(19,2),(3,3),(10,3),(16,3),(4,4),(9,4),(18,4),(2,5),(5,5),(7,5),(13,5),(19,5),(1,6),(6,6),(8,6),(12,6),(16,6),(20,6),(3,7),(8,7),(14,7),(5,8),(10,8),(15,8),(6,9),(13,9),(4,10),(14,10),(18,10);
/*!40000 ALTER TABLE `athlete_sport` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comment`
--

DROP TABLE IF EXISTS `comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comment` (
  `CommentID` int NOT NULL AUTO_INCREMENT,
  `AthleteID` int NOT NULL,
  `PostID` int NOT NULL,
  `Text` text NOT NULL,
  `DateCreated` datetime NOT NULL,
  PRIMARY KEY (`CommentID`),
  KEY `AthleteID` (`AthleteID`),
  KEY `PostID` (`PostID`),
  CONSTRAINT `comment_ibfk_1` FOREIGN KEY (`AthleteID`) REFERENCES `athlete` (`AthleteID`),
  CONSTRAINT `comment_ibfk_2` FOREIGN KEY (`PostID`) REFERENCES `post` (`PostID`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comment`
--

LOCK TABLES `comment` WRITE;
/*!40000 ALTER TABLE `comment` DISABLE KEYS */;
INSERT INTO `comment` VALUES (1,2,1,'Keep up the good work!','2026-10-20 11:15:00'),(2,3,2,'Agility training makes a big difference.','2026-10-21 16:20:00'),(3,1,3,'Sounds like a great practice.','2026-10-21 18:15:00'),(4,5,4,'Consistency is key. Keep going!','2026-10-22 09:15:00'),(5,4,5,'Nice work! Make sure to recover.','2026-10-22 19:00:00'),(6,1,6,'That serve looked clean in the video.','2026-10-24 13:00:00'),(7,8,6,'Ladder match next week?','2026-10-24 14:20:00'),(8,12,6,'Watching this as a beginner and taking notes.','2026-10-24 18:05:00'),(9,2,7,'Put me down for the next one.','2026-10-25 21:00:00'),(10,11,7,'Good runs tonight.','2026-10-25 21:40:00'),(11,14,8,'Great to see you back out there.','2026-10-26 17:00:00'),(12,16,8,'Shoulder patience pays off.','2026-10-26 19:30:00'),(13,3,9,'Agreed. Nothing else gets the heart rate there.','2026-10-27 19:15:00'),(14,19,10,'Those splits are moving in the right direction.','2026-10-28 09:00:00'),(15,5,10,'Early sessions are the hardest part.','2026-10-28 10:30:00'),(16,2,10,'Respect for the 6:30 start.','2026-10-28 12:00:00'),(17,5,11,'Eleven miles on that terrain is no joke.','2026-10-29 10:15:00'),(18,9,11,'Which trailhead did you start from?','2026-10-29 12:00:00'),(19,4,12,'Ninety miles is a serious day.','2026-10-30 12:30:00'),(20,14,12,'Joining the next group ride.','2026-10-30 13:45:00'),(21,13,13,'The first three steps change everything.','2026-10-31 19:00:00'),(22,5,13,'Was the clinic open to non-members?','2026-10-31 20:15:00'),(23,2,13,'Saving this for the spring season.','2026-10-31 21:00:00'),(24,17,14,'Fifty up-and-downs is dedication.','2026-11-01 12:10:00'),(25,12,14,'This is why your short game is good.','2026-11-01 13:00:00'),(26,10,15,'Conditioning block is the worst part and the best part.','2026-11-02 20:00:00'),(27,3,15,'See you at the friendly.','2026-11-02 20:45:00'),(28,18,16,'Catch takes months. Keep filming it.','2026-11-03 10:00:00'),(29,4,16,'Needed to read this today.','2026-11-03 11:30:00'),(30,7,17,'Charting shots changed my practice completely.','2026-11-03 21:00:00'),(31,19,17,'Corner three comes with reps.','2026-11-03 21:45:00'),(32,13,18,'Congratulations on the personal best.','2026-11-04 19:00:00'),(33,12,18,'That is a serious lift.','2026-11-04 19:30:00'),(34,9,18,'Technique looked solid.','2026-11-04 20:00:00'),(35,15,19,'Three hundred points is a real milestone.','2026-11-04 21:20:00'),(36,6,19,'Consistency over intensity.','2026-11-04 21:50:00'),(37,5,20,'Count me in for the relay practice.','2026-11-04 22:30:00'),(38,13,20,'I will be there.','2026-11-04 22:45:00'),(39,2,20,'Is it open to sprinters outside the club?','2026-11-05 07:10:00'),(40,16,21,'Welcome back to the pitch.','2026-10-26 14:00:00'),(41,10,21,'Touch always comes back faster than fitness.','2026-10-26 15:30:00'),(42,13,22,'Recovery weeks are underrated.','2026-10-27 10:00:00'),(43,18,23,'Cross training is good for you.','2026-10-28 21:00:00'),(44,16,24,'Congratulations. The portfolio works.','2026-10-30 18:00:00'),(45,3,24,'Which program reached out?','2026-10-30 18:45:00'),(46,19,24,'Well deserved.','2026-10-30 20:00:00'),(47,7,25,'Lateral quickness wins games.','2026-10-31 17:30:00'),(48,10,26,'Sharing early is the right call.','2026-11-01 15:00:00'),(49,18,27,'The pool gets easier. Promise.','2026-11-02 11:00:00'),(50,9,27,'Three swims in is the hardest part.','2026-11-02 12:30:00'),(51,1,28,'Clinics are the best way to start.','2026-11-02 16:15:00'),(52,8,28,'Glad you tried it.','2026-11-02 17:00:00'),(53,15,29,'Thirty days is a real streak.','2026-11-03 22:30:00'),(54,2,29,'Setting that as my own target.','2026-11-04 08:00:00'),(55,5,30,'I am in for Tuesday.','2026-11-04 20:00:00');
/*!40000 ALTER TABLE `comment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `post`
--

DROP TABLE IF EXISTS `post`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `post` (
  `PostID` int NOT NULL,
  `AthleteID` int NOT NULL,
  `Content` text NOT NULL,
  `DateCreated` datetime NOT NULL,
  `MediaURL` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`PostID`),
  KEY `AthleteID` (`AthleteID`),
  CONSTRAINT `post_ibfk_1` FOREIGN KEY (`AthleteID`) REFERENCES `athlete` (`AthleteID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `post`
--

LOCK TABLES `post` WRITE;
/*!40000 ALTER TABLE `post` DISABLE KEYS */;
INSERT INTO `post` VALUES (1,1,'Finished a productive golf practice session!','2026-10-20 11:00:00',NULL),(2,2,'Working on speed and agility before the next game.','2026-10-21 16:00:00',NULL),(3,3,'Great team effort at soccer practice today.','2026-10-21 18:00:00',NULL),(4,4,'Improving my swimming endurance this week.','2026-10-22 09:00:00',NULL),(5,5,'Track workout completed. Time to recover!','2026-10-22 18:30:00',NULL),(6,6,'Two hours on court this morning. Serve finally feels repeatable.','2026-10-24 12:15:00',NULL),(7,7,'Pickup game ran long again. No complaints.','2026-10-25 20:30:00',NULL),(8,8,'First volleyball scrimmage since the shoulder issue. Slow but pain free.','2026-10-26 16:10:00',NULL),(9,10,'Small-sided games are the best conditioning there is.','2026-10-27 18:45:00',NULL),(10,13,'400m repeats at 6:30 in the morning. Worth it.','2026-10-28 08:05:00','https://media.ath.example/posts/track-repeats.jpg'),(11,15,'Eleven miles on the ridge trail. Legs are done.','2026-10-29 09:40:00',NULL),(12,18,'Ninety miles with the group ride. New distance record for me.','2026-10-30 11:20:00',NULL),(13,19,'Sprint clinic today. Coach rebuilt my first three steps.','2026-10-31 18:00:00',NULL),(14,1,'Short game practice. Fifty up-and-downs before I let myself leave.','2026-11-01 11:00:00',NULL),(15,16,'Conditioning block done. Four weeks until the first friendly.','2026-11-02 19:10:00',NULL),(16,9,'Swim technique session. Still fighting my catch but it is improving.','2026-11-03 09:00:00',NULL),(17,11,'Two hundred shots, charted. Corner three is the weak spot.','2026-11-03 20:30:00',NULL),(18,6,'Clean and jerk at a new personal best tonight.','2026-11-04 18:40:00','https://media.ath.example/posts/clean-jerk.jpg'),(19,13,'Hit 300 Activity Points this month. Consistency pays.','2026-11-04 21:00:00',NULL),(20,19,'Relay practice posted for the 18th. Open to anyone on the track.','2026-11-04 22:10:00',NULL),(21,3,'Back on the pitch after fall break. Touch comes back fast.','2026-10-26 13:00:00',NULL),(22,5,'Easy recovery week. Learning that rest is part of training.','2026-10-27 09:30:00',NULL),(23,14,'Volleyball and cycling in the same week is a strange combination.','2026-10-28 20:00:00',NULL),(24,10,'Recruiter reached out today. Portfolio was worth building.','2026-10-30 17:15:00',NULL),(25,2,'Agility work is paying off. Lateral quickness feels different.','2026-10-31 16:45:00',NULL),(26,16,'Shared my training history with two programs this week.','2026-11-01 14:20:00',NULL),(27,4,'Three swims in and I no longer dread the pool.','2026-11-02 10:05:00',NULL),(28,12,'Beginner tennis clinic was less intimidating than I expected.','2026-11-02 15:30:00',NULL),(29,7,'Logged every workout for thirty straight days.','2026-11-03 22:00:00','https://media.ath.example/posts/streak.png'),(30,15,'Tempo run Tuesday if anyone wants company.','2026-11-04 19:25:00',NULL);
/*!40000 ALTER TABLE `post` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recruiter`
--

DROP TABLE IF EXISTS `recruiter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recruiter` (
  `RecruiterID` int NOT NULL,
  `Name` varchar(100) NOT NULL,
  `Organization` varchar(150) DEFAULT NULL,
  `Email` varchar(150) NOT NULL,
  PRIMARY KEY (`RecruiterID`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recruiter`
--

LOCK TABLES `recruiter` WRITE;
/*!40000 ALTER TABLE `recruiter` DISABLE KEYS */;
INSERT INTO `recruiter` VALUES (1,'Morgan Bennett','Piedmont College Athletics','morgan.bennett@example.com'),(2,'Casey Parker','Carolina Sports Academy','casey.parker@example.com'),(3,'Riley Thompson','Elite Soccer Recruiting','riley.thompson@example.com'),(4,'Jamie Carter','Regional Swim Programs','jamie.carter@example.com'),(5,'Avery Brooks','Track Talent Network','avery.brooks@example.com'),(6,'Dana Whitfield','Appalachian State Track','dana.whitfield@example.com'),(7,'Marcus Hale','Queens University Tennis','marcus.hale@example.com'),(8,'Nina Alvarez','Clemson Soccer Recruiting','nina.alvarez@example.com'),(9,'Trent Boyd','Southeast Basketball Scouts','trent.boyd@example.com'),(10,'Priya Raman','Collegiate Swim Network','priya.raman@example.com');
/*!40000 ALTER TABLE `recruiter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recruiter_athlete`
--

DROP TABLE IF EXISTS `recruiter_athlete`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recruiter_athlete` (
  `RecruiterID` int NOT NULL,
  `AthleteID` int NOT NULL,
  `InterestDate` date NOT NULL,
  `Status` varchar(30) NOT NULL,
  `Notes` text,
  PRIMARY KEY (`RecruiterID`,`AthleteID`),
  KEY `AthleteID` (`AthleteID`),
  CONSTRAINT `recruiter_athlete_ibfk_1` FOREIGN KEY (`RecruiterID`) REFERENCES `recruiter` (`RecruiterID`),
  CONSTRAINT `recruiter_athlete_ibfk_2` FOREIGN KEY (`AthleteID`) REFERENCES `athlete` (`AthleteID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recruiter_athlete`
--

LOCK TABLES `recruiter_athlete` WRITE;
/*!40000 ALTER TABLE `recruiter_athlete` DISABLE KEYS */;
INSERT INTO `recruiter_athlete` VALUES (1,1,'2026-10-01','Interested','Requested recent golf tournament results.'),(1,17,'2026-10-25','Interested','First tournament entry, early stage prospect.'),(2,2,'2026-10-03','Contacted','Discussed basketball experience.'),(2,12,'2026-10-29','Declined','Too early in development for this program.'),(3,3,'2026-10-05','Interested','Reviewed soccer performance statistics.'),(3,16,'2026-11-01','Under Review','Second recruiter reviewing soccer profile.'),(4,4,'2026-10-08','Contacted','Requested swimming times.'),(5,5,'2026-10-10','Under Review','Reviewing track personal records.'),(6,5,'2026-10-02','Interested','Reviewing recent track workout history.'),(6,13,'2026-09-18','Offer Extended','Scholarship offer extended for the 400m.'),(6,15,'2026-10-19','Contacted','Discussed cross country transition.'),(6,19,'2026-09-21','Offer Extended','Top sprint prospect in the region.'),(7,1,'2026-10-26','Interested','Dual sport athlete, golf and tennis.'),(7,6,'2026-09-29','Under Review','Reviewing doubles tournament footage.'),(7,8,'2026-10-21','Contacted','Requested availability for a campus visit.'),(7,16,'2026-10-07','Interested','Strong club ladder results.'),(8,3,'2026-10-11','Contacted','Requested full season highlights.'),(8,10,'2026-09-15','Offer Extended','Leading scorer with excellent portfolio.'),(8,14,'2026-10-28','Interested','Multi sport background noted.'),(8,16,'2026-09-30','Under Review','Reviewing defensive statistics.'),(9,2,'2026-10-30','Interested','Agility metrics are improving quickly.'),(9,7,'2026-09-24','Under Review','All conference guard, reviewing film.'),(9,11,'2026-10-09','Interested','Most improved player award noted.'),(9,19,'2026-10-16','Contacted','Discussed dual sport commitment.'),(10,4,'2026-10-24','Declined','Not a fit for current roster needs.'),(10,9,'2026-10-13','Interested','First distance event completed recently.'),(10,18,'2026-09-26','Contacted','Endurance background from cycling.');
/*!40000 ALTER TABLE `recruiter_athlete` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reward`
--

DROP TABLE IF EXISTS `reward`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reward` (
  `RewardID` int NOT NULL,
  `SponsorID` int NOT NULL,
  `Description` varchar(255) NOT NULL,
  `PointsRequired` int NOT NULL,
  `Availability` int DEFAULT NULL,
  `ExpirationDate` date DEFAULT NULL,
  PRIMARY KEY (`RewardID`),
  KEY `SponsorID` (`SponsorID`),
  CONSTRAINT `reward_ibfk_1` FOREIGN KEY (`SponsorID`) REFERENCES `sponsor` (`SponsorID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reward`
--

LOCK TABLES `reward` WRITE;
/*!40000 ALTER TABLE `reward` DISABLE KEYS */;
INSERT INTO `reward` VALUES (1,1,'Sports equipment gift voucher',500,20,'2027-06-30'),(2,2,'Fitness accessory package',300,15,'2027-05-31'),(3,3,'Reusable sports water bottle',150,50,'2027-04-30'),(4,4,'Athletic apparel discount',250,30,'2027-06-30'),(5,5,'Wellness session voucher',400,10,'2027-03-31'),(6,6,'Trail running shoe voucher',550,10,'2027-07-31'),(7,7,'Electrolyte subscription, three months',300,0,'2027-08-31'),(8,1,'Racquet restring voucher',120,40,'2027-09-30'),(9,2,'Recovery foam roller set',200,25,'2026-10-31'),(10,4,'Team warm up jacket',650,8,'2027-09-30');
/*!40000 ALTER TABLE `reward` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reward_redemption`
--

DROP TABLE IF EXISTS `reward_redemption`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reward_redemption` (
  `RedemptionID` int NOT NULL AUTO_INCREMENT,
  `AthleteID` int NOT NULL,
  `RewardID` int NOT NULL,
  `RedemptionDate` date NOT NULL,
  `Status` varchar(30) NOT NULL,
  PRIMARY KEY (`RedemptionID`),
  KEY `AthleteID` (`AthleteID`),
  KEY `RewardID` (`RewardID`),
  CONSTRAINT `reward_redemption_ibfk_1` FOREIGN KEY (`AthleteID`) REFERENCES `athlete` (`AthleteID`),
  CONSTRAINT `reward_redemption_ibfk_2` FOREIGN KEY (`RewardID`) REFERENCES `reward` (`RewardID`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reward_redemption`
--

LOCK TABLES `reward_redemption` WRITE;
/*!40000 ALTER TABLE `reward_redemption` DISABLE KEYS */;
INSERT INTO `reward_redemption` VALUES (1,1,1,'2026-10-12','Approved'),(2,2,2,'2026-10-13','Pending'),(3,3,3,'2026-10-14','Completed'),(4,4,4,'2026-10-15','Approved'),(5,5,5,'2026-10-16','Pending'),(6,13,8,'2026-09-28','Completed'),(7,19,3,'2026-10-01','Completed'),(8,6,8,'2026-10-04','Approved'),(9,10,2,'2026-10-06','Completed'),(10,15,3,'2026-10-09','Completed'),(11,7,4,'2026-10-11','Approved'),(12,18,3,'2026-10-14','Completed'),(13,16,8,'2026-10-18','Approved'),(14,13,1,'2026-10-20','Pending'),(15,19,6,'2026-10-23','Pending'),(16,3,8,'2026-10-25','Completed'),(17,10,4,'2026-10-27','Approved'),(18,8,3,'2026-10-30','Completed'),(19,6,2,'2026-11-01','Pending'),(20,15,8,'2026-11-03','Approved');
/*!40000 ALTER TABLE `reward_redemption` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sponsor`
--

DROP TABLE IF EXISTS `sponsor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sponsor` (
  `SponsorID` int NOT NULL,
  `Company` varchar(150) NOT NULL,
  `SponsorType` varchar(50) DEFAULT NULL,
  `ContactInformation` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`SponsorID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sponsor`
--

LOCK TABLES `sponsor` WRITE;
/*!40000 ALTER TABLE `sponsor` DISABLE KEYS */;
INSERT INTO `sponsor` VALUES (1,'Peak Performance Sports','Sports Equipment','contact@peakperformance.example'),(2,'Campus Fitness Supply','Fitness Equipment','info@campusfitness.example'),(3,'Hydration Plus','Nutrition and Hydration','support@hydrationplus.example'),(4,'Athlete Gear Co','Sports Apparel','sales@athletegear.example'),(5,'Active Life Wellness','Wellness Services','hello@activelife.example'),(6,'Trailhead Outfitters','Outdoor Equipment','team@trailhead.example'),(7,'Court Side Nutrition','Nutrition','orders@courtside.example');
/*!40000 ALTER TABLE `sponsor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sport`
--

DROP TABLE IF EXISTS `sport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sport` (
  `SportID` int NOT NULL,
  `Name` varchar(50) NOT NULL,
  `Type` varchar(50) NOT NULL,
  PRIMARY KEY (`SportID`),
  UNIQUE KEY `Name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sport`
--

LOCK TABLES `sport` WRITE;
/*!40000 ALTER TABLE `sport` DISABLE KEYS */;
INSERT INTO `sport` VALUES (1,'Golf','Individual'),(2,'Basketball','Team'),(3,'Soccer','Team'),(4,'Swimming','Individual'),(5,'Track and Field','Individual'),(6,'Tennis','Individual'),(7,'Volleyball','Team'),(8,'Cross Country','Individual'),(9,'Weightlifting','Individual'),(10,'Cycling','Individual');
/*!40000 ALTER TABLE `sport` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `workout`
--

DROP TABLE IF EXISTS `workout`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `workout` (
  `WorkoutID` int NOT NULL,
  `AthleteID` int NOT NULL,
  `ScheduledDate` date NOT NULL,
  `WorkoutType` varchar(50) NOT NULL,
  `Duration` int DEFAULT NULL,
  `CompletionStatus` varchar(20) NOT NULL,
  `TrainingNotes` text,
  PRIMARY KEY (`WorkoutID`),
  KEY `AthleteID` (`AthleteID`),
  CONSTRAINT `workout_ibfk_1` FOREIGN KEY (`AthleteID`) REFERENCES `athlete` (`AthleteID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `workout`
--

LOCK TABLES `workout` WRITE;
/*!40000 ALTER TABLE `workout` DISABLE KEYS */;
INSERT INTO `workout` VALUES (1,1,'2026-10-20','Strength Training',45,'Completed','Lower body strength and core stability.'),(2,2,'2026-10-21','Conditioning',40,'Completed','Agility drills and interval running.'),(3,3,'2026-10-21','Strength Training',50,'Completed','Leg strength and explosive power.'),(4,4,'2026-10-22','Endurance Training',35,'Scheduled','Easy aerobic swim session.'),(5,5,'2026-10-22','Speed Training',45,'Completed','Sprint intervals and mobility work.'),(6,1,'2026-11-15','Speed Training',35,'Scheduled','Sprint intervals and acceleration drills.'),(7,1,'2026-09-05','Technique Session',40,'Completed','Skill work and video review.'),(8,1,'2026-10-07','Mobility and Recovery',55,'Completed','Stretching, foam rolling, and light movement.'),(9,1,'2026-09-27','Endurance Training',45,'Completed','Steady aerobic base session.'),(10,1,'2026-10-19','Strength Training',45,'Completed','Lower body strength and core stability.'),(11,2,'2026-11-15','Conditioning',40,'Scheduled','Agility ladder work and interval running.'),(12,2,'2026-10-30','Core Stability',35,'Missed','Anti-rotation and bracing circuit.'),(13,2,'2026-09-26','Conditioning',50,'Missed','Agility ladder work and interval running.'),(14,2,'2026-10-07','Mobility and Recovery',35,'Completed','Stretching, foam rolling, and light movement.'),(15,3,'2026-11-15','Speed Training',65,'Scheduled','Sprint intervals and acceleration drills.'),(16,3,'2026-11-01','Speed Training',75,'Completed','Sprint intervals and acceleration drills.'),(17,3,'2026-10-13','Technique Session',75,'Completed','Skill work and video review.'),(18,3,'2026-10-23','Strength Training',35,'Completed','Lower body strength and core stability.'),(19,3,'2026-09-15','Interval Training',45,'Completed','High intensity intervals with timed rest.'),(20,3,'2026-09-23','Strength Training',55,'Completed','Lower body strength and core stability.'),(21,4,'2026-09-25','Mobility and Recovery',65,'Completed','Stretching, foam rolling, and light movement.'),(22,4,'2026-10-20','Mobility and Recovery',40,'Completed','Stretching, foam rolling, and light movement.'),(23,5,'2026-11-11','Speed Training',55,'Scheduled','Sprint intervals and acceleration drills.'),(24,5,'2026-09-24','Conditioning',70,'Completed','Agility ladder work and interval running.'),(25,5,'2026-09-13','Core Stability',35,'Completed','Anti-rotation and bracing circuit.'),(26,5,'2026-09-09','Speed Training',40,'Completed','Sprint intervals and acceleration drills.'),(27,6,'2026-11-12','Speed Training',35,'Scheduled','Sprint intervals and acceleration drills.'),(28,6,'2026-09-05','Conditioning',45,'Completed','Agility ladder work and interval running.'),(29,6,'2026-11-04','Endurance Training',65,'Completed','Steady aerobic base session.'),(30,6,'2026-10-31','Interval Training',60,'Completed','High intensity intervals with timed rest.'),(31,6,'2026-10-14','Speed Training',75,'Completed','Sprint intervals and acceleration drills.'),(32,6,'2026-09-23','Mobility and Recovery',75,'Completed','Stretching, foam rolling, and light movement.'),(33,6,'2026-10-15','Mobility and Recovery',75,'Missed','Stretching, foam rolling, and light movement.'),(34,6,'2026-09-20','Speed Training',35,'Completed','Sprint intervals and acceleration drills.'),(35,7,'2026-11-21','Core Stability',70,'Scheduled','Anti-rotation and bracing circuit.'),(36,7,'2026-09-09','Conditioning',70,'Missed','Agility ladder work and interval running.'),(37,7,'2026-10-14','Conditioning',60,'Completed','Agility ladder work and interval running.'),(38,7,'2026-10-19','Technique Session',45,'Completed','Skill work and video review.'),(39,7,'2026-09-08','Conditioning',70,'Completed','Agility ladder work and interval running.'),(40,7,'2026-10-26','Conditioning',45,'Completed','Agility ladder work and interval running.'),(41,8,'2026-11-20','Endurance Training',45,'Scheduled','Steady aerobic base session.'),(42,8,'2026-09-08','Conditioning',65,'Completed','Agility ladder work and interval running.'),(43,8,'2026-09-07','Endurance Training',35,'Completed','Steady aerobic base session.'),(44,8,'2026-11-02','Conditioning',60,'Completed','Agility ladder work and interval running.'),(45,9,'2026-11-20','Mobility and Recovery',60,'Scheduled','Stretching, foam rolling, and light movement.'),(46,9,'2026-10-09','Endurance Training',40,'Completed','Steady aerobic base session.'),(47,9,'2026-09-15','Endurance Training',35,'Completed','Steady aerobic base session.'),(48,10,'2026-11-09','Strength Training',45,'Scheduled','Lower body strength and core stability.'),(49,10,'2026-10-27','Technique Session',45,'Completed','Skill work and video review.'),(50,10,'2026-09-18','Core Stability',35,'Completed','Anti-rotation and bracing circuit.'),(51,10,'2026-10-02','Interval Training',75,'Completed','High intensity intervals with timed rest.'),(52,10,'2026-10-29','Technique Session',60,'Completed','Skill work and video review.'),(53,10,'2026-10-22','Endurance Training',70,'Completed','Steady aerobic base session.'),(54,10,'2026-10-15','Endurance Training',50,'Completed','Steady aerobic base session.'),(55,11,'2026-11-13','Mobility and Recovery',75,'Scheduled','Stretching, foam rolling, and light movement.'),(56,11,'2026-09-12','Speed Training',75,'Completed','Sprint intervals and acceleration drills.'),(57,11,'2026-10-18','Core Stability',65,'Completed','Anti-rotation and bracing circuit.'),(58,11,'2026-11-02','Core Stability',35,'Completed','Anti-rotation and bracing circuit.'),(59,12,'2026-10-20','Strength Training',50,'Completed','Lower body strength and core stability.'),(60,12,'2026-09-19','Conditioning',65,'Completed','Agility ladder work and interval running.'),(61,13,'2026-11-13','Endurance Training',65,'Scheduled','Steady aerobic base session.'),(62,13,'2026-09-12','Technique Session',40,'Completed','Skill work and video review.'),(63,13,'2026-10-19','Mobility and Recovery',65,'Completed','Stretching, foam rolling, and light movement.'),(64,13,'2026-10-17','Mobility and Recovery',70,'Completed','Stretching, foam rolling, and light movement.'),(65,13,'2026-09-26','Speed Training',40,'Missed','Sprint intervals and acceleration drills.'),(66,13,'2026-09-27','Strength Training',40,'Completed','Lower body strength and core stability.'),(67,13,'2026-09-24','Strength Training',55,'Completed','Lower body strength and core stability.'),(68,13,'2026-10-16','Endurance Training',75,'Completed','Steady aerobic base session.'),(69,13,'2026-10-28','Mobility and Recovery',70,'Completed','Stretching, foam rolling, and light movement.'),(70,14,'2026-11-19','Conditioning',65,'Scheduled','Agility ladder work and interval running.'),(71,14,'2026-11-01','Technique Session',45,'Completed','Skill work and video review.'),(72,14,'2026-09-11','Interval Training',40,'Completed','High intensity intervals with timed rest.'),(73,14,'2026-09-07','Interval Training',40,'Completed','High intensity intervals with timed rest.'),(74,14,'2026-10-06','Interval Training',60,'Completed','High intensity intervals with timed rest.'),(75,15,'2026-11-13','Core Stability',55,'Scheduled','Anti-rotation and bracing circuit.'),(76,15,'2026-10-28','Speed Training',45,'Completed','Sprint intervals and acceleration drills.'),(77,15,'2026-10-29','Interval Training',40,'Completed','High intensity intervals with timed rest.'),(78,15,'2026-10-27','Technique Session',70,'Completed','Skill work and video review.'),(79,15,'2026-10-07','Speed Training',55,'Completed','Sprint intervals and acceleration drills.'),(80,15,'2026-10-23','Technique Session',60,'Completed','Skill work and video review.'),(81,16,'2026-11-17','Conditioning',65,'Scheduled','Agility ladder work and interval running.'),(82,16,'2026-10-04','Speed Training',70,'Completed','Sprint intervals and acceleration drills.'),(83,16,'2026-10-04','Conditioning',50,'Completed','Agility ladder work and interval running.'),(84,16,'2026-10-28','Speed Training',75,'Missed','Sprint intervals and acceleration drills.'),(85,16,'2026-09-29','Interval Training',45,'Completed','High intensity intervals with timed rest.'),(86,16,'2026-09-29','Endurance Training',75,'Completed','Steady aerobic base session.'),(87,17,'2026-10-22','Technique Session',65,'Completed','Skill work and video review.'),(88,18,'2026-11-17','Conditioning',70,'Scheduled','Agility ladder work and interval running.'),(89,18,'2026-10-12','Mobility and Recovery',55,'Completed','Stretching, foam rolling, and light movement.'),(90,18,'2026-10-31','Strength Training',55,'Completed','Lower body strength and core stability.'),(91,18,'2026-10-26','Technique Session',50,'Completed','Skill work and video review.'),(92,18,'2026-09-08','Technique Session',40,'Completed','Skill work and video review.'),(93,19,'2026-11-19','Strength Training',50,'Scheduled','Lower body strength and core stability.'),(94,19,'2026-10-26','Technique Session',35,'Completed','Skill work and video review.'),(95,19,'2026-09-28','Technique Session',35,'Completed','Skill work and video review.'),(96,19,'2026-10-03','Mobility and Recovery',70,'Completed','Stretching, foam rolling, and light movement.'),(97,19,'2026-09-18','Core Stability',50,'Completed','Anti-rotation and bracing circuit.'),(98,19,'2026-09-25','Technique Session',75,'Missed','Skill work and video review.'),(99,19,'2026-09-14','Interval Training',60,'Completed','High intensity intervals with timed rest.'),(100,19,'2026-09-27','Core Stability',55,'Missed','Anti-rotation and bracing circuit.'),(101,19,'2026-09-16','Conditioning',45,'Completed','Agility ladder work and interval running.'),(102,19,'2026-10-12','Conditioning',60,'Completed','Agility ladder work and interval running.');
/*!40000 ALTER TABLE `workout` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Current Database: `ath`
--

USE `ath`;

--
-- Final view structure for view `athlete_portfolio`
--

/*!50001 DROP VIEW IF EXISTS `athlete_portfolio`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `athlete_portfolio` AS select `a`.`AthleteID` AS `AthleteID`,`a`.`Name` AS `Name`,`a`.`Username` AS `Username`,`a`.`Location` AS `Location`,`a`.`SkillLevel` AS `SkillLevel`,(select count(0) from `athlete_sport` `ats` where (`ats`.`AthleteID` = `a`.`AthleteID`)) AS `SportCount`,(select count(0) from `achievement` `ach` where (`ach`.`AthleteID` = `a`.`AthleteID`)) AS `AchievementCount`,(select count(0) from `workout` `w` where ((`w`.`AthleteID` = `a`.`AthleteID`) and (`w`.`CompletionStatus` = 'Completed'))) AS `CompletedWorkouts`,(select coalesce(sum(`w`.`Duration`),0) from `workout` `w` where ((`w`.`AthleteID` = `a`.`AthleteID`) and (`w`.`CompletionStatus` = 'Completed'))) AS `TotalTrainingMinutes`,(select count(0) from `activity_participant` `ap` where ((`ap`.`AthleteID` = `a`.`AthleteID`) and (`ap`.`ParticipationStatus` = 'Attended'))) AS `ActivitiesAttended`,(select coalesce(sum(`p`.`PointsEarned`),0) from `activity_point` `p` where (`p`.`AthleteID` = `a`.`AthleteID`)) AS `TotalActivityPoints` from `athlete` `a` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-20 12:57:25
