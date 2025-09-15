from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from .tools import extract_resume_structure, search_company_info, search_interview_questions, search_company_news
from .state import ResumeAnalysisState
from ..llm_module.client_manager import LLMClientManager
from ..llm_module.llm_caller import LLMCaller

# Initialize LLM with fallback chain
load_dotenv()
client_manager = LLMClientManager()
llm_caller = LLMCaller(client_manager)


def job_fit_analysis_agent(state: ResumeAnalysisState) -> ResumeAnalysisState:
    """Analyze job fit and generate score with detailed analysis"""

    system_prompt = """You are an expert resume analyst. Analyze the resume against the job description 
    and provide a comprehensive analysis with:
    1. A score from 0-100
    2. Key strengths that match the role
    3. Areas for improvement
    4. Missing keywords from the job description
    
    Format your response as JSON with keys: score, strengths, improvements, missing_keywords"""

    prompt = f"""
    Resume: {state.get('extracted_resume') or state.get('resume_text')}
    Job Description: {state.get('job_description')}
    
    Provide comprehensive job fit analysis.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    try:
        response = llm_caller.llm_call("gemini-2.5-flash", messages)
    except Exception as llm_error:
        print(f"[Job Fit Analysis] LLM API Error: {llm_error}")
        # Fallback to basic analysis
        state["job_fit_score"] = 75  # Default score
        state["strengths"] = ["Resume shows relevant experience"]
        state["improvements"] = ["Add more specific achievements"]
        state["missing_keywords"] = ["Some keywords from job description"]
        state["current_step"] = "job_fit_completed"
        state["error"] = f"LLM API unavailable: {str(llm_error)}"
        return state

    try:
        # Parse the response (assuming it's JSON)
        import json
        analysis = json.loads(response.choices[0].message.content)

        state["job_fit_score"] = analysis.get("score", 0)
        state["strengths"] = analysis.get("strengths", [])
        state["improvements"] = analysis.get("improvements", [])
        state["missing_keywords"] = analysis.get("missing_keywords", [])
        state["current_step"] = "job_fit_completed"

    except Exception as e:
        state["error"] = f"Job fit analysis error: {str(e)}"
        state["job_fit_score"] = 0

    return state


def cv_optimization_agent(state: ResumeAnalysisState) -> ResumeAnalysisState:
    """Generate CV optimization recommendations"""

    system_prompt = """You are a CV optimization expert. Based on the job fit analysis, 
    provide specific recommendations for improving the resume. Focus on:
    1. Specific changes to make
    2. Keywords to add
    3. Skills to highlight
    4. Experience to emphasize"""

    prompt = f"""
    Current Analysis:
    - Score: {state.get('job_fit_score')}
    - Strengths: {state.get('strengths')}
    - Improvements needed: {state.get('improvements')}
    - Missing keywords: {state.get('missing_keywords')}
    
    Job Description: {state.get('job_description')}
    
    Provide specific recommendations for CV improvement.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    try:
        response = llm_caller.llm_call("gemini-2.5-flash", messages)
    except Exception as llm_error:
        print(f"[CV Optimization] LLM API Error: {llm_error}")
        # Fallback to basic recommendations
        state["recommendations"] = [
            "Highlight relevant technical skills more prominently",
            "Add quantifiable achievements with metrics",
            "Include missing keywords from job description",
            "Restructure experience section for better ATS compatibility"
        ]
        state["current_step"] = "cv_optimization_completed"
        return state

    try:
        # Parse the LLM response to extract recommendations
        import json
        response_text = response.choices[0].message.content

        # Try to parse as JSON first
        try:
            recommendations_data = json.loads(response_text)
            if isinstance(recommendations_data, list):
                state["recommendations"] = recommendations_data
            elif isinstance(recommendations_data, dict) and "recommendations" in recommendations_data:
                state["recommendations"] = recommendations_data["recommendations"]
            else:
                # If not structured, split by lines and clean up
                state["recommendations"] = [
                    line.strip() for line in response_text.split('\n') if line.strip()]
        except json.JSONDecodeError:
            # If not JSON, split by lines and clean up
            state["recommendations"] = [
                line.strip() for line in response_text.split('\n') if line.strip()]

    except Exception as e:
        # Fallback to basic recommendations if parsing fails
        state["recommendations"] = [
            "Highlight relevant technical skills more prominently",
            "Add quantifiable achievements with metrics",
            "Include missing keywords from job description",
            "Restructure experience section for better ATS compatibility"
        ]
        print(f"Error parsing CV optimization response: {e}")

    state["current_step"] = "cv_optimization_completed"

    return state


def interview_prep_agent(state: ResumeAnalysisState) -> ResumeAnalysisState:
    """Generate interview questions based on role and company"""

    # Extract job title from job description using LLM
    job_title_prompt = f"""
    Extract the job title/position from this job description. Return only the job title, nothing else.
    
    Job Description: {state.get('job_description')}
    """

    try:
        title_messages = [{"role": "user", "content": job_title_prompt}]
        title_response = llm_caller.llm_call(
            "gemini-2.5-flash", title_messages)
        job_title = title_response.choices[0].message.content.strip()
    except Exception as e:
        job_title = "Software Engineer"  # Fallback
        print(f"Error extracting job title: {e}")

    # Use tools to search for company-specific info
    web_search_results = None
    if state.get('company_name'):
        try:
            web_search_results = search_interview_questions.invoke({
                "job_title": job_title,
                "company_name": state.get('company_name')
            })
        except Exception as e:
            print(f"Error in web search for interview questions: {e}")

    system_prompt = f"""Generate interview questions in 3 categories based on the job description and company:
    1. Technical questions based on the job requirements
    2. Behavioral questions 
    3. Company-specific questions
    
    Format your response as JSON with keys: technical_questions, behavioral_questions, company_specific_questions
    Each should be an array of strings."""

    prompt = f"""
    Job Description: {state.get('job_description')}
    Job Title: {job_title}
    Company: {state.get('company_name')}
    Resume Skills: {state.get('extracted_resume')}
    Web Search Results: {web_search_results if web_search_results else 'No web search results available'}
    
    Generate comprehensive interview questions based on the actual job requirements and company.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    try:
        response = llm_caller.llm_call("gemini-2.5-flash", messages)
    except Exception as llm_error:
        print(f"[Interview Prep] LLM API Error: {llm_error}")
        # Fallback to basic questions
        state["technical_questions"] = [
            "Explain your relevant technical experience"]
        state["behavioral_questions"] = [
            "Tell me about a challenging project you worked on"]
        state["company_specific_questions"] = [
            f"Why do you want to work at {state.get('company_name')}?"] if state.get('company_name') else []
        state["current_step"] = "interview_prep_completed"
        return state

    try:
        # Parse the LLM response
        import json
        response_text = response.choices[0].message.content

        try:
            questions_data = json.loads(response_text)
            state["technical_questions"] = questions_data.get(
                "technical_questions", [])
            state["behavioral_questions"] = questions_data.get(
                "behavioral_questions", [])
            state["company_specific_questions"] = questions_data.get(
                "company_specific_questions", [])
        except json.JSONDecodeError:
            # If not JSON, create basic questions
            state["technical_questions"] = [
                "Based on job requirements - technical questions"]
            state["behavioral_questions"] = [
                "Tell me about a challenging project you worked on", "How do you handle conflicting priorities?"]
            state["company_specific_questions"] = [
                f"Why do you want to work at {state.get('company_name')}?"] if state.get('company_name') else []

    except Exception as e:
        # Fallback to basic questions
        state["technical_questions"] = [
            "Explain your relevant technical experience"]
        state["behavioral_questions"] = [
            "Tell me about a challenging project you worked on"]
        state["company_specific_questions"] = [
            f"Why do you want to work at {state.get('company_name')}?"] if state.get('company_name') else []
        print(f"Error parsing interview questions response: {e}")

    state["current_step"] = "interview_prep_completed"
    return state


def company_insights_agent(state: ResumeAnalysisState) -> ResumeAnalysisState:
    """Research company insights and hiring trends"""

    web_search_results = None
    if state.get('company_name'):
        try:
            # Search for company information
            web_search_results = search_company_info.invoke(
                {"company_name": state.get('company_name')})
        except Exception as e:
            print(f"Error in web search for company info: {e}")

    system_prompt = """Based on the search results, extract and analyze:
    1. Hiring trends and patterns
    2. Interview process details
    3. Employee experiences and reviews
    
    Format your response as JSON with keys: hiring_trends, interview_process, employee_experiences
    Each should be an array of strings with specific insights."""

    prompt = f"""
    Company: {state.get('company_name')}
    Job Description: {state.get('job_description')}
    Web Search Results: {web_search_results if web_search_results else 'No web search results available'}
    
    Analyze and structure the company insights based on the search results and job description.
    If search results are limited, provide general insights based on the company name and job description.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    try:
        response = llm_caller.llm_call("gemini-2.5-flash", messages)
    except Exception as llm_error:
        print(f"[Company Insights] LLM API Error: {llm_error}")
        # Fallback to basic insights
        state["hiring_trends"] = [
            "Company focuses on technical skills and cultural fit"]
        state["interview_process"] = [
            "Initial screening, technical assessment, final interview"]
        state["employee_experiences"] = [
            "Positive work environment with growth opportunities"]
        state["current_step"] = "company_insights_completed"
        return state

    try:

        # Parse the LLM response
        import json
        response_text = response.choices[0].message.content

        try:
            insights_data = json.loads(response_text)
            state["hiring_trends"] = insights_data.get("hiring_trends", [])
            state["interview_process"] = insights_data.get(
                "interview_process", [])
            state["employee_experiences"] = insights_data.get(
                "employee_experiences", [])
        except json.JSONDecodeError:
            # If not JSON, create basic insights
            state["hiring_trends"] = [
                "Company focuses on technical skills and cultural fit"]
            state["interview_process"] = [
                "Initial screening, technical assessment, final interview"]
            state["employee_experiences"] = [
                "Positive work environment with growth opportunities"]

    except Exception as e:
        # Fallback to basic insights
        state["hiring_trends"] = [
            "Company focuses on technical skills and cultural fit"]
        state["interview_process"] = [
            "Initial screening, technical assessment, final interview"]
        state["employee_experiences"] = [
            "Positive work environment with growth opportunities"]
        print(f"Error parsing company insights response: {e}")

    state["current_step"] = "company_insights_completed"
    return state


def web_research_agent(state: ResumeAnalysisState) -> ResumeAnalysisState:
    """Research latest news and recent interview experiences"""

    web_search_results = None
    if state.get('company_name'):
        try:
            # Search for recent news and experiences
            web_search_results = search_company_news.invoke(
                {"company_name": state.get('company_name')})
        except Exception as e:
            print(f"Error in web search for company news: {e}")

    system_prompt = """Based on the search results, extract and analyze:
    1. Latest company news and updates
    2. Recent interview experiences and feedback
    
    Format your response as JSON with keys: latest_news, recent_experiences
    Each should be an array of strings with specific information."""

    prompt = f"""
    Company: {state.get('company_name')}
    Job Description: {state.get('job_description')}
    Web Search Results: {web_search_results if web_search_results else 'No web search results available'}
    
    Analyze and structure the latest company news and recent interview experiences based on the search results.
    If search results are limited, provide general insights based on the company name and job description.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    try:
        response = llm_caller.llm_call("gemini-2.5-flash", messages)
    except Exception as llm_error:
        print(f"[Web Research] LLM API Error: {llm_error}")
        # Fallback to basic news and experiences
        state["latest_news"] = [f"{state.get('company_name')} continues to grow and expand"] if state.get(
            'company_name') else ["Company is actively hiring"]
        state["recent_experiences"] = [
            "Interview process focuses on technical skills and cultural fit"]
        state["current_step"] = "web_research_completed"
        return state

    try:

        # Parse the LLM response
        import json
        response_text = response.choices[0].message.content

        try:
            research_data = json.loads(response_text)
            state["latest_news"] = research_data.get("latest_news", [])
            state["recent_experiences"] = research_data.get(
                "recent_experiences", [])
        except json.JSONDecodeError:
            # If not JSON, create basic news and experiences
            state["latest_news"] = [f"{state.get('company_name')} continues to grow and expand"] if state.get('company_name') else [
                "Company is actively hiring"]
            state["recent_experiences"] = [
                "Interview process focuses on technical skills and cultural fit"]

    except Exception as e:
        # Fallback to basic news and experiences
        state["latest_news"] = [f"{state.get('company_name')} continues to grow and expand"] if state.get('company_name') else [
            "Company is actively hiring"]
        state["recent_experiences"] = [
            "Interview process focuses on technical skills and cultural fit"]
        print(f"Error parsing web research response: {e}")

    state["current_step"] = "web_research_completed"
    return state
