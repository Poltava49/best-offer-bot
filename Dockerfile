FROM python:3.12-slim-bookworm

COPY --from=docker.io/astral/uv:0.11 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock requirements.txt ./

RUN uv pip install --system -r requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN useradd -m appuser && chown -R appuser:appuser /app

USER appuser

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
