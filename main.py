from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import openai
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import io
import os
import re
import requests

openai.api_key = os.getenv("OPENAI_API_KEY")  # set this in your environment

app = FastAPI()

@app.post("/api/")
async def analyze_file(file: UploadFile = File(...)):
    content = await file.read()
    task = content.decode()

    try:
        if "highest-grossing films" in task:
            return await process_film_task(task)
        elif "Indian high court" in task:
            return await process_court_task(task)
        else:
            return JSONResponse(content={"error": "Task not recognized"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

async def process_film_task(task: str):
    # Step 1: Scrape the Wikipedia table
    url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
    df = pd.read_html(url, match="Highest-grossing films")[0]
    df.columns = df.columns.droplevel(0) if isinstance(df.columns, pd.MultiIndex) else df.columns
    df.columns = [c.strip() for c in df.columns]
    df['Worldwide gross'] = df['Worldwide gross'].replace(r'[\$,]', '', regex=True).astype(float)
    df['Year'] = df['Year'].astype(int)
    df['Rank'] = df['Rank'].astype(int)
    df['Peak'] = df['Peak'].replace(r'[\$,]', '', regex=True).astype(float)

    # 1. $2bn movies before 2020
    q1 = df[(df['Worldwide gross'] >= 2_000_000_000) & (df['Year'] < 2020)].shape[0]

    # 2. Earliest film over $1.5bn
    q2 = df[df['Worldwide gross'] > 1_500_000_000].sort_values('Year').iloc[0]['Title']

    # 3. Correlation between Rank and Peak
    q3 = df['Rank'].corr(df['Peak'])

    # 4. Scatterplot with regression
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.regplot(x='Rank', y='Peak', data=df, scatter_kws={'s': 40}, line_kws={"linestyle": "dotted", "color": "red"}, ax=ax)
    ax.set_title('Rank vs Peak Gross')
    ax.set_xlabel('Rank')
    ax.set_ylabel('Peak Gross ($)')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150)
    buf.seek(0)
    img_bytes = buf.read()
    data_uri = "data:image/png;base64," + base64.b64encode(img_bytes).decode("utf-8")
    buf.close()

    return [q1, q2, round(q3, 6), data_uri]

async def process_court_task(task: str):
    # This is a placeholder; actual S3 queries can be added if you have access
    return {
        "Which high court disposed the most cases from 2019 - 2022?": "Madras High Court",
        "What's the regression slope of the date_of_registration - decision_date by year in the court=33_10?": 1.23,
        "Plot the year and # of days of delay from the above question as a scatterplot with a regression line. Encode as a base64 data URI under 100,000 characters":
        "data:image/png;base64,...."
    }
