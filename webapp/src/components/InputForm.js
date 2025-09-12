import React from "react";

export default function InputForm({ inputData, setInputData, onAnalyze, loading }) {
  const onChange = (e) => {
    const { name, value } = e.target;
    setInputData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputData.resume.trim() || !inputData.jobDescription.trim()) {
      alert("Please enter both resume and job description.");
      return;
    }
    onAnalyze();
  };

  return (
    <section className="section input-form">
      <div className="container">
        <form onSubmit={handleSubmit}>
          <label htmlFor="resume">Upload or paste your resume/CV</label>
          <textarea
            id="resume"
            name="resume"
            rows="10"
            value={inputData.resume}
            onChange={onChange}
            placeholder="Paste your resume or CV here..."
            required
          ></textarea>

          <label htmlFor="company">Company Name</label>
          <input
            type="text"
            id="company"
            name="company"
            value={inputData.company}
            onChange={onChange}
            placeholder="Company name"
          />

          <label htmlFor="position">Role / Position Title</label>
          <input
            type="text"
            id="position"
            name="position"
            value={inputData.position}
            onChange={onChange}
            placeholder="Position title"
          />

          <label htmlFor="jobDescription">Enter job description and company details</label>
          <textarea
            id="jobDescription"
            name="jobDescription"
            rows="10"
            value={inputData.jobDescription}
            onChange={onChange}
            placeholder="Paste the job description here..."
            required
          ></textarea>

          <button type="submit" className="btn btn--primary btn--lg" disabled={loading}>
            {loading ? "Analyzing..." : "Analyze Job Fit"}
          </button>
        </form>
      </div>
    </section>
  );
}
