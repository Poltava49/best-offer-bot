FROM selenium/standalone-chromium:latest

USER root

WORKDIR /app


COPY pyproject.toml requirements.txt* ./

RUN apt-get update && apt-get install -y \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir uv \
    && uv pip install --system --no-cache . \
    && pip install webdriver-manager \
    telegram


COPY . .
USER seluser

CMD ["python", "-m", "src.main"]