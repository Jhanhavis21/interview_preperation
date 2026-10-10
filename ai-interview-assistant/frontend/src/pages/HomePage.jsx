import FeatureCard from '../components/FeatureCard';

const features = [
  {
    title: 'Role-specific preparation',
    description: 'Generate questions matching your target role, experience, and skills.',
  },
  {
    title: 'AI-powered evaluation',
    description: 'Get detailed feedback across technical correctness, clarity, and depth.',
  },
  {
    title: 'Adaptive follow-up',
    description: 'Continue the conversation with questions tailored to your previous answer.',
  },
];

function HomePage({ onStart }) {
  return (
    <div className="page home-page">
      <section className="hero">
        <div>
          <p className="eyebrow">AI Interview Preparation Assistant</p>
          <h1>Practice interviews with AI and improve your technical and communication skills.</h1>
          <p className="subtext">
            Prepare for technical and HR interviews with personalized questions, adaptive follow-ups,
            and objective feedback designed for students and job seekers.
          </p>
          <button className="primary-button" onClick={onStart}>
            Start Interview
          </button>
        </div>
      </section>

      <section className="feature-grid">
        {features.map((feature) => (
          <FeatureCard key={feature.title} title={feature.title} description={feature.description} />
        ))}
      </section>

      <section className="process-section">
        <h2>How It Works</h2>
        <div className="steps-grid">
          <div className="step-box">
            <span>1</span>
            <h3>Set up your profile</h3>
            <p>Select your role, experience, skills, and interview preferences.</p>
          </div>
          <div className="step-box">
            <span>2</span>
            <h3>Answer AI questions</h3>
            <p>Respond to role-aligned interview questions with realistic interview conditions.</p>
          </div>
          <div className="step-box">
            <span>3</span>
            <h3>Review feedback</h3>
            <p>Improve with AI scoring, sample answers, and final recommendations.</p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default HomePage;
