FROM debian:buster-slim

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -qq update && \
    apt-get -qq upgrade && \
    apt-get install --yes linphone-nogtk pulseaudio && \
    gpasswd -a root pulse-access && \
    apt-get -yqq autoremove && \
    apt-get clean

ADD linphone.sh /root/linphone.sh

CMD /root/linphone.sh
