import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Form , Query
from fastapi.middleware.cors import CORSMiddleware
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import csv
import os
import json
import requests
import re
import time
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from typing import Dict
import glob


# Load environment variables from a .env file
load_dotenv()

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

# FastAPI app setup
app = FastAPI()

# Allow frontend requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure Form Recognizer Credentials
endpoint = os.getenv("AZURE_ENDPOINT")
api_key = os.getenv("AZURE_API_KEY")
client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

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

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT_NAME = "gpt-4o"
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
HEADERS = {
    "Content-Type": "application/json",
    "api-key": AZURE_API_KEY
}

def extract_keywords(narration):
    """Cleans transaction narration by removing numbers & special characters but keeping meaningful words."""
    logging.debug(f"Extracting keywords from narration: {narration}")
    narration = narration.lower()
    narration = re.sub(r'[^a-zA-Z\s]', '', narration)  # Keep only letters and spaces
    words = narration.split()
    return " ".join(words)  # Return cleaned words

def classify_transaction(narration, max_retries=3, retry_delay=20):
    """Classifies a transaction narration using Azure OpenAI GPT-4 with retries and delay."""
    keywords = extract_keywords(narration)
    prompt = (
        f"Analyze and classify this financial transaction: '{keywords}'.\n"
        "Forcefully categorize it into one of the following categories:\n"
        "- **Groceries** (supermarkets, grocery stores, food-related transactions)\n"
        "- **Shopping** (e-commerce, retail, fashion, online purchases)\n"
        "- **Personal Transfers** (sending/receiving money from individuals)\n"
        "- **EMI & Loans** (monthly installments, chit fund payments, loan repayments)\n"
        "- **Travel & Transport** (metro, fuel, tickets, ride-sharing)\n"
        "- **Bill Payments** (electricity, mobile recharge, Paytm, Google Pay, UPI bills)\n"
        "- **Cash Transactions** (ATM withdrawals, debit/credit card purchases)\n"
        "- **Rewards & Cashback** (Google rewards, refunded money, cashback)\n"
        "If you are unsure, pick the closest category instead of 'Uncategorized'.\n"
        "Return **only** the category name with no ** symbols, nothing else."
        
    )
    payload = {
        "messages": [{"role": "system", "content": "You are a financial transaction classifier."},
                     {"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 50
    }
    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_DEPLOYMENT_NAME}/chat/completions?api-version=2024-02-01"
    for attempt in range(max_retries):
        try:
            logging.debug(f"Sending request to Azure OpenAI with narration: '{narration}'")
            response = requests.post(url, headers=HEADERS, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                category = result["choices"][0]["message"]["content"].strip()
                logging.debug(f"Classified as: {category}")
                return category if category else "Uncategorized"
            elif response.status_code == 429:  # Rate limit exceeded
                logging.warning(f"Rate limit exceeded, retrying after {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2   # Wait for retry_delay before retrying
            else:
                logging.warning(f"Unexpected response status: {response.status_code}")
                return "Uncategorized"
        except requests.exceptions.RequestException as e:
            logging.error(f"API Request Failed: {e}")
            time.sleep(retry_delay)  # Wait before retrying after failure
    return "Uncategorized"
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

@app.get("/")
def read_root():
    return {"message": "PDF Table Extraction API is running"}

@app.options("/query")
async def options_query():
    return JSONResponse(content={}, status_code=200)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), month: str = Form(...), year: str = Form(...)):
    """Handles file upload and processing."""
    if not file or not month or not year:
        raise HTTPException(status_code=400, detail="Please select a file and specify month and year.")
    
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    
    file_size = os.path.getsize(file_location)
    if file_size == 0:
        os.remove(file_location)
        raise HTTPException(status_code=400, detail="Uploaded file is empty!")
    
    logging.debug(f"File uploaded: {file.filename} (Size: {file_size} bytes)")
    
    output_csv = process_pdf(file_location, month, year)
    return {"filename": file.filename, "output_csv": output_csv, "message": "File processed successfully."}

def process_pdf(pdf_path, month, year):
    """Extracts tables from the PDF, classifies transactions, and saves them as CSV."""
    logging.debug(f"Processing PDF: {pdf_path}")
    
    with open(pdf_path, "rb") as file:
        poller = client.begin_analyze_document("prebuilt-layout", document=file)
        result = poller.result()
    
    if not result.tables:
        logging.warning("No tables found in the document!")
        return "No tables found"
    
    logging.debug(f"Tables extracted: {len(result.tables)}")
    
    csv_filename = f"{month}-{year}.csv"
    output_path = os.path.join(UPLOAD_FOLDER, csv_filename)
    
    combined_rows = []
    
    for table in result.tables:
        rows = [["" for _ in range(table.column_count)] for _ in range(table.row_count)]
        
        for cell in table.cells:
            rows[cell.row_index][cell.column_index] = cell.content
        
        # Remove rows where both withdrawal and deposit columns are empty
        filtered_rows = [row for row in rows if len(row) > 6 and (row[5].strip() or row[6].strip())]
        combined_rows.extend(filtered_rows)
    
    # Classify transactions
    classified_rows = []
    for idx, row in enumerate(combined_rows):
        narration = row[1]  # Assuming narration is in the second column
        logging.debug(f"Classifying narration for row {idx}: {narration}")
        category = classify_transaction(narration)  # With delay integrated
        row.append(category)  # Add category as a new column
        classified_rows.append(row)
    
    # Write classified data to CSV
    try:
        with open(output_path, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(classified_rows)
        logging.debug(f"Combined and classified table data saved to: {output_path}")
    except Exception as e:
        logging.error(f"Error writing CSV: {e}")
        return "Error writing CSV"
    
    return output_path

@app.get("/get_graph_data/")
async def get_graph_data(month: str, year: str):
    """Fetch spending breakdown by category for the selected month and year."""
    file_name = f"{month}-{year}.csv"
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="No data found for the selected month and year.")
    
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    # Ensure the columns are numeric and handle errors
    df["Withdrawal Amt."] = pd.to_numeric(df["Withdrawal Amt."], errors="coerce").fillna(0)
    df["Deposit Amt."] = pd.to_numeric(df["Deposit Amt."], errors="coerce").fillna(0)
    df["Amount"] = df["Withdrawal Amt."]
    
    # Group by category and calculate the sum of the spending (Amount)
    category_spending = df.groupby("Category")["Amount"].sum().reset_index()
    
    # Prepare the data for frontend
    graph_data = category_spending.to_dict(orient="records")
    
    # Return the categorized data to the frontend
    return graph_data

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


##NEW ENDPOINTS
# Azure Form Recognizer configuration

FORM_RECOGNIZER_ENDPOINT = os.getenv("AZURE_ENDPOINT")
FORM_RECOGNIZER_API_KEY = os.getenv("AZURE_API_KEY")
FORM_RECOGNIZER_MODEL_URL = FORM_RECOGNIZER_ENDPOINT + "formrecognizer/documentModels/prebuilt-receipt:analyze?api-version=2023-07-31"



# Headers for API Requests
FORM_HEADERS = {"Ocp-Apim-Subscription-Key": FORM_RECOGNIZER_API_KEY, "Content-Type": "application/pdf"}
OPENAI_HEADERS = {"Content-Type": "application/json", "api-key": AZURE_API_KEY}

# Upload folder for receipts
UPLOAD_RECEIPTS_FOLDER = "uploaded_receipts"

# Ensure the upload folder exists
os.makedirs(UPLOAD_RECEIPTS_FOLDER, exist_ok=True)

def clean_and_convert_balance(balance_str):
    """Cleans the balance string and converts it to float."""
    balance_str = balance_str.replace(',', '').strip()  # Remove commas and spaces
    balance_str = balance_str.replace('₹', '').strip()  # Remove the ₹ symbol
    # Check if the balance_str is not empty before attempting conversion
    if balance_str:
        try:
            return float(balance_str)
        except ValueError:
            print(f"⚠️ Error: Invalid value '{balance_str}' for conversion.")
            return 0.0  # Return 0.0 if conversion fails
    else:
        return 0.0  # Return 0.0 if the string is empty

    
# Function to extract receipt data using Azure Form Recognizer
def extract_receipt_data(file_path):
    """Uploads a receipt PDF and extracts date, brand, and total cost using Azure Form Recognizer."""
    with open(file_path, "rb") as f:
        response = requests.post(FORM_RECOGNIZER_MODEL_URL, headers=FORM_HEADERS, data=f)
    
    if response.status_code != 202:
        print(f"⚠️ Error: {response.text}")
        return None

    operation_url = response.headers["Operation-Location"]

    # Polling until processing is complete
    while True:
        result_response = requests.get(operation_url, headers={"Ocp-Apim-Subscription-Key": FORM_RECOGNIZER_API_KEY})
        result_json = result_response.json()
        
        if result_json["status"] == "succeeded":
            break
        elif result_json["status"] == "failed":
            print("⚠️ Error: Document processing failed.")
            return None
        time.sleep(5)

    documents = result_json.get("analyzeResult", {}).get("documents", [])
    if not documents:
        print("⚠️ No valid data extracted.")
        return None

    fields = documents[0].get("fields", {})

    # Debugging: print the fields extracted
    print("Extracted Fields:", fields)

    # Handle missing data gracefully
    return {
        "date": fields.get("TransactionDate", {}).get("content", "N/A"),
        "brand": fields.get("MerchantName", {}).get("content", "Unknown"),  # Handle missing brand
        "total_cost": fields.get("Total", {}).get("content", "Unknown")  # Handle missing total cost
    }

# Function to classify the transaction using Azure OpenAI GPT-4
def classify_transaction_ocr(brand, total_cost):
    """Classifies a transaction using Azure OpenAI GPT-4."""
    narration = f"{brand} {total_cost}"

    prompt = (
        f"Analyze and classify this financial transaction: '{narration}'.\n"
        "Forcefully categorize it into one of the following categories:\n"
        "- **Groceries** (supermarkets, grocery stores, food-related transactions)\n"
        "- **Shopping** (e-commerce, retail, fashion, online purchases)\n"
        "- **Personal Transfers** (sending/receiving money from individuals)\n"
        "- **EMI & Loans** (monthly installments, chit fund payments, loan repayments)\n"
        "- **Travel & Transport** (metro, fuel, tickets, ride-sharing)\n"
        "- **Bill Payments** (electricity, mobile recharge, Paytm, Google Pay, UPI bills)\n"
        "- **Cash Transactions** (ATM withdrawals, debit/credit card purchases)\n"
        "- **Rewards & Cashback** (Google rewards, refunded money, cashback)\n"
        "- **Business** (Trading, Export, Import, Product Purchase)\n"
        "If you are unsure, pick the closest category instead of 'Uncategorized'.\n"
        "Return **only** the category name with no ** symbols, nothing else."
    )

    payload = {
        "messages": [
            {"role": "system", "content": "You are a financial transaction classifier."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 50
    }

    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_DEPLOYMENT_NAME}/chat/completions?api-version=2024-02-01"

    try:
        response = requests.post(url, headers=OPENAI_HEADERS, json=payload)
        if response.status_code == 200:
            result = response.json()
            category_ocr = result["choices"][0]["message"]["content"].strip()
            return category_ocr if category_ocr else "Uncategorized"
        else:
            print(f"⚠️ Unexpected response status: {response.status_code}")
            return "Uncategorized"
    except requests.exceptions.RequestException as e:
        print(f"⚠️ API Request Failed: {e}")
        return "Uncategorized"

# Endpoint for handling receipt PDF uploads and classification
@app.post("/upload_receipt/")
async def upload_receipt(file: UploadFile = File(...), transactionType: str = Form(...)):
    """Handles receipt PDF upload, extracts details, and classifies the transaction."""
    if not file:
        raise HTTPException(status_code=400, detail="Please select a file.")

    # Save the uploaded receipt PDF
    file_location = os.path.join(UPLOAD_RECEIPTS_FOLDER, file.filename)
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    
    # Extract data from receipt using Azure Form Recognizer
    receipt_data = extract_receipt_data(file_location)
    if not receipt_data:
        raise HTTPException(status_code=400, detail="Failed to extract data from receipt.")
    
    # Extracted data from receipt (brand, total cost, and date)
    date = receipt_data.get("date", "N/A")
    brand = receipt_data.get("brand", "N/A")
    total_cost = receipt_data.get("total_cost", "N/A")
    
    if brand == "N/A" or total_cost == "N/A":
        raise HTTPException(status_code=400, detail="Incomplete receipt data.")
    
    # Clean and convert the total_cost to a float
    total_cost_float = clean_and_convert_balance(total_cost)
    
    # Classify the transaction using Azure OpenAI GPT-4
    category_ocr = classify_transaction_ocr(brand, total_cost)
    
    # Get the transaction type (received or paid)
    if transactionType not in ["received", "paid"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type.")
    
    # Determine withdrawal or deposit
    withdrawal_amt = total_cost_float if transactionType == "paid" else 0
    deposit_amt = total_cost_float if transactionType == "received" else 0

    # Update CSV file with the transaction
    update_csv_with_transaction(receipt_data, withdrawal_amt, deposit_amt, category_ocr)
    
    # Return a structured and complete response including the date
    return {
        "date": date,  # Date of transaction
        "brand": brand,  # Brand of the service
        "total_cost": total_cost,  # Total cost of the transaction
        "category": category_ocr,  # Classified category of the transaction
        "transaction_type": transactionType  # Added transaction type to response
    }

def update_csv_with_transaction(transaction_data, withdrawal_amt, deposit_amt, category_ocr):
    """Adds a new transaction to the CSV file and updates closing balance."""
    # Locate the CSV file in 'uploads' folder (month-year.csv format)
    # Convert '20-Jan-25' to '19/01/25' format
    formatted_date = datetime.strptime(transaction_data['date'], "%d-%b-%y").strftime("%d/%m/%y")

    # Extract month-year for CSV filename (January-2025)
    month_year = datetime.strptime(transaction_data['date'], "%d-%b-%y").strftime("%B-%Y").lower()

    csv_file_path = f"uploads/{month_year}.csv"
    
    # Check if the CSV exists, otherwise create it
    if not os.path.exists(csv_file_path):
        print(f"⚠️ No matching CSV found for {month_year}. Creating a new one.")
        df = pd.DataFrame(columns=["Date", "Narration", "Withdrawal Amt.", "Deposit Amt.", "Closing Balance", "Category"])
    else:
        df = pd.read_csv(csv_file_path)
    
    # Get the last closing balance or start from 0
    closing_balance = clean_and_convert_balance(df.iloc[-1]["Closing Balance"]) if not df.empty else 0.0
    new_closing_balance = closing_balance - withdrawal_amt + deposit_amt
    
    # Prepare the new transaction row
    new_transaction = {
        "Date": formatted_date,
        "Narration": transaction_data['brand'],
        "Withdrawal Amt.": withdrawal_amt,
        "Deposit Amt.": deposit_amt,
        "Closing Balance": new_closing_balance,
        "Category": category_ocr  # Use the category from upload_receipt function
    }

    # Append the new transaction row to the DataFrame
    new_transaction_df = pd.DataFrame([new_transaction])
    df = pd.concat([df, new_transaction_df], ignore_index=True)

    # Save the updated CSV file
    df.to_csv(csv_file_path, index=False)
    print("✅ Transaction added successfully!")
   

# Insights Provider
def load_past_statements():
    """Load all CSV files from the uploads folder and combine them into a single DataFrame."""
    csv_files = glob.glob(os.path.join(UPLOAD_FOLDER, "*.csv"))
    dataframes = []
    
    for file in csv_files:
        if os.path.getsize(file) > 0:
            df = pd.read_csv(file, dtype=str)
            df["Withdrawal Amt."] = df["Withdrawal Amt."].str.replace(",", "").astype(float, errors='ignore')
            df["Deposit Amt."] = df["Deposit Amt."].str.replace(",", "").astype(float, errors='ignore')
            dataframes.append(df)
    
    return pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame()

def analyze_spending_saving(data: pd.DataFrame, spending_pct: float, saving_pct: float) -> Dict:
    """Analyze spending trends and provide insights."""
    if data.empty:
        return {"message": "No data available for analysis."}
    
    total_spent = data["Withdrawal Amt."].sum()
    total_saved = data["Deposit Amt."].sum() - total_spent
    expected_spent = (spending_pct / 100) * (total_spent + total_saved)
    expected_saved = (saving_pct / 100) * (total_spent + total_saved)
    
    # Identify max spending areas
    category_spending = data.groupby("Category")["Withdrawal Amt."].sum().sort_values(ascending=False)
    max_spent_category = category_spending.idxmax() if not category_spending.empty else "No spending data"
    
    insights = {
        "total_spent": total_spent,
        "total_saved": total_saved,
        "expected_spent": expected_spent,
        "expected_saved": expected_saved,
        "deviation_spent": total_spent - expected_spent,
        "deviation_saved": total_saved - expected_saved,
        "max_spent_category": max_spent_category,
        "suggestions": []
    }
    
    # Provide suggestions
    if total_spent > expected_spent:
        insights["suggestions"].append(f"Reduce spending in {max_spent_category}.")
    if total_saved < expected_saved:
        insights["suggestions"].append("Increase savings by cutting unnecessary expenses.")
    # Generate AI recommendations using Gemini or Azure service
    prompt = (
        f"Based on the following financial insights:\n"
        f"Total Spent: {total_spent}\n"
        f"Total Saved: {total_saved}\n"
        f"Expected Spent: {expected_spent}\n"
        f"Expected Saved: {expected_saved}\n"
        f"Deviation Spent: {total_spent - expected_spent}\n"
        f"Deviation Saved: {total_saved - expected_saved}\n"
        f"Max Spent Category: {max_spent_category}\n"
        f"Suggestions: {insights['suggestions']}\n"
        f"Provide additional recommendations to improve financial health, in 3 short points and avoid ** symbols while returning back, please. "
    )

    payload = {
        "messages": [
            {"role": "system", "content": "You are a financial advisor."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 150
    }

    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_DEPLOYMENT_NAME}/chat/completions?api-version=2024-02-01"

    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        if response.status_code == 200:
            result = response.json()
            ai_recommendations = result["choices"][0]["message"]["content"].strip()
            insights["ai_recommendations"] = ai_recommendations
        else:
            insights["ai_recommendations"] = "Failed to generate AI recommendations."
    except requests.exceptions.RequestException as e:
        insights["ai_recommendations"] = f"API Request Failed: {e}"
        ai_recommendations = insights.get("ai_recommendations", "No recommendations available")
        logging.info(f"AI Recommendations: {ai_recommendations}")
    return {
        "total_spent": insights["total_spent"],
        "total_saved": insights["total_saved"],
        "expected_spent": insights["expected_spent"],
        "expected_saved": insights["expected_saved"],
        "deviation_spent": insights["deviation_spent"],
        "deviation_saved": insights["deviation_saved"],
        "max_spent_category": insights["max_spent_category"],
        "suggestions": insights["suggestions"],
        "ai_recommendations": insights["ai_recommendations"]
    }

@app.get("/analyze")
def get_savings_analysis(spending_pct: float = Query(..., ge=0, le=100), saving_pct: float = Query(..., ge=0, le=100)):
    """API endpoint to analyze savings based on user-defined percentages."""
    if spending_pct + saving_pct != 100:
        return {"error": "Spending and saving percentages must sum to 100."}
    
    data = load_past_statements()
    insights = analyze_spending_saving(data, spending_pct, saving_pct)
    return insights
