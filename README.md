# PyChrono Simulations

PyChrono Simulations for the ITU braid robotics project.

---

## Setup

#### Install:

https://api.projectchrono.org/pychrono_installation.html

#### Run

```bash
$ conda activate chrono
```

#### Install dependencies

```bash
$ conda install --file requirements.txt
```

---
---
---

## The Docker Setup

The Docker setup vastly improves and standardizes the installation process by building PyChrono from source. 

There are two configurations:

1. Just PyChrono (no visualization)
1. PyChrono with Irrlicht (visualization) 

The first one is still a useful way to run simulations and replicate the values / access the experimentation dashboard. 

In order to get the visualization working by forwarding the display to the host machine, one must use VNC or X11 forwarding. This requires Linux and perhaps Windows Subsystem for Linux but has not been tried yet. 


---
---
---

## Todo 

* Get the Docker visualization working with VNC or X11 forwarding.

* Implement the pure PyChrono Docker setup (without Irrlicht) and make it work with the experimentation dashboard.

* Create the experimentation dashboard.

