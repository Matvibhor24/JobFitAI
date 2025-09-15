from langgraph.graph import StateGraph, END
from app.llm_module.llm_caller import LLMCaller
from app.llm_module.client_manager import LLMClientManager
import json

client_manager = LLMClientManager()
llm_caller = LLMCaller(client_manager)


def _extract_json_field(output: str, field: str, default):
    """Helper to parse JSON safely from LLM output"""
    try:
        data = json.loads(output)
        return data.get(field, default)
    except Exception:
        return default


# -------------------------------
# Node 1 – Job Fit Analysis
# -------------------------------
def job_fit_node(state: dict):
    messages = [
        {"role": "system", "content": "You are an expert career coach. Analyze resume vs job description."},
        {"role": "user", "content": f"""
Resume:
{state.get("resume_text", "")}

Job Description:
{state.get("job_description", "")}

Company: {state.get("company_name", "")}
Position: {state.get("position", "")}

Provide JSON with:
- score (0–100)
- strengths (list)
- improvements (list)
- missingKeywords (list)
- recommendations (list)
"""}
    ]
    res = llm_caller.llm_call("gemini-2.5-flash", messages)
    output = res.choices[0].message.content

    state["job_fit_score"] = _extract_json_field(output, "score", 70)
    state["strengths"] = _extract_json_field(output, "strengths", [])
    state["improvements"] = _extract_json_field(output, "improvements", [])
    state["missing_keywords"] = _extract_json_field(output, "missingKeywords", [])
    state["recommendations"] = _extract_json_field(output, "recommendations", [])
    state["current_step"] = "job_fit_done"
    return state


# -------------------------------
# Node 2 – Interview Preparation
# -------------------------------
def interview_prep_node(state: dict):
    messages = [
        {"role": "system", "content": "You are an interview coach."},
        {"role": "user", "content": f"""
Generate interview preparation questions for role:
Resume: {state.get("resume_text", "")}
Position: {state.get("position", "")}
Company: {state.get("company_name", "")}

Provide JSON with:
- technicalQuestions
- behavioralQuestions
- companySpecificQuestions
"""}
    ]
    res = llm_caller.llm_call("gemini-2.5-flash", messages)
    output = res.choices[0].message.content

    state["technical_questions"] = _extract_json_field(output, "technicalQuestions", [])
    state["behavioral_questions"] = _extract_json_field(output, "behavioralQuestions", [])
    state["company_specific_questions"] = _extract_json_field(output, "companySpecificQuestions", [])
    state["current_step"] = "interview_prep_done"
    return state


# -------------------------------
# Node 3 – Company Insights
# -------------------------------
def company_insights_node(state: dict):
    messages = [
        {"role": "system", "content": "You are a company research assistant."},
        {"role": "user", "content": f"""
Research company insights for {state.get("company_name", "")}.

Provide JSON with:
- hiringTrends
- interviewProcess
- employeeExperiences
"""}
    ]
    res = llm_caller.llm_call("gemini-2.5-flash", messages)
    output = res.choices[0].message.content

    state["hiring_trends"] = _extract_json_field(output, "hiringTrends", [])
    state["interview_process"] = _extract_json_field(output, "interviewProcess", [])
    state["employee_experiences"] = _extract_json_field(output, "employeeExperiences", [])
    state["current_step"] = "company_insights_done"
    return state


# -------------------------------
# Node 4 – Web Research
# -------------------------------
def web_research_node(state: dict):
    messages = [
        {"role": "system", "content": "You are a research assistant."},
        {"role": "user", "content": f"""
Find recent news and candidate experiences for {state.get("company_name", "")}.

Provide JSON with:
- latestNews
- recentExperiences
"""}
    ]
    res = llm_caller.llm_call("gemini-2.5-flash", messages)
    output = res.choices[0].message.content

    state["latest_news"] = _extract_json_field(output, "latestNews", [])
    state["recent_experiences"] = _extract_json_field(output, "recentExperiences", [])
    state["current_step"] = "web_research_done"
    return state


# -------------------------------
# Build the LangGraph workflow
# -------------------------------
workflow = StateGraph(dict)

workflow.add_node("job_fit", job_fit_node)
workflow.add_node("interview_prep", interview_prep_node)
workflow.add_node("company_insights", company_insights_node)
workflow.add_node("web_research", web_research_node)

workflow.set_entry_point("job_fit")
workflow.add_edge("job_fit", "interview_prep")
workflow.add_edge("interview_prep", "company_insights")
workflow.add_edge("company_insights", "web_research")
workflow.add_edge("web_research", END)

resume_workflow = workflow.compile()
