import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import Landing from "./components/Landing";
import InputForm from "./components/InputForm";
import ResultsDashboard from "./components/ResultsDashboard";
import ProcessingPage from "./components/ProcessingPage";
const sampleData = {
  jobFitAnalysis: {
    score: 0,
    strengths: [],
    improvements: [],
    missingKeywords: [],
    recommendations: [],
  },
  interviewPrep: {
    technicalQuestions: [],
    behavioralQuestions: [],
    companySpecificQuestions: [],
  },
  companyInsights: {
    hiringTrends: [],
    interviewProcess: [],
    employeeExperiences: [],
  },
  webResearch: { latestNews: [], recentExperiences: [] },
};

export default function App() {
  const [currentPage, setCurrentPage] = useState("landing");
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileStatus, setFileStatus] = useState(null);
  const [processingProgress, setProcessingProgress] = useState("");
  const [inputData, setInputData] = useState({
    resume: "",
    jobDescription: "",
    company: "",
    position: "",
  });

  useEffect(() => {
    if (fileStatus?.file_id && currentPage === "processing") {
      const eventSource = new EventSource(
        `http://localhost:8000/stream/${fileStatus.file_id}`
      );

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("SSE update:", data);

          if (data.error) {
            setProcessingProgress(`Error: ${data.error}`);
            eventSource.close();
            return;
          }

          setProcessingProgress(data.status);

          if (data.status === "processed") {
            // You only need score + result now
            setAnalysisResult({
              score: data.score || 0,
              result: data.result || "",
            });

            setCurrentPage("results");
            setLoading(false);
            eventSource.close();
          }
        } catch (err) {
          console.error("Invalid SSE data:", event.data);
        }
      };

      eventSource.onerror = () => {
        setProcessingProgress("Connection error");
        eventSource.close();
      };

      return () => eventSource.close();
    }
  }, [fileStatus, currentPage]);

  const analyzeJobFit = async () => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("company_name", inputData.company);
      formData.append("job_description", inputData.jobDescription);
      formData.append("position", inputData.position || "");
      if (selectedFile) formData.append("file", selectedFile);
      else formData.append("resume_text", inputData.resume);

      const resp = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      if (!resp.ok) throw new Error("Upload failed");
      const data = await resp.json();
      setFileStatus({
        file_id: data.file_id,
        name: selectedFile?.name || "text",
      });
      setCurrentPage("processing");
      setProcessingProgress("Starting analysis...");
    } catch (e) {
      alert(e.message);
      setLoading(false);
    }
  };

  const startNewAnalysis = () => {
    setAnalysisResult(null);
    setSelectedFile(null);
    setFileStatus(null);
    setProcessingProgress("");
    setInputData({ resume: "", jobDescription: "", company: "", position: "" });
    setCurrentPage("input");
  };

  useEffect(() => {
    // Load state from storage on first mount
    const savedResult = localStorage.getItem("analysisResult");
    const savedPage = localStorage.getItem("currentPage");
    if (savedResult) setAnalysisResult(JSON.parse(savedResult));
    if (savedPage) setCurrentPage(savedPage);
  }, []);

  useEffect(() => {
    if (analysisResult) {
      localStorage.setItem("analysisResult", JSON.stringify(analysisResult));
    }
  }, [analysisResult]);

  useEffect(() => {
    localStorage.setItem("currentPage", currentPage);
  }, [currentPage]);

  return (
    <>
      <Header
        onNewAnalysis={startNewAnalysis}
        showNewAnalysis={currentPage !== "landing"}
        onNavigate={setCurrentPage}
      />
      {currentPage === "landing" && (
        <Landing onStart={() => setCurrentPage("input")} />
      )}
      {currentPage === "input" && (
        <InputForm
          inputData={inputData}
          setInputData={setInputData}
          selectedFile={selectedFile}
          setSelectedFile={setSelectedFile}
          onAnalyze={analyzeJobFit}
          loading={loading}
        />
      )}
      {currentPage === "processing" && (
        <ProcessingPage
          progress={processingProgress}
          fileName={fileStatus?.name}
          onCancel={startNewAnalysis}
        />
      )}
      {currentPage === "results" && analysisResult && (
        <ResultsDashboard
          data={analysisResult}
          onNewAnalysis={startNewAnalysis}
          loading={loading}
        />
      )}
    </>
  );
}
