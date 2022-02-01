CREATE TABLE mais.USER(
    id int auto_increment NOT NULL PRIMARY KEY,
    email VARCHAR(50) NOT NULL,
    PASSWORD VARCHAR(64) NOT NULL,
    passphrase varchar(64) default NULL null
);

CREATE TABLE mais.IMAGE(
    id INT AUTO_INCREMENT PRIMARY KEY,
    image VARCHAR(50) NOT NULL,
    mac BLOB NOT NULL,
    user_id int NOT NULL,

    FOREIGN KEY (user_id) REFERENCES USER(id)
);

CREATE TABLE mais.WAV(
    id INT AUTO_INCREMENT PRIMARY KEY,
    voice VARCHAR(50) NOT NULL ,
    mac BLOB NOT NULL,
    user_id int NOT NULL,

    FOREIGN KEY (user_id) REFERENCES USER(id)
);

CREATE TABLE mais.RECORD(
    id INT AUTO_INCREMENT PRIMARY KEY,
    date VARCHAR(30) NOT NULL,
    status ENUM('FAILED', 'SUCCEEDED') NOT NULL,
    type ENUM('Face ID', 'Voice ID') NOT NULL,
    user_id int NOT NULL,

    FOREIGN KEY (user_id) REFERENCES USER(id)
);