FROM debian:bullseye-slim as builder

ARG LINPHONE_VERSION=5.2

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /root

RUN apt-get update -qq && \
    apt-get install -yqq git cmake doxygen yasm nasm pkg-config libx11-dev python3 python3-pip libasound2-dev libv4l-dev && \
    pip3 install six pystache && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    git clone --single-branch --recurse-submodules --shallow-submodules --branch release/$LINPHONE_VERSION https://gitlab.linphone.org/BC/public/linphone-sdk.git linphone-sdk && \
    mkdir ./linphone-sdk/build

WORKDIR /root/linphone-sdk/build
RUN cmake -DENABLE_UNIT_TESTS=0 -DENABLE_TOOLS=0 -DENABLE_CXX_WRAPPER=0 ..

# Patch mediastream to allow to create a socket that can be bound by anyone
RUN sed -i 's/fchmod(sock,S_IRUSR|S_IWUSR)/fchmod(sock,S_IRUSR|S_IWUSR|S_IRGRP|S_IWGRP|S_IROTH|S_IWOTH)/' ../bctoolbox/src/utils/port.c

# Patch call-stats command to remove video infos to avoid crash
# It should have a better way to fix it, but for tests it's good enough
RUN sed -i '/ostr <<.*video/d' ../liblinphone/daemon/commands/call-stats.cc

RUN cmake --build . --parallel 4

FROM debian:bullseye-slim
RUN apt-get update -qq && \
    apt-get install -yqq libasound2 libv4l-0 libx11-6 && \
    rm -rf /var/lib/apt/lists/*

# Create directory for linphone database
RUN mkdir -p /root/.local/share/linphone
COPY --from=builder /root/linphone-sdk/build/linphone-sdk/desktop /root/linphone-sdk/build/linphone-sdk/desktop
COPY entrypoint.sh /root/linphone-daemon.sh
ENTRYPOINT ["/root/linphone-daemon.sh"]
