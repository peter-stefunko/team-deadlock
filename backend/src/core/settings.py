from pydantic_settings import BaseSettings
from yarl import URL


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000

    workers_count: int = 3
    reload: bool = True

    domain: str

    newsmatics_api_base: str
    newsmatics_api_token: str

    openai_token: str

    @property
    def url(self) -> str:
        return f"http://{self.domain}"

    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_base: str
    db_echo: bool

    @property
    def async_db_url(self) -> URL:
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_password,
            path=f"/{self.db_base}",
        )

    @property
    def db_url(
        self,
    ) -> URL:
        url = URL.build(
            scheme="postgresql+psycopg2",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_password,
            path=f"/{self.db_base}",
        )
        return url

    class Config:
        env_prefix = "DEADLOCK_"


settings = Settings()
