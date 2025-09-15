import React from "react";

export default function InputForm({
  inputData = { resume: "", jobDescription: "", company: "", position: "" },
  setInputData = () => {},
  selectedFile = null,
  setSelectedFile = () => {},
  onAnalyze = () => {},
  loading = false,
}) {
  const onChange = (e) => {
    const { name, value } = e.target;
    setInputData((prev) => ({ ...prev, [name]: value }));
  };

  const onFileChange = (e) => {
    if (e.target.files?.length > 0) {
      setSelectedFile(e.target.files[0]);
      setInputData((prev) => ({ ...prev, resume: "" })); // clear text resume if file uploaded
    } else {
      setSelectedFile(null);
    }
  };

  const onTextChange = (e) => {
    onChange(e);
    if (e.target.name === "resume" && e.target.value.trim() && selectedFile) {
      setSelectedFile(null); // clear file if text is typed
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!selectedFile && !inputData.resume.trim()) {
      alert("Please upload a file or paste your resume.");
      return;
    }
    if (!inputData.company.trim()) {
      alert("Please enter the company name.");
      return;
    }
    if (!inputData.jobDescription.trim()) {
      alert("Please enter the job description.");
      return;
    }

    onAnalyze();
  };

  return (
    <section className="section input-form">
      <div className="container">
        <form onSubmit={handleSubmit}>
          {/* File Upload */}
          <label>Upload your resume/CV</label>
          <input type="file" accept=".pdf" onChange={onFileChange} />
          {selectedFile && (
            <p style={{ color: "green", fontSize: "0.9rem" }}>
              Selected: {selectedFile.name}
            </p>
          )}

          <p style={{ textAlign: "center", margin: "1rem 0", fontWeight: "bold" }}>
            OR
          </p>

          {/* Resume Text */}
          <label htmlFor="resume">Paste your resume/CV here</label>
          <textarea
            id="resume"
            name="resume"
            rows="10"
            value={inputData.resume}
            onChange={onTextChange}
            placeholder="Paste your resume or CV here..."
            disabled={!!selectedFile}
          />

          {/* Company / Job Info */}
          <label htmlFor="company">Company Name *</label>
          <input
            type="text"
            id="company"
            name="company"
            value={inputData.company}
            onChange={onChange}
            required
          />

          <label htmlFor="position">Role / Position Title</label>
          <input
            type="text"
            id="position"
            name="position"
            value={inputData.position}
            onChange={onChange}
          />

          <label htmlFor="jobDescription">Job Description *</label>
          <textarea
            id="jobDescription"
            name="jobDescription"
            rows="10"
            value={inputData.jobDescription}
            onChange={onChange}
            required
          />

          <button
            type="submit"
            className="btn btn--primary btn--lg"
            disabled={loading}
          >
            {loading ? "Analyzing..." : "Analyze Job Fit"}
          </button>
        </form>
      </div>
    </section>
  );
}
