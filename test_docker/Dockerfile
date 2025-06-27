FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
  libirrlicht-dev libeigen3-dev cmake build-essential ninja-build \
  swig libxxf86vm-dev freeglut3-dev python3 python3-pip python3-numpy \
  python3-venv python3-dev libglu1-mesa-dev libglew-dev libglfw3-dev \
  libblas-dev liblapack-dev git xorg-dev

RUN git clone --recursive -b 9.0.0 https://github.com/projectchrono/chrono.git /chrono
RUN cd /chrono && git submodule update --init --recursive

RUN mkdir -p /chrono/build && cd /chrono/build && \
  cmake .. -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DENABLE_MODULE_PYTHON=ON \
    -DENABLE_MODULE_IRRLICHT=ON \
    -DENABLE_MODULE_POSTPROCESS=ON \
    -DPYTHON_EXECUTABLE=$(which python3) \
    -DPYTHON_VERSION=3.10 \
    -DCMAKE_INSTALL_PREFIX=/chrono/install \
    -DBUILD_DEMOS=OFF \
  && ninja && ninja install \
  && PY_SITE=$(python3 -c "import site; print(site.getsitepackages()[0])") \
  && mkdir -p $PY_SITE \
  && cp -r /chrono/build/bin/pychrono $PY_SITE/ \
  && cp /chrono/build/bin/_core.so $PY_SITE/pychrono/ \
  && cp /chrono/build/bin/_irrlicht.so $PY_SITE/pychrono/ \
  && cp /chrono/build/lib/libChronoEngine_irrlicht.so /usr/local/lib/ \
  && ldconfig \
  || cp /chrono/install/share/chrono/python/pychrono/_core.so $PY_SITE/pychrono/ \
  && cp /chrono/build/bin/_irrlicht.so $PY_SITE/pychrono/

ENV PYTHONPATH="/usr/local/lib/python3.10/dist-packages:$PYTHONPATH"

COPY helloworld.py /home/chrono/helloworld.py

CMD ["bash"]