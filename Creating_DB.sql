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

CREATE TABLE class (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    university VARCHAR(100),
    
    UNIQUE (class_name, university)
);

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
    action VARCHAR(255) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);