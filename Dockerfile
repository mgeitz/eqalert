FROM debian:bookworm

LABEL maintainer="mgeitz" \
      description="A Configurable and Context Driven Project 1999 Log Parser with NCurses Interface for Linux"

RUN groupadd -g 1000 eqalert \
    && useradd -r -u 1000 -g eqalert eqalert \
    && usermod -a -G audio eqalert

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
        gcc \
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
        pkg-config \
        pulseaudio \
        python3-dev \
        python3-poetry \
    && apt-get clean

USER eqalert

WORKDIR /usr/src/eqalert

COPY . .

RUN poetry run pip install --upgrade pip \
    && poetry run pip install --upgrade wheel \
    && poetry run pip install playsound

RUN poetry install --without dev

RUN poetry build

CMD poetry run eqalert
