# AI Interview Preparation Assistant

## Problem Statement
Students and job seekers often practice interviews without personalized feedback or adaptive follow-up questions. This project solves that by creating an AI-based interview assistant that generates role-specific questions, evaluates user responses, gives actionable feedback, and saves interview history for review.

## Features
- Role-based interview setup
- AI-generated technical, HR, and behavioral questions
- Real-time answer evaluation using the OpenAI API
- Adaptive follow-up question generation
- Final performance report and recommendations
- SQLite-backed interview history and dashboard
- Error handling for invalid input and API failures

## Technology Stack
- Frontend: React + Vite + CSS + Axios
- Backend: Python + Flask + Flask-CORS
- Database: SQLite
- AI: OpenAI GPT models

## System Architecture
The frontend sends interview configuration and answers to the Flask backend. The backend stores session data in SQLite, calls the OpenAI API using a secure environment variable, and returns structured JSON responses to the UI.

## Installation
1. Navigate to the project folder.
2. Create and activate a Python virtual environment (optional but recommended).
3. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
4. Install frontend dependencies:
   ```bash
   cd ../frontend
   npm install
   ```

## Environment Variables
Create a `.env` file in the `backend` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Do not commit the real API key to source control. If the OpenAI API is unavailable or quota is exhausted, the app falls back to local template-based interview generation so the demo still runs.

## Running the Frontend
```bash
cd frontend
npm run dev -- --host 0.0.0.0
```
The app should open on the default Vite port (typically 5173).

## Running the Backend
```bash
cd backend
D:/python.exe app.py
```
The Flask server runs on `http://127.0.0.1:5000`.

## API Details
### POST /api/interviews
Creates an interview session.

### POST /api/generate-questions
Generates interview questions for a given session.

### POST /api/evaluate-answer
Evaluates a candidate answer and returns scores and feedback.

### POST /api/follow-up
Generates a follow-up question based on the previous answer.

### POST /api/final-report
Generates the final overall interview performance report.

### GET /api/interviews
Returns all stored interview sessions.

### GET /api/interviews/<id>
Returns a specific interview session and its details.

### GET /api/dashboard
Returns dashboard summary numbers.

## GenAI Integration
The application uses the OpenAI API with secure environment configuration. Prompt functions are kept in `backend/prompts/prompts.py`, and the OpenAI request wrapper is in `backend/services/ai_service.py`.

## Screenshots
Add screenshots of the home page, setup form, interview screen, feedback, report, and history dashboard here for your Learning Block 1 report.

## Future Improvements
- Voice-based interviews
- Resume-aware question generation
- Authentication and user accounts
- More advanced analytics and trend tracking
- Multi-language support

## Local Demo Instructions
1. Start the backend server.
2. Start the Vite frontend.
3. Open the app in a browser.
4. Complete the setup form.
5. Generate questions.
6. Answer the questions and review AI feedback.
7. Navigate to the final report and interview history.

## Screenshot Guidance for the Learning Block 1 Report
Take screenshots at the following points:
- Home page
- Interview setup form
- AI-generated question screen
- Feedback screen after an answer
- Final interview report
- Interview history/dashboard page

These screenshots demonstrate system flow and end-to-end functionality.
