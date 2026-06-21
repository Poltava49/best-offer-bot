"""Captcha handler: detects captcha on page and attempts to solve it via slider drag."""

import logging
import re
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

from src.captcha import collector, solver

logger = logging.getLogger(__name__)


def _parse_left_px(style: str) -> int:
    """Extract left: <N>px value from CSS style string."""
    match = re.search(r"left:\s*(\d+)px", style or "")
    return int(match.group(1)) if match else 0


def _human_drag(driver, slider_el, distance: int) -> None:
    """Drag slider element by distance px with human-like acceleration curve."""
    actions = ActionChains(driver)
    actions.click_and_hold(slider_el)
    actions.pause(0.1)

    # split movement into steps with easing
    steps = 30
    for i in range(1, steps + 1):
        # ease-in-out curve
        t = i / steps
        eased = t * t * (3 - 2 * t)
        x = int(distance * eased)
        actions.move_by_offset(x - int(distance * ((i - 1) / steps) ** 2 * (3 - 2 * (i - 1) / steps)), 0)
        actions.pause(0.01)

    actions.release()
    actions.perform()


def handle(driver) -> bool:
    """Detect and solve captcha if present.

    Returns True if captcha was solved (or not present), False if failed.
    """
    if not collector.is_captcha_page(driver):
        return True

    logger.info("Solving captcha...")

    try:
        image_url = driver.find_element(By.ID, "image").get_attribute("src")
        puzzle_el = driver.find_element(By.ID, "puzzle")
        puzzle_url = puzzle_el.get_attribute("src")
        puzzle_style = puzzle_el.get_attribute("style")
        slider_el = driver.find_element(By.ID, "slider")
    except Exception as e:
        logger.warning("Cannot find captcha elements: %s", e)
        collector.collect(driver)
        return False

    puzzle_start_x = _parse_left_px(puzzle_style)
    cookies = {c["name"]: c["value"] for c in driver.get_cookies()}

    # get scale factor from captcha container CSS var --scale
    try:
        scale_str = driver.execute_script(
            "return getComputedStyle(document.getElementById('captcha'))"
            ".getPropertyValue('--scale').trim()"
        )
        scale = float(scale_str) if scale_str else 1.0
    except Exception:
        scale = 1.0
    logger.info("Captcha scale: %.2f, puzzle_start_x: %d", scale, puzzle_start_x)

    # get actual rendered width of slider track
    try:
        slider_bg = driver.find_element(By.ID, "slider-background")
        slider_width = driver.execute_script(
            "return arguments[0].offsetWidth", slider_bg
        )
    except Exception:
        slider_width = None
    logger.info("Slider track width: %s", slider_width)

    drag_distance = solver.solve(image_url, puzzle_url, puzzle_start_x, cookies)

    if drag_distance is None:
        logger.warning("Solver failed — saving sample for training")
        collector.collect(driver)
        return False

    # scale drag distance to match rendered size
    scaled_distance = int(drag_distance * scale)
    logger.info("drag_distance=%d, scale=%.2f, scaled=%d, slider_width=%s",
                drag_distance, scale, scaled_distance, slider_width)
    _human_drag(driver, slider_el, scaled_distance)
    time.sleep(2)

    if collector.is_captcha_page(driver):
        logger.warning("Captcha still present after solve attempt")
        collector.collect(driver)
        return False

    logger.info("Captcha solved successfully")
    return True
