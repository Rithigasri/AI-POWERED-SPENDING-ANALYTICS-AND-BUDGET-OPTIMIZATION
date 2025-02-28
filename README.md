# AI - POWERED SPENDING ANALYTICS AND BUDGET OPTIMIZATION
## OBJECTIVE
To develop an AI-powered financial analytics system that automates expense tracking, transaction classification, and budget optimization using Azure Form Recognizer, GPT-4, and Google Gemini API.

## ABOUT
AI-Powered Spending Analytics and Budget Optimization is an intelligent financial management system designed for automating expense tracking, transaction classification, and budget analysis. It extracts and processes transaction data from bank statements and receipts using Azure Form Recognizer, converting them into structured CSV files. The system leverages GPT-4 for transaction classification and Google Gemini API for AI-driven financial recommendations and queries.

The platform visualizes spending patterns through interactive charts, such as bar graphs and savings reports, allowing users to gain insights into their financial habits. It also supports real-time transaction updates by analyzing receipts and historical spending trends. Built with FastAPI, it integrates Azure SDKs, Pandas, and other Python libraries for efficient data processing and scalability.

By automating financial data extraction and analysis, the system empowers users to optimize their spending, manage budgets effectively, and make informed financial decisions with personalized AI-driven insights.

## FEATURES
### 1. Automated PDF Processing
- Upload bank statements in PDF format.
- Extract transaction data using **Azure Form Recognizer**.
- Convert structured data into CSV for further analysis.

### 2. Receipt-Based Transaction Updates
- Upload receipts for real-time expense tracking.
- Extract and classify receipt data.
- Update the existing financial dataset dynamically.

### 3. AI-Powered Transaction Classification
- Uses **GPT-4** to automatically categorize transactions.
- Enhances accuracy in expense tracking and budgeting.

### 4. Spending & Savings Visualization
- Generates **bar graphs** and **spending breakdowns**.
- Displays categorized spending trends for better insights.

### 5. Personalized Financial Insights & Recommendations
- Analyzes historical spending patterns.
- Provides AI-driven budget optimization suggestions via **Google Gemini API**.

### 6. Interactive Chatbot for Financial Queries
- Users can ask finance-related questions.
- Provides instant AI-generated responses and budgeting tips.

### 7. Efficient Backend Processing
- **FastAPI-based** backend for handling API requests.
- Uses **Pandas** for data processing and analysis.
- Ensures secure and scalable financial data handling.

### 8. Seamless Integration with External Services
- **Azure Form Recognizer** for document processing.
- **GPT-4** for AI-powered classification and chatbot responses.
- **Google Gemini API** for advanced financial recommendations.

### 9. User-Friendly Interface
- Simple dashboard for uploading files and viewing insights.
- Easy-to-understand reports on spending, savings, and budget optimization.

## REQUIREMENTS
* **Hardware Environment:**
  * Processor: Intel Core i5 (or equivalent)
  * Server/Cloud Infrastructure: Microsoft Azure
  * Hard Disk: 256 GB SSD (minimum)
  * RAM: 8 GB (minimum)
  * Graphics Card: NVIDIA GeForce GTX 1050 or higher (recommended for efficient deep learning processing)
  * Keyboard: Standard 104 keys keyboard
  * Mouse: Standard optical mouse

* **Software Environment:**
  * Operating System: Windows 10/11, macOS, or Linux (Ubuntu 20.04 or later)
  * Python Version: Python 3.9 or later
  * Development Environment: VSCode as the Integrated Development Environment for coding, debugging, and version control integration.
  * Libraries and Frameworks:
    * FastAPI: For building REST API endpoints
    * FastAPI Middleware (CORS): Allows cross-origin requests
    * Azure SDKs:
      * azure.ai.formrecognizer – For document and table extraction
      * azure.core.credentials.AzureKeyCredential – For authentication
    * Azure OpenAI: Integrates GPT-4 for transaction classification and recommendations
    * Google Gemini API: For generative language responses and query processing
    * Python Standard Libraries:
      * logging – For debugging and logging
      * csv – For reading and writing CSV files
      * os – For file system operations
      * json – For encoding and decoding JSON data
      * re – For regular expressions and query parsing
      * time – For managing delays and polling operations
      * datetime – For date manipulation and formatting
      * glob – For file pattern matching
    * Requests: For making HTTP requests to Azure OpenAI, Gemini API, and Azure Form Recognizer
    * Pandas: For data manipulation, CSV operations, and analytics
    * Pydantic: For defining and validating data models for API requests
    * Python-Dotenv: For managing environment variables and API keys

* **Frontend Environment:**
  * Framework: React.js (Recommended for UI development)
  * Libraries:
    * axios – For making API requests
    * chart.js – For data visualization
    * react-router-dom – For navigation
    * material-ui – For UI components
  * Development Tools:
    * Node.js (16+ recommended)
    * npm or yarn for package management

* **Technologies Used:**
  * Programming Language: Python 3.9+
  * Backend Framework: FastAPI (for building REST API endpoints)
  * Frontend Framework: React.js (for UI development)
  * Cloud Services:
    * Azure Form Recognizer – For extracting tables and receipt data from PDFs
    * Azure OpenAI (GPT-4) – For transaction classification and financial recommendations
    * Google Gemini API – For chatbot and user query responses
  * Database & File Storage: CSV-based storage for categorized transactions and analysis
  * Data Processing & Analysis:
    * Pandas – For data manipulation and aggregation
    * NumPy – For numerical computations (if required)
  * Visualization Tools:
    * Matplotlib / Seaborn – For spending analysis graphs (backend)
    * Chart.js (React) – For frontend data visualization
  * API Communication:
    * Requests – For making HTTP requests to Azure OpenAI, Gemini API, and Form Recognizer
    * Axios – For frontend API communication
  * Environment & Configuration Management:
    * Python-Dotenv – For managing API keys and environment variables
    * Node.js & npm/yarn – For managing frontend dependencies
  * Security & Middleware:
    * CORS Middleware (FastAPI) – Allows cross-origin requests
    * Authentication via API keys – For secure access to cloud services

## SYSTEM ARCHITECTURE
![WhatsApp Image 2025-02-20 at 1 25 42 PM](https://github.com/user-attachments/assets/9e4c9a18-ffc1-46d7-b69b-7a9d484431f7)

## OUTPUT
#### Output 1 - Upload Monthly Statement
![image](https://github.com/user-attachments/assets/cc3b721c-bed6-4f93-b20b-fceaec685f06)

#### Output 2 - Extracting Receipt Details 
![image](https://github.com/user-attachments/assets/8bc53fb9-e828-4b3f-a6a4-be3915d482a6)

#### Output 3 - Categorize Transactions
![image](https://github.com/user-attachments/assets/adf802b3-e8bc-4a8f-8be7-7d231f8f5eab)

#### Output 4 -  Saving Vs Expenses Chart
![image](https://github.com/user-attachments/assets/35e6d81b-947c-4d9a-a9fc-692dfc3c2168)

#### Output 5 -  Personal Finance Advisor
![image](https://github.com/user-attachments/assets/d9953260-5a20-45ea-a8c6-dcb2e212fa8a)

#### Output 6 -  Insights Provider
![image](https://github.com/user-attachments/assets/ccd3b0ce-7684-49d8-a723-794cb099a478)

## RESULTS 
The AI-Powered Spending Analytics and Budget Optimization system successfully automates financial tracking through AI-driven transaction classification, automated data extraction, and interactive chatbot capabilities. It integrates Azure Form Recognizer, Azure OpenAI (GPT-4), and Google Gemini API to ensure accurate processing of financial data. With modular components for PDF processing, receipt analysis, financial insights, and chatbot interactions, the system provides a scalable and efficient solution for personal finance management.

## IMPACTS
This system enhances financial decision-making by offering personalized insights, spending pattern detection, and AI-driven recommendations. Graphical representations, such as spending breakdowns and savings trends, improve user experience. Future enhancements include predictive financial modeling, real-time bank API integration, advanced receipt scanning, and mobile application support, further expanding its usability for individuals, families, and businesses.

## REFERENCES
[1]  Y. Bai, Y. Gao, R. Wan, S. Zhang, and R. Song, "A review of reinforcement learning in financial applications," arXiv preprint arXiv:2411.12746, Nov. 2024.https://arxiv.org/abs/2411.12746?context=q-fin.CP

[2] S. K. Gorai and A. Maurya, "Artificial intelligence in personal finance management: Opportunities and challenges," IOSR J. Comput. Eng., vol. 27, no. 1, pp. 7–17,2025,https://www.iosrjournals.org/iosr-jce/papers/Vol27-issue1/Ser-1/B2701010717.pdf

[3] N. R. Tadapaneni, "Artificial intelligence in finance and investments," Int. J. Res. Eng. Sci., vol. 9, no. 6, pp. 45–52, 2021.

[4] A. Al Masarweh, K. Y. Aram, and Y. S. Alhaj-Yaseen, "Identifying new earnings management components: A machine learning approach," Int. J. Financ. Res., vol. 12, no. 3, pp. 123–135, 2021.

[5] A. E. Khandani, A. J. Kim, and A. W. Lo, "Consumer credit-risk models via machine-learning algorithms," J. Bank. Finance, vol. 34, no. 11, pp. 2767–2787, Nov. 2010.

[6] Y. Zhao, "Construction of budget management system based on financial risk prevention," Adv. Econ. Bus. Manag. Res., vol. 120, pp. 123–128, 2020.

[7] B. Huang and J. Wei, "Research on deep learning-based financial risk prediction," J. Phys. Conf. Ser., vol. 1237, no. 2, pp. 1–6, 2019.




