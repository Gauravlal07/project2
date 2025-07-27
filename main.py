from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import requests
import os

app = FastAPI()

# 👇 PUT YOUR AI PIPE TOKEN HERE via environment variable in Render settings
AIPIPE_API_KEY = os.getenv("eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDE2MTlAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.G1z9xdDGSJ9ySQnW-yAPMu9UtKf4erFV12cWYq8jeMQ")

# This is an example function - adjust the endpoint and payload to match AI Pipe's docs
def call_aipipe(prompt_text: str):
    url = "https://aipipe.org/api/generate"  # 🔁 Update if AI Pipe uses a different endpoint

    headers = {
        "Authorization": f"Bearer {AIPIPE_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt_text,
        "model": "gpt-3.5"  # 🔁 Change this to the correct model if needed
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def read_root():
    return {"message": "FastAPI is running with AI Pipe 🎉"}

@app.post("/api/")
async def process_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        prompt = contents.decode("utf-8")
        result = call_aipipe(prompt)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
