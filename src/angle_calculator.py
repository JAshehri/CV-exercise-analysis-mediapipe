"""
angle_calculator.py

============================================================
Joint Angle Calculator Module
============================================================

Purpose:
--------
Calculate human joint angles from MediaPipe Pose landmarks.

Features:
---------
- Supports 2D and 3D angle calculation.
- Uses Visibility and Presence validation.
- Handles missing landmarks safely.
- Supports MediaPipe pose_landmarks and world_landmarks.
"""

import math
from typing import Dict, Optional, Any, List


# ==========================================================
# MediaPipe Landmark Index Mapping
# ==========================================================

LANDMARK_INDEX = {
    "left_shoulder": 11,
    "right_shoulder": 12,

    "left_elbow": 13,
    "right_elbow": 14,

    "left_wrist": 15,
    "right_wrist": 16,

    "left_hip": 23,
    "right_hip": 24,

    "left_knee": 25,
    "right_knee": 26,

    "left_ankle": 27,
    "right_ankle": 28
}


# ==========================================================
# Single Angle Calculation
# ==========================================================

def calculate_angle(
    point_a: Any,
    point_b: Any,
    point_c: Any,
    visibility_threshold: float = 0.40,
    presence_threshold: float = 0.40,
    use_3d: bool = True,
    debug: bool = False
) -> Optional[float]:
    """
    Calculate angle between three points.

    Angle:
        A
        \
         \
          B -------- C

    The angle is calculated at point B.

    Parameters
    ----------
    use_3d:
        True  -> use x,y,z
        False -> use x,y only

    Returns
    -------
    float angle in degrees
    or None if data is unreliable.
    """

    try:

        # --------------------------------------------------
        # Validate Points
        # --------------------------------------------------

        for point in (point_a, point_b, point_c):

            if point is None:
                return None


            visibility = getattr(
                point,
                "visibility",
                1.0
            )

            presence = getattr(
                point,
                "presence",
                1.0
            )


            if visibility < visibility_threshold:
                return None


            if presence < presence_threshold:
                return None


        # --------------------------------------------------
        # Extract Coordinates
        # --------------------------------------------------

        if use_3d:

            a = [
                point_a.x,
                point_a.y,
                getattr(point_a, "z", 0.0)
            ]

            b = [
                point_b.x,
                point_b.y,
                getattr(point_b, "z", 0.0)
            ]

            c = [
                point_c.x,
                point_c.y,
                getattr(point_c, "z", 0.0)
            ]

        else:

            a = [
                point_a.x,
                point_a.y
            ]

            b = [
                point_b.x,
                point_b.y
            ]

            c = [
                point_c.x,
                point_c.y
            ]


        # --------------------------------------------------
        # Create Vectors
        # --------------------------------------------------

        vector_1 = [
            a[i] - b[i]
            for i in range(len(a))
        ]

        vector_2 = [
            c[i] - b[i]
            for i in range(len(a))
        ]


        # --------------------------------------------------
        # Dot Product
        # --------------------------------------------------

        dot_product = sum(
            vector_1[i] * vector_2[i]
            for i in range(len(a))
        )


        magnitude_1 = math.sqrt(
            sum(
                x*x
                for x in vector_1
            )
        )


        magnitude_2 = math.sqrt(
            sum(
                x*x
                for x in vector_2
            )
        )


        # Avoid division by zero

        if magnitude_1 == 0 or magnitude_2 == 0:
            return None


        # --------------------------------------------------
        # Angle Calculation
        # --------------------------------------------------

        cosine_angle = (
            dot_product /
            (magnitude_1 * magnitude_2)
        )


        # Numerical stability

        cosine_angle = max(
            -1.0,
            min(
                1.0,
                cosine_angle
            )
        )


        angle = math.degrees(
            math.acos(cosine_angle)
        )


        return round(angle, 2)


    except Exception as error:

        if debug:
            print(
                f"Angle calculation error: {error}"
            )

        return None



# ==========================================================
# Angle Calculator Class
# ==========================================================

class AngleCalculator:


    def __init__(
        self,
        visibility_threshold: float = 0.40,
        presence_threshold: float = 0.40,
        use_3d: bool = True,
        debug: bool = False
    ):

        self.visibility_threshold = visibility_threshold
        self.presence_threshold = presence_threshold
        self.use_3d = use_3d
        self.debug = debug



    def calculate(
        self,
        landmarks: List[Any]
    ) -> Dict[str, Optional[float]]:


        angles = {

            "left_elbow": None,
            "right_elbow": None,

            "left_shoulder": None,
            "right_shoulder": None,

            "left_hip": None,
            "right_hip": None,

            "left_knee": None,
            "right_knee": None
        }


        # --------------------------------------------------
        # Validate MediaPipe Output
        # --------------------------------------------------

        if (
            landmarks is None
            or len(landmarks) < 33
        ):
            return angles



        def angle(
            a,
            b,
            c
        ):

            return calculate_angle(

                landmarks[
                    LANDMARK_INDEX[a]
                ],

                landmarks[
                    LANDMARK_INDEX[b]
                ],

                landmarks[
                    LANDMARK_INDEX[c]
                ],

                self.visibility_threshold,
                self.presence_threshold,
                self.use_3d,
                self.debug
            )


        # --------------------------------------------------
        # Calculate Joint Angles
        # --------------------------------------------------

        angles["left_elbow"] = angle(
            "left_shoulder",
            "left_elbow",
            "left_wrist"
        )

        angles["right_elbow"] = angle(
            "right_shoulder",
            "right_elbow",
            "right_wrist"
        )


        angles["left_shoulder"] = angle(
            "left_elbow",
            "left_shoulder",
            "left_hip"
        )

        angles["right_shoulder"] = angle(
            "right_elbow",
            "right_shoulder",
            "right_hip"
        )


        angles["left_hip"] = angle(
            "left_shoulder",
            "left_hip",
            "left_knee"
        )

        angles["right_hip"] = angle(
            "right_shoulder",
            "right_hip",
            "right_knee"
        )


        angles["left_knee"] = angle(
            "left_hip",
            "left_knee",
            "left_ankle"
        )

        angles["right_knee"] = angle(
            "right_hip",
            "right_knee",
            "right_ankle"
        )


        return angles
    

"""
test_angle_calculator.py

Test:
Pose Detector + Angle Calculator

Purpose:
---------
Verify that MediaPipe landmarks are correctly
converted into joint angles.
"""


# from pathlib import Path

# from pose_detector import PoseDetector
# from angle_calculator import AngleCalculator
# from dataset_loader import DatasetLoader

# # ==========================================================
# # Configuration
# # ==========================================================

# MODEL_PATH = r"c:\MediaPipe\pose_landmarker_full.task"
# DATASETS_DIR = r"C:\Users\JoudA\OneDrive\سطح المكتب\COOP - JOUD ALSHEHRI\code\datasets"

# # ==========================================================
# # Initialize Modules
# # ==========================================================

# loader = DatasetLoader(DATASETS_DIR)
# detector = PoseDetector(MODEL_PATH)

# calculator = AngleCalculator(
#     visibility_threshold=0.40,
#     presence_threshold=0.40,
#     use_3d=True,
#     debug=True
# )

# # ==========================================================
# # Run Batch Test
# # ==========================================================

# if __name__ == "__main__":
#     print("=" * 60)
#     print("Testing Angle Calculator on ALL Exercises")
#     print("=" * 60)

#     # 1. الحصول على قائمة جميع التمارين
#     # نستخدم get_exercises إذا كانت متوفرة، أو نبحث في المجلدات مباشرة
#     exercises = loader.get_exercises() if hasattr(loader, "get_exercises") else [
#         d.name for d in Path(DATASETS_DIR).iterdir() if d.is_dir()
#     ]

#     try:
#         # 2. المرور على كل تمرين
#         for exercise_name in exercises:
#             print(f"\n\n{'='*60}")
#             print(f"Exercise: {exercise_name.upper()}")
#             print(f"{'='*60}")

#             # 3. جلب مقاطع الفيديو المرجعية الخاصة بالتمرين الحالي
#             ref_videos = loader.get_reference_videos(exercise_name) if hasattr(loader, "get_reference_videos") else list(
#                 (Path(DATASETS_DIR) / exercise_name / "reference").glob("*.*")
#             )

#             if not ref_videos:
#                 print(f"  [!] No reference videos found for {exercise_name}.")
#                 continue

#             # 4. المرور على كل مقطع فيديو داخل التمرين
#             for vid_path in ref_videos:
#                 v_path = Path(vid_path)
#                 print(f"\n  Processing Video: {v_path.name}")
#                 print("  " + "-" * 58)

#                 frame_count = 0

#                 # 5. تحليل الفيديو إطاراً بإطار
#                 for frame in detector.process_video_stream(str(v_path)):
                    
#                     # نستخدم فقط الإطارات التي تم اكتشاف جسم فيها
#                     if not frame.has_pose:
#                         continue

#                     frame_count += 1

#                     # حساب الزوايا باستخدام إحداثيات 3D
#                     angles = calculator.calculate(frame.world_landmarks)

#                     print(f"\n    Frame: {frame.frame_idx}")
#                     for joint, value in angles.items():
#                         print(f"    {joint:15}: {value}")

#                     # اختبار أول 3 إطارات فقط لكل فيديو لتجنب امتلاء الشاشة
#                     # (يمكنك تغيير الرقم إلى 10 أو أي رقم آخر)
#                     if frame_count >= 10:
#                         print(f"\n    [Stopped after {frame_count} frames for {v_path.name}]")
#                         break

#     finally:
#         # التأكد من إغلاق الموديل وتحرير الذاكرة في كل الأحوال
#         detector.close()

#     print("\n" + "=" * 60)
#     print("Batch Test Finished Successfully")
#     print("=" * 60)
