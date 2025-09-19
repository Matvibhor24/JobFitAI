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
from app.agents.prompts import SYSTEM_PROMPT

load_dotenv()
client_manager = LLMClientManager()
llm_caller = LLMCaller(client_manager)


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def parse_llm_json_response(raw_content: str):
    try:
        parsed = json.loads(raw_content)
        return parsed
    except json.JSONDecodeError as e:
        print(f"[Parser] JSON parsing error: {e}")
        return None


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

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""Give me a detailed overall recommendation and precise match score of image of CV/Resume based on this specific job decription of company name - {company} for the postion of {position}. 
                    Job Description: {job_description}. Response strictly in following JSON format strictly.
                    Example valid output:
                    {{
                    "match_score": 85,
                    "overall_recommendations": "Candidate fits well but should include more cloud skills experience..."
                    }}
                    """,
                },
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{img_b64}"}},
            ],
        },
    ]

    # ✅ Safe defaults (always defined)
    match_score = 0
    overall_recommendations = ""
    strengths = []
    weaknesses = []
    areas_for_improvement = []
    cv_optimization_suggestions = []
    keywords_already_matched = []
    missing_keywords_to_add = []

    try:
        res = llm_caller.llm_call("gemini-2.5-flash", messages)
        raw_content = res.choices[0].message.content
        analysis_result = parse_llm_json_response(raw_content) or {}

        match_score = analysis_result.get("match_score", 0)
        overall_recommendations = analysis_result.get(
            "overall_recommendations", "")
        strengths = analysis_result.get("strengths", [])
        weaknesses = analysis_result.get("weaknesses", [])
        areas_for_improvement = analysis_result.get(
            "areas_for_improvement", [])
        cv_optimization_suggestions = analysis_result.get(
            "cv_optimization_suggestions", [])
        keywords_already_matched = analysis_result.get(
            "keywords_already_matched", [])
        missing_keywords_to_add = analysis_result.get(
            "missing_keywords_to_add", [])

        print("score = ", match_score)
        print("SUMMARY = ", overall_recommendations)

    except Exception as e:
        print(f"[Worker] LLM analysis failed: {e}")
        # keep defaults already set above

    await files_collection.update_one(
        {"_id": ObjectId(file_id)},
        {"$set": {
            "status": "processed",
            "jobfit_status": "processed",
            "score": match_score,
            "result": overall_recommendations,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "areas_for_improvement": areas_for_improvement,
            "cv_optimization_suggestions": cv_optimization_suggestions,
            "keywords_already_matched": keywords_already_matched,
            "missing_keywords_to_add": missing_keywords_to_add,
        }}
    )

    print(f"[Worker] Updated DB for ID {file_id} with final results")


async def process_text(file_id: str, resume_text: str):
    print(f"[Worker] process_text start for ID {file_id}")
    await files_collection.update_one(
        {"_id": ObjectId(file_id)}, {"$set": {"status": "processing"}}
    )
    doc = await files_collection.find_one({"_id": ObjectId(file_id)})
    company = doc.get("company_name", "")
    job_description = doc.get("job_description", "")
    position = doc.get("position", "")

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"Give me a detailed analysis of CV/Resume text: {resume_text} ,based on this specific job decription of company name - {company} for the postion of {position}. Job Description: {job_description}"
        }
    ]

    # ✅ initialize defaults so they're always defined
    score = 0
    strengths = []
    weaknesses = []
    areas_for_improvement = []
    cv_optimization_suggestions = []
    keywords_already_matched = []
    missing_keywords_to_add = []
    result = {}
    try:
        res = llm_caller.llm_call("gemini-2.5-flash", messages)
        raw_content = res.choices[0].message.content
        analysis_result = parse_llm_json_response(raw_content)

        match_score = analysis_result.get("match_score", 0)
        overall_recommendations = analysis_result.get(
            "overall_recommendations", "")
        strengths = analysis_result.get("strengths", [])
        weaknesses = analysis_result.get("weaknesses", [])
        areas_for_improvement = analysis_result.get(
            "areas_for_improvement", [])
        cv_optimization_suggestions = analysis_result.get(
            "cv_optimization_suggestions", [])
        keywords_already_matched = analysis_result.get(
            "keywords_already_matched", [])
        missing_keywords_to_add = analysis_result.get(
            "missing_keywords_to_add", [])

    except Exception as e:
        print(f"[Worker] LLM analysis failed: {e}")
        match_score = None
        strengths = []
        weaknesses = []
        areas_for_improvement = []
        cv_optimization_suggestions = []
        interview_preparation_advice = []
        company_insights = {}
        contacts_or_networking_suggestions = []
        overall_recommendations = ""

    await files_collection.update_one(
        {"_id": ObjectId(file_id)},
        {"$set": {
            "status": "processed",
            "jobfit_status": "processed",
            "score": match_score,
            "result": overall_recommendations,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "areas_for_improvement": areas_for_improvement,
            "cv_optimization_suggestions": cv_optimization_suggestions,
            "keywords_already_matched": keywords_already_matched,
            "missing_keywords_to_add": missing_keywords_to_add,
        }}
    )

    print(f"[Worker] Updated DB for ID {file_id} with final results")
