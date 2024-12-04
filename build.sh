#!/bin/bash

echo "构建镜像中..."
docker build -f Dockerfile -t seapig-tornado-mock:1.0.0 .
echo "构建镜像结束"
