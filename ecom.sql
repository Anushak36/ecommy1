-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: localhost    Database: ecommy
-- ------------------------------------------------------
-- Server version	8.0.36

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
-- Table structure for table `additems`
--

DROP TABLE IF EXISTS `additems`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `additems` (
  `item_id` binary(16) NOT NULL,
  `item_name` longtext NOT NULL,
  `discription` longtext,
  `quantity` int DEFAULT NULL,
  `category` enum('makeup','skincare','haircare','bodycare') DEFAULT NULL,
  `price` int DEFAULT NULL,
  `addedby` varchar(100) DEFAULT NULL,
  `imgid` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`item_id`),
  KEY `addedby` (`addedby`),
  CONSTRAINT `additems_ibfk_1` FOREIGN KEY (`addedby`) REFERENCES `vendor` (`email`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `additems`
--

LOCK TABLES `additems` WRITE;
/*!40000 ALTER TABLE `additems` DISABLE KEYS */;
INSERT INTO `additems` VALUES (_binary '�y��\��>�0}\�','mac lipstick','hydrating',12,'makeup',567,'anushakatta243@gmail.com','2Yb6Hs.avif'),(_binary '\"q��]\��>�0}\�',' Kerastase shampoo','For saloon like hair',20,'haircare',3335,'anushakatta243@gmail.com','3Cz6Ii.jpeg'),(_binary '1����\��>�0}\�','Dr.Sheths suncreen','Protects you from Uv Rays',12,'skincare',500,'anushakatta243@gmail.com','3Wl6Sg.webp');
/*!40000 ALTER TABLE `additems` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `ordid` binary(16) NOT NULL,
  `itemid` binary(16) NOT NULL,
  `item_name` varchar(255) DEFAULT NULL,
  `qty` int DEFAULT NULL,
  `total_price` decimal(20,4) DEFAULT NULL,
  `user` varchar(255) DEFAULT NULL,
  `category` varchar(150) DEFAULT NULL,
  `dis` text,
  `imgid` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ordid`),
  KEY `itemid` (`itemid`),
  KEY `user` (`user`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`itemid`) REFERENCES `additems` (`item_id`) ON DELETE CASCADE,
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`user`) REFERENCES `user` (`email`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (_binary 'ɧ\�L�\��>�0}\�',_binary '�y��\��>�0}\�','mac lipstick',1,567.0000,'anushakatta243@gmail.com','makeup','hydrating','2Yb6Hs.avif'),(_binary 'ړ��\��>�0}\�',_binary '�y��\��>�0}\�','mac lipstick',1,567.0000,'anushakatta243@gmail.com','makeup','hydrating','2Yb6Hs.avif');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `username` varchar(255) NOT NULL,
  `mobile_no` bigint NOT NULL,
  `email` varchar(255) NOT NULL,
  `address` text NOT NULL,
  `password` varbinary(255) DEFAULT NULL,
  PRIMARY KEY (`email`),
  UNIQUE KEY `mobile_no` (`mobile_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES ('anusha',1234567891,'anushakatta243@gmail.com','vijayawada',_binary '$2b$12$SF.MkP.ilL0St4dycHS/bOkRnQ54Ofbox7RbSxWc0NmtxGDsTG25i');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vendor`
--

DROP TABLE IF EXISTS `vendor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vendor` (
  `email` varchar(100) NOT NULL,
  `v_name` varchar(255) NOT NULL,
  `mobile_no` bigint NOT NULL,
  `address` text NOT NULL,
  `password` varbinary(255) DEFAULT NULL,
  PRIMARY KEY (`email`),
  UNIQUE KEY `mobile_no` (`mobile_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vendor`
--

LOCK TABLES `vendor` WRITE;
/*!40000 ALTER TABLE `vendor` DISABLE KEYS */;
INSERT INTO `vendor` VALUES ('anushakatta243@gmail.com','anusha',1234567891,'vijayawada',_binary '$2b$12$DIYYZSo5Pj2okcnjcUJqq.s7weFqhsp1fcdxIsvHxqfeDWt34jSDC');
/*!40000 ALTER TABLE `vendor` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-05-31 16:42:37
