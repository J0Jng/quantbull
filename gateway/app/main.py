"""
API Gateway - Main Application Entry
"""
from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title="QuantBull API Gateway",
    version="1.0.0",
    description="API Gateway for QuantBull Platform"
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "gateway"}

