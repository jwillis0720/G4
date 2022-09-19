from pydantic import BaseSettings


class CommonSettings(BaseSettings):
    APP_NAME: str = "G4"
    DEBUG_MODE: bool = True


class ServerSettings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8999


class DatabaseSettings(BaseSettings):
    DB_NAME: str = "G3-dev"
    # DB_NAME: str = "G3"


class Settings(CommonSettings, ServerSettings, DatabaseSettings):
    pass


settings = Settings()
