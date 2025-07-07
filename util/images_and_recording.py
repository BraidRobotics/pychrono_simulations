import subprocess
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(os.getcwd())

def get_path_with_experiment_series_name(experiment_series_name):
	base_path = PROJECT_ROOT / "assets" / experiment_series_name
	base_path.mkdir(parents=True, exist_ok=True)
	return str(base_path)

def get_screenshot_path_if_exists(experiment_series_name):
	return PROJECT_ROOT / "assets" / experiment_series_name / "model.jpg"

def take_model_screenshot(visualization, experiment_series_name):
	base_path = get_path_with_experiment_series_name(experiment_series_name)
	filename = os.path.join(base_path, "model.jpg")
	visualization.WriteImageToFile(filename)

frame_count = 0

def take_screenshot(visualization, experiment_series_name):
	global frame_count
	path = get_path_with_experiment_series_name(experiment_series_name)
	filename = f"{path}/{frame_count:05d}.jpg"
	visualization.WriteImageToFile(filename)
	frame_count += 1


def make_video_from_frames(experiment_series_name, output="output.mp4", fps=30):
	global frame_count
	frame_count = 0

	path = get_path_with_experiment_series_name(experiment_series_name)

	cmd = [
		"ffmpeg",
		"-framerate", str(fps),
		"-start_number", "0",
		"-i", f"{path}/%05d.jpg",
		"-c:v", "libx264",
		"-pix_fmt", "yuv420p",
		output
	]
	subprocess.run(cmd)



if __name__ == "__main__":
	make_video_from_frames()
