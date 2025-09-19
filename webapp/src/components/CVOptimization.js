import React from "react";

export default function CVOptimization({ data = {} }) {
  const strengths = data.strengths || [];
  const improvements = data.improvements || data.areasForImprovement || [];
  const missingKeywords = data.missingKeywords || data.missingKeywordsToAdd || [];
  const recommendations = data.recommendations || data.cvOptimizationSuggestions || [];

  const copy = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      // optionally show small toast
    } catch (e) {
      console.error("Clipboard error", e);
    }
  };

  return (
    <div className="cv-optimization">
      <h3>Strengths</h3>
      <ul>{strengths.length ? strengths.map((s,i)=> <li key={i}>✅ {s}</li>) : <li>No strengths detected.</li>}</ul>

      
      <h3>Areas for Improvement</h3>
      <ul>{improvements.length ? improvements.map((s,i)=> <li key={i}>⚠️ {s}</li>) : <li>No improvements suggested.</li>}</ul>

      <h3>Missing Keywords</h3>
      <ul>{missingKeywords.length ? missingKeywords.map((s,i)=> <li key={i}>🔑 {s}</li>) : <li>No missing keywords suggested.</li>}</ul>

      <h3>Recommended Changes (Copy to clipboard)</h3>
      <ul>
        {recommendations.length ? recommendations.map((item, idx) => (
          <li key={idx} className="recommendation-item">
            {"📝 "}{item}{" "}
            <button onClick={() => copy(item)} title="Copy to clipboard" className="copy-btn">📋</button>
          </li>
        )) : <li>No optimization suggestions.</li>}
      </ul>
    </div>
  );
}
