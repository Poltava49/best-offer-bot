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
    """Find x-coordinate of matching cutout using edge contour matching."""
    piece_mask = _get_piece_mask(puzzle_img)
    ph, pw = piece_mask.shape

    bg_gray = cv2.cvtColor(background_img[:, :, :3], cv2.COLOR_BGR2GRAY)
    bg_h, bg_w = bg_gray.shape

    if ph > bg_h or pw > bg_w:
        logger.warning("Puzzle piece larger than background")
        return None

    # get contour edges of puzzle piece shape
    piece_edges = cv2.Canny(piece_mask, 50, 150)
    # dilate slightly to allow small misalignments
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    piece_edges_dilated = cv2.dilate(piece_edges, kernel, iterations=1)

    # get gradient magnitude of background — highlights cutout borders
    bg_blur = cv2.GaussianBlur(bg_gray, (3, 3), 0)
    grad_x = cv2.Sobel(bg_blur, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(bg_blur, cv2.CV_64F, 0, 1, ksize=3)
    bg_gradient = cv2.magnitude(grad_x, grad_y)
    bg_gradient = cv2.normalize(bg_gradient, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # method 1: match puzzle contour edges against background gradient
    result_edge = cv2.matchTemplate(
        bg_gradient, piece_edges_dilated, cv2.TM_CCOEFF_NORMED
    )
    _, max_val_edge, _, max_loc_edge = cv2.minMaxLoc(result_edge)

    # method 2: match puzzle contour against background edges (Canny)
    bg_edges = cv2.Canny(bg_gray, 30, 100)
    result_canny = cv2.matchTemplate(
        bg_edges, piece_edges_dilated, cv2.TM_CCOEFF_NORMED
    )
    _, max_val_canny, _, max_loc_canny = cv2.minMaxLoc(result_canny)

    logger.info("Edge score: %.3f at %s | Gradient score: %.3f at %s",
                max_val_canny, max_loc_canny, max_val_edge, max_loc_edge)

    # pick method with higher confidence
    if max_val_edge >= max_val_canny:
        best_loc = max_loc_edge
        best_score = max_val_edge
        method = "gradient"
    else:
        best_loc = max_loc_canny
        best_score = max_val_canny
        method = "canny"

    best_x, best_y = best_loc
    logger.info("Using %s method, score=%.3f at x=%d y=%d", method, best_score, best_x, best_y)

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
