SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(255) NOT NULL COMMENT '保存密码哈希值',
  `salt` VARCHAR(64) NOT NULL COMMENT '密码盐',
  `role` ENUM('NORMAL', 'ADMIN') NOT NULL DEFAULT 'NORMAL',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1:正常, 0:禁用',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `sessions` (
  `token` VARCHAR(128) NOT NULL,
  `user_id` INT NOT NULL,
  `expires_at` VARCHAR(40) NOT NULL,
  `created_at` VARCHAR(40) NOT NULL,
  PRIMARY KEY (`token`),
  CONSTRAINT `fk_sessions_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `detection_logs` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `username` VARCHAR(80) NOT NULL,
  `image_id` VARCHAR(80) NOT NULL,
  `original_filename` VARCHAR(255) NOT NULL,
  `detection_mode` VARCHAR(40) NOT NULL,
  `detection_mode_label` VARCHAR(80) NOT NULL,
  `models_used` TEXT NOT NULL,
  `total_count` INT NOT NULL,
  `risk_level` VARCHAR(40) NOT NULL,
  `risk_score` DOUBLE NOT NULL,
  `scene_type` VARCHAR(80) NOT NULL,
  `class_count` TEXT NOT NULL,
  `report` TEXT NOT NULL,
  `result_image_url` VARCHAR(255) NOT NULL,
  `result_json_url` VARCHAR(255) NOT NULL,
  `created_at` VARCHAR(40) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_detection_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS = 1;
