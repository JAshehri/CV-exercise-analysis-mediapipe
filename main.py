import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))
from dataset_loader import DatasetLoader
from pose_detector import PoseDetector, LANDMARK_NAMES
from angle_calculator import AngleCalculator
from feature_extraction import FeatureExtractor
from repetition_counter import RepetitionCounter
from feedback import FeedbackEngine
import json
import cv2

# ==========================================================
# Project Constants
# ==========================================================

MODEL_PATH = Path(r"C:\MediaPipe\pose_landmarker_full.task")

DATASET_ROOT = Path(
    r"C:\Users\JoudA\OneDrive\سطح المكتب\COOP - JOUD ALSHEHRI\code\datasets"
)


# ==========================================================
# Helper Functions
# ==========================================================

def choose_from_list(title: str, items: list[str]) -> str:
    print(f"\n{title}")
    print("-" * 60)

    for idx, item in enumerate(items, start=1):
        print(f"{idx}. {item}")

    while True:
        choice = input("\nEnter the number: ").strip()

        if not choice.isdigit():
            print("Invalid choice, please try again.")
            continue

        index = int(choice) - 1

        if 0 <= index < len(items):
            return items[index]

        print("Number out of range, please try again.")


def landmarks_to_dict(landmarks):
    """
    Converts MediaPipe landmarks list to dict:
    {
        "nose": landmark_obj,
        "left_shoulder": landmark_obj,
        ...
    }
    """
    result = {}

    if landmarks is None:
        return result

    count = min(len(LANDMARK_NAMES), len(landmarks))

    for i in range(count):
        result[LANDMARK_NAMES[i]] = landmarks[i]

    return result


def print_joint_features_table(features: dict):
    print("\n")
    print("=" * 130)
    print("JOINT FEATURES TABLE")
    print("=" * 130)

    print(
        f"{'Joint':<18}"
        f"{'ROM':<10}"
        f"{'Min':<10}"
        f"{'Max':<10}"
        f"{'Average':<12}"
        f"{'Direction':<15}"
        f"{'Avg Speed':<12}"
        f"{'Max Speed':<12}"
        f"{'Stability':<10}"
    )

    print("-" * 130)

    for joint, data in features["joint_features"].items():
        stats = data["statistics"]
        speed = data["speed"]

        print(
            f"{joint:<18}"
            f"{str(data['rom']):<10}"
            f"{str(stats['min']):<10}"
            f"{str(stats['max']):<10}"
            f"{str(stats['average']):<12}"
            f"{str(data['movement_direction']):<15}"
            f"{str(speed['average_speed']):<12}"
            f"{str(speed['max_speed']):<12}"
            f"{str(data['stability']):<10}"
        )


# ==========================================================
# Main
# ==========================================================

def main():
    print("=" * 60)
    print("Exercise Analysis Pipeline")
    print("=" * 60)

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found:\n{MODEL_PATH}")

    if not DATASET_ROOT.exists():
        raise FileNotFoundError(f"Dataset root not found:\n{DATASET_ROOT}")

    loader = DatasetLoader(DATASET_ROOT)

    exercises = loader.get_exercises()
    if not exercises:
        raise ValueError("No exercises found in dataset root.")

    # ------------------------------------------------------
    # 1) User selects exercise
    # ------------------------------------------------------
    exercise_name = choose_from_list(
        "Choose the exercise name",
        exercises
    )

    exercise_folder = DATASET_ROOT / exercise_name
    config_path = exercise_folder / "exercise_config.json"

    if not config_path.exists():
        raise FileNotFoundError(
            f"exercise_config.json not found:\n{config_path}"
        )

    # ------------------------------------------------------
    # 2) User selects video source
    # ------------------------------------------------------
    source_choice = choose_from_list(
        "Choose the video type",
        ["reference", "user"]
    )

    if source_choice == "reference":
        videos = loader.get_reference_videos(exercise_name)
    else:
        videos = loader.get_user_videos(exercise_name)

    if not videos:
        raise ValueError(
            f"No videos found for exercise '{exercise_name}' in '{source_choice}'."
        )

    video_names = [Path(v).name for v in videos]

    selected_video_name = choose_from_list(
        f"Choose a video from {source_choice}",
        video_names
    )

    video_path = Path(videos[video_names.index(selected_video_name)])

    # ------------------------------------------------------
    # 3) Load exercise config
    # ------------------------------------------------------
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    print("\nSelected Exercise:", exercise_name)
    print("Selected Video   :", video_path.name)
    print("Config Path      :", config_path)

    # ------------------------------------------------------
    # 4) Initialize modules
    # ------------------------------------------------------
    print("\nLoading Pose Detector...")
    pose_detector = PoseDetector(str(MODEL_PATH))

    print("Loading Angle Calculator...")
    angle_calculator = AngleCalculator(
        visibility_threshold=0.40,
        presence_threshold=0.40,
        use_3d=True,
        debug=False
    )

    print("Loading Feature Extractor...")
    feature_extractor = FeatureExtractor(fps=30.0)

    print("Loading Repetition Counter...")
    repetition_counter = RepetitionCounter(config)

    print("Loading Feedback Engine...")
    feedback_engine = FeedbackEngine(str(config_path))

    # ------------------------------------------------------
    # 5) Video information
    # ------------------------------------------------------
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise Exception(f"Cannot open video:\n{video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps and fps > 0:
        feature_extractor.fps = fps
    else:
        fps = 30.0

    cap.release()

    print("\nVideo Information")
    print("-" * 60)
    print(f"Total Frames : {total_frames}")
    print(f"FPS          : {fps}")

    # ------------------------------------------------------
    # 6) Storage
    # ------------------------------------------------------
    template_angles = angle_calculator.calculate(None)

    angle_sequence = {
        joint: []
        for joint in template_angles.keys()
    }

    landmarks_frames = []

    detected_frames = 0

    best_landmarks_dict = None
    best_angles = None
    best_frame_idx = None
    best_tracked_angle = None

    last_valid_landmarks_dict = None
    last_valid_angles = None

    # ------------------------------------------------------
    # 7) Process video
    # ------------------------------------------------------
    print("\nProcessing Video...")
    print("-" * 60)

    try:
        for pose_data in pose_detector.process_video_stream(str(video_path)):

            if not pose_data.has_pose:
                continue

            landmarks = pose_data.world_landmarks
            if landmarks is None:
                continue

            # Angles from AngleCalculator
            angles = angle_calculator.calculate(landmarks)

            # Store angle sequence
            for joint, value in angles.items():
                angle_sequence[joint].append(value)

            # Store landmarks frames for confidence
            landmarks_frames.append(landmarks)
            detected_frames += 1

            # Update repetition counter
            repetition_counter.update(angles)

            # Convert landmarks to dict for feedback engine
            landmarks_dict = landmarks_to_dict(landmarks)

            tracked_joint = repetition_counter.joint
            tracked_angle = angles.get(tracked_joint)

            last_valid_landmarks_dict = landmarks_dict
            last_valid_angles = angles

            # Choose the best frame for feedback:
            # the frame with the minimum tracked angle (deepest point)
            if tracked_angle is not None:
                if best_tracked_angle is None or tracked_angle < best_tracked_angle:
                    best_tracked_angle = tracked_angle
                    best_landmarks_dict = landmarks_dict
                    best_angles = angles
                    best_frame_idx = pose_data.frame_idx

    finally:
        pose_detector.close()

    # ------------------------------------------------------
    # 8) Feature extraction
    # ------------------------------------------------------
    print("\n")
    print("=" * 60)
    print("Extracting Features...")
    print("=" * 60)

    features = feature_extractor.extract_features(
        angle_sequence=angle_sequence,
        total_frames=total_frames,
        landmarks_frames=landmarks_frames
    )

    # ------------------------------------------------------
    # 9) Feedback evaluation
    # ------------------------------------------------------
    if best_landmarks_dict is None:
        best_landmarks_dict = last_valid_landmarks_dict or {}
        best_angles = last_valid_angles or {}
        best_frame_idx = best_frame_idx if best_frame_idx is not None else -1

    feedback_result = feedback_engine.evaluate(
        best_landmarks_dict,
        best_angles
    )

    # ------------------------------------------------------
    # 10) Print results
    # ------------------------------------------------------
    print("\n")
    print("=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)

    print(f"Exercise         : {exercise_name}")
    print(f"Video            : {video_path.name}")
    print(f"Detected Frames  : {detected_frames}")
    print(f"Total Frames     : {total_frames}")
    print(f"FPS              : {fps}")
    print(f"Repetitions      : {repetition_counter.get_count()}")
    print(f"Feedback Frame   : {best_frame_idx}")

    print("\n")
    print("=" * 60)
    print("FEEDBACK")
    print("=" * 60)

    print(f"Score: {feedback_result['score']}")
    print("Errors:")
    if feedback_result["errors"]:
        for err in feedback_result["errors"]:
            print("-", err)
    else:
        print("- None")

    print("Messages:")
    if feedback_result["feedback"]:
        for msg in feedback_result["feedback"]:
            print("-", msg)
    else:
        print("- None")

    # Optional feature table
    print_joint_features_table(features)

    print("\n")
    print("=" * 60)
    print("Pipeline Test Finished Successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()
