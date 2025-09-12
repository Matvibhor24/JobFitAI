import React from "react";

export default function CompanyInsights({ data }) {
  return (
    <div className="company-insights">
      <h3>Hiring Trends</h3>
      <ul>
        {data.hiringTrends.map((item, idx) => (
          <li key={idx}>📈 {item}</li>
        ))}
      </ul>

      <h3>Interview Process</h3>
      <ol>
        {data.interviewProcess.map((step, idx) => (
          <li key={idx}>{step}</li>
        ))}
      </ol>

      <h3>Recent Employee Experiences</h3>
      <ul>
        {data.employeeExperiences.map((item, idx) => (
          <li key={idx}>💬 {item}</li>
        ))}
      </ul>
    </div>
  );
}
