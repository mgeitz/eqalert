from debian:bullseye-slim

LABEL maintainer="mgeitz" \
      version="3.4.2" \
      description="A Configurable and Context Driven Project 1999 Log Parser with NCurses Interface for Linux"

RUN groupadd -g 1000 eqalert && \
    useradd -r -u 1000 -g eqalert eqalert

WORKDIR /usr/apt/eqalert

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install python3 python3-pip libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0 libgstreamer1.0-0 gstreamer1.0-dev gstreamer1.0-tools -y && \
    python3 -m pip install --upgrade pip

RUN python3 -m pip install pycairo && \
    python3 -m pip install pygobject

COPY . .

RUN python3 -m pip install -e .

USER eqalert

CMD eqalert
