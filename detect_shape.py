# detect_shape.py  — pure OpenCV, no mediapipe / YOLO required
import os
import cv2
import numpy as np


###############################################
#   SILHOUETTE-BASED BODY SHAPE DETECTION
###############################################

def _get_person_mask(img):
    """
    Returns a binary mask isolating the foreground person.
    Uses GrabCut seeded from the image centre.
    """
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    # Seed rect: leave a small border so GrabCut has background to learn from
    margin_x = int(w * 0.10)
    margin_y = int(h * 0.05)
    rect = (margin_x, margin_y, w - 2 * margin_x, h - 2 * margin_y)

    try:
        cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        fg_mask = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
        return fg_mask
    except Exception as e:
        print(f"[detect_shape] GrabCut failed: {e}")
        return None


def _measure_width_at_row(fg_mask, row_y):
    """Return pixel width of the foreground region at a given row."""
    if row_y < 0 or row_y >= fg_mask.shape[0]:
        return 0
    row = fg_mask[row_y, :]
    cols = np.where(row > 127)[0]
    if len(cols) < 2:
        return 0
    return int(cols[-1] - cols[0])


def _classify_shape(shoulder_w, hip_w):
    if hip_w == 0 or shoulder_w == 0:
        return "Unknown"
    ratio = shoulder_w / hip_w
    print(f"[detect_shape] shoulder_w={shoulder_w}, hip_w={hip_w}, ratio={ratio:.3f}")
    if ratio >= 1.10:
        return "Inverted Triangle"
    elif ratio <= 0.92:
        return "Pear"
    elif 0.92 < ratio <= 1.05:
        return "Rectangle"
    else:
        return "Hourglass"


def _detect_via_silhouette(img):
    """
    Estimate body shape by measuring silhouette width at shoulder and hip levels.
    Samples several rows around the expected anatomical positions and averages them.
    """
    h, w = img.shape[:2]

    fg_mask = _get_person_mask(img)
    if fg_mask is None:
        return "Unknown"

    # Find the vertical extent of the foreground blob
    rows_with_fg = np.where(fg_mask.max(axis=1) > 127)[0]
    if len(rows_with_fg) < 20:
        print("[detect_shape] Silhouette too small — try a clearer full-body photo")
        return "Unknown"

    top_row = int(rows_with_fg[0])
    bot_row = int(rows_with_fg[-1])
    body_h  = bot_row - top_row

    # Shoulder zone: 18–26 % down the body height
    # Hip zone:      55–65 % down the body height
    def avg_width(pct_lo, pct_hi):
        widths = []
        for pct in np.linspace(pct_lo, pct_hi, 7):
            row_y = int(top_row + pct * body_h)
            ww = _measure_width_at_row(fg_mask, row_y)
            if ww > 0:
                widths.append(ww)
        return int(np.median(widths)) if widths else 0

    shoulder_w = avg_width(0.18, 0.26)
    hip_w      = avg_width(0.55, 0.65)

    print(f"[detect_shape] Silhouette — shoulder_w={shoulder_w}, hip_w={hip_w}")
    if shoulder_w == 0 or hip_w == 0:
        return "Unknown"

    return _classify_shape(shoulder_w, hip_w)


###############################################
#         MAIN DETECTION FUNCTION
###############################################
def detect_body_shape(image_path):
    print(f"[detect_shape] Processing: {image_path}")

    img = cv2.imread(image_path)
    if img is None:
        print(f"[detect_shape] Could not read image: {image_path}")
        return "Unknown"

    h, w = img.shape[:2]
    print(f"[detect_shape] Image size: {w}x{h}")

    # Resize very large images for speed (GrabCut is slow on 4K images)
    max_dim = 800
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
        print(f"[detect_shape] Resized to {img.shape[1]}x{img.shape[0]}")

    shape = _detect_via_silhouette(img)
    print(f"[detect_shape] Result: {shape}")
    return shape
