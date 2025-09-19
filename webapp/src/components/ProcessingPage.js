// components/ProcessingPage.jsx
import React from "react";

export default function ProcessingPage({
  progress,
  fileName,
  onCancel,
  jobfitStatus,
  insightsStatus,
  agentStage,
  agentProgress = []
}) {
  return (
    <section className="section processing-page">
      <div className="container">
        <div style={{ textAlign: "center", padding: "2rem" }}>
          <h2>Processing Your Resume</h2>
          {fileName && <p>File: {fileName}</p>}

          <div style={{ marginTop: "1rem", textAlign: "left" }}>
            <h4>Analysis steps</h4>
            <ul>
              <li>
                <strong>JobFit & CV Analysis:</strong>{" "}
                {jobfitStatus === "processed" ? "✅ Done" : jobfitStatus ? `⏳ ${jobfitStatus}` : "Waiting"}
              </li>
              <li>
                <strong>Company Insights / Interview Prep (agent):</strong>{" "}
                {insightsStatus === "processed" ? "✅ Done" : insightsStatus ? `⏳ ${insightsStatus}` : "Queued"}
              </li>
            </ul>

            {agentStage && (
              <div style={{ marginTop: "1rem" }}>
                <strong>Current agent stage:</strong> {agentStage}
                <ul>
                  {agentProgress.length === 0 && <li>Collecting...</li>}
                  {agentProgress.map((p, i) => (
                    <li key={i}>
                      {p.stage} — {p.status} {p.items_count ? `(${p.items_count})` : ""}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="progress-indicator" style={{ marginTop: "1.5rem" }}>
            <div className="spinner"></div>
            <p style={{ marginTop: "1rem", fontSize: "1.1rem", color: "#2274a5" }}>
              {progress || "Starting..."}
            </p>
          </div>

          <button onClick={onCancel} className="btn btn--secondary" style={{ marginTop: "2rem" }}>
            Cancel & Start New Analysis
          </button>
        </div>
      </div>
    </section>
  );
}
