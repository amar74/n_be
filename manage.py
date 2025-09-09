import os
import subprocess
from typing import Optional
from app.environment import environment
import typer


app = typer.Typer(
    help="Megapolis management commands",
    context_settings={"help_option_names": ["-h", "--help"]},
)


def env_with_db_url(database_url: Optional[str] = None) -> dict[str, str]:
    env = os.environ.copy()
    if database_url:
        env["DATABASE_URL"] = database_url
    return env


@app.command()
def run(host: str = "0.0.0.0", port: int = 8000, reload: bool = True) -> None:
    args = [
        "uvicorn",
        "app.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    if reload:
        args.append("--reload")
    subprocess.run(args, check=True, env=env_with_db_url(environment.DATABASE_URL))


@app.command()
def migrate(message: str) -> None:
    subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", message],
        check=True,
        env=env_with_db_url(environment.DATABASE_URL),
    )


@app.command()
def upgrade(revision: str = "head") -> None:
    subprocess.run(["alembic", "upgrade", revision], check=True, env=env_with_db_url(environment.DATABASE_URL))


@app.command()
def downgrade(revision: str = "-1") -> None:
    subprocess.run(
        ["alembic", "downgrade", revision], check=True, env=env_with_db_url(environment.DATABASE_URL)
    )

@app.command()
def stamp_head() -> None:
    subprocess.run(
        ["alembic", "stamp", "head"], check=True, env=env_with_db_url(environment.DATABASE_URL)
    )


@app.command()
def initdb() -> None:
    subprocess.run(["alembic", "upgrade", "head"], check=True, env=env_with_db_url(environment.DATABASE_URL))


if __name__ == "__main__":
    app()
