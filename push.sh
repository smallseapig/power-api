#!/bin/bash

echo "打 TAG 中..."
docker tag seapig-tornado-mock:latest 192.168.168.207:30002/public/seapig-tornado-mock:1.0.0
echo "推送镜像中..."
docker push 192.168.168.207:30002/public/seapig-tornado-mock:1.0.0
echo "推送镜像结束"
