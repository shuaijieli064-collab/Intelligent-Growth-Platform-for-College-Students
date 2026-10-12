-- ============================================================
-- V5 课程/知识点归属 — 区分系统预置与学生自建数据
--   created_by IS NULL  => 系统预置（种子课程/预置知识点，只读共享）
--   created_by = 学生ID => 该学生自建（仅本人可见/可改）
-- 已存在的数据库通过下列条件化 ALTER 增列；重复执行安全。
-- ============================================================
USE student_growth_platform;

-- course.created_by
SET @ddl := IF(
    (SELECT COUNT(*) FROM information_schema.COLUMNS
      WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'course'
        AND COLUMN_NAME = 'created_by') = 0,
    'ALTER TABLE course ADD COLUMN created_by INT DEFAULT NULL COMMENT ''创建者学生ID(NULL=系统预置)''',
    'SELECT 1'
);
PREPARE add_course_owner FROM @ddl;
EXECUTE add_course_owner;
DEALLOCATE PREPARE add_course_owner;

-- knowledge_point.created_by
SET @ddl := IF(
    (SELECT COUNT(*) FROM information_schema.COLUMNS
      WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'knowledge_point'
        AND COLUMN_NAME = 'created_by') = 0,
    'ALTER TABLE knowledge_point ADD COLUMN created_by INT DEFAULT NULL COMMENT ''创建者学生ID(NULL=系统预置)''',
    'SELECT 1'
);
PREPARE add_kp_owner FROM @ddl;
EXECUTE add_kp_owner;
DEALLOCATE PREPARE add_kp_owner;

-- 存量课程默认视为系统预置（NULL），仅管理员可删；
-- 学生新建课程从本版本起写入 created_by。
