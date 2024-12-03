#!/bin/bash

echo "停止容器中..."
docker stop seapig-tornado-mock-api
echo "删除容器中..."
docker rm seapig-tornado-mock-api
echo "删除容器结束"
