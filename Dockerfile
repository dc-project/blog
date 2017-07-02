FROM debian:stretch

MAINTAINER Ysicing Zheng<root@ysicing.net>


# pip http
COPY pip.conf /root/.pip/pip.conf

# apt
ADD sid.list  /etc/apt/sources.list

RUN DEBIAN_FRONTEND=noninteractive apt-get update; \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        python3.6 python3.6-apt  python3-pip python3.6-dev  build-essential apt-utils gcc;\
    rm -rf /var/lib/apt/lists/*


ENV TZ "Asia/Shanghai"
ENV TERM xterm
ENV LANG en_US.UTF-8

RUN mkdir -p /data/ops
COPY . /data/ops
WORKDIR /data/ops

VOLUME ["/data/ops"]

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["bash"]



