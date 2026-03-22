FROM python:3.12-slim-bookworm

COPY --from=docker.io/astral/uv:0.10 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["uv", "run", "-m", "src.main"]
