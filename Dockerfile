FROM ysicing/debian
# FROM dl.ysicing.net:5000/debian

MAINTAINER Ysicing Zheng<root@ysicing.net>

ENV TZ "Asia/Shanghai"
ENV TERM xterm
ENV LANG en_US.UTF-8

#自定义源
ADD sid.list  /etc/apt/sources.list

#VOLUME ["/data/ops"]

RUN mkdir -p /data/ops
COPY . /data/ops
WORKDIR /data/ops

VOLUME ["/data/ops"]

RUN echo $(python3.6 -V) && apt update && apt install -y sudo lsof python3.6-dev openssl gcc libssl-dev libcurl4-openssl-dev

RUN python3.6 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN chmod +x /data/ops/docker-entrypoint.sh

EXPOSE 4000
#CMD 'python3.6'
ENTRYPOINT ["/data/ops/docker-entrypoint.sh"]
#CMD ["gunicorn", "--bind","0.0.0.0:4000","-w","4","app.create_app()", "--access-logfile", "/data/ops/app/logs/access.log", "--error-logfile", "/data/ops/app/logs/error.log"]
