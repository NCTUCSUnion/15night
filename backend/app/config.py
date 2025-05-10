from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    FRONTEND_URL: str
    FRONTEND_REDIRECT_PATH: str
    
    ALLOW_MOCK_LOGIN: bool
    
    NYCU_CLIENT_ID: str
    NYCU_CLIENT_SECRET: str
    NYCU_REDIRECT_URI: str
    NYCU_AUTHORIZE_URL: str = "https://id.nycu.edu.tw/o/authorize/"
    NYCU_TOKEN_URL: str = "https://id.nycu.edu.tw/o/token/"
    NYCU_PROFILE_URL: str = "https://id.nycu.edu.tw/api/profile/"

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 36000

    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

    class Config:
        env_file = ".env"

settings = Settings()
