CREATE TABLE IF NOT EXISTS `Users` (
	`user_id` integer primary key NOT NULL UNIQUE,
	`first_name` TEXT NOT NULL,
	`last_name` TEXT NOT NULL,
	`phone_number` INTEGER NOT NULL,
	`email` TEXT NOT NULL UNIQUE,
	`password` TEXT NOT NULL,
	`otp` TEXT,
	`otp_timestamp` REAL,
	`location` TEXT NOT NULL,
	`status` TEXT NOT NULL DEFAULT 'Inactive',
	`last_login` REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS `Products` (
	`product_id` integer primary key NOT NULL UNIQUE,
	`product_name` TEXT NOT NULL,
	`product_category` TEXT NOT NULL,
	`product_description` TEXT NOT NULL,
	`product_quantity` INTEGER NOT NULL,
	`product_cost` INTEGER NOT NULL,
	`retail_price` INTEGER NOT NULL,
	`user_id` INTEGER,
	`product_registration` TEXT NOT NULL,
	`product_location` TEXT NOT NULL,
	`location_description` TEXT,
	`status` TEXT NOT NULL DEFAULT 'Not sold',
FOREIGN KEY(`user_id`) REFERENCES `Users`(`user_id`)
);
CREATE TABLE IF NOT EXISTS `Orders` (
	`order_id` integer primary key NOT NULL UNIQUE,
	`product_id` INTEGER NOT NULL,
	`user_id` INTEGER NOT NULL,
	`employee_id` INTEGER NOT NULL,
	`fleet_id` INTEGER NOT NULL,
	`status` TEXT NOT NULL DEFAULT 'Stage 1',
	`order_timestamp` REAL NOT NULL,
FOREIGN KEY(`product_id`) REFERENCES `Products`(`product_id`),
FOREIGN KEY(`user_id`) REFERENCES `Users`(`user_id`),
FOREIGN KEY(`employee_id`) REFERENCES `Employees`(`employee_id`),
FOREIGN KEY(`fleet_id`) REFERENCES `Fleet`(`fleet_id`)
);
CREATE TABLE IF NOT EXISTS `Fleet` (
	`fleet_id` integer primary key NOT NULL UNIQUE,
	`registration_number` TEXT NOT NULL UNIQUE,
	`fleet_brand` TEXT NOT NULL,
	`fleet_model` TEXT NOT NULL,
	`fleet_category` TEXT NOT NULL,
	`registration_date` REAL NOT NULL,
	`employee_id` INTEGER NOT NULL,
	`fleet_mileage` INTEGER NOT NULL,
	`chassis_number` INTEGER NOT NULL,
	`cargo_type` TEXT NOT NULL,
	`max_capacity` INTEGER NOT NULL,
	`status` TEXT NOT NULL DEFAULT 'Inactive',
	`last_login` REAL NOT NULL,
FOREIGN KEY(`employee_id`) REFERENCES `Employees`(`employee_id`)
);
CREATE TABLE IF NOT EXISTS `Employees` (
	`employee_id` integer primary key NOT NULL UNIQUE,
	`first_name` TEXT NOT NULL,
	`last_name` TEXT NOT NULL,
	`phone_number` INTEGER NOT NULL,
	`email` TEXT NOT NULL UNIQUE,
	`password` TEXT NOT NULL,
	`otp` TEXT NOT NULL,
	`otp_timestamp` REAL NOT NULL,
	`location` TEXT NOT NULL,
	`role` TEXT NOT NULL DEFAULT 'Customer',
	`status` TEXT NOT NULL DEFAULT 'Inactive',
	`last_login` REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS `Reviews` (
	`review_id` integer primary key NOT NULL UNIQUE,
	`product_id` INTEGER NOT NULL,
	`text_review` TEXT NOT NULL,
	`ratings` INTEGER NOT NULL,
	`user_id` INTEGER NOT NULL,
	`review_timestamp` TEXT NOT NULL,
	`status` TEXT NOT NULL DEFAULT 'Not sold',
FOREIGN KEY(`product_id`) REFERENCES `Products`(`product_id`),
FOREIGN KEY(`user_id`) REFERENCES `Users`(`user_id`)
);