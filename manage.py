import os
import subprocess
from typing import Optional, List
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


TEST_DB_URL_DEFAULT = "postgresql+psycopg://postgres:postgres@localhost:5444/test_db"


def get_test_db_url() -> str:
    """Return the test database URL, allowing override via TEST_DATABASE_URL."""
    return os.getenv("TEST_DATABASE_URL", TEST_DB_URL_DEFAULT)


@app.command(name="pytest")
def run_pytest(args: List[str] = typer.Argument(None)) -> None:
    """Run pytest against the test database.

    Extra args are passed through to pytest, e.g.:
      poetry run python manage.py pytest -k smoke -q
    """
    extra_args = args or []
    subprocess.run(["pytest", *extra_args], check=True, env=env_with_db_url(get_test_db_url()))


@app.command(name="upgrade-pytest-db")
def upgrade_pytest_db(revision: str = "head") -> None:
    try:
        """Run Alembic upgrade against the test database (default: head)."""
        subprocess.run(["alembic", "upgrade", revision], check=True, env=env_with_db_url(get_test_db_url()))
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error upgrading test database: {e}", err=True)
        raise typer.Exit(1)

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
def migrate(
    message: str = typer.Option(..., "-m", "--message", help="Migration message")
) -> None:
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
