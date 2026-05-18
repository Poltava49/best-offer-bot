"""
Main entry point for the marketplace parser bot.
"""

import logging

from fastapi import FastAPI

from src.db.database import connect_to_db
from src.exceptions import DatabaseConnectionError

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

app = FastAPI()


@app.on_event("startup")
async def startup_event() -> None:
    """Run on application startup."""

    logger.info("Launching marketplace parser bot...")

    try:
        connect_to_db()
        logger.info("Connection to PostgreSQL successful!")

    except DatabaseConnectionError:
        logger.exception("Error connecting to database")


@app.get("/")
async def root():
    return {"status": "ok"}