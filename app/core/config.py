'''
Module for defining config.

Created on 21-06-2025
@author: Harry New

'''
from pydantic import PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

# - - - - - - - - - - - - - - - - - - -

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
        
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

# - - - - - - - - - - - - - - - - - - -

settings = Settings(
    POSTGRES_DB="investment_tracker"
)

# Settings configured for test setup.
test_settings = Settings(
    POSTGRES_DB="investment_tracker_test"
)

# Settings configured for docker setup.
docker_settings = Settings(
    POSTGRES_SERVER="host.docker.internal",
    POSTGRES_DB="investment_tracker"
)