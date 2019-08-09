-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- Host: classmysql.engr.oregonstate.edu:3306
-- Generation Time: Aug 03, 2019 at 11:20 AM
-- Server version: 10.3.13-MariaDB-log
-- PHP Version: 7.0.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cs340_mouleja`
--

-- --------------------------------------------------------

--
-- Table structure for table `Ingredient`
--

CREATE TABLE `Ingredient` (
  `ingredientId` int(10) NOT NULL,
  `name` varchar(255) NOT NULL,
  `defaultAmount` float DEFAULT NULL,
  `defaultUnit` varchar(15) DEFAULT NULL,
  `calories` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Ingredient`
--

INSERT INTO `Ingredient` (`ingredientId`, `name`, `defaultAmount`, `defaultUnit`, `calories`) VALUES
(2, 'Chicken Broth', 1, 'cup', 5),
(3, 'Quinoa - Dry', 0.25, 'cup', 222),
(4, 'Vegetable Oil', 1, 'teaspoon', 40),
(5, 'onion', 3.5, 'ounce', 40),
(6, 'garlic', 1, 'ounce', 42),
(7, 'Ground Chicken', 4, 'ounce', 170),
(8, 'Rotel Diced Tomatoes And Green Chilies', 1, 'can', 62),
(9, 'Wheat Bread', 1, 'slice', 69),
(10, 'Mayo', 1, 'tablespoon', 50),
(11, 'Dijon Mustard', 1, 'teaspoon', 0),
(12, 'Polish Dill Pickle Spear', 1, 'ounce', 0),
(13, 'Cheddar Cheese', 19, 'grams', 80),
(14, 'celery', 0, '', 0),
(15, 'carrot', 0, '', 0),
(16, 'Half-and-half', 0, '', 0),
(17, 'Butter', 0, '', 0),
(18, 'Olive Oil', 0, '', 0),
(19, 'Flour', 0, '', 0),
(20, 'Ham', 0, '', 0),
(21, 'Cooked Ham', 0, '', 0),
(22, 'Imitation Crab', 0, '', 0);

-- --------------------------------------------------------

--
-- Table structure for table `Recipe`
--

CREATE TABLE `Recipe` (
  `recipeId` int(10) NOT NULL,
  `name` varchar(255) NOT NULL,
  `userId` int(10) NOT NULL,
  `date` datetime NOT NULL DEFAULT current_timestamp(),
  `sourceId` int(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Recipe`
--

INSERT INTO `Recipe` (`recipeId`, `name`, `userId`, `date`, `sourceId`) VALUES
(1, 'Quinoa Chicken', 1, '2019-07-24 00:00:00', 1),
(2, 'Grilled Pickle Sandwich', 1, '2019-07-24 18:55:27', 2),
(3, 'Babaganoush', 1, '2019-08-02 13:07:33', NULL),
(14, 'Chicken Soup', 10, '2019-08-02 22:50:38', 4),
(15, 'Joe\'s Crab Sandwich', 11, '2019-08-02 23:04:55', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `Recipe_Ingredient`
--

CREATE TABLE `Recipe_Ingredient` (
  `recipeId` int(10) NOT NULL,
  `ingredientId` int(10) NOT NULL,
  `amount` float NOT NULL,
  `unit` varchar(15) NOT NULL,
  `preperation` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Recipe_Ingredient`
--

INSERT INTO `Recipe_Ingredient` (`recipeId`, `ingredientId`, `amount`, `unit`, `preperation`) VALUES
(1, 2, 2, 'cups', NULL),
(1, 3, 1, 'cup', NULL),
(1, 4, 2, 'teaspoons', NULL),
(1, 6, 2, 'cloves', 'minced'),
(1, 7, 1.5, 'pounds', NULL),
(1, 8, 1, 'can', NULL),
(2, 9, 2, 'slices', NULL),
(2, 10, 1, 'tablespoon', NULL),
(2, 11, 2, 'teaspoons', NULL),
(2, 12, 3, 'spears', NULL),
(2, 13, 2, 'slices', NULL),
(14, 2, 1, 'cups', ''),
(14, 7, 0.5, 'lbs', ''),
(15, 9, 4, 'slices', ''),
(15, 10, 2, 'tbsp', ''),
(15, 12, 2, 'spears', ''),
(15, 22, 1, 'can', 'drained');

-- --------------------------------------------------------

--
-- Table structure for table `Source`
--

CREATE TABLE `Source` (
  `sourceId` int(10) NOT NULL,
  `name` varchar(255) NOT NULL,
  `url` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Source`
--

INSERT INTO `Source` (`sourceId`, `name`, `url`) VALUES
(1, 'allrecipes', 'www.allrecipes.com'),
(2, 'Smith family recipe', NULL),
(4, 'family secret', ''),
(5, 'back of the can', ''),
(6, 'just guessing', '');

-- --------------------------------------------------------

--
-- Table structure for table `Step`
--

CREATE TABLE `Step` (
  `recipeId` int(10) NOT NULL,
  `step` int(10) NOT NULL,
  `instruction` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Step`
--

INSERT INTO `Step` (`recipeId`, `step`, `instruction`) VALUES
(1, 1, 'Bring chicken broth and quinoa to a boil in a saucepan. Reduce heat to medium-low, cover, and simmer until quinoa is tender and water has been absorbed, 15 to 20 minutes.'),
(1, 2, 'Heat vegetable oil in a large skillet over medium-high heat. Saute onion and garlic in hot oil until onion is translucent, 5 to 7 minutes. Add ground chicken and break into small pieces while cooking until completely browned, 7 to 10 minutes.'),
(1, 3, 'Stir cooked quinoa and diced tomatoes into the chicken mixture; bring to a simmer and cook long enough for the flavors to meld, about 10 minutes more.'),
(2, 1, 'Apply mayo to one slice of bread'),
(2, 2, 'Apply mustard, pickles and cheese to other slice of bread'),
(2, 3, 'Place first slice of bread on top of second.'),
(2, 4, 'Grill in non-stick pan until cheese is melted.  Enjoy!'),
(14, 1, 'Brown ground chicken'),
(15, 1, 'Mixed it all together and put between bread');

-- --------------------------------------------------------

--
-- Table structure for table `User`
--

CREATE TABLE `User` (
  `userId` int(10) NOT NULL,
  `name` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `admin` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `User`
--

INSERT INTO `User` (`userId`, `name`, `password`, `admin`) VALUES
(1, 'Jason', '1234', 1),
(2, 'Tommy', '8888', 1),
(5, 'admin', 'admin', 1),
(7, 'anotheruser', '1111', 0),
(9, 'TommyA', '312312', 0),
(10, 'guest', '1', 0),
(11, 'joe', '1', 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Ingredient`
--
ALTER TABLE `Ingredient`
  ADD PRIMARY KEY (`ingredientId`);

--
-- Indexes for table `Recipe`
--
ALTER TABLE `Recipe`
  ADD PRIMARY KEY (`recipeId`),
  ADD KEY `userId` (`userId`),
  ADD KEY `sourceId` (`sourceId`);

--
-- Indexes for table `Recipe_Ingredient`
--
ALTER TABLE `Recipe_Ingredient`
  ADD PRIMARY KEY (`recipeId`,`ingredientId`),
  ADD KEY `ingredientId` (`ingredientId`);

--
-- Indexes for table `Source`
--
ALTER TABLE `Source`
  ADD PRIMARY KEY (`sourceId`);

--
-- Indexes for table `Step`
--
ALTER TABLE `Step`
  ADD PRIMARY KEY (`recipeId`,`step`);

--
-- Indexes for table `User`
--
ALTER TABLE `User`
  ADD PRIMARY KEY (`userId`),
  ADD UNIQUE KEY `name` (`name`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `Ingredient`
--
ALTER TABLE `Ingredient`
  MODIFY `ingredientId` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `Recipe`
--
ALTER TABLE `Recipe`
  MODIFY `recipeId` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `Source`
--
ALTER TABLE `Source`
  MODIFY `sourceId` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `User`
--
ALTER TABLE `User`
  MODIFY `userId` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `Recipe`
--
ALTER TABLE `Recipe`
  ADD CONSTRAINT `Recipe_ibfk_2` FOREIGN KEY (`sourceId`) REFERENCES `Source` (`sourceId`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `Recipe_ibfk_3` FOREIGN KEY (`userId`) REFERENCES `User` (`userId`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `Recipe_Ingredient`
--
ALTER TABLE `Recipe_Ingredient`
  ADD CONSTRAINT `Recipe_Ingredient_ibfk_1` FOREIGN KEY (`recipeId`) REFERENCES `Recipe` (`recipeId`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `Recipe_Ingredient_ibfk_2` FOREIGN KEY (`ingredientId`) REFERENCES `Ingredient` (`ingredientId`) ON UPDATE CASCADE;

--
-- Constraints for table `Step`
--
ALTER TABLE `Step`
  ADD CONSTRAINT `Step_ibfk_1` FOREIGN KEY (`recipeId`) REFERENCES `Recipe` (`recipeId`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
