-- ============================================================
-- 大学生智能成长平台 - PostgreSQL Schema (Supabase)
-- 由 MySQL schema.sql + v2_extend.sql + v3_health_extend.sql 转换而来
-- 在 Supabase SQL Editor 中执行此文件即可
-- ============================================================

-- -----------------------------------------------------------
-- ENUM 类型定义（PostgreSQL 需要先创建类型）
-- -----------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE gender_enum AS ENUM ('M', 'F');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE risk_level_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE message_role_enum AS ENUM ('user', 'assistant', 'system');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- -----------------------------------------------------------
-- 1. 学生表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS student (
    student_id      SERIAL PRIMARY KEY,
    student_no      VARCHAR(20)  NOT NULL UNIQUE,
    name            VARCHAR(50)  NOT NULL,
    gender          gender_enum  NOT NULL,
    grade_level     VARCHAR(10)  NOT NULL,
    major           VARCHAR(100) NOT NULL,
    enrollment_year INT          NOT NULL,
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE student IS '学生信息表';
COMMENT ON COLUMN student.student_no IS '学号';
COMMENT ON COLUMN student.grade_level IS '年级，如大一、大二';

-- -----------------------------------------------------------
-- 2. 课程表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS course (
    course_id              SERIAL PRIMARY KEY,
    course_code            VARCHAR(20)  NOT NULL UNIQUE,
    course_name            VARCHAR(100) NOT NULL,
    credit                 NUMERIC(3,1) NOT NULL,
    semester               VARCHAR(20)  NOT NULL,
    is_compulsory          BOOLEAN      DEFAULT TRUE,
    prerequisite_course_id INT          DEFAULT NULL,
    FOREIGN KEY (prerequisite_course_id) REFERENCES course(course_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

COMMENT ON TABLE course IS '课程表';
COMMENT ON COLUMN course.semester IS '学期，如2025-春';
COMMENT ON COLUMN course.is_compulsory IS '是否必修';

-- -----------------------------------------------------------
-- 3. 学生选课表 (M:N)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS student_course (
    id              SERIAL PRIMARY KEY,
    student_id      INT NOT NULL,
    course_id       INT NOT NULL,
    usual_score     NUMERIC(5,2) DEFAULT NULL,
    midterm_score   NUMERIC(5,2) DEFAULT NULL,
    final_score     NUMERIC(5,2) DEFAULT NULL,
    predicted_final NUMERIC(5,2) DEFAULT NULL,
    UNIQUE (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (course_id)  REFERENCES course(course_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

COMMENT ON TABLE student_course IS '学生选课与成绩表';

-- -----------------------------------------------------------
-- 4. 学习记录表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS study_record (
    record_id      SERIAL PRIMARY KEY,
    student_id     INT NOT NULL,
    course_id      INT DEFAULT NULL,
    study_date     DATE NOT NULL,
    study_hours    NUMERIC(4,1) NOT NULL,
    task_completed INT DEFAULT 0,
    focus_score    SMALLINT DEFAULT NULL,
    notes          TEXT DEFAULT NULL,
    FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (course_id)  REFERENCES course(course_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

COMMENT ON TABLE study_record IS '每日学习记录表';
COMMENT ON COLUMN study_record.focus_score IS '专注度自评(0-100)';

-- -----------------------------------------------------------
-- 5. 健康评估表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS health_assessment (
    assessment_id   SERIAL PRIMARY KEY,
    student_id      INT NOT NULL,
    assessment_date DATE NOT NULL,
    academic_score  NUMERIC(5,2) NOT NULL,
    physical_score  NUMERIC(5,2) NOT NULL,
    mental_score    NUMERIC(5,2) NOT NULL,
    social_score    NUMERIC(5,2) NOT NULL,
    overall_health  NUMERIC(5,2) NOT NULL,
    risk_level      risk_level_enum NOT NULL,
    FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

COMMENT ON TABLE health_assessment IS '数字孪生健康评估表';

-- -----------------------------------------------------------
-- 6. 知识点表 (知识图谱节点)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_point (
    kp_id        SERIAL PRIMARY KEY,
    kp_name      VARCHAR(200) NOT NULL,
    course_id    INT NOT NULL,
    parent_kp_id INT DEFAULT NULL,
    difficulty   SMALLINT DEFAULT 1,
    weight       NUMERIC(3,2) DEFAULT 1.0,
    FOREIGN KEY (course_id)   REFERENCES course(course_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (parent_kp_id) REFERENCES knowledge_point(kp_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

COMMENT ON TABLE knowledge_point IS '知识点表(知识图谱节点)';
COMMENT ON COLUMN knowledge_point.difficulty IS '难度(1-5)';

-- -----------------------------------------------------------
-- 7. 知识点掌握度表 (学生-知识点 边)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_mastery (
    mastery_id    SERIAL PRIMARY KEY,
    student_id    INT NOT NULL,
    kp_id         INT NOT NULL,
    mastery_level NUMERIC(5,2) NOT NULL,
    last_assessed DATE NOT NULL,
    UNIQUE (student_id, kp_id),
    FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (kp_id)      REFERENCES knowledge_point(kp_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

COMMENT ON TABLE knowledge_mastery IS '知识点掌握度表';

-- -----------------------------------------------------------
-- 8. 风险告警表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS risk_alert (
    alert_id       SERIAL PRIMARY KEY,
    student_id     INT NOT NULL,
    alert_type     VARCHAR(50) NOT NULL,
    risk_level     risk_level_enum NOT NULL,
    alert_message  TEXT NOT NULL,
    rule_triggered VARCHAR(100) NOT NULL,
    is_resolved    BOOLEAN DEFAULT FALSE,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at    TIMESTAMP DEFAULT NULL,
    FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

COMMENT ON TABLE risk_alert IS '风险告警表';

-- -----------------------------------------------------------
-- 9. AI教练对话日志表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_coach_log (
    log_id      SERIAL PRIMARY KEY,
    student_id  INT NOT NULL,
    session_id  VARCHAR(50) NOT NULL,
    role        message_role_enum NOT NULL,
    message     TEXT NOT NULL,
    tokens_used INT DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

COMMENT ON TABLE ai_coach_log IS 'AI教练对话日志表';

-- -----------------------------------------------------------
-- 10. 用户表（登录认证）
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS app_user (
    user_id       SERIAL PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(100) DEFAULT NULL,
    password_hash VARCHAR(255) NOT NULL,
    student_id    INT DEFAULT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

COMMENT ON TABLE app_user IS '用户登录表';

-- -----------------------------------------------------------
-- 11. 学习计划表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS study_plan (
    id           SERIAL PRIMARY KEY,
    student_id   INT NOT NULL,
    subject      VARCHAR(50)  NOT NULL,
    goal_score   REAL         NOT NULL,
    exam_date    DATE         NOT NULL,
    plan_content TEXT         NOT NULL,
    status       VARCHAR(20)  DEFAULT 'active',
    progress     REAL         DEFAULT 0,
    created_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
);

COMMENT ON TABLE study_plan IS '学习计划表';

-- -----------------------------------------------------------
-- 12. 资源推荐表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS resource_recommendation (
    id            SERIAL PRIMARY KEY,
    student_id    INT NOT NULL,
    kp_id         INT DEFAULT NULL,
    resource_type VARCHAR(30) NOT NULL,
    title         VARCHAR(200) NOT NULL,
    url           VARCHAR(500),
    reason        TEXT,
    is_completed  BOOLEAN DEFAULT FALSE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (kp_id) REFERENCES knowledge_point(kp_id) ON DELETE SET NULL
);

COMMENT ON TABLE resource_recommendation IS '资源推荐表';

-- -----------------------------------------------------------
-- 13. 成长档案表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS growth_report (
    id            SERIAL PRIMARY KEY,
    student_id    INT NOT NULL,
    report_type   VARCHAR(20)  NOT NULL,
    report_date   DATE         NOT NULL,
    period_start  DATE,
    period_end    DATE,
    summary       TEXT,
    detail        TEXT,
    health_score  REAL,
    risk_level    VARCHAR(20),
    created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
);

COMMENT ON TABLE growth_report IS '成长档案表';

-- -----------------------------------------------------------
-- 14. 身体健康记录表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS physical_health_record (
    id                SERIAL PRIMARY KEY,
    student_id        INT NOT NULL,
    record_date       DATE NOT NULL,
    exercise_type     VARCHAR(50)  DEFAULT NULL,
    exercise_duration INT DEFAULT 0,
    sleep_hours       NUMERIC(3,1) DEFAULT NULL,
    steps             INT DEFAULT 0,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
);

COMMENT ON TABLE physical_health_record IS '身体健康记录表';

-- -----------------------------------------------------------
-- 15. 心理健康记录表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS mental_health_record (
    id            SERIAL PRIMARY KEY,
    student_id    INT NOT NULL,
    record_date   DATE NOT NULL,
    mood_score    SMALLINT DEFAULT NULL,
    stress_level  SMALLINT DEFAULT NULL,
    anxiety_level SMALLINT DEFAULT NULL,
    notes         TEXT DEFAULT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
);

COMMENT ON TABLE mental_health_record IS '心理健康记录表';

-- -----------------------------------------------------------
-- 16. 社交健康记录表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS social_health_record (
    id                SERIAL PRIMARY KEY,
    student_id        INT NOT NULL,
    record_date       DATE NOT NULL,
    activity_type     VARCHAR(50) DEFAULT NULL,
    duration_minutes  INT DEFAULT 0,
    interaction_count INT DEFAULT 0,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
);

COMMENT ON TABLE social_health_record IS '社交健康记录表';

-- ============================================================
-- 索引（提升查询性能）
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_study_record_student  ON study_record(student_id, study_date);
CREATE INDEX IF NOT EXISTS idx_health_assessment_stu ON health_assessment(student_id, assessment_date);
CREATE INDEX IF NOT EXISTS idx_risk_alert_student    ON risk_alert(student_id, is_resolved, created_at);
CREATE INDEX IF NOT EXISTS idx_ai_coach_log_student  ON ai_coach_log(student_id, session_id);
CREATE INDEX IF NOT EXISTS idx_student_course_student ON student_course(student_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_mastery_stu  ON knowledge_mastery(student_id);
