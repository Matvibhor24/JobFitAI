import React from "react";

export default function CompanyInsights({ insights }) {
  if (!insights || typeof insights !== "object") {
    return <p>No insights available yet.</p>;
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-3">Company Insights</h2>
      <ul className="list-disc ml-6 space-y-2">
        {Object.entries(insights).map(([text, url], i) => (
          <li key={i}>
            {text}{" "}
            {url && (
              <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 underline ml-1"
              >
                [Source]
              </a>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

