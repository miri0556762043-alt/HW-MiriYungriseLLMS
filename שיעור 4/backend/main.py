from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
from fastapi import FastAPI, UploadFile, File
import base64
import httpx

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print("OpenAI API Key loaded:", bool(api_key))



client = OpenAI(
    api_key=api_key,
    http_client=httpx.Client(verify=False)
)

app = FastAPI()

def encode_image(image_data):
    return base64.b64encode(image_data).decode("utf-8")

class ChatRequest(BaseModel):
    message: str

    
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    image_data = await file.read()

    base64_image = encode_image(image_data)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Analyze this synthetic sample ID card and extract the visible fields. Return only the information that is clearly visible."
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:{file.content_type};base64,{base64_image}"
                    }
                ]
            }
        ]
    )

    return {
        "filename": file.filename,
        "analysis": response.output_text
    }

@app.get("/")
def home():
    return {"message": "AI Server is running!"}