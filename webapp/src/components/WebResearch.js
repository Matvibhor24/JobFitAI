import React from "react";

export default function WebResearch({ webResearch }) {
  if (!webResearch || typeof webResearch !== "object") {
    return <p>No web research data available yet.</p>;
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-3">Web Research</h2>
      <ul className="list-disc ml-6 space-y-2">
        {Object.entries(webResearch).map(([text, url], i) => (
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

