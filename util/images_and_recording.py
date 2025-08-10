import subprocess
import os
from pathlib import Path
import shutil

PROJECT_ROOT = Path(os.getcwd())

def get_path_with_experiment_series_name(experiment_series_name):
	base_path = PROJECT_ROOT / "assets" / experiment_series_name
	base_path.mkdir(parents=True, exist_ok=True)
	return str(base_path)

def delete_experiment_series_folder(experiment_series_name):
    base_path = get_path_with_experiment_series_name(experiment_series_name)
    if os.path.isdir(base_path):
        shutil.rmtree(base_path)
    elif os.path.exists(base_path):
        os.remove(base_path)
    else:
        print(f"Path {base_path} does not exist, nothing to delete.")

def _get_image_path(experiment_series_name, filename):
	base_path = get_path_with_experiment_series_name(experiment_series_name)
	return os.path.join(base_path, filename)

def take_model_screenshot(visualization, experiment_series_name):
	file_path = _get_image_path(experiment_series_name, "model.jpg")
	visualization.WriteImageToFile(file_path)

frame_count = 0


def take_final_screenshot(visualization, experiment_series_name, experiment_id):
	filename = f"{experiment_series_name}_{experiment_id}.jpg"
	file_path = _get_image_path(experiment_series_name, filename)
	visualization.WriteImageToFile(file_path)

def take_video_screenshot(visualization, experiment_series_name):
	global frame_count
	path = get_path_with_experiment_series_name(experiment_series_name)
	filename = f"{path}/{frame_count:05d}.jpg"
	visualization.WriteImageToFile(filename)
	frame_count += 1

def make_video_from_frames(experiment_series_name, output="output.mp4", fps=30):
	global frame_count

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
	frame_count = 0



if __name__ == "__main__":
	make_video_from_frames("_default")
