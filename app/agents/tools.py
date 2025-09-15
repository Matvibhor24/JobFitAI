from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from typing import Dict, List, Any
import requests
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv

load_dotenv()
search_tool = TavilySearch(max_results=5)


@tool
def extract_resume_structure(resume_text: str) -> Dict[str, Any]:
    """Extract structured information from resume text"""
    # This would normally use NLP/LLM to parse resume
    # For now, return a structured format
    return {
        "name": "Extracted from resume",
        "skills": ["Python", "React", "AI/ML"],
        "experience": ["Software Engineer", "AI Developer"],
        "education": ["Computer Science Degree"]
    }


@tool
def search_company_info(company_name: str) -> Dict[str, Any]:
    """Search for company hiring trends and information"""
    try:
        # Use Tavily search to find company info
        results = search_tool.invoke(
            f"{company_name} hiring process interview experience")
        return {
            "search_results": results,
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@tool
def search_interview_questions(job_title: str, company_name: str) -> Dict[str, Any]:
    """Search for interview questions specific to role and company"""
    try:
        query = f"{company_name} {job_title} interview questions experience"
        results = search_tool.invoke(query)
        return {
            "questions": results,
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@tool
def search_company_news(company_name: str) -> Dict[str, Any]:
    """Search for recent company news and updates"""
    try:
        query = f"{company_name} news hiring recent updates"
        results = search_tool.invoke(query)
        return {
            "news": results,
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}
