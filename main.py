from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from openai import OpenAI
import uvicorn
import base64
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns
import io

app = FastAPI()

# 🔐 Insert your AI Pipe token below
AIPIPE_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDE2MTlAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.G1z9xdDGSJ9ySQnW-yAPMu9UtKf4erFV12cWYq8jeMQ"  # <<--- Drop your token (from aipipe.org/login) here

API_URL = "https://aipipe.org/openrouter/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {AIPIPE_TOKEN}",
    "Content-Type": "application/json"
}

@app.get("/")
def root():
    return {"message": "AI Pipe data‑analyst agent is running"}

@app.post("/api/")
async def analyze(file: UploadFile = File(...)):
    try:
        prompt_text = (await file.read()).decode("utf-8")

        payload = {
            "model": "openai/gpt-4.1-nano",  # model accessible via AI Pipe
            "messages": [
                {"role": "user", "content": prompt_text}
            ]
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(API_URL, headers=HEADERS, json=payload)

        resp.raise_for_status()
        response = resp.json()
        answer = response["choices"][0]["message"]["content"]
        return {"response": answer}

    except httpx.HTTPStatusError as exc:
        return JSONResponse(
            status_code=exc.response.status_code,
            content={"error": exc.response.text}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))


