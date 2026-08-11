from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    database_url:str="sqlite+aiosqlite:///./nexo.db"
    secret_key:str="change-me"
    jwt_secret:str="change-me"
    cors_origins:str="http://localhost:5173"
    login_username:str="Nexo"
    login_password:str="admin"
    request_timeout:float=8.0
    max_concurrency:int=4
    max_requests_per_scan:int=80
    version:str="3.0.0"
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
settings=Settings()
