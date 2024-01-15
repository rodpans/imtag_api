CREATE DATABASE IF NOT EXISTS Pictures;
USE Pictures;


CREATE TABLE IF NOT EXISTS pictures (
    id VARCHAR(36) PRIMARY KEY,
    path VARCHAR(255),
    date DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS tags (
    tag VARCHAR(32),
    picture_id VARCHAR(36),
    confidence DECIMAL(5, 2),
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tag, picture_id),
    FOREIGN KEY (picture_id) REFERENCES pictures(id)
);
