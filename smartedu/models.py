from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association table for Student <-> Subject enrollment
student_subjects = db.Table('student_subjects',
    db.Column('student_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'), primary_key=True),
    db.Column('enrolled_at', db.DateTime, default=datetime.utcnow)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student') # 'student', 'faculty', 'admin'
    identifier = db.Column(db.String(50)) # Roll Number or Faculty ID
    department = db.Column(db.String(100), default='Computer Science')
    semester = db.Column(db.Integer, default=5)
    avatar_color = db.Column(db.String(30), default='indigo')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active_account = db.Column(db.Boolean, default=True)

    # Relationships
    enrolled_subjects = db.relationship('Subject', secondary=student_subjects, backref=db.backref('enrolled_students', lazy='dynamic'))
    taught_subjects = db.relationship('Subject', backref='faculty', lazy=True, foreign_keys='Subject.faculty_id')
    quiz_attempts = db.relationship('QuizAttempt', backref='student', lazy=True, cascade='all, delete-orphan')
    assignment_submissions = db.relationship('AssignmentSubmission', backref='student', lazy=True, cascade='all, delete-orphan')
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy=True, foreign_keys='AttendanceRecord.student_id', cascade='all, delete-orphan')
    timetable_slots = db.relationship('TimetableSlot', backref='student', lazy=True, cascade='all, delete-orphan')
    chat_messages = db.relationship('AIChatMessage', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def is_faculty(self):
        return self.role == 'faculty'

    @property
    def is_admin(self):
        return self.role == 'admin'


class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False) # e.g. CS301
    name = db.Column(db.String(120), nullable=False) # e.g. Data Structures & Algorithms
    description = db.Column(db.Text)
    department = db.Column(db.String(100), default='Computer Science')
    credits = db.Column(db.Integer, default=4)
    semester = db.Column(db.Integer, default=5)
    faculty_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    materials = db.relationship('StudyMaterial', backref='subject', lazy=True, cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', backref='subject', lazy=True, cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', backref='subject', lazy=True, cascade='all, delete-orphan')
    attendance_records = db.relationship('AttendanceRecord', backref='subject', lazy=True, cascade='all, delete-orphan')
    announcements = db.relationship('Announcement', backref='subject', lazy=True, cascade='all, delete-orphan')


class StudyMaterial(db.Model):
    __tablename__ = 'study_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    material_type = db.Column(db.String(30), default='notes') # 'notes', 'slides', 'syllabus', 'reference', 'cheatsheet'
    file_path = db.Column(db.String(255))
    file_name = db.Column(db.String(150))
    file_size_kb = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    faculty = db.relationship('User', foreign_keys=[faculty_id])


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    time_limit_minutes = db.Column(db.Integer, default=15)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)

    questions = db.relationship('QuizQuestion', backref='quiz', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True, cascade='all, delete-orphan')
    faculty = db.relationship('User', foreign_keys=[faculty_id])

    @property
    def total_marks(self):
        return sum(q.marks for q in self.questions) or len(self.questions)


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False) # 'A', 'B', 'C', 'D'
    explanation = db.Column(db.Text)
    marks = db.Column(db.Integer, default=1)


class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    total_possible = db.Column(db.Float, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    answers_json = db.Column(db.Text) # Store user answers dictionary as JSON


class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    max_marks = db.Column(db.Integer, default=100)
    due_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submissions = db.relationship('AssignmentSubmission', backref='assignment', lazy=True, cascade='all, delete-orphan')
    faculty = db.relationship('User', foreign_keys=[faculty_id])


class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    submission_text = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    marks_obtained = db.Column(db.Float, nullable=True) # None until graded
    feedback = db.Column(db.Text)
    graded_at = db.Column(db.DateTime, nullable=True)


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(15), nullable=False) # 'present', 'absent', 'late'
    remarks = db.Column(db.String(100))

    faculty = db.relationship('User', foreign_keys=[faculty_id])


class Announcement(db.Model):
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True) # Null = Global
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='normal') # 'normal', 'urgent', 'info'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    faculty = db.relationship('User', foreign_keys=[faculty_id])


class TimetableSlot(db.Model):
    __tablename__ = 'timetable_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False) # Monday, Tuesday, etc.
    start_time = db.Column(db.String(10), nullable=False) # "09:00"
    end_time = db.Column(db.String(10), nullable=False)   # "10:30"
    subject_name = db.Column(db.String(120), nullable=False)
    activity_type = db.Column(db.String(50), default='Lecture') # 'Lecture', 'Self Study', 'Practice/Quiz', 'Lab Revision'
    room = db.Column(db.String(50), default='Room 302 / Online')
    is_custom = db.Column(db.Boolean, default=False)


class AIChatMessage(db.Model):
    __tablename__ = 'ai_chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sender = db.Column(db.String(20), nullable=False) # 'user' or 'ai'
    message = db.Column(db.Text, nullable=False)
    subject_tag = db.Column(db.String(50), default='General')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
