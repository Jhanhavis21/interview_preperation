function InterviewPage({
  question,
  questionIndex,
  totalQuestions,
  answer,
  onAnswerChange,
  onSubmit,
  onSkip,
  onPrevious,
  onNext,
  loading,
  error,
  canGoPrevious,
  canGoNext,
  evaluation,
  followUp,
  onFinish,
}) {
  const progress = ((questionIndex + 1) / totalQuestions) * 100;

  return (
    <div className="page interview-page">
      <div className="panel interview-panel">
        <div className="interview-header">
          <div>
            <p className="eyebrow">Question {questionIndex + 1} of {totalQuestions}</p>
            <h2>{question?.question}</h2>
          </div>
          <div className="meta-box">
            <div>
              <label>Category</label>
              <strong>{question?.category || 'General'}</strong>
            </div>
            <div>
              <label>Difficulty</label>
              <strong>{question?.difficulty || 'Medium'}</strong>
            </div>
          </div>
        </div>

        <div className="progress-bar-wrap">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>

        {error && <div className="error-banner">{error}</div>}

        <textarea
          value={answer}
          onChange={(e) => onAnswerChange(e.target.value)}
          placeholder="Type your answer here..."
          rows={10}
        />

        <div className="button-row">
          <button className="secondary-button" onClick={onSkip} disabled={loading}>
            Skip
          </button>
          <button className="secondary-button" onClick={onPrevious} disabled={!canGoPrevious || loading}>
            Previous
          </button>
          <button className="primary-button" onClick={onSubmit} disabled={loading}>
            {loading ? 'AI is evaluating your answer...' : 'Submit Answer'}
          </button>
          <button className="primary-button" onClick={onNext} disabled={!canGoNext || loading}>
            Next
          </button>
        </div>

        {evaluation && (
          <div className="feedback-box">
            <h3>AI Evaluation</h3>
            <div className="score-grid">
              {[
                ['Overall Score', `${evaluation.overall_score || 0}/10`],
                ['Technical', `${evaluation.technical_correctness || 0}/10`],
                ['Completeness', `${evaluation.completeness || 0}/10`],
                ['Relevance', `${evaluation.relevance || 0}/10`],
                ['Clarity', `${evaluation.clarity || 0}/10`],
                ['Practical', `${evaluation.practical_understanding || 0}/10`],
                ['Communication', `${evaluation.communication || 0}/10`],
              ].map(([label, value]) => (
                <div key={label} className="score-pill">
                  <span>{label}</span>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>
            <div className="feedback-sections">
              <div>
                <h4>What You Did Well</h4>
                <ul>{(evaluation.strengths || []).map((point) => <li key={point}>{point}</li>)}</ul>
              </div>
              <div>
                <h4>What You Missed</h4>
                <ul>{(evaluation.missing_points || []).map((point) => <li key={point}>{point}</li>)}</ul>
              </div>
              <div>
                <h4>How to Improve</h4>
                <ul>{(evaluation.improvements || []).map((point) => <li key={point}>{point}</li>)}</ul>
              </div>
              <div>
                <h4>Better Answer</h4>
                <p>{evaluation.sample_answer}</p>
              </div>
            </div>
          </div>
        )}

        {followUp && (
          <div className="followup-box">
            <h3>Follow-up Question</h3>
            <p>{followUp}</p>
          </div>
        )}

        {evaluation && questionIndex === totalQuestions - 1 && (
          <button className="primary-button" onClick={onFinish} disabled={loading}>
            Finish Interview
          </button>
        )}
      </div>
    </div>
  );
}

export default InterviewPage;
