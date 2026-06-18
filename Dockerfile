FROM python:3.12-slim-bookworm

COPY --from=docker.io/astral/uv:0.11 /uv /uvx /bin/

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        chromium \
        chromium-driver \
        libglib2.0-0 \
        libnss3 \
        libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

ENV CHROMIUM_PATH=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

COPY pyproject.toml uv.lock ./

RUN uv export --no-dev --frozen > requirements.txt

RUN uv pip install --system -r requirements.txt

COPY . .

RUN useradd -m appuser && chown -R appuser:appuser /app

USER appuser

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
