# app/queue/agent_worker.py
import asyncio
import json
import hashlib
import time
import re
from typing import List, Dict, Any
from urllib.parse import urlparse

import requests
import trafilatura
from duckduckgo_search import DDGS  # pip install duckduckgo-search

from bson import ObjectId
from ..db.collections.files import files_collection
from app.llm_module.client_manager import LLMClientManager
from app.llm_module.llm_caller import LLMCaller

# Initialize your existing LLM client manager / caller
client_manager = LLMClientManager()
llm_caller = LLMCaller(client_manager)

# ---- Configuration ----
DISCOVERY_QUERIES_TEMPLATE = [
    "{company} {role} interview experience",
    "{company} {role} interview questions",
    "{company} {role} glassdoor reviews / experience",
    "{company} {role} reddit experience",
    "{company} {role} hiring news posts linkedin ",
    "{company} {role} salary",
]

MAX_DISCOVERY_PER_QUERY = 15
MAX_FETCH_CONCURRENCY = 6
MAX_DOCS_TO_FETCH = 30


# -------------------------
# Utility helpers
# -------------------------
def now_ts() -> float:
    return time.time()


def url_domain(url: str) -> str:
    try:
        return urlparse(url).netloc
    except Exception:
        return ""


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def safe_json_load(s: str) -> Any:
    try:
        return json.loads(s)
    except Exception:
        return None


def extract_json_from_text(text: str):
    """Try to extract JSON object from messy LLM output."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            return None
    return None


# -------------------------
# Discovery: DuckDuckGo search (DDGS)
# -------------------------
def discover_urls(company: str, role: str, max_per_query: int = MAX_DISCOVERY_PER_QUERY) -> List[str]:
    queries = [t.format(company=company, role=role) for t in DISCOVERY_QUERIES_TEMPLATE]
    seen = set()
    urls: List[str] = []

    try:
        with DDGS() as ddgs:
            for q in queries:
                print(f"[DEBUG] Searching DDG for query: {q}")
                try:
                    results_iter = ddgs.text(q, max_results=max_per_query)
                except TypeError:
                    results_iter = ddgs.text(q)

                for r in results_iter:
                    if isinstance(r, dict):
                        candidate = r.get("href") or r.get("url") or r.get("link") or r.get("source")
                    else:
                        candidate = r
                    if not candidate:
                        continue
                    if candidate in seen:
                        continue
                    seen.add(candidate)
                    urls.append(candidate)
                    if len(urls) >= MAX_DOCS_TO_FETCH:
                        break
                if len(urls) >= MAX_DOCS_TO_FETCH:
                    break
    except Exception as e:
        print("[DEBUG] DuckDuckGo search failed:", e)
        return urls

    print(f"[DEBUG] Discovered {len(urls)} URLs")
    return urls


# -------------------------
# Fetch & extract
# -------------------------
def fetch_and_extract_blocking(url: str, timeout: int = 15) -> Dict[str, Any]:
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0 (compatible; JobFitBot/1.0)"})
        status = resp.status_code
        if status != 200:
            return {"url": url, "status": status, "error": f"HTTP {status}", "text": None}
        html = resp.text
        extracted = trafilatura.extract(html, include_comments=False, include_tables=False)
        text = extracted or ""

        # Find <title>
        title = ""
        try:
            start = html.lower().find("<title")
            if start != -1:
                start = html.find(">", start) + 1
                end = html.find("</title>", start)
                title = html[start:end].strip() if end != -1 else ""
        except Exception:
            title = ""

        return {"url": url, "status": status, "title": title, "text": text}
    except Exception as e:
        return {"url": url, "status": None, "error": str(e), "text": None}


async def fetch_and_extract(url: str, sem: asyncio.Semaphore) -> Dict[str, Any]:
    async with sem:
        return await asyncio.to_thread(fetch_and_extract_blocking, url)


# -------------------------
# Per-doc summarization
# -------------------------
def summarize_doc_with_llm(doc: Dict[str, Any], company: str, role: str) -> Dict[str, Any]:
    system_prompt = (
        "You are an assistant that extracts concise, factual information from a webpage."
        " Given the document text and its URL, return ONLY valid JSON with keys:"
        " summary (short 1-2 sentences), key_points (list), interview_questions (list),"
        " salary_mentions (list), quotes (list), source (url)."
    )
    user_payload = {
        "company": company,
        "role": role,
        "url": doc.get("url"),
        "title": doc.get("title"),
        "text": (doc.get("text") or "")[:30000]
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(user_payload)}
    ]
    try:
        res = llm_caller.llm_call("gemini-2.5-flash", messages)
        print("[DEBUG] Full LLM response (summarize_doc_with_llm):", res)

        raw = getattr(res.choices[0].message, "content", None) if res else None
        print("[DEBUG] Raw LLM output (summarize_doc_with_llm):", raw)

        parsed = safe_json_load(raw) or extract_json_from_text(raw or "")
        if isinstance(parsed, dict):
            parsed.setdefault("source", doc.get("url"))
            return parsed
        else:
            text = (doc.get("text") or "")
            short = (text.strip().replace("\n", " ")[:280] + "...") if text else ""
            return {"summary": short, "key_points": [], "interview_questions": [], "salary_mentions": [], "quotes": [], "source": doc.get("url")}
    except Exception as e:
        print("[DEBUG] summarize_doc_with_llm failed:", e)
        return {"summary": "", "key_points": [], "interview_questions": [], "salary_mentions": [], "quotes": [], "source": doc.get("url"), "error": str(e)}


# -------------------------
# Aggregate
# -------------------------
def aggregate_with_llm(company: str, role: str, doc_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    system_prompt = (
        "You are a research summarization assistant. Given a list of per-document JSON summaries,"
        " synthesize and return ONLY VALID JSON with keys: company_insights, interview_prep, web_research, sources."
        " Each claim inside company_insights or interview_prep should list sources (URLs). Keep results concise and factual."
    )
    user_payload = {"company": company, "role": role, "doc_summaries": doc_summaries}
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(user_payload)}
    ]
    try:
        res = llm_caller.llm_call("gemini-2.5-flash", messages)
        print("[DEBUG] Full LLM response (aggregate_with_llm):", res)

        raw = getattr(res.choices[0].message, "content", None) if res else None
        print("[DEBUG] Raw LLM output (aggregate_with_llm):", raw)

        parsed = safe_json_load(raw) or extract_json_from_text(raw or "")
        if isinstance(parsed, dict):
            return parsed
    except Exception as e:
        print("[DEBUG] aggregate_with_llm failed:", e)

    return {
        "company_insights": {"hiring_trends": [], "interview_process": [], "employee_experiences": []},
        "interview_prep": {"technical_questions": [], "behavioral_questions": [], "company_specific_questions": [], "prep_tips": []},
        "web_research": {"latest_news": []},
        "sources": []
    }


# -------------------------
# Orchestration
# -------------------------
async def process_agent(file_id: str):
    print(f"[Agent] start for ID {file_id}")
    doc = await files_collection.find_one({"_id": ObjectId(file_id)})
    if not doc:
        print("[Agent] file not found")
        return

    company = doc.get("company_name", "") or ""
    role = doc.get("position", "") or ""
    print(f"[DEBUG] Processing company={company}, role={role}")

    await files_collection.update_one(
        {"_id": ObjectId(file_id)},
        {"$set": {
            "insights_status": "processing",
            "agent_stage": "starting",
            "agent_progress": []
        }}
    )

    try:
        # Stage 1: Discovery
        urls = discover_urls(company, role)
        print(f"[DEBUG] Discovered URLs: {urls[:5]} (showing first 5)")
        
        # Stage 2: Fetch & Extract
        sem = asyncio.Semaphore(MAX_FETCH_CONCURRENCY)
        fetched_results = await asyncio.gather(*[fetch_and_extract(u, sem) for u in urls])
        print(f"[DEBUG] Number of fetched results: {len(fetched_results)}")

        docs: List[Dict[str, Any]] = []
        seen_hashes = set()
        for fr in fetched_results:
            text = fr.get("text") or ""
            if not text:
                continue
            h = hash_text(text[:20000])
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            docs.append({"url": fr.get("url"), "title": fr.get("title") or "", "text": text})
        print(f"[DEBUG] Deduped documents: {len(docs)}")

        # Stage 3: Per-doc summarization
        doc_summaries: List[Dict[str, Any]] = []
        for i, d in enumerate(docs):
            summary = summarize_doc_with_llm(d, company, role)
            doc_summaries.append(summary)
        print("[DEBUG] Sample doc summary:", json.dumps(doc_summaries[:1], indent=2))

        # Stage 4: Aggregate
        aggregated = aggregate_with_llm(company, role, doc_summaries)
        print("[DEBUG] Aggregated result:", json.dumps(aggregated, indent=2))

        # Save final
        await files_collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {
                "insights_status": "processed",
                "agent_stage": "done",
                "company_insights": aggregated.get("company_insights", {}),
                "interview_prep": aggregated.get("interview_prep", {}),
                "web_research": aggregated.get("web_research", {}),
            }}
        )
        print(f"[Agent] finished for ID {file_id}")

    except Exception as e:
        print(f"[Agent] failed for ID {file_id}: {e}")
        await files_collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {"insights_status": "error", "agent_stage": "failed", "agent_error": str(e)}}
        )
