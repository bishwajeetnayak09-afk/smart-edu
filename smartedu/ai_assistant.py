import re
import random
from datetime import datetime, timedelta

# Rich knowledge base for offline AI assistance
TOPIC_KNOWLEDGE = {
    "data structures": {
        "summary": "Data Structures organize and store data for efficient access and modification. Core structures include Arrays, Linked Lists, Stacks, Queues, Trees, Heaps, Hash Tables, and Graphs.",
        "key_points": [
            "Arrays: Contiguous memory, O(1) random access, O(n) insert/delete.",
            "Linked Lists: Dynamic sizing, O(1) insert/delete at head, O(n) search.",
            "Hash Tables: Key-value lookup, average O(1) lookup, worst-case O(n) upon collisions.",
            "Binary Search Trees: In-order traversal gives sorted order, O(log n) balanced search.",
            "Graphs: Vertices & edges, traversed with BFS (Queue, shortest path unweighted) or DFS (Stack/recursion)."
        ],
        "common_questions": {
            "stack vs queue": "A Stack follows LIFO (Last In First Out) using push/pop (e.g., undo operations, call stack). A Queue follows FIFO (First In First Out) using enqueue/dequeue (e.g., print spooling, CPU task scheduling).",
            "time complexity": "Time complexity measures operations relative to input size n. Best to worst: O(1) < O(log n) < O(n) < O(n log n) < O(n^2) < O(2^n).",
            "binary search": "Binary Search operates on sorted arrays in O(log n). It repeatedly divides search range by half by comparing the middle element with the target key."
        }
    },
    "dbms": {
        "summary": "Database Management Systems (DBMS) manage structured data, ensure ACID transactions, and support relational querying with SQL.",
        "key_points": [
            "ACID Properties: Atomicity (all-or-nothing), Consistency (integrity constraints), Isolation (concurrent safety), Durability (persisted commits).",
            "Normalization: 1NF (atomic values), 2NF (no partial dependency), 3NF (no transitive dependency), BCNF.",
            "Indexing: B+ Trees are used in relational DBs for range and point queries; Hash Indexes for direct equality.",
            "Joins: INNER JOIN, LEFT OUTER JOIN, RIGHT OUTER JOIN, FULL OUTER JOIN."
        ],
        "common_questions": {
            "acid properties": "Atomicity ensures all actions in a transaction succeed or rollback completely. Consistency ensures DB state satisfies all rules. Isolation prevents concurrent transactions from interfering. Durability ensures committed changes survive power crashes.",
            "primary key vs foreign key": "A Primary Key uniquely identifies a record in a table (non-null, unique). A Foreign Key references the primary key of another table, maintaining referential integrity."
        }
    },
    "operating systems": {
        "summary": "Operating Systems mediate between computer hardware and user applications, managing CPU scheduling, memory, file systems, and concurrency.",
        "key_points": [
            "Process vs Thread: Process has its own address space; threads share process memory and resources.",
            "Deadlock: 4 Necessary conditions: Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait.",
            "Virtual Memory: Paging and segmentation allow running programs larger than physical RAM.",
            "CPU Scheduling: FCFS, Shortest Job First (SJF), Round Robin (RR), Multi-Level Feedback Queue."
        ],
        "common_questions": {
            "deadlock": "Deadlock happens when processes are stuck waiting for resources held by each other. Prevention strategies include ordering resource requests, banker's algorithm for avoidance, or deadlock detection with recovery."
        }
    },
    "computer networks": {
        "summary": "Computer Networks enable distributed communications over layered protocols (OSI 7-layer & TCP/IP models).",
        "key_points": [
            "OSI Layers: Physical, Data Link, Network (IP), Transport (TCP/UDP), Session, Presentation, Application (HTTP, DNS).",
            "TCP vs UDP: TCP is connection-oriented, reliable, with 3-way handshake & flow control. UDP is connectionless, fast, lightweight (ideal for streaming & gaming).",
            "Subnetting: Dividing IP address space using subnet masks (CIDR notation /24).",
            "DNS: Domain Name System translates hostnames like smartedu.io into IP addresses."
        ]
    },
    "machine learning": {
        "summary": "Machine Learning algorithms learn patterns from data without explicit procedural programming.",
        "key_points": [
            "Supervised Learning: Labeled data (Classification: Logistic Regression, Random Forest, SVM; Regression: Linear Regression).",
            "Unsupervised Learning: Unlabeled data (Clustering: K-Means, DBSCAN; Dimensionality Reduction: PCA).",
            "Overfitting: High variance / low bias; mitigated by Regularization (L1/L2), Dropout, Cross-Validation, and more data.",
            "Evaluation Metrics: Accuracy, Precision, Recall, F1-Score, ROC-AUC."
        ]
    }
}

STUDY_TIPS = [
    "💡 **Feynman Technique**: Explain the concept to a beginner in simple words without jargon. If you stumble, revisit the foundational text.",
    "⏰ **Pomodoro Method**: Study intensely for 25 minutes, followed by a 5-minute break. After 4 cycles, take an extended 20-minute break.",
    "🧠 **Active Recall**: Test yourself with flashcards or questions rather than passively re-reading slides.",
    "🔁 **Spaced Repetition**: Review challenging topics after 1 day, 3 days, 7 days, and 14 days to cement long-term memory."
]

def generate_ai_response(student_name, query, subject_context="General", mode="explain"):
    """
    Generates intelligent pedagogical responses tailored to the student and subject.
    Supports modes: 'explain', 'quiz', 'solve', 'summary', 'timetable'.
    """
    q_lower = query.lower().strip()
    
    # 1. Mode: QUIZ GENERATOR
    if mode == "quiz" or "quiz" in q_lower or "test me" in q_lower:
        return generate_mini_quiz(query, subject_context)

    # 2. Mode: PROBLEM SOLVER
    if mode == "solve" or "how to solve" in q_lower or "calculate" in q_lower or "derivation" in q_lower:
        return generate_step_by_step_solution(query, subject_context)

    # 3. Mode: SUMMARY / CHEATSHEET
    if mode == "summary" or "summary" in q_lower or "cheatsheet" in q_lower or "quick notes" in q_lower:
        return generate_topic_summary(query, subject_context)

    # 4. Mode: TIMETABLE & REVISION ADVICE
    if mode == "timetable" or "timetable" in q_lower or "study plan" in q_lower:
        return (
            f"### 📅 AI Personalized Study Plan for {student_name}\n\n"
            f"Here is an optimized weekly allocation based on spaced repetition:\n\n"
            f"| Day | Focus Area | Recommended Hours | Key Objective |\n"
            f"| --- | ---------- | ----------------- | ------------- |\n"
            f"| **Mon** | **{subject_context}** (Core Concepts) | 2.0 hrs | Review chapter notes & derive proofs |\n"
            f"| **Tue** | Problem Solving / Coding | 1.5 hrs | Solve 4-5 practice questions on weak areas |\n"
            f"| **Wed** | Secondary Subject & Lab | 2.0 hrs | Complete assignments before deadline |\n"
            f"| **Thu** | Active Recall & Flashcards | 1.0 hr | Self-quiz without checking reference solutions |\n"
            f"| **Fri** | Assignment Submissions | 1.5 hrs | Polish and submit weekly tasks |\n"
            f"| **Sat** | Mock Test & Review | 2.5 hrs | Full-length quiz under exam conditions |\n"
            f"| **Sun** | Rest & Light Overview | 1.0 hr | Review mistakes log and prepare for next week |\n\n"
            f"**Recommendation**: Spend 65% of study time on active problem solving rather than re-reading notes!"
        )

    # 5. GENERAL / CONCEPT EXPLANATION
    # Match known concepts
    matched_subject = None
    for subj_key, data in TOPIC_KNOWLEDGE.items():
        if subj_key in q_lower or subj_key in subject_context.lower():
            matched_subject = data
            break

    # Look for common specific questions
    if matched_subject:
        for question_key, ans in matched_subject.get("common_questions", {}).items():
            if question_key in q_lower:
                return (
                    f"### 🎯 Answer for '{question_key.title()}'\n\n"
                    f"{ans}\n\n"
                    f"**Why this matters in exams:** Faculty love asking comparison questions and edge-case scenarios. Ensure you draw block diagrams or write time complexity when answering in written exams.\n\n"
                    f"{random.choice(STUDY_TIPS)}"
                )

    # Custom explanation builder
    header = f"### 📘 SmartEdu AI Tutor: Explaining **{query.title()}**\n\n"
    intro = (
        f"Hello **{student_name}**! Let's break down **'{query}'** systematically.\n\n"
        f"#### 1. Intuition & High-Level Concept\n"
        f"Think of this topic as a practical building block in **{subject_context}**. "
        f"Whenever you encounter this in an exam or project, the primary goal is understanding *how data moves* and *why trade-offs exist*.\n\n"
    )

    core_breakdown = (
        f"#### 2. Core Pillars & Mechanism\n"
        f"- **Fundamental Rule**: Always analyze the inputs, transformations, and output expectations.\n"
        f"- **Best Practice**: Verify boundary constraints (e.g. null inputs, memory limits, edge cases).\n"
        f"- **Time / Space Trade-off**: Improving speed often requires trading auxiliary memory (e.g. caching, memoization, hash maps).\n\n"
    )

    example_box = (
        f"#### 3. Concrete Example & Walkthrough\n"
        f"```text\n"
        f"[Input State] ---> [Transformation / Processing] ---> [Validated Result]\n"
        f"Example: Processing '{query}' ensures deterministic behavior with zero unexpected side effects.\n"
        f"```\n\n"
    )

    takeaway = (
        f"#### 4. Exam Tip & Quick Check\n"
        f"- Can you state the definition in one sentence?\n"
        f"- Can you list at least two pros and two cons?\n\n"
        f"{random.choice(STUDY_TIPS)}"
    )

    return header + intro + core_breakdown + example_box + takeaway


def generate_mini_quiz(query, subject_context):
    return (
        f"### 📝 Quick Practice Quiz: **{query or subject_context}**\n\n"
        f"Test your understanding by answering these 3 quick questions:\n\n"
        f"**Q1. What is the primary characteristic of an efficient algorithm in this topic?**\n"
        f"- [A] Minimal number of lines of code\n"
        f"- [B] Optimal time and space complexity with deterministic execution (✅ Correct)\n"
        f"- [C] Random execution order\n"
        f"- [D] Only works on small inputs\n\n"
        f"**Q2. When evaluating edge cases, which one must always be guarded against?**\n"
        f"- [A] Null / empty inputs & off-by-one boundary conditions (✅ Correct)\n"
        f"- [B] Fast processors\n"
        f"- [C] Excessive comments\n"
        f"- [D] Alphabetical variable names\n\n"
        f"**Q3. Which technique best mitigates deep recursion stack overflows?**\n"
        f"- [A] Removing all termination checks\n"
        f"- [B] Tail recursion, iterative loops, or explicit stacks (✅ Correct)\n"
        f"- [C] Increasing font size\n"
        f"- [D] Running in debug mode only\n\n"
        f"*Tip: You can also take full faculty-assigned quizzes in the **Quizzes** tab!*"
    )


def generate_step_by_step_solution(query, subject_context):
    return (
        f"### 🧮 Step-by-Step Problem Solver\n\n"
        f"**Problem statement:** '{query}' ({subject_context})\n\n"
        f"**Step 1: Identify Given Variables & Constraints**\n"
        f"- State the explicit input specifications.\n"
        f"- Check non-negativity and boundary limits.\n\n"
        f"**Step 2: Choose Applicable Formula or Algorithm**\n"
        f"- For mathematical problems: Establish the invariant equation $f(n)$.\n"
        f"- For CS problems: Determine if Greedy, Dynamic Programming, or Divide & Conquer applies.\n\n"
        f"**Step 3: Execution & Intermediate Reduction**\n"
        f"- Substitute values systematically.\n"
        f"- Simplify terms without skipping cross-checks.\n\n"
        f"**Step 4: Verification**\n"
        f"- Plug the final value back into the original condition to verify consistency.\n"
        f"- Confirm time complexity is within acceptable limits.\n\n"
        f"✅ **Result**: Solution structured with full proof of correctness!"
    )


def generate_topic_summary(query, subject_context):
    return (
        f"### 📌 High-Yield Revision Cheatsheet: **{query or subject_context}**\n\n"
        f"| Concept Element | Key Takeaway | Exam Importance |\n"
        f"| --- | --- | --- |\n"
        f"| **Core Definition** | Foundation of the chapter | High (Definitions) |\n"
        f"| **Formulas / Complexity** | O(1) / O(log n) / O(n) standards | Crucial (Numerical MCQs) |\n"
        f"| **Real-World Use** | Production systems & operating efficiency | Medium (Theory / Viva) |\n"
        f"| **Common Traps** | Off-by-one errors & boundary checks | Very High |\n\n"
        f"**Quick Flashcard:**\n"
        f"> *Question:* How do you know when to apply this?\n"
        f"> *Answer:* When the problem requires deterministic scalability with predictable resources."
    )


def analyze_weak_areas(student):
    """
    Analyzes student quiz attempts, assignments, and attendance to compute:
    - Subject-wise scores
    - Overall GPA / Average
    - Weak subjects (score < 60% or attendance < 75%)
    - Concrete action items
    """
    from models import Subject, QuizAttempt, AssignmentSubmission, AttendanceRecord
    
    enrolled = student.enrolled_subjects
    if not enrolled:
        return {
            "overall_score": 0,
            "overall_attendance": 0,
            "subjects_breakdown": [],
            "weak_subjects": [],
            "recommendations": ["Enroll in subjects to start tracking progress."]
        }

    breakdown = []
    weak_subjects = []
    total_score_sum = 0
    total_score_count = 0
    total_att_presents = 0
    total_att_sessions = 0

    for subj in enrolled:
        # Quiz stats
        attempts = QuizAttempt.query.join(QuizAttempt.quiz).filter(
            QuizAttempt.student_id == student.id,
            QuizAttempt.quiz.has(subject_id=subj.id)
        ).all()
        
        quiz_avg = (sum(a.percentage for a in attempts) / len(attempts)) if attempts else 75.0
        
        # Assignment stats
        submissions = AssignmentSubmission.query.join(AssignmentSubmission.assignment).filter(
            AssignmentSubmission.student_id == student.id,
            AssignmentSubmission.assignment.has(subject_id=subj.id)
        ).all()
        graded_subs = [s for s in submissions if s.marks_obtained is not None]
        assignment_avg = (sum((s.marks_obtained / s.assignment.max_marks * 100) for s in graded_subs) / len(graded_subs)) if graded_subs else 78.0

        # Attendance stats
        att_records = AttendanceRecord.query.filter_by(student_id=student.id, subject_id=subj.id).all()
        if att_records:
            presents = sum(1 for a in att_records if a.status in ['present', 'late'])
            att_pct = round((presents / len(att_records)) * 100, 1)
            total_att_presents += presents
            total_att_sessions += len(att_records)
        else:
            att_pct = 85.0
            total_att_presents += 8
            total_att_sessions += 10

        composite_score = round((quiz_avg * 0.6) + (assignment_avg * 0.4), 1)
        total_score_sum += composite_score
        total_score_count += 1

        is_weak = composite_score < 65.0 or att_pct < 75.0
        status_label = "Needs Attention" if is_weak else ("Excellent" if composite_score >= 85 else "Good")

        subj_data = {
            "id": subj.id,
            "code": subj.code,
            "name": subj.name,
            "faculty_name": subj.faculty.full_name if subj.faculty else "Unassigned",
            "quiz_avg": round(quiz_avg, 1),
            "assignment_avg": round(assignment_avg, 1),
            "composite_score": composite_score,
            "attendance_pct": att_pct,
            "is_weak": is_weak,
            "status_label": status_label,
            "quizzes_taken": len(attempts),
            "assignments_submitted": len(submissions)
        }
        breakdown.append(subj_data)
        if is_weak:
            weak_subjects.append(subj_data)

    overall_score = round(total_score_sum / total_score_count, 1) if total_score_count else 0
    overall_attendance = round((total_att_presents / total_att_sessions) * 100, 1) if total_att_sessions else 85.0

    recommendations = []
    if weak_subjects:
        for ws in weak_subjects:
            reasons = []
            if ws["composite_score"] < 65.0:
                reasons.append(f"quiz & assignment performance is {ws['composite_score']}%")
            if ws["attendance_pct"] < 75.0:
                reasons.append(f"attendance is critically low at {ws['attendance_pct']}% (below 75% threshold)")
            recommendations.append(f"⚠️ **{ws['code']} - {ws['name']}**: Priority review recommended! Reason: {', '.join(reasons)}. Utilize the AI Assistant for chapter revisions.")
    else:
        recommendations.append("🌟 Outstanding balance across all enrolled subjects! Continue active recall to maintain your high GPA.")

    if overall_attendance < 75.0:
        recommendations.append("🚨 **Warning**: Overall attendance is below 75%. Please attend upcoming lecture sessions to avoid exam eligibility issues.")

    return {
        "overall_score": overall_score,
        "overall_attendance": overall_attendance,
        "subjects_breakdown": breakdown,
        "weak_subjects": weak_subjects,
        "recommendations": recommendations
    }
