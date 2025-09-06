FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*
RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root --no-interaction --no-ansi

COPY . .

EXPOSE 80

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 80"]


