"""
repetition_counter.py

============================================================
Exercise Repetition Counter
============================================================

Pipeline:

Video
  |
Pose Detector
  |
Angle Calculator
  |
Repetition Counter
  |
Final Repetition Count

============================================================
"""


import json
import os
import cv2


from pose_detector import PoseDetector
from angle_calculator import AngleCalculator



# ==========================================================
# Repetition Counter Class
# ==========================================================


class RepetitionCounter:


    def __init__(self, config):

        repetition = config["repetition"]

        self.joint = repetition["tracking_joint"]

        self.start_angle = repetition["start_condition"]["angle"]

        self.bottom_angle = repetition["bottom_condition"]["angle"]

        self.threshold = repetition.get("threshold", 15)

        self.state = "INITIALIZING"

        self.repetitions = 0

        self.initial_angle = None



    def update(self, angles):


        angle = angles.get(
            self.joint
        )


        if angle is None:
            return self.repetitions



        # ==================================================
        # INITIAL CALIBRATION
        # Detect starting position
        # ==================================================

        if self.state == "INITIALIZING":


            if angle >= (
                self.start_angle - self.threshold
            ):

                self.state = "START"

                self.initial_angle = angle


            return self.repetitions



        # ==================================================
        # START -> DOWN
        # Going down
        # ==================================================

        if self.state == "START":


            if angle <= (
                self.bottom_angle + self.threshold
            ):


                self.state = "DOWN"



        # ==================================================
        # DOWN -> START
        # Completed repetition
        # ==================================================

        elif self.state == "DOWN":


            if angle >= (
                self.start_angle - self.threshold
            ):


                self.repetitions += 1

                self.state = "START"



        return self.repetitions



    def get_count(self):

        return self.repetitions

# import os
# import json
# from pathlib import Path

# from pose_detector import PoseDetector
# from angle_calculator import AngleCalculator
# from repetition_counter import RepetitionCounter
# from dataset_loader import DatasetLoader

# # ==========================================================
# # Configuration
# # ==========================================================

# MODEL_PATH = r"C:\MediaPipe\pose_landmarker_full.task"
# DATASETS_DIR = r"C:\Users\JoudA\OneDrive\سطح المكتب\COOP - JOUD ALSHEHRI\code\datasets"

# # ==========================================================
# # TEST (Batch Testing Repetition Counter)
# # ==========================================================

# if __name__ == "__main__":

#     print("=" * 60)
#     print("Testing Repetition Counter on ALL Exercises")
#     print("=" * 60)

#     # 1. تهيئة الـ Loader والـ Detector والـ Calculator
#     loader = DatasetLoader(DATASETS_DIR)
#     detector = PoseDetector(model_path=MODEL_PATH)

#     angle_calculator = AngleCalculator(
#         visibility_threshold=0.40,
#         presence_threshold=0.40,
#         use_3d=True,
#         debug=False
#     )

#     # 2. الحصول على قائمة بجميع التمارين
#     exercises = loader.get_exercises() if hasattr(loader, "get_exercises") else [
#         d.name for d in Path(DATASETS_DIR).iterdir() if d.is_dir()
#     ]

#     try:
#         # 3. المرور على كل تمرين
#         for exercise_name in exercises:
#             exercise_dir = Path(DATASETS_DIR) / exercise_name
#             config_path = exercise_dir / "exercise_config.json"

#             # التحقق من وجود ملف الإعدادات للتمرين الحالي
#             if not config_path.exists():
#                 print(f"\n[Skipping] Config file not found for: {exercise_name}")
#                 continue

#             # قراءة ملف الإعدادات الخاص بالتمرين
#             with open(config_path, "r", encoding="utf-8") as file:
#                 config = json.load(file)

#             print(f"\n\n{'='*60}")
#             print(f"Exercise: {config.get('exercise_name', exercise_name).upper()}")
#             print(f"{'='*60}")

#             # جلب المقاطع المرجعية للتمرين الحالي
#             ref_videos = loader.get_reference_videos(exercise_name) if hasattr(loader, "get_reference_videos") else list(
#                 (exercise_dir / "reference").glob("*.*")
#             )

#             if not ref_videos:
#                 print(f"  [!] No reference videos found for {exercise_name}.")
#                 continue

#             # 4. المرور على كل فيديو مرجعي للتمرين
#             for vid_path in ref_videos:
#                 v_path = Path(vid_path)
#                 print(f"\n  Processing Video: {v_path.name}")
#                 print("  " + "-" * 58)

#                 # إنشاء كائن جديد للعداد مع كل فيديو لصفر التكرارات
#                 counter = RepetitionCounter(config)
#                 frame_count = 0

#                 # 5. معالجة إطارات الفيديو
#                 for pose_data in detector.process_video_stream(str(v_path)):
#                     frame_count += 1

#                     if not pose_data.has_pose or pose_data.world_landmarks is None:
#                         continue

#                     landmarks = pose_data.world_landmarks

#                     # حساب الزوايا
#                     angles = angle_calculator.calculate(landmarks)

#                     tracked_joint_angle = angles.get(counter.joint)

#                     # تحديث العداد
#                     reps = counter.update(angles)

#                     # طباعة حالة كل إطار
#                     print(
#                         f"    Frame: {frame_count:03d} | "
#                         f"{counter.joint}: {tracked_joint_angle} | "
#                         f"State: {counter.state} | "
#                         f"Reps: {reps}"
#                     )

#                 print("  " + "-" * 58)
#                 print(f"  FINAL REP COUNT for [{v_path.name}]: {counter.get_count()}")

#     finally:
#         # إغلاق الموديل وتحرير الذاكرة
#         detector.close()

#     print("\n" + "=" * 60)
#     print("Batch Repetition Counter Test Finished Successfully")
#     print("=" * 60)