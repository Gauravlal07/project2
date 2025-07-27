# main.py

from fastapi import FastAPI, UploadFile, File
import uvicorn
import aiohttp
import os
import base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import duckdb
import io

app = FastAPI()

# 🔐 Place your AI Pipe token here
AI_PIPE_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDE2MTlAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.G1z9xdDGSJ9ySQnW-yAPMu9UtKf4erFV12cWYq8jeMQ"  # <<--- Replace this

@app.post("/process/")
async def process_file(file: UploadFile = File(...)):
    content = await file.read()
    prompt_text = content.decode("utf-8")

    headers = {
        "Authorization": f"Bearer {AI_PIPE_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",  # Or whatever model your AI Pipe account supports
        "messages": [{"role": "user", "content": prompt_text}]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data) as resp:
            if resp.status == 200:
                result = await resp.json()
                return {"response": result['choices'][0]['message']['content']}
            else:
                return JSONResponse(
                    content={"error": "Failed to get a response from AI Pipe."},
                    status_code=resp.status
                )

async def ask_ai_pipe(prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"  # Replace if different
    headers = {
        "Authorization": f"Bearer {AI_PIPE_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "gpt-4",  # or whatever model you're allowed to use
        "messages": [{"role": "user", "content": prompt}]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as resp:
            res = await resp.json()
            return res['choices'][0]['message']['content']
@app.get("/")
def read_root():
    return {"message": "AI Pipe API is working!"}

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

    answer = await ask_ai_pipe(prompt)
    return answer

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
