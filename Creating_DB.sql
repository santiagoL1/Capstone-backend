CREATE TABLE TestNow_groupflash (
	group_flash_id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT,
    set_id INT,
    
    FOREIGN KEY (group_id) REFERENCES TestNow_group(group_id),
    FOREIGN KEY (set_id) REFERENCES TestNow_flashcardset(set_id)
);

CREATE TABLE TestNow_group(
	group_id INT AUTO_INCREMENT PRIMARY KEY,
    members VARCHAR(255) NOT NULL UNIQUE,
	group_name VARCHAR(255) NOT NULL
);

INSERT INTO TestNow_group(members, group_name)
VALUES ('5', 'GROUP GOAT');

INSERT INTO TestNow_groupflash(group_id,set_id) 
VALUE(1,);

UPDATE TestNow_userclass
SET user_class_id = 1
WHERE user_class_id = 2;



SELECT * FROM TestNow_user;

SELECT * FROM TestNow_classtable;

SELECT * FROM TestNow_userclass;


CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    university VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    last_login DATETIME,
    
    CONSTRAINT chk_username_length CHECK (CHAR_LENGTH(username) >= 3)
);

SELECT * FROM user WHERE user_id = 7;



INSERT INTO TestNow_user 
    (email, first_name, last_name, university, password, username, last_login, is_active, is_staff, is_superuser) 
VALUES 
    ('generic@gmail.com', 'Joe', 'Davis', 'Hoe Town University', 'not_a_password', 'generic', NULL, TRUE, TRUE, TRUE);


DELETE FROM TestNow_user;
Select * from TestNow_classtable;
SELECT * FROM TestNow_userclass;
SELECT * FROM TestNow_flashcardset;

INSERT INTO TestNow_flashcardset (set_name, class_model_id, user_id) 
VALUE ('generic', 1,1);

INSERT INTO TestNow_userclass (class_model_id, user_id) 
VALUES (1,1);

INSERT INTO TestNow_classtable (class_name, university) 
VALUES ('Generic Class','NA');

INSERT INTO TestNow_classtable (class_id, class_name, university) 
VALUES (1,'BIA 484','Creighton');

INSERT INTO TestNow_userclass (class_model_id, user_id) 
VALUES (1,5);

SELECT * FROM TestNow_classtable;

SELECT * FROM TestNow_userclass;

Select * from TestNow_activitylog;



ALTER TABLE user AUTO_INCREMENT = 1;
select * from user;

select * from TestNow_user;
'pbkdf2_sha256$870000$eVH9KqsPlyZg8bOOCnjB93$b0bhMzbs9DjH9aPu+pVbDL8/RRIoHZOwdmzvNQO2jH0='
'pbkdf2_sha256$870000$eVH9KqsPlyZg8bOOCnjB93$b0bhMzbs9DjH9aPu+pVbDL8/RRIoHZOwdmzvNQO2jH0='

CREATE TABLE class (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    university VARCHAR(100),
    
    UNIQUE (class_name, university)
);

INSERT INTO class (class_id, class_name, university) VALUES
('BIA 330', 'Creighton University');

CREATE TABLE user_class (
    user_class_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    class_id INT,
    
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (class_id) REFERENCES class(class_id)
);

CREATE TABLE flash_cards_set (
    set_id INT AUTO_INCREMENT PRIMARY KEY,
    set_name VARCHAR(100) NOT NULL,
    class_id INT,
    user_id INT,
    
    FOREIGN KEY (class_id) REFERENCES class(class_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE flash_cards (
    card_id INT AUTO_INCREMENT PRIMARY KEY,
    set_id INT,
    question VARCHAR(255) NOT NULL,
    answer VARCHAR(255) NOT NULL,
    
    FOREIGN KEY (set_id) REFERENCES flash_cards_set(set_id)
);

CREATE TABLE activity_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action_done VARCHAR(255) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);