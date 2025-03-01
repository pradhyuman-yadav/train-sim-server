from fastapi import Depends, HTTPException  # Import HTTPException
from supabase import create_client, Client
from app.core.config import settings
from typing import List, Optional, Dict
from app.models.passenger import Passenger, PassengerCreate, PassengerUpdate
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

def get_db() -> Client:
    """Dependency function to get the Supabase client."""
    return supabase

async def get_all_passengers(db: Client) -> List[Passenger]:
    """Retrieves all passengers from the database."""
    try:
        data = db.table("passengers").select("*").execute()
        return [Passenger(**item) for item in data.data]  # Access data directly
    except Exception as e:
        logger.exception("Error getting all passengers:")
        raise HTTPException(status_code=500, detail="Failed to retrieve passengers")

async def get_passenger(db: Client, passenger_id: str) -> Optional[Passenger]:
    """Retrieves a passenger by ID."""
    try:
        data = db.table("passengers").select("*").eq("id", passenger_id).execute()
        if not data.data:
            return None
        return Passenger(**data.data[0])
    except Exception as e:
        logger.exception(f"Error getting passenger with ID {passenger_id}:")
        raise HTTPException(status_code=500, detail="Failed to retrieve passenger")
async def create_passenger(db: Client, passenger: PassengerCreate) -> Passenger:
    """Creates a new passenger."""
    try:
        data = db.table("passengers").insert(passenger.dict()).execute()
        return Passenger(**data.data[0])
    except Exception as e:
        logger.exception("Error creating passenger:")
        raise HTTPException(status_code=500, detail="Failed to create passenger")

async def update_passenger(db: Client, passenger_id: str, passenger: PassengerUpdate) -> Optional[Passenger]:
    """Updates an existing passenger."""
    try:
        data = db.table("passengers").update(passenger.dict(exclude_unset=True)).eq("id", passenger_id).execute()
        if not data.data:
            return None
        return Passenger(**data.data[0])
    except Exception as e:
        logger.exception(f"Error updating passenger with ID {passenger_id}:")
        raise HTTPException(status_code=500, detail="Failed to update passenger")

async def delete_passenger(db: Client, passenger_id: str) -> None:
    """Deletes a passenger."""
    try:
        data = db.table("passengers").delete().eq("id", passenger_id).execute()
        if not data.data: #check if data is not None
            logger.warning(f"No passenger found with ID {passenger_id} to delete.")

    except Exception as e:
        logger.exception(f"Error deleting passenger with ID {passenger_id}:")
        raise HTTPException(status_code=500, detail="Failed to delete passenger")

async def insert_passengers_to_db(passengers: List[Dict], db:Client):
    """Inserts a list of passengers into the Supabase database."""
    try:
        data = db.table("passengers").insert(passengers).execute()
        return data
    except Exception as e:
        logger.exception("Error inserting passengers:")
        raise HTTPException(status_code=500, detail="Failed to insert passengers")


async def get_station_ids(db: Client = Depends(get_db)) -> List[str]:
    """Fetches all station IDs from the Supabase database."""
    try:
        data = db.table("stations").select("id").execute()
        return [item['id'] for item in data.data]  # Access data directly
    except Exception as e:
        logger.exception("Error getting station IDs:")
        raise HTTPException(status_code=500, detail="Failed to retrieve station IDs")