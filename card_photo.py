"""Bounded, optional photo preparation for card identification.

The original photograph is never replaced in the audit record. This module
only prepares a temporary inference copy and reports OCR as unverified clues.
"""
from __future__ import annotations

import re
from PIL import Image, ImageEnhance, ImageOps


def prepare_card_photo(image: Image.Image, *, max_side: int = 1600) -> Image.Image:
    """Normalize orientation/contrast and rectify a clear card quadrilateral.

    OpenCV is optional: deployment without it still has a safe Pillow path.
    Ambiguous contours are ignored instead of cropping away card details.
    """
    if not 320 <= max_side <= 2400:
        raise ValueError('Invalid image limit')
    result = ImageOps.exif_transpose(image).convert('RGB')
    result.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    try:
        import cv2
        import numpy as np
    except ImportError:
        cv2 = None
    if cv2 is not None:
        pixels = np.asarray(result)
        gray = cv2.cvtColor(pixels, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        area = result.width * result.height
        for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:8]:
            perimeter = cv2.arcLength(contour, True)
            corners = cv2.approxPolyDP(contour, 0.025 * perimeter, True)
            if len(corners) != 4 or cv2.contourArea(corners) < 0.28 * area:
                continue
            pts = corners.reshape(4, 2).astype('float32')
            ordered = np.zeros((4, 2), dtype='float32')
            ordered[0], ordered[2] = pts[np.argmin(pts.sum(axis=1))], pts[np.argmax(pts.sum(axis=1))]
            ordered[1], ordered[3] = pts[np.argmin(np.diff(pts, axis=1))], pts[np.argmax(np.diff(pts, axis=1))]
            width = max(np.linalg.norm(ordered[1] - ordered[0]), np.linalg.norm(ordered[2] - ordered[3]))
            height = max(np.linalg.norm(ordered[3] - ordered[0]), np.linalg.norm(ordered[2] - ordered[1]))
            if not 0.55 <= min(width, height) / max(width, height) <= 0.85:
                continue
            target = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype='float32')
            warped = cv2.warpPerspective(pixels, cv2.getPerspectiveTransform(ordered, target),
                                         (int(width), int(height)))
            result = Image.fromarray(warped)
            break
    # A modest contrast lift helps OCR without aggressive sharpening of foil glare.
    return ImageEnhance.Contrast(ImageOps.autocontrast(result, cutoff=1)).enhance(1.08)


def unverified_collector_numbers(image: Image.Image) -> tuple[str, ...]:
    """Extract possible collector numbers when local Tesseract is installed.

    OCR is a search clue only; it must not create a catalog-confirmed variant.
    """
    try:
        import pytesseract
        raw = pytesseract.image_to_string(image, config='--psm 11', timeout=3)
    except (ImportError, RuntimeError, OSError):
        return ()
    tokens = re.findall(r'(?<!\w)(?:[A-Z]{0,3}\s*)?\d{1,4}\s*/\s*\d{1,4}(?!\w)', raw.upper())
    return tuple(dict.fromkeys(re.sub(r'\s+', '', value) for value in tokens))[:8]
