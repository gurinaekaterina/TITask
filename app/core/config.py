from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    jwt_secret: str
    access_token_expire_minutes: int
    algorithm: str

    sqlalchemy_database_url: str
    alembic_db_url: str | None = None

    target_word: str
    company_name_col: str
    default_txt_chunk: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
