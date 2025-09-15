import React from "react";

export default function JobFitScore({ score = 0, backendResult = "" }) {
  // Clamp score between 0 and 100
  const clamp = (num, min, max) => Math.min(Math.max(num, min), max);
  const safeScore = clamp(score, 0, 100);

  // Interpolate color between red and yellow
  const ratio = safeScore / 100;
  const redRGB = { r: 234, g: 67, b: 53 };
  const yellowRGB = { r: 251, g: 188, b: 5 };
  const r = Math.round(redRGB.r + (yellowRGB.r - redRGB.r) * ratio);
  const g = Math.round(redRGB.g + (yellowRGB.g - redRGB.g) * ratio);
  const b = Math.round(redRGB.b + (yellowRGB.b - redRGB.b) * ratio);
  const fillColor = `rgb(${r}, ${g}, ${b})`;

  return (
    <div className="job-fit-score">
      <div className="score-section">
        <svg
          width="150"
          height="150"
          viewBox="0 0 36 36"
          className="circular-chart"
        >
          {/* Rotate so progress starts at bottom */}
          <g transform="rotate(180 18 18)">
            <path
              d="M18 2.0845
                 a 15.9155 15.9155 0 0 1 0 31.831
                 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke={fillColor}
              strokeWidth="2"
              strokeDasharray={`${safeScore} ${100 - safeScore}`}
              strokeDashoffset="25"
              strokeLinecap="round"
            />
          </g>
          <g transform="rotate(90 18 18)">
            <text
              x="18"
              y="20.35"
              fill={fillColor}
              textAnchor="middle"
              fontSize="8"
            >
              {safeScore}%
            </text>
          </g>
        </svg>

        <p className="summary"><b>
          {safeScore >= 80
            ? "Excellent fit for the role"
            : safeScore >= 60
            ? "Good match, some areas to improve"
            : "Low fit, consider revising your CV or role"}
        </b></p>
      </div>

      {backendResult && (
        <div className="analysis-result">
          <h3>AI Match Analysis</h3>
          <p className="summary">{backendResult}</p>
        </div>
      )}
    </div>
  );
}
