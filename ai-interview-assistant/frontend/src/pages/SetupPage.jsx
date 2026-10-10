const roleOptions = [
  'Java Developer',
  'Python Developer',
  'Full Stack Developer',
  'Software Engineer',
  'Data Analyst',
  'Cloud Engineer',
];

const experienceLevels = ['Fresher', '0–2 years', '2–5 years'];
const interviewTypes = ['Technical', 'HR', 'Behavioral', 'Mixed'];
const difficultyLevels = ['Easy', 'Medium', 'Hard'];
const questionCounts = [5, 10, 15];

function SetupPage({ form, onChange, onSubmit, loading, error }) {
  return (
    <div className="page setup-page">
      <div className="panel">
        <h1>Interview Setup</h1>
        {error && <div className="error-banner">{error}</div>}

        <div className="form-grid">
          <label>
            <span>Job Role</span>
            <select value={form.jobRole} onChange={(e) => onChange('jobRole', e.target.value)}>
              <option value="">Select role</option>
              {roleOptions.map((role) => (
                <option key={role} value={role}>{role}</option>
              ))}
            </select>
          </label>

          <label>
            <span>Experience Level</span>
            <select value={form.experienceLevel} onChange={(e) => onChange('experienceLevel', e.target.value)}>
              <option value="">Select level</option>
              {experienceLevels.map((level) => (
                <option key={level} value={level}>{level}</option>
              ))}
            </select>
          </label>

          <label>
            <span>Interview Type</span>
            <select value={form.interviewType} onChange={(e) => onChange('interviewType', e.target.value)}>
              <option value="">Select type</option>
              {interviewTypes.map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </label>

          <label>
            <span>Difficulty</span>
            <select value={form.difficulty} onChange={(e) => onChange('difficulty', e.target.value)}>
              <option value="">Select difficulty</option>
              {difficultyLevels.map((level) => (
                <option key={level} value={level}>{level}</option>
              ))}
            </select>
          </label>

          <label>
            <span>Number of Questions</span>
            <select value={form.totalQuestions} onChange={(e) => onChange('totalQuestions', Number(e.target.value))}>
              {questionCounts.map((count) => (
                <option key={count} value={count}>{count}</option>
              ))}
            </select>
          </label>
        </div>

        <label className="skills-field">
          <span>Skills</span>
          <textarea
            value={form.skills}
            onChange={(e) => onChange('skills', e.target.value)}
            placeholder="Java, SQL, Spring Boot, HTML, CSS, JavaScript, Git"
            rows={4}
          />
        </label>

        <button className="primary-button" onClick={onSubmit} disabled={loading}>
          {loading ? 'Preparing ...' : 'Start Interview'}
        </button>
      </div>
    </div>
  );
}

export default SetupPage;
