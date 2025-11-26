import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose

def get_px(landmark, width, height):
    return int(landmark.x * width), int(landmark.y * height)

def average(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None

def detect_body_shape(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "Unknown"

    h, w, _ = img.shape

    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
        results = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        if not results.pose_landmarks:
            return "Unknown"

        lm = results.pose_landmarks.landmark

        # collect multiple shoulder width measurements
        shoulder_points = []
        hip_points = []

        def safe_landmark(idx):
            try:
                return lm[idx]
            except Exception:
                return None

        # primary shoulder pair
        shoulder_points.append((safe_landmark(mp_pose.PoseLandmark.LEFT_SHOULDER),
                                safe_landmark(mp_pose.PoseLandmark.RIGHT_SHOULDER)))
        # secondary shoulder proxy
        shoulder_points.append((safe_landmark(mp_pose.PoseLandmark.LEFT_ELBOW),
                                safe_landmark(mp_pose.PoseLandmark.RIGHT_ELBOW)))

        # primary hip pair
        hip_points.append((safe_landmark(mp_pose.PoseLandmark.LEFT_HIP),
                           safe_landmark(mp_pose.PoseLandmark.RIGHT_HIP)))
        # secondary hip proxy (knees)
        hip_points.append((safe_landmark(mp_pose.PoseLandmark.LEFT_KNEE),
                           safe_landmark(mp_pose.PoseLandmark.RIGHT_KNEE)))

        shoulder_widths = []
        hip_widths = []

        for p1, p2 in shoulder_points:
            if p1 is None or p2 is None:
                shoulder_widths.append(None)
                continue
            x1, y1 = get_px(p1, w, h)
            x2, y2 = get_px(p2, w, h)
            shoulder_widths.append(abs(x2 - x1))

        for p1, p2 in hip_points:
            if p1 is None or p2 is None:
                hip_widths.append(None)
                continue
            x1, y1 = get_px(p1, w, h)
            x2, y2 = get_px(p2, w, h)
            hip_widths.append(abs(x2 - x1))

        shoulder = average(shoulder_widths)
        hip = average(hip_widths)

        if shoulder is None or hip is None or hip == 0:
            return "Unknown"

        ratio = shoulder / hip  

        # classification — tuned thresholds
        if ratio < 0.92:
            return "Pear"
        elif 0.92 <= ratio <= 1.05:
            return "Rectangle"
        elif ratio >= 1.10:
            return "Inverted Triangle"
        else:
            return "Hourglass"
