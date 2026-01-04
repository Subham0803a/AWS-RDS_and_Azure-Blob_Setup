# from fastapi import FastAPI
# import uvicorn

# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"message": "Hello World"}

# if __name__ == "__main__":
#     # The uvicorn.run command starts the server
#     uvicorn.run("main:app", host="localhost", port=5000, reload=True)

# ------------------------------------------------------------------------

from fastapi import FastAPI
from app.database.connection import engine, Base, test_connection
from app.routers import auth, users, documents
from app.database.azure_blob import azure_storage
import uvicorn

app = FastAPI(title="Skynet LLM API", version="2.0.0")

# database connection on startup
@app.on_event("startup")
def startup_event():
    print("🚀 Starting Skynet application...")
    if test_connection():
        print("📊 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
    else:
        print("⚠️ Warning: Could not connect to database")
    
    try:
        container_name = azure_storage.container_name
        print(f"✅ Azure Blob Storage connected - Container: {container_name}")
    except Exception as e:
        print(f"⚠️ Warning: Could not connect to Azure Blob Storage: {e}")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Skynet LLM API",
        "status": "running",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth",
            "users": "/users",
            "documents": "/documents"
        }
    }


@app.get("/health")
def health_check():
    db_status = "AWS RDS connected" if test_connection() else "AWS RDS disconnected"
    
    try:
        azure_storage.container_client.get_container_properties()
        azure_status = "Azure Blob Storage connected"
    except:
        azure_status = "Azure Blob Storage disconnected"

    return {
        "status": "healthy",
        "database": db_status,
        "azure_storage": azure_status
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=5000, reload=True)