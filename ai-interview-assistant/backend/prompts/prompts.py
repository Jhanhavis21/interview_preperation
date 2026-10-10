def generate_questions_prompt(job_role, experience_level, skills, interview_type, difficulty, number_of_questions):
    skills_text = ", ".join(skills) if isinstance(skills, list) else str(skills)
    return f"""You are an expert technical interviewer conducting a professional interview.

Candidate Profile:
Job Role: {job_role}
Experience Level: {experience_level}
Skills: {skills_text}
Interview Type: {interview_type}
Difficulty: {difficulty}

Generate {number_of_questions} interview questions appropriate for this candidate.

Requirements:
1. Questions must be relevant to the selected job role.
2. Questions must match the candidate's experience level.
3. Cover the provided skills where appropriate.
4. Include a mixture of conceptual, practical, and scenario-based questions when the interview type is technical or mixed.
5. Avoid duplicate questions.
6. Questions should gradually increase in difficulty.
7. Do not provide the answers yet.
Return the response in valid JSON format:

{{
  "questions": [
    {{
      "id": 1,
      "question": "...",
      "category": "...",
      "difficulty": "..."
    }}
  ]
}}"""


def evaluate_answer_prompt(question, answer, job_role):
    return f"""You are an expert interviewer evaluating a candidate's answer.

Question:
{question}

Candidate Answer:
{answer}

Job Role:
{job_role}

Evaluate the answer objectively.

Consider:
1. Technical correctness
2. Completeness
3. Relevance
4. Clarity
5. Practical understanding
6. Communication quality
Give scores from 0 to 10 for each criterion.

Also provide:
- Overall score
- What the candidate did well
- What is missing
- Specific improvements
- A better sample answer
- One possible follow-up question
Return valid JSON:

{{
  "technical_correctness": 0,
  "completeness": 0,
  "relevance": 0,
  "clarity": 0,
  "practical_understanding": 0,
  "communication": 0,
  "overall_score": 0,
  "strengths": [],
  "missing_points": [],
  "improvements": [],
  "sample_answer": "...",
  "follow_up_question": "..."
}}"""


def generate_followup_prompt(question, answer, evaluation, job_role):
    evaluation_text = json_to_text(evaluation)
    return f"""You are conducting an adaptive technical interview.

Previous Question:
{question}

Candidate Answer:
{answer}

Evaluation:
{evaluation_text}

Job Role:
{job_role}

Generate ONE appropriate follow-up question.

If the candidate demonstrated strong understanding, increase the difficulty.
If the candidate struggled, ask a simpler question that tests the missing concept.
Do not repeat the previous question.
Return JSON:

{{
  "follow_up_question": "...",
  "difficulty": "...",
  "reason": "..."
}}"""


def generate_final_report_prompt(session_data, answers_summary):
    return f"""You are an expert interview coach creating a final performance report.

Interview Details:
{session_data}

Answered Questions Summary:
{answers_summary}

Generate a clear, actionable final interview report in valid JSON format:

{{
  "overall_score": 0,
  "category_performance": {{
    "Technical Knowledge": 0,
    "Problem Solving": 0,
    "Communication": 0,
    "Practical Knowledge": 0
  }},
  "strong_areas": ["..."],
  "areas_to_improve": ["..."],
  "recommendations": [
    {{"day": "Day 1", "plan": "..."}},
    {{"day": "Day 2", "plan": "..."}}
  ],
  "summary": "..."
}}"""


def json_to_text(data):
    return str(data)
