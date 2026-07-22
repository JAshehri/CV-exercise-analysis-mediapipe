"""
pose_detector.py
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Iterator

import cv2

# ==========================================================
# دالة كتم تحذيرات C++ النابعة من MediaPipe / TFLite
# ==========================================================
def suppress_stderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    os.dup2(devnull, 2)
    os.close(devnull)
    return old_stderr

def restore_stderr(old_stderr):
    os.dup2(old_stderr, 2)
    os.close(old_stderr)

# تفعيل الكتم قبل استيراد Mediapipe
old_stderr = suppress_stderr()

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# استعادة الـ stderr العادي بعد الانتهاء من الاستيراد والتهيئة
restore_stderr(old_stderr)

os.environ["GLOG_minloglevel"] = "2"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

try:
    from dataset_loader import DatasetLoader
except ImportError:
    DatasetLoader = None


# أسماء الـ Landmarks الـ 33 الخاصة بـ MediaPipe
LANDMARK_NAMES = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer",
    "right_eye_inner", "right_eye", "right_eye_outer",
    "left_ear", "right_ear", "mouth_left", "mouth_right",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_pinky", "right_pinky",
    "left_index", "right_index", "left_thumb", "right_thumb",
    "left_hip", "right_hip", "left_knee", "right_knee",
    "left_ankle", "right_ankle", "left_heel", "right_heel",
    "left_foot_index", "right_foot_index",
]


@dataclass(slots=True)
class PoseFrameData:
    frame_idx: int
    timestamp_ms: int
    landmarks: Optional[Any]
    world_landmarks: Optional[Any]
    avg_visibility: float
    min_visibility: float
    has_pose: bool


class PoseDetector:
    def __init__(self, model_path: str):
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found:\n{model_path}")

        with open(model_path, "rb") as file:
            self.model_bytes = file.read()

        self.detector = None
        self._init_detector()

    def _init_detector(self):
        if self.detector is not None:
            try:
                self.detector.close()
            except Exception:
                pass

        # كتم رسائل C++ أثناء بناء الموديل
        old_err = suppress_stderr()
        try:
            base_options = python.BaseOptions(model_asset_buffer=self.model_bytes)
            options = vision.PoseLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.VIDEO,
                num_poses=1
            )
            self.detector = vision.PoseLandmarker.create_from_options(options)
        finally:
            restore_stderr(old_err)

    def process_video_stream(self, video_path: str) -> Iterator[PoseFrameData]:
        self._init_detector()

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video:\n{video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30.0

        frame_idx = 0
        last_timestamp_ms = -1

        try:
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break

                timestamp_ms = int(frame_idx / fps * 1000)
                if timestamp_ms <= last_timestamp_ms:
                    timestamp_ms = last_timestamp_ms + 1
                last_timestamp_ms = timestamp_ms

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

                # كتم رسائل C++ أثناء التتبع (Inference)
                old_err = suppress_stderr()
                try:
                    result = self.detector.detect_for_video(mp_image, timestamp_ms)
                finally:
                    restore_stderr(old_err)

                if result.pose_landmarks and len(result.pose_landmarks[0]) == 33:
                    image_landmarks = result.pose_landmarks[0]
                    world_landmarks = (
                        result.pose_world_landmarks[0]
                        if result.pose_world_landmarks
                        else None
                    )
                    visibility = [lm.visibility for lm in image_landmarks]
                    avg_visibility = sum(visibility) / len(visibility)
                    min_visibility = min(visibility)

                    has_pose = avg_visibility >= 0.40 and min_visibility >= 0.05

                    yield PoseFrameData(
                        frame_idx=frame_idx,
                        timestamp_ms=timestamp_ms,
                        landmarks=image_landmarks,
                        world_landmarks=world_landmarks,
                        avg_visibility=float(avg_visibility),
                        min_visibility=float(min_visibility),
                        has_pose=has_pose
                    )
                else:
                    yield PoseFrameData(
                        frame_idx=frame_idx,
                        timestamp_ms=timestamp_ms,
                        landmarks=None,
                        world_landmarks=None,
                        avg_visibility=0.0,
                        min_visibility=0.0,
                        has_pose=False
                    )

                frame_idx += 1
        finally:
            cap.release()
    def detect(self, frame):
        """
        Detect pose landmarks from a single OpenCV frame.

        Args:
            frame:
                OpenCV BGR image

        Returns:
            Pose landmarks or None
        """

        if self.detector is None:
            self._init_detector()

        # تحويل BGR -> RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        old_err = suppress_stderr()

        try:
            result = self.detector.detect(mp_image)

        finally:
            restore_stderr(old_err)


        if result.pose_landmarks:

            landmarks = result.pose_landmarks[0]

            if len(landmarks) == 33:
                return landmarks


        return None
    def close(self):
        if self.detector is not None:
            self.detector.close()


def print_table(title: str, headers: list[str], rows: list[list[str]]):
    print(f"\n📌 {title}")
    if not rows:
        print("   (No data available)")
        return

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    header_str = " | ".join(f"{headers[i]:<{col_widths[i]}}" for i in range(len(headers)))
    separator = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

    print("+" + "-" * (len(header_str) + 2) + "+")
    print(f"| {header_str} |")
    print("+" + separator + "+")

    for row in rows:
        row_str = " | ".join(f"{str(row[i]):<{col_widths[i]}}" for i in range(len(row)))
        print(f"| {row_str} |")
    print("+" + "-" * (len(header_str) + 2) + "+")


# # ==========================================================
# # Test
# # ==========================================================

# if __name__ == "__main__":
#     MODEL_PATH = r"c:\MediaPipe\pose_landmarker_full.task"
#     DATASETS_DIR = r"C:\Users\JoudA\OneDrive\سطح المكتب\COOP - JOUD ALSHEHRI\code\datasets"

#     detector = PoseDetector(MODEL_PATH)

#     if DatasetLoader is None:
#         raise ImportError("Could not import `DatasetLoader`.")

#     loader = DatasetLoader(DATASETS_DIR)
#     exercises = loader.get_exercise_names() if hasattr(loader, "get_exercise_names") else [d.name for d in Path(DATASETS_DIR).iterdir() if d.is_dir()]

#     summary_rows = []

#     try:
#         for exercise_name in exercises:
#             ref_videos = loader.get_reference_videos(exercise_name) if hasattr(loader, "get_reference_videos") else list((Path(DATASETS_DIR) / exercise_name / "reference").glob("*.*"))

#             table_rows = []
#             ex_total_frames = 0
#             ex_detected_frames = 0

#             for vid_path in ref_videos:
#                 v_path = Path(vid_path)
#                 v_total, v_detected = 0, 0
                
#                 xyz_rows = []
#                 for frame in detector.process_video_stream(str(v_path)):
#                     v_total += 1
#                     if frame.has_pose:
#                         v_detected += 1
                        
#                         # تجميع إحداثيات (X, Y, Z) للـ World Landmarks
#                         if frame.world_landmarks:
#                             for idx in [0, 11, 12, 23, 24]: # Nose, Left/Right Shoulder, Left/Right Hip
#                                 lm_name = LANDMARK_NAMES[idx]
#                                 lm_obj = frame.world_landmarks[idx]
#                                 xyz_rows.append([str(v_path.name), str(frame.frame_idx), lm_name, f"{lm_obj.x:.3f}", f"{lm_obj.y:.3f}", f"{lm_obj.z:.3f}"])

#                 rate = (v_detected / v_total * 100) if v_total > 0 else 0.0
#                 table_rows.append(["Reference", v_path.name, str(v_total), str(v_detected), f"{rate:.1f}%"])
                
#                 ex_total_frames += v_total
#                 ex_detected_frames += v_detected

#                 # طباعة جدول إحداثيات XYZ لكل فيديو (أول 10 عينات كمثال)
#                 if xyz_rows:
#                     xyz_headers = ["Video Name", "Frame", "Landmark", "X", "Y", "Z"]
#                     print_table(f"XYZ Coordinates Sample for [{v_path.name}]", xyz_headers, xyz_rows[:10])

#             headers = ["Category", "Video Name", "Total Frames", "Detected Frames", "Accuracy"]
#             print_table(f"Results for [{exercise_name}] (References Only)", headers, table_rows)

#             ex_rate = (ex_detected_frames / ex_total_frames * 100) if ex_total_frames > 0 else 0.0
#             summary_rows.append([exercise_name, str(len(ref_videos)), str(ex_total_frames), str(ex_detected_frames), f"{ex_rate:.1f}%"])

#         headers_summary = ["Exercise Name", "Ref Videos Count", "Total Frames", "Detected Frames", "Avg Accuracy"]
#         print_table("OVERALL BATCH SUMMARY", headers_summary, summary_rows)

#     finally:
#         detector.close()
