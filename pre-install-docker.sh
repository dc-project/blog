#!/bin/sh


curl -sSL https://get.daocloud.io/docker | sh
curl -L https://get.daocloud.io/docker/compose/releases/download/1.11.2/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
curl -sSL https://get.daocloud.io/daotools/set_mirror.sh | sh -s http://d3f9a56b.m.daocloud.io
