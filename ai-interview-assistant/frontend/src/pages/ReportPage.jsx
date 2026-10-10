function ReportPage({ report }) {
  if (!report) {
    return <div className="page"><div className="panel"><p>Loading final report...</p></div></div>;
  }

  return (
    <div className="page report-page">
      <div className="panel">
        <h1>Interview Performance</h1>
        <div className="report-score">
          <strong>{report.overall_score ?? 0}/10</strong>
        </div>

        <h3>Category Performance</h3>
        <div className="report-grid">
          {Object.entries(report.category_performance || {}).map(([label, value]) => (
            <div key={label} className="score-pill">
              <span>{label}</span>
              <strong>{value}/10</strong>
            </div>
          ))}
        </div>

        <div className="report-columns">
          <div>
            <h3>Strong Areas</h3>
            <ul>{(report.strong_areas || []).map((item) => <li key={item}>{item}</li>)}</ul>
          </div>
          <div>
            <h3>Areas to Improve</h3>
            <ul>{(report.areas_to_improve || []).map((item) => <li key={item}>{item}</li>)}</ul>
          </div>
        </div>

        <h3>AI Recommendations</h3>
        <ul>
          {(report.recommendations || []).map((item) => (
            <li key={item.day}>
              <strong>{item.day}:</strong> {item.plan}
            </li>
          ))}
        </ul>

        <div className="report-summary">
          <h3>Summary</h3>
          <p>{report.summary}</p>
        </div>
      </div>
    </div>
  );
}

export default ReportPage;
