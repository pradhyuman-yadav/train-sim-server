from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Define enums to match Supabase types
class PassengerStatus(str, Enum):
    waiting = "waiting"
    boarding = "boarding"
    in_transit = "in_transit"
    arrived = "arrived"
    exited = "exited"

class TicketType(str, Enum):
    adult = "adult"
    child = "child"
    senior = "senior"
    student = "student"
    concession = "concession"

class LuggageSize(str, Enum):
    none = "none"
    small = "small"
    medium = "medium"
    large = "large"

class PassengerBase(BaseModel):
    origin_station_id: str
    destination_station_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    ticket_type: Optional[TicketType] = None
    luggage_size: Optional[LuggageSize] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    patience: Optional[int] = None  # Make patience optional
    status: PassengerStatus = PassengerStatus.waiting # Set default status

    @validator('email', pre=True, always=True)
    def validate_email(cls, v):
        if v == "":  # Allow for empty strings to become None
            return None
        return v

    @validator('phone_number', pre=True, always=True)
    def validate_phone(cls,v):
        if v == "":
            return None
        return v

class PassengerCreate(PassengerBase):
    pass

class PassengerUpdate(PassengerBase):
    # Make all fields optional for updates
    origin_station_id: Optional[str] = None
    destination_station_id: Optional[str] = None
    current_station_id: Optional[str] = None
    train_id: Optional[str] = None
    status: Optional[PassengerStatus] = None
    board_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    ticket_type: Optional[TicketType] = None
    luggage_size: Optional[LuggageSize] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
     # Optional: Validate email format if provided


class Passenger(PassengerBase):
    id: str
    spawn_time: datetime
    current_station_id: Optional[str] = None
    train_id: Optional[str] = None
    board_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    class Config:
        from_attributes = True