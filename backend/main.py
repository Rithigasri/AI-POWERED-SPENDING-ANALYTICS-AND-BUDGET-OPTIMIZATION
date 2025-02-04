from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import csv
import os
import requests
import re
import time
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

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
    print(f"🔍 Extracting keywords from narration: {narration}")
    narration = narration.lower()
    narration = re.sub(r'[^a-zA-Z\s]', '', narration)  # Keep only letters and spaces
    words = narration.split()
    return " ".join(words)  # Return cleaned words

# Function to classify transactions using Azure OpenAI GPT-4 with a delay
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
        "Return **only** the category name, nothing else."
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
            print(f"🔄 Sending request to Azure OpenAI with narration: '{narration}'")
            response = requests.post(url, headers=HEADERS, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                category = result["choices"][0]["message"]["content"].strip()
                print(f"✅ Classified as: {category}")
                return category if category else "Uncategorized"
            elif response.status_code == 429:  # Rate limit exceeded
                print(f"⚠️ Rate limit exceeded, retrying after {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2   # Wait for retry_delay before retrying
            else:
                print(f"⚠️ Unexpected response status: {response.status_code}")
                return "Uncategorized"
        except requests.exceptions.RequestException as e:
            print(f"⚠️ API Request Failed: {e}")
            time.sleep(retry_delay)  # Wait before retrying after failure

    return "Uncategorized"

@app.get("/")
def read_root():
    return {"message": "PDF Table Extraction API is running"}

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
    
    print(f"✅ File uploaded: {file.filename} (Size: {file_size} bytes)")
    
    output_csv = process_pdf(file_location, month, year)
    return {"filename": file.filename, "output_csv": output_csv, "message": "File processed successfully."}

def process_pdf(pdf_path, month, year):
    """Extracts tables from the PDF, classifies transactions, and saves them as CSV."""
    print(f"🔍 Processing PDF: {pdf_path}")
    
    with open(pdf_path, "rb") as file:
        poller = client.begin_analyze_document("prebuilt-layout", document=file)
        result = poller.result()
    
    if not result.tables:
        print("⚠️ No tables found in the document!")
        return "No tables found"
    
    print(f"✅ Tables extracted: {len(result.tables)}")
    
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
    for row in combined_rows:
        narration = row[1]  # Assuming narration is in the second column
        print(f"🔍 Classifying narration: {narration}")
        category = classify_transaction(narration)  # With delay integrated
        row.append(category)  # Add category as a new column
        classified_rows.append(row)
    
    # Write classified data to CSV
    with open(output_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(classified_rows)
    
    print(f"✅ Combined and classified table data saved to: {output_path}")
    return output_path

@app.get("/get_graph_data/")
async def get_graph_data(month: str, year: str):
    """Fetch spending breakdown by category for the selected month and year."""
    file_name = f"{month}-{year}.csv"
    file_path = os.path.join(UPLOAD_FOLDER, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="No data found for the selected month and year.")
    import pandas as pd
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