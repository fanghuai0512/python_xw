from src.crawler.amazon_crawler import AmazonCrawler
from src.tasks.task_handle import get_task
from src.utils.config_util import load_common_config

if __name__ == '__main__':
    conf = load_common_config("./configs")
    _task_data = get_task(conf['task_token'])
    crawler = AmazonCrawler(task_data=_task_data, config=conf)
    crawler.crawler_data_from_task()
