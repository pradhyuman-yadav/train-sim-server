from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api import passengers
from app.core.config import settings
from app.core.database import get_db  # Import get_db
from supabase import Client
import asyncio

app = FastAPI(
    title="Train Simulation API",
    description="An API for managing a train simulation using FastAPI and Supabase.",
    version="0.1.0",
)

# CORS (Cross-Origin Resource Sharing)
origins = [
    "http://localhost:3000",  # Your Next.js frontend
    "http://localhost",
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


@app.on_event("startup")
async def startup_event():
    """Starts the background passenger generation on application startup."""
    db: Client = get_db()  # Get the database client (important: do this *within* the event handler)
    asyncio.create_task(passengers.continuous_passenger_generation(db))


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Train Simulation API!"}