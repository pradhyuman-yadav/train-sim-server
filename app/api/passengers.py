from fastapi import APIRouter, HTTPException, Depends, Body, BackgroundTasks
from typing import List, Dict, Optional
from app.models.passenger import Passenger, PassengerCreate, PassengerUpdate
from app.core.database import get_db, get_all_passengers, get_passenger, create_passenger, update_passenger, delete_passenger, insert_passengers_to_db, get_station_ids
from supabase import Client
import random
import uuid
from faker import Faker
from datetime import datetime, timezone
import logging
import asyncio  # Import asyncio

# Configure logging (keep this as before)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

router = APIRouter()

# --- Passenger Generation Functions (Modified) ---

def generate_passengers(
    station_id: str,
    destination_station_ids: List[str],
    generation_rate: int,
    num_passengers: int = None,

) -> List[Dict]:
    """Generates passenger dictionaries."""
    fake = Faker()
    passengers = []

    if num_passengers is None:
        num_to_generate = int(generation_rate * random.uniform(0.5, 1.5))
    else:
        num_to_generate = num_passengers

    for _ in range(num_to_generate):
        passenger = {
            "id": str(uuid.uuid4()),
            "origin_station_id": station_id,
            "destination_station_id": random.choice(destination_station_ids),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "age": random.randint(5, 90),
            "ticket_type": random.choice(["adult", "child", "senior", "student", "concession"]),
            "luggage_size": random.choice(["none", "small", "medium", "large"]),
            "email": fake.email(),
            "phone_number": fake.phone_number(),
            "spawn_time": datetime.now(timezone.utc).isoformat(),
            "status": "waiting",
            "current_station_id": None,
            "train_id": None,
            "patience": None,
            "board_time": None,
            "arrival_time": None,
        }
        passengers.append(passenger)

    return passengers

async def generate_and_insert_passengers(
        station_id: str,
        destination_station_ids: List[str],
        generation_rate: int,
        db: Client,
        num_passengers: Optional[int] = None
):
    """Generates passengers and inserts them into the database."""
    passengers = generate_passengers(station_id, destination_station_ids, generation_rate, num_passengers)
    if passengers:
        result = await insert_passengers_to_db(passengers, db)
        return result
    return None



async def continuous_passenger_generation(db: Client):
    """Continuously generates passengers in the background."""
    while True:
        try:
            station_ids = await get_station_ids(db)
            if not station_ids:
                logger.warning("No stations found.  Skipping passenger generation.")
                await asyncio.sleep(60)  # Wait longer if no stations
                continue

            for station_id in station_ids:
                # Example:  Vary generation rate based on station importance (if you have that field)
                # You'll need to fetch station data to do this properly.  This is just a placeholder.
                #  station_data = await get_station(db, station_id)  # You'd need a get_station function
                #  generation_rate = station_data.get("importance_level", 1) * 5  # Default rate of 5

                generation_rate = 5 # Put a base generation rate
                destination_station_ids = [sid for sid in station_ids if sid != station_id] #All the stations except for itself.
                if not destination_station_ids:
                    continue  # Skip if only one station
                await generate_and_insert_passengers(station_id, destination_station_ids, generation_rate, db)
                logger.info(f"Generated passengers at station {station_id}")

            await asyncio.sleep(10)  # Generate passengers every 10 seconds (adjust as needed)

        except Exception as e:
            logger.exception("Error in continuous passenger generation:")
            await asyncio.sleep(60)  # Wait longer on error to avoid spamming logs

# --- FastAPI Endpoints (Keep as before, plus the on_event) ---

@router.post("/generate/{station_id}", response_model=List[Passenger])
async def generate_passengers_endpoint(
    station_id: str,
    generation_rate: int = Body(...),
    destination_station_ids: List[str] = Body(...),
    num_passengers: Optional[int] = Body(None),
    db: Client = Depends(get_db)
):
    """Generates and inserts passengers."""
    try:
        # --- VALIDATION ---
        valid_station_ids = await get_station_ids(db)  # Get all valid station IDs
        if station_id not in valid_station_ids:
            raise HTTPException(status_code=400, detail="Invalid origin station ID")
        for dest_id in destination_station_ids:
            if dest_id not in valid_station_ids:
                raise HTTPException(status_code=400, detail=f"Invalid destination station ID: {dest_id}")
        # --- END VALIDATION ---

        result = await generate_and_insert_passengers(station_id, destination_station_ids, generation_rate, db, num_passengers)
        if result:
            return [Passenger(**p) for p in result.data]
        else:
            raise HTTPException(status_code=500, detail="Failed to insert passengers")
    except HTTPException as http_exc:
        logger.error(f"HTTP Exception: {http_exc.detail}")
        raise
    except Exception as e:
        logger.exception("An unexpected error occurred:")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.get("/", response_model=List[Passenger])
async def read_passengers(db: Client = Depends(get_db)):
    """Retrieves all passengers."""
    try:
        passengers = await get_all_passengers(db)
        return passengers
    except Exception as e:
        logger.exception("An unexpected error occurred while getting passenger:")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{passenger_id}", response_model=Passenger)
async def read_passenger(passenger_id: str, db: Client = Depends(get_db)):
    """Retrieves a single passenger by ID."""
    try:
        passenger = await get_passenger(db, passenger_id)
        if not passenger:
            raise HTTPException(status_code=404, detail="Passenger not found")
        return passenger
    except Exception as e:
        logger.exception("An unexpected error occurred while getting passenger by id:")

        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Passenger, status_code=201)
async def create_passenger_endpoint(passenger: PassengerCreate, db: Client = Depends(get_db)):
    """Creates a new passenger."""
    try:
        new_passenger = await create_passenger(db, passenger)
        return new_passenger
    except Exception as e:
        logger.exception("An unexpected error occurred while creating passenger:")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{passenger_id}", response_model=Passenger)
async def update_passenger_endpoint(passenger_id: str, passenger: PassengerUpdate, db: Client = Depends(get_db)):
    """Updates an existing passenger."""
    try:
        updated_passenger = await update_passenger(db, passenger_id, passenger)
        if not updated_passenger:
            raise HTTPException(status_code=404, detail="Passenger not found")
        return updated_passenger
    except Exception as e:
        logger.exception("An unexpected error occurred while updating passenger:")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{passenger_id}", status_code=204)
async def delete_passenger_endpoint(passenger_id: str, db: Client = Depends(get_db)):
    """Deletes a passenger."""
    try:
        await delete_passenger(db, passenger_id)
        return  # 204 No Content
    except Exception as e:
        logger.exception("An unexpected error occurred while deleting passenger:")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stations/ids", response_model=List[str])
async def get_all_station_ids(db: Client = Depends(get_db)):
    """Retrieves all station IDs (utility endpoint)."""
    try:
        return await get_station_ids(db)  # Call the function from database.py
    except Exception as e:
        logger.exception("An unexpected error occurred while getting station ids")
        raise HTTPException(status_code=500, detail=str(e))