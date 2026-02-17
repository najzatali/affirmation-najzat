from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "local"
    app_name: str = "Affirmation Studio"
    app_url: str = "http://localhost:3000"
    api_url: str = "http://localhost:8000"
    secret_key: str = "dev-secret"
    access_token_expire_min: int = 60

    database_url: str
    redis_url: str

    s3_endpoint: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket: str
    s3_region: str = "us-east-1"
    s3_public_url: str

    llm_provider: str = "deepseek"
    tts_provider: str = "edge"
    voice_provider: str = "mock"

    gigachat_auth_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    gigachat_api_base: str = "https://gigachat.devices.sberbank.ru/api/v1"
    gigachat_client_id: str = ""
    gigachat_client_secret: str = ""
    gigachat_scope: str = "GIGACHAT_API_PERS"
    gigachat_model: str = "GigaChat"
    gigachat_verify_ssl: bool = True

    deepseek_api_base: str = "https://api.deepseek.com"
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"

    ollama_api_base: str = "http://host.docker.internal:11434"
    ollama_model: str = "qwen2.5:7b-instruct"

    openai_api_base: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    max_text_chars_free: int = 1500
    max_text_chars_pro: int = 9000
    max_generations_free: int = 3
    max_generations_pro: int = 100

    voice_retention_days: int = 14
    require_consent: bool = True

    cors_origins: str = "http://localhost:3000,http://localhost:4000"

    billing_provider: str = "local"
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_pro: str = ""
    stripe_price_team: str = ""
    robokassa_login: str = ""
    robokassa_password_1: str = ""
    robokassa_password_2: str = ""
    robokassa_test_mode: bool = True
    robokassa_checkout_url: str = "https://auth.robokassa.ru/Merchant/Index.aspx"

    ffmpeg_path: str = "ffmpeg"
    espeak_path: str = "espeak-ng"

    @property
    def cors_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
