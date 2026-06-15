from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
import json
import os

app = FastAPI(title="Data Integration API", version="1.0")

# API Security: Require an API key for management and access control
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
VALID_API_KEYS = ["secure_token_123", "enterprise_partner_456"]

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key")
    return api_key

# Core Data Access Endpoint
@app.get("/api/v1/data", dependencies=[Depends(verify_api_key)])
def get_integrated_data():
    """
    Exposes the scraped and integrated data to authorized clients.
    """
    file_path = "../webscraping/shared_data.json"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Data not available yet. Scraper must run first.")
        
    with open(file_path, "r") as f:
        data = json.load(f)
        
    return {
        "status": "success",
        "total_records": len(data),
        "data": data
    }

if __name__ == "__main__":
    import uvicorn
    # In production, run this using an ASGI server
    print("Starting API Server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)