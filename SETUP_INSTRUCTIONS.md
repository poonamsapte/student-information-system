# Student Information System (SIS) - Setup Instructions

## 🎓 Overview

This is a comprehensive web-based Student Information System built with Flask and PostgreSQL. It provides role-based dashboards for Admins, Teachers, and Students with complete academic management features.

---

## 📋 Prerequisites

Before setting up the project, ensure you have:

1. **Python 3.8+** installed
2. **PostgreSQL** database server installed and running
3. **pip** (Python package manager)

---

## 🚀 Installation Steps

### Step 1: Install Python Dependencies

Open terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- psycopg2-binary (PostgreSQL adapter)
- Werkzeug (security utilities)
- python-dotenv (environment variables)

### Step 2: Database Setup

1. **Start PostgreSQL** and login as admin:
   ```bash
   psql -U postgres
   ```

2. **Create the database**:
   ```sql
   CREATE DATABASE studentdb;
   ```

3. **Exit psql** and run the schema file:
   ```bash
   psql -U postgres -d studentdb -f database_schema.sql
   ```

   Or manually execute the SQL commands in `database_schema.sql` through pgAdmin or psql.

### Step 3: Configure Database Connection

Open `app.py` and update the database connection settings in the `get_db_connection()` function:

```python
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="studentdb",
        user="postgres",      # Your PostgreSQL username
        password="your_password",  # Your PostgreSQL password
        port="5432"
    )
    return conn
```

### Step 4: Run the Application

```bash
python app.py
```

The application will start on: `http://127.0.0.1:5000/`

---

## 👥 Default Login Credentials

### Admin Access
After running the schema, you need to create an admin user manually in the database:

```sql
-- Insert admin user (password: admin123)
INSERT INTO users (username, email, password_hash, role) 
VALUES ('admin', 'admin@sis.com', 'pbkdf2:sha256:260000$randomsalt$hashedvalue', 'admin');
```

**OR** use the signup page to create your first admin account, then manually update the role in the database.

### Creating Test Users

You can register new users through `/signup` or directly insert into the database.

---

## 🗺️ Application Routes

### Public Routes
- `/` - Home Page
- `/login` - Login Page
- `/signup` - Registration Page
- `/contact` - Contact Form

### Admin Routes
- `/admin/dashboard` - Admin Dashboard
- `/admin/students` - Manage Students
- `/admin/teachers` - Manage Teachers
- `/admin/courses` - Manage Courses
- `/admin/send-notification` - Send Notifications

### Teacher Routes
- `/teacher/dashboard` - Teacher Dashboard
- `/teacher/attendance/<course_id>` - Mark Attendance
- `/teacher/upload-marks/<course_id>` - Upload Marks

### Student Routes
- `/student/dashboard` - Student Dashboard
- `/student/timetable` - View Timetable
- `/student/results` - View Results
- `/student/attendance` - View Attendance

### Common Routes
- `/notifications` - View Notifications
- `/profile` - User Profile Management
- `/logout` - Logout

---

## 🔐 Security Features

1. **Password Hashing** - All passwords are hashed using Werkzeug's security functions
2. **Role-Based Access Control** - Users can only access routes permitted for their role
3. **Session Management** - Secure session handling with Flask sessions
4. **SQL Injection Prevention** - Parameterized queries throughout

---

## 📊 Database Schema

### Tables Created:
1. **users** - User accounts with roles
2. **students** - Student profiles
3. **teachers** - Teacher profiles
4. **courses** - Course information
5. **enrollments** - Student-course enrollments
6. **attendance** - Attendance records
7. **results** - Exam marks and grades
8. **notifications** - Announcements
9. **contact_queries** - Support messages

---

## 🎨 Features Implemented

### ✅ Admin Features
- Dashboard with statistics
- CRUD operations for students, teachers, courses
- Send notifications to specific roles
- Monitor system activity

### ✅ Teacher Features
- View assigned courses
- Mark student attendance
- Upload and manage marks
- Automatic grade calculation

### ✅ Student Features
- View enrolled courses
- Check attendance percentage
- View results and grades
- Access course timetable
- Receive notifications

### ✅ Common Features
- User profile management
- Password change functionality
- Role-based redirection
- Flash message notifications
- Responsive UI design

---

## 🛠️ Troubleshooting

### Issue: Cannot connect to database
**Solution:** 
- Ensure PostgreSQL is running
- Check database credentials in `app.py`
- Verify database `studentdb` exists

### Issue: Module not found errors
**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Tables not found
**Solution:**
- Re-run `database_schema.sql`
- Check if you're connected to the correct database

### Issue: Login not working
**Solution:**
- Verify password hashing is working correctly
- Check if user exists in the database
- Clear browser cache and cookies

---

## 📝 Usage Tips

1. **First Time Setup:**
   - Create admin account first
   - Add teachers and courses
   - Enroll students in courses
   - Teachers can then mark attendance and upload marks

2. **Best Practices:**
   - Change default passwords immediately
   - Regular database backups
   - Review logs periodically
   - Keep dependencies updated

---

## 🔧 Customization

### Modify Grade Calculation
Edit the `calculate_grade()` function in `app.py`:

```python
def calculate_grade(percentage):
    if percentage >= 90:
        return 'O'
    elif percentage >= 80:
        return 'A+'
    # ... modify as needed
```

### Change Color Scheme
Update CSS gradients in template files:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

---

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review error logs in console
- Verify database connection and permissions

---

## 📄 License

This project is created for educational purposes.

---

## 🎉 Next Steps

1. Run the application
2. Create your admin account
3. Start adding data
4. Explore all the features!

**Happy Learning! 🚀**
