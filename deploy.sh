#!/bin/bash

echo "部署容器中..."
docker run -d -p 35080:35080 -p 35443:35443 --name seapig-tornado-mock-api --restart=always -v $(pwd)/code:/home/code -v /etc/localtime:/etc/localtime:ro seapig-tornado-mock:1.0.0
echo "部署容器结束"
