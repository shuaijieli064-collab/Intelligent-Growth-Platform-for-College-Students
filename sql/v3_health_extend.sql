-- ============================================================
-- V3 健康维度扩展表
-- ============================================================
USE student_growth_platform;

-- 身体健康记录：运动、睡眠、步数
CREATE TABLE IF NOT EXISTS physical_health_record (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    student_id       INT NOT NULL,
    record_date      DATE NOT NULL COMMENT '记录日期',
    exercise_type    VARCHAR(50)  DEFAULT NULL COMMENT '运动类型：跑步/球类/健身/瑜伽/游泳/其他',
    exercise_duration INT DEFAULT 0 COMMENT '运动时长(分钟)',
    sleep_hours      DECIMAL(3,1) DEFAULT NULL COMMENT '睡眠时长',
    steps            INT DEFAULT 0 COMMENT '步数',
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='身体健康记录表';

-- 心理健康记录：心情、压力、焦虑、日记
CREATE TABLE IF NOT EXISTS mental_health_record (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    student_id       INT NOT NULL,
    record_date      DATE NOT NULL COMMENT '记录日期',
    mood_score       TINYINT DEFAULT NULL COMMENT '心情评分(1-10)',
    stress_level     TINYINT DEFAULT NULL COMMENT '压力等级(1-5，越高越压力)',
    anxiety_level    TINYINT DEFAULT NULL COMMENT '焦虑等级(1-5)',
    notes            TEXT DEFAULT NULL COMMENT '心情日记',
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='心理健康记录表';

-- 社交健康记录：活动类型、时长、互动人数
CREATE TABLE IF NOT EXISTS social_health_record (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    student_id        INT NOT NULL,
    record_date       DATE NOT NULL COMMENT '记录日期',
    activity_type     VARCHAR(50) DEFAULT NULL COMMENT '活动类型：社团/聚会/团队项目/志愿/其他',
    duration_minutes  INT DEFAULT 0 COMMENT '活动时长(分钟)',
    interaction_count INT DEFAULT 0 COMMENT '有效社交人数',
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='社交健康记录表';
