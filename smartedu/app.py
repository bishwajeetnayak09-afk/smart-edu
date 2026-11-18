import os
import json
from datetime import datetime, date, timedelta
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, send_from_directory, abort
)
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)
from werkzeug.utils import secure_filename

from models import (
    db, User, Subject, StudyMaterial, Quiz, QuizQuestion,
    QuizAttempt, Assignment, AssignmentSubmission, AttendanceRecord,
    Announcement, TimetableSlot, AIChatMessage, student_subjects
)
from seed_data import seed_database
from ai_assistant import generate_ai_response, analyze_weak_areas

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smartedu-secure-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'smartedu.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Role requirement decorators
def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role not in allowed_roles:
                flash(f"Access denied: You do not have permissions for this portal ({current_user.role}).", "danger")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Context processor for common template variables
@app.context_processor
def inject_global_data():
    recent_announcements = []
    if current_user.is_authenticated:
        recent_announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(3).all()
    return {
        'now': datetime.utcnow(),
        'recent_announcements': recent_announcements
    }


# ==========================================
# PUBLIC & AUTHENTICATION ROUTES
# ==========================================

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_student:
            return redirect(url_for('student_dashboard'))
        elif current_user.is_faculty:
            return redirect(url_for('faculty_dashboard'))
        elif current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password):
            if not user.is_active_account:
                flash("Your account is currently disabled. Please contact the administrator.", "danger")
                return render_template('login.html')
            
            login_user(user)
            flash(f"Welcome back, {user.full_name}!", "success")
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            
            if user.is_student:
                return redirect(url_for('student_dashboard'))
            elif user.is_faculty:
                return redirect(url_for('faculty_dashboard'))
            else:
                return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid username or password. Please try again.", "danger")

    return render_template('login.html')


@app.route('/demo-login/<role>')
def demo_login(role):
    """Convenient 1-click demo switcher for seamless exploration."""
    user_map = {
        'student': 'alex_student',
        'faculty': 'sarah_faculty',
        'admin': 'admin'
    }
    username = user_map.get(role)
    if not username:
        flash("Invalid role selected.", "danger")
        return redirect(url_for('login'))
        
    user = User.query.filter_by(username=username).first()
    if user:
        login_user(user)
        flash(f"Logged in as Demo {role.title()} ({user.full_name})", "success")
        if user.is_student:
            return redirect(url_for('student_dashboard'))
        elif user.is_faculty:
            return redirect(url_for('faculty_dashboard'))
        else:
            return redirect(url_for('admin_dashboard'))
    flash("Demo user not found. Please re-seed the database.", "warning")
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    all_subjects = Subject.query.order_by(Subject.name).all()

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        department = request.form.get('department', 'Computer Science')
        semester = int(request.form.get('semester', 5))
        roll_number = request.form.get('roll_number', '').strip()
        selected_subject_ids = request.form.getlist('subject_ids')

        # Validation
        if User.query.filter_by(username=username).first():
            flash("Username already taken. Please choose another.", "warning")
            return render_template('register.html', subjects=all_subjects)
        
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return render_template('register.html', subjects=all_subjects)

        new_student = User(
            username=username,
            email=email,
            full_name=full_name,
            role='student',
            identifier=roll_number or f"STU-{int(datetime.utcnow().timestamp()) % 10000}",
            department=department,
            semester=semester,
            avatar_color='blue'
        )
        new_student.set_password(password)
        db.session.add(new_student)
        db.session.commit()

        # Enroll in selected subjects (or all semester subjects by default)
        if selected_subject_ids:
            for s_id in selected_subject_ids:
                subj = Subject.query.get(int(s_id))
                if subj:
                    new_student.enrolled_subjects.append(subj)
        else:
            for subj in all_subjects:
                new_student.enrolled_subjects.append(subj)
        
        db.session.commit()
        login_user(new_student)
        flash("Registration successful! Welcome to SmartEdu.", "success")
        return redirect(url_for('student_dashboard'))

    return render_template('register.html', subjects=all_subjects)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for('login'))


# ==========================================
# STUDENT PORTAL ROUTES
# ==========================================

@app.route('/student/dashboard')
@login_required
@role_required('student')
def student_dashboard():
    # Performance analytics & weak areas
    analysis = analyze_weak_areas(current_user)

    # Enrolled subjects
    subjects = current_user.enrolled_subjects

    # Upcoming quizzes
    all_quizzes = Quiz.query.filter(Quiz.subject_id.in_([s.id for s in subjects])).all()
    taken_quiz_ids = [a.quiz_id for a in current_user.quiz_attempts]
    pending_quizzes = [q for q in all_quizzes if q.id not in taken_quiz_ids]

    # Active assignments
    all_assignments = Assignment.query.filter(Assignment.subject_id.in_([s.id for s in subjects])).all()
    submitted_assignment_ids = [s.assignment_id for s in current_user.assignment_submissions]
    pending_assignments = [a for a in all_assignments if a.id not in submitted_assignment_ids]

    # Recent study materials
    recent_materials = StudyMaterial.query.filter(
        StudyMaterial.subject_id.in_([s.id for s in subjects])
    ).order_by(StudyMaterial.created_at.desc()).limit(5).all()

    # Announcements
    announcements = Announcement.query.filter(
        (Announcement.subject_id.in_([s.id for s in subjects])) | (Announcement.subject_id.is_(None))
    ).order_by(Announcement.created_at.desc()).limit(4).all()

    return render_template(
        'student/dashboard.html',
        analysis=analysis,
        subjects=subjects,
        pending_quizzes=pending_quizzes,
        pending_assignments=pending_assignments,
        recent_materials=recent_materials,
        announcements=announcements
    )


@app.route('/student/subjects')
@login_required
@role_required('student')
def student_subjects():
    subjects = current_user.enrolled_subjects
    selected_subject_id = request.args.get('subject_id', type=int)
    
    current_subject = None
    materials = []
    quizzes = []
    assignments = []

    if subjects:
        if selected_subject_id:
            current_subject = Subject.query.get(selected_subject_id)
        if not current_subject:
            current_subject = subjects[0]
            
        materials = StudyMaterial.query.filter_by(subject_id=current_subject.id).order_by(StudyMaterial.created_at.desc()).all()
        quizzes = Quiz.query.filter_by(subject_id=current_subject.id).all()
        assignments = Assignment.query.filter_by(subject_id=current_subject.id).all()

    return render_template(
        'student/subjects.html',
        subjects=subjects,
        current_subject=current_subject,
        materials=materials,
        quizzes=quizzes,
        assignments=assignments
    )


@app.route('/student/ai-assistant')
@login_required
@role_required('student')
def student_ai_assistant():
    subjects = current_user.enrolled_subjects
    history = AIChatMessage.query.filter_by(student_id=current_user.id).order_by(AIChatMessage.timestamp.asc()).all()
    return render_template('student/ai_assistant.html', subjects=subjects, history=history)


@app.route('/api/student/ai-chat', methods=['POST'])
@login_required
@role_required('student')
def api_student_ai_chat():
    data = request.get_json() or {}
    query = data.get('message', '').strip()
    subject_context = data.get('subject', 'General')
    mode = data.get('mode', 'explain')

    if not query:
        return jsonify({'error': 'Message cannot be empty'}), 400

    # Save user message
    user_msg = AIChatMessage(
        student_id=current_user.id,
        sender='user',
        message=query,
        subject_tag=subject_context
    )
    db.session.add(user_msg)

    # Generate response
    ai_response_text = generate_ai_response(
        student_name=current_user.full_name,
        query=query,
        subject_context=subject_context,
        mode=mode
    )

    # Save AI message
    ai_msg = AIChatMessage(
        student_id=current_user.id,
        sender='ai',
        message=ai_response_text,
        subject_tag=subject_context
    )
    db.session.add(ai_msg)
    db.session.commit()

    return jsonify({
        'reply': ai_response_text,
        'timestamp': datetime.utcnow().strftime('%I:%M %p')
    })


@app.route('/student/quizzes')
@login_required
@role_required('student')
def student_quizzes():
    subjects = current_user.enrolled_subjects
    quizzes = Quiz.query.filter(Quiz.subject_id.in_([s.id for s in subjects])).order_by(Quiz.created_at.desc()).all()
    
    attempts = {a.quiz_id: a for a in current_user.quiz_attempts}
    return render_template('student/quizzes.html', quizzes=quizzes, attempts=attempts)


@app.route('/student/quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
@role_required('student')
def student_take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    existing_attempt = QuizAttempt.query.filter_by(quiz_id=quiz.id, student_id=current_user.id).first()

    if request.method == 'POST':
        if existing_attempt:
            flash("You have already submitted this quiz.", "info")
            return redirect(url_for('student_quizzes'))

        # Score calculation
        score = 0
        total_possible = sum(q.marks for q in quiz.questions)
        answers_dict = {}

        for q in quiz.questions:
            user_choice = request.form.get(f'question_{q.id}')
            answers_dict[str(q.id)] = user_choice
            if user_choice == q.correct_option:
                score += q.marks

        pct = round((score / total_possible) * 100, 1) if total_possible > 0 else 0
        attempt = QuizAttempt(
            quiz_id=quiz.id,
            student_id=current_user.id,
            score=score,
            total_possible=total_possible,
            percentage=pct,
            answers_json=json.dumps(answers_dict)
        )
        db.session.add(attempt)
        db.session.commit()

        flash(f"Quiz completed! You scored {score}/{total_possible} ({pct}%).", "success")
        return redirect(url_for('student_quizzes'))

    answers_json = json.loads(existing_attempt.answers_json) if existing_attempt and existing_attempt.answers_json else {}
    return render_template('student/take_quiz.html', quiz=quiz, attempt=existing_attempt, user_answers=answers_json)


@app.route('/student/assignments', methods=['GET', 'POST'])
@login_required
@role_required('student')
def student_assignments():
    subjects = current_user.enrolled_subjects
    assignments = Assignment.query.filter(Assignment.subject_id.in_([s.id for s in subjects])).order_by(Assignment.due_date.asc()).all()
    submissions = {s.assignment_id: s for s in current_user.assignment_submissions}

    if request.method == 'POST':
        assignment_id = int(request.form.get('assignment_id'))
        submission_text = request.form.get('submission_text', '').strip()

        # Handle file upload if provided
        file_path = None
        if 'submission_file' in request.files:
            file = request.files['submission_file']
            if file and file.filename != '':
                filename = secure_filename(f"asg_{assignment_id}_stu_{current_user.id}_{file.filename}")
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)
                file_path = filename

        sub = AssignmentSubmission.query.filter_by(assignment_id=assignment_id, student_id=current_user.id).first()
        if sub:
            sub.submission_text = submission_text
            if file_path:
                sub.file_path = file_path
            sub.submitted_at = datetime.utcnow()
            flash("Assignment submission updated successfully!", "success")
        else:
            sub = AssignmentSubmission(
                assignment_id=assignment_id,
                student_id=current_user.id,
                submission_text=submission_text,
                file_path=file_path
            )
            db.session.add(sub)
            flash("Assignment submitted successfully!", "success")
            
        db.session.commit()
        return redirect(url_for('student_assignments'))

    return render_template('student/assignments.html', assignments=assignments, submissions=submissions)


@app.route('/student/performance')
@login_required
@role_required('student')
def student_performance():
    analysis = analyze_weak_areas(current_user)
    return render_template('student/performance.html', analysis=analysis)


@app.route('/student/attendance')
@login_required
@role_required('student')
def student_attendance():
    subjects = current_user.enrolled_subjects
    attendance_summary = []

    for subj in subjects:
        records = AttendanceRecord.query.filter_by(student_id=current_user.id, subject_id=subj.id).order_by(AttendanceRecord.date.desc()).all()
        total_classes = len(records)
        presents = sum(1 for r in records if r.status in ['present', 'late'])
        absents = sum(1 for r in records if r.status == 'absent')
        pct = round((presents / total_classes * 100), 1) if total_classes > 0 else 100.0

        attendance_summary.append({
            'subject': subj,
            'total': total_classes,
            'presents': presents,
            'absents': absents,
            'percentage': pct,
            'is_low': pct < 75.0,
            'recent_records': records[:5]
        })

    return render_template('student/attendance.html', attendance_summary=attendance_summary)


@app.route('/student/timetable', methods=['GET', 'POST'])
@login_required
@role_required('student')
def student_timetable():
    if request.method == 'POST':
        day = request.form.get('day_of_week')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        subject_name = request.form.get('subject_name')
        activity_type = request.form.get('activity_type', 'Self Study')
        room = request.form.get('room', 'Personal Study Desk')

        new_slot = TimetableSlot(
            student_id=current_user.id,
            day_of_week=day,
            start_time=start_time,
            end_time=end_time,
            subject_name=subject_name,
            activity_type=activity_type,
            room=room,
            is_custom=True
        )
        db.session.add(new_slot)
        db.session.commit()
        flash("Custom study block added to your timetable!", "success")
        return redirect(url_for('student_timetable'))

    slots = TimetableSlot.query.filter_by(student_id=current_user.id).order_by(TimetableSlot.start_time.asc()).all()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    timetable_by_day = {day: [s for s in slots if s.day_of_week == day] for day in days}

    # AI Timetable Recommendation based on weak areas
    analysis = analyze_weak_areas(current_user)

    return render_template(
        'student/timetable.html',
        timetable_by_day=timetable_by_day,
        days=days,
        analysis=analysis
    )


@app.route('/student/timetable/delete/<int:slot_id>', methods=['POST'])
@login_required
@role_required('student')
def student_delete_slot(slot_id):
    slot = TimetableSlot.query.filter_by(id=slot_id, student_id=current_user.id).first_or_404()
    db.session.delete(slot)
    db.session.commit()
    flash("Study block removed from timetable.", "info")
    return redirect(url_for('student_timetable'))


# ==========================================
# FACULTY PORTAL ROUTES
# ==========================================

@app.route('/faculty/dashboard')
@login_required
@role_required('faculty')
def faculty_dashboard():
    taught_subjects = current_user.taught_subjects
    subject_ids = [s.id for s in taught_subjects]

    # Collect assigned students
    students = User.query.filter(User.role == 'student', User.enrolled_subjects.any(Subject.id.in_(subject_ids))).all()
    
    # Calculate struggling students (score < 50% or attendance < 75%)
    struggling_students = []
    for st in students:
        ana = analyze_weak_areas(st)
        if ana['weak_subjects'] or ana['overall_attendance'] < 75.0:
            struggling_students.append({
                'student': st,
                'overall_score': ana['overall_score'],
                'overall_attendance': ana['overall_attendance'],
                'weak_subjects': ana['weak_subjects']
            })

    total_quizzes = Quiz.query.filter(Quiz.subject_id.in_(subject_ids)).count()
    total_materials = StudyMaterial.query.filter(StudyMaterial.subject_id.in_(subject_ids)).count()
    pending_submissions = AssignmentSubmission.query.join(Assignment).filter(
        Assignment.subject_id.in_(subject_ids),
        AssignmentSubmission.marks_obtained.is_(None)
    ).count()

    recent_announcements = Announcement.query.filter_by(faculty_id=current_user.id).order_by(Announcement.created_at.desc()).limit(3).all()

    return render_template(
        'faculty/dashboard.html',
        taught_subjects=taught_subjects,
        total_students=len(students),
        struggling_students=struggling_students,
        total_quizzes=total_quizzes,
        total_materials=total_materials,
        pending_submissions=pending_submissions,
        recent_announcements=recent_announcements
    )


@app.route('/faculty/students')
@login_required
@role_required('faculty')
def faculty_students():
    taught_subjects = current_user.taught_subjects
    subject_ids = [s.id for s in taught_subjects]
    
    students = User.query.filter(User.role == 'student', User.enrolled_subjects.any(Subject.id.in_(subject_ids))).all()
    
    filter_struggling = request.args.get('filter') == 'struggling'
    
    student_cards = []
    for st in students:
        ana = analyze_weak_areas(st)
        is_struggling = len(ana['weak_subjects']) > 0 or ana['overall_attendance'] < 75.0
        
        if filter_struggling and not is_struggling:
            continue

        student_cards.append({
            'student': st,
            'analysis': ana,
            'is_struggling': is_struggling
        })

    return render_template('faculty/students.html', student_cards=student_cards, filter_struggling=filter_struggling)


@app.route('/faculty/attendance', methods=['GET', 'POST'])
@login_required
@role_required('faculty')
def faculty_attendance():
    taught_subjects = current_user.taught_subjects
    if not taught_subjects:
        flash("You are not currently assigned to any subjects.", "info")
        return render_template('faculty/attendance.html', taught_subjects=[])

    selected_subject_id = request.args.get('subject_id', type=int) or taught_subjects[0].id
    subject = Subject.query.get_or_404(selected_subject_id)
    students = subject.enrolled_students.all()

    today_str = date.today().strftime('%Y-%m-%d')
    filter_date_str = request.args.get('date', today_str)
    try:
        current_date = datetime.strptime(filter_date_str, '%Y-%m-%d').date()
    except ValueError:
        current_date = date.today()

    if request.method == 'POST':
        action = request.form.get('action')
        post_date_str = request.form.get('date', today_str)
        post_date = datetime.strptime(post_date_str, '%Y-%m-%d').date()

        for st in students:
            status = request.form.get(f'status_{st.id}', 'present')
            remarks = request.form.get(f'remarks_{st.id}', '')

            # Update or create
            record = AttendanceRecord.query.filter_by(
                subject_id=subject.id,
                student_id=st.id,
                date=post_date
            ).first()

            if record:
                record.status = status
                record.remarks = remarks
                record.faculty_id = current_user.id
            else:
                record = AttendanceRecord(
                    subject_id=subject.id,
                    student_id=st.id,
                    faculty_id=current_user.id,
                    date=post_date,
                    status=status,
                    remarks=remarks
                )
                db.session.add(record)

        db.session.commit()
        flash(f"Attendance for {subject.name} on {post_date} recorded successfully!", "success")
        return redirect(url_for('faculty_attendance', subject_id=subject.id, date=post_date_str))

    # Existing records for this date
    existing_records = {
        r.student_id: r for r in AttendanceRecord.query.filter_by(
            subject_id=subject.id,
            date=current_date
        ).all()
    }

    return render_template(
        'faculty/attendance.html',
        taught_subjects=taught_subjects,
        current_subject=subject,
        students=students,
        current_date=current_date,
        existing_records=existing_records
    )


@app.route('/faculty/materials', methods=['GET', 'POST'])
@login_required
@role_required('faculty')
def faculty_materials():
    taught_subjects = current_user.taught_subjects
    
    if request.method == 'POST':
        subject_id = int(request.form.get('subject_id'))
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        material_type = request.form.get('material_type', 'notes')

        file_name = None
        file_size_kb = 0
        if 'material_file' in request.files:
            file = request.files['material_file']
            if file and file.filename != '':
                sec_name = secure_filename(file.filename)
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], sec_name)
                file.save(save_path)
                file_name = sec_name
                file_size_kb = int(os.path.getsize(save_path) / 1024)

        if not file_name:
            file_name = f"{title.replace(' ', '_')}.pdf"
            file_size_kb = 1200

        material = StudyMaterial(
            subject_id=subject_id,
            faculty_id=current_user.id,
            title=title,
            description=description,
            material_type=material_type,
            file_name=file_name,
            file_size_kb=file_size_kb
        )
        db.session.add(material)
        db.session.commit()
        flash(f"Study material '{title}' uploaded and published to students!", "success")
        return redirect(url_for('faculty_materials'))

    materials = StudyMaterial.query.filter_by(faculty_id=current_user.id).order_by(StudyMaterial.created_at.desc()).all()
    return render_template('faculty/materials.html', taught_subjects=taught_subjects, materials=materials)


@app.route('/faculty/quizzes', methods=['GET', 'POST'])
@login_required
@role_required('faculty')
def faculty_quizzes():
    taught_subjects = current_user.taught_subjects

    if request.method == 'POST':
        subject_id = int(request.form.get('subject_id'))
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        time_limit = int(request.form.get('time_limit_minutes', 15))
        due_days = int(request.form.get('due_days', 7))

        quiz = Quiz(
            subject_id=subject_id,
            faculty_id=current_user.id,
            title=title,
            description=description,
            time_limit_minutes=time_limit,
            due_date=datetime.utcnow() + timedelta(days=due_days)
        )
        db.session.add(quiz)
        db.session.commit()

        # Parse questions (dynamic from form)
        question_count = int(request.form.get('question_count', 1))
        for i in range(1, question_count + 1):
            q_text = request.form.get(f'q_{i}_text')
            opt_a = request.form.get(f'q_{i}_a')
            opt_b = request.form.get(f'q_{i}_b')
            opt_c = request.form.get(f'q_{i}_c')
            opt_d = request.form.get(f'q_{i}_d')
            correct = request.form.get(f'q_{i}_correct', 'A')
            explanation = request.form.get(f'q_{i}_explanation', '')
            marks = int(request.form.get(f'q_{i}_marks', 2))

            if q_text and opt_a and opt_b:
                question = QuizQuestion(
                    quiz_id=quiz.id,
                    question_text=q_text,
                    option_a=opt_a,
                    option_b=opt_b,
                    option_c=opt_c or 'N/A',
                    option_d=opt_d or 'N/A',
                    correct_option=correct,
                    explanation=explanation,
                    marks=marks
                )
                db.session.add(question)

        db.session.commit()
        flash(f"Quiz '{title}' created and published successfully!", "success")
        return redirect(url_for('faculty_quizzes'))

    quizzes = Quiz.query.filter_by(faculty_id=current_user.id).order_by(Quiz.created_at.desc()).all()
    return render_template('faculty/quizzes.html', taught_subjects=taught_subjects, quizzes=quizzes)


@app.route('/faculty/assignments', methods=['GET', 'POST'])
@login_required
@role_required('faculty')
def faculty_assignments():
    taught_subjects = current_user.taught_subjects

    if request.method == 'POST':
        action = request.form.get('action')
        
        # Grading a submission
        if action == 'grade':
            submission_id = int(request.form.get('submission_id'))
            marks = float(request.form.get('marks'))
            feedback = request.form.get('feedback', '')
            
            sub = AssignmentSubmission.query.get_or_404(submission_id)
            sub.marks_obtained = marks
            sub.feedback = feedback
            sub.graded_at = datetime.utcnow()
            db.session.commit()
            flash(f"Grade and feedback submitted for {sub.student.full_name}.", "success")
            return redirect(url_for('faculty_assignments'))

        # Creating a new assignment
        subject_id = int(request.form.get('subject_id'))
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        max_marks = int(request.form.get('max_marks', 100))
        due_days = int(request.form.get('due_days', 7))

        asg = Assignment(
            subject_id=subject_id,
            faculty_id=current_user.id,
            title=title,
            description=description,
            max_marks=max_marks,
            due_date=datetime.utcnow() + timedelta(days=due_days)
        )
        db.session.add(asg)
        db.session.commit()
        flash(f"Assignment '{title}' posted successfully!", "success")
        return redirect(url_for('faculty_assignments'))

    assignments = Assignment.query.filter_by(faculty_id=current_user.id).order_by(Assignment.created_at.desc()).all()
    return render_template('faculty/assignments.html', taught_subjects=taught_subjects, assignments=assignments)


@app.route('/faculty/announcements', methods=['GET', 'POST'])
@login_required
@role_required('faculty')
def faculty_announcements():
    taught_subjects = current_user.taught_subjects

    if request.method == 'POST':
        subject_id_raw = request.form.get('subject_id')
        subject_id = int(subject_id_raw) if subject_id_raw and subject_id_raw != 'all' else None
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        priority = request.form.get('priority', 'normal')

        ann = Announcement(
            faculty_id=current_user.id,
            subject_id=subject_id,
            title=title,
            content=content,
            priority=priority
        )
        db.session.add(ann)
        db.session.commit()
        flash("Announcement broadcasted successfully!", "success")
        return redirect(url_for('faculty_announcements'))

    announcements = Announcement.query.filter_by(faculty_id=current_user.id).order_by(Announcement.created_at.desc()).all()
    return render_template('faculty/announcements.html', taught_subjects=taught_subjects, announcements=announcements)


@app.route('/faculty/reports')
@login_required
@role_required('faculty')
def faculty_reports():
    taught_subjects = current_user.taught_subjects
    subject_ids = [s.id for s in taught_subjects]

    students = User.query.filter(User.role == 'student', User.enrolled_subjects.any(Subject.id.in_(subject_ids))).all()
    
    # Calculate performance metrics
    subject_stats = []
    for subj in taught_subjects:
        all_attempts = QuizAttempt.query.join(Quiz).filter(Quiz.subject_id == subj.id).all()
        quiz_avg = (sum(a.percentage for a in all_attempts) / len(all_attempts)) if all_attempts else 0
        
        att_records = AttendanceRecord.query.filter_by(subject_id=subj.id).all()
        if att_records:
            att_pct = round((sum(1 for a in att_records if a.status in ['present', 'late']) / len(att_records)) * 100, 1)
        else:
            att_pct = 0.0

        subject_stats.append({
            'subject': subj,
            'students_count': subj.enrolled_students.count(),
            'quiz_avg': round(quiz_avg, 1),
            'attendance_pct': att_pct
        })

    return render_template('faculty/reports.html', taught_subjects=taught_subjects, subject_stats=subject_stats, total_students=len(students))


# ==========================================
# ADMIN PORTAL ROUTES
# ==========================================

@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    total_students = User.query.filter_by(role='student').count()
    total_faculty = User.query.filter_by(role='faculty').count()
    total_subjects = Subject.query.count()
    total_quizzes = Quiz.query.count()
    total_materials = StudyMaterial.query.count()

    recent_users = User.query.order_by(User.created_at.desc()).limit(6).all()
    subjects = Subject.query.all()

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        total_faculty=total_faculty,
        total_subjects=total_subjects,
        total_quizzes=total_quizzes,
        total_materials=total_materials,
        recent_users=recent_users,
        subjects=subjects
    )


@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_users():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'toggle_status':
            user_id = int(request.form.get('user_id'))
            user = User.query.get_or_404(user_id)
            user.is_active_account = not user.is_active_account
            db.session.commit()
            state = "activated" if user.is_active_account else "deactivated"
            flash(f"Account for {user.full_name} has been {state}.", "info")
            return redirect(url_for('admin_users'))

        if action == 'delete':
            user_id = int(request.form.get('user_id'))
            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            flash("User removed successfully.", "warning")
            return redirect(url_for('admin_users'))

        # Create user
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', 'password123')
        role = request.form.get('role', 'student')
        identifier = request.form.get('identifier', '')
        department = request.form.get('department', 'Computer Science')

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for('admin_users'))

        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            identifier=identifier,
            department=department
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash(f"New {role.title()} '{full_name}' created successfully!", "success")
        return redirect(url_for('admin_users'))

    role_filter = request.args.get('role')
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    users = query.order_by(User.role, User.full_name).all()

    return render_template('admin/users.html', users=users, current_filter=role_filter)


@app.route('/admin/subjects', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_subjects():
    faculty_list = User.query.filter_by(role='faculty').all()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'delete':
            subject_id = int(request.form.get('subject_id'))
            subj = Subject.query.get_or_404(subject_id)
            db.session.delete(subj)
            db.session.commit()
            flash(f"Subject '{subj.name}' removed.", "warning")
            return redirect(url_for('admin_subjects'))

        if action == 'assign_faculty':
            subject_id = int(request.form.get('subject_id'))
            faculty_id = int(request.form.get('faculty_id'))
            subj = Subject.query.get_or_404(subject_id)
            subj.faculty_id = faculty_id
            db.session.commit()
            flash(f"Faculty assigned to '{subj.name}'.", "success")
            return redirect(url_for('admin_subjects'))

        # Create Subject
        code = request.form.get('code', '').strip().upper()
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        department = request.form.get('department', 'Computer Science')
        credits = int(request.form.get('credits', 4))
        semester = int(request.form.get('semester', 5))
        faculty_id = int(request.form.get('faculty_id')) if request.form.get('faculty_id') else None

        if Subject.query.filter_by(code=code).first():
            flash(f"Subject code '{code}' already exists.", "danger")
            return redirect(url_for('admin_subjects'))

        new_subject = Subject(
            code=code,
            name=name,
            description=description,
            department=department,
            credits=credits,
            semester=semester,
            faculty_id=faculty_id
        )
        db.session.add(new_subject)
        db.session.commit()
        flash(f"Subject '{name} ({code})' created successfully!", "success")
        return redirect(url_for('admin_subjects'))

    subjects = Subject.query.order_by(Subject.code).all()
    return render_template('admin/subjects.html', subjects=subjects, faculty_list=faculty_list)


@app.route('/admin/seed-reset', methods=['POST'])
@login_required
@role_required('admin')
def admin_seed_reset():
    db.drop_all()
    db.create_all()
    seed_database()
    flash("Database successfully reset and re-seeded with demo data!", "success")
    return redirect(url_for('admin_dashboard'))


# File download endpoint for uploaded materials
@app.route('/downloads/<path:filename>')
@login_required
def download_file(filename):
    # Check if exists on disk; if mock/seeded, generate sample notes response
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        # Create a sample study document so the download works perfectly
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"=== SMARTEDU STUDY MATERIAL ===\nDocument: {filename}\nGenerated for: {current_user.full_name}\n\nKey Concepts & High-Yield Examination Notes:\n1. Foundation Definitions and Mathematical Bounds\n2. Practical Step-by-Step Problem Solving Procedures\n3. Common Pitfalls and Boundary Test Cases\n\nStudy Well and Aim for Excellence!")
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


# Initialize DB on first run
with app.app_context():
    db.create_all()
    seed_database()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
