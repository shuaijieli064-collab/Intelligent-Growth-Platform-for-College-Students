-- ============================================================
-- V6 知识点三层结构 — node_type 区分 课程根/章/叶子知识点
--   node_type = 'course'   课程根节点
--   node_type = 'chapter'  章节节点
--   node_type = 'kp'       叶子知识点（默认，存量行全部为此值）
-- 已存在的数据库通过条件化 ALTER 增列；重复执行安全。
-- 应用启动时 ensure_preset_hierarchy 也会兜底补列并重建层级。
-- ============================================================
USE student_growth_platform;

SET @ddl := IF(
    (SELECT COUNT(*) FROM information_schema.COLUMNS
      WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'knowledge_point'
        AND COLUMN_NAME = 'node_type') = 0,
    'ALTER TABLE knowledge_point ADD COLUMN node_type ENUM(''course'',''chapter'',''kp'') NOT NULL DEFAULT ''kp'' COMMENT ''节点类型: course/chapter/kp''',
    'SELECT 1'
);
PREPARE add_kp_node_type FROM @ddl;
EXECUTE add_kp_node_type;
DEALLOCATE PREPARE add_kp_node_type;
