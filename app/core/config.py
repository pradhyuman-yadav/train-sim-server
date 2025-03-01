from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()  # Explicitly load the .env file


class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str

    model_config = SettingsConfigDict(env_prefix="TRAINSIM_") # Keep the prefix

settings = Settings()