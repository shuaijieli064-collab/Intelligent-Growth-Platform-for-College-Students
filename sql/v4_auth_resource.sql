-- ============================================================
-- V4 认证与资源推荐扩展
-- ============================================================
USE student_growth_platform;

-- 用户表（登录认证）
CREATE TABLE IF NOT EXISTS app_user (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL,
    email         VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    student_id    INT DEFAULT NULL,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY username (username),
    KEY student_id (student_id),
    CONSTRAINT app_user_ibfk_1 FOREIGN KEY (student_id)
        REFERENCES student (student_id) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='用户登录表';

-- 资源推荐表补充课程关联（列已存在时跳过）
SET @ddl := IF(
    (SELECT COUNT(*) FROM information_schema.COLUMNS
      WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'resource_recommendation'
        AND COLUMN_NAME = 'course_id') = 0,
    'ALTER TABLE resource_recommendation ADD COLUMN course_id INT NULL',
    'SELECT 1'
);
PREPARE add_course_id FROM @ddl;
EXECUTE add_course_id;
DEALLOCATE PREPARE add_course_id;

-- 资源推荐表课程外键（约束已存在时跳过）
SET @ddl := IF(
    (SELECT COUNT(*) FROM information_schema.KEY_COLUMN_USAGE
      WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'resource_recommendation'
        AND COLUMN_NAME = 'course_id'
        AND REFERENCED_TABLE_NAME = 'course') = 0,
    'ALTER TABLE resource_recommendation ADD CONSTRAINT fk_resource_recommendation_course FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE SET NULL',
    'SELECT 1'
);
PREPARE add_course_fk FROM @ddl;
EXECUTE add_course_fk;
DEALLOCATE PREPARE add_course_fk;
