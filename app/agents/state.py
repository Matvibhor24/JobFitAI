from typing import List, Optional
from langgraph.graph import MessagesState


class ResumeAnalysisState(MessagesState):
    # Inputs
    resume_text: str
    job_description: str
    company_name: str
    position: str
    current_step: str

    # Job fit
    job_fit_score: Optional[int] = None
    strengths: List[str] = []
    improvements: List[str] = []
    missing_keywords: List[str] = []
    recommendations: List[str] = []

    # Interview prep
    technical_questions: List[str] = []
    behavioral_questions: List[str] = []
    company_specific_questions: List[str] = []

    # Company insights
    hiring_trends: List[str] = []
    interview_process: List[str] = []
    employee_experiences: List[str] = []

    # Web research
    latest_news: List[str] = []
    recent_experiences: List[str] = []
