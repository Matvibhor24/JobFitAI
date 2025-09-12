import React from "react";

export default function CVOptimization({ data }) {
  return (
    <div className="cv-optimization">
      <h3>Strengths</h3>
      <ul>
        {data.strengths.map((item, idx) => (
          <li key={idx}>✅ {item}</li>
        ))}
      </ul>

      <h3>Areas for Improvement</h3>
      <ul>
        {data.improvements.map((item, idx) => (
          <li key={idx}>⚠️ {item}</li>
        ))}
      </ul>

      <h3>Missing Keywords</h3>
      <ul>
        {data.missingKeywords.map((item, idx) => (
          <li key={idx}>🔑 {item}</li>
        ))}
      </ul>

      <h3>Recommended Changes</h3>
      <ul>
        {data.recommendations.map((item, idx) => (
          <li key={idx} className="recommendation-item">
            {item}{" "}
            <button
              onClick={() => navigator.clipboard.writeText(item)}
              title="Copy to clipboard"
              className="copy-btn"
            >
              📋
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
