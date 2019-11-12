FROM debian:buster-slim

ARG LINPHONE_VERSION=4.2

ENV DEBIAN_FRONTEND noninteractive

WORKDIR /root

RUN apt-get update -qq && \
    apt-get install -yqq git cmake doxygen yasm nasm pkg-config libx11-dev python3 python3-pip libasound2-dev libv4l-dev && \
    pip3 install six pystache && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    git clone --single-branch --branch release/$LINPHONE_VERSION https://gitlab.linphone.org/BC/public/linphone-sdk.git linphone-sdk && \
    mkdir ./linphone-sdk/build  && \
    # Create directory for linphone database
    mkdir -p /root/.local/share/linphone

WORKDIR /root/linphone-sdk/build
RUN cmake ..

# Patch mediastream to allow to create a socket that can be bound by anyone
RUN sed -i 's/fchmod(sock,S_IRUSR|S_IWUSR)/fchmod(sock,S_IRUSR|S_IWUSR|S_IRGRP|S_IWGRP|S_IROTH|S_IWOTH)/' ../ortp/src/port.c

RUN cmake --build . --parallel 4

COPY entrypoint.sh /root/linphone-daemon.sh
ENTRYPOINT ["/root/linphone-daemon.sh"]
