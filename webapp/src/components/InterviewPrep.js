import React, { useState } from "react";

export default function InterviewPrep({ data }) {
  const [activeTab, setActiveTab] = useState("technical");

  const questionsByTab = {
    technical: data.technicalQuestions,
    behavioral: data.behavioralQuestions,
    companySpecific: data.companySpecificQuestions,
  };

  return (
    <div className="interview-prep">
      <nav className="prep-tabs">
        <button
          className={activeTab === "technical" ? "active" : ""}
          onClick={() => setActiveTab("technical")}
        >
          Technical
        </button>
        <button
          className={activeTab === "behavioral" ? "active" : ""}
          onClick={() => setActiveTab("behavioral")}
        >
          Behavioral
        </button>
        <button
          className={activeTab === "companySpecific" ? "active" : ""}
          onClick={() => setActiveTab("companySpecific")}
        >
          Company-Specific
        </button>
      </nav>

      <ul className="questions-list">
        {questionsByTab[activeTab].map((q, idx) => (
          <li key={idx} className="question-item">
            {q}
          </li>
        ))}
      </ul>
    </div>
  );
}
