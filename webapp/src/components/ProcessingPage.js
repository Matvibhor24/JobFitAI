import React from "react";

export default function ProcessingPage({
  progress = "Starting...",
  fileName = "",
  onCancel = () => {},
}) {
  return (
    <section className="section processing-page">
      <div className="container">
        <div style={{ textAlign: "center", padding: "2rem" }}>
          <h2>Processing Your Resume</h2>

          {fileName && <p>File: {fileName}</p>}

          <div className="progress-indicator">
            <div className="spinner"></div>
            <p
              style={{
                marginTop: "1rem",
                fontSize: "1.1rem",
                color: "#2274a5",
              }}
            >
              {progress}
            </p>
          </div>

          <button
            onClick={onCancel}
            className="btn btn--secondary"
            style={{ marginTop: "2rem" }}
          >
            Cancel & Start New Analysis
          </button>
        </div>
      </div>
    </section>
  );
}
