


-- Active: 1682022069673@@phase2-6.cpqmwccqu44e.us-east-1.rds.amazonaws.com@3306@university


DROP DATABASE IF EXISTS university;
CREATE DATABASE university;

SET FOREIGN_KEY_CHECKS=0;
use university;
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`(
    `id`                INT(8) UNSIGNED ZEROFILL NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `type`              ENUM('sysadmin', 'gs', 'student', 'alum', 'applicant', 'faculty') NOT NULL,
    `email`             VARCHAR(50),
    `username`          VARCHAR(50) UNIQUE,
    `password`          VARCHAR(50),
    `first_name`        VARCHAR(50) NOT NULL,
    `last_name`         VARCHAR(50) NOT NULL,
    `street_address`    VARCHAR(50),
    `city`              VARCHAR(50),
    `state`             VARCHAR(2),
    `zip`               VARCHAR(5)
);

DROP TABLE IF EXISTS `course`; 
CREATE TABLE course(
    ID int NOT NULL AUTO_INCREMENT,
    department ENUM('CSCI','ECE','MATH') NOT NULL,
    cnumber INTEGER,
    title VARCHAR(50),
    credits INTEGER,
    day CHARACTER,
    year YEAR,
    required_masters  TINYINT(1) NOT NULL,
    semester CHARACTER,
    -- 1 = 3:00-5:30, 2 = 4:00-6:30, 3 = 6:00-8:30, 4 = 3:30-6:00
    time INTEGER,
    section INTEGER,
    location VARCHAR(50),
    capacity INTEGER,
    professor INT(8) UNSIGNED ZEROFILL NULL,
    primary key (ID),
    FOREIGN KEY (professor) REFERENCES user(id)
); 

DROP TABLE IF EXISTS `course_prereq`;
CREATE TABLE `course_prereq`(
    `course_id`     INT NOT NULL,
    `prereq_id`     INT NOT NULL,
    PRIMARY KEY     (`course_id`, `prereq_id`),
    FOREIGN KEY     (`course_id`) REFERENCES `course`(`id`)
                    ON DELETE CASCADE,
    FOREIGN KEY     (`prereq_id`) REFERENCES `course`(`id`)
                    ON DELETE CASCADE
);

DROP TABLE IF EXISTS `student_courses_planned`;
CREATE TABLE `student_courses_planned`(
    `user_id`       INT UNSIGNED NOT NULL,
    `course_id`     INT NOT NULL,
    PRIMARY KEY     (`user_id`, `course_id`),
    FOREIGN KEY     (`user_id`) REFERENCES `user`(`id`)
                    ON DELETE CASCADE,
    FOREIGN KEY     (`course_id`) REFERENCES `course`(`id`)
                    ON DELETE CASCADE
);

-- applications
DROP TABLE IF EXISTS applications;
CREATE TABLE applications (
    app_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    UID INT(8) UNSIGNED ZEROFILL NOT NULL,
    SSN VARCHAR(15) UNIQUE,
    DegreeSought VARCHAR(255),
    AdmissionDate TEXT,
    PriorDegrees VARCHAR (255),
    Status VARCHAR(255),
    rec_letter VARCHAR(255),
    Degree VARCHAR(255),
    YearOfGraduation YEAR,
    GPA FLOAT,
    University VARCHAR(255),
    VerbalScore INT,
    QuantitativeScore INT,
    TotalScore INT,
    Experience TEXT,
    TranscriptReceivedStatus BOOLEAN,
    TranscriptSentStatus BOOLEAN,
    Payment BOOLEAN,
    FOREIGN KEY (uid) REFERENCES user(id)
);

DROP TABLE IF EXISTS RecommendationLetters;
CREATE TABLE RecommendationLetters (
    
    ID INT UNSIGNED NOT NULL,
    LetterWriterName VARCHAR(255),
    LetterWriterEmail VARCHAR(255),
    LetterWriterTitle VARCHAR(255),
    LetterWriterAffiliation VARCHAR(255),
    LetterRequestEmailSentStatus BOOLEAN,
    LetterReceivedStatus BOOLEAN,
    RecommendationRating INT,
    GenericRating BOOLEAN,
    CredibilityRating BOOLEAN,
    RecommendationComments TEXT,
    FOREIGN KEY (ID) REFERENCES user (ID)
);


DROP TABLE IF EXISTS ReviewForms;
CREATE TABLE ReviewForms (
    ID INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    ReviewerID INT UNSIGNED,
    ReviewerComments TEXT,
    RecommendationRating INT,
    RecommendedAdvisor TEXT,
    FOREIGN KEY (ReviewerID) REFERENCES user (id)
);


-- degree_requirements
DROP TABLE IF EXISTS `degree_requirements`;
CREATE TABLE `degree_requirements`(
    `program`       ENUM('masters', 'phd') NOT NULL,
    `requirement`   ENUM('min_gpa', 'min_credit_hours', 'most_non_cs_courses', 'min_cs_credit_hours', 'most_below_b_grades', 'thesis_passed') NOT NULL,
    `value`        FLOAT(4,2) NOT NULL,
    PRIMARY KEY     (`program`, `requirement`)
);

-- student_courses
DROP TABLE IF EXISTS `student_courses`;
CREATE TABLE `student_courses`(
    `user_id`       INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `course_id`     INT NOT NULL,
    `semester`      ENUM('fall', 'spring', 'summer') NOT NULL,
    `year`          YEAR NOT NULL DEFAULT (YEAR(CURDATE())),
    `grade`         ENUM('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F', 'IP') NOT NULL DEFAULT 'IP',
    PRIMARY KEY     (`user_id`, `course_id`),
    FOREIGN KEY     (`user_id`) REFERENCES `user`(`id`)
                    ON DELETE CASCADE,
    FOREIGN KEY     (`course_id`) REFERENCES `course`(`id`)
                    ON DELETE CASCADE
);
-- student_info
DROP TABLE IF EXISTS student_info;
CREATE TABLE `student_info`(
    `user_id`           INT UNSIGNED NOT NULL PRIMARY KEY,
    `admit_year`        YEAR NOT NULL DEFAULT (YEAR(CURDATE())),
    `program`           ENUM('masters','phd'),
    `advisor_id`        INT UNSIGNED,
    `grad_status`       ENUM('pending', 'cleared') NOT NULL DEFAULT 'pending',
    `thesis_passed`     TINYINT(1) NOT NULL DEFAULT 0,
    `form_approved`     TINYINT(1) NOT NULL DEFAULT 0,
    `grad_semester`     ENUM('fall', 'spring', 'summer') NOT NULL,
    `grad_year`         YEAR NOT NULL DEFAULT (YEAR(CURDATE()) + 1),
    FOREIGN KEY         (`user_id`) REFERENCES `user`(`id`)
                        ON DELETE CASCADE,
    FOREIGN KEY         (`advisor_id`) REFERENCES `user`(`id`)
                        ON DELETE SET NULL
);

--alumni info 
DROP TABLE IF EXISTS `alumni_info`;
CREATE TABLE `alumni_info`(
    `user_id`           INT UNSIGNED NOT NULL PRIMARY KEY,
    `program`           ENUM('masters','phd'),
    `grad_year`         YEAR NOT NULL DEFAULT (YEAR(CURDATE())),
    FOREIGN KEY         (`user_id`) REFERENCES `user`(`id`)
                        ON DELETE CASCADE
);

DROP TABLE IF EXISTS `faculty_info`;
CREATE TABLE `faculty_info`(
    `user_id`               INT UNSIGNED NOT NULL PRIMARY KEY,
    `department`            ENUM('CSCI','ECE','MATH'),
    `is_advisor`            TINYINT(1) NOT NULL DEFAULT 0,
    `is_reviewer`           TINYINT(1) NOT NULL DEFAULT 0,
    `is_instructor`         TINYINT(1) NOT NULL DEFAULT 0,
    `is_admissions_chair`   TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY             (`user_id`) REFERENCES `user`(`id`)
                            ON DELETE CASCADE
);

DROP TABLE IF EXISTS `privateMessages`;
CREATE TABLE privateMessages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT(8) UNSIGNED ZEROFILL NOT NULL,
    recipient_id INT(8) UNSIGNED ZEROFILL NOT NULL,
    message VARCHAR(250) NOT NULL,
    date DATETIME NOT NULL,
    time DATETIME NOT NULL,
    CID INT NOT NULL,
    FOREIGN KEY (sender_id) REFERENCES user(id),
    FOREIGN KEY (recipient_id) REFERENCES user(id),
    FOREIGN KEY (CID) REFERENCES course(ID)
);
DROP TABLE IF EXISTS `ratings`;
CREATE TABLE ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT(8) UNSIGNED ZEROFILL NOT NULL,
    professor_id INT(8) UNSIGNED ZEROFILL,
    course_id INT,
    rating INT NOT NULL,
    comment TEXT,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (professor_id) REFERENCES user (id),
    FOREIGN KEY (course_id) REFERENCES course (ID)
);


DROP TABLE IF EXISTS `alumni_messages`;
CREATE TABLE `alumni_messages`(
    `user_id`        INT UNSIGNED NOT NULL,
    `identity`       VARCHAR(50),
    `message`        VARCHAR(100),
    `message_time`   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY      (`user_id`, `message_time`),
    FOREIGN KEY      (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
    FOREIGN KEY      (`identity`) REFERENCES `user`(`username`) ON DELETE CASCADE
);


-- Insert users
INSERT INTO `user` (`type`, `email`, `username`, `password`, `id`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`) VALUES ('student', 'paulmccartney@gmail.com', 'paul', '123', '55555555', 'Paul', 'McCartney', '123 Main St', 'New York', 'NY', '10001');
INSERT INTO `user` (`type`, `email`, `username`, `password`, `id`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`) VALUES ('student', 'georgeharrison@gmail.com', 'george', '123', '66666666', 'George', 'Harrison', '123 Main St', 'New York', 'NY', '10001');
INSERT INTO `user` (`type`, `email`, `username`, `password`, `id`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`) VALUES ('student', 'ringostarr@gmail.com', 'ringo', '123', '87654321', 'Ringo', 'Starr', '123 Main St', 'New York', 'NY', '10001');
INSERT INTO `user` (`type`, `email`, `username`, `password`, `id`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`) VALUES ('alum', 'ericclapton@gmail.com', 'eric', '123', '77777777', 'Eric', 'Clapton', '123 Main St', 'New York', 'NY', '10001');
INSERT INTO `user` (`type`, `email`, `username`, `password`, `id`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`) VALUES ('gs', 'erichcast@gmail.com', 'erich', '123', '12345678', 'Erich', 'Cast', '123 Main St', 'New York', 'NY', '10001');

INSERT INTO `user` (`type`, `email`, `username`, `password`, `id`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`) VALUES ('faculty', 'parmer@gwu.edu', 'parmer', '123', '33333333', 'Gabe', 'Parmer', '123 Main St', 'New York', 'NY', '10001');
INSERT INTO `user` (`type`, `email`, `username`, `password`, `id`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`) VALUES ('sysadmin', 'jrt@gwu.edu', 'james', '123', '44444444', 'James', 'Taylor', '123 Main St', 'New York', 'NY', '10001');
INSERT INTO `user` (`type`, `email`, `username`, `password`, `id`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`) VALUES ('applicant', 'ringostarr2@gmail.com', 'ringo2', '123', '87654322', 'Ringo', 'Starr', '123 Main St', 'New York', 'NY', '10001');

INSERT INTO `user` (`type`, `email`, `username`, `password`, `id`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`) VALUES ('alum', 'test@gwu.edu', 'kurt', '123', '12345679', 'Kurt', 'Cobain', '123 Main St', 'New York', 'NY', '10001');


INSERT INTO `user` (`type`, `email`, `username`, `password`, `id`, `first_name`, `last_name`, `street_address`, `city`, `state`, `zip`) VALUES ('applicant', 'jlennon@gwu.edu', 'jlennon', '123', '12312312', 'John', 'Lennon', '123 Main St', 'New York', 'NY', '10001');
-- Insert data into the 'user' table
INSERT INTO `user` (`id`, `type`, `email`, `username`, `password`, `first_name`, `last_name`)
VALUES 
(88888888, 'student', 'billie.holiday@example.com', 'holiday', '123', 'Billie', 'Holiday'),
(99999999, 'student', 'diana.krall@example.com', 'krall', '123', 'Diana', 'Krall'),
(10000001, 'gs', 'jamie.parker@example.com', 'parker', '123', 'Jamie', 'Parker'),
(22222222, 'faculty', 'narahari@example.com', 'narahari', '123', 'Narahari', 'LastNameN'),
(10000003, 'faculty', 'choi@example.com', 'choi', '123', 'Choi', 'LastNameC');

-- Insert data into the 'course' table

INSERT INTO course (department, cnumber, title, credits, day, year, required_masters, semester, time, section, location, capacity, professor) VALUES
('CSCI', 6221, 'SW Paradigms', 3, 'M', 2023, 1, 'S', 2, 1, 'SEH', 40, NULL),
('CSCI', 6461, 'Computer Architecture', 3, 'T', 2023, 1, 'S', 2, 1, 'SEH', 40, NULL),
('CSCI', 6212, 'Algorithms', 3, 'W', 2023, 1, 'S', 1, 1, 'SEH', 40, NULL),
('CSCI', 6220, 'Machine Learning', 3, 'R', 2023, 0, 'S', 2, 1, 'SEH', 40, NULL),
('CSCI', 6232, 'Networks 1', 3, 'M', 2023, 0, 'S', 3, 1, 'SEH', 40, NULL),
('CSCI', 6233, 'Networks 2', 3, 'T', 2023, 0, 'S', 3, 1, 'SEH', 40, NULL),
('CSCI', 6241, 'Database 1', 3, 'W', 2023, 0, 'S', 3, 1, 'SEH', 40, NULL),
('CSCI', 6242, 'Database 2', 3, 'R', 2023, 0, 'S', 3, 1, 'SEH', 40, NULL),
('CSCI', 6246, 'Compilers', 3, 'T', 2023, 0, 'S', 1, 1, 'SEH', 40, NULL),
('CSCI', 6260, 'Multimedia', 3, 'R', 2023, 0, 'S', 3, 1, 'SEH', 40, NULL),
('CSCI', 6251, 'Cloud Computing', 3, 'M', 2023, 0, 'S', 3, 1, 'SEH', 40, NULL),
('CSCI', 6254, 'SW Engineering', 3, 'M', 2023, 0, 'S', 4, 1, 'SEH', 40, NULL),
('CSCI', 6262, 'Graphics 1', 3, 'W', 2023, 0, 'S', 3, 1, 'SEH', 40, NULL),
('CSCI', 6283, 'Security 1', 3, 'T', 2023, 0, 'S', 3, 1, 'SEH', 40, NULL),
('CSCI', 6284, 'Cryptography', 3, 'M', 2023, 0, 'S', 3, 1, 'SEH', 40, NULL),
('CSCI', 6286, 'Network Security', 3, 'W', 2023, 0, 'S', 3, 1, 'SEH', 40, NULL),
('CSCI', 6325, 'Algorithms 2', 3, 'W', 2023, 0, 'S', 1, 1, 'SEH', 40, NULL),
('CSCI', 6339, 'Embedded Systems', 3, 'R', 2023, 0, 'S', 2, 1, 'SEH', 40, NULL),
('CSCI', 6384, 'Cryptography 2', 3, 'W', 2023, 0, 'S', 1, 1, 'SEH', 40, NULL),
('ECE', 6241, 'Communication Theory', 3, 'M', 2023, 0, 'S', 3, 1, 'SEH', 40, NULL),
('ECE', 6242, 'Information Theory', 2, 'T', 2023, 0, 'S', 3, 1, 'SEH', 40, NULL),
('MATH', 6210, 'Logic', 2, 'W', 2023, 0, 'S', 3, 0, 'SEH', 40, NULL);


-- Insert course_prereq
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (6, 5);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (8, 7);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (9, 2);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (9, 3);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (11, 2);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (12, 1);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (14, 3);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (15, 3);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (16, 14);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (16, 5);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (17, 3);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (18, 2);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (18, 3);
INSERT INTO `course_prereq` (`course_id`, `prereq_id`) VALUES (19, 15);


-- Insert applications
INSERT INTO `applications` (`app_id`, `uid`, `SSN`, `DegreeSought`, `AdmissionDate`, `PriorDegrees`, `Status`, `rec_letter`) VALUES
(1, 12312312, '111-11-1111', 'masters', 'Summer 2023', 'Bachelors', 'complete', 'rec@gmail.com');
INSERT INTO `applications` (`app_id`, `uid`, `SSN`, `DegreeSought`, `AdmissionDate`, `PriorDegrees`, `Status`, `rec_letter`) VALUES
(2, 87654322, '222-11-1111', 'masters', 'Summer 2023', 'Bachelors', 'incomplete', 'rec@gmail.com');

-- Insert degree_requirements
INSERT INTO `degree_requirements` VALUES ('masters', 'min_gpa', 3.0);
INSERT INTO `degree_requirements` VALUES ('masters', 'min_credit_hours', 30);
INSERT INTO `degree_requirements` VALUES ('masters', 'most_non_cs_courses', 2);
INSERT INTO `degree_requirements` VALUES ('masters', 'most_below_b_grades', 2);
INSERT INTO `degree_requirements` VALUES ('phd', 'min_gpa', 3.5);
INSERT INTO `degree_requirements` VALUES ('phd', 'min_credit_hours', 36);
INSERT INTO `degree_requirements` VALUES ('phd', 'min_cs_credit_hours', 30);
INSERT INTO `degree_requirements` VALUES ('phd', 'most_below_b_grades', 1);
INSERT INTO `degree_requirements` VALUES ('phd', 'thesis_passed', 1);

-- Insert student_courses
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('55555555', '1', 'fall', '2020', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('55555555', '3', 'spring', '2021', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('55555555', '2', 'fall', '2020', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('55555555', '5', 'fall', '2021', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('55555555', '6', 'spring', '2022', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('55555555', '7', 'fall', '2020', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('55555555', '9', 'spring', '2021', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('55555555', '13', 'fall', '2020', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('55555555', '14', 'fall', '2021', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('55555555', '8', 'spring', '2022', 'B');

INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('66666666', '21', 'spring', '2022', 'C');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('66666666', '1', 'spring', '2022', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('66666666', '2', 'spring', '2022', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('66666666', '3', 'spring', '2022', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('66666666', '5', 'spring', '2022', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('66666666', '6', 'spring', '2022', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('66666666', '7', 'spring', '2022', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('66666666', '8', 'spring', '2022', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('66666666', '14', 'spring', '2022', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('66666666', '15', 'spring', '2022', 'B');

INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('87654321', '1', 'spring', '2022', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('87654321', '2', 'spring', '2022', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('87654321', '3', 'spring', '2022', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('87654321', '4', 'spring', '2022', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('87654321', '5', 'spring', '2022', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('87654321', '6', 'spring', '2022', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('87654321', '7', 'spring', '2022', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('87654321', '8', 'spring', '2022', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('87654321', '9', 'spring', '2022', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('87654321', '10', 'spring', '2022', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('87654321', '11', 'spring', '2022', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('87654321', '12', 'spring', '2022', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('77777777', '1', 'spring', '2022', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('77777777', '3', 'spring', '2022', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('77777777', '2', 'spring', '2022', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('77777777', '5', 'spring', '2022', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('77777777', '6', 'spring', '2022', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('77777777', '7', 'spring', '2022', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('77777777', '8', 'spring', '2022', 'B');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('77777777', '14', 'spring', '2022', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('77777777', '15', 'spring', '2022', 'A');
INSERT INTO `student_courses` (`user_id`, `course_id`, `semester`, `year`, `grade`) VALUES ('77777777', '16', 'spring', '2022', 'A');

-- Insert student_info
INSERT INTO `student_info` (`user_id`, `program`, `advisor_id`, `grad_semester`, `grad_year`) VALUES ('55555555', 'masters', '22222222', 'fall', '2023');
INSERT INTO `student_info` (`user_id`, `program`, `advisor_id`, `grad_semester`, `grad_year`) VALUES ('66666666', 'masters', '33333333', 'fall', '2023');
INSERT INTO `student_info` (`user_id`, `program`, `advisor_id`, `grad_semester`, `grad_year`) VALUES ('87654321', 'phd', '22222222', 'fall', '2023');


-- Insert alumni_info
INSERT INTO `alumni_info` (`user_id`, `program`, `grad_year`) VALUES ('77777777', 'masters', '2014');
INSERT INTO `alumni_info` (`user_id`, `program`, `grad_year`) VALUES ('12345679', 'masters', '2017');

--Insert faculty_info
INSERT INTO `faculty_info` (`user_id`, `department`, `is_advisor`, `is_reviewer`, `is_instructor`) VALUES ('22222222', 'CSCI', 1, 1, 1);
INSERT INTO `faculty_info` (`user_id`, `department`, `is_reviewer`, `is_admissions_chair`, `is_advisor`) VALUES ('33333333','CSCI', 1, 1, 1);
INSERT INTO `student_info` (`user_id`, `admit_year`, `program`, `advisor_id`, `grad_status`, `thesis_passed`, `form_approved`, `grad_semester`, `grad_year`)
VALUES 
(88888888, 2021, 'masters', NULL, 'pending', 0, 0, 'spring', 2023),
(99999999, 2022, 'masters', NULL, 'pending', 0, 0, 'spring', 2024);

INSERT INTO `faculty_info` (`user_id`, `department`, `is_advisor`, `is_reviewer`, `is_instructor`, `is_admissions_chair`)
VALUES (10000003, 'CSCI', 0, 0, 1, 0);
