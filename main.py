from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from openai import OpenAI
import uvicorn
import base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io



# Load .env variables (AIPIPE_TOKEN should be set there)
load_dotenv()

AIPIPE_TOKEN = os.getenv("eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDE2MTlAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.G1z9xdDGSJ9ySQnW-yAPMu9UtKf4erFV12cWYq8jeMQ")
AI_ENDPOINT = "https://aipipe.org/openrouter/v1/chat/completions"
AI_MODEL = "openai/gpt-4.1-nano"  # or other supported model

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "API is live. Use POST /process/ to get answers."}


@app.post("/process/")
async def process(file: UploadFile):
    try:
        content = await file.read()
        question = content.decode("utf-8").strip()

        if not question:
            return JSONResponse(status_code=400, content={"error": "Empty question"})

        headers = {
            "Authorization": f"Bearer {AIPIPE_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": AI_MODEL,
            "messages": [{"role": "user", "content": question}]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(AI_ENDPOINT, json=payload, headers=headers)

        if response.status_code != 200:
            return JSONResponse(status_code=500, content={
                "error": f"Failed to get response from AI Pipe",
                "details": response.text
            })

        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        return {"question": question, "answer": answer}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})



