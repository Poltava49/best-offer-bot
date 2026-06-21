"""OpenCV-based Ozon slider captcha solver.

Strategy: cutouts on background are darker than surrounding area.
We use the puzzle piece silhouette as a mask and scan the background
for the position where the masked region is darkest (= the actual hole).
"""

import logging

import cv2
import numpy as np
import requests

logger = logging.getLogger(__name__)


def _download_image(url: str, cookies: dict) -> np.ndarray | None:
    try:
        resp = requests.get(url, cookies=cookies, timeout=10)
        resp.raise_for_status()
        arr = np.frombuffer(resp.content, np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
    except Exception as e:
        logger.warning("Failed to download image %s: %s", url, e)
        return None


def _get_piece_mask(puzzle_img: np.ndarray) -> np.ndarray:
    """Extract binary silhouette of puzzle piece from alpha or color."""
    if puzzle_img.shape[2] == 4:
        alpha = puzzle_img[:, :, 3]
        _, mask = cv2.threshold(alpha, 10, 255, cv2.THRESH_BINARY)
        return mask

    # fallback: threshold by saturation if no alpha
    hsv = cv2.cvtColor(puzzle_img, cv2.COLOR_BGR2HSV)
    _, mask = cv2.threshold(hsv[:, :, 1], 30, 255, cv2.THRESH_BINARY)
    return mask


def _find_gap_x(background_img: np.ndarray, puzzle_img: np.ndarray) -> int | None:
    """Find x-coordinate of matching cutout using ring-border template matching."""
    piece_mask = _get_piece_mask(puzzle_img)
    ph, pw = piece_mask.shape

    bg_gray = cv2.cvtColor(background_img[:, :, :3], cv2.COLOR_BGR2GRAY)
    bg_h, bg_w = bg_gray.shape

    if ph > bg_h or pw > bg_w:
        logger.warning("Puzzle piece larger than background")
        return None

    # create ring template: only the border of the puzzle piece shape
    # erode mask and subtract — leaves just the outline
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    piece_eroded = cv2.erode(piece_mask, kernel, iterations=3)
    piece_border = cv2.subtract(piece_mask, piece_eroded)

    # enhance background edges to make cutout borders visible
    bg_blur = cv2.GaussianBlur(bg_gray, (3, 3), 0)
    bg_edges = cv2.Canny(bg_blur, 20, 80)

    # match the piece border shape against background edges
    result = cv2.matchTemplate(bg_edges, piece_border, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    best_x, best_y = max_loc
    logger.info("Ring match score: %.3f at x=%d y=%d", max_val, best_x, best_y)

    # save debug image with detected region highlighted
    try:
        debug = background_img.copy()
        cv2.rectangle(debug, (best_x, best_y), (best_x + pw, best_y + ph), (0, 255, 0, 255), 3)
        cv2.imwrite("/app/captcha_debug.png", debug)
    except Exception:
        pass

    gap_x = best_x + pw // 2
    return gap_x


def solve(image_url: str, puzzle_url: str, puzzle_start_x: int, cookies: dict) -> int | None:
    """Calculate how many pixels to drag the slider."""
    background = _download_image(image_url, cookies)
    puzzle = _download_image(puzzle_url, cookies)

    if background is None:
        logger.warning("Failed to download background image")
        return None
    if puzzle is None:
        logger.warning("Failed to download puzzle image")
        return None

    logger.info("Images downloaded: bg=%s puzzle=%s", background.shape, puzzle.shape)

    try:
        gap_x = _find_gap_x(background, puzzle)
    except Exception as e:
        logger.warning("_find_gap_x raised exception: %s", e, exc_info=True)
        return None
    if gap_x is None:
        logger.warning("_find_gap_x returned None")
        return None

    drag_distance = gap_x - puzzle_start_x
    logger.info("gap_x=%d, puzzle_start_x=%d, drag=%d", gap_x, puzzle_start_x, drag_distance)
    return max(0, drag_distance)
