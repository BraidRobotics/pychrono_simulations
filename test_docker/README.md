Builds PyChrono from source using Docker.

```bash
$ docker build -f Dockerfile.build -t chrono-base .
```

Build the runtime image:

```bash
$ docker compose up --build
```

