FROM python:3.12-slim-bookworm

COPY --from=docker.io/astral/uv:0.11 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock requirements.txt ./

RUN uv pip install --system -r requirements.txt

COPY . .

RUN useradd -m appuser && chown -R appuser:appuser /app

USER appuser

CMD ["python", "-m", "src.main"]
