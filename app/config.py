import os


class Settings:
    # Format: postgresql+psycopg2://<user>:<password>@<host>:<port>/<dbname>
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:dev@localhost:5432/postgres",
    )


settings = Settings()
