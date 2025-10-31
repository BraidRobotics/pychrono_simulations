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

## Database

`SQLite` is used as the database and the database is pushed. 

To keep things neater, `alembic` is setup in the database folder instead of root. 

That means that a migration must be run in the following way:

```bash
$ alembic -c database/alembic.ini upgrade head
```

And to create a migration (using `initial` in this case):

```bash
$ alembic -c database/alembic.ini revision --autogenerate -m "initial schema"
```

---

## Images

Images are stored in the `assets` directory which isn't tracked by git since it will take up too much space. If images need to be transfered, they will have to be copied manually.

If the `assets` folder doesn't exist, it will be created and it will create a subfolder for each experiment series.

---

## OS specifics

While it works on MacOS (tested on M2 Chip), the MK Solver does not support ARM so a less precise solver is used.

---
---
---

## The Docker Setup [Experimental]

The Docker setup vastly improves and standardizes the installation process by building PyChrono from source. 

There are two configurations:

1. Just PyChrono (no visualization)
1. PyChrono with Irrlicht (visualization) 

The first one is still a useful way to run simulations and replicate the values / access the experimentation dashboard. 

In order to get the visualization working by forwarding the display to the host machine, one must use VNC or X11 forwarding. This requires Linux and perhaps Windows Subsystem for Linux but has not been tried yet. 

