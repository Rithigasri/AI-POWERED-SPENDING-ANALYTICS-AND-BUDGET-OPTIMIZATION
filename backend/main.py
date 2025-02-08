import os
import json
import logging
import requests
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import re

# Configure logging
logging.basicConfig(level=logging.INFO)

# FastAPI app setup
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["OPTIONS", "POST", "GET"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# API Key for Gemini
API_KEY = "AIzaSyBii4JbQ36_nXHxy3jT9Q6o8zQEih4JL_E"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# Define Pydantic models
class QueryRequest(BaseModel):
    query: str
    month: str
    year: str

class BarGraphData(BaseModel):
    savings: float
    expenses: float

# Check for file existence function
def check_for_file(month, year):
    filename = f"{month}-{year}.csv"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    logging.info(f"Checking for file at path: {file_path}")
    return file_path if os.path.exists(file_path) else None

# Create prompt for Gemini API
def create_prompt(query, data_context):
    return f"User Query: {query}\nData Context:\n{data_context}\nAssistant Response:"

# Ask Gemini API for response
def ask_gemini(query, file_path):
    df = pd.read_csv(file_path)
    data_context = df.to_string()

    full_prompt = create_prompt(query, data_context)
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": full_prompt}
                ]
            }
        ]
    }
    headers = {"Content-Type": "application/json"}

    logging.info(f"Payload: {json.dumps(payload)}")
    response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload), params={"key": API_KEY})
    logging.info(f"Response status code: {response.status_code}")
    logging.info(f"Response text: {response.text}")

    if response.status_code != 200:
        logging.error(f"Error with Gemini API: {response.status_code} - {response.text}")
        return f"Error with Gemini API: {response.status_code} - {response.text}"
    
    response_data = response.json()
    response_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
    return response_text

# Routes
@app.options("/query")
async def options_query():
    return JSONResponse(content={}, status_code=200)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), month: str = Form(...), year: str = Form(...)):
    """Handles file upload and processing."""
    if not file or not month or not year:
        raise HTTPException(status_code=400, detail="Please select a file and specify month and year.")
    
    file_location = os.path.join(UPLOAD_FOLDER, f"{month}-{year}.csv")
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    return {"filename": file.filename, "message": "File uploaded successfully."}

@app.get("/get_graph_data/")
async def get_graph_data(month: str, year: str):
    """Fetch category-wise spending data."""
    file_name = f"{month}-{year}.csv"
    file_path = os.path.join(UPLOAD_FOLDER, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="No data found for the selected month and year.")

    df = pd.read_csv(file_path)

    df["Withdrawal Amt."] = pd.to_numeric(df["Withdrawal Amt."], errors="coerce").fillna(0)
    df["Amount"] = df["Withdrawal Amt."]

    category_spending = df.groupby("Category")["Amount"].sum().reset_index()

    return category_spending.to_dict(orient="records")

@app.get("/get_bar_graph_data/")
async def get_bar_graph_data(month: str, year: str):
    """Fetch savings vs. expenses data."""
    file_path = check_for_file(month, year)
    if not file_path:
        raise HTTPException(status_code=404, detail="No data found for the selected month and year.")
    
    df = pd.read_csv(file_path)
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%y", errors="coerce")
    df = df.dropna(subset=["Date"])
    
    month_name = df["Date"].dt.strftime("%B").iloc[0]  
    df["Week"] = df["Date"].dt.day // 7 + 1  
    df["Withdrawal Amt."] = df["Withdrawal Amt."].astype(str).str.replace(",", "").astype(float)
    
    monthly_income = 50000  
    num_weeks = df["Week"].nunique()
    weekly_income = monthly_income / num_weeks if num_weeks > 0 else 0  
    
    weekly_spending = df.groupby("Week")["Withdrawal Amt."].sum().reset_index()
    weekly_spending["Savings"] = weekly_income - weekly_spending["Withdrawal Amt."]
    weekly_spending["Savings"] = weekly_spending["Savings"].apply(lambda x: max(x, 0))
    
    weekly_spending_melted = weekly_spending.melt(id_vars=["Week"], value_vars=["Withdrawal Amt.", "Savings"], var_name="Type", value_name="Amount")

    return {
        "month_name": month_name,
        "weekly_spending": weekly_spending_melted.to_dict(orient="records")
    }

@app.post("/query")
async def process_query(request: QueryRequest):
    """Handles user query."""
    file_path = check_for_file(request.month, request.year)
    if not file_path:
        raise HTTPException(status_code=404, detail=f"No data found for {request.month} {request.year}.")
    response = ask_gemini(request.query, file_path)
    return {"response": response}

@app.post("/chat")
async def chat_with_genie(query: str = Form(...)):
    """Handles conversation with Genie."""
    month_year_match = re.search(r"(\w+)\s(\d{4})", query)
    month, year = (month_year_match.group(1).lower(), month_year_match.group(2)) if month_year_match else (None, None)
    
    if not (month and year):
        raise HTTPException(status_code=400, detail="Please specify the month and year in your query.")
        
    file_path = check_for_file(month, year)
    if not file_path:
        return {"response": "No data found for the selected month and year."}
    
    response = ask_gemini(query, file_path)
    return {"response": response}
