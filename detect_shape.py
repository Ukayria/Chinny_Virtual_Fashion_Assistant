# detect_shape.py — robust edge-based detection for Render free tier
import os
import cv2
import numpy as np


def _width_at_band(mask, top, pct_lo, pct_hi, body_h):
    """Average filled-mask width across a vertical band."""
    widths = []
    for pct in np.linspace(pct_lo, pct_hi, 9):
        row_y = int(top + pct * body_h)
        if row_y >= mask.shape[0]:
            continue
        cols = np.where(mask[row_y] > 0)[0]
        if len(cols) >= 2:
            widths.append(int(cols[-1] - cols[0]))
    return int(np.median(widths)) if widths else 0


def _classify(shoulder_w, hip_w):
    if shoulder_w == 0 or hip_w == 0:
        return None
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


def _try_detect(img):
    """Try detection with given image. Returns shape string or None."""
    h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Try multiple Canny threshold pairs from lenient to strict
    for lo, hi in [(20, 60), (30, 90), (15, 45), (50, 120)]:
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, lo, hi)

        # Close gaps in silhouette
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        # Dilate to thicken edges
        closed = cv2.dilate(closed, kernel, iterations=1)

        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue

        biggest = max(contours, key=cv2.contourArea)
        area_ratio = cv2.contourArea(biggest) / (h * w)
        print(f"[detect_shape] Canny({lo},{hi}) largest contour area ratio: {area_ratio:.3f}")

        # Accept if contour covers at least 3% of image (was 5%, now more lenient)
        if area_ratio < 0.03:
            continue

        # Build filled mask
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(mask, [biggest], -1, 255, thickness=cv2.FILLED)

        rows = np.where(mask.max(axis=1) > 0)[0]
        if len(rows) < 20:
            continue

        top_row = int(rows[0])
        bot_row = int(rows[-1])
        body_h  = bot_row - top_row

        shoulder_w = _width_at_band(mask, top_row, 0.18, 0.26, body_h)
        hip_w      = _width_at_band(mask, top_row, 0.55, 0.65, body_h)

        shape = _classify(shoulder_w, hip_w)
        if shape:
            return shape

    return None


def detect_body_shape(image_path):
    print(f"[detect_shape] Processing: {image_path}")

    img = cv2.imread(image_path)
    if img is None:
        print("[detect_shape] Could not read image")
        return "Unknown"

    h, w = img.shape[:2]

    # Resize to 600px max — keeps memory low on Render free tier
    max_dim = 600
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)),
                         interpolation=cv2.INTER_AREA)
        h, w = img.shape[:2]
    print(f"[detect_shape] Working size: {w}x{h}")

    # ── Attempt 1: original image ──
    shape = _try_detect(img)
    if shape:
        print(f"[detect_shape] Result: {shape}")
        return shape

    # ── Attempt 2: boost contrast with CLAHE then retry ──
    print("[detect_shape] Retrying with contrast enhancement...")
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    enhanced = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
    shape = _try_detect(enhanced)
    if shape:
        print(f"[detect_shape] Result (enhanced): {shape}")
        return shape

    # ── Attempt 3: segment using simple threshold on value channel ──
    print("[detect_shape] Retrying with HSV threshold segmentation...")
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Build a mask of non-white, non-very-dark pixels (the person)
    lower = np.array([0,  20,  30])
    upper = np.array([180, 255, 230])
    mask = cv2.inRange(hsv, lower, upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 13))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.dilate(mask, kernel, iterations=2)

    rows = np.where(mask.max(axis=1) > 0)[0]
    if len(rows) >= 20:
        top_row = int(rows[0])
        bot_row = int(rows[-1])
        body_h  = bot_row - top_row
        shoulder_w = _width_at_band(mask, top_row, 0.18, 0.26, body_h)
        hip_w      = _width_at_band(mask, top_row, 0.55, 0.65, body_h)
        shape = _classify(shoulder_w, hip_w)
        if shape:
            print(f"[detect_shape] Result (HSV): {shape}")
            return shape

    # ── Final fallback: use width profile of whole image brightness ──
    print("[detect_shape] Using brightness profile fallback...")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Find the darkest horizontal band (the person against a lighter background)
    col_profile = np.mean(gray, axis=0)  # average brightness per column
    row_profile = np.mean(gray, axis=1)  # average brightness per row

    # Find where person likely is: rows with below-average brightness
    thresh = np.mean(row_profile) * 0.95
    person_rows = np.where(row_profile < thresh)[0]

    if len(person_rows) >= 20:
        top_row = int(person_rows[0])
        bot_row = int(person_rows[-1])
        body_h  = bot_row - top_row

        def band_width(pct_lo, pct_hi):
            widths = []
            for pct in np.linspace(pct_lo, pct_hi, 9):
                row_y = int(top_row + pct * body_h)
                if row_y >= gray.shape[0]:
                    continue
                row = gray[row_y]
                row_thresh = np.mean(row) * 0.92
                dark_cols = np.where(row < row_thresh)[0]
                if len(dark_cols) >= 2:
                    widths.append(int(dark_cols[-1] - dark_cols[0]))
            return int(np.median(widths)) if widths else 0

        shoulder_w = band_width(0.18, 0.26)
        hip_w      = band_width(0.55, 0.65)
        shape = _classify(shoulder_w, hip_w)
        if shape:
            print(f"[detect_shape] Result (brightness fallback): {shape}")
            return shape

    print("[detect_shape] All methods failed — defaulting to Hourglass")
    return "Hourglass"   # graceful default so app always shows recommendations
