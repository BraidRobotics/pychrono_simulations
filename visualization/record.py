import subprocess


frame_count = 0

def output_image_frame(visualization, path="assets/frames"):
	global frame_count
	import os
	os.makedirs(path, exist_ok=True)
	filename = f"{path}/{frame_count:05d}.jpg"
	visualization.WriteImageToFile(filename)
	frame_count += 1


def make_video_from_frames(path="assets/frames", output="output.mp4", fps=30):
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

