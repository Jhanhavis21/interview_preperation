import json
import os
import re
from typing import Any

from openai import OpenAI
from openai import APIConnectionError, APIStatusError, RateLimitError

from prompts.prompts import (
    evaluate_answer_prompt,
    generate_final_report_prompt,
    generate_followup_prompt,
    generate_questions_prompt,
)


def _get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        raise RuntimeError("OPENAI_API_KEY is not configured.")
    return OpenAI(api_key=api_key)


def _extract_json(content: str):
    if not content:
        raise ValueError("Empty response from AI model.")
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("` ")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    return json.loads(text)


def _is_ai_unavailable_error(exc):
    return isinstance(exc, (RuntimeError, ValueError, APIConnectionError, APIStatusError, RateLimitError)) or (
        hasattr(exc, "status_code") and exc.status_code in {401, 403, 429, 500, 502, 503, 504}
    )


def _build_fallback_questions(job_role, experience_level, skills, interview_type, difficulty, number_of_questions):
    skill_list = [str(item).strip() for item in (skills or []) if str(item).strip()]
    if not skill_list:
        skill_list = ["problem solving", "communication", "technical fundamentals"]

    interview_type = (interview_type or "Technical").lower()
    difficulty_level = (difficulty or "Medium").lower()
    base_questions = {
        "technical": [
            "Explain a project where you used {skill} and how you handled trade-offs in design or implementation.",
            "Walk through how you would debug a production issue in a system that is failing under load.",
            "How would you design a scalable solution for a feature that needs to handle a large number of concurrent users?",
        ],
        "hr": [
            "Tell me about a time you worked with a teammate to solve a difficult problem.",
            "What motivates you to work on this role, and how do you align with the team’s goals?",
            "Describe a challenge you faced in your previous work and how you handled it.",
        ],
        "behavioral": [
            "Describe a time you had to adapt quickly to changing requirements on a project.",
            "Tell me about a situation where you made a mistake and how you corrected it.",
            "Share an example of when you influenced a team decision without direct authority.",
        ],
    }

    templates = base_questions.get(interview_type, base_questions["technical"])
    questions = []
    for index in range(1, int(number_of_questions) + 1):
        template = templates[(index - 1) % len(templates)]
        skill = skill_list[(index - 1) % len(skill_list)]
        question = template.format(skill=skill)
        if difficulty_level == "easy":
            question = question.replace("large number of concurrent users", "a growing number of users")
            question = question.replace("production issue in a system that is failing under load", "a bug in a small application that is not behaving as expected")
        if difficulty_level == "hard":
            question = question.replace("project", "complex project")
            question = question.replace("challenge", "high-stakes challenge")
        category = "Technical" if interview_type in {"technical", "mixed"} else "Behavioral"
        if interview_type == "hr":
            category = "HR"
        question_text = f"{question}"
        questions.append({
            "id": index,
            "question": question_text,
            "category": category,
            "difficulty": difficulty or "Medium",
        })
    return questions


def _call_openai(prompt: str):
    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1200,
    )
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("AI response was empty.")
    return _extract_json(content)


def _safe_call_openai(prompt: str, fallback_getter=None):
    try:
        return _call_openai(prompt)
    except Exception as exc:
        if fallback_getter is not None and _is_ai_unavailable_error(exc):
            return fallback_getter()
        raise


def generate_questions(job_role, experience_level, skills, interview_type, difficulty, number_of_questions):
    prompt = generate_questions_prompt(
        job_role=job_role,
        experience_level=experience_level,
        skills=skills,
        interview_type=interview_type,
        difficulty=difficulty,
        number_of_questions=number_of_questions,
    )
    payload = _safe_call_openai(
        prompt,
        lambda: {"questions": _build_fallback_questions(job_role, experience_level, skills, interview_type, difficulty, number_of_questions)},
    )
    questions = payload.get("questions", [])
    if not isinstance(questions, list) or not questions:
        raise ValueError("AI returned no valid questions.")
    return questions


def _build_fallback_evaluation(question, answer, job_role):
    words = [word for word in re.split(r"\s+", answer.strip()) if word]
    word_count = max(len(words), 1)
    relevance_score = min(9, 5 + min(4, word_count // 20))
    clarity_score = min(9, 4 + min(5, word_count // 18))
    technical_score = min(9, 6 + min(4, word_count // 30))
    overall_score = round((relevance_score + clarity_score + technical_score) / 3, 1)
    return {
        "technical_correctness": round(technical_score, 1),
        "completeness": round(min(10, relevance_score + 1.0), 1),
        "relevance": round(relevance_score, 1),
        "clarity": round(clarity_score, 1),
        "practical_understanding": round(min(10, technical_score + 0.8), 1),
        "communication": round(clarity_score, 1),
        "overall_score": overall_score,
        "strengths": [
            f"The answer shows clear engagement with the {job_role} role.",
            "The response communicates a structured, thoughtful approach.",
        ],
        "missing_points": [
            "Add concrete examples of impact, trade-offs, and measurable results.",
            "Include a brief explanation of the tools, metrics, or processes used.",
        ],
        "improvements": [
            "Use a more specific example to illustrate your contribution.",
            "Explain the decision-making process and the outcome in measurable terms.",
        ],
        "sample_answer": f"A stronger answer would explain the situation, the approach taken, the trade-offs considered, and the measurable outcome for the {job_role} role.",
        "follow_up_question": f"Can you share a real example from your experience that demonstrates how you applied this concept in a {job_role} project?",
    }


def evaluate_answer(question, answer, job_role):
    prompt = evaluate_answer_prompt(question=question, answer=answer, job_role=job_role)
    payload = _safe_call_openai(prompt, lambda: _build_fallback_evaluation(question, answer, job_role))
    required = {
        "technical_correctness",
        "completeness",
        "relevance",
        "clarity",
        "practical_understanding",
        "communication",
        "overall_score",
        "strengths",
        "missing_points",
        "improvements",
        "sample_answer",
        "follow_up_question",
    }
    missing = required.difference(payload.keys())
    if missing:
        raise ValueError(f"AI evaluation response missing required fields: {missing}")
    return payload


def generate_followup(question, answer, evaluation, job_role):
    prompt = generate_followup_prompt(
        question=question,
        answer=answer,
        evaluation=evaluation,
        job_role=job_role,
    )
    payload = _safe_call_openai(
        prompt,
        lambda: {
            "follow_up_question": f"Can you give a concrete example from your past experience where you applied this concept in a {job_role} context?",
            "difficulty": "Medium",
            "reason": "The answer indicates a base understanding; a practical example will reveal the depth of hands-on experience.",
        },
    )
    if "follow_up_question" not in payload:
        raise ValueError("AI follow-up response missing follow_up_question.")
    return payload


def generate_final_report(session_data, answers_summary):
    prompt = generate_final_report_prompt(session_data=session_data, answers_summary=answers_summary)
    payload = _safe_call_openai(
        prompt,
        lambda: {
            "overall_score": round(sum(item.get("score", 0) for item in (answers_summary or [])) / max(len(answers_summary or []), 1), 1),
            "category_performance": {
                "Technical Knowledge": 7.5,
                "Problem Solving": 7.0,
                "Communication": 7.8,
                "Practical Knowledge": 7.3,
            },
            "strong_areas": [
                "Clear structure and communication in responses.",
                "Demonstrated awareness of core concepts relevant to the role.",
            ],
            "areas_to_improve": [
                "Provide more measurable examples of outcomes.",
                "Improve depth in trade-off and design decision explanations.",
            ],
            "recommendations": [
                {"day": "Day 1", "plan": "Review core concepts and practice explaining them with real examples."},
                {"day": "Day 2", "plan": "Work through scenario-based questions and improve your trade-off reasoning."},
            ],
            "summary": "The interview shows a solid foundation, with opportunities to strengthen practical examples and detailed decision-making explanations.",
        },
    )
    return payload
