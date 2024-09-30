# coding=gbk
import os
import time
from pymongo.errors import ServerSelectionTimeoutError, BulkWriteError, DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorClient
from src.utils.loggerDefine import logger_define

logging = logger_define(os.getcwd(), 'async_save_data')


class PyMongo:
    def __init__(self, config):
        mongodb_config = config['mongodb_config']
        self.db = AsyncIOMotorClient(mongodb_config['client_url'])
        self.client = self.db[mongodb_config['db']]
        self.collection = self.client[mongodb_config['collect']]

    async def save_data(self, data) -> None:
        """
        Save detail data
        """
        detail_data_list = [each.get('data') for each in data if each.get("data")]
        while True:
            try:
                if detail_data_list and detail_data_list != [None]:
                    await self.collection.insert_many(detail_data_list)
                    logging.info(f'Save detail data successful--{len(detail_data_list)}')
                    break
                else:
                    break
            except (BulkWriteError, DuplicateKeyError):
                logging.info(f"Id of detail data is repeating--{[each.get('_id') for each in detail_data_list]}")
                break
            except ServerSelectionTimeoutError:
                logging.error('Save detail data failed,waiting for retry')
                time.sleep(3)
            except Exception as e:
                logging.error(
                    f'Save detail data failed,waiting for retry;msg: {e}')
                time.sleep(3)
                continue
