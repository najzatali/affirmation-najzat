from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "local"
    redis_url: str
    database_url: str

    s3_endpoint: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket: str
    s3_region: str = "us-east-1"
    s3_public_url: str

    ffmpeg_path: str = "ffmpeg"
    espeak_path: str = "espeak-ng"
    tts_provider: str = "edge"

    yandex_api_key: str = ""
    yandex_tts_url: str = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
    yandex_voice: str = "filipp"
    yandex_lang: str = "ru-RU"
    yandex_format: str = "mp3"

    salute_api_key: str = ""
    salute_tts_url: str = "https://smartspeech.sber.ru/rest/v1/text:synthesize"
    salute_voice: str = "Nec_24000"
    salute_lang: str = "ru-RU"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
