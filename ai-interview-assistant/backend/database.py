import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "interview_app.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS interview_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_role TEXT NOT NULL,
                experience_level TEXT NOT NULL,
                interview_type TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                skills TEXT NOT NULL,
                total_questions INTEGER NOT NULL,
                overall_score REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS interview_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                category TEXT,
                difficulty TEXT,
                FOREIGN KEY(session_id) REFERENCES interview_sessions(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS interview_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                answer TEXT NOT NULL,
                score REAL,
                feedback TEXT,
                sample_answer TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(question_id) REFERENCES interview_questions(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def create_session(payload):
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO interview_sessions (
                job_role, experience_level, interview_type, difficulty, skills, total_questions, overall_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["job_role"],
                payload["experience_level"],
                payload["interview_type"],
                payload["difficulty"],
                payload["skills"],
                payload["total_questions"],
                None,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def create_question(session_id, question, category, difficulty):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO interview_questions (session_id, question, category, difficulty) VALUES (?, ?, ?, ?)",
            (session_id, question, category, difficulty),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def save_answer(question_id, answer, score, feedback, sample_answer):
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO interview_answers (question_id, answer, score, feedback, sample_answer)
            VALUES (?, ?, ?, ?, ?)
            """,
            (question_id, answer, score, json.dumps(feedback) if isinstance(feedback, dict) else feedback, sample_answer),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_session_score(session_id, overall_score):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE interview_sessions SET overall_score = ? WHERE id = ?",
            (overall_score, session_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_session_by_id(session_id):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM interview_sessions WHERE id = ?",
            (session_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_question_by_id(question_id):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM interview_questions WHERE id = ?",
            (question_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def list_sessions():
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, job_role, experience_level, interview_type, difficulty, skills, total_questions, overall_score, created_at
            FROM interview_sessions
            ORDER BY created_at DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_session_with_details(session_id):
    conn = get_connection()
    try:
        session = conn.execute(
            "SELECT * FROM interview_sessions WHERE id = ?",
            (session_id,),
        ).fetchone()
        if not session:
            return None
        questions = conn.execute(
            "SELECT * FROM interview_questions WHERE session_id = ? ORDER BY id ASC",
            (session_id,),
        ).fetchall()
        answers = []
        for q in questions:
            row = conn.execute(
                "SELECT * FROM interview_answers WHERE question_id = ? ORDER BY created_at DESC",
                (q["id"],),
            ).fetchone()
            if row:
                answers.append({"question": q["question"], "answer": row["answer"], "score": row["score"], "feedback": json.loads(row["feedback"]) if row["feedback"] else None, "sample_answer": row["sample_answer"]})
        return {
            "session": dict(session),
            "questions": [dict(q) for q in questions],
            "answers": answers,
        }
    finally:
        conn.close()


def get_dashboard_stats():
    conn = get_connection()
    try:
        sessions = conn.execute(
            "SELECT * FROM interview_sessions WHERE overall_score IS NOT NULL ORDER BY created_at DESC"
        ).fetchall()
        if not sessions:
            return {
                "interviews_completed": 0,
                "average_score": 0,
                "best_score": 0,
                "weakest_category": "N/A",
                "recent_sessions": [],
            }

        scores = [float(s["overall_score"]) for s in sessions]
        average_score = round(sum(scores) / len(scores), 2)
        best_score = round(max(scores), 2)
        recent_sessions = [{
            "id": s["id"],
            "job_role": s["job_role"],
            "interview_type": s["interview_type"],
            "overall_score": s["overall_score"],
            "created_at": s["created_at"],
        } for s in sessions[:5]]
        weakest_category = "Communication"
        return {
            "interviews_completed": len(sessions),
            "average_score": average_score,
            "best_score": best_score,
            "weakest_category": weakest_category,
            "recent_sessions": recent_sessions,
        }
    finally:
        conn.close()
