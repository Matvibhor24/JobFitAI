import React, { useState } from "react";
import JobFitScore from "./JobFitScore";
import CVOptimization from "./CVOptimization";
import InterviewPrep from "./InterviewPrep";
import CompanyInsights from "./CompanyInsights";
import WebResearch from "./WebResearch";

export default function ResultsDashboard({ data, onNewAnalysis, loading }) {
  const [activeTab, setActiveTab] = useState("jobFitScore");

  return (
    <section className="section results-dashboard">
      <div className="container">
        <div className="results-header">
          <h2>Job Fit Analysis Results</h2>
          <button className="btn btn--secondary btn--sm" onClick={onNewAnalysis}>
            New Analysis
          </button>
        </div>

        <nav className="results-tabs">
          <button
            className={activeTab === "jobFitScore" ? "active" : ""}
            onClick={() => setActiveTab("jobFitScore")}
          >
            Job Fit Score
          </button>
          <button
            className={activeTab === "cvOptimization" ? "active" : ""}
            onClick={() => setActiveTab("cvOptimization")}
          >
            CV Optimization
          </button>
          <button
            className={activeTab === "interviewPrep" ? "active" : ""}
            onClick={() => setActiveTab("interviewPrep")}
          >
            Interview Preparation
          </button>
          <button
            className={activeTab === "companyInsights" ? "active" : ""}
            onClick={() => setActiveTab("companyInsights")}
          >
            Company Insights
          </button>
          <button
            className={activeTab === "webResearch" ? "active" : ""}
            onClick={() => setActiveTab("webResearch")}
          >
            Web Research
          </button>
        </nav>

        <div className="results-content">
          {loading && <p>Loading results...</p>}

          {!loading && activeTab === "jobFitScore" && <JobFitScore score={data.jobFitAnalysis.score} />}
          {!loading && activeTab === "cvOptimization" && <CVOptimization data={data.jobFitAnalysis} />}
          {!loading && activeTab === "interviewPrep" && <InterviewPrep data={data.interviewPrep} />}
          {!loading && activeTab === "companyInsights" && <CompanyInsights data={data.companyInsights} />}
          {!loading && activeTab === "webResearch" && <WebResearch data={data.webResearch} />}
        </div>
      </div>
    </section>
  );
}
