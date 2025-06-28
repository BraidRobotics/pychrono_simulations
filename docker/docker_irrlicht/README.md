# PyChrono Docker Irrlicht

Builds PyChrono from source using Docker and this setup includes Irrlicht.

While containers are headless there are techniques to forward the display to a host machine, such as using VNC or X11 forwarding. 

**The below claim has not been tested yet:**

(This will work on Linux and possibly Windows with WSL2. (But not MacOS).)

**What has been tested is that it correctly installs Irrlicht and the error messages relate to forwarding the display.**

---

## How to get started

Build the Docker image. 

```bash
$ docker compose up --build
```

Run the image and start a bash shell in the container:

```bash
$ docker compose run chorno bash
```

In the shell, start the `helloworld.py` script:

```bash
$ python3 /home/chrono/helloworld.py
```

