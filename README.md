⚙️ How to Setup

# Create and activate virtual environment

python -m venv venv

.\venv\Scripts\Activate.ps1

# Install required libraries
pip install -r requirements.txt 

# 3. Add .env & Your Keys

DB_HOST=testing-db.cpceoka4oj77.ap-south-1.rds.amazonaws.com

DB_PORT=5432

DB_NAME=llm

DB_USER=postgres

DB_PASSWORD=subham0803

AZURE_STORAGE_CONNECTION_STRING=your_connection_string_here

AZURE_CONTAINER_NAME=documents

# 4. Run the API
Run this command in PowerShell ---> python main.py

