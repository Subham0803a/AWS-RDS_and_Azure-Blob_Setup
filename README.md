🚀 LLM Document Management API
A FastAPI-based backend for managing users and their document uploads. This project integrates AWS RDS (PostgreSQL) for structured data metadata and Azure Blob Storage for cloud file hosting.

🛠️ Tech Stack
Framework: FastAPI

Database: AWS RDS (PostgreSQL)

Storage: Azure Blob Storage

ORM: SQLAlchemy

Validation: Pydantic

📋 Prerequisites
Python 3.8+

An active AWS Account (for RDS)

An active Azure Account (for Blob Storage)

⚙️ Local Setup
1. Clone the Repository
Bash

git clone <your-repo-url>
cd AWS-RDS_and_Azure-Blob-storage_setup
2. Configure Environment Variables
Create a .env file in the root directory and paste your credentials:

Ini, TOML

# AWS RDS Configuration
DB_HOST=testing-db.cpceoka4oj77.ap-south-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=llm
DB_USER=postgres
DB_PASSWORD=your_password

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING="your_connection_string"
AZURE_CONTAINER_NAME=documents
3. Setup Virtual Environment
Bash

# Create venv
python -m venv venv

# Activate venv (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
4. Run the Application
Bash

python main.py
The server will start at http://localhost:5000. You can verify the health of the connections at http://localhost:5000/health.

🧪 Testing with Postman
1. Create a User
Method: POST

URL: http://localhost:5000/users

Body (JSON):

JSON

{
  "username": "subham_dev",
  "email": "subham@example.com",
  "full_name": "Subham Pratap"
}
Note: Save the returned id.

2. Upload a Document (Linked to User)
Method: POST

URL: http://localhost:5000/documents/upload

Body Type: form-data

Keys:

file: (Select a PDF or Image file)

user_id: 1 (The ID of the user created in step 1)

3. List User Documents (The Relationship)
Method: GET

URL: http://localhost:5000/documents/user/1/list

Result: This returns all documents belonging specifically to User ID 1.

📂 Project Structure
Plaintext

.
├── app/
│   ├── database/       # DB Connection & Azure Config
│   ├── models/         # SQLAlchemy Models (User/Document Relationship)
│   ├── routers/        # API Endpoints
│   └── schemas/        # Pydantic Models
├── main.py             # Entry point & Startup logic
├── .env                # Private Credentials (IGNORED)
├── .gitignore          # Git exclusion rules
└── requirements.txt    # Project dependencies
