import React from "react";

export default function Landing({ onStart }) {
  return (
    <section className="section landing active">
      <div className="container hero">
        <div className="hero-content">
          <h1 className="hero-title">Analyze Your Job Fit with AI-Powered Insights</h1>
          <p className="hero-subtitle">
            Get personalized CV optimization, interview preparation, and company insights to land your dream job
          </p>
          <button className="btn btn--primary btn--lg" onClick={onStart}>
            Start Analysis
          </button>
        </div>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Job Fit Analysis</h3>
            <p>AI-powered matching between your CV and job descriptions with detailed scoring</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📝</div>
            <h3>CV Optimization</h3>
            <p>Get specific suggestions to improve your resume with missing keywords and recommendations</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🎤</div>
            <h3>Interview Preparation</h3>
            <p>Practice technical and behavioral questions tailored to your role</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3>Company Insights</h3>
            <p>Latest hiring trends and interview experiences from real candidates</p>
          </div>
        </div>
      </div>
    </section>
  );
}
