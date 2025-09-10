from ..db.collections.files import files_collection
from bson import ObjectId
from pdf2image import convert_from_path
import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv('GOOGLE_API_KEY'),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def process_file(id: str, file_path: str):
    await files_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {
            "status": "processing"
        }
    })

    await files_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {
            "status": "converting to images"
        }
    })

    pages = convert_from_path(file_path)
    images = []

    for i, page in enumerate(pages):
        image_save_path = f"/mnt/uploads/images/{id}/image-{i}.jpg"
        os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
        page.save(image_save_path, 'JPEG')
        images.append(image_save_path)

    await files_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {
            "status": "converting to images success"
        }
    })

    images_base64 = [encode_image(img) for img in images]

    res = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Roast this image of a resume.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url":  f"data:image/jpeg;base64,{images_base64[0]}"
                        },
                    },
                ],
            }
        ],
    )

    # res = client.responses.create(
    #     model="gpt-4o-mini",
    #     input=[
    #         {
    #             "role": "user",
    #             "content": [
    #                 {"type": "input_text", "text": "whats in this image?"},
    #                 {
    #                     "type": "input_image",
    #                     "image_url": f"data:image/jpeg;base64,{images_base64[0]}",
    #                 },
    #             ],
    #         }
    #     ],
    # )
    print(res.choices[0].message.content)
    await files_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {
            "status": "processed",
            "result": res.choices[0].message.content
        }
    })
