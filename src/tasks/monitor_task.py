from src.common.py_msql import PySql
from src.utils.config_util import load_common_config
from src.utils.request_util import Aiohttp


class MonitorTask(object):
    item_base_url = 'https://www.amazon.com/dp/{asin}/'

    def __init__(self, config):
        self.config = config
        self.mysql_config = config['mysql_config']
        self.mysql_service = PySql(config)
        self.table_name = self.mysql_config['table_name']

    def get_all_asin(self):
        sql_str = f"SELECT asin FROM {self.table_name}"
        result = self.mysql_service.fetch_all(sql=sql_str)
        asin_list = [each.get('asin') for each in result if each.get('asin')]
        return asin_list

    def main(self):
        while True:
            asin_list = self.get_all_asin()
            url_list = [self.item_base_url.format(asin=asin) for asin in asin_list]
            length = len(url_list)

            for start_index in range(0, length, 10):
                end_index = min(start_index + 10, length)
                task_item = url_list[start_index:end_index]
                downloader = Aiohttp(url_list=task_item, config=self.config)
                data_list = downloader.run()
                del downloader
                monitor_data_list = []
                for each in data_list:
                    for i in each:
                        data = i['data']
                        profile = i['profile']
                        asin = profile.get("asin", None)
                        price = data.get('finalPurchasePrice', None)
                        stock = data.get("stock")
                        if profile.get('exceptionType') == 17:
                            collect_status = 404
                        elif asin and price and stock != -1:
                            collect_status = 0
                        else:
                            collect_status = -1
                        collect_msg = profile.get('remark')
                        item = {
                            "asin": asin,
                            "collect_status": collect_status,
                            "collect_msg": collect_msg,
                            "sell_price": price,
                            "stock": stock
                        }
                        monitor_data_list.append(item)
                self.mysql_service.insert_many(table=self.table_name, data_list=monitor_data_list)


if __name__ == '__main__':
    conf = load_common_config("../../configs")
    MT = MonitorTask(config=conf)
    print(MT.main())
