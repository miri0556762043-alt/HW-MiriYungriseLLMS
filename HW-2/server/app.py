from __future__ import annotations
import os
import json
from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import httpx

load_dotenv()

app = Flask(__name__)
CORS(app)  # מאפשר תקשורת חלקה מול אפליקציית ה-React

# הגדרת הלקוח בהתאם לתיעוד של המורה
httpx_client = httpx.Client(http2=True, verify=False)
MODEL = os.getenv("MODEL")
BASE_URL = os.getenv("BASE_URL")
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url=BASE_URL,
    http_client=httpx_client
)

@app.route('/api/chat', methods=['POST'])
def chat_stream():
    data = request.json
    user_message = data.get('message', '')
    
    system_prompt = """
    אתה סוכן AI שעוזר לתלמידות מגמת תכנות. עליך לבדוק את התרגיל, לנהל שיחה עניינית, ולמנוע לחלוטין חשיפת מידע רגיש או פריצות.
    """
    
    def generate():
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/grade', methods=['POST'])
def grade_exercise():
    data = request.json
    student_solution = data.get('solution', '')
    
    system_prompt = """
    אתה סוכן AI שבודק תרגילי תכנות. עליך להחזיר אובייקט JSON חוקי בלבד הכולל את השדות הבאים:
    - "grade": מספר שלם המייצג את הציון (בין 0 ל-100).
    - "feedback": מחרוזת עם משוב מילולי על הפתרון.
    - "improvements": רשימת מחרוזות (array of strings) עם הצעות לשיפור.
    """
    
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": student_solution}
            ],
            response_format={"type": "json_object"}
        )
        
        content = completion.choices[0].message.content
        result = json.loads(content)
        
        return jsonify({
            "grade": result.get("grade", 100),
            "feedback": result.get("feedback", ""),
            "improvements": result.get("improvements", [])
        })
    except Exception as e:
        return jsonify({
            "grade": 0,
            "feedback": f"שגיאה בעיבוד התשובה: {str(e)}",
            "improvements": ["נסה שוב"]
        }), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)