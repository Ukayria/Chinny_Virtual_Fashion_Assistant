# detect_shape.py
import os
import cv2
import numpy as np

# Try ultralytics YOLO pose
_USE_ULTRALYTICS = False
_pose_model = None

try:
    from ultralytics import YOLO
    _USE_ULTRALYTICS = True
except Exception:
    _USE_ULTRALYTICS = False

# Mediapipe fallback
_MP_AVAILABLE = False
try:
    import mediapipe as mp
    _MP_AVAILABLE = True
    mp_pose = mp.solutions.pose
except Exception:
    _MP_AVAILABLE = False


###############################################
#           LOAD YOLOv8 POSE MODEL
###############################################
if _USE_ULTRALYTICS:
    try:
        # First try local file
        local_path = os.path.join(os.getcwd(), "yolov8n-pose.pt")
        if os.path.exists(local_path):
            _pose_model = YOLO(local_path)
        else:
            # Auto-download from ultralytics
            _pose_model = YOLO("yolov8n-pose.pt")
    except Exception:
        _pose_model = None


###############################################
#      CLASSIFY BODY SHAPE FROM KEYPOINTS
###############################################
def _classify_from_keypoints_xy(xy):
    try:
        if xy is None or xy.shape[0] < 13:
            return "Unknown"

        # COCO keypoints index:
        # 5 = Left Shoulder, 6 = Right Shoulder
        # 11 = Left Hip, 12 = Right Hip
        left_sh = xy[5]
        right_sh = xy[6]
        left_hip = xy[11]
        right_hip = xy[12]

        if np.any(np.isnan(left_sh)) or np.any(np.isnan(right_sh)) or np.any(np.isnan(left_hip)) or np.any(np.isnan(right_hip)):
            return "Unknown"

        shoulder_w = np.linalg.norm(left_sh - right_sh)
        hip_w = np.linalg.norm(left_hip - right_hip)

        if hip_w == 0 or shoulder_w == 0:
            return "Unknown"

        ratio = shoulder_w / hip_w

        # Tuned thresholds
        if ratio >= 1.10:
            return "Inverted Triangle"
        elif ratio <= 0.92:
            return "Pear"
        elif 0.92 < ratio <= 1.05:
            return "Rectangle"
        else:
            return "Hourglass"

    except Exception:
        return "Unknown"


###############################################
#         MAIN DETECTION FUNCTION
###############################################
def detect_body_shape(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "Unknown"

    ###############################
    #      TRY YOLOv8 POSE
    ###############################
    if _USE_ULTRALYTICS and _pose_model is not None:
        try:
            results = _pose_model(img)
            if results and len(results) > 0:
                r = results[0]

                if hasattr(r, "keypoints") and r.keypoints is not None:
                    kp = r.keypoints

                    # YOLOv8 format: list of tensors [1,17,2]
                    if hasattr(kp, "xy"):
                        arr = kp.xy
                        if isinstance(arr, (list, tuple)) and len(arr) > 0:
                            xy = arr[0].cpu().numpy() if hasattr(arr[0], "cpu") else np.array(arr[0])
                            return _classify_from_keypoints_xy(xy)

        except Exception:
            pass  # fallback to mediapipe

    ###############################
    #     MEDIAPIPE FALLBACK
    ###############################
    if _MP_AVAILABLE:
        try:
            with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb)

                if not results.pose_landmarks:
                    return "Unknown"

                lm = results.pose_landmarks.landmark
                h, w, _ = img.shape

                def px(i):
                    return np.array([lm[i].x * w, lm[i].y * h], dtype=float)

                left_sh = px(mp_pose.PoseLandmark.LEFT_SHOULDER)
                right_sh = px(mp_pose.PoseLandmark.RIGHT_SHOULDER)
                left_hip = px(mp_pose.PoseLandmark.LEFT_HIP)
                right_hip = px(mp_pose.PoseLandmark.RIGHT_HIP)

                shoulder_w = np.linalg.norm(left_sh - right_sh)
                hip_w = np.linalg.norm(left_hip - right_hip)

                if hip_w == 0 or shoulder_w == 0:
                    return "Unknown"

                ratio = shoulder_w / hip_w

                if ratio >= 1.10:
                    return "Inverted Triangle"
                elif ratio <= 0.92:
                    return "Pear"
                elif 0.92 < ratio <= 1.05:
                    return "Rectangle"
                else:
                    return "Hourglass"

        except Exception:
            return "Unknown"

    return "Unknown"