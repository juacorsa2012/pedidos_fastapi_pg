from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  DATABASE_URL: str
  API_DESCRIPCION: str
  API_VERSION: str
  PORT: int
  PAGINACION_LIMITE_POR_DEFECTO: int = 100
  PAGINACION_LIMITE_MAXIMO: int = 500
  
  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8"
  )

settings = Settings()