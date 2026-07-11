"""
Analyzer module.

This module build simple visualization and analitics on parsing data
"""

import logging
from dataclasses import asdict
from typing import Any, cast

import pandas as pd
from sklearn.preprocessing import StandardScaler  # type: ignore[import-untyped]

from src.app.models import Product

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

FEATURES_WEIGTHS: dict[str, float] = {
    "price": -0.45,
    "rating": 0.25,
    "rating_count": 0.3,
}


class BestOfferAnalyzer:
    """Analyzes parsed product data to generate insights and visualizations."""

    def __init__(self) -> None:
        """Initialize analyzer."""

    def get_distribution_of_products_price(self) -> None:  # bytes
        """Generate plot figure with price distribution by user query."""
        ...  # noqa: PIE790

    def get_top_n_products(
        self, n: int, products: list[Product]
    ) -> list[dict[str, Any]]:
        """Calculate top-5 products by weighted scores."""
        if not products:
            return []
        df = pd.DataFrame([asdict(p) for p in products])
        scaler = StandardScaler()
        features = ["price", "rating", "rating_count"]
        normalized = df.copy()
        normalized[features] = scaler.fit_transform(normalized[features])
        normalized["score"] = normalized[features].dot(pd.Series(FEATURES_WEIGTHS))
        df["score"] = normalized["score"]
        logger.info("Products with scores %s", df.head(15))
        top = df.sort_values("score", ascending=False).head(n).drop("score", axis=1)
        return cast("list[dict[str, Any]]", top.to_dict(orient="records"))
