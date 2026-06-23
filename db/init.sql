CREATE DATABASE IF NOT EXISTS `zekin`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE `zekin`;

CREATE TABLE IF NOT EXISTS `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(64) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `real_name` VARCHAR(64) NOT NULL,
  `role` VARCHAR(16) NOT NULL,
  `class_name` VARCHAR(64) NULL,
  `phone` VARCHAR(20) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_users_username` (`username`),
  UNIQUE KEY `uq_users_phone` (`phone`),
  KEY `ix_users_role` (`role`),
  KEY `ix_users_class_name` (`class_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `checkins` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `type` VARCHAR(24) NOT NULL,
  `content` TEXT NOT NULL,
  `photo_url` VARCHAR(500) NULL,
  `lat` FLOAT NULL,
  `lng` FLOAT NULL,
  `status` VARCHAR(24) NOT NULL DEFAULT 'pending',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_checkins_user_id` (`user_id`),
  KEY `ix_checkins_type` (`type`),
  KEY `ix_checkins_status` (`status`),
  KEY `ix_checkins_created_at` (`created_at`),
  CONSTRAINT `fk_checkins_user_id_users`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `reviews` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `checkin_id` INT NOT NULL,
  `reviewer_id` INT NOT NULL,
  `action` VARCHAR(24) NOT NULL,
  `comment` TEXT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_reviews_checkin_id` (`checkin_id`),
  KEY `ix_reviews_reviewer_id` (`reviewer_id`),
  KEY `ix_reviews_created_at` (`created_at`),
  CONSTRAINT `fk_reviews_checkin_id_checkins`
    FOREIGN KEY (`checkin_id`) REFERENCES `checkins` (`id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT `fk_reviews_reviewer_id_users`
    FOREIGN KEY (`reviewer_id`) REFERENCES `users` (`id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `users` (
  `id`,
  `username`,
  `password_hash`,
  `real_name`,
  `role`,
  `class_name`,
  `phone`
) VALUES
  (
    1,
    'admin_demo',
    '$2b$12$1A.nxUKK/i/1md5sneqO6e63QLO3P.iEsiPvMzQ1pq8elfjpn6SSC',
    '管理员',
    'admin',
    '校级',
    '13910000001'
  ),
  (
    2,
    'student_demo',
    '$2b$12$Yg2QA9TPzdjXH0PiEWSw8.yfr9avI3BtDaxgQD/kaDxA3ia.EVeFm',
    '王同学',
    'student',
    '软件一班',
    '13910000002'
  ),
  (
    3,
    'teacher_demo',
    '$2b$12$Q0HcVGDtfwlJ3UdQ5uSCbeKo46qgPXvGUEkP17QsEN4AW6ZBjWt1G',
    '华老师',
    'teacher',
    '软件一班',
    '13910000003'
  )
ON DUPLICATE KEY UPDATE
  `real_name` = VALUES(`real_name`),
  `role` = VALUES(`role`),
  `class_name` = VALUES(`class_name`),
  `phone` = VALUES(`phone`);

INSERT INTO `checkins` (
  `id`,
  `user_id`,
  `type`,
  `content`,
  `photo_url`,
  `lat`,
  `lng`,
  `status`
) VALUES
  (
    1,
    2,
    'dorm',
    '今天按时完成查寝打卡，宿舍情况正常。',
    'https://example.com/demo-dorm.jpg',
    30.2741,
    120.1551,
    'approved'
  ),
  (
    2,
    2,
    'class',
    '今天按时完成课堂打卡，出勤正常。',
    'https://example.com/demo-class.jpg',
    30.2741,
    120.1551,
    'pending'
  )
ON DUPLICATE KEY UPDATE
  `content` = VALUES(`content`),
  `photo_url` = VALUES(`photo_url`),
  `lat` = VALUES(`lat`),
  `lng` = VALUES(`lng`),
  `status` = VALUES(`status`);

INSERT INTO `reviews` (
  `id`,
  `checkin_id`,
  `reviewer_id`,
  `action`,
  `comment`
) VALUES
  (
    1,
    1,
    3,
    'approved',
    '记录完整，通过。'
  )
ON DUPLICATE KEY UPDATE
  `action` = VALUES(`action`),
  `comment` = VALUES(`comment`);
