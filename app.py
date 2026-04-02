from flask import Flask, render_template, request, redirect, session, flash, url_for
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)


def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="studentdb",
        user="postgres",
        password="sharwari123",
        port="5432"
    )
    return conn


# Password hashing functions
def hash_password(password):
    return generate_password_hash(password)


def verify_password(hash, password):
    return check_password_hash(hash, password)


# Decorators for authentication and authorization
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') not in allowed_roles:
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Grade calculation function
def calculate_grade(percentage):
    if percentage >= 90:
        return 'O'
    elif percentage >= 80:
        return 'A+'
    elif percentage >= 70:
        return 'A'
    elif percentage >= 60:
        return 'B+'
    elif percentage >= 50:
        return 'B'
    elif percentage >= 40:
        return 'C'
    else:
        return 'F'
# -------- AUTHENTICATION ROUTES --------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]  # student/teacher
        
        # Validate inputs
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template("signup.html")
        
        # Hash password
        password_hash = hash_password(password)
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Insert into users table
            cur.execute(
                "INSERT INTO users(username, email, password_hash, role) VALUES(%s, %s, %s, %s) RETURNING user_id",
                (username, email, password_hash, role)
            )
            user_id = cur.fetchone()[0]
            
            # Create profile based on role
            if role == 'student':
                cur.execute(
                    "INSERT INTO students(user_id, name) VALUES(%s, %s)",
                    (user_id, username)
                )
            elif role == 'teacher':
                cur.execute(
                    "INSERT INTO teachers(user_id, name) VALUES(%s, %s)",
                    (user_id, username)
                )
            
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
        finally:
            cur.close()
            conn.close()
    
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            "SELECT user_id, username, password_hash, role FROM users WHERE username=%s OR email=%s",
            (username, username)
        )
        user = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if user and verify_password(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            
            flash(f'Welcome back, {user[1]}!', 'success')
            
            # Role-based redirection
            if user[3] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user[3] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user[3] == 'student':
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('frontpage'))

@app.route("/")
def frontpage():
    return render_template("frontpage.html")


# -------- DASHBOARD ROUTES --------

@app.route("/dashboard")
def dashboard():
    if "user" not in session and "user_id" not in session:
        flash('Please login to access dashboard', 'error')
        return redirect(url_for('login'))
    
    # Generic dashboard - redirects based on role
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif session.get('role') == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    elif session.get('role') == 'student':
        return redirect(url_for('student_dashboard'))
    
    return render_template("dashboard.html")


# -------- ADMIN DASHBOARD --------

@app.route("/admin/dashboard")
@login_required
@role_required(['admin'])
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get statistics
    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM teachers")
    total_teachers = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM courses")
    total_courses = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM users WHERE role='student'")
    active_students = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return render_template("admin_dashboard.html", 
                         total_students=total_students,
                         total_teachers=total_teachers,
                         total_courses=total_courses,
                         active_students=active_students)


# -------- TEACHER DASHBOARD --------

@app.route("/teacher/dashboard")
@login_required
@role_required(['teacher'])
def teacher_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get teacher details
    cur.execute("SELECT * FROM teachers WHERE user_id=%s", (session['user_id'],))
    teacher = cur.fetchone()
    
    courses = []
    if teacher:
        teacher_id = teacher[0]
        # Get courses assigned to this teacher
        cur.execute("SELECT * FROM courses WHERE teacher_id=%s", (teacher_id,))
        courses = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template("teacher_dashboard.html", teacher=teacher, courses=courses)


# -------- STUDENT DASHBOARD --------

@app.route("/student/dashboard")
@login_required
@role_required(['student'])
def student_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get student details
    cur.execute("SELECT * FROM students WHERE user_id=%s", (session['user_id'],))
    student = cur.fetchone()
    
    courses = []
    attendance_pct = 0
    results = []
    
    if student:
        student_id = student[0]
        
        # Get enrolled courses
        cur.execute("""
            SELECT c.course_name, c.course_code, t.name as teacher_name
            FROM enrollments e
            JOIN courses c ON e.course_id = c.course_id
            JOIN teachers t ON c.teacher_id = t.teacher_id
            WHERE e.student_id = %s
        """, (student_id,))
        courses = cur.fetchall()
        
        # Get attendance percentage
        cur.execute("""
            SELECT COALESCE(COUNT(*) FILTER (WHERE status='present') * 100.0 / NULLIF(COUNT(*), 0), 0)
            FROM attendance 
            WHERE student_id = %s
        """, (student_id,))
        result = cur.fetchone()[0]
        attendance_pct = float(result) if result else 0
        
        # Get results
        cur.execute("""
            SELECT c.course_name, r.marks_obtained, r.total_marks, r.grade, r.exam_type
            FROM results r
            JOIN courses c ON r.course_id = c.course_id
            WHERE r.student_id = %s
        """, (student_id,))
        results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template("student_dashboard.html", 
                         student=student, 
                         courses=courses, 
                         attendance=attendance_pct,
                         results=results)


# -------- ADMIN MANAGEMENT ROUTES --------

@app.route("/admin/students", methods=["GET", "POST"])
@login_required
@role_required(['admin'])
def admin_manage_students():
    if request.method == "POST":
        # Add new student
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        name = request.form["name"]
        dob = request.form["dob"]
        prn = request.form["prn"]
        course = request.form["course"]  # This is the course name
        
        password_hash = hash_password(password)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                "INSERT INTO users(username, email, password_hash, role) VALUES(%s, %s, %s, 'student') RETURNING user_id",
                (username, email, password_hash)
            )
            user_id = cur.fetchone()[0]
            
            cur.execute(
                "INSERT INTO students(user_id, name, dob, prn, course) VALUES(%s, %s, %s, %s, %s)",
                (user_id, name, dob, prn, course)
            )
            student_id = cur.lastrowid  # Get the newly created student_id
            
            # Auto-enroll in the course if it exists
            if course:
                # Try to find the course by name
                cur.execute("SELECT course_id FROM courses WHERE course_name ILIKE %s", (f'%{course}%',))
                course_result = cur.fetchone()
                if course_result:
                    course_id = course_result[0]
                    # Create enrollment record
                    cur.execute(
                        "INSERT INTO enrollments(student_id, course_id) VALUES(%s, %s)",
                        (student_id, course_id)
                    )
            
            conn.commit()
            flash('Student added successfully and enrolled in course!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            print(f"Error: {e}")
        finally:
            cur.close()
            conn.close()
        
        return redirect(url_for('admin_manage_students'))
    
    # GET - list all students
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.student_id, s.name, s.prn, s.course, u.username, u.email 
        FROM students s 
        JOIN users u ON s.user_id = u.user_id
        ORDER BY s.student_id
    """)
    students = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template("admin_students.html", students=students)


@app.route("/admin/enrollment", methods=["GET", "POST"])
@login_required
@role_required(['admin'])
def admin_enrollment():
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == "POST":
        student_id = request.form["student_id"]
        course_id = request.form["course_id"]
        
        try:
            # Check if already enrolled
            cur.execute(
                "SELECT * FROM enrollments WHERE student_id=%s AND course_id=%s",
                (student_id, course_id)
            )
            if cur.fetchone():
                flash('Student is already enrolled in this course!', 'error')
            else:
                cur.execute(
                    "INSERT INTO enrollments(student_id, course_id) VALUES(%s, %s)",
                    (student_id, course_id)
                )
                conn.commit()
                flash('Student enrolled successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            print(f"Error: {e}")
        finally:
            cur.close()
            conn.close()
        
        return redirect(url_for('admin_enrollment'))
    
    # GET - show enrollment form with dropdowns
    cur.execute("SELECT student_id, name, prn FROM students ORDER BY name")
    students = cur.fetchall()
    
    cur.execute("SELECT course_id, course_name, course_code FROM courses ORDER BY course_name")
    courses = cur.fetchall()
    
    cur.execute("""
        SELECT s.student_id, s.name, c.course_name, c.course_code, e.enrollment_date
        FROM enrollments e
        JOIN students s ON e.student_id = s.student_id
        JOIN courses c ON e.course_id = c.course_id
        ORDER BY e.enrollment_date DESC
    """)
    enrollments = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template("admin_enrollment.html", students=students, courses=courses, enrollments=enrollments)


@app.route("/admin/student/delete/<int:id>")
@login_required
@role_required(['admin'])
def admin_delete_student(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get user_id first
    cur.execute("SELECT user_id FROM students WHERE student_id=%s", (id,))
    result = cur.fetchone()
    if result:
        user_id = result[0]
        cur.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
        conn.commit()
        flash('Student deleted successfully!', 'success')
    
    cur.close()
    conn.close()
    return redirect(url_for('admin_manage_students'))


@app.route("/admin/teachers", methods=["GET", "POST"])
@login_required
@role_required(['admin'])
def admin_manage_teachers():
    if request.method == "POST":
        # Add new teacher
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        name = request.form["name"]
        qualification = request.form["qualification"]
        specialization = request.form["specialization"]
        
        password_hash = hash_password(password)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                "INSERT INTO users(username, email, password_hash, role) VALUES(%s, %s, %s, 'teacher') RETURNING user_id",
                (username, email, password_hash)
            )
            user_id = cur.fetchone()[0]
            
            cur.execute(
                "INSERT INTO teachers(user_id, name, qualification, subject_specialization) VALUES(%s, %s, %s, %s)",
                (user_id, name, qualification, specialization)
            )
            
            conn.commit()
            flash('Teacher added successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            cur.close()
            conn.close()
        
        return redirect(url_for('admin_manage_teachers'))
    
    # GET - list all teachers
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT t.teacher_id, t.name, t.qualification, t.subject_specialization, u.username, u.email
        FROM teachers t
        JOIN users u ON t.user_id = u.user_id
        ORDER BY t.teacher_id
    """)
    teachers = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template("admin_teachers.html", teachers=teachers)


@app.route("/admin/teacher/delete/<int:id>")
@login_required
@role_required(['admin'])
def admin_delete_teacher(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT user_id FROM teachers WHERE teacher_id=%s", (id,))
    result = cur.fetchone()
    if result:
        user_id = result[0]
        cur.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
        conn.commit()
        flash('Teacher deleted successfully!', 'success')
    
    cur.close()
    conn.close()
    return redirect(url_for('admin_manage_teachers'))


@app.route("/admin/courses", methods=["GET", "POST"])
@login_required
@role_required(['admin'])
def admin_manage_courses():
    if request.method == "POST":
        # Add new course
        course_name = request.form["course_name"]
        course_code = request.form["course_code"]
        description = request.form["description"]
        credits = request.form["credits"]
        teacher_id = request.form.get("teacher_id")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                "INSERT INTO courses(course_name, course_code, description, credits, teacher_id) VALUES(%s, %s, %s, %s, %s)",
                (course_name, course_code, description, credits, teacher_id if teacher_id else None)
            )
            conn.commit()
            flash('Course added successfully!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            cur.close()
            conn.close()
        
        return redirect(url_for('admin_manage_courses'))
    
    # GET - list all courses
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.course_id, c.course_name, c.course_code, c.description, c.credits, t.name as teacher_name
        FROM courses c
        LEFT JOIN teachers t ON c.teacher_id = t.teacher_id
        ORDER BY c.course_id
    """)
    courses = cur.fetchall()
    
    # Get teachers for dropdown
    cur.execute("SELECT teacher_id, name FROM teachers")
    teachers = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template("admin_courses.html", courses=courses, teachers=teachers)


@app.route("/admin/course/delete/<int:id>")
@login_required
@role_required(['admin'])
def admin_delete_course(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM courses WHERE course_id=%s", (id,))
    conn.commit()
    flash('Course deleted successfully!', 'success')
    
    cur.close()
    conn.close()
    return redirect(url_for('admin_manage_courses'))


# -------- TEACHER FEATURES --------

@app.route("/teacher/attendance/<int:course_id>", methods=["GET", "POST"])
@login_required
@role_required(['teacher'])
def mark_attendance(course_id):
    if request.method == "POST":
        date = request.form["date"]
        attendance_data = request.form.getlist("attendance")  # List of "student_id:status"
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        for item in attendance_data:
            student_id, status = item.split(":")
            try:
                cur.execute("""
                    INSERT INTO attendance(student_id, course_id, date, status) 
                    VALUES(%s, %s, %s, %s)
                    ON CONFLICT (student_id, course_id, date) 
                    DO UPDATE SET status=EXCLUDED.status
                """, (student_id, course_id, date, status))
            except Exception as e:
                print(f"Error: {e}")
        
        conn.commit()
        flash('Attendance marked successfully!', 'success')
        cur.close()
        conn.close()
        return redirect(url_for('teacher_dashboard'))
    
    # GET - show student list for attendance
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.student_id, s.name 
        FROM enrollments e 
        JOIN students s ON e.student_id = s.student_id 
        WHERE e.course_id = %s
    """, (course_id,))
    students = cur.fetchall()
    
    # If no enrollments, get all students
    if not students:
        cur.execute("SELECT student_id, name FROM students")
        students = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template("teacher_attendance.html", students=students, course_id=course_id)


@app.route("/teacher/upload-marks/<int:course_id>", methods=["GET", "POST"])
@login_required
@role_required(['teacher'])
def upload_marks(course_id):
    if request.method == "POST":
        exam_type = request.form["exam_type"]
        total_marks = request.form["total_marks"]
        student_ids = request.form.getlist("student_ids")
        marks_list = request.form.getlist("marks_list")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            for i in range(len(student_ids)):
                student_id = student_ids[i]
                marks = int(marks_list[i])
                
                # Calculate grade
                percentage = (marks / int(total_marks)) * 100
                grade = calculate_grade(percentage)
                
                cur.execute("""
                    INSERT INTO results(student_id, course_id, marks_obtained, total_marks, grade, exam_type)
                    VALUES(%s, %s, %s, %s, %s, %s)
                """, (student_id, course_id, marks, total_marks, grade, exam_type))
            
            conn.commit()
            flash('Marks uploaded successfully!', 'success')
        except Exception as e:
            flash(f'Error uploading marks: {str(e)}', 'error')
            print(f"Error: {e}")
        finally:
            cur.close()
            conn.close()
        
        return redirect(url_for('teacher_dashboard'))
    
    # GET - show form to upload marks
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get enrolled students or all students
    cur.execute("""
        SELECT s.student_id, s.name 
        FROM enrollments e 
        JOIN students s ON e.student_id = s.student_id 
        WHERE e.course_id = %s
    """, (course_id,))
    students = cur.fetchall()
    
    if not students:
        cur.execute("SELECT student_id, name FROM students")
        students = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template("teacher_upload_marks.html", students=students, course_id=course_id)


# -------- STUDENT FEATURES --------

@app.route("/student/timetable")
@login_required
@role_required(['student'])
def view_timetable():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT student_id FROM students WHERE user_id=%s", (session['user_id'],))
    result = cur.fetchone()
    
    timetable = []
    if result:
        cur.execute("""
            SELECT c.course_name, c.course_code, COALESCE(t.name, 'TBA') as teacher_name
            FROM enrollments e
            JOIN courses c ON e.course_id = c.course_id
            LEFT JOIN teachers t ON c.teacher_id = t.teacher_id
            WHERE e.student_id = %s
        """, (result[0],))
        timetable = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template("student_timetable.html", timetable=timetable)


@app.route("/student/results")
@login_required
@role_required(['student'])
def view_results():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT student_id FROM students WHERE user_id=%s", (session['user_id'],))
    result = cur.fetchone()
    student_id = result[0] if result else None
    
    results = []
    if student_id:
        cur.execute("""
            SELECT c.course_name, r.marks_obtained, r.total_marks, r.grade, r.exam_type, r.upload_date
            FROM results r
            JOIN courses c ON r.course_id = c.course_id
            WHERE r.student_id = %s
            ORDER BY r.upload_date DESC
        """, (student_id,))
        results = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template("student_results.html", results=results)


@app.route("/student/attendance")
@login_required
@role_required(['student'])
def view_attendance():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT student_id FROM students WHERE user_id=%s", (session['user_id'],))
    result = cur.fetchone()
    student_id = result[0] if result else None
    
    attendance_details = []
    if student_id:
        cur.execute("""
            SELECT c.course_name, a.date, a.status,
                   (SELECT COUNT(*) FROM attendance a2 
                    WHERE a2.student_id = a.student_id AND a2.course_id = a.course_id) as total_classes,
                   (SELECT COUNT(*) FROM attendance a3 
                    WHERE a3.student_id = a.student_id AND a3.course_id = a.course_id AND a3.status='present') as present_classes
            FROM attendance a
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.student_id = %s
            ORDER BY a.date DESC
        """, (student_id,))
        attendance_details = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template("student_attendance.html", attendance=attendance_details)


# -------- NOTIFICATIONS & CONTACT --------

@app.route("/notifications")
@login_required
def notifications():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get notifications for user's role
    cur.execute("""
        SELECT n.title, n.message, n.created_at, u.username as created_by
        FROM notifications n
        JOIN users u ON n.created_by = u.user_id
        WHERE (n.target_role = %s OR n.target_role = 'all')
        AND n.is_active = TRUE
        ORDER BY n.created_at DESC
    """, (session['role'],))
    notifications_list = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template("notifications.html", notifications=notifications_list)


@app.route("/admin/send-notification", methods=["GET", "POST"])
@login_required
@role_required(['admin'])
def send_notification():
    if request.method == "POST":
        title = request.form["title"]
        message = request.form["message"]
        target_role = request.form["target_role"]
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO notifications(title, message, target_role, created_by)
            VALUES(%s, %s, %s, %s)
        """, (title, message, target_role, session['user_id']))
        
        conn.commit()
        flash('Notification sent successfully!', 'success')
        cur.close()
        conn.close()
        return redirect(url_for('notifications'))
    
    return render_template("send_notification.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO contact_queries(name, email, subject, message)
            VALUES(%s, %s, %s, %s)
        """, (name, email, subject, message))
        
        conn.commit()
        flash('Your query has been submitted. We will contact you soon!', 'success')
        cur.close()
        conn.close()
        return redirect(url_for('contact'))
    
    return render_template("contact.html")


# -------- PROFILE MANAGEMENT --------

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        email = request.form["email"]
        current_password = request.form["current_password"]
        new_password = request.form.get("new_password")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verify current password
        cur.execute("SELECT password_hash FROM users WHERE user_id=%s", (session['user_id'],))
        user = cur.fetchone()
        
        if verify_password(user[0], current_password):
            if new_password:
                new_hash = hash_password(new_password)
                cur.execute("UPDATE users SET password_hash=%s WHERE user_id=%s", (new_hash, session['user_id']))
            
            cur.execute("UPDATE users SET email=%s WHERE user_id=%s", (email, session['user_id']))
            conn.commit()
            flash('Profile updated successfully!', 'success')
        else:
            flash('Current password is incorrect', 'error')
        
        cur.close()
        conn.close()
        return redirect(url_for('profile'))
    
    # GET - show profile form
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=%s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    return render_template("profile.html", user=user)


# -------- SEARCH FUNCTIONALITY --------

@app.route("/admin/students/search")
@login_required
@role_required(['admin'])
def search_students():
    query = request.args.get('q', '')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT s.student_id, s.name, s.prn, s.course, u.username, u.email
        FROM students s
        JOIN users u ON s.user_id = u.user_id
        WHERE s.name ILIKE %s OR s.prn ILIKE %s OR s.course ILIKE %s
    """, (f'%{query}%', f'%{query}%', f'%{query}%'))
    
    students = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template("admin_students.html", students=students)


# -------- STUDENT FORM --------

@app.route("/student", methods=["GET", "POST"])
def student():

    if request.method == "POST":

        name = request.form["name"]
        dob = request.form["dob"]
        prn = request.form["prn"]
        aadhar = request.form["aadhar"]
        pan = request.form["pan"]
        marks10 = int(float(request.form["marks10"]))  # Convert to integer
        marks12 = int(float(request.form["marks12"]))  # Convert to integer
        course = request.form["course"]

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO students(name,dob,prn,aadhar,pan,marks10,marks12,course) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                (name, dob, prn, aadhar, pan, marks10, marks12, course)
            )
            conn.commit()
            flash('Student registered successfully!', 'success')
        except Exception as e:
            flash(f'Error registering student: {str(e)}', 'error')
            print(f"Error: {e}")
        finally:
            cur.close()
            conn.close()

        return redirect("/dashboard")

    return render_template("student.html")


# -------- RUN --------

if __name__ == "__main__":
    app.run(debug=True)