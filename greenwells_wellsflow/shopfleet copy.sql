CREATE TABLE IF NOT EXISTS `Users` (
	`user_id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`first_name` text NOT NULL,
	`last_name` text NOT NULL,
	`phone_number` int NOT NULL,
	`email` varchar(255) NOT NULL UNIQUE,
	`password` text NOT NULL,
	`otp` text,
	`otp_timestamp` datetime,
	`location` text NOT NULL,
	`status` text NOT NULL DEFAULT 'Inactive',
	`last_login` datetime NOT NULL,
	PRIMARY KEY (`user_id`)
);

CREATE TABLE IF NOT EXISTS `1757008016` (

);

CREATE TABLE IF NOT EXISTS `Products` (
	`product_id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`product_name` text NOT NULL,
	`product_description` text NOT NULL,
	`product_quantity` int NOT NULL,
	`product_cost` int NOT NULL,
	`retail_price` int NOT NULL,
	`user_id` int,
	`product_registration` timestamp NOT NULL,
	`product_location` text NOT NULL,
	`location_description` text,
	`status` text NOT NULL DEFAULT 'Not sold',
	PRIMARY KEY (`product_id`)
);

CREATE TABLE IF NOT EXISTS `1757008021` (

);

CREATE TABLE IF NOT EXISTS `Orders` (
	`order_id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`product_id` int NOT NULL,
	`user_id` int NOT NULL,
	`employee_id` int NOT NULL,
	`fleet_id` int NOT NULL,
	`status` text NOT NULL DEFAULT 'Stage 1',
	`order_timestamp` datetime NOT NULL,
	PRIMARY KEY (`order_id`)
);

CREATE TABLE IF NOT EXISTS `Fleet` (
	`fleet_id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`registration_number` text NOT NULL UNIQUE,
	`fleet_brand` text NOT NULL,
	`fleet_model` text NOT NULL,
	`registration_date` datetime NOT NULL,
	`employee_id` int,
	`fleet_mileage` int NOT NULL,
	`chassis_number` int NOT NULL,
	`cargo_type` text NOT NULL,
	`max_capacity` int NOT NULL,
	`status` text NOT NULL DEFAULT 'Inactive',
	`last_login` datetime NOT NULL,
	PRIMARY KEY (`fleet_id`)
);

CREATE TABLE IF NOT EXISTS `Employees` (
	`employee_id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`first_name` text NOT NULL,
	`last_name` text NOT NULL,
	`phone_number` int NOT NULL,
	`email` varchar(255) NOT NULL UNIQUE,
	`password` text NOT NULL,
	`otp` text NOT NULL,
	`otp_timestamp` datetime NOT NULL,
	`location` text NOT NULL,
	`role` text NOT NULL DEFAULT 'Customer',
	`status` text NOT NULL DEFAULT 'Inactive',
	`last_login` datetime NOT NULL,
	PRIMARY KEY (`employee_id`)
);

CREATE TABLE IF NOT EXISTS `Reviews` (
	`review_id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`product_id` int NOT NULL,
	`text_review` text NOT NULL,
	`ratings` int NOT NULL,
	`user_id` int NOT NULL,
	`review_timestamp` timestamp NOT NULL,
	`status` text NOT NULL DEFAULT 'Not sold',
	PRIMARY KEY (`review_id`)
);



ALTER TABLE `Products` ADD CONSTRAINT `Products_fk6` FOREIGN KEY (`user_id`) REFERENCES `Users`(`user_id`);

ALTER TABLE `Orders` ADD CONSTRAINT `Orders_fk1` FOREIGN KEY (`product_id`) REFERENCES `Products`(`product_id`);

ALTER TABLE `Orders` ADD CONSTRAINT `Orders_fk2` FOREIGN KEY (`user_id`) REFERENCES `Users`(`user_id`);

ALTER TABLE `Orders` ADD CONSTRAINT `Orders_fk3` FOREIGN KEY (`employee_id`) REFERENCES `Employees`(`employee_id`);

ALTER TABLE `Orders` ADD CONSTRAINT `Orders_fk4` FOREIGN KEY (`fleet_id`) REFERENCES `Fleet`(`fleet_id`);
ALTER TABLE `Fleet` ADD CONSTRAINT `Fleet_fk5` FOREIGN KEY (`employee_id`) REFERENCES `Employees`(`employee_id`);

ALTER TABLE `Reviews` ADD CONSTRAINT `Reviews_fk1` FOREIGN KEY (`product_id`) REFERENCES `Products`(`product_id`);

ALTER TABLE `Reviews` ADD CONSTRAINT `Reviews_fk4` FOREIGN KEY (`user_id`) REFERENCES `Users`(`user_id`);