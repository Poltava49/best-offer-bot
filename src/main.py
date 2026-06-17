"""Main entry point for the marketplace parser bot."""

import logging
from typing import Annotated

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.app import find_best_offer
from src.app.models import MarketPlace
from src.db.database import connect_to_db
from src.exceptions import DatabaseConnectionError

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

app = FastAPI()

templates = Jinja2Templates(directory="src/templates")


def _parse_marketplace(value: str) -> MarketPlace:
    """Convert form value to marketplace enum."""
    aliases = {
        "ozon": MarketPlace.OZON,
        "wb": MarketPlace.WB,
        "yandex": MarketPlace.YANDEX,
    }
    try:
        return aliases[value]
    except KeyError as exc:
        msg = f"Unknown marketplace: {value}"
        raise ValueError(msg) from exc


@app.on_event("startup")
async def startup_event() -> None:
    """Run on application startup."""
    logger.info("Launching marketplace parser bot...")

    try:
        connect_to_db()
        logger.info("Connection to PostgreSQL successful!")

    except DatabaseConnectionError:
        logger.exception("Error connecting to database")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Render home page."""
    return templates.TemplateResponse(
        request,
        "index.html",
    )


@app.get("/parser", response_class=HTMLResponse)
async def parser_form(request: Request) -> HTMLResponse:
    """Render parser form."""
    return templates.TemplateResponse(
        request,
        "parser_form.html",
    )


@app.post("/parser", response_class=HTMLResponse)
async def parser_result(
    request: Request,
    marketplaces: Annotated[list[str], Form(...)],
    product_name: Annotated[str, Form(...)],
) -> HTMLResponse:
    """Return result of parsing."""
    selected_markets = [_parse_marketplace(m) for m in marketplaces]
    logger.info(
        "Start parsing marketplace=%s product=%s",
        selected_markets,
        product_name,
    )

    products = find_best_offer(
        query=product_name,
        marketplaces=selected_markets,
        count_products=5,
    )

    logger.info(
        "Parsing completed. Found %s products",
        len(products),
    )

    return templates.TemplateResponse(
        request=request,
        name="result_table.html",
        context={
            "request": request,
            "products": products,
        },
    )
