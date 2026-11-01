
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import httpx

load_dotenv()

MODEL = os.getenv("MODEL")
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("OPENAI_API_KEY")


def read_today_tasks():
    """מחזירה את המשימות להיום - כרגע נתונים מדומים."""

    tasks = [
        {
            "id": 1,
            "title": "תיקון באג בהתחברות",
            "description": "משתמשים לא מצליחים להתחבר למערכת",
            "deadline": "היום"
        },
        {
            "id": 2,
            "title": "הוספת שדה חיפוש",
            "description": "הוספת אפשרות חיפוש ברשימת לקוחות",
            "deadline": "מחר"
        },
        {
            "id": 3,
            "title": "עדכון תיעוד API",
            "description": "עדכון מסמכי התיעוד",
            "deadline": "השבוע"
        }
    ]

    return tasks


def ask_user(question: str):
    print("\nשאלה למשתמש:")
    print(question)
    answer = input("התשובה שלך: ")
    return answer


def create_file(content: str, filename: str):
    """יוצרת קובץ טקסט ושומרת בו את התוכן."""

    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)

    return f"הקובץ {filename} נוצר בהצלחה"


TOOLS = [
    {
        "type": "function",
        "name": "read_today_tasks",
        "description": "קריאת המשימות של היום ממערכת TFS",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "ask_user",
        "description": "הצגת שאלה למשתמש וקבלת תשובה",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "השאלה שיש להציג למשתמש"
                }
            },
            "required": ["question"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "create_file",
        "description": "יצירת קובץ טקסט עם תוכן ושם קובץ",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "filename": {"type": "string"}
            },
            "required": ["content", "filename"],
            "additionalProperties": False
        },
        "strict": True
    }
]


TOOLS_REGISTER = {
    "read_today_tasks": read_today_tasks,
    "ask_user": ask_user,
    "create_file": create_file
}


SYSTEM_PROMPT = """
אתה Agent לניהול משימות יומיות מתוך מערכת TFS.

התפקיד שלך:
1. לקרוא את המשימות של היום באמצעות הכלי read_today_tasks.
2. לנתח כל משימה ולהעריך את רמת הדחיפות שלה: גבוהה, בינונית או נמוכה.
3. להעריך כמה זמן יידרש לביצוע כל משימה.
4. להציג למשתמש טבלה מסודרת עם המשימות, רמת הדחיפות וזמן הביצוע המשוער.
5. לשאול את המשתמש האם הוא מעוניין לייצא את הטבלה לקובץ.
6. אם המשתמש מעוניין, לשאול באיזה פורמט הוא מעדיף לשמור את הקובץ.
7. ליצור את הקובץ בהתאם לבחירת המשתמש.

השתמש בכלים שהוגדרו לך כדי לבצע פעולות.
אל תמציא משימות שלא התקבלו ממערכת TFS.
היה ברור, מסודר ותמציתי.
"""


httpx_client = httpx.Client(http2=True, verify=False)

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL or None,
    http_client=httpx_client
)

messages = []


max_turns = 5

while True:

    user_input = input("\nUser >>> ")

    if user_input.strip() == "":
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    for turn in range(max_turns):

        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_PROMPT,
            input=messages,
            tools=TOOLS,
            temperature=0.2
        )

        function_calls = []

        for obj in response.output:

            if obj.type == "message":
                output_text = response.output_text

                if output_text:
                    print("\nASSISTANT >>>", output_text)

            if obj.type == "function_call":
                function_calls.append(obj)
                messages.append(obj)

        if not function_calls:
            break

        for call in function_calls:

            name = call.name
            args = json.loads(call.arguments)

            print("TOOL >>>", name)

            result = TOOLS_REGISTER[name](**args)

            messages.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(result, ensure_ascii=False)
            })


messages.append({
    "role": "user",
    "content": user_input
})


max_turns = 5

while user_input != "" and max_turns > 0:

    max_turns -= 1

    response = client.responses.create(
        model=MODEL,
        instructions=SYSTEM_PROMPT,
        input=messages,
        tools=TOOLS,
        temperature=0.2
    )

    function_calls = []

    for obj in response.output:

        if obj.type == "message":
            output_text = response.output_text

            if output_text:
                print("ASSISTANT >>>", output_text)

        if obj.type == "function_call":
            function_calls.append(obj)
            messages.append(obj)

    if not function_calls:
        break

    for call in function_calls:

        name = call.name
        args = json.loads(call.arguments)

        print("TOOL >>>", name)

        result = TOOLS_REGISTER[name](**args)

        messages.append({
            "type": "function_call_output",
            "call_id": call.call_id,
            "output": json.dumps(result, ensure_ascii=False)
        })
