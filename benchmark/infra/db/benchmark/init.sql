CREATE DATABASE IF NOT EXISTS test_db;
GRANT ALL PRIVILEGES ON test_db.* TO 'test_user'@'%';
FLUSH PRIVILEGES;

-- 사용자 테이블 생성
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    mobile VARCHAR(20) NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE users_mobile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NULL,
    mobile VARCHAR(20) NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 트리거 생성
DELIMITER $$

CREATE TRIGGER update_is_admin_trigger
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    IF NEW.is_admin = True THEN
        SET mobile = '01012345678';
        IF EXISTS (SELECT * FROM users_mobile WHERE user_id = NEW.id and mobile is NULL) THEN
            UPDATE users_mobile SET mobile = '01012345678' WHERE user_id = NEW.id;
        ELSE
            INSERT INTO users_mobile (user_id, mobile) VALUES (NEW.id, '01012345678');
        END IF;
    END IF;
END$$

DELIMITER ;
