# 使用botengine作为基础镜像
FROM python:3.8.16

USER root

# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有文件到工作目录
COPY . .

# 安装curl
# RUN apt-get update && apt-get install -y curl vim

# 安装应用所需的依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN ["bash", "startup.sh"]