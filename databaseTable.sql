CREATE DATABASE referral_db;

USE referral_db;

CREATE TABLE users_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100),
    referral_code VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    disabled BOOLEAN DEFAULT FALSE
);

SELECT * FROM users_table;
SELECT disabled FROM users_table;

truncate TABLE users_table;
DROP TABLE users_table;



