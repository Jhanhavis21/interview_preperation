import MetricCard from '../components/MetricCard';

function DashboardPage({ stats }) {
  return (
    <div className="page dashboard-page">
      <div className="dashboard-grid">
        <MetricCard label="Interviews Completed" value={stats?.interviews_completed ?? 0} />
        <MetricCard label="Average Score" value={`${stats?.average_score ?? 0}/10`} />
        <MetricCard label="Best Score" value={`${stats?.best_score ?? 0}/10`} />
        <MetricCard label="Weakest Category" value={stats?.weakest_category ?? 'N/A'} />
      </div>

      <div className="panel">
        <h2>Recent Interviews</h2>
        <div className="history-list">
          {(stats?.recent_sessions || []).map((session) => (
            <div key={session.id} className="history-item">
              <span>{new Date(session.created_at).toLocaleDateString()}</span>
              <strong>{session.job_role}</strong>
              <span>{session.interview_type}</span>
              <span>{session.overall_score}/10</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
