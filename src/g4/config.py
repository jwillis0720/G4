from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "G4"
    DEBUG_MODE: bool = True
    MONGO_HOST = "germlinegenegateway.uvdtl.mongodb.net"
    MONGO_PORT = 27017 
    MONGO_DATABASE_NAME = "g4"
    MONGO_COLLECTION_NAME: str = "G4-dev"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8999


