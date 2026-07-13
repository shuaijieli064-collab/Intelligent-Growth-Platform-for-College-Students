-- ============================================================
-- 大学生智能成长平台 - 数据库初始化脚本
-- ============================================================

CREATE DATABASE IF NOT EXISTS student_growth_platform
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE student_growth_platform;

-- -----------------------------------------------------------
-- 1. 学生表
-- -----------------------------------------------------------
CREATE TABLE student (
    student_id      INT AUTO_INCREMENT PRIMARY KEY,
    student_no      VARCHAR(20)  NOT NULL UNIQUE COMMENT '学号',
    name            VARCHAR(50)  NOT NULL COMMENT '姓名',
    gender          ENUM('M','F') NOT NULL COMMENT '性别',
    grade_level     VARCHAR(10)  NOT NULL COMMENT '年级，如大一、大二',
    major           VARCHAR(100) NOT NULL COMMENT '专业',
    enrollment_year INT          NOT NULL COMMENT '入学年份',
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='学生信息表';

-- -----------------------------------------------------------
-- 2. 课程表
-- -----------------------------------------------------------
CREATE TABLE course (
    course_id             INT AUTO_INCREMENT PRIMARY KEY,
    course_code           VARCHAR(20)  NOT NULL UNIQUE COMMENT '课程代码',
    course_name           VARCHAR(100) NOT NULL COMMENT '课程名称',
    credit                DECIMAL(3,1) NOT NULL COMMENT '学分',
    semester              VARCHAR(20)  NOT NULL COMMENT '学期，如2025-春',
    is_compulsory         BOOLEAN      DEFAULT TRUE COMMENT '是否必修',
    prerequisite_course_id INT         DEFAULT NULL COMMENT '先修课程ID',
    FOREIGN KEY (prerequisite_course_id) REFERENCES course(course_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='课程表';

-- -----------------------------------------------------------
-- 3. 学生选课表 (M:N)
-- -----------------------------------------------------------
CREATE TABLE student_course (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL,
    course_id       INT NOT NULL,
    usual_score     DECIMAL(5,2) DEFAULT NULL COMMENT '平时成绩',
    midterm_score   DECIMAL(5,2) DEFAULT NULL COMMENT '期中成绩',
    final_score     DECIMAL(5,2) DEFAULT NULL COMMENT '期末成绩(实际)',
    predicted_final DECIMAL(5,2) DEFAULT NULL COMMENT 'ML预测期末成绩',
    UNIQUE KEY uk_student_course (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (course_id)  REFERENCES course(course_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='学生选课与成绩表';

-- -----------------------------------------------------------
-- 4. 学习记录表
-- -----------------------------------------------------------
CREATE TABLE study_record (
    record_id      INT AUTO_INCREMENT PRIMARY KEY,
    student_id     INT NOT NULL,
    course_id      INT DEFAULT NULL COMMENT '关联课程(可选)',
    study_date     DATE NOT NULL COMMENT '学习日期',
    study_hours    DECIMAL(4,1) NOT NULL COMMENT '学习时长(小时)',
    task_completed INT DEFAULT 0 COMMENT '完成任务数',
    focus_score    TINYINT DEFAULT NULL COMMENT '专注度自评(0-100)',
    notes          TEXT DEFAULT NULL COMMENT '备注',
    FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (course_id)  REFERENCES course(course_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='每日学习记录表';

-- -----------------------------------------------------------
-- 5. 健康评估表
-- -----------------------------------------------------------
CREATE TABLE health_assessment (
    assessment_id   INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL,
    assessment_date DATE NOT NULL COMMENT '评估日期',
    academic_score  DECIMAL(5,2) NOT NULL COMMENT '学业健康(0-100)',
    physical_score  DECIMAL(5,2) NOT NULL COMMENT '身体健康(0-100)',
    mental_score    DECIMAL(5,2) NOT NULL COMMENT '心理健康(0-100)',
    social_score    DECIMAL(5,2) NOT NULL COMMENT '社交健康(0-100)',
    overall_health  DECIMAL(5,2) NOT NULL COMMENT '综合健康度(0-100)',
    risk_level      ENUM('LOW','MEDIUM','HIGH','CRITICAL') NOT NULL COMMENT '风险等级',
    FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='数字孪生健康评估表';

-- -----------------------------------------------------------
-- 6. 知识点表 (知识图谱节点)
-- -----------------------------------------------------------
CREATE TABLE knowledge_point (
    kp_id        INT AUTO_INCREMENT PRIMARY KEY,
    kp_name      VARCHAR(200) NOT NULL COMMENT '知识点名称',
    course_id    INT NOT NULL COMMENT '所属课程',
    parent_kp_id INT DEFAULT NULL COMMENT '前置知识点',
    difficulty   TINYINT DEFAULT 1 COMMENT '难度(1-5)',
    weight       DECIMAL(3,2) DEFAULT 1.0 COMMENT '重要性权重',
    FOREIGN KEY (course_id)   REFERENCES course(course_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (parent_kp_id) REFERENCES knowledge_point(kp_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='知识点表(知识图谱节点)';

-- -----------------------------------------------------------
-- 7. 知识点掌握度表 (学生-知识点 边)
-- -----------------------------------------------------------
CREATE TABLE knowledge_mastery (
    mastery_id    INT AUTO_INCREMENT PRIMARY KEY,
    student_id    INT NOT NULL,
    kp_id         INT NOT NULL,
    mastery_level DECIMAL(5,2) NOT NULL COMMENT '掌握度(0-100)',
    last_assessed DATE NOT NULL COMMENT '最近评估日期',
    UNIQUE KEY uk_student_kp (student_id, kp_id),
    FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (kp_id)      REFERENCES knowledge_point(kp_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='知识点掌握度表';

-- -----------------------------------------------------------
-- 8. 风险告警表
-- -----------------------------------------------------------
CREATE TABLE risk_alert (
    alert_id       INT AUTO_INCREMENT PRIMARY KEY,
    student_id     INT NOT NULL,
    alert_type     VARCHAR(50) NOT NULL COMMENT '告警类型: 学业/健康/心理/综合',
    risk_level     ENUM('LOW','MEDIUM','HIGH','CRITICAL') NOT NULL,
    alert_message  TEXT NOT NULL COMMENT '告警描述',
    rule_triggered VARCHAR(100) NOT NULL COMMENT '触发规则名称',
    is_resolved    BOOLEAN DEFAULT FALSE,
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at    DATETIME DEFAULT NULL,
    FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='风险告警表';

-- -----------------------------------------------------------
-- 9. AI教练对话日志表
-- -----------------------------------------------------------
CREATE TABLE ai_coach_log (
    log_id      INT AUTO_INCREMENT PRIMARY KEY,
    student_id  INT NOT NULL,
    session_id  VARCHAR(50) NOT NULL COMMENT '会话ID',
    role        ENUM('user','assistant','system') NOT NULL COMMENT '消息角色',
    message     TEXT NOT NULL COMMENT '消息内容',
    tokens_used INT DEFAULT 0 COMMENT '消耗token数',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='AI教练对话日志表';
