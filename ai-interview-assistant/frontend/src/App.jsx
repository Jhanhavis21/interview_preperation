import { useEffect, useState } from 'react';
import './App.css';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import SetupPage from './pages/SetupPage';
import InterviewPage from './pages/InterviewPage';
import HistoryPage from './pages/HistoryPage';
import DashboardPage from './pages/DashboardPage';
import ReportPage from './pages/ReportPage';
import api from './services/api';

const defaultForm = {
  jobRole: '',
  experienceLevel: '',
  interviewType: '',
  difficulty: '',
  totalQuestions: 5,
  skills: '',
};

function App() {
  const [page, setPage] = useState('home');
  const [form, setForm] = useState(defaultForm);
  const [sessionId, setSessionId] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answerText, setAnswerText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [evaluations, setEvaluations] = useState([]);
  const [followUp, setFollowUp] = useState(null);
  const [report, setReport] = useState(null);
  const [history, setHistory] = useState([]);
  const [dashboardStats, setDashboardStats] = useState({
    interviews_completed: 0,
    average_score: 0,
    best_score: 0,
    weakest_category: 'N/A',
    recent_sessions: [],
  });

  const currentQuestion = questions[currentIndex] || null;
  const currentEvaluation = currentQuestion
    ? evaluations.find((item) => item.questionId === currentQuestion.id) || null
    : null;

  const fetchHistory = async () => {
    try {
      const response = await api.get('/api/interviews');
      setHistory(response.data.interviews || []);
    } catch (err) {
      setHistory([]);
    }
  };

  const fetchDashboard = async () => {
    try {
      const response = await api.get('/api/dashboard');
      setDashboardStats(response.data || {
        interviews_completed: 0,
        average_score: 0,
        best_score: 0,
        weakest_category: 'N/A',
        recent_sessions: [],
      });
    } catch (err) {
      setDashboardStats({
        interviews_completed: 0,
        average_score: 0,
        best_score: 0,
        weakest_category: 'N/A',
        recent_sessions: [],
      });
    }
  };

  useEffect(() => {
    fetchHistory();
    fetchDashboard();
  }, []);

  const handleNavigate = async (nextPage) => {
    setPage(nextPage);
    if (nextPage === 'history' || nextPage === 'dashboard') {
      await fetchHistory();
      await fetchDashboard();
    }
  };

  const updateForm = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const startInterview = async () => {
    if (!form.jobRole || !form.experienceLevel || !form.interviewType || !form.difficulty || !form.skills.trim()) {
      setError('Please complete the full interview setup before starting.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const sessionResponse = await api.post('/api/interviews', {
        job_role: form.jobRole,
        experience_level: form.experienceLevel,
        interview_type: form.interviewType,
        difficulty: form.difficulty,
        skills: form.skills,
        total_questions: form.totalQuestions,
      });

      const sessionIdValue = sessionResponse.data.session_id;
      const questionResponse = await api.post('/api/generate-questions', {
        session_id: sessionIdValue,
        job_role: form.jobRole,
        experience_level: form.experienceLevel,
        interview_type: form.interviewType,
        difficulty: form.difficulty,
        skills: form.skills,
        total_questions: form.totalQuestions,
      });

      setSessionId(sessionIdValue);
      setQuestions(questionResponse.data.questions || []);
      setCurrentIndex(0);
      setAnswerText('');
      setFollowUp(null);
      setEvaluations([]);
      setReport(null);
      setPage('interview');
      await fetchHistory();
      await fetchDashboard();
    } catch (err) {
      setError(err.response?.data?.error || 'Unable to generate interview questions.');
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!currentQuestion) {
      return;
    }

    if (!answerText.trim()) {
      setError('Answer cannot be empty before evaluation.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await api.post('/api/evaluate-answer', {
        question_id: currentQuestion.id,
        question: currentQuestion.question,
        answer: answerText,
        job_role: form.jobRole,
      });

      const evaluation = response.data.evaluation;
      const updatedEvaluation = {
        questionId: currentQuestion.id,
        question: currentQuestion.question,
        answer: answerText,
        evaluation,
      };

      setEvaluations((prev) => {
        const filtered = prev.filter((item) => item.questionId !== currentQuestion.id);
        return [...filtered, updatedEvaluation];
      });

      const followUpResponse = await api.post('/api/follow-up', {
        question: currentQuestion.question,
        answer: answerText,
        evaluation,
        job_role: form.jobRole,
      });

      const generatedFollowUp = followUpResponse.data?.follow_up?.follow_up_question || 
        followUpResponse.data?.follow_up_question ||
        null;

      setFollowUp(generatedFollowUp);
    } catch (err) {
      setError(err.response?.data?.error || 'AI evaluation failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const goToPreviousQuestion = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
      setAnswerText('');
      setError('');
      setFollowUp(null);
    }
  };

  const goToNextQuestion = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
      setAnswerText('');
      setError('');
      setFollowUp(null);
      return;
    }

    finishInterview();
  };

  const skipQuestion = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
      setAnswerText('');
      setError('');
      setFollowUp(null);
    } else {
      finishInterview();
    }
  };

  const finishInterview = async () => {
    if (!sessionId) {
      return;
    }

    const answerSummary = evaluations.map((item) => ({
      question: item.question,
      answer: item.answer,
      score: item.evaluation.overall_score,
    }));

    setLoading(true);
    setError('');

    try {
      const reportResponse = await api.post('/api/final-report', {
        session_id: sessionId,
        answers_summary: answerSummary,
      });
      setReport(reportResponse.data.report);
      setPage('report');
      await fetchHistory();
      await fetchDashboard();
    } catch (err) {
      setError(err.response?.data?.error || 'Unable to generate the final interview report.');
    } finally {
      setLoading(false);
    }
  };

  const renderPage = () => {
    if (page === 'home') {
      return <HomePage onStart={() => setPage('setup')} />;
    }

    if (page === 'setup') {
      return (
        <SetupPage
          form={form}
          onChange={updateForm}
          onSubmit={startInterview}
          loading={loading}
          error={error}
        />
      );
    }

    if (page === 'interview' && currentQuestion) {
      return (
        <InterviewPage
          question={currentQuestion}
          questionIndex={currentIndex}
          totalQuestions={questions.length}
          answer={answerText}
          onAnswerChange={setAnswerText}
          onSubmit={submitAnswer}
          onSkip={skipQuestion}
          onPrevious={goToPreviousQuestion}
          onNext={goToNextQuestion}
          loading={loading}
          error={error}
          canGoPrevious={currentIndex > 0}
          canGoNext={currentIndex < questions.length - 1 || !!currentEvaluation}
          evaluation={currentEvaluation?.evaluation || null}
          followUp={followUp}
          onFinish={finishInterview}
        />
      );
    }

    if (page === 'history') {
      return <HistoryPage history={history} />;
    }

    if (page === 'dashboard') {
      return <DashboardPage stats={dashboardStats} />;
    }

    if (page === 'report') {
      return <ReportPage report={report} />;
    }

    return <HomePage onStart={() => setPage('setup')} />;
  };

  return (
    <div className="app-shell">
      <Navbar onNavigate={handleNavigate} activePage={page} />
      {renderPage()}
    </div>
  );
}

export default App;
