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
    """Find x-coordinate of matching cutout using darkness scanning."""
    piece_mask = _get_piece_mask(puzzle_img)
    ph, pw = piece_mask.shape

    # convert background to grayscale — cutouts appear darker
    bg_gray = cv2.cvtColor(background_img[:, :, :3], cv2.COLOR_BGR2GRAY)
    bg_h, bg_w = bg_gray.shape

    if ph > bg_h or pw > bg_w:
        logger.warning("Puzzle piece larger than background")
        return None

    # invert: dark areas become bright → we look for maximum
    bg_inv = 255 - bg_gray.astype(np.float32)

    # normalize mask to 0..1
    mask_norm = piece_mask.astype(np.float32) / 255.0
    mask_area = mask_norm.sum()

    best_score = -1.0
    best_x = 0
    best_y = 0

    # slide the mask across the background
    for x in range(bg_w - pw):
        for y in range(bg_h - ph):
            region = bg_inv[y:y + ph, x:x + pw]
            score = float((region * mask_norm).sum()) / mask_area
            if score > best_score:
                best_score = score
                best_x = x
                best_y = y

    logger.info("Best darkness score: %.2f at x=%d y=%d", best_score, best_x, best_y)

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

    if background is None or puzzle is None:
        return None

    gap_x = _find_gap_x(background, puzzle)
    if gap_x is None:
        return None

    drag_distance = gap_x - puzzle_start_x
    logger.info("gap_x=%d, puzzle_start_x=%d, drag=%d", gap_x, puzzle_start_x, drag_distance)
    return max(0, drag_distance)
