import json
import os
import base64
from bson import ObjectId
from pdf2image import convert_from_path
from dotenv import load_dotenv
from ..db.collections.files import files_collection

from app.agents.workflow import resume_workflow
from app.agents.state import ResumeAnalysisState
from app.llm_module.client_manager import LLMClientManager
from app.llm_module.llm_caller import LLMCaller

load_dotenv()
client_manager = LLMClientManager()
llm_caller = LLMCaller(client_manager)


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


async def process_file(file_id: str, file_path: str):
    print(f"[Worker] process_file start for ID {file_id}")
    doc = await files_collection.find_one({"_id": ObjectId(file_id)})
    company = doc.get("company_name", "")
    job_description = doc.get("job_description", "")
    position = doc.get("position", "")
    print(f"[Worker] Retrieved job details for ID {file_id}")

    await files_collection.update_one(
        {"_id": ObjectId(file_id)}, {"$set": {"status": "processing"}}
    )

    pages = convert_from_path(file_path)
    print(f"[Worker] Converted PDF to {len(pages)} pages")
    img_paths = []
    for i, page in enumerate(pages):
        img_path = f"/mnt/uploads/images/{file_id}/img-{i}.jpg"
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        page.save(img_path, "JPEG")
        img_paths.append(img_path)

    img_b64 = encode_image(img_paths[0])
    print(f"[Worker] Extracting text via LLM for ID {file_id}")
    messages = [
        {"role": "system", "content": "Extract all text content from this resume image."},
        {"role": "user", "content": f"data:image/jpeg;base64,{img_b64}"}
    ]
    try:
        res = llm_caller.llm_call("gemini-2.5-flash", messages)
        resume_text = res.choices[0].message.content
    except Exception as e:
        print(f"[Worker] LLM extraction failed: {e}")
        resume_text = "Resume text extraction failed - using fallback"
    print(f"[Worker] Extracted resume text length {len(resume_text)}")

    initial_state = ResumeAnalysisState(
        resume_text=resume_text,
        job_description=job_description,
        company_name=company,
        position=position,
        current_step="starting"
    )
    print(f"[Worker] Invoking LangGraph workflow for ID {file_id}")
    final_state = resume_workflow.invoke(initial_state)
    print(
        f"[Worker] Workflow completed with score {final_state.job_fit_score}")

    analysis_result = {
        "jobFitAnalysis": {
            "score": final_state.job_fit_score or 0,
            "strengths": final_state.strengths or [],
            "improvements": final_state.improvements or [],
            "missingKeywords": final_state.missing_keywords or [],
            "recommendations": final_state.recommendations or []
        },
        "interviewPrep": {
            "technicalQuestions": final_state.technical_questions or [],
            "behavioralQuestions": final_state.behavioral_questions or [],
            "companySpecificQuestions": final_state.company_specific_questions or []
        },
        "companyInsights": {
            "hiringTrends": final_state.hiring_trends or [],
            "interviewProcess": final_state.interview_process or [],
            "employeeExperiences": final_state.employee_experiences or []
        },
        "webResearch": {
            "latestNews": final_state.latest_news or [],
            "recentExperiences": final_state.recent_experiences or []
        }
    }
    print(f"[Worker] Built analysis_result for ID {file_id}")

    await files_collection.update_one(
        {"_id": ObjectId(file_id)},
        {"$set": {
            "status": "processed",
            "score": final_state.job_fit_score or 0,
            "result": json.dumps(analysis_result)
        }}
    )
    print(f"[Worker] Updated DB for ID {file_id} with final results")


async def process_text(file_id: str, resume_text: str):
    print(f"[Worker] process_text start for ID {file_id}")
    doc = await files_collection.find_one({"_id": ObjectId(file_id)})
    company = doc.get("company_name", "")
    job_description = doc.get("job_description", "")
    position = doc.get("position", "")

    initial_state = ResumeAnalysisState(
        resume_text=resume_text,
        job_description=job_description,
        company_name=company,
        position=position,
        current_step="starting"
    )

    print(f"[Worker] Invoking LangGraph workflow for ID {file_id}")
    final_state = resume_workflow.invoke(initial_state)
    print(
        f"[Worker] Workflow completed with score {final_state.job_fit_score}")

    analysis_result = {
        "jobFitAnalysis": {
            "score": final_state.job_fit_score or 0,
            "strengths": final_state.strengths or [],
            "improvements": final_state.improvements or [],
            "missingKeywords": final_state.missing_keywords or [],
            "recommendations": final_state.recommendations or []
        },
        "interviewPrep": {
            "technicalQuestions": final_state.technical_questions or [],
            "behavioralQuestions": final_state.behavioral_questions or [],
            "companySpecificQuestions": final_state.company_specific_questions or []
        },
        "companyInsights": {
            "hiringTrends": final_state.hiring_trends or [],
            "interviewProcess": final_state.interview_process or [],
            "employeeExperiences": final_state.employee_experiences or []
        },
        "webResearch": {
            "latestNews": final_state.latest_news or [],
            "recentExperiences": final_state.recent_experiences or []
        }
    }
    print(f"[Worker] Built analysis_result for ID {file_id}")

    await files_collection.update_one(
        {"_id": ObjectId(file_id)},
        {"$set": {
            "status": "processed",
            "score": final_state.job_fit_score or 0,
            "result": json.dumps(analysis_result)
        }}
    )
    print(f"[Worker] Updated DB for ID {file_id} with final results")
