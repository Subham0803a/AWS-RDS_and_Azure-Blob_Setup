## ⚙️ How to Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <your-project-folder>
```

### 2. Create and Activate Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.\venv\Scripts\activate.bat

# Activate (Linux/Mac)
source venv/bin/activate
```

### 3. Install Required Libraries
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

Edit `.env` with your actual values:
```dotenv
# AWS RDS Configuration
DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_db_username
DB_PASSWORD=your_db_password

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your_account_name;AccountKey=your_account_key;EndpointSuffix=core.windows.net
AZURE_CONTAINER_NAME=documents

# SMTP (Brevo) Email Settings
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=your_smtp_user@smtp-brevo.com
SMTP_PASSWORD=your_smtp_password
SMTP_FROM_EMAIL=your_email@example.com
SMTP_FROM_NAME=Your_App_Name

# JWT Configuration
SECRET_KEY=generate_a_strong_random_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OTP Configuration
OTP_EXPIRY_MINUTES=10
```

> **Note:** Generate a secure SECRET_KEY using:
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

### 5. Run the API
```bash
python main.py
```

The API will be available at: `http://localhost:5000`

### 6. Access API Documentation
Once the server is running, visit:
- **Swagger UI:** `http://localhost:5000/docs`
- **ReDoc:** `http://localhost:5000/redoc`

---

## 🔐 Security Notes
- **Never commit `.env` file to git**
- Add `.env` to your `.gitignore`
- Use strong, unique passwords for production
- Rotate your SECRET_KEY regularly in production