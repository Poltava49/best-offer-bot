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
    """Find x-coordinate of matching cutout using contour shape matching."""
    piece_mask = _get_piece_mask(puzzle_img)
    ph, pw = piece_mask.shape

    bg_gray = cv2.cvtColor(background_img[:, :, :3], cv2.COLOR_BGR2GRAY)
    bg_h, bg_w = bg_gray.shape

    if ph > bg_h or pw > bg_w:
        logger.warning("Puzzle piece larger than background")
        return None

    # get puzzle piece contour
    piece_contours, _ = cv2.findContours(piece_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not piece_contours:
        logger.warning("No contours found in puzzle piece")
        return None
    piece_contour = max(piece_contours, key=cv2.contourArea)
    piece_area = cv2.contourArea(piece_contour)

    # threshold background to find cutout regions (they differ in brightness)
    bg_blur = cv2.GaussianBlur(bg_gray, (5, 5), 0)
    # find regions brighter than background median (cutouts tend to be lighter)
    median_val = float(np.median(bg_blur))
    _, bg_thresh_light = cv2.threshold(bg_blur, median_val + 10, 255, cv2.THRESH_BINARY)
    # also try darker threshold (for dark-style captchas)
    _, bg_thresh_dark = cv2.threshold(bg_blur, median_val - 10, 255, cv2.THRESH_BINARY_INV)

    best_x = 0
    best_y = 0
    best_score = float("inf")  # lower = better for matchShapes

    for bg_thresh in (bg_thresh_light, bg_thresh_dark):
        contours, _ = cv2.findContours(bg_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # filter by area — must be reasonably close to puzzle piece area
            if area < piece_area * 0.3 or area > piece_area * 3.0:
                continue
            # compare shape using Hu moments (0 = identical shape)
            score = cv2.matchShapes(piece_contour, cnt, cv2.CONTOURS_MATCH_I2, 0)
            if score < best_score:
                best_score = score
                best_x, best_y = cv2.boundingRect(cnt)[:2]

    logger.info("Best shape match score: %.4f at x=%d y=%d", best_score, best_x, best_y)

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
