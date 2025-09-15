from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
from bson import ObjectId
import json, asyncio
from .utils.file import save_to_disk
from .db.collections.files import files_collection, FileSchema
from .queue.worker_node import process_file, process_text
from .queue.q import q


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload(
    file: UploadFile = None,
    resume_text: str = Form(""),
    company_name: str = Form(...),
    job_description: str = Form(...),
    position: str = Form("")
):
    print(f"[Upload] Received upload. file: {bool(file)}, text length: {len(resume_text)}, company: {company_name}, position: {position}")
    db_obj = FileSchema(
        name=(file.filename if file else "text-input"),
        status="saving",
        company_name=company_name,
        job_description=job_description,
        position=position
    )
    result = await files_collection.insert_one(db_obj)
    file_id = str(result.inserted_id)

    if file:
        print(f"[Upload] Enqueue process_file for ID {file_id}")
        path = f"/mnt/uploads/{file_id}/{file.filename}"
        await save_to_disk(await file.read(), path)
        q.enqueue(process_file, file_id, path)
        await files_collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {"status": "queued"}}
        )
    else:
        print(f"[Upload] Enqueue process_text for ID {file_id}")
        await files_collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {"status": "processing"}}
        )
        q.enqueue(process_text, file_id, resume_text)

    print(f"[Upload] Returning file_id {file_id}")
    return {"file_id": file_id}

@app.post("/cancel/{file_id}")
async def cancel_processing(file_id: str):
    await files_collection.update_one(
        {"_id": ObjectId(file_id)}, {"$set": {"status": "cancelled"}}
    )
    return {"message": "Processing cancelled"}

@app.get("/stream/{file_id}")
async def stream_file_status(file_id: str):
    async def event_generator() -> AsyncGenerator[str, None]:
        while True:
            db_file = await files_collection.find_one({"_id": ObjectId(file_id)})
            if not db_file:
                yield f"data: {json.dumps({'error':'File not found'})}\n\n"
                break

            data = {
                "_id": str(db_file["_id"]),
                "status": db_file["status"],
                "result": db_file.get("result"),
                "score": db_file.get("score", 0)
            }
            yield f"data: {json.dumps(data)}\n\n"

            if db_file["status"] in ["processed", "error", "failed"]:
                await asyncio.sleep(1)
                updated = await files_collection.find_one({"_id": db_file["_id"]})
                final = {
                    "_id": str(updated["_id"]),
                    "status": updated["status"],
                    "result": updated["result"],
                    "score": updated["score"]
                }
                yield f"data: {json.dumps(final)}\n\n"
                break

            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )
