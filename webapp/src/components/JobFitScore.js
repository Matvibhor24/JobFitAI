import React from "react";

export default function JobFitScore({ score }) {
  const color =
    score >= 80 ? "#33a853" : score >= 60 ? "#fbbc05" : "#ea4335";

  return (
    <div className="job-fit-score">
      <svg width="150" height="150" viewBox="0 0 36 36" className="circular-chart">
        <path
          className="circle-bg"
          d="M18 2.0845
           a 15.9155 15.9155 0 0 1 0 31.831
           a 15.9155 15.9155 0 0 1 0 -31.831"
          fill="none"
          stroke="#eee"
          strokeWidth="2"
        />
        <path
          className="circle"
          stroke={color}
          strokeWidth="2"
          strokeDasharray={`${score}, 100`}
          d="M18 2.0845
           a 15.9155 15.9155 0 0 1 0 31.831
           a 15.9155 15.9155 0 0 1 0 -31.831"
          fill="none"
          strokeLinecap="round"
        />
        <text x="18" y="20.35" className="percentage" fill={color} textAnchor="middle" fontSize="8">
          {score}%
        </text>
      </svg>
      <p className="summary">
        {score >= 80
          ? "Excellent fit for the role"
          : score >= 60
          ? "Good match, some areas to improve"
          : "Low fit, consider revising your CV or role"}
      </p>
    </div>
  );
}
