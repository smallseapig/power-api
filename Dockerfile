FROM python:3.6.3-alpine3.6
RUN echo 'Asia/Shanghai' > /etc/timezone
ENV LANG C.UTF-8
RUN apk update
RUN apk add --no-cache ca-certificates tzdata curl bash vim && rm -rf /var/cache/apk/*
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN pip3 install requests tornado pyyaml -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --trusted-host pypi.org --trusted-host files.pythonhosted.org
ADD code /home/code/
WORKDIR /home/code/
CMD python3 main.py