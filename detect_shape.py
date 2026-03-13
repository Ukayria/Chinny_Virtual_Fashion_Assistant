# detect_shape.py — lightweight edge-based detection, no GrabCut/YOLO/MediaPipe
import os
import cv2
import numpy as np


def _width_at_band(edge_mask, top, pct_lo, pct_hi, body_h):
    """Average foreground width across a vertical band."""
    widths = []
    for pct in np.linspace(pct_lo, pct_hi, 9):
        row_y = int(top + pct * body_h)
        if row_y >= edge_mask.shape[0]:
            continue
        cols = np.where(edge_mask[row_y] > 0)[0]
        if len(cols) >= 2:
            widths.append(int(cols[-1] - cols[0]))
    return int(np.median(widths)) if widths else 0


def _classify(shoulder_w, hip_w):
    if shoulder_w == 0 or hip_w == 0:
        return "Unknown"
    ratio = shoulder_w / hip_w
    print(f"[detect_shape] shoulder={shoulder_w}px  hip={hip_w}px  ratio={ratio:.3f}")
    if ratio >= 1.10:
        return "Inverted Triangle"
    elif ratio <= 0.92:
        return "Pear"
    elif ratio <= 1.05:
        return "Rectangle"
    else:
        return "Hourglass"


def detect_body_shape(image_path):
    print(f"[detect_shape] Processing: {image_path}")

    img = cv2.imread(image_path)
    if img is None:
        print("[detect_shape] Could not read image")
        return "Unknown"

    # ── Resize to max 600px — fast & low-memory ──
    h, w = img.shape[:2]
    max_dim = 600
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)),
                         interpolation=cv2.INTER_AREA)
    h, w = img.shape[:2]
    print(f"[detect_shape] Working size: {w}x{h}")

    # ── Convert to grayscale, blur, edge detect ──
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 30, 90)

    # ── Morphological close to fill silhouette gaps ──
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # ── Find the largest contour (= person) ──
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("[detect_shape] No contours found")
        return "Unknown"

    biggest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(biggest) < (h * w * 0.05):
        print("[detect_shape] Largest contour too small — poor background contrast")
        return "Unknown"

    # ── Build filled mask from contour ──
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.drawContours(mask, [biggest], -1, 255, thickness=cv2.FILLED)

    # ── Find vertical extent of the person ──
    rows = np.where(mask.max(axis=1) > 0)[0]
    if len(rows) < 20:
        print("[detect_shape] Mask too thin")
        return "Unknown"

    top_row = int(rows[0])
    bot_row = int(rows[-1])
    body_h  = bot_row - top_row

    # ── Sample shoulder (18–26%) and hip (55–65%) bands ──
    shoulder_w = _width_at_band(mask, top_row, 0.18, 0.26, body_h)
    hip_w      = _width_at_band(mask, top_row, 0.55, 0.65, body_h)

    if shoulder_w == 0 or hip_w == 0:
        print("[detect_shape] Could not measure widths — try a photo with plain background")
        return "Unknown"

    shape = _classify(shoulder_w, hip_w)
    print(f"[detect_shape] Result: {shape}")
    return shape
