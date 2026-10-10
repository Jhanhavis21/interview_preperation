import os
import json
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from database import (
    create_question,
    create_session,
    get_dashboard_stats,
    get_session_by_id,
    get_session_with_details,
    init_db,
    list_sessions,
    save_answer,
    update_session_score,
)
from services.ai_service import (
    evaluate_answer,
    generate_final_report,
    generate_followup,
    generate_questions,
)

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.errorhandler(400)
def handle_bad_request(error):
    return jsonify({"error": "Invalid request payload."}), 400


@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({"error": "Resource not found."}), 404


@app.errorhandler(500)
def handle_server_error(error):
    return jsonify({"error": "An internal server error occurred."}), 500


def validate_required_fields(payload, fields):
    missing = [field for field in fields if not payload.get(field)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


@app.route("/api/interviews", methods=["POST"])
def create_interview_session():
    try:
        payload = request.get_json(silent=True) or {}
        validate_required_fields(
            payload,
            ["job_role", "experience_level", "interview_type", "difficulty", "skills", "total_questions"],
        )
        if not isinstance(payload["skills"], str) or not payload["skills"].strip():
            raise ValueError("Skills cannot be empty.")
        session_id = create_session(
            {
                "job_role": payload["job_role"].strip(),
                "experience_level": payload["experience_level"].strip(),
                "interview_type": payload["interview_type"].strip(),
                "difficulty": payload["difficulty"].strip(),
                "skills": payload["skills"].strip(),
                "total_questions": int(payload["total_questions"]),
            }
        )
        return jsonify({"session_id": session_id, "message": "Interview session created."}), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError:
        return jsonify({"error": "AI service is currently unavailable. Please configure OPENAI_API_KEY and try again."}), 500
    except Exception:
        return jsonify({"error": "Unable to create interview session."}), 500


@app.route("/api/generate-questions", methods=["POST"])
def generate_interview_questions():
    try:
        payload = request.get_json(silent=True) or {}
        validate_required_fields(
            payload,
            ["session_id", "job_role", "experience_level", "skills", "interview_type", "difficulty", "total_questions"],
        )
        skills = [item.strip() for item in str(payload["skills"]).split(",") if item.strip()]
        questions = generate_questions(
            job_role=payload["job_role"],
            experience_level=payload["experience_level"],
            skills=skills,
            interview_type=payload["interview_type"],
            difficulty=payload["difficulty"],
            number_of_questions=int(payload["total_questions"]),
        )

        saved_questions = []
        for item in questions:
            question_id = create_question(
                int(payload["session_id"]),
                item.get("question", "").strip(),
                item.get("category", "General"),
                item.get("difficulty", "Medium"),
            )
            saved_questions.append({
                "id": question_id,
                "question": item.get("question", "").strip(),
                "category": item.get("category", "General"),
                "difficulty": item.get("difficulty", "Medium"),
            })

        return jsonify({"questions": saved_questions}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError:
        return jsonify({"error": "AI service is currently unavailable. Please configure OPENAI_API_KEY and try again."}), 500
    except Exception:
        return jsonify({"error": "AI question generation failed. Please try again."}), 500


@app.route("/api/evaluate-answer", methods=["POST"])
def evaluate_interview_answer():
    try:
        payload = request.get_json(silent=True) or {}
        validate_required_fields(payload, ["question", "answer", "job_role", "question_id"])
        if not payload["answer"].strip():
            raise ValueError("Answer cannot be empty.")

        evaluation = evaluate_answer(
            question=payload["question"],
            answer=payload["answer"],
            job_role=payload["job_role"],
        )
        score_value = float(evaluation.get("overall_score", 0.0))
        feedback_summary = {
            "technical_correctness": evaluation.get("technical_correctness", 0),
            "completeness": evaluation.get("completeness", 0),
            "relevance": evaluation.get("relevance", 0),
            "clarity": evaluation.get("clarity", 0),
            "practical_understanding": evaluation.get("practical_understanding", 0),
            "communication": evaluation.get("communication", 0),
            "overall_score": evaluation.get("overall_score", 0),
            "strengths": evaluation.get("strengths", []),
            "missing_points": evaluation.get("missing_points", []),
            "improvements": evaluation.get("improvements", []),
            "follow_up_question": evaluation.get("follow_up_question", ""),
        }
        save_answer(
            question_id=int(payload["question_id"]),
            answer=payload["answer"].strip(),
            score=score_value,
            feedback=feedback_summary,
            sample_answer=evaluation.get("sample_answer", ""),
        )
        return jsonify({"evaluation": evaluation}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError:
        return jsonify({"error": "AI service is currently unavailable. Please configure OPENAI_API_KEY and try again."}), 500
    except Exception:
        return jsonify({"error": "AI evaluation failed. Please try again."}), 500


@app.route("/api/follow-up", methods=["POST"])
def generate_follow_up_question():
    try:
        payload = request.get_json(silent=True) or {}
        validate_required_fields(payload, ["question", "answer", "evaluation", "job_role"])
        follow_up = generate_followup(
            question=payload["question"],
            answer=payload["answer"],
            evaluation=payload["evaluation"],
            job_role=payload["job_role"],
        )
        return jsonify({"follow_up": follow_up}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError:
        return jsonify({"error": "AI service is currently unavailable. Please configure OPENAI_API_KEY and try again."}), 500
    except Exception:
        return jsonify({"error": "Follow-up question generation failed."}), 500


@app.route("/api/final-report", methods=["POST"])
def final_report():
    try:
        payload = request.get_json(silent=True) or {}
        validate_required_fields(payload, ["session_id", "answers_summary"])  # type: ignore[arg-type]
        session_id = int(payload["session_id"])
        session = get_session_by_id(session_id)
        if not session:
            return jsonify({"error": "Session not found."}), 404

        report = generate_final_report(
            session_data={
                "job_role": session["job_role"],
                "experience_level": session["experience_level"],
                "interview_type": session["interview_type"],
                "difficulty": session["difficulty"],
                "skills": session["skills"],
            },
            answers_summary=payload["answers_summary"],
        )

        overall_score = float(report.get("overall_score", 0.0))
        update_session_score(session_id, overall_score)
        return jsonify({"report": report}), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError:
        return jsonify({"error": "AI service is currently unavailable. Please configure OPENAI_API_KEY and try again."}), 500
    except Exception:
        return jsonify({"error": "Final report generation failed."}), 500


@app.route("/api/interviews", methods=["GET"])
def get_all_interviews():
    sessions = list_sessions()
    return jsonify({"interviews": sessions}), 200


@app.route("/api/interviews/<int:session_id>", methods=["GET"])
def get_interview_by_id(session_id):
    session = get_session_with_details(session_id)
    if not session:
        return jsonify({"error": "Interview session not found."}), 404
    return jsonify(session), 200


@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    stats = get_dashboard_stats()
    return jsonify(stats), 200


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
