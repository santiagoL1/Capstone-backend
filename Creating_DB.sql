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


INSERT INTO TestNow_user (email, first_name, last_name, university, password_hash, username, last_login) VALUES
('whogenkamp3@gmail.com', 'Liam', 'Hogenkamp', 'Creighton University', 'pbkdf2_sha256$870000$Kp6G4N37zsNLhUvdfv2ujC$FrnkRczDn2U6Iu/s6RokpHG5PLaF40b1A9IeeZMUzNI=', 'whogenkamp', '2024-11-02 18:32:04');


INSERT INTO TestNow_user (email, first_name, last_name, university, password_hash, username, last_login) VALUES
('liam@gmail', 'Liam', 'Hogenkamp', 'Creighton University', 'pbkdf2_sha256$870000$Sb3B0n1dsN8Xrw4lQE1AlD$uLrLSN4GyIK26Gg5/NQBEEgopi6E0LXM1ZC11k2d3DI=', 'whogenkamp', '2024-11-07 21:54:21');

DELETE FROM TestNow_user;

Select * from TestNow_user;




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