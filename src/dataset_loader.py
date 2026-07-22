"""
dataset_loader.py

------------------------------------------------------------
Dataset Loader Module
------------------------------------------------------------

Purpose
-------
This module is responsible for automatically discovering all
exercise videos stored inside the datasets directory.

It scans every exercise folder and returns a structured
dictionary containing:

- Exercise name
- Reference videos
- User videos

The Pose Detector or any other module should NEVER know where
videos are stored. They only receive a video path from this
module.

Example folder structure

datasets/
│
├── pushup/
│   ├── reference/
│   │      front.mp4
│   │      side.mp4
│   │
│   └── user/
│          front.mp4
│          side.mp4
│
├── air_squat/
│   ├── reference/
│   └── user/
│
└── ...

Output format

{
    "pushup":
    {
        "reference":[
            ".../front.mp4",
            ".../side.mp4"
        ],

        "user":[
            ".../front.mp4",
            ".../side.mp4"
        ]
    }
}
"""

from pathlib import Path

# Supported video extensions
VIDEO_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".wmv"
}


class DatasetLoader:

    def __init__(self, dataset_root):
        self.dataset_root = Path(dataset_root)

        if not self.dataset_root.exists():
            raise FileNotFoundError(
                f"Dataset folder not found:\n{self.dataset_root}"
            )

    # -------------------------------------------------------

    def _get_video_files(self, folder):

        """
        Return all videos inside a folder.

        Parameters
        ----------
        folder : Path

        Returns
        -------
        list[str]
        """

        if not folder.exists():
            return []

        videos = []

        for file in sorted(folder.iterdir()):

            if (
                file.is_file()
                and file.suffix.lower() in VIDEO_EXTENSIONS
            ):
                videos.append(str(file))

        return videos

    # -------------------------------------------------------

    def load(self):

        """
        Scan the entire datasets folder.

        Returns
        -------
        dict

        Example

        {
            "pushup":
            {
                "reference":[...],
                "user":[...]
            }
        }
        """

        dataset = {}

        for exercise_folder in sorted(self.dataset_root.iterdir()):

            if not exercise_folder.is_dir():
                continue

            exercise_name = exercise_folder.name

            reference_folder = exercise_folder / "reference"
            user_folder = exercise_folder / "user"

            dataset[exercise_name] = {

                "reference":
                    self._get_video_files(reference_folder),

                "user":
                    self._get_video_files(user_folder)
            }

        return dataset

    # -------------------------------------------------------

    def get_exercises(self):

        """
        Return exercise names only.
        """

        return list(self.load().keys())

    # -------------------------------------------------------

    def get_reference_videos(self, exercise_name):

        dataset = self.load()

        return dataset.get(exercise_name, {}).get("reference", [])

    # -------------------------------------------------------

    def get_user_videos(self, exercise_name):

        dataset = self.load()

        return dataset.get(exercise_name, {}).get("user", [])

    # -------------------------------------------------------

    def get_all_videos(self, exercise_name):

        dataset = self.load()

        exercise = dataset.get(exercise_name)

        if exercise is None:
            return []

        return exercise["reference"] + exercise["user"]


# ==========================================================
# Test
# # ==========================================================

# if __name__ == "__main__":

#     loader = DatasetLoader(
#         r"C:\Users\JoudA\OneDrive\سطح المكتب\COOP - JOUD ALSHEHRI\code\datasets"
#     )

#     datasets = loader.load()

#     print("=" * 60)

#     for exercise, videos in datasets.items():

#         print(f"\nExercise : {exercise}")

#         print("\nReference Videos")

#         for video in videos["reference"]:
#             print("   ", Path(video).name)

#         print("\nUser Videos")

#         for video in videos["user"]:
#             print("   ", Path(video).name)

#         print("-" * 60)
