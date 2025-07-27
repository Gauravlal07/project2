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

# 🔐 Your API key from AI Pipe
AIPIPE_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDE2MTlAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.G1z9xdDGSJ9ySQnW-yAPMu9UtKf4erFV12cWYq8jeMQ"  # Replace with your actual key

AIPIPE_ENDPOINT = "https://aipipe.org/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {AIPIPE_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:10000",  # Optional for attribution
    "X-Title": "AI Pipe Data Agent"  # Optional
}

@app.get("/")
def read_root():
    return {"message": "AI Pipe custom backend running!"}

@app.post("/process/")
async def process_file(file: UploadFile = File(...)):
    try:
        prompt_text = (await file.read()).decode("utf-8")

        payload = {
            "model": "openai/gpt-4o",  # or any model supported by AI Pipe
            "messages": [{"role": "user", "content": prompt_text}]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(AIPIPE_ENDPOINT, json=payload, headers=HEADERS)

        response.raise_for_status()
        data = response.json()
        return {"response": data["choices"][0]["message"]["content"]}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/")
async def analyze_file(file: UploadFile = File(...)):
    try:
        text = (await file.read()).decode("utf-8")

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

        payload = {
            "model": "openai/gpt-4o",
            "messages": [{"role": "user", "content": prompt}]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(AIPIPE_ENDPOINT, json=payload, headers=HEADERS)

        response.raise_for_status()
        data = response.json()
        return {"response": data["choices"][0]["message"]["content"]}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)

