/*
 Navicat Premium Data Transfer

 Source Server         : MySQL
 Source Server Type    : MySQL
 Source Server Version : 90400 (9.4.0-commercial)
 Source Host           : localhost:3306
 Source Schema         : drone-detection-sql

 Target Server Type    : MySQL
 Target Server Version : 90400 (9.4.0-commercial)
 File Encoding         : UTF-8

 Date: 14/06/2026 13:28:48
 Description: 去除额度与 Pro 角色后的数据库结构与数据
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for detection_logs
-- ----------------------------
DROP TABLE IF EXISTS `detection_logs`;
CREATE TABLE `detection_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `username` varchar(80) NOT NULL,
  `image_id` varchar(80) NOT NULL,
  `original_filename` varchar(255) NOT NULL,
  `detection_mode` varchar(40) NOT NULL,
  `detection_mode_label` varchar(80) NOT NULL,
  `models_used` text NOT NULL,
  `total_count` int NOT NULL,
  `risk_level` varchar(40) NOT NULL,
  `risk_score` double NOT NULL,
  `scene_type` varchar(80) NOT NULL,
  `class_count` text NOT NULL,
  `report` text NOT NULL,
  `result_image_url` varchar(255) NOT NULL,
  `result_json_url` varchar(255) NOT NULL,
  `created_at` varchar(40) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_detection_logs_user` (`user_id`),
  CONSTRAINT `fk_detection_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for sessions
-- ----------------------------
DROP TABLE IF EXISTS `sessions`;
CREATE TABLE `sessions` (
  `token` varchar(128) NOT NULL,
  `user_id` int NOT NULL,
  `expires_at` varchar(40) NOT NULL,
  `created_at` varchar(40) NOT NULL,
  PRIMARY KEY (`token`),
  KEY `fk_sessions_user` (`user_id`),
  CONSTRAINT `fk_sessions_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `salt` varchar(64) NOT NULL DEFAULT '',
  `role` enum('NORMAL','ADMIN') DEFAULT 'NORMAL',
  `status` tinyint DEFAULT '1' COMMENT '1:正常, 0:禁用',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of users
-- ----------------------------
BEGIN;
INSERT INTO `users` (`id`, `username`, `password`, `salt`, `role`, `status`, `created_at`, `updated_at`) VALUES (4, 'admin', '03247a396323f3f61ae8c45ef702c5e02ddb8c89903b4e9ad1c40b8450776773', '445bc1dbe3f0a9aa2fb94c21151d9a9b', 'ADMIN', 1, '2026-06-12 16:14:06', '2026-06-14 11:22:09');
INSERT INTO `users` (`id`, `username`, `password`, `salt`, `role`, `status`, `created_at`, `updated_at`) VALUES (5, 'normal_user', '64107cc96535376fe74afa095d028b1c7d365077310cd4b3179cfe7bf022a5da', '15ef6b80ceeeff8d845e9b492b62e92b', 'NORMAL', 1, '2026-06-14 05:05:34', '2026-06-14 05:06:30');
COMMIT;

-- ----------------------------
-- Records of sessions
-- ----------------------------
BEGIN;
INSERT INTO `sessions` (`token`, `user_id`, `expires_at`, `created_at`) VALUES ('17Wm02seiHXM25oOWb842cY8XfZPlmkDdITaiZQJtR0', 4, '2026-06-14T15:22:19.845097+00:00', '2026-06-14T03:22:19.845097+00:00');
INSERT INTO `sessions` (`token`, `user_id`, `expires_at`, `created_at`) VALUES ('7DI-04Ek-hJ-xfr42kk78Og4yIaUlY_0Q1mU_hOUlFc', 4, '2026-06-14T15:22:27.845878+00:00', '2026-06-14T03:22:27.845878+00:00');
INSERT INTO `sessions` (`token`, `user_id`, `expires_at`, `created_at`) VALUES ('Fvh-P3konmmcKgO7UJybshPh0ZGaAPJA3945jxOiCAQ', 4, '2026-06-14T17:06:23.256138+00:00', '2026-06-14T05:06:23.256138+00:00');
INSERT INTO `sessions` (`token`, `user_id`, `expires_at`, `created_at`) VALUES ('gyannHB8XgtSKFFF-9j1ezhql6SMLrE4NRZmavBKIOA', 4, '2026-06-14T15:22:17.238171+00:00', '2026-06-14T03:22:17.238171+00:00');
INSERT INTO `sessions` (`token`, `user_id`, `expires_at`, `created_at`) VALUES ('kRui2_SaIRDIhFPfDx4EVA6rN7BzeS1swdqUI8RwqWs', 4, '2026-06-14T15:24:37.237919+00:00', '2026-06-14T03:24:37.237919+00:00');
INSERT INTO `sessions` (`token`, `user_id`, `expires_at`, `created_at`) VALUES ('LteZEoZgXzlkh_oON6V4Py1LWXTOEXehksTL2cdWBiU', 4, '2026-06-14T15:24:57.859716+00:00', '2026-06-14T03:24:57.859716+00:00');
INSERT INTO `sessions` (`token`, `user_id`, `expires_at`, `created_at`) VALUES ('rNvzIpNU0N3xZGnl17m2lYJj1GCjnBVbe0oT0NYzBxQ', 4, '2026-06-14T15:22:20.580854+00:00', '2026-06-14T03:22:20.580854+00:00');
COMMIT;

-- ----------------------------
-- Records of detection_logs
-- ----------------------------
BEGIN;
INSERT INTO `detection_logs` (`id`, `user_id`, `username`, `image_id`, `original_filename`, `detection_mode`, `detection_mode_label`, `models_used`, `total_count`, `risk_level`, `risk_score`, `scene_type`, `class_count`, `report`, `result_image_url`, `result_json_url`, `created_at`) VALUES (1, 4, 'admin', '5ab4cfd0-c728-4ff8-8e0e-044ffc029bf4', '0000006_01111_d_0000003.jpg', 'fusion', '粗细粒度融合检测', '[\"scene\", \"visdrone\"]', 24, '高风险', 90, '交通车辆密集场景', '{\"tree\": 3, \"road_area\": 2, \"car\": 12, \"truck\": 2, \"pedestrian\": 1, \"motor\": 3, \"people\": 1}', '本次采用粗细粒度融合检测，共检测到 24 个目标。其中场景要素 5 个，细粒度目标 19 个。其中数量最多的类别为 car，共 12 个。融合去重后剔除了 1 个重复目标。综合判断，该图像属于交通车辆密集场景。系统识别到 24 个目标，主要场景标签包括：道路区域、车辆活动、植被覆盖。当前综合风险等级为高风险，车辆越界异常：严重异常；道路交通密度异常：中度异常。', '/results/5ab4cfd0-c728-4ff8-8e0e-044ffc029bf4_result.jpg', '/results/5ab4cfd0-c728-4ff8-8e0e-044ffc029bf4_result.json', '2026-06-14T03:59:34.254866+00:00');
INSERT INTO `detection_logs` (`id`, `user_id`, `username`, `image_id`, `original_filename`, `detection_mode`, `detection_mode_label`, `models_used`, `total_count`, `risk_level`, `risk_score`, `scene_type`, `class_count`, `report`, `result_image_url`, `result_json_url`, `created_at`) VALUES (2, 4, 'admin', '97a2652f-ea06-45b1-b5fd-1231d90e480d', '0000006_03636_d_0000009.jpg', 'fusion', '粗细粒度融合检测', '[\"scene\", \"visdrone\"]', 12, '正常', 12.9, '城市道路巡检场景', '{\"road_area\": 2, \"tree\": 1, \"building\": 1, \"truck\": 7, \"pedestrian\": 1}', '本次采用粗细粒度融合检测，共检测到 12 个目标。其中场景要素 4 个，细粒度目标 8 个。其中数量最多的类别为 truck，共 7 个。综合判断，该图像属于城市道路巡检场景。系统识别到 12 个目标，主要场景标签包括：道路区域、车辆活动、建筑区域、植被覆盖。当前综合风险等级为正常，各异常模块暂未发现明显风险。', '/results/97a2652f-ea06-45b1-b5fd-1231d90e480d_result.jpg', '/results/97a2652f-ea06-45b1-b5fd-1231d90e480d_result.json', '2026-06-14T04:27:08.930570+00:00');
INSERT INTO `detection_logs` (`id`, `user_id`, `username`, `image_id`, `original_filename`, `detection_mode`, `detection_mode_label`, `models_used`, `total_count`, `risk_level`, `risk_score`, `scene_type`, `class_count`, `report`, `result_image_url`, `result_json_url`, `created_at`) VALUES (3, 4, 'admin', '36a33232-1136-4fa0-bc68-2f87910b68a6', '53902-476396222.mp4', 'fusion', '粗细粒度融合检测', '[\"scene\", \"visdrone\"]', 25, '低风险', 42.3, '交通车辆密集场景', '{\"road_area\": 3, \"tree\": 7, \"car\": 28, \"bus\": 3, \"truck\": 2, \"pedestrian\": 1, \"van\": 1}', '本次采用粗细粒度融合检测，视频抽帧共尝试 1 轮，选中第 29 帧，共检测到 25 个目标。其中场景要素 9 个，细粒度目标 16 个。其中数量最多的类别为 car，共 28 个。融合去重后剔除了 1 个重复目标。综合判断，该图像属于交通车辆密集场景。系统识别到 25 个目标，主要场景标签包括：道路区域、车辆活动、植被覆盖。当前综合风险等级为低风险，车辆越界异常：轻微异常；道路交通密度异常：轻微异常。 视频多帧投票共参考 3 帧，稳定类别包括：bus、car、road_area、tree、truck。 短时序跟踪发现 5 条车辆轨迹连续贴近道路边缘，存在疑似越界或靠边停留风险。', '/results/36a33232-1136-4fa0-bc68-2f87910b68a6_result.jpg', '/results/36a33232-1136-4fa0-bc68-2f87910b68a6_result.json', '2026-06-14T04:27:51.627641+00:00');
INSERT INTO `detection_logs` (`id`, `user_id`, `username`, `image_id`, `original_filename`, `detection_mode`, `detection_mode_label`, `models_used`, `total_count`, `risk_level`, `risk_score`, `scene_type`, `class_count`, `report`, `result_image_url`, `result_json_url`, `created_at`) VALUES (4, 4, 'admin', 'fc287909-aff5-4cbf-bf44-11982b63bc94', '0000006_02616_d_0000007.jpg', 'fusion', '粗细粒度融合检测', '[\"scene\", \"visdrone\"]', 19, '低风险', 26.1, '交通车辆密集场景', '{\"tree\": 1, \"road_area\": 1, \"truck\": 17}', '本次采用粗细粒度融合检测，共检测到 19 个目标。其中场景要素 2 个，细粒度目标 17 个。其中数量最多的类别为 truck，共 17 个。融合去重后剔除了 1 个重复目标。综合判断，该图像属于交通车辆密集场景。系统识别到 19 个目标，主要场景标签包括：道路区域、车辆活动、植被覆盖。当前综合风险等级为低风险，道路交通密度异常：轻微异常。', '/results/fc287909-aff5-4cbf-bf44-11982b63bc94_result.jpg', '/results/fc287909-aff5-4cbf-bf44-11982b63bc94_result.json', '2026-06-14T04:42:36.747492+00:00');
INSERT INTO `detection_logs` (`id`, `user_id`, `username`, `image_id`, `original_filename`, `detection_mode`, `detection_mode_label`, `models_used`, `total_count`, `risk_level`, `risk_score`, `scene_type`, `class_count`, `report`, `result_image_url`, `result_json_url`, `created_at`) VALUES (5, 4, 'admin', '5e4ecdb5-e3ad-4977-ae02-3f7ef6aae002', '0000006_02616_d_0000007.jpg', 'fine', '细粒度目标检测', '[\"visdrone\"]', 17, '正常', 15, '未识别到明确巡检场景', '{\"truck\": 17}', '本次采用细粒度目标检测，共检测到 17 个目标。其中场景要素 0 个，细粒度目标 17 个。其中数量最多的类别为 truck，共 17 个。融合去重后剔除了 1 个重复目标。综合判断，该图像属于未识别到明确巡检场景。系统识别到 17 个目标，主要场景标签包括：车辆活动。当前综合风险等级为正常，各异常模块暂未发现明显风险。', '/results/5e4ecdb5-e3ad-4977-ae02-3f7ef6aae002_result.jpg', '/results/5e4ecdb5-e3ad-4977-ae02-3f7ef6aae002_result.json', '2026-06-14T04:47:43.973526+00:00');
INSERT INTO `detection_logs` (`id`, `user_id`, `username`, `image_id`, `original_filename`, `detection_mode`, `detection_mode_label`, `models_used`, `total_count`, `risk_level`, `risk_score`, `scene_type`, `class_count`, `report`, `result_image_url`, `result_json_url`, `created_at`) VALUES (6, 4, 'admin', '7de7cddf-18e7-40d6-a9ae-36dc28c18957', '0000006_02616_d_0000007.jpg', 'fusion', '粗细粒度融合检测', '[\"scene\", \"visdrone\"]', 19, '低风险', 26.1, '交通车辆密集场景', '{\"tree\": 1, \"road_area\": 1, \"truck\": 17}', '本次采用粗细粒度融合检测，共检测到 19 个目标。其中场景要素 2 个，细粒度目标 17 个。其中数量最多的类别为 truck，共 17 个。融合去重后剔除了 1 个重复目标。综合判断，该图像属于交通车辆密集场景。系统识别到 19 个目标，主要场景标签包括：道路区域、车辆活动、植被覆盖。当前综合风险等级为低风险，道路交通密度异常：轻微异常。', '/results/7de7cddf-18e7-40d6-a9ae-36dc28c18957_result.jpg', '/results/7de7cddf-18e7-40d6-a9ae-36dc28c18957_result.json', '2026-06-14T04:48:31.335231+00:00');
INSERT INTO `detection_logs` (`id`, `user_id`, `username`, `image_id`, `original_filename`, `detection_mode`, `detection_mode_label`, `models_used`, `total_count`, `risk_level`, `risk_score`, `scene_type`, `class_count`, `report`, `result_image_url`, `result_json_url`, `created_at`) VALUES (7, 4, 'admin', '048e6a16-0abc-4bb7-8d20-94e5440d8642', '0000006_02616_d_0000007.jpg', 'fusion', '粗细粒度融合检测', '[\"scene\", \"visdrone\"]', 19, '低风险', 26.1, '交通车辆密集场景', '{\"tree\": 1, \"road_area\": 1, \"truck\": 17}', '本次采用粗细粒度融合检测，共检测到 19 个目标。其中场景要素 2 个，细粒度目标 17 个。其中数量最多的类别为 truck，共 17 个。融合去重后剔除了 1 个重复目标。综合判断，该图像属于交通车辆密集场景。系统识别到 19 个目标，主要场景标签包括：道路区域、车辆活动、植被覆盖。当前综合风险等级为低风险，道路交通密度异常：轻微异常。', '/results/048e6a16-0abc-4bb7-8d20-94e5440d8642_result.jpg', '/results/048e6a16-0abc-4bb7-8d20-94e5440d8642_result.json', '2026-06-14T04:52:02.127042+00:00');
INSERT INTO `detection_logs` (`id`, `user_id`, `username`, `image_id`, `original_filename`, `detection_mode`, `detection_mode_label`, `models_used`, `total_count`, `risk_level`, `risk_score`, `scene_type`, `class_count`, `report`, `result_image_url`, `result_json_url`, `created_at`) VALUES (8, 5, 'normal_user', '816e3aed-8fe2-4b5a-830a-af78f3880538', '0000006_02616_d_0000007.jpg', 'fusion', '粗细粒度融合检测', '[\"scene\", \"visdrone\"]', 19, '低风险', 26.1, '交通车辆密集场景', '{\"tree\": 1, \"road_area\": 1, \"truck\": 17}', '本次采用粗细粒度融合检测，共检测到 19 个目标。其中场景要素 2 个，细粒度目标 17 个。其中数量最多的类别为 truck，共 17 个。融合去重后剔除了 1 个重复目标。综合判断，该图像属于交通车辆密集场景。系统识别到 19 个目标，主要场景标签包括：道路区域、车辆活动、植被覆盖。当前综合风险等级为低风险，道路交通密度异常：轻微异常。', '/results/816e3aed-8fe2-4b5a-830a-af78f3880538_result.jpg', '/results/816e3aed-8fe2-4b5a-830a-af78f3880538_result.json', '2026-06-14T05:06:05.688610+00:00');
INSERT INTO `detection_logs` (`id`, `user_id`, `username`, `image_id`, `original_filename`, `detection_mode`, `detection_mode_label`, `models_used`, `total_count`, `risk_level`, `risk_score`, `scene_type`, `class_count`, `report`, `result_image_url`, `result_json_url`, `created_at`) VALUES (9, 4, 'admin', '24c90df0-670f-4af1-8cd7-d65788b90c4f', '0000006_02138_d_0000006.jpg', 'fusion', '粗细粒度融合检测', '[\"scene\", \"visdrone\"]', 31, '低风险', 38.4, '交通车辆密集场景', '{\"road_area\": 2, \"tree\": 1, \"building\": 1, \"truck\": 21, \"car\": 6}', '本次采用粗细粒度融合检测，共检测到 31 个目标。其中场景要素 4 个，细粒度目标 27 个。其中数量最多的类别为 truck，共 21 个。融合去重后剔除了 4 个重复目标。综合判断，该图像属于交通车辆密集场景。系统识别到 31 个目标，主要场景标签包括：道路区域、车辆活动、建筑区域、植被覆盖。当前综合风险等级为低风险，道路交通密度异常：轻微异常。', '/results/24c90df0-670f-4af1-8cd7-d65788b90c4f_result.jpg', '/results/24c90df0-670f-4af1-8cd7-d65788b90c4f_result.json', '2026-06-14T05:28:16.149999+00:00');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
