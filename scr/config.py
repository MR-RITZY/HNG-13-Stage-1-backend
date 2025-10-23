from pydantic_settings import BaseSettings, SettingsConfigDict




class Settings(BaseSettings):
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME:str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()