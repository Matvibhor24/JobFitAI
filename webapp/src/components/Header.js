import React from "react";

export default function Header({ onNewAnalysis, showNewAnalysis, onNavigate }) {
  return (
    <nav className="navbar">
      <div className="container nav-content">
        <div className="logo" onClick={() => onNavigate("landing")} style={{ cursor: "pointer" }}>
          <h2>JobFit AI</h2>
        </div>
        <div className="nav-actions">
          {showNewAnalysis && (
            <button className="btn btn--secondary btn--sm" onClick={onNewAnalysis}>
              New Analysis
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}
