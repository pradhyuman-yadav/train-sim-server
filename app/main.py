from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import passengers  # Import the passengers router
from app.core.config import settings
from app.core.database import get_db
from supabase import Client
import asyncio

app = FastAPI(
    title="Train Simulation API",
    description="An API for managing a train simulation using FastAPI and Supabase.",
    version="0.1.0",
)

# CORS (Cross-Origin Resource Sharing)
origins = [
    "*"
    # Add other origins as necessary
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(passengers.router, prefix="/passengers", tags=["passengers"])

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Train Simulation API!"}