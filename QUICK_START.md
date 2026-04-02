# 🚀 Quick Start Guide - Student Information System

## ⚡ Fast Setup (5 Minutes)

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Setup Database
```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE studentdb;

# Exit and run schema
\q
psql -U postgres -d studentdb -f database_schema.sql
```

### 3️⃣ Update Database Password
Edit `app.py` line 10:
```python
password="YOUR_POSTGRES_PASSWORD"
```

### 4️⃣ Run Application
```bash
python app.py
```

Visit: http://127.0.0.1:5000/

---

## 🔑 First-Time Admin Setup

Since password hashing is now enabled, you need to create an admin account:

**Option 1: Via Signup Page (Recommended)**
1. Go to `/signup`
2. Register as admin with role "student" temporarily
3. In PostgreSQL, update the role:
   ```sql
   UPDATE users SET role='admin' WHERE username='your_username';
   ```

**Option 2: Direct SQL (Advanced)**
```sql
-- You'll need to generate a proper password hash
-- Use Python to generate: 
-- from werkzeug.security import generate_password_hash
-- print(generate_password_hash('admin123'))

INSERT INTO users (username, email, password_hash, role) 
VALUES ('admin', 'admin@sis.com', 'generated_hash_here', 'admin');
```

---

## 📁 Project Structure

```
SIS_Project/
├── app.py                          # Main Flask application
├── database_schema.sql             # Database setup script
├── requirements.txt                # Python dependencies
├── SETUP_INSTRUCTIONS.md          # Detailed setup guide
├── QUICK_START.md                 # This file
└── templates/                     # HTML templates
    ├── admin_dashboard.html
    ├── admin_students.html
    ├── admin_teachers.html
    ├── admin_courses.html
    ├── teacher_dashboard.html
    ├── teacher_attendance.html
    ├── teacher_upload_marks.html
    ├── student_dashboard.html
    ├── student_results.html
    ├── student_timetable.html
    ├── student_attendance.html
    ├── notifications.html
    ├── send_notification.html
    ├── profile.html
    ├── login.html
    ├── signup.html
    └── [other templates...]
```

---

## 🎯 Key Features Checklist

### ✅ Completed
- [x] Secure authentication with password hashing
- [x] Role-based access control (Admin/Teacher/Student)
- [x] Admin dashboard with statistics
- [x] Student management (CRUD)
- [x] Teacher management (CRUD)
- [x] Course management (CRUD)
- [x] Teacher dashboard with course list
- [x] Attendance marking system
- [x] Marks upload with automatic grading
- [x] Student dashboard with performance metrics
- [x] Results viewing with grade display
- [x] Attendance tracking and history
- [x] Timetable view
- [x] Notification system
- [x] Contact/Query submission
- [x] Profile management with password change
- [x] Search functionality
- [x] Responsive UI design
- [x] Flash message notifications

---

## 🧪 Test the System

### Create Test Data

1. **Register a Student:**
   - Visit `/signup`
   - Username: `student1`
   - Email: `student1@test.com`
   - Password: `pass123`
   - Role: Student

2. **Register a Teacher:**
   - Visit `/signup`
   - Username: `teacher1`
   - Email: `teacher1@test.com`
   - Password: `pass123`
   - Role: Teacher

3. **Login as Admin** and:
   - Add students
   - Add teachers
   - Create courses
   - Send notifications

4. **Login as Teacher** and:
   - Mark attendance
   - Upload marks

5. **Login as Student** and:
   - View courses
   - Check attendance
   - View results

---

## 🔐 Security Notes

- All passwords are hashed using Werkzeug
- Sessions are securely managed
- SQL injection prevented via parameterized queries
- Role-based authorization enforced on all protected routes

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Database connection error | Check PostgreSQL is running and credentials in `app.py` |
| Module not found | Run `pip install -r requirements.txt` |
| Tables not found | Re-run `database_schema.sql` |
| Login fails | Clear browser cache, verify password hash |
| Template not found | Ensure you're in project directory when running |

---

## 📊 Database Tables

9 tables created:
1. **users** - Authentication & roles
2. **students** - Student profiles
3. **teachers** - Teacher profiles  
4. **courses** - Course catalog
5. **enrollments** - Course enrollments
6. **attendance** - Daily attendance
7. **results** - Marks & grades
8. **notifications** - Announcements
9. **contact_queries** - Support tickets

---

## 🎨 UI Theme

Modern gradient-based design with:
- Purple/blue gradients for primary elements
- Card-based layouts
- Responsive navigation
- Animated flash messages
- Color-coded grades and status

---

## 📞 Need Help?

1. Check `SETUP_INSTRUCTIONS.md` for detailed guide
2. Review error messages in console
3. Verify database connection
4. Clear browser cache

---

## 🎉 You're Ready!

The complete Student Information System is now set up and ready to use!

**Access the application at:** http://127.0.0.1:5000/

Happy managing! 🚀📚
