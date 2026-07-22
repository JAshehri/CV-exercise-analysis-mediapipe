# CV-Based Exercise Analysis Using MediaPipe BlazePose & Rule-Based Evaluation

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-BlazePose-orange.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg)
![Architecture](https://img.shields.io/badge/Architecture-Modular%20%26%20Config--Driven-purple.svg)

**Author:** Joud Ali Alshehri  

---

## Introduction

This repository contains a **Computer Vision-based Exercise Analysis System** designed to automatically evaluate human exercise performance from pre-recorded videos. Powered by **MediaPipe BlazePose**, the pipeline estimates 3D body landmarks, computes joint angles, extracts detailed motion features, counts repetitions dynamically, and generates personalized, rule-based feedback.

The system features a **modular, configuration-driven architecture**. All exercise-specific thresholds, joint targets, and form evaluation rules are stored in external JSON files (`exercise_config.json`). This allows new exercises to be added seamlessly without modifying the core implementation.

---

## Project Objectives

* **3D Pose Estimation:** Detect human body poses and extract 33 spatial $3D$ world coordinates $(X, Y, Z)$ using MediaPipe BlazePose.
* **Joint Angle Calculation:** Measure major joint angles (elbows, shoulders, hips, knees) across exercise frames.
* **Biomechanical Feature Extraction:** Summarize movement characteristics using Range of Motion (ROM), angular speeds, movement direction, and stability metrics.
* **Dynamic Repetition Counting:** Automatically track and count completed reps based on exercise-specific JSON rules.
* **Rule-Based Performance Evaluation:** Compare user execution against target thresholds to calculate an overall performance score and detect form errors.
* **Extensible & Scalable Design:** Support multiple upper-body and lower-body exercises via modular JSON configurations.

---

## Project Structure

```text
code/
│── main.py
│
├── datasets/
│   ├── air_squat/
│   ├── back_squat/
│   ├── pushup/
│   ├── easy_pushup/
│   ├── cross_knee_plank/
│   └── marching_plank/
│
└── src/
    ├── pose_detector.py
    ├── angle_calculator.py
    ├── feature_extraction.py
    ├── repetition_counter.py
    ├── feedback.py
    └── dataset_loader.py

```

---

## Module Overview

| Module | Primary Responsibility |
| --- | --- |
| **`DatasetLoader`** | Discovers available exercises, organizes reference/user video paths, and loads corresponding `exercise_config.json` files. |
| **`PoseDetector`** | Processes video streams frame-by-frame using MediaPipe BlazePose to detect 33 $3D$ world landmarks. |
| **`AngleCalculator`** | Computes 3D joint angles for key anatomical joints (elbows, shoulders, hips, knees). |
| **`FeatureExtractor`** | Extracts movement features: Range of Motion (ROM), Min/Max/Avg angles, angular speed, direction, and stability. |
| **`RepetitionCounter`** | Tracks state transitions of target joint angles to accurately count completed repetitions. |
| **`FeedbackEngine`** | Evaluates posture against configurable rules, computes a performance score, identifies form errors, and highlights the best evaluation frame. |

---

## Dataset & Configuration Structure

Each supported exercise resides in its own isolated dataset directory containing video assets and configuration rules:

```text
exercise_folder/
│── reference/          # Benchmark/correct execution videos
│── user/               # User-submitted test videos
└── exercise_config.json# Dynamic rules, landmark definitions & thresholds

```

### `exercise_config.json` Scope:

* Exercise name, category, target muscles, and required camera angle.
* Required landmark indices and target joint angle formulas.
* Expected Range of Motion (ROM) and threshold limits.
* Repetition counting state machine conditions.
* Form error definitions and corresponding user feedback messages.

---

## Currently Supported Exercises

1. **Air Squat** *(Lower Body)*
2. **Back Squat** *(Lower Body)*
3. **Push-up** *(Upper Body)*
4. **Easy Push-up** *(Upper Body)*
5. **Cross Knee Plank** *(Core / Stability)*
6. **Marching Plank** *(Core / Stability)*

---

## Experimental Results & System Evaluation

The proposed system was evaluated on both **Reference** and **User** videos captured from multiple viewpoints (Front, Side, Back).

### Pose Detection Performance Summary

| Exercise Name | Reference Videos Count | Average Detection Accuracy | Viewpoint Sensitivity Notes |
| --- | --- | --- | --- |
| **Air Squat** | 3 | **100.00%** | Excellent landmark stability from both Front and Side views. |
| **Cross Knee Plank** | 2 | **100.00%** | Controlled movement yields perfect landmark tracking. |
| **Easy Push-up** | 2 | **92.40%** | Highly reliable; slight detection drop in side view. |
| **Marching Plank** | 2 | **89.60%** | Strong performance during dynamic lower-limb transitions. |
| **Back Squat** | 3 | **76.50%** | Side view introduced self-occlusion during deep squat phases. |
| **Push-up** | 2 | **60.70%** | Highly sensitive to view: **Side (100%)** vs **Front (21.3%)**. |

### Key System Insights:

* **Camera Viewpoint:** Critical factor for landmark tracking accuracy. Profile (side) views are optimal for upper-body pushing exercises, while front views excel for bilateral squatting/plank movements.
* **Modular Reliability:** Downstream modules (`AngleCalculator` and `FeedbackEngine`) consistently produce meaningful feedback whenever pose detection remains stable.

---

## Getting Started

### Prerequisites

Ensure you have Python 3.8+ installed along with the required dependencies:

```bash
pip install opencv-python mediapipe numpy

```

### MediaPipe Model Setup

Download the MediaPipe Pose Landmarker task file (`pose_landmarker_full.task`) and update the `MODEL_PATH` in `main.py` accordingly.

### Running the Analysis Pipeline

```bash
python main.py

```

---

## Future Improvements

* Enhance repetition counting logic for static isometric holds and non-cyclic/alternating movements.
* Implement occlusion-handling techniques for side-view deep squats and frontal push-ups.
* Develop a real-time stream feedback interface for live webcam input.

---

## Author

**Joud Ali Alshehri**

*AI & Computer Vision Student / Developer*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](http://www.linkedin.com/in/joud-alshehri)
[![X (Twitter)](https://img.shields.io/badge/X-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/JA_shehri)
