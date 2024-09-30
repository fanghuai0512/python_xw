1.crawl.py 为爬虫代码，这应该是项目的第一步，爬取亚马逊的数据暂存于redis。
2.save.py 为数据储存代码，读取redis中的数据，将这些数据保存到mongodb中。
3.monitor.py 为监控数据代码，循环监控数据库中的所有数据，并爬取最新的数据更新。

注意：
    在执行代码前请先检查/configs 目录下的配置信息
    三个部分都可以独立运行
    运行startup.sh即同时启动这三段代码

linux部署流程：
    1.构建镜像：docker build -t amazon-collect:1.0 .
    2.创建容器:docker run -it -d --name collect_contain --rm amazon-collect:1.0 /bin/bash
    3.进入容器:docker exec -it collect_contain /bin/bash
    4.运行代码:bash startup.sh
# python_xw
