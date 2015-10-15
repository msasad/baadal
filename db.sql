-- MySQL dump 10.13  Distrib 5.6.19, for debian-linux-gnu (x86_64)
--
-- Host: 10.237.23.178    Database: baadal2
-- ------------------------------------------------------
-- Server version	5.5.44-MariaDB-1ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `network_secgroups`
--

DROP TABLE IF EXISTS `network_secgroups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `network_secgroups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `network` varchar(36) DEFAULT NULL,
  `secgroup` varchar(36) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unik1` (`network`,`secgroup`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `network_secgroups`
--

LOCK TABLES `network_secgroups` WRITE;
/*!40000 ALTER TABLE `network_secgroups` DISABLE KEYS */;
/*!40000 ALTER TABLE `network_secgroups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `security_domain`
--

DROP TABLE IF EXISTS `security_domain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `security_domain` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `vlan` int(11) DEFAULT NULL,
  `visible_to_all` char(1) NOT NULL DEFAULT 'T',
  `org_visibility` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `security_domain`
--

LOCK TABLES `security_domain` WRITE;
/*!40000 ALTER TABLE `security_domain` DISABLE KEYS */;
INSERT INTO `security_domain` VALUES (1,'Research',1,'T',NULL),(2,'Private',2,'T',NULL),(3,'Infrastructure',3,'T',NULL),(4,'Baadal Internal',4,'T',NULL);
/*!40000 ALTER TABLE `security_domain` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vm_requests`
--

DROP TABLE IF EXISTS `vm_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vm_requests` (
  `id` int(5) NOT NULL AUTO_INCREMENT,
  `vm_name` varchar(36) DEFAULT NULL,
  `flavor` varchar(36) DEFAULT NULL,
  `sec_domain` varchar(36) DEFAULT NULL,
  `image` varchar(36) DEFAULT NULL,
  `owner` varchar(36) DEFAULT NULL,
  `purpose` tinytext,
  `public_ip_required` int(1) DEFAULT '0',
  `extra_storage` int(4) DEFAULT '0',
  `collaborators` tinytext,
  `request_time` int(10) NOT NULL,
  `state` int(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `vm_name` (`vm_name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

-- Request state values and their meanings:
--    0   Pending faculty approval
--    1   Pending admin approval
--    2   Approved
--    3   Modified and approved
--    4   Rejected
--
--
-- Dumping data for table `vm_requests`
--

LOCK TABLES `vm_requests` WRITE;
/*!40000 ALTER TABLE `vm_requests` DISABLE KEYS */;
INSERT INTO `vm_requests` VALUES (1,'testvm09','cd5d72cd-acc6-4273-96c7-ff7f3f039a2b','c54848ab-2dd8-4665-8991-7afc1ff6391b','2d18a3be-9298-44fb-9c05-e3b2be159504','test','',0,NULL,'',1444813702,0),(2,'demovm01','cd5d72cd-acc6-4273-96c7-ff7f3f039a2b','c54848ab-2dd8-4665-8991-7afc1ff6391b','2d18a3be-9298-44fb-9c05-e3b2be159504','test','',0,NULL,'',1444879606,0);
/*!40000 ALTER TABLE `vm_requests` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-10-15  9:47:15
