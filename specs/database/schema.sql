-- ZeKin MVP Database Schema
-- Owner: 赵耀 | Version: 1.0 | 2026-06-22
-- MySQL 8.0+ utf8mb4

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS zekin DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE zekin;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录名，默认可与 phone 相同',
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(50) NOT NULL,
    role ENUM('student', 'teacher', 'admin') NOT NULL DEFAULT 'student',
    class_name VARCHAR(50) NULL COMMENT '学生班级；教师所管班级可扩展 teacher_classes 表',
    phone VARCHAR(20) NOT NULL UNIQUE,
    points INT NOT NULL DEFAULT 0 COMMENT 'Could: 积分体系',
    continuous_days INT NOT NULL DEFAULT 0 COMMENT 'Could: 连续打卡',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role (role),
    INDEX idx_class (class_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 打卡记录表
CREATE TABLE IF NOT EXISTS checkins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    checkin_type ENUM('dorm', 'class', 'internship') NOT NULL DEFAULT 'dorm',
    content TEXT NOT NULL,
    photo_url VARCHAR(500) NULL,
    latitude DECIMAL(10, 7) NULL,
    longitude DECIMAL(10, 7) NULL,
    location_valid TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'GPS 是否在白名单内',
    ai_status ENUM('pending', 'pass', 'fail') NOT NULL DEFAULT 'pending',
    teacher_status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_ai_status (ai_status),
    INDEX idx_teacher_status (teacher_status),
    UNIQUE KEY uk_user_type_date (user_id, checkin_type, (DATE(created_at)))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 审核记录表
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    checkin_id INT NOT NULL,
    reviewer_id INT NOT NULL,
    action ENUM('approved', 'rejected') NOT NULL,
    comment TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (checkin_id) REFERENCES checkins(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id),
    INDEX idx_checkin (checkin_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 课程表
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    teacher_id INT NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    weekday TINYINT NOT NULL COMMENT '1=周一, 7=周日',
    start_time TIME NOT NULL,
    location VARCHAR(200) NULL,
    semester VARCHAR(20) NULL,
    FOREIGN KEY (teacher_id) REFERENCES users(id),
    INDEX idx_class_weekday (class_name, weekday)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 打卡地点白名单
CREATE TABLE IF NOT EXISTS allowed_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location_type ENUM('dorm', 'class', 'internship') NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    radius INT NOT NULL DEFAULT 200 COMMENT '允许半径(米)',
    is_enabled TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'MVP 默认关闭强制校验',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 补签申请
CREATE TABLE IF NOT EXISTS makeup_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    checkin_type ENUM('dorm', 'class', 'internship') NOT NULL,
    target_date DATE NOT NULL,
    reason TEXT NOT NULL,
    status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
    reviewer_id INT NULL,
    review_comment TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (reviewer_id) REFERENCES users(id),
    INDEX idx_user_status (user_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 系统配置
CREATE TABLE IF NOT EXISTS system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value JSON NOT NULL,
    description VARCHAR(255) NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 默认配置：查寝时段
INSERT INTO system_config (config_key, config_value, description) VALUES
('dorm_checkin_window', '{"start": "22:00", "end": "23:00"}', '查寝打卡时段'),
('current_semester', '"2025-2026-2"', '当前学期')
ON DUPLICATE KEY UPDATE config_key = config_key;

SET FOREIGN_KEY_CHECKS = 1;
