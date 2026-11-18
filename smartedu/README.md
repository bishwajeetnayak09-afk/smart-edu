# SmartEdu - Intelligent Academic Learning & Management Platform

**SmartEdu** is an academic management and adaptive learning platform featuring role-based portals for **Students**, **Faculty**, and **Administrators**, integrated with an **AI Study Assistant**, real-time attendance tracking, automated quiz evaluation, and diagnostic weak-subject performance analytics.

---

## 🌟 Key Features Breakdown

### 🎓 1. Student Access
- **Account & Profile**: Student registration and sign-in with customizable semester and subject enrollment.
- **Subjects & Study Materials**: Browse enrolled courses, download faculty notes, lecture slides, cheatsheets, and syllabi.
- **AI Study Assistant**:
  - Interactive chat interface with subject-aware context.
  - Multi-mode support:
    - 💡 *Explain Concept*: Clear pedagogical breakdowns with analogies and real-world examples.
    - 📝 *Mini Practice Quiz*: Generates 3-question retention challenges with instant answer keys.
    - 🧮 *Step-by-Step Solver*: Systematic mathematical and algorithmic derivations.
    - 📌 *High-Yield Cheatsheet*: Flashcard key takeaways and exam traps.
    - 📅 *Study Plan Advice*: Revision timetable recommendations.
- **Quizzes & Tests**: Take faculty-assigned assessments with active countdown timer, instant grading, and review mode with explanations.
- **Assignments & Tasks**: Submit code/text solutions and upload files; inspect faculty grades and feedback comments.
- **Performance & Diagnostic**: Chart.js Radar and Bar charts highlighting score distributions and automated detection of weak subjects.
- **Attendance Tracker**: Subject-wise presence/absence ratios with visual alerts if attendance drops below the 75% cutoff.
- **Personalized Study Timetable**: Weekly schedule combining lectures, labs, and student-customized self-study blocks.

---

### 👨‍🏫 2. Faculty Access
- **Faculty Account**: Dedicated faculty portal with course overview.
- **Assigned Students**: View roster across all taught courses with performance scores and attendance metrics.
- **Struggling Students Early-Alert Radar**: Automatic detection of students scoring below 50% or with attendance < 75%.
- **Mark Attendance**: Daily attendance ledger with 1-click *Mark All Present* / *All Absent* and custom remarks.
- **Upload Notes & Handouts**: Upload and categorize PDFs, presentation decks, and syllabi for classes.
- **Create Quizzes & Tests**: Interactive builder for multiple-choice questions, custom time limits, marks, and explanations.
- **Assignments & Grading Desk**: Post problem statements, inspect student submissions, enter marks, and provide feedback.
- **Broadcast Announcements**: Post alerts and exam dates to specific classes or global rosters.
- **Performance Reports & Charts**: Aggregated class averages and grade distribution charts.

---

### 🛡️ 3. Admin Panel
- **Manage Students & Faculty Accounts**: Provision new accounts, toggle active/disabled states, reset access, or delete users.
- **Curriculum & Subjects**: Add new courses, define credits/semester, and assign faculty instructors.
- **System Overview**: Metrics on total students, faculty, active courses, and quizzes.
- **1-Click Database Reset**: Restore the system to a clean realistic demo state at any time.

---

## 🚀 Quick Start Guide

### Running the Application
Open a terminal in the project directory:
```powershell
cd C:\Users\bishw\.gemini\antigravity\scratch\smartedu
python run.py
```
Then open your web browser to **[http://127.0.0.1:5000](http://127.0.0.1:5000)**.

---

## 🔑 Demo Login Credentials

You can use the **1-Click Quick Demo Sign-in buttons** on the login page or manually enter:

| Role | Username | Password | Full Name / Description |
| :--- | :--- | :--- | :--- |
| **Student** | `alex_student` | `student123` | Alex Mercer (Enrolled in 5 CS subjects) |
| **Student (Struggling)** | `jordan_student` | `student123` | Jordan Lee (Triggers struggling alert) |
| **Faculty** | `sarah_faculty` | `faculty123` | Dr. Sarah Chen (DSA & OS Instructor) |
| **Faculty** | `priya_faculty` | `faculty123` | Dr. Priya Sharma (DBMS & ML Instructor) |
| **Admin** | `admin` | `admin123` | System Administrator (Full privileges) |

---

## 📁 Project Architecture

```text
smartedu/
├── app.py                     # Main Flask application with routes, API, and auth
├── models.py                  # SQLAlchemy models (User, Subject, Quiz, Attendance, etc.)
├── ai_assistant.py            # AI Study Assistant engine & weak-areas diagnostic analyzer
├── seed_data.py               # Pre-seeded realistic demo data
├── test_app.py                # Automated end-to-end test suite
├── run.py                     # Launcher script
├── uploads/                   # Uploaded student submissions & faculty lecture handouts
├── static/
│   ├── css/style.css          # Styling enhancements & typography
│   └── js/app.js              # Interactivity & alert management
└── templates/
    ├── base.html              # Responsive layout with role switchers
    ├── index.html             # Landing showcase & demo launchers
    ├── login.html             # Login with 1-click demo buttons
    ├── register.html          # Student registration form
    ├── student/               # 8 Student Views
    ├── faculty/               # 8 Faculty Views
    └── admin/                 # 3 Administrator Views
```
