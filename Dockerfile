FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


COPY . .


RUN pip install --no-cache-dir uv \
    && uv pip install --system --no-cache .

CMD ["python", "src/app/telegram_bot.py"]