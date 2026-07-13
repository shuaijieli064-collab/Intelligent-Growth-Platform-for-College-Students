-- ============================================================
-- V2 扩展表
-- ============================================================
USE student_growth_platform;

-- 学习计划表
CREATE TABLE IF NOT EXISTS study_plan (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT NOT NULL,
    subject     VARCHAR(50)  NOT NULL COMMENT '科目',
    goal_score  FLOAT        NOT NULL COMMENT '目标分数',
    exam_date   DATE         NOT NULL COMMENT '考试日期',
    plan_content TEXT        NOT NULL COMMENT '任务计划 JSON',
    status      VARCHAR(20)  DEFAULT 'active' COMMENT 'active/completed/cancelled',
    progress    FLOAT        DEFAULT 0 COMMENT '进度 0-100',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='学习计划表';

-- 资源推荐表
CREATE TABLE IF NOT EXISTS resource_recommendation (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    student_id    INT NOT NULL,
    kp_id         INT COMMENT '关联薄弱知识点',
    resource_type VARCHAR(30) NOT NULL COMMENT 'video/exercise/article/course',
    title         VARCHAR(200) NOT NULL,
    url           VARCHAR(500),
    reason        TEXT COMMENT '推荐理由',
    is_completed  BOOLEAN DEFAULT FALSE,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (kp_id) REFERENCES knowledge_point(kp_id) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='资源推荐表';

-- 成长档案表
CREATE TABLE IF NOT EXISTS growth_report (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    student_id    INT NOT NULL,
    report_type   VARCHAR(20)  NOT NULL COMMENT 'weekly/monthly/semester',
    report_date   DATE         NOT NULL,
    period_start  DATE,
    period_end    DATE,
    summary       TEXT         COMMENT '摘要',
    detail        LONGTEXT     COMMENT '报告详情 JSON',
    health_score  FLOAT,
    risk_level    VARCHAR(20),
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='成长档案表';
