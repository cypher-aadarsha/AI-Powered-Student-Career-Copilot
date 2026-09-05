FROM python:3.12-slim

WORKDIR /app

# System deps for psycopg2 (build) — kept minimal, removed from the final layer's apt cache.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# --reload matches docker-compose.yml's bind-mounted ./backend, which is a
# local-dev convenience. A production compose file would drop both, and
# would run migrations as a separate release step rather than on every boot.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
