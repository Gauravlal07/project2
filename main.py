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

# 🔐 Replace with your actual AI Pipe token
AI_PIPE_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDE2MTlAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.G1z9xdDGSJ9ySQnW-yAPMu9UtKf4erFV12cWYq8jeMQ"

# Initialize OpenAI SDK with AI Pipe endpoint
client = OpenAI(
    base_url="https://aipipe.org/v1/chat/completions",
    api_key=AI_PIPE_API_KEY,
)

@app.get("/")
def read_root():
    return {"message": "AI Pipe API is working!"}

@app.post("/process/")
async def process_file(file: UploadFile = File(...)):
    content = await file.read()
    prompt_text = content.decode("utf-8")

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "user", "content": prompt_text}
            ],
            extra_headers={
                "HTTP-Referer": "https://yourdomain.com",  # Optional
                "X-Title": "Your App Title",               # Optional
            }
        )
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

@app.post("/api/")
async def analyze_file(file: UploadFile = File(...)):
    text = (await file.read()).decode("utf-8")

    # Compose system prompt for data analysis
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
        completion = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            extra_headers={
                "HTTP-Referer": "https://yourdomain.com",  # Optional
                "X-Title": "Your App Title",               # Optional
            }
        )
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
