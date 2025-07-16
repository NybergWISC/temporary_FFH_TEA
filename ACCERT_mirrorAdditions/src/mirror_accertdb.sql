CREATE DATABASE  IF NOT EXISTS `accert_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `accert_db`;
-- MySQL dump 10.13  Distrib 8.0.38, for macos14 (arm64)
--
-- Host: 127.0.0.1    Database: accert_db
-- ------------------------------------------------------
-- Server version	8.0.27

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `mirror_acco`
--

DROP TABLE IF EXISTS `mirror_acco`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mirror_acco` (
  `ind` int DEFAULT NULL,
  `code_of_account` varchar(20) NOT NULL,
  `account_description` text,
  `total_cost` double DEFAULT NULL,
  `level` int DEFAULT NULL,
  `supaccount` text,
  `review_status` text,
  `prn` double DEFAULT NULL,
  `alg_name` text,
  `fun_unit` text,
  `variables` text,
  PRIMARY KEY (`code_of_account`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mirror_acco`
--

LOCK TABLES `mirror_acco` WRITE;
/*!40000 ALTER TABLE `mirror_acco` DISABLE KEYS */;
INSERT INTO `mirror_acco` VALUES (TODO),(),();
/*!40000 ALTER TABLE `mirror_acco` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mirror_alg`
--

DROP TABLE IF EXISTS `mirror_alg`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mirror_alg` (
  `ind` int DEFAULT NULL,
  `alg_name` varchar(20) NOT NULL,
  `alg_for` text,
  `alg_description` text,
  `alg_python` text,
  `alg_formulation` text,
  `alg_units` text,
  PRIMARY KEY (`alg_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mirror_alg`
--

LOCK TABLES `mirror_alg` WRITE;
/*!40000 ALTER TABLE `mirror_alg` DISABLE KEYS */;
INSERT INTO `mirror_alg` VALUES (TODO),(),();
/*!40000 ALTER TABLE `mirror_alg` ENABLE KEYS */;
UNLOCK TABLES;

/* TODO Deleted LCOE tables for now */

--
-- Table structure for table `mirror_varv`
--

DROP TABLE IF EXISTS `mirror_varv`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mirror_varv` (
  `ind` int DEFAULT NULL,
  `var_name` varchar(20) NOT NULL,
  `var_description` text,
  `var_value` double DEFAULT NULL,
  `var_unit` text,
  `var_alg` text,
  `var_need` text,
  `v_linked` text,
  `user_input` int DEFAULT NULL,
  PRIMARY KEY (`var_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mirror_varv`
--

LOCK TABLES `mirror_varv` WRITE;
/*!40000 ALTER TABLE `mirror_varv` DISABLE KEYS */;
INSERT INTO `mirror_varv` VALUES (TODO),(),();
/*!40000 ALTER TABLE `mirror_varv` ENABLE KEYS */;
UNLOCK TABLES;

/* TODO add mirror vars and others */

--
-- Dumping events for database 'accert_db'
--

--
-- Dumping routines for database 'accert_db'
--
/*!50003 DROP PROCEDURE IF EXISTS `cal_direct_cost_elements` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `cal_direct_cost_elements`(IN acc_table VARCHAR(50),
																		IN cel_table varchar(50))
BEGIN
    DECLARE tprn DECIMAL(18,6);

    -- Calculate tprn (sum of 'prn' in the account table)
    SET @query = CONCAT('SELECT SUM(t1.prn) INTO @tprn
                         FROM ', acc_table, ' AS t1
                         LEFT JOIN ', acc_table, ' AS t2
                         ON t1.code_of_account = t2.supaccount
                         WHERE t2.code_of_account IS NULL
                         AND t1.code_of_account != ''2''
                         AND t1.code_of_account != ''2C'';');
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
    
    -- Get the calculated tprn value
    SET tprn = @tprn;

    -- Select the calculated 'fac', 'lab', and 'mat' values
    SET @query = CONCAT('SELECT cost_2017 / ', tprn, ' AS fac FROM ', cel_table, '
                        WHERE account = ''2'' AND cost_element = ''2c_fac'';');
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    SET @query = CONCAT('SELECT cost_2017 / ', tprn, ' AS lab FROM ', cel_table, '
                        WHERE account = ''2'' AND cost_element = ''2c_lab'';');
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    SET @query = CONCAT('SELECT cost_2017 / ', tprn, ' AS mat FROM ', cel_table, '
                        WHERE account = ''2'' AND cost_element = ''2c_mat'';');
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    SET @query = CONCAT('SELECT 
        (SELECT cost_2017 / ', tprn, ' FROM ', cel_table, ' WHERE account = ''2'' AND cost_element = ''2c_fac'') AS fac,
        (SELECT cost_2017 / ', tprn, ' FROM ', cel_table, ' WHERE account = ''2'' AND cost_element = ''2c_lab'') AS lab,
        (SELECT cost_2017 / ', tprn, ' FROM ', cel_table, ' WHERE account = ''2'' AND cost_element = ''2c_mat'') AS mat;');
    
    PREPARE stmt FROM @query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `extract_affected_accounts` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `extract_affected_accounts`(IN acc_table VARCHAR(50),
																		IN var_table VARCHAR(50))
BEGIN
	SET @stmt = CONCAT("SELECT va.var_name, (SELECT GROUP_CONCAT(ac.code_of_account SEPARATOR ', ')
        FROM ", acc_table, " ac
        WHERE FIND_IN_SET(va.var_name, REPLACE(ac.variables, ' ', '')) > 0) AS ac_affected
                        FROM
                        (SELECT * FROM ",var_table,"
                        WHERE user_input = 1) as va
                        WHERE (SELECT GROUP_CONCAT(ac.code_of_account SEPARATOR ', ')
								FROM ", acc_table, " ac
						WHERE FIND_IN_SET(va.var_name, REPLACE(ac.variables, ' ', '')) > 0) IS NOT NULL
                        ");
	PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `extract_affected_cost_elements` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `extract_affected_cost_elements`(IN cel_table varchar(50),
                                                                              IN var_table varchar(50))
BEGIN
    SET @stmt = CONCAT("SELECT va.var_name, (SELECT GROUP_CONCAT(ce.cost_element SEPARATOR ', ')
        FROM ", cel_table, " ce
        WHERE FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0) AS ce_affected
                        FROM
                        (SELECT * FROM ",var_table,"
                        WHERE user_input = 1) as va
                        WHERE (SELECT GROUP_CONCAT(ce.cost_element SEPARATOR ', ')
								FROM ", cel_table, " ce
						WHERE FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0) IS NOT NULL
                        ");
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `extract_affected_cost_elements_w_dis` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `extract_affected_cost_elements_w_dis`(IN cel_table varchar(50),
                                                                              IN var_table varchar(50))
BEGIN
    SET @stmt = CONCAT("SELECT va.var_name,va.var_description, (SELECT GROUP_CONCAT(ce.cost_element SEPARATOR ', ')
        FROM ", cel_table, " ce
        WHERE FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0) AS ce_affected
                        FROM
                        (SELECT * FROM ",var_table,"
                        WHERE user_input = 1) as va
                        WHERE (SELECT GROUP_CONCAT(ce.cost_element SEPARATOR ', ')
								FROM cost_element ce
						WHERE FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0) IS NOT NULL
                        ");
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `extract_changed_cost_elements` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `extract_changed_cost_elements`(IN cel_table VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT cost_element, cost_2017
                        FROM ',cel_table,'
                        WHERE updated != 0
                        ORDER BY account, cost_element;');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `extract_super_val` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `extract_super_val`(IN table_name VARCHAR(50),
                                          IN var_name VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT v_linked FROM ', table_name, ' WHERE var_name = ?');
 PREPARE stmt FROM @stmt;
 SET @var_name = var_name;
 EXECUTE stmt USING @var_name;
 DEALLOCATE PREPARE stmt;
 END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `extract_total_cost_on_name` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `extract_total_cost_on_name`(IN table_name VARCHAR(50),
                                          IN tc_name VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT code_of_account, account_description, total_cost
                        FROM ', table_name, ' WHERE code_of_account = ?');
PREPARE stmt FROM @stmt;
SET @tc_name = tc_name;
EXECUTE stmt USING @tc_name;
DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `extract_user_changed_variables` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `extract_user_changed_variables`(IN table_name VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT var_name,var_description, var_value, var_unit
                        FROM ', table_name, ' WHERE user_input = 1 ORDER BY var_name;');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `extract_variable_info_on_name` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `extract_variable_info_on_name`(IN table_name VARCHAR(50),
                                          IN var_name VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT var_value, var_unit FROM ', table_name, ' WHERE var_name = ?');
PREPARE stmt FROM @stmt;
SET @var_name = var_name;
EXECUTE stmt USING @var_name;
DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_current_COAs` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `get_current_COAs`(IN table_name VARCHAR(50), 
                                  IN inp_id VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT code_of_account, 
                       ind FROM ', table_name, ' WHERE supaccount = ?');
    PREPARE stmt FROM @stmt;
    SET @inp_id = inp_id;
    EXECUTE stmt USING @inp_id;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_var_value_by_name` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `get_var_value_by_name`(IN table_name VARCHAR(50),
                                                                    IN `var_name` VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT var_value FROM ', table_name, ' WHERE var_name = ?');
    PREPARE stmt FROM @stmt;
    SET @var_name = var_name;
    EXECUTE stmt USING @var_name;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `insert_new_COA` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `insert_new_COA`(IN table_name VARCHAR(50),
											IN ind INT,
											IN supaccount VARCHAR(50),
											IN level INT,
											IN code_of_account VARCHAR(50),
											IN account_description VARCHAR(50),
											IN total_cost INT,
											IN review_status VARCHAR(50),
											IN prn VARCHAR(50))
BEGIN
	SET @stmt = CONCAT('INSERT INTO ', table_name,
						' (ind, supaccount, level, code_of_account, account_description, 
							total_cost, review_status, prn) 
							VALUES (?, ?, ?, ?, ?, ?, ?, ?)');
PREPARE stmt FROM @stmt;
SET @ind = ind;
SET @supaccount = supaccount;
SET @level = level;
SET @code_of_account = code_of_account;
SET @account_description = account_description;
SET @total_cost = total_cost;
SET @review_status = review_status;
SET @prn = prn;


EXECUTE stmt USING @ind, @supaccount, @level, @code_of_account, @account_description,
@total_cost, @review_status, @prn;
DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `insert_new_COA_gncoa` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `insert_new_COA_gncoa`(IN table_name VARCHAR(50),
											IN ind INT,
											IN supaccount VARCHAR(50),
											IN level INT,
											IN code_of_account VARCHAR(50),
											IN account_description VARCHAR(50),
											IN total_cost INT,
											IN review_status VARCHAR(50),
											IN prn VARCHAR(50),
                                            IN gncoa VARCHAR(50), 
                                            IN gn_level INT, 
                                            IN gn_supaccount VARCHAR(50), 
											IN gn_ind INT)
BEGIN
	SET @stmt = CONCAT('INSERT INTO ', table_name,
						' (ind, supaccount, level, code_of_account, account_description, 
							total_cost, review_status, prn, 
                            gncoa, gn_level, gn_supaccount, gn_ind) 
							VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)');
PREPARE stmt FROM @stmt;
SET @ind = ind;
SET @supaccount = supaccount;
SET @level = level;
SET @code_of_account = code_of_account;
SET @account_description = account_description;
SET @total_cost = total_cost;
SET @review_status = review_status;
SET @prn = prn;
SET @gncoa = gncoa; 
SET @gn_level = gn_level; 
SET @gn_supaccount = gn_supaccount;
SET @gn_ind = gn_ind;

EXECUTE stmt USING @ind, @supaccount, @level, @code_of_account, @account_description,
@total_cost, @review_status, @prn, @gncoa, @gn_level, @gn_supaccount, @gn_ind;
DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_account_all` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_account_all`(IN table_name varchar(50),
                                                                IN level int)
BEGIN
    SET @stmt=CONCAT('SELECT * FROM ',table_name,' WHERE level <= ?');
    PREPARE stmt FROM @stmt;
    SET @level=level;
    EXECUTE stmt USING @level;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_account_simple` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_account_simple`(IN table_name varchar(50),
                                                                   IN level int)
BEGIN
    SET @stmt=CONCAT('SELECT ind,
                            code_of_account,
                            account_description,
                            total_cost,
                            level,
                            review_status
                            FROM ',table_name,' WHERE level <= ?');
    PREPARE stmt FROM @stmt;
    SET @level=level;
    EXECUTE stmt USING @level;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_leveled_accounts_all` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_leveled_accounts_all`(IN acc_table varchar(50),
                                                                        IN  cel_table varchar(50),
                                                                        IN  level int)
BEGIN
    SET @stmt=CONCAT('SELECT acc.level,
                            rankedcoa.code_of_account as code_of_account,
                            acc.account_description,
                            sorted_ce.fac_cost,
                            sorted_ce.lab_cost,
                            sorted_ce.mat_cost,
                            acc.total_cost,
                            acc.review_status
                            FROM ',acc_table,' as acc
                            JOIN
                            (SELECT node.code_of_account AS COA , 
								CONCAT( REPEAT(" ", node.level), node.code_of_account) AS code_of_account
								FROM ',acc_table,' AS node
								ORDER BY node.ind) as rankedcoa
                                ON acc.code_of_account=rankedcoa.COA
                                JOIN (SELECT splt_act.code_of_account,
											   cef.cost_2017 AS fac_cost,
											   cel.cost_2017 AS lab_cost,
											   cem.cost_2017 AS mat_cost
										FROM 
											(SELECT code_of_account, 
													CONCAT(code_of_account, "_fac") AS fac_name,
													CONCAT(code_of_account, "_lab") AS lab_name,
													CONCAT(code_of_account, "_mat") AS mat_name
											 FROM ',acc_table,') AS splt_act
										LEFT JOIN ',cel_table,' AS cef
											ON cef.cost_element = splt_act.fac_name
										LEFT JOIN ',cel_table,' AS cel
											ON cel.cost_element = splt_act.lab_name
										LEFT JOIN ',cel_table,' AS cem
											ON cem.cost_element = splt_act.mat_name) as sorted_ce
                                    ON sorted_ce.code_of_account=acc.code_of_account
                                    WHERE acc.level <= ?
                                    ORDER BY acc.ind;');
    PREPARE stmt FROM @stmt;
    SET @level=level;
    EXECUTE stmt USING @level;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_leveled_accounts_gn` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_leveled_accounts_gn`(
    IN acc_table VARCHAR(255),
    IN map_table VARCHAR(255),
    IN level INT
)
BEGIN
    SET @stmt = CONCAT(
        'SELECT rankedcoa.gncoa,
				map.gncoa_description,
                acc.total_cost,
                acc.gn_level,
                acc.review_status
         FROM ', acc_table, ' AS acc
         JOIN 
         (
             SELECT node.gncoa AS COA, 
                    CONCAT(REPEAT(" ", node.gn_level), node.gncoa) AS gncoa
             FROM ', acc_table, ' AS node
             ORDER BY node.gn_ind
         ) AS rankedcoa
         ON acc.gncoa = rankedcoa.COA
         JOIN ',map_table,' as map
         ON acc.gncoa = map.gncoa
         WHERE acc.gn_level <= ?
         ORDER BY acc.gn_ind;'
    );
    
    PREPARE stmt FROM @stmt;
    SET @level = level;
    EXECUTE stmt USING @level;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_leveled_accounts_gn_all` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_leveled_accounts_gn_all`(IN acc_table varchar(50),
                                                                        IN  cel_table varchar(50),
                                                                        IN  level int)
BEGIN
    SET @stmt=CONCAT('SELECT acc.gn_level,
                            rankedcoa.gncoa as gncoa,
                            acc.account_description,
                            sorted_ce.fac_cost,
                            sorted_ce.lab_cost,
                            sorted_ce.mat_cost,
                            acc.total_cost,
                            acc.review_status
                            FROM ',acc_table,' as acc
                            JOIN
							 (SELECT node.gncoa AS COA, 
										CONCAT(REPEAT(" ", node.gn_level), node.gncoa) AS gncoa
								 FROM ', acc_table, ' AS node
								 ORDER BY node.gn_ind) AS rankedcoa
                                ON acc.gncoa=rankedcoa.COA
                                JOIN (SELECT splt_act.code_of_account,
											   cef.cost_2017 AS fac_cost,
											   cel.cost_2017 AS lab_cost,
											   cem.cost_2017 AS mat_cost
										FROM 
											(SELECT code_of_account, 
													CONCAT(code_of_account, "_fac") AS fac_name,
													CONCAT(code_of_account, "_lab") AS lab_name,
													CONCAT(code_of_account, "_mat") AS mat_name
											 FROM ',acc_table,') AS splt_act
										LEFT JOIN ',cel_table,' AS cef
											ON cef.cost_element = splt_act.fac_name
										LEFT JOIN ',cel_table,' AS cel
											ON cel.cost_element = splt_act.lab_name
										LEFT JOIN ',cel_table,' AS cem
											ON cem.cost_element = splt_act.mat_name) as sorted_ce
                                    ON sorted_ce.code_of_account=acc.code_of_account
                                    WHERE acc.gn_level <= ?
                                    ORDER BY acc.gn_ind;');
    PREPARE stmt FROM @stmt;
    SET @level=level;
    EXECUTE stmt USING @level;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_leveled_accounts_simple` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_leveled_accounts_simple`(IN acc_table VARCHAR(255), IN level INT)
BEGIN
    SET @stmt = CONCAT('SELECT rankedcoa.code_of_account,
                    acc.account_description,
                    acc.total_cost,
                    acc.level,
                    acc.review_status
                    FROM ',acc_table,' as acc
                    JOIN
                    (SELECT node.code_of_account AS COA , 
                    CONCAT( REPEAT(" ", node.level), node.code_of_account) AS code_of_account
                    FROM ',acc_table,' AS node
                    ORDER BY node.ind) as rankedcoa
                    ON acc.code_of_account=rankedcoa.COA
                    WHERE acc.level <= ?
                    ORDER BY acc.ind;');
    PREPARE stmt FROM @stmt;
    SET @level=level;
    EXECUTE stmt USING @level;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_table` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_table`(IN table_name VARCHAR(255))
BEGIN
    SET @stmt = CONCAT('SELECT * FROM ',table_name);
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_updated_cost_elements` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_updated_cost_elements`(IN cel_table VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT ind,
                                cost_element,
                                cost_2017,    
                                sup_cost_ele,
                                account,
                                updated
                        FROM ',cel_table,'
                        WHERE updated = 1');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `print_user_request_parameter` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `print_user_request_parameter`(IN all_col BOOLEAN,
                                                                           IN var_table VARCHAR(50), 
                                                                           IN cel_table VARCHAR(50))
BEGIN
    IF all_col THEN
		SET @stmt = CONCAT("SELECT va.ind, va.var_name, 
       (SELECT GROUP_CONCAT(ce.cost_element SEPARATOR ', ')
        FROM ", cel_table, " ce
        WHERE FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0) AS ce_affected
		FROM ",var_table," as va
		WHERE va.var_value IS NULL
		ORDER BY va.ind;");
    ELSE
        SET @stmt = CONCAT("SELECT va.var_name, 
       (SELECT GROUP_CONCAT(ce.cost_element SEPARATOR ', ')
        FROM ", cel_table, " ce
        WHERE FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0) AS ce_affected
		FROM ",var_table," as va
		WHERE va.var_value IS NULL
		ORDER BY va.ind;");
    END IF;
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `remove_specific_row` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `remove_specific_row`(
    IN table_name VARCHAR(50),
    IN target_code VARCHAR(50)
)
BEGIN
    SET SQL_SAFE_UPDATES = 0;
    
    SET @stmt = CONCAT(
        'DELETE FROM ', table_name,
        ' WHERE code_of_account = \'', target_code, '\''
    );

    -- Debug: Print the constructed SQL statement
    SELECT @stmt;
    
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `roll_up_account_table_by_gn_level` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `roll_up_account_table_by_gn_level`(
    IN table_name VARCHAR(50),
    IN from_level INT,
    IN to_level INT
)
BEGIN
    SET SQL_SAFE_UPDATES = 0;

    SET @stmt = CONCAT(
        'UPDATE ', table_name, ',',
        '(SELECT a', to_level, '.gncoa AS ac', to_level, '_coa, ',
                'SUM(ua', from_level, '.total_cost) AS a', to_level, '_cal_total_cost ',
        'FROM ', table_name, ' AS ua', from_level,
        ' JOIN ', table_name, ' AS a', to_level,
        ' ON ua', from_level, '.gn_supaccount = a', to_level, '.gncoa ',
        'WHERE ua', from_level, '.gn_level = ', from_level,
        ' AND a', to_level, '.gn_level = ', to_level,
        ' GROUP BY a', to_level, '.gncoa) AS updated_ac', to_level,
        ' SET ',
        table_name, '.total_cost = updated_ac', to_level, '.a', to_level, '_cal_total_cost, ',
        table_name, '.review_status = \'Updated\' ',
        'WHERE ',
        table_name, '.gncoa = updated_ac', to_level, '.ac', to_level, '_coa'
    );

    -- Debug: Print the constructed SQL statement
    SELECT @stmt;

    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `roll_up_account_table_by_level` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `roll_up_account_table_by_level`(IN table_name varchar(50),
                                                                        IN from_level int, IN to_level int)
BEGIN
	SET SQL_SAFE_UPDATES = 0;
    SET @stmt = CONCAT('UPDATE ', table_name, ',',
                    '(SELECT a',to_level,'.code_of_account as ac',to_level,'_coa, ',
                            'sum(ua',from_level,'.total_cost) as a',to_level,'_cal_total_cost ',
                    'FROM ', table_name, ' as ua',from_level,
                    ' JOIN ', table_name, ' as a',to_level,
                    ' on ua',from_level,'.supaccount=a',to_level,'.code_of_account ',
                    'where ua',from_level,'.level=',from_level,
                    ' and a',to_level,'.level=',to_level,
                    ' group by a',to_level,'.code_of_account) as updated_ac',to_level,
                    ' SET ',
                    table_name,'.total_cost = updated_ac',to_level,'.a',to_level,'_cal_total_cost,',
                    table_name,'.review_status = \'Updated\' ',
                    'WHERE ',
                    table_name,'.code_of_account = updated_ac',to_level,'.ac',to_level,'_coa');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `roll_up_cost_elements_by_level` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `roll_up_cost_elements_by_level`(IN table_name varchar(50), 
                                                                  IN from_level int, IN to_level int)
BEGIN
    SET @stmt = CONCAT('UPDATE ', table_name, ',',
                        '(SELECT c',to_level,'.cost_element as ce',to_level,'_ce, ',
                            'sum(uc',from_level,'.cost_2017) as c',to_level,'_cal_total_cost ',
                        'FROM ', table_name, ' as uc',from_level,
                        ' JOIN ', table_name, ' as c',to_level,
                        ' on uc',from_level,'.sup_cost_ele=c',to_level,'.cost_element ',
                        'join account as ac',to_level,
                        ' on c',to_level,'.account = ac',to_level,'.code_of_account ',
                        'where ac',to_level,'.level=',to_level,
                        ' group by c',to_level,'.cost_element) as updated_ce',to_level,
                        ' SET ',
                        table_name,'.cost_2017 = updated_ce',to_level,'.c',to_level,'_cal_total_cost,',
                        table_name,'.updated = 1 ',
                        'WHERE ',
                        table_name,'.cost_element = updated_ce',to_level,'.ce',to_level,'_ce');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `roll_up_lmt_account_2C` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `roll_up_lmt_account_2C`(IN acc_tabl_name varchar(50))
BEGIN
    SET @stmt = CONCAT('UPDATE ', acc_tabl_name, ',',
                        '(SELECT sum(t1.total_cost) as tc, sum(t1.prn) as tprn FROM
                            ', acc_tabl_name, ' AS t1 LEFT JOIN ', acc_tabl_name, ' as t2
                            ON t1.code_of_account = t2.supaccount
                            WHERE t2.code_of_account IS NULL
                            and t1.code_of_account!=\'2\'
                            and t1.code_of_account!=\'2C\') as dircost
                        SET ', acc_tabl_name, '.total_cost = dircost.tc,
                        ', acc_tabl_name, '.prn=dircost.tprn,
                        review_status = \'Ready for Review\'
                        WHERE ', acc_tabl_name, '.code_of_account = \'2C\';');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `roll_up_lmt_direct_cost` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `roll_up_lmt_direct_cost`(IN acc_tabl_name varchar(50))
BEGIN
    SET @stmt = CONCAT('UPDATE ', acc_tabl_name, ',',
                        '(SELECT  (total_cost/prn) as talcost
                            FROM ', acc_tabl_name, ' as pre_acc
                            WHERE pre_acc.code_of_account =\'2C\') as calcost
                        SET ', acc_tabl_name, '.total_cost = calcost.talcost,
                        review_status = \'Ready for Review\'
                        WHERE ', acc_tabl_name, '.code_of_account = \'2\';');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sum_cost_elements_2C_fac` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `sum_cost_elements_2C_fac`(IN cel_tabl_name varchar(50),
                                                                    IN acc_tabl_name varchar(50))
BEGIN
    SET @stmt = CONCAT('SELECT sum(cef.cost_2017) from
                        (SELECT t1.code_of_account,
                        CONCAT(t1.code_of_account,\'_fac\') as fac_name
                        FROM ', acc_tabl_name, ' AS t1
                        LEFT JOIN ', acc_tabl_name, ' as t2
                        ON t1.code_of_account = t2.supaccount
                        WHERE t2.code_of_account IS NULL
                        and t1.code_of_account!=\'2\'
                        and t1.code_of_account!=\'2C\' )as ac
                        join ', cel_tabl_name, ' as cef
                                on cef.cost_element = ac.fac_name
                                where ac.code_of_account!=\'2C\'');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sum_cost_elements_2C_lab` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `sum_cost_elements_2C_lab`(IN cel_tabl_name varchar(50),  
                                                                    IN acc_tabl_name varchar(50))
BEGIN
    SET @stmt = CONCAT('SELECT sum(cef.cost_2017) from
                        (SELECT t1.code_of_account,
                        CONCAT(t1.code_of_account,\'_lab\') as lab_name
                        FROM ', acc_tabl_name, ' AS t1
                        LEFT JOIN ', acc_tabl_name, ' as t2
                        ON t1.code_of_account = t2.supaccount
                        WHERE t2.code_of_account IS NULL
                        and t1.code_of_account!=\'2\'
                        and t1.code_of_account!=\'2C\' )as ac
                        join ', cel_tabl_name, ' as cef
                                on cef.cost_element = ac.lab_name
                                where ac.code_of_account!=\'2C\'');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sum_cost_elements_2C_mat` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `sum_cost_elements_2C_mat`(IN cel_tabl_name varchar(50),
                                                                    IN acc_tabl_name varchar(50))
BEGIN
    SET @stmt = CONCAT('SELECT sum(cef.cost_2017) from
                        (SELECT t1.code_of_account,
                        CONCAT(t1.code_of_account,\'_mat\') as mat_name
                        FROM ', acc_tabl_name, ' AS t1
                        LEFT JOIN ', acc_tabl_name, ' as t2
                        ON t1.code_of_account = t2.supaccount
                        WHERE t2.code_of_account IS NULL
                        and t1.code_of_account!=\'2\'
                        and t1.code_of_account!=\'2C\' )as ac
                        join ', cel_tabl_name, ' as cef
                                on cef.cost_element = ac.mat_name
                                where ac.code_of_account!=\'2C\'');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sum_up_lmt_account_2C` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `sum_up_lmt_account_2C`(IN acc_tabl_name varchar(50))
BEGIN
    SET @stmt = CONCAT('UPDATE ', acc_tabl_name, ',',
                        '(SELECT sum(t1.total_cost) as tc, sum(t1.prn) as tprn FROM
                            ', acc_tabl_name, ' AS t1 LEFT JOIN ', acc_tabl_name, ' as t2
                            ON t1.code_of_account = t2.supaccount
                            WHERE t2.code_of_account IS NULL
                            and t1.code_of_account!=\'2\'
                            and t1.code_of_account!=\'2C\') as dircost
                        SET ', acc_tabl_name, '.total_cost = dircost.tc,
                        ', acc_tabl_name, '.prn=dircost.tprn,
                        review_status = \'Ready for Review\'
                        WHERE ', acc_tabl_name, '.code_of_account = \'2C\';');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sum_up_lmt_direct_cost` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `sum_up_lmt_direct_cost`(IN acc_tabl_name varchar(50))
BEGIN
    SET @stmt = CONCAT('UPDATE ', acc_tabl_name, ',',
                        '(SELECT  (total_cost/prn) as talcost
                            FROM ', acc_tabl_name, ' as pre_acc
                            WHERE pre_acc.code_of_account =\'2C\') as calcost
                        SET ', acc_tabl_name, '.total_cost = calcost.talcost,
                        review_status = \'Ready for Review\'
                        WHERE ', acc_tabl_name, '.code_of_account = \'2\';');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sup_coa_level` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `sup_coa_level`(IN table_name VARCHAR(50),
                                          IN supaccount VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT level FROM ', table_name, ' WHERE code_of_account = ?');
PREPARE stmt FROM @stmt;
SET @supaccount = supaccount;
EXECUTE stmt USING @supaccount;
DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_account_before_insert` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `update_account_before_insert`(IN table_name VARCHAR(50),
                                              IN min_ind INT)
BEGIN
	SET SQL_SAFE_UPDATES = 0;
    SET @stmt = CONCAT('UPDATE ', table_name,
                       ' SET ind = ind + 1 WHERE ind >?');
    PREPARE stmt FROM @stmt;
    SET @min_ind = min_ind;
    EXECUTE stmt USING @min_ind;
    DEALLOCATE PREPARE stmt;  
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_account_table_by_cost_elements` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `update_account_table_by_cost_elements`(IN acc_tabl_name varchar(50),
																					IN cel_tabl_name varchar(50))
BEGIN
	SET SQL_SAFE_UPDATES = 0;
	SET @stmt = CONCAT('UPDATE ', acc_tabl_name, ',',
						'(SELECT ', acc_tabl_name, '.code_of_account,
								ce.total_cost as cost,
								ce.updated as updated
						FROM ', acc_tabl_name, '
						JOIN (SELECT account,
									sum(cost_2017) as total_cost,
									sum(updated) as updated
							FROM ', cel_tabl_name, '
							GROUP BY ', cel_tabl_name, '.account ) as ce
						on ', acc_tabl_name, '.code_of_account = ce.account
						ORDER BY ', acc_tabl_name, '.ind) as updated_account
						SET ', acc_tabl_name, '.total_cost = updated_account.cost,
						review_status = \'Ready for Review\'
						WHERE updated_account.updated > 0
						and ', acc_tabl_name, '.code_of_account = updated_account.code_of_account;');
	PREPARE stmt FROM @stmt;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_cost_element_on_name` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `update_cost_element_on_name`(IN table_name VARCHAR(50),
                                                                          IN `ce_name` VARCHAR(50),
                                                                          IN `alg_value` DECIMAL(20,5)  )
BEGIN
    SET SQL_SAFE_UPDATES = 0;

    SET @stmt = CONCAT('UPDATE ', table_name, 
                       ' SET cost_2017 = ', alg_value, 
                       ', updated = 1 WHERE cost_element = ''', ce_name, '''');
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_new_accounts` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `update_new_accounts`(IN acc_tabl_name VARCHAR(50),
                                                                        IN var_tabl_name VARCHAR(50),
                                                                        IN alg_tabl_name VARCHAR(50))
BEGIN
	SET SQL_SAFE_UPDATES = 0;
    SET @stmt = CONCAT("SELECT ac.ind, ac.code_of_account,
       ac.total_cost, ac.alg_name,
       ac.variables, 
       alg.alg_python, alg.alg_formulation, alg.alg_units 
		FROM ", acc_tabl_name, " AS ac 
		JOIN ", alg_tabl_name, " AS alg ON ac.alg_name = alg.alg_name
		WHERE EXISTS (
			SELECT 1
			FROM ", var_tabl_name, " AS va
			WHERE va.user_input = 1
			AND FIND_IN_SET(va.var_name, REPLACE(ac.variables, ' ', '')) > 0);");
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_new_cost_elements` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `update_new_cost_elements`(IN cel_tabl_name VARCHAR(50),
                                                                        IN var_tabl_name VARCHAR(50),
                                                                        IN alg_tabl_name VARCHAR(50))
BEGIN
	SET SQL_SAFE_UPDATES = 0;
    SET @stmt = CONCAT("SELECT ce.ind, ce.cost_element,
       ce.cost_2017, ce.alg_name,
       ce.variables, ce.algno,
       alg.alg_python, alg.alg_formulation, alg.alg_units 
		FROM ", cel_tabl_name, " AS ce 
		JOIN ", alg_tabl_name, " AS alg ON ce.alg_name = alg.alg_name
		WHERE EXISTS (
			SELECT 1
			FROM ", var_tabl_name, " AS va
			WHERE va.user_input = 1
			AND FIND_IN_SET(va.var_name, REPLACE(ce.variables, ' ', '')) > 0);");
    PREPARE stmt FROM @stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_super_variable` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `update_super_variable`(IN var_table_name VARCHAR(50),
                            IN alg_table_name VARCHAR(50), IN `u_i_var_name` VARCHAR(50))
BEGIN
    SET @stmt = CONCAT('SELECT var.ind, var.var_name, var.var_value,
                        var.var_alg, var.var_need, alg.ind, alg.alg_python,
                        alg.alg_formulation, alg.alg_units, var.var_unit
                        FROM ', var_table_name, ' as var JOIN ', alg_table_name, ' as alg
                        ON var.var_alg=alg.alg_name
                        WHERE var.var_name=?');
PREPARE stmt FROM @stmt;
SET @var_name = u_i_var_name;
EXECUTE stmt USING @var_name;
DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_total_cost_on_name` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `update_total_cost_on_name`(IN table_name VARCHAR(50),
                                                                        IN `tc_id` VARCHAR(50), 
                                                                        IN `u_i_tc_value` DECIMAL(20,5))
BEGIN
	SET SQL_SAFE_UPDATES = 0;
    SET @stmt = CONCAT('UPDATE ', table_name, ' SET total_cost = ?, 
                                              review_status = "User Input" WHERE code_of_account = ?');
    PREPARE stmt FROM @stmt;
    SET @tc_id = tc_id;
    SET @u_i_tc_value = u_i_tc_value;
    EXECUTE stmt USING @u_i_tc_value, @tc_id;
    DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `update_variable_info_on_name` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`mnyberg`@`localhost` PROCEDURE `update_variable_info_on_name`(IN table_name VARCHAR(50),
                            IN `u_i_var_name` VARCHAR(50), IN `value` DECIMAL(20,5), IN `unit` VARCHAR(50))
BEGIN
	SET SQL_SAFE_UPDATES = 0;
    SET @stmt = CONCAT('UPDATE ', table_name, ' SET var_value = ?,
                        var_unit = ?,
                        user_input = ? WHERE var_name = ?');
PREPARE stmt FROM @stmt;
SET @var_value = value;
SET @var_unit = unit;
SET @user_input = 1;
SET @var_name = u_i_var_name;
EXECUTE stmt USING @var_value, @var_unit, @user_input, @var_name;
DEALLOCATE PREPARE stmt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-09-26 13:08:24
