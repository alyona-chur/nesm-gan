ARG CUDA_VERSION=11.6.2
ARG CUDNN_VERSION=8
ARG UBUNTU_VERSION=18.04
FROM nvcr.io/nvidia/cuda:${CUDA_VERSION}-cudnn${CUDNN_VERSION}-devel-ubuntu${UBUNTU_VERSION} as base

SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

# Python environment and arguments
ENV LANG C.UTF-8
ARG PYTHON=python3.7
ARG PIP=pip3.7

# Install basic packages
RUN apt-get update && apt-get install -y \
    ${PYTHON} \
    curl \
    wget \
    vim \
    git \
    cmake \
    build-essential \
    pkg-config \
    python3-dev \
    python3-pip \
    python3-distutils \
    python3-setuptools \
    python-pip \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libeigen3-dev \
    libyaml-cpp-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libdc1394-22-dev \
    libsndfile1 libsndfile1-dev  # For sndfile

# Create a user to map from docker host
ARG USER_ID
ARG GROUP_ID
ARG USER_NAME
RUN addgroup --gid $GROUP_ID $USER_NAME --force-badname
RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID $USER_NAME --force-badname

# Install required Python packages
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN ${PYTHON} get-pip.py
RUN ${PIP} --no-cache-dir install --upgrade pip

# Install required pip packages
COPY ./requirements.txt ./
RUN ${PIP} install --upgrade pip \
   && ${PIP} install --no-cache-dir -r requirements.txt \
   && rm requirements.txt

# Install VGM
RUN wget https://github.com/vgmrips/vgmplay/archive/0.40.8.tar.gz
RUN tar -xzvf 0.40.8.tar.gz
RUN mkdir /usr/vgplay_bin && cd vgmplay-legacy-0.40.8/VGMPlay \
    && sed -i 's/USE_LIBAO = 1/#USE_LIBAO = 1/' Makefile \
    && make vgm2wav && cp vgm2wav /usr/vgplay_bin

# Specify working dir for a project
ARG WORKING_DIR=/usr/src/app
WORKDIR ${WORKING_DIR}

# Customize command prompt
RUN echo 'PS1="nes-gan>:\w\$ "' >> /etc/bash.bashrc

# Setting up user environment
USER ${USER_NAME}
ENV LANG C.UTF-8
