"""
feature_extraction.py

============================================================
Motion Feature Extraction Module
============================================================

Purpose:
--------
Convert pose and joint angle sequences into biomechanical
features used for exercise analysis.

Extracted Features:
-------------------
- Range of Motion (ROM)
- Angle Statistics
- Angular Velocity
- Movement Direction
- Movement Speed
- Body Stability
- Landmark Confidence Score
- Landmark Trajectory
- Exercise Duration
"""

import math
import statistics
from typing import Dict, List, Optional, Any


class FeatureExtractor:

    def __init__(self, fps: float = 30):

        """
        Parameters:
        -----------
        fps:
            Video frame rate
        """

        self.fps = fps


    # ======================================================
    # Angle Features
    # ======================================================

    def calculate_rom(
        self,
        angles: List[float]
    ) -> Optional[float]:

        """
        Range Of Motion

        ROM = Maximum Angle - Minimum Angle
        """

        values = [
            x for x in angles
            if x is not None
        ]

        if len(values) < 2:
            return None


        return round(
            max(values) - min(values),
            2
        )


    def angle_statistics(
        self,
        angles: List[float]
    ) -> Dict[str, Optional[float]]:

        """
        Calculate minimum,
        maximum and average angle
        """

        values = [
            x for x in angles
            if x is not None
        ]


        if not values:
            return {
                "min": None,
                "max": None,
                "average": None
            }


        return {

            "min":
                round(min(values),2),

            "max":
                round(max(values),2),

            "average":
                round(
                    statistics.mean(values),
                    2
                )
        }



    # ======================================================
    # Speed Features
    # ======================================================

    def calculate_velocity(
        self,
        angles: List[float]
    ) -> List[Optional[float]]:

        """
        Angular velocity

        degree / second
        """

        velocity = []

        dt = 1 / self.fps


        for i in range(1,len(angles)):


            if (
                angles[i] is None or
                angles[i-1] is None
            ):
                velocity.append(None)
                continue


            delta = (
                angles[i]
                -
                angles[i-1]
            )


            velocity.append(
                round(
                    delta / dt,
                    2
                )
            )


        return velocity



    def movement_speed(
        self,
        velocity: List[float]
    ) -> Dict[str,Optional[float]]:

        """
        Calculate average and maximum speed
        """

        values = [
            abs(v)
            for v in velocity
            if v is not None
        ]


        if not values:
            return {
                "average_speed":None,
                "max_speed":None
            }


        return {

            "average_speed":
                round(
                    statistics.mean(values),
                    2
                ),

            "max_speed":
                round(
                    max(values),
                    2
                )
        }



    # ======================================================
    # Movement Direction
    # ======================================================

    def movement_direction(
        self,
        angles: List[float]
    ) -> Optional[str]:

        """
        Detect general movement direction
        """

        values = [
            x for x in angles
            if x is not None
        ]


        if len(values)<2:
            return None


        if values[-1] > values[0]:

            return "increasing"

        elif values[-1] < values[0]:

            return "decreasing"


        return "stable"



    # ======================================================
    # Stability
    # ======================================================

    def calculate_stability(
        self,
        values: List[float]
    ) -> Optional[float]:

        """
        Lower deviation = better stability
        """

        values = [
            x for x in values
            if x is not None
        ]


        if len(values)<2:
            return None


        deviation = statistics.stdev(values)


        return round(
            deviation,
            2
        )



    # ======================================================
    # Landmark Confidence
    # ======================================================

    def calculate_confidence(
        self,
        landmarks_frames: List[List[Any]]
    ) -> Dict[str,float]:

        """
        Calculate average landmark confidence
        using visibility and presence
        """


        scores=[]


        for frame in landmarks_frames:

            for point in frame:


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


                score = (
                    visibility
                    +
                    presence
                ) / 2


                scores.append(score)



        if not scores:

            return {

                "average_confidence":0,
                "low_confidence_points":0

            }


        low = len(
            [
                x for x in scores
                if x < 0.4
            ]
        )


        return {

            "average_confidence":
                round(
                    statistics.mean(scores),
                    3
                ),

            "low_confidence_points":
                low
        }



    # ======================================================
    # Landmark Trajectory
    # ======================================================

    def calculate_trajectory(
        self,
        landmark_sequence: List[Any]
    ) -> Optional[float]:

        """
        Total landmark movement distance
        """

        if len(landmark_sequence)<2:
            return None


        distance=0


        for i in range(1,len(landmark_sequence)):


            p1 = landmark_sequence[i-1]
            p2 = landmark_sequence[i]


            dx=p2.x-p1.x
            dy=p2.y-p1.y
            dz=getattr(p2,"z",0)-getattr(p1,"z",0)


            distance += math.sqrt(
                dx**2+
                dy**2+
                dz**2
            )


        return round(
            distance,
            4
        )



    # ======================================================
    # Duration
    # ======================================================

    def calculate_duration(
        self,
        total_frames:int
    ) -> float:

        """
        Exercise duration in seconds
        """

        return round(
            total_frames / self.fps,
            2
        )



    # ======================================================
    # Main Feature Extraction
    # ======================================================

    def extract_features(
        self,
        angle_sequence: Dict[str,List[float]],
        total_frames:int,
        landmarks_frames=None
    ) -> Dict:


        features={}


        # Duration

        features["exercise_duration"] = (
            self.calculate_duration(
                total_frames
            )
        )


        # Angles

        features["joint_features"]={}


        for joint,angles in angle_sequence.items():


            velocity = (
                self.calculate_velocity(
                    angles
                )
            )


            features["joint_features"][joint]={


                "rom":
                    self.calculate_rom(
                        angles
                    ),


                "statistics":
                    self.angle_statistics(
                        angles
                    ),


                "movement_direction":
                    self.movement_direction(
                        angles
                    ),


                "velocity":
                    velocity,


                "speed":
                    self.movement_speed(
                        velocity
                    ),


                "stability":
                    self.calculate_stability(
                        angles
                    )
            }



        # Confidence

        if landmarks_frames:

            features["confidence"] = (
                self.calculate_confidence(
                    landmarks_frames
                )
            )


        return features


# ==========================================================
# Test
# ==========================================================
# import cv2
# from pathlib import Path

# from pose_detector import PoseDetector
# from angle_calculator import AngleCalculator
# from feature_extraction import FeatureExtractor
# from dataset_loader import DatasetLoader

# # ==========================================================
# # Configuration
# # ==========================================================

# MODEL_PATH = r"C:\MediaPipe\pose_landmarker_full.task"
# DATASETS_DIR = r"C:\Users\JoudA\OneDrive\سطح المكتب\COOP - JOUD ALSHEHRI\code\datasets"

# # ==========================================================
# # TEST (Batch Testing Feature Extraction Pipeline)
# # ==========================================================

# if __name__ == "__main__":

#     print("=" * 60)
#     print("Testing Full Feature Extraction Pipeline on ALL Exercises")
#     print("=" * 60)

#     # ======================================================
#     # Initialize Modules
#     # ======================================================
#     print("\nLoading Modules...")
    
#     loader = DatasetLoader(DATASETS_DIR)
    
#     pose_detector = PoseDetector(model_path=MODEL_PATH)
    
#     angle_calculator = AngleCalculator(
#         visibility_threshold=0.40,
#         presence_threshold=0.40,
#         use_3d=True,
#         debug=False
#     )
    
#     feature_extractor = FeatureExtractor(fps=30)

#     # 1. الحصول على قائمة جميع التمارين
#     exercises = loader.get_exercises() if hasattr(loader, "get_exercises") else [
#         d.name for d in Path(DATASETS_DIR).iterdir() if d.is_dir()
#     ]

#     try:
#         # 2. المرور على كل تمرين
#         for exercise_name in exercises:
#             print(f"\n\n{'='*130}")
#             print(f"Exercise: {exercise_name.upper()}")
#             print(f"{'='*130}")

#             # جلب مقاطع الفيديو المرجعية
#             ref_videos = loader.get_reference_videos(exercise_name) if hasattr(loader, "get_reference_videos") else list(
#                 (Path(DATASETS_DIR) / exercise_name / "reference").glob("*.*")
#             )

#             if not ref_videos:
#                 print(f"  [!] No reference videos found for {exercise_name}.")
#                 continue

#             # 3. المرور على كل فيديو مرجعي
#             for vid_path in ref_videos:
#                 v_path = Path(vid_path)
                
#                 # ======================================================
#                 # Video Information
#                 # ======================================================
#                 cap = cv2.VideoCapture(str(v_path))
#                 if not cap.isOpened():
#                     print(f"  [!] Cannot open video: {v_path.name}")
#                     continue

#                 total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#                 fps = cap.get(cv2.CAP_PROP_FPS)

#                 if fps and fps > 0:
#                     feature_extractor.fps = fps
#                 else:
#                     fps = 30.0

#                 cap.release()

#                 print(f"\n  Processing Video: {v_path.name} | Total Frames: {total_frames} | FPS: {fps:.2f}")
#                 print("  " + "-" * 128)

#                 # ======================================================
#                 # Storage Storage (إعادة تصفير المتغيرات لكل فيديو)
#                 # ======================================================
#                 angle_sequence = {
#                     "left_elbow": [], "right_elbow": [],
#                     "left_shoulder": [], "right_shoulder": [],
#                     "left_hip": [], "right_hip": [],
#                     "left_knee": [], "right_knee": []
#                 }
                
#                 landmarks_frames = []
#                 successful_frames = 0

#                 # ======================================================
#                 # Process Video Frames
#                 # ======================================================
#                 for pose_data in pose_detector.process_video_stream(str(v_path)):
#                     if not pose_data.has_pose:
#                         continue

#                     landmarks = pose_data.world_landmarks
#                     if landmarks is None:
#                         continue

#                     # حساب الزوايا
#                     angles = angle_calculator.calculate(landmarks)

#                     for joint, value in angles.items():
#                         if joint in angle_sequence:
#                             angle_sequence[joint].append(value)

#                     landmarks_frames.append(landmarks)
#                     successful_frames += 1

#                     # 💡 نكتفي بـ 30 إطاراً لكل فيديو لتسريع الاختبار
#                     if successful_frames >= 30:
#                         break

#                 if successful_frames == 0:
#                     print("    [!] No successful frames processed.")
#                     continue

#                 # ======================================================
#                 # Feature Extraction
#                 # ======================================================
#                 features = feature_extractor.extract_features(
#                     angle_sequence=angle_sequence,
#                     total_frames=total_frames,
#                     landmarks_frames=landmarks_frames
#                 )

#                 # ======================================================
#                 # Print Feature Table
#                 # ======================================================
#                 print(f"\n    {'Joint':<18}{'ROM':<10}{'Min':<10}{'Max':<10}{'Average':<12}{'Direction':<15}{'Avg Speed':<12}{'Max Speed':<12}{'Stability':<10}")
#                 print("    " + "-" * 126)

#                 for joint, data in features["joint_features"].items():
#                     stats = data["statistics"]
#                     speed = data["speed"]
                    
#                     print(
#                         f"    {joint:<18}"
#                         f"{str(data['rom']):<10}"
#                         f"{str(stats['min']):<10}"
#                         f"{str(stats['max']):<10}"
#                         f"{str(stats['average']):<12}"
#                         f"{str(data['movement_direction']):<15}"
#                         f"{str(speed['average_speed']):<12}"
#                         f"{str(speed['max_speed']):<12}"
#                         f"{str(data['stability']):<10}"
#                     )

#                 # ======================================================
#                 # Other Features (Global)
#                 # ======================================================
#                 print(f"\n    [Global Features]")
#                 print(f"    - Exercise Duration : {features['exercise_duration']} sec (Based on Processed Frames)")
                
#                 if "confidence" in features:
#                     print(f"    - Average Confidence: {features['confidence']['average_confidence']}")
#                     print(f"    - Low Conf. Points  : {features['confidence']['low_confidence_points']}")

#     finally:
#         pose_detector.close()

#     print("\n\n" + "=" * 60)
#     print("Batch Feature Extraction Pipeline Test Finished Successfully")
#     print("=" * 60)