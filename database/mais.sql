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
