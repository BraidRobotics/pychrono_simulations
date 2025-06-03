# pychrono_simulations

Testing out basic simulations with PyChrono


---

## Installation

<!-- todo -->
https://api.projectchrono.org/pychrono_installation.html


---

## Run

```bash
$ conda activate chrono
```




---

# Install dependencies

```bash
$ conda install --file requirements.txt
```

---

## ffmpeg command to create a video:

First recomment this line in main.py:

visualization.WriteImageToFile("assets/frames/" + f'{int(system.GetChTime() / timestep):05d}' + ".jpg")


In root run:

ffmpeg -framerate 30 -start_number 0 -i assets/frames/%05d.jpg -c:v libx264 -pix_fmt yuv420p output.mp4

