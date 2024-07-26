CREATE DATABASE IF NOT EXISTS Online_Assesment;

USE Online_Assesment;

CREATE TABLE IF NOT EXISTS Computer(
    id INT AUTO_INCREMENT PRIMARY KEY,
    question VARCHAR(255) NOT NULL,
    option1 VARCHAR(255) NOT NULL,
    option2 VARCHAR(255) NOT NULL,
    option3 VARCHAR(255) NOT NULL,
    option4 VARCHAR(255) NOT NULL,
    correct_option VARCHAR(255) NOT NULL,
    tag VARCHAR(50) NOT NULL
);


CREATE TABLE Teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);


CREATE TABLE Tests (
    test_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT,
    test_name VARCHAR(255) NOT NULL,
    Number_of_questions INT NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id)
);


CREATE TABLE IF NOT EXISTS Test_Questions(
    id INT AUTO_INCREMENT PRIMARY KEY,
    question VARCHAR(255) NOT NULL,
    option1 VARCHAR(255) NOT NULL,
    option2 VARCHAR(255) NOT NULL,
    option3 VARCHAR(255) NOT NULL,
    option4 VARCHAR(255) NOT NULL,
    correct_option VARCHAR(255) NOT NULL,
    tag VARCHAR(50) NOT NULL,
    test_id INT,
    FOREIGN KEY (test_id) REFERENCES Tests(test_id)
);
