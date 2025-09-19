import React from "react";

export default function InterviewPrep({ interviewPrep }) {
  if (!interviewPrep || typeof interviewPrep !== "object") {
    return <p>No interview preparation data available yet.</p>;
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-3">Interview Preparation</h2>
      <ul className="list-disc ml-6 space-y-2">
        {Object.entries(interviewPrep).map(([text, url], i) => (
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

