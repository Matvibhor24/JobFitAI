import React from "react";

export default function WebResearch({ data }) {
  return (
    <div className="web-research">
      <h3>Latest Hiring News</h3>
      <ul>
        {data.latestNews.map((news, idx) => (
          <li key={idx}>📰 {news}</li>
        ))}
      </ul>

      <h3>Recent Interview Experiences</h3>
      <ul>
        {data.recentExperiences.map((exp, idx) => (
          <li key={idx}>💡 {exp}</li>
        ))}
      </ul>
    </div>
  );
}
