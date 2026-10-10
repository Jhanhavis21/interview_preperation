function HistoryPage({ history }) {
  return (
    <div className="page history-page">
      <div className="panel">
        <h1>Interview History</h1>
        <div className="history-table">
          <div className="history-header">
            <span>Date</span>
            <span>Job Role</span>
            <span>Interview Type</span>
            <span>Score</span>
          </div>
          {history.length === 0 ? (
            <p className="empty-state">No interviews have been completed yet.</p>
          ) : (
            history.map((session) => (
              <div key={session.id} className="history-row">
                <span>{new Date(session.created_at).toLocaleDateString()}</span>
                <span>{session.job_role}</span>
                <span>{session.interview_type}</span>
                <span>{session.overall_score ? `${session.overall_score}/10` : 'Pending'}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default HistoryPage;
