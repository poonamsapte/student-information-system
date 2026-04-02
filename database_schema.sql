-- Student Information System Database Schema
-- Run this script to create all necessary tables

-- Drop existing tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS contact_queries CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS results CASCADE;
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS enrollments CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS teachers CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Users table with roles
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'teacher', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students table
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    name VARCHAR(100) NOT NULL,
    dob DATE,
    prn VARCHAR(50) UNIQUE,
    aadhar VARCHAR(12),
    pan VARCHAR(10),
    marks10 INTEGER,
    marks12 INTEGER,
    course VARCHAR(100),
    enrollment_year INTEGER
);

-- Teachers table
CREATE TABLE teachers (
    teacher_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    name VARCHAR(100) NOT NULL,
    qualification VARCHAR(100),
    subject_specialization VARCHAR(100),
    experience_years INTEGER
);

-- Courses table
CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    course_code VARCHAR(20) UNIQUE,
    description TEXT,
    credits INTEGER,
    teacher_id INTEGER REFERENCES teachers(teacher_id)
);

-- Enrollments table
CREATE TABLE enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(student_id),
    course_id INTEGER REFERENCES courses(course_id),
    enrollment_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'active'
);

-- Attendance table
CREATE TABLE attendance (
    attendance_id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(student_id),
    course_id INTEGER REFERENCES courses(course_id),
    date DATE NOT NULL,
    status VARCHAR(20) CHECK (status IN ('present', 'absent', 'late', 'excused')),
    UNIQUE(student_id, course_id, date)
);

-- Results/Marks table
CREATE TABLE results (
    result_id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(student_id),
    course_id INTEGER REFERENCES courses(course_id),
    marks_obtained INTEGER,
    total_marks INTEGER DEFAULT 100,
    grade VARCHAR(5),
    semester INTEGER,
    exam_type VARCHAR(50),
    upload_date DATE DEFAULT CURRENT_DATE
);

-- Notifications/Announcements table
CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    target_role VARCHAR(20),
    created_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Contact/Queries table
CREATE TABLE contact_queries (
    query_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    subject VARCHAR(200),
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_students_user_id ON students(user_id);
CREATE INDEX idx_teachers_user_id ON teachers(user_id);
CREATE INDEX idx_courses_teacher_id ON courses(teacher_id);
CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX idx_attendance_student_id ON attendance(student_id);
CREATE INDEX idx_results_student_id ON results(student_id);
CREATE INDEX idx_notifications_target_role ON notifications(target_role);

-- Insert default admin user (password: admin123)
-- Note: In production, use proper password hashing
INSERT INTO users (username, email, password_hash, role) 
VALUES ('admin', 'admin@sis.com', 'pbkdf2:sha256:260000$defaultsalt$hashedpassword', 'admin');

-- Sample data for testing (optional)
-- Uncomment below to insert sample data

-- INSERT INTO users (username, email, password_hash, role) VALUES 
-- ('student1', 'student1@sis.com', 'hashedpwd', 'student'),
-- ('teacher1', 'teacher1@sis.com', 'hashedpwd', 'teacher');
