import asyncio
import datetime
import os
import pickle
import random
import time
from redis.client import StrictRedis
from src.common.py_mongo import PyMongo
from src.utils.loggerDefine import logger_define
from src.utils.config_util import load_common_config

logging = logger_define(os.getcwd(), 'redis_save_mongo')
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class DataHolder(object):

    def __init__(self, config):
        redis_config = config['redis_config']
        self.redis_service = StrictRedis(**redis_config)
        self.redis_key = config['product_redis_key']
        self.mogodb_service = PyMongo(config)

    @staticmethod
    def filte_data(data_list):
        seen_asins = set()
        # 创建一个新的双列表用于存储去重后的数据
        filtered_double_list = []

        # 遍历原始的双列表
        for sublist in data_list:
            # 创建一个新的子列表用于存储去重后的项目
            new_sublist = []
            for item in sublist:
                # 提取当前项目的asin
                asin = item['profile']['asin']
                # 检查asin是否已经出现过
                if asin not in seen_asins:
                    # 如果没有出现过，添加到新的子列表和集合中
                    new_sublist.append(item)
                    seen_asins.add(asin)
            # 将去重后的子列表添加到新的双列表中
            if new_sublist:
                filtered_double_list.append(new_sublist)
        data_list = filtered_double_list
        return data_list

    def save_to_mogondb(self, data_list) -> None:
        """Run event loop"""
        data_list = self.filte_data(data_list)

        if data_list:
            loop = asyncio.get_event_loop()
            tasks = [asyncio.ensure_future(self.mogodb_service.save_data(data)) for data in data_list]
            loop.run_until_complete(asyncio.wait(tasks))
        else:
            logging.info("Task is empty!")

    def get_data_item_from_redis(self) -> list:
        """
        Get data from redis

        Return detail data of product
        """
        while True:
            try:
                length = self.redis_service.llen(self.redis_key)
                logging.info(f"{datetime.datetime.now()}-left data count:<{length}>")
                if length:
                    pickle_data = self.redis_service.lrange(self.redis_key, 0, 0)[0]
                    # pickle_data = self.redis_service.rpop(self.redis_key)
                    if pickle_data and isinstance(pickle_data, bytes):
                        data = pickle.loads(pickle_data)
                        logging.info("Get data item success!")
                        return data
                    else:
                        logging.error("Queue is empty,failed request of data!")
                        return []
            except Exception as e:
                logging.error(f"Get data item from redis failed: msg:{e}")

    def main(self) -> None:
        """Method to running"""
        try:
            while True:
                data = self.get_data_item_from_redis()
                if data:
                    logging.info("save data start")
                    while True:
                        try:
                            self.save_to_mogondb(data)
                            break
                        except Exception as e:
                            logging.error(f"Redis save to mongodb error; msg:{e}")
                else:
                    sleep_time = random.randint(55, 65)
                    logging.info(f"waiting..........")
                    time.sleep(sleep_time)
        except Exception as e:
            logging.error(f"Save item error; msg: {e}")


if __name__ == '__main__':
    conf = load_common_config("../../../../configs")
    rstm = DataHolder(conf)
    rstm.main()
