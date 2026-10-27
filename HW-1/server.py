from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from openai import OpenAI
import httpx

app = FastAPI(title="Server API")

# הגדרת הרשאות גישה (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY_SAFEAI = "sk-safeai-dfa2d649b8d1b5c974a5f72e97575e3d6b604d5f7ade2ce1"
BASE_URL = "https://safeai613.com/v1"

# יצירת לקוח httpx
httpx_client = httpx.Client(http2=True, verify=False)

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY_SAFEAI,
    http_client=httpx_client
)

# מבנה הודעה יחידה
class Message(BaseModel):
    role: str
    content: str

# מבנה הבקשה מהלקוח - מקבל רשימת הודעות
class RequestModel(BaseModel):
    model: str
    messages: List[Message]

# מבנה התשובה ללקוח
class ResponseModel(BaseModel):
    output_text: str
    model: str

@app.post("/generate", response_model=ResponseModel)
async def generate_content(request: RequestModel):
    try:
        # המרת אובייקטי ה-Pydantic למילונים רגילים עבור OpenAI
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # קריאה ל-API של OpenAI
        response = client.chat.completions.create(
            model=request.model,
            messages=formatted_messages
        )
        
        # חילוץ תוכן התשובה
        output_content = response.choices[0].message.content

        return ResponseModel(
            output_text=output_content,
            model=request.model
        )
    except Exception as e:
        print(f"Error detail: {e}")  # הדפסת השגיאה המדויקת לטרמינל
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("shutdown")
async def shutdown_event():
    httpx_client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)