FROM debian:bookworm

LABEL maintainer="mgeitz" \
      description="A Configurable and Context Driven Project 1999 Log Parser with NCurses Interface for Linux"

WORKDIR /usr/src/eqalert

RUN groupadd -g 1000 eqalert \
    && useradd -r -u 1000 -g eqalert eqalert \
    && usermod -a -G audio eqalert

RUN mkdir -p /home/eqalert \
    && chown eqalert:eqalert /home/eqalert

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
        espeak-ng \
        gcc \
        g++ \
        gir1.2-gtk-3.0 \
        gstreamer1.0-alsa \
        gstreamer1.0-dev \
        gstreamer1.0-gl \
        gstreamer1.0-gtk3 \
        gstreamer1.0-libav \
        gstreamer1.0-plugins-base \
        gstreamer1.0-plugins-good \
        gstreamer1.0-plugins-bad \
        gstreamer1.0-plugins-ugly \
        gstreamer1.0-pulseaudio \
        gstreamer1.0-qt5 \
        gstreamer1.0-tools \
        gstreamer1.0-x \
        libasound2 \
        libasound2-plugins \
        libpulse0 \
        libsndfile1-dev \
        libgirepository1.0-dev \
        libgstreamer1.0-0 \
        libgstreamer1.0-dev \
        libgstreamer-plugins-bad1.0-dev \
        libgstreamer-plugins-base1.0-dev \
        make \
        pkg-config \
        pulseaudio \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        python3-wheel \
        python3-cairo \
        python3-gi \
    && apt-get clean

USER eqalert

ENV PATH "$PATH:/home/eqalert/.local/bin"

COPY . .

RUN scripts/install-playsound.sh

RUN python3 -m pip install -e . --break-system-packages

CMD eqalert