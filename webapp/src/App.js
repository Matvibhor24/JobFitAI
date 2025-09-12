import React, { useState } from "react";
import Header from "./components/Header";
import Landing from "./components/Landing";
import InputForm from "./components/InputForm";
import ResultsDashboard from "./components/ResultsDashboard";

// Sample Data as in previous versions
const sampleData = {
  sampleResume: `John Doe
Software Developer

EXPERIENCE:
- 3+ years developing web applications using React, Node.js, and Python
- Built RESTful APIs and microservices architecture
- Experience with AWS, Docker, and CI/CD pipelines
- Led team of 4 developers on e-commerce platform

SKILLS:
JavaScript, Python, React, Node.js, PostgreSQL, MongoDB, Git, AWS, Docker

EDUCATION:
B.Tech Computer Science - XYZ University (2020)`,
  sampleJobDescription: {
    company: "Tech Innovations Inc",
    position: "Senior Full Stack Developer",
    description:
      "We are looking for a Senior Full Stack Developer with 5+ years of experience. Required skills: React, Node.js, Python, AWS, PostgreSQL. Experience with microservices and team leadership preferred. You will work on our core platform serving 1M+ users.",
  },
  jobFitAnalysis: {
    score: 78,
    strengths: [
      "Strong match in core technologies: React, Node.js, Python",
      "Relevant AWS and database experience",
      "Leadership experience aligns with team lead expectations",
      "Microservices architecture experience",
    ],
    improvements: [
      "Highlight specific team leadership achievements with metrics",
      "Add more details about AWS services used",
      "Mention specific PostgreSQL projects",
      "Quantify the impact of your microservices work",
    ],
    missingKeywords: [
      "PostgreSQL",
      "microservices",
      "scalability",
      "team leadership",
      "user-facing applications",
    ],
    recommendations: [
      "Add 'Led cross-functional team of 4 developers, resulting in 30% faster delivery'",
      "Include specific AWS services: 'EC2, RDS, Lambda, S3'",
      "Mention database optimization: 'Optimized PostgreSQL queries reducing response time by 40%'",
    ],
  },
  interviewPrep: {
    technicalQuestions: [
      "Explain the difference between REST and GraphQL",
      "How would you scale a web application to handle 1M users?",
      "Describe your experience with microservices architecture",
      "Walk me through your approach to database optimization",
    ],
    behavioralQuestions: [
      "Tell me about a time you led a challenging project",
      "How do you handle conflicting priorities in a fast-paced environment?",
      "Describe a situation where you had to learn a new technology quickly",
    ],
    companySpecificQuestions: [
      "Why are you interested in working at Tech Innovations Inc?",
      "How would you contribute to our platform serving 1M+ users?",
      "What interests you about our mission to democratize technology?",
    ],
  },
  companyInsights: {
    hiringTrends: [
      "Actively hiring 15+ developers across all levels",
      "Focus on full-stack developers with cloud experience",
      "Recent expansion into AI/ML team",
      "Remote-first company culture",
    ],
    interviewProcess: [
      "Initial screening call (30 mins)",
      "Technical assessment (90 mins)",
      "System design round (60 mins)",
      "Cultural fit interview (45 mins)",
      "Final round with engineering manager",
    ],
    employeeExperiences: [
      "Positive work-life balance according to recent Glassdoor reviews",
      "Strong learning and development opportunities",
      "Competitive compensation with equity options",
      "Flexible remote work policy",
    ],
  },
  webResearch: {
    latestNews: [
      "Tech Innovations Inc raised $50M Series B funding (Last month)",
      "Launched new AI-powered features on their platform",
      "Acquired small startup to expand their team",
      "CEO interview about scaling engineering teams",
    ],
    recentExperiences: [
      "Software Engineer shared positive interview experience on LinkedIn",
      "Technical round focuses on system design and scalability",
      "Company values cultural fit and collaborative mindset",
      "Average interview process takes 2-3 weeks",
    ],
  },
};

export default function App() {
  const [currentPage, setCurrentPage] = useState("landing");
  const [inputData, setInputData] = useState({
    resume: sampleData.sampleResume,
    jobDescription: sampleData.sampleJobDescription.description,
    company: sampleData.sampleJobDescription.company,
    position: sampleData.sampleJobDescription.position,
  });
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Simulated backend call
  const analyzeJobFit = () => {
    setLoading(true);
    setTimeout(() => {
      setAnalysisResult(sampleData);
      setLoading(false);
      setCurrentPage("results");
    }, 1500);
  };

  const startNewAnalysis = () => {
    setAnalysisResult(null);
    setInputData({
      resume: "",
      jobDescription: "",
      company: "",
      position: "",
    });
    setCurrentPage("input");
  };

  return (
    <div>
      <Header onNewAnalysis={startNewAnalysis} showNewAnalysis={currentPage === "results"} onNavigate={setCurrentPage} />
      {currentPage === "landing" && <Landing onStart={() => setCurrentPage("input")} />}
      {currentPage === "input" && (
        <InputForm
          inputData={inputData}
          setInputData={setInputData}
          onAnalyze={analyzeJobFit}
          loading={loading}
        />
      )}
      {currentPage === "results" && analysisResult && (
        <ResultsDashboard data={analysisResult} onNewAnalysis={startNewAnalysis} loading={loading} />
      )}
    </div>
  );
}
