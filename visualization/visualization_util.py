frame_count = 0

def output_image_frame(visualization, path="assets/frames"):
	global frame_count
	import os
	os.makedirs(path, exist_ok=True)
	filename = f"{path}/{frame_count:05d}.jpg"
	visualization.WriteImageToFile(filename)
	frame_count += 1
