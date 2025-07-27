# main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import duckdb
import io
import base64
import os

from openai import OpenAI

# FastAPI App
app = FastAPI()

# 🔐 Replace with your real OpenRouter API key
OPENROUTER_API_KEY = "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"

# Setup OpenAI SDK for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

async def ask_ai_pipe(prompt: str) -> str:
    response = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://your-project-name.onrender.com",  # Optional
            "X-Title": "Data Analyst Agent",  # Optional
        },
        model="openai/gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

@app.get("/")
def read_root():
    return {"message": "AI Pipe (OpenRouter) API is working!"}

@app.post("/process/")
async def process_file(file: UploadFile = File(...)):
    content = await file.read()
    prompt_text = content.decode("utf-8")

    try:
        result = await ask_ai_pipe(prompt_text)
        return {"response": result}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/")
async def analyze_file(file: UploadFile = File(...)):
    text = (await file.read()).decode("utf-8")

    # Step 1: Ask LLM to plan the task
    prompt = f"""You are a data analyst. The user has provided this task:
{text}
Break it into steps. Then write Python code to solve it. Include DuckDB or pandas where necessary.
Do not print anything. Return a JSON array like:
[
  answer_1,
  answer_2,
  correlation_value (float),
  "data:image/png;base64,..."
]
If you generate a chart, return it as base64 URI string under 100kB.
"""

    try:
        answer = await ask_ai_pipe(prompt)
        return answer
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
