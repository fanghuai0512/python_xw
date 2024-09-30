import pickle

from redis import StrictRedis
from src.tasks.task_handle import get_task
from src.utils.request_util import Aiohttp
from src.utils.config_util import load_common_config
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] %(message)s')


class AmazonCrawler(object):
    item_base_url = 'https://www.amazon.com/dp/{asin}/'
    redis_key = "MongoData"

    def __init__(self, task_data, config):
        self.config = config
        self.task_data = task_data
        redis_config = config['redis_config']
        self.redis_service = StrictRedis(**redis_config)

    def crawler_data_from_task(self):
        """
        Collect task of item set
        """
        task_data = self.task_data
        # task_data = {'task_id': task_data.get('id'), 'user_id': task_data.get('userId'), 'exception_type': -1,
        #              "orderby": task_data.get('orderby')}
        asin_list = set(task_data.get("itemIdList"))
        url_list = [self.item_base_url.format(asin=asin) for asin in asin_list]
        url_list = url_list[:10]
        length = len(url_list)

        for start_index in range(0, length, 10):
            end_index = min(start_index + 10, length)
            task_item = url_list[start_index:end_index]
            data_list = Aiohttp(url_list=task_item, config=self.config, task_data=task_data).run()
            self.save_data_to_redis(data=data_list)

    def save_data_to_redis(self, data):
        """
        Save data to redis database
        """
        pickle_data = pickle.dumps(data)
        self.redis_service.lpush(self.redis_key, pickle_data)

    def save(self):
        pass


if __name__ == '__main__':
    conf = load_common_config("../../../../configs")
    _task_data = get_task(conf['task_token'])
    crawler = AmazonCrawler(task_data=_task_data, config=conf)
    crawler.crawler_data_from_task()
