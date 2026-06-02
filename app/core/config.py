from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_KEY: str = ""
    PORT: int = 8099
    DB_HOST: str = "localhost"
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_PORT: int = 5432


settings = Settings()
