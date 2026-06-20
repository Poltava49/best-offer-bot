"""OpenCV-based Ozon slider captcha solver.

Downloads background and puzzle images, finds the matching cutout
using edge-based template matching, returns the x-offset to drag the slider.
"""

import logging

import cv2
import numpy as np
import requests

logger = logging.getLogger(__name__)


def _download_image(url: str, cookies: dict) -> np.ndarray | None:
    """Download image from URL and decode as RGBA numpy array."""
    try:
        resp = requests.get(url, cookies=cookies, timeout=10)
        resp.raise_for_status()
        arr = np.frombuffer(resp.content, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
        return img
    except Exception as e:
        logger.warning("Failed to download image %s: %s", url, e)
        return None


def _alpha_to_edge_template(puzzle_img: np.ndarray) -> np.ndarray:
    """Extract alpha channel of puzzle piece and apply edge detection."""
    if puzzle_img.shape[2] == 4:
        alpha = puzzle_img[:, :, 3]
    else:
        alpha = cv2.cvtColor(puzzle_img, cv2.COLOR_BGR2GRAY)

    # binary mask of the puzzle shape
    _, mask = cv2.threshold(alpha, 10, 255, cv2.THRESH_BINARY)
    edges = cv2.Canny(mask, 50, 150)
    return edges


def _find_gap_x(background_img: np.ndarray, puzzle_img: np.ndarray) -> int | None:
    """Find x-coordinate of the matching cutout in the background image."""
    bg_gray = cv2.cvtColor(background_img[:, :, :3], cv2.COLOR_BGR2GRAY)
    bg_edges = cv2.Canny(bg_gray, 30, 100)

    template = _alpha_to_edge_template(puzzle_img)

    result = cv2.matchTemplate(bg_edges, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    logger.info("Template match score: %.3f at x=%d", max_val, max_loc[0])

    if max_val < 0.2:
        logger.warning("Low match confidence: %.3f", max_val)
        return None

    # center x of the matched region
    gap_x = max_loc[0] + puzzle_img.shape[1] // 2
    return gap_x


def solve(image_url: str, puzzle_url: str, puzzle_start_x: int, cookies: dict) -> int | None:
    """Calculate how many pixels to drag the slider.

    Args:
        image_url: URL of background image with cutouts.
        puzzle_url: URL of puzzle piece image.
        puzzle_start_x: initial left position of puzzle piece (from CSS style).
        cookies: browser cookies for CDN auth.

    Returns:
        Pixel distance to drag slider, or None if detection failed.
    """
    background = _download_image(image_url, cookies)
    puzzle = _download_image(puzzle_url, cookies)

    if background is None or puzzle is None:
        return None

    gap_x = _find_gap_x(background, puzzle)
    if gap_x is None:
        return None

    drag_distance = gap_x - puzzle_start_x
    logger.info("gap_x=%d, puzzle_start_x=%d, drag=%d", gap_x, puzzle_start_x, drag_distance)
    return max(0, drag_distance)
