import json
from datetime import datetime, date, timedelta
from models import (
    db, User, Subject, StudyMaterial, Quiz, QuizQuestion,
    QuizAttempt, Assignment, AssignmentSubmission, AttendanceRecord,
    Announcement, TimetableSlot, AIChatMessage
)

def seed_database():
    """Populates the database with realistic demo accounts and academic data."""
    # Check if already seeded
    if User.query.first():
        print("Database already contains data. Skipping seeding.")
        return

    print("Seeding database with demo users, subjects, quizzes, and materials...")

    # 1. Users
    admin = User(
        username="admin",
        email="admin@smartedu.edu",
        full_name="System Administrator",
        role="admin",
        identifier="ADM-001",
        department="Academic Administration",
        avatar_color="purple"
    )
    admin.set_password("admin123")
    db.session.add(admin)

    # Faculty members
    faculty1 = User(
        username="sarah_faculty",
        email="sarah.chen@smartedu.edu",
        full_name="Dr. Sarah Chen",
        role="faculty",
        identifier="FAC-101",
        department="Computer Science",
        avatar_color="emerald"
    )
    faculty1.set_password("faculty123")

    faculty2 = User(
        username="priya_faculty",
        email="priya.sharma@smartedu.edu",
        full_name="Dr. Priya Sharma",
        role="faculty",
        identifier="FAC-102",
        department="Computer Science",
        avatar_color="blue"
    )
    faculty2.set_password("faculty123")

    faculty3 = User(
        username="alan_faculty",
        email="alan.vance@smartedu.edu",
        full_name="Prof. Alan Vance",
        role="faculty",
        identifier="FAC-103",
        department="Computer Science",
        avatar_color="indigo"
    )
    faculty3.set_password("faculty123")

    db.session.add_all([faculty1, faculty2, faculty3])

    # Students
    student1 = User(
        username="alex_student",
        email="alex.mercer@smartedu.edu",
        full_name="Alex Mercer",
        role="student",
        identifier="STU-2024-001",
        department="Computer Science",
        semester=5,
        avatar_color="blue"
    )
    student1.set_password("student123")

    student2 = User(
        username="maya_student",
        email="maya.lin@smartedu.edu",
        full_name="Maya Lin",
        role="student",
        identifier="STU-2024-002",
        department="Computer Science",
        semester=5,
        avatar_color="rose"
    )
    student2.set_password("student123")

    student3 = User(
        username="jordan_student",
        email="jordan.lee@smartedu.edu",
        full_name="Jordan Lee",
        role="student",
        identifier="STU-2024-003",
        department="Computer Science",
        semester=5,
        avatar_color="amber"
    )
    student3.set_password("student123")

    student4 = User(
        username="zara_student",
        email="zara.patel@smartedu.edu",
        full_name="Zara Patel",
        role="student",
        identifier="STU-2024-004",
        department="Computer Science",
        semester=5,
        avatar_color="teal"
    )
    student4.set_password("student123")

    db.session.add_all([student1, student2, student3, student4])
    db.session.commit()

    # 2. Subjects
    subj_dsa = Subject(
        code="CS301",
        name="Data Structures & Algorithms",
        description="Comprehensive study of tree algorithms, balanced search trees, graph theory, dynamic programming, and complexity bounds.",
        department="Computer Science",
        credits=4,
        semester=5,
        faculty_id=faculty1.id
    )
    subj_dbms = Subject(
        code="CS302",
        name="Database Management Systems",
        description="Relational data models, SQL querying, relational algebra, normal forms (1NF through BCNF), indexing, and transaction management.",
        department="Computer Science",
        credits=4,
        semester=5,
        faculty_id=faculty2.id
    )
    subj_cn = Subject(
        code="CS303",
        name="Computer Networks",
        description="OSI and TCP/IP protocol architectures, packet routing algorithms, congestion control, subnetting, and socket programming.",
        department="Computer Science",
        credits=3,
        semester=5,
        faculty_id=faculty3.id
    )
    subj_os = Subject(
        code="CS304",
        name="Operating Systems",
        description="Process concurrency, mutual exclusion, CPU scheduling algorithms, virtual memory paging, and Unix file systems.",
        department="Computer Science",
        credits=4,
        semester=5,
        faculty_id=faculty1.id
    )
    subj_ml = Subject(
        code="CS305",
        name="Machine Learning Fundamentals",
        description="Supervised and unsupervised learning, regression, classification, neural network basics, and model evaluation metrics.",
        department="Computer Science",
        credits=3,
        semester=5,
        faculty_id=faculty2.id
    )

    db.session.add_all([subj_dsa, subj_dbms, subj_cn, subj_os, subj_ml])
    db.session.commit()

    # Enroll students
    all_students = [student1, student2, student3, student4]
    all_subjects = [subj_dsa, subj_dbms, subj_cn, subj_os, subj_ml]
    for s in all_students:
        for subj in all_subjects:
            s.enrolled_subjects.append(subj)
    db.session.commit()

    # 3. Study Materials
    m1 = StudyMaterial(
        subject_id=subj_dsa.id,
        faculty_id=faculty1.id,
        title="Module 3: Balanced Binary Trees & AVL Rotations",
        description="Full lecture presentation on balance factors, left-right rotations, and worst-case insertion complexity.",
        material_type="notes",
        file_name="AVL_Trees_Master_Notes.pdf",
        file_size_kb=1420
    )
    m2 = StudyMaterial(
        subject_id=subj_dsa.id,
        faculty_id=faculty1.id,
        title="Graph Algorithms Cheatsheet: Dijkstra & Kruskal",
        description="Step-by-step pseudo-code and trace tables for shortest paths and minimum spanning trees.",
        material_type="cheatsheet",
        file_name="Graph_Algorithms_Cheatsheet.pdf",
        file_size_kb=860
    )
    m3 = StudyMaterial(
        subject_id=subj_dbms.id,
        faculty_id=faculty2.id,
        title="Complete SQL Optimization & B+ Tree Indexing Guide",
        description="Hands-on guide to indexing structures, clustered vs non-clustered indexes, and query execution plans.",
        material_type="notes",
        file_name="DBMS_Indexing_Guide.pdf",
        file_size_kb=2310
    )
    m4 = StudyMaterial(
        subject_id=subj_cn.id,
        faculty_id=faculty3.id,
        title="TCP 3-Way Handshake & Flow Control Architecture",
        description="Detailed packet exchange sequence diagrams, sliding window calculations, and congestion window states.",
        material_type="slides",
        file_name="TCP_Flow_Control_Slides.pdf",
        file_size_kb=1750
    )
    m5 = StudyMaterial(
        subject_id=subj_os.id,
        faculty_id=faculty1.id,
        title="Virtual Memory & Page Replacement Algorithms",
        description="Comparison of FIFO, Optimal, and LRU page replacement policies with Belady's anomaly explained.",
        material_type="notes",
        file_name="Virtual_Memory_Lecture.pdf",
        file_size_kb=1920
    )
    m6 = StudyMaterial(
        subject_id=subj_ml.id,
        faculty_id=faculty2.id,
        title="Introduction to Gradient Descent & Cost Functions",
        description="Mathematical foundations of convex optimization, learning rates, and batch vs stochastic gradient descent.",
        material_type="reference",
        file_name="ML_Gradient_Descent_Derivations.pdf",
        file_size_kb=1580
    )
    db.session.add_all([m1, m2, m3, m4, m5, m6])

    # 4. Quizzes
    quiz1 = Quiz(
        subject_id=subj_dsa.id,
        faculty_id=faculty1.id,
        title="DSA Mastery Check: Binary Trees & Heaps",
        description="15-minute diagnostic quiz assessing trees traversal, balance factors, and binary heap operations.",
        time_limit_minutes=15,
        due_date=datetime.utcnow() + timedelta(days=4)
    )
    db.session.add(quiz1)
    db.session.commit()

    q1_1 = QuizQuestion(
        quiz_id=quiz1.id,
        question_text="What is the maximum number of nodes in a binary tree of depth/height 'h' (root at height 1)?",
        option_a="2^h",
        option_b="2^h - 1",
        option_c="2^(h-1)",
        option_d="2^(h+1)",
        correct_option="B",
        explanation="For a full binary tree of height h, the total number of nodes is 1 + 2 + 4 + ... + 2^(h-1) = 2^h - 1.",
        marks=2
    )
    q1_2 = QuizQuestion(
        quiz_id=quiz1.id,
        question_text="In an AVL tree, what is the maximum permissible difference between the heights of left and right subtrees?",
        option_a="0",
        option_b="1",
        option_c="2",
        option_d="No limit",
        correct_option="B",
        explanation="An AVL tree maintains the balance factor (height(left) - height(right)) within {-1, 0, 1}.",
        marks=2
    )
    q1_3 = QuizQuestion(
        quiz_id=quiz1.id,
        question_text="What is the worst-case time complexity of extracting the minimum element from a Binary Min-Heap of size N?",
        option_a="O(1)",
        option_b="O(log N)",
        option_c="O(N)",
        option_d="O(N log N)",
        correct_option="B",
        explanation="Extracting min removes the root and bubbles down the last element, taking at most the height of tree: O(log N).",
        marks=2
    )
    q1_4 = QuizQuestion(
        quiz_id=quiz1.id,
        question_text="Which tree traversal visits nodes in non-decreasing order when performed on a Binary Search Tree?",
        option_a="Pre-order",
        option_b="Post-order",
        option_c="In-order",
        option_d="Level-order",
        correct_option="C",
        explanation="In-order traversal visits Left Subtree -> Root -> Right Subtree, resulting in sorted ascending order for BST.",
        marks=2
    )
    db.session.add_all([q1_1, q1_2, q1_3, q1_4])

    quiz2 = Quiz(
        subject_id=subj_dbms.id,
        faculty_id=faculty2.id,
        title="DBMS Challenge: Normalization & ACID Properties",
        description="Comprehensive evaluation on relational normalization forms, primary keys, and transaction integrity.",
        time_limit_minutes=20,
        due_date=datetime.utcnow() + timedelta(days=6)
    )
    db.session.add(quiz2)
    db.session.commit()

    q2_1 = QuizQuestion(
        quiz_id=quiz2.id,
        question_text="Which Normal Form requires that no non-prime attribute is transitively dependent on any candidate key?",
        option_a="1NF",
        option_b="2NF",
        option_c="3NF",
        option_d="BCNF",
        correct_option="C",
        explanation="3NF strictly disallows transitive functional dependencies (A -> B and B -> C where C is non-prime).",
        marks=2
    )
    q2_2 = QuizQuestion(
        quiz_id=quiz2.id,
        question_text="Which ACID property guarantees that either all operations of a transaction are reflected in database or none are?",
        option_a="Atomicity",
        option_b="Consistency",
        option_c="Isolation",
        option_d="Durability",
        correct_option="A",
        explanation="Atomicity guarantees an 'all-or-nothing' execution rule for transactions.",
        marks=2
    )
    q2_3 = QuizQuestion(
        quiz_id=quiz2.id,
        question_text="Which data structure is primarily utilized for disk-resident database indexing to minimize I/O block reads?",
        option_a="Binary Search Tree",
        option_b="Red-Black Tree",
        option_c="B+ Tree",
        option_d="Linked List",
        correct_option="C",
        explanation="B+ Trees have very high fan-out, reducing tree height and disk seek overhead significantly.",
        marks=2
    )
    db.session.add_all([q2_1, q2_2, q2_3])

    quiz3 = Quiz(
        subject_id=subj_cn.id,
        faculty_id=faculty3.id,
        title="Computer Networks: OSI Model & TCP/UDP Basics",
        description="Core concepts quiz on transport layers, socket addressing, and transmission reliability.",
        time_limit_minutes=15,
        due_date=datetime.utcnow() + timedelta(days=2)
    )
    db.session.add(quiz3)
    db.session.commit()

    q3_1 = QuizQuestion(
        quiz_id=quiz3.id,
        question_text="Which protocol is connection-oriented, guarantees ordered delivery, and performs congestion control?",
        option_a="UDP",
        option_b="TCP",
        option_c="IP",
        option_d="ICMP",
        correct_option="B",
        explanation="Transmission Control Protocol (TCP) establishes reliable connections with packet sequencing and retransmissions.",
        marks=2
    )
    q3_2 = QuizQuestion(
        quiz_id=quiz3.id,
        question_text="At which layer of the OSI model does IP routing occur?",
        option_a="Data Link Layer",
        option_b="Transport Layer",
        option_c="Network Layer",
        option_d="Session Layer",
        correct_option="C",
        explanation="The Network Layer (Layer 3) handles logical packet routing and forwarding via IP addresses.",
        marks=2
    )
    db.session.add_all([q3_1, q3_2])
    db.session.commit()

    # Pre-recorded Quiz Attempts
    # Alex Mercer took quiz 1 and quiz 2 with good scores
    att1 = QuizAttempt(
        quiz_id=quiz1.id,
        student_id=student1.id,
        score=8.0,
        total_possible=8.0,
        percentage=100.0,
        submitted_at=datetime.utcnow() - timedelta(days=2),
        answers_json=json.dumps({"1": "B", "2": "B", "3": "B", "4": "C"})
    )
    att2 = QuizAttempt(
        quiz_id=quiz2.id,
        student_id=student1.id,
        score=4.0,
        total_possible=6.0,
        percentage=66.7,
        submitted_at=datetime.utcnow() - timedelta(days=1),
        answers_json=json.dumps({"1": "C", "2": "A", "3": "A"})
    )

    # Maya took quiz 1
    att3 = QuizAttempt(
        quiz_id=quiz1.id,
        student_id=student2.id,
        score=6.0,
        total_possible=8.0,
        percentage=75.0,
        submitted_at=datetime.utcnow() - timedelta(days=3),
        answers_json=json.dumps({"1": "B", "2": "B", "3": "A", "4": "C"})
    )

    # Jordan (struggling student) scored low on quiz 1 and quiz 2
    att4 = QuizAttempt(
        quiz_id=quiz1.id,
        student_id=student3.id,
        score=2.0,
        total_possible=8.0,
        percentage=25.0,
        submitted_at=datetime.utcnow() - timedelta(days=2),
        answers_json=json.dumps({"1": "A", "2": "C", "3": "B", "4": "A"})
    )
    att5 = QuizAttempt(
        quiz_id=quiz2.id,
        student_id=student3.id,
        score=2.0,
        total_possible=6.0,
        percentage=33.3,
        submitted_at=datetime.utcnow() - timedelta(days=1),
        answers_json=json.dumps({"1": "A", "2": "B", "3": "C"})
    )
    db.session.add_all([att1, att2, att3, att4, att5])

    # 5. Assignments
    asg1 = Assignment(
        subject_id=subj_dsa.id,
        faculty_id=faculty1.id,
        title="Assignment 1: Dijkstra's Shortest Path Implementation",
        description="Implement Dijkstra's shortest path algorithm using a Min-Heap priority queue in Python or C++. Include complexity analysis report and edge case test suits (disconnected graphs, negative cycle detection).",
        max_marks=50,
        due_date=datetime.utcnow() + timedelta(days=5)
    )
    asg2 = Assignment(
        subject_id=subj_dbms.id,
        faculty_id=faculty2.id,
        title="Assignment 2: Schema Design & 3NF Normalization Case Study",
        description="Design a complete relational database for a hospital management system. Provide ER diagrams, functional dependencies list, and step-by-step decomposition to 3NF and BCNF.",
        max_marks=100,
        due_date=datetime.utcnow() + timedelta(days=7)
    )
    asg3 = Assignment(
        subject_id=subj_cn.id,
        faculty_id=faculty3.id,
        title="Assignment 3: Wireshark Packet Inspection & HTTP Analysis",
        description="Capture and inspect TCP 3-way handshake packets and TLS ClientHello handshakes using Wireshark. Submit a 4-page analysis with screenshots.",
        max_marks=50,
        due_date=datetime.utcnow() + timedelta(days=3)
    )
    db.session.add_all([asg1, asg2, asg3])
    db.session.commit()

    # Assignment Submissions
    sub1 = AssignmentSubmission(
        assignment_id=asg1.id,
        student_id=student1.id,
        submission_text="Implemented Dijkstra's algorithm using heapq in Python. Handled infinity distance initialization, adjacency list representation, and visited sets. Verified across 10 random connected graphs.",
        submitted_at=datetime.utcnow() - timedelta(days=1),
        marks_obtained=47.0,
        feedback="Excellent modular implementation! Clean code structure and comprehensive boundary condition checks.",
        graded_at=datetime.utcnow()
    )
    sub2 = AssignmentSubmission(
        assignment_id=asg2.id,
        student_id=student1.id,
        submission_text="Hospital Management schema decomposed into 7 normalized tables. All functional dependencies satisfy 3NF. SQL DDL scripts included.",
        submitted_at=datetime.utcnow() - timedelta(hours=14),
        marks_obtained=92.0,
        feedback="Very well presented ER diagram and accurate relational schemas.",
        graded_at=datetime.utcnow()
    )
    sub3 = AssignmentSubmission(
        assignment_id=asg1.id,
        student_id=student3.id, # Jordan
        submission_text="Incomplete Dijkstra script without priority queue; O(V^2) implementation.",
        submitted_at=datetime.utcnow() - timedelta(days=1),
        marks_obtained=22.0,
        feedback="Code failed min-heap complexity constraint. Please review priority queue modules and resubmit during revision week.",
        graded_at=datetime.utcnow()
    )
    db.session.add_all([sub1, sub2, sub3])

    # 6. Attendance Records (Last 14 days)
    today = date.today()
    for day_offset in range(12, 0, -1):
        record_date = today - timedelta(days=day_offset)
        # Skip weekends
        if record_date.weekday() >= 5:
            continue

        for subj, fac in [(subj_dsa, faculty1), (subj_dbms, faculty2), (subj_cn, faculty3), (subj_os, faculty1)]:
            # Alex is mostly present
            db.session.add(AttendanceRecord(
                subject_id=subj.id,
                student_id=student1.id,
                faculty_id=fac.id,
                date=record_date,
                status="present" if day_offset % 7 != 0 else "late",
                remarks="Active participant"
            ))
            # Maya is 100% present
            db.session.add(AttendanceRecord(
                subject_id=subj.id,
                student_id=student2.id,
                faculty_id=fac.id,
                date=record_date,
                status="present",
                remarks="Punctual"
            ))
            # Jordan has high absences (struggling student demonstration)
            jordan_status = "absent" if (day_offset % 3 == 0 or day_offset % 4 == 0) else "present"
            db.session.add(AttendanceRecord(
                subject_id=subj.id,
                student_id=student3.id,
                faculty_id=fac.id,
                date=record_date,
                status=jordan_status,
                remarks="Unexcused absence" if jordan_status == "absent" else "Attended"
            ))

    # 7. Announcements
    ann1 = Announcement(
        faculty_id=faculty1.id,
        subject_id=subj_dsa.id,
        title="📢 Dijkstra Assignment Doubt Clearing Session",
        content="Join Dr. Sarah Chen this Thursday at 4:30 PM in Room 302 or Google Meet for edge cases walkthrough and priority queue optimizations.",
        priority="urgent"
    )
    ann2 = Announcement(
        faculty_id=faculty2.id,
        subject_id=subj_dbms.id,
        title="🔔 Mid-Semester Examination Syllabus Update",
        content="Mid-sem exams begin next Monday. Syllabus includes ER models, Relational Algebra, SQL queries, and Normalization up to BCNF. Please review notes module 3.",
        priority="normal"
    )
    ann3 = Announcement(
        faculty_id=faculty3.id,
        subject_id=None, # Global
        title="🌟 Annual SmartEdu Hackathon & Project Expo Registration Open",
        content="Students from all semesters are invited to form teams of 3-4 members. Prizes include cloud credits, internship fast-tracks, and hardware kits.",
        priority="info"
    )
    db.session.add_all([ann1, ann2, ann3])

    # 8. Timetable Slots for Alex Mercer
    timetable_data = [
        # Monday
        {"day": "Monday", "start": "09:00", "end": "10:30", "subj": "Data Structures & Algorithms", "type": "Lecture", "room": "Hall A"},
        {"day": "Monday", "start": "11:00", "end": "12:30", "subj": "Database Management Systems", "type": "Lecture", "room": "Hall B"},
        {"day": "Monday", "start": "14:00", "end": "16:00", "subj": "Data Structures Lab", "type": "Lab Session", "room": "CS Lab 2"},
        {"day": "Monday", "start": "17:00", "end": "18:30", "subj": "AI Personalized Revision: Trees", "type": "Self Study", "room": "Library / Dorm"},

        # Tuesday
        {"day": "Tuesday", "start": "09:30", "end": "11:00", "subj": "Computer Networks", "type": "Lecture", "room": "Hall C"},
        {"day": "Tuesday", "start": "11:30", "end": "13:00", "subj": "Operating Systems", "type": "Lecture", "room": "Hall A"},
        {"day": "Tuesday", "start": "15:00", "end": "16:30", "subj": "Machine Learning Fundamentals", "type": "Lecture", "room": "Hall D"},

        # Wednesday
        {"day": "Wednesday", "start": "09:00", "end": "10:30", "subj": "Data Structures & Algorithms", "type": "Lecture", "room": "Hall A"},
        {"day": "Wednesday", "start": "11:00", "end": "13:00", "subj": "DBMS SQL Practicum", "type": "Lab Session", "room": "CS Lab 1"},
        {"day": "Wednesday", "start": "16:00", "end": "18:00", "subj": "Assignment Coding: Dijkstra", "type": "Self Study", "room": "Personal Desk"},

        # Thursday
        {"day": "Thursday", "start": "10:00", "end": "11:30", "subj": "Computer Networks", "type": "Lecture", "room": "Hall C"},
        {"day": "Thursday", "start": "13:00", "end": "14:30", "subj": "Operating Systems", "type": "Lecture", "room": "Hall A"},
        {"day": "Thursday", "start": "15:30", "end": "17:00", "subj": "Active Recall & Quiz Revision", "type": "Self Study", "room": "SmartEdu Portal"},

        # Friday
        {"day": "Friday", "start": "09:00", "end": "10:30", "subj": "Database Management Systems", "type": "Lecture", "room": "Hall B"},
        {"day": "Friday", "start": "11:00", "end": "12:30", "subj": "Machine Learning Fundamentals", "type": "Lecture", "room": "Hall D"},
        {"day": "Friday", "start": "14:00", "end": "16:00", "subj": "Weekly Test Review & Doubt Clearing", "type": "Revision", "room": "Room 302"},
    ]

    for item in timetable_data:
        db.session.add(TimetableSlot(
            student_id=student1.id,
            day_of_week=item["day"],
            start_time=item["start"],
            end_time=item["end"],
            subject_name=item["subj"],
            activity_type=item["type"],
            room=item["room"],
            is_custom=False
        ))

    # 9. Initial AI Chat Messages for Student Alex
    m_user = AIChatMessage(
        student_id=student1.id,
        sender="user",
        message="Can you explain the difference between B-Trees and B+ Trees in DBMS?",
        subject_tag="Database Management Systems",
        timestamp=datetime.utcnow() - timedelta(hours=3)
    )
    m_ai = AIChatMessage(
        student_id=student1.id,
        sender="ai",
        message=(
            "### 🎯 B-Tree vs. B+ Tree Key Differences\n\n"
            "1. **Data Pointers Location**:\n"
            "   - In a **B-Tree**, data pointers (actual records) can exist at internal nodes AND leaf nodes.\n"
            "   - In a **B+ Tree**, data pointers exist **ONLY at leaf nodes**. Internal nodes strictly store index keys for navigation.\n\n"
            "2. **Range Queries & Leaf Linking**:\n"
            "   - **B+ Tree leaves are linked via a doubly linked list**, making sequential range scans (e.g. `WHERE salary BETWEEN 50000 AND 80000`) blazing fast O(log N + k).\n"
            "   - B-Trees require expensive full in-order traversal across multiple disk blocks for range queries.\n\n"
            "3. **Height & Disk I/O**:\n"
            "   - Because B+ tree internal nodes don't carry records, higher fan-out fits into each disk block, keeping the tree shorter and reducing disk I/O.\n\n"
            "💡 *Exam Tip: Almost all production relational databases (MySQL InnoDB, PostgreSQL) use B+ Trees for indexes!*"
        ),
        subject_tag="Database Management Systems",
        timestamp=datetime.utcnow() - timedelta(hours=3) + timedelta(seconds=2)
    )
    db.session.add_all([m_user, m_ai])

    db.session.commit()
    print("Database seeding completed successfully!")
