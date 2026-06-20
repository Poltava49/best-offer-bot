"""Ozon captcha dataset collector.

Detects slider captcha on page, downloads background and puzzle images,
saves them to dataset directory for CNN training.
"""

import json
import logging
from pathlib import Path
from uuid import uuid4

import requests

logger = logging.getLogger(__name__)

DATASET_DIR = Path("captcha_dataset/raw")


def is_captcha_page(driver) -> bool:
    """Check if current page is Ozon antibot captcha."""
    try:
        return driver.find_element("id", "captcha-container") is not None
    except Exception:
        return False


def collect(driver) -> Path | None:
    """Download captcha images and save to dataset.

    Returns path to saved sample directory, or None if captcha not detected.
    """
    if not is_captcha_page(driver):
        return None

    logger.info("Captcha detected — collecting sample")

    try:
        image_url = driver.find_element("id", "image").get_attribute("src")
        puzzle_url = driver.find_element("id", "puzzle").get_attribute("src")
        puzzle_style = driver.find_element("id", "puzzle").get_attribute("style")
        incident = driver.find_element("id", "incident").get_attribute("value")
    except Exception:
        logger.warning("Failed to extract captcha elements")
        return None

    sample_id = uuid4().hex
    sample_dir = DATASET_DIR / sample_id
    sample_dir.mkdir(parents=True, exist_ok=True)

    cookies = {c["name"]: c["value"] for c in driver.get_cookies()}

    if not _download(image_url, sample_dir / "background.png", cookies):
        return None
    if not _download(puzzle_url, sample_dir / "puzzle.png", cookies):
        return None

    metadata = {
        "id": sample_id,
        "incident": incident,
        "image_url": image_url,
        "puzzle_url": puzzle_url,
        "puzzle_style": puzzle_style,
        # x-coordinate label — to be filled after manual annotation
        "gap_x": None,
    }
    (sample_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2)
    )

    logger.info("Captcha sample saved: %s", sample_dir)
    return sample_dir


def _download(url: str, dest: Path, cookies: dict) -> bool:
    """Download image from CDN using session cookies."""
    try:
        resp = requests.get(url, cookies=cookies, timeout=10)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
        return True
    except Exception as e:
        logger.warning("Failed to download %s: %s", url, e)
        return False
