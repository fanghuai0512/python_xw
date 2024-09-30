# 运行爬虫代码，请按需求注释
ENV=dev nohup python crawl.py >> /logs/crawl.log 2>&1 &

# 运行保存数据代码，请按需求注释
ENV=dev nohup python save.py >> /logs/save.log 2>&1 &

# 运行监控代码，请按需求注释
ENV=dev nohup python monitor.py >> /logs/monitor.log 2>&1 &

