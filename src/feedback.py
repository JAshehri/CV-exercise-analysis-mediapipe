"""
feedback.py

============================================================
Feedback Engine
============================================================

Reads the exercise JSON configuration and generates
feedback based on calculated biomechanics.

Current version:
- JSON Loader
- Rule Loader
- Feedback Generator
- Skeleton for future checks
"""

import json
from pathlib import Path


class FeedbackEngine:

    def __init__(self, json_file):

        self.json_file = Path(json_file)

        with open(self.json_file, "r", encoding="utf-8") as f:
            self.exercise = json.load(f)

        self.exercise_name = self.exercise["exercise_name"]

        self.required_landmarks = self.exercise["required_landmarks"]

        self.angle_rules = self.exercise["angle_rules"]

        self.form_errors = self.exercise["form_errors"]

        self.feedback_messages = self.exercise["feedback_messages"]

        self.repetition = self.exercise["repetition"]

        self.movement = self.exercise["movement"]


    # ======================================================
    # Main
    # ======================================================

    def evaluate(self, landmarks, angles):

        result = {
            "score": 100,
            "feedback": [],
            "errors": []
        }

        self.check_required_landmarks(
            landmarks,
            result
        )

        self.check_angles(
            angles,
            result
        )

        self.check_form(
            landmarks,
            angles,
            result
        )

        self.generate_feedback(result)

        return result


    # ======================================================
    # Required landmarks
    # ======================================================

    def check_required_landmarks(
        self,
        landmarks,
        result
    ):

        for lm in self.required_landmarks:

            if lm not in landmarks:

                result["score"] -= 20

                result["errors"].append(
                    f"Missing landmark: {lm}"
                )


    # ======================================================
    # Angle Rules
    # ======================================================

    def check_angles(
        self,
        angles,
        result
    ):

        for rule_name, rule in self.angle_rules.items():

            joint = rule["joint"]

            if joint not in angles:
                continue

            value = angles[joint]
            if value is None:
                continue
            minimum = rule["rom"]["min"]
            maximum = rule["rom"]["max"]

            if value < minimum or value > maximum:

                result["score"] -= 10

                result["errors"].append(
                    f"{joint} angle outside ROM"
                )


    # ======================================================
    # Form Checks
    # ======================================================

    def check_form(
        self,
        landmarks,
        angles,
        result
    ):

        for error_name, rule in self.form_errors.items():

            check = rule.get("check")

            if check == "knee_inside_foot":

                self.check_knee_valgus(
                    landmarks,
                    result,
                    rule
                )

            elif check == "hip_shoulder_alignment":

                self.check_back_posture(
                    landmarks,
                    result,
                    rule
                )

            elif error_name == "insufficient_depth":

                self.check_depth(
                    angles,
                    result,
                    rule
                )


    # ======================================================
    # Future implementations
    # ======================================================

    def check_knee_valgus(
        self,
        landmarks,
        result,
        rule
    ):
        """
        TODO

        Will use x coordinates
        Knee vs Foot alignment

        """
        pass


    def check_back_posture(
        self,
        landmarks,
        result,
        rule
    ):
        """
        TODO

        Shoulder-Hip alignment

        """
        pass


    def check_depth(
        self,
        angles,
        result,
        rule
    ):
        """
        TODO

        Knee angle threshold

        """
        pass


    # ======================================================
    # Feedback
    # ======================================================

    def generate_feedback(
        self,
        result
    ):

        if len(result["errors"]) == 0:

            result["feedback"].append(

                self.feedback_messages["good_rep"][0]

            )

        else:

            for error in result["errors"]:

                result["feedback"].append(error)


# # ==========================================================
# # Test
# # ==========================================================
# from pathlib import Path
# from dataset_loader import DatasetLoader
# from feedback import FeedbackEngine

# # ==========================================================
# # Configuration
# # ==========================================================

# DATASETS_DIR = r"C:\Users\JoudA\OneDrive\سطح المكتب\COOP - JOUD ALSHEHRI\code\datasets"

# # ==========================================================
# # TEST (Batch Testing Feedback Engine Configs)
# # ==========================================================

# if __name__ == "__main__":

#     print("=" * 60)
#     print("Testing Feedback Engine Configs on ALL Exercises")
#     print("=" * 60)

#     # 1. تهيئة الـ Loader لجلب قائمة التمارين
#     loader = DatasetLoader(DATASETS_DIR)

#     # 2. الحصول على قائمة بجميع التمارين
#     exercises = loader.get_exercises() if hasattr(loader, "get_exercises") else [
#         d.name for d in Path(DATASETS_DIR).iterdir() if d.is_dir()
#     ]

#     if not exercises:
#         print("[!] No exercises found in the dataset directory.")
#     else:
#         # 3. المرور على كل تمرين وقراءة ملف الإعدادات الخاص به
#         for exercise_name in exercises:
#             exercise_dir = Path(DATASETS_DIR) / exercise_name
#             json_path = exercise_dir / "exercise_config.json"

#             # التحقق من وجود ملف الإعدادات
#             if not json_path.exists():
#                 print(f"\n[Skipping] exercise_config.json not found for: {exercise_name}")
#                 continue

#             # تهيئة الـ FeedbackEngine باستخدام مسار الملف للتمارين الحالية
#             engine = FeedbackEngine(str(json_path))

#             print(f"\n\n{'='*60}")
#             print(f"Exercise Name: {getattr(engine, 'exercise_name', exercise_name).upper()}")
#             print(f"{'='*60}")

#             # طباعة النقاط/المعالم المطلوبة (Required Landmarks)
#             print("\n  [Required Landmarks]")
#             required_lms = getattr(engine, "required_landmarks", [])
#             if required_lms:
#                 for lm in required_lms:
#                     print(f"    - {lm}")
#             else:
#                 print("    - None specified")

#             # طباعة قواعد الزوايا (Angle Rules)
#             print("\n  [Angle Rules]")
#             angle_rules = getattr(engine, "angle_rules", {})
#             if angle_rules:
#                 for name, rule in angle_rules.items():
#                     print(f"    - {name:<20}: {rule}")
#             else:
#                 print("    - None specified")

#             # طباعة أخطاء الأداء (Form Errors)
#             print("\n  [Form Errors]")
#             form_errors = getattr(engine, "form_errors", {})
#             if form_errors:
#                 for name, rule in form_errors.items():
#                     print(f"    - {name:<20}: {rule}")
#             else:
#                 print("    - None specified")

#     print("\n" + "=" * 60)
#     print("Batch Feedback Engine Test Finished Successfully")
#     print("=" * 60)
