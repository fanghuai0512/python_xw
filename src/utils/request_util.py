# coding=gbk
import re
import time
import os
import random
import ssl
import asyncio
import aiohttp
from aiohttp.client_exceptions import ClientHttpProxyError
from scrapy import Selector
from src.utils.loggerDefine import logger_define
from src.utils.verify import Verify
from src.utils.parser_util import DetailParse
from configs.request_headers_and_cookies import cookies, headers

my_logger = logger_define(os.getcwd(), 'asyncio')
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Aiohttp:
    semaphore_numb = 5

    def __init__(self, url_list, config, task_data=None):
        self.config = config
        if task_data:
            self.task_data = task_data
        else:
            self.task_data = {}
        proxy_config = config['proxy_config']
        self.tunnel_proxy = f"http://{proxy_config['host']}:{proxy_config['port']}"
        self.proxy_auth = aiohttp.BasicAuth(proxy_config['username'], proxy_config['password'])
        self.url_list = url_list
        self.data_list = []

    @staticmethod
    def get_ssl() -> ssl.SSLContext:
        """
        Modify fingerprint of tls
        """
        ORIGIN_CIPHERS = ('ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
                          'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES')
        ciphers = ORIGIN_CIPHERS.split(':')
        random.shuffle(ciphers)
        ciphers = ":".join(ciphers)
        ciphers = ciphers + ":!aNULL:!eNULL:!MD5"
        context = ssl.create_default_context()
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_TLSv1_1
        context.options |= ssl.OP_NO_TLSv1_2
        context.options |= ssl.OP_NO_TLSv1_3
        context.set_ciphers(ciphers)
        return context

    async def fetch(self, session, furl, sslgen) -> str:
        """
        Send asynchronous request
        """
        semaphore = asyncio.Semaphore(self.semaphore_numb)
        async with semaphore:
            error_num = 0
            for i in range(50):
                headers['downlink'] = str(float(random.choice(range(100, 2000, 5)) / 100))
                headers['sec-ch-ua'] = random.choice(['";Not A Brand";v="99", "Chromium";v="94"',
                                                      '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
                                                      '"Google Chrome";v="104", "Chromium";v="104", "Not=A?Brand";v="81"',
                                                      '"Google Chrome";v="101", "Chromium";v="101", "Not=A?Brand";v="54"',
                                                      '"Google Chrome";v="99", "Chromium";v="99", "Not=A?Brand";v="51"',
                                                      '"Google Chrome";v="98", "Chromium";v="98", "Not=A?Brand";v="102"',
                                                      '"Google Chrome";v="96", "Chromium";v="96", "Not=A?Brand";v="45"',
                                                      '"Google Chrome";v="94", "Chromium";v="94", "Not=A?Brand";v="81"',
                                                      '"Google Chrome";v="92", "Chromium";v="92", "Not=A?Brand";v="159"',
                                                      '"Google Chrome";v="92", "Chromium";v="92", "Not=A?Brand";v="107"',
                                                      '"Google Chrome";v="91", "Chromium";v="91", "Not=A?Brand";v="124"',
                                                      '"Google Chrome";v="91", "Chromium";v="91", "Not=A?Brand";v="77"',
                                                      '"Google Chrome";v="105", "Chromium";v="105", "Not=A?Brand";v="19"',
                                                      '"Google Chrome";v="102", "Chromium";v="102", "Not=A?Brand";v="40"',
                                                      '"Google Chrome";v="100", "Chromium";v="100", "Not=A?Brand";v="20"',
                                                      '"Google Chrome";v="99", "Chromium";v="99", "Not=A?Brand";v="35"',
                                                      '"Google Chrome";v="97", "Chromium";v="97", "Not=A?Brand";v="20"',
                                                      '"Google Chrome";v="95", "Chromium";v="95", "Not=A?Brand";v="40"',
                                                      '"Google Chrome";v="93", "Chromium";v="93", "Not=A?Brand";v="51"',
                                                      '"Google Chrome";v="92", "Chromium";v="92", "Not=A?Brand";v="107"',
                                                      '"Google Chrome";v="92", "Chromium";v="92", "Not=A?Brand";v="70"',
                                                      '"Google Chrome";v="91", "Chromium";v="91", "Not=A?Brand";v="77"',
                                                      '"Google Chrome";v="106", "Chromium";v="106", "Not=A?Brand";v="6"',
                                                      '"Google Chrome";v="98", "Chromium";v="98", "Not=A?Brand";v="4"',
                                                      '"Google Chrome";v="94", "Chromium";v="94", "Not=A?Brand";v="12"',
                                                      '"Google Chrome";v="93", "Chromium";v="93", "Not=A?Brand";v="8"',
                                                      '"Google Chrome";v="92", "Chromium";v="92", "Not=A?Brand";v="20"',
                                                      '"Google Chrome";v="92", "Chromium";v="92", "Not=A?Brand";v="2"',
                                                      '"Google Chrome";v="93", "Chromium";v="93", "Not=A?Brand";v="4"',
                                                      '"Google Chrome";v="93", "Chromium";v="93", "Not=A?Brand";v="3"'])
                headers['viewport-width'] = str(random.choice(range(1024, 2400, 2)))
                headers['sec-ch-viewport-width'] = headers['viewport-width']
                headers['dpr'] = str(random.choice(range(100, 200, 5)) / 100)
                headers['sec-ch-dpr'] = headers['dpr']
                headers[
                    'accept'] = f'text/html,application/xhtml+xml,application/xml;q={str(random.choice(range(6, 9)) / 10)},image/avif,image/webp,image/apng,*/*;q={str(random.choice(range(6, 9)) / 10)},application/signed-exchange;v=b3;q={str(random.choice(range(6, 9)) / 10)}'
                headers[
                    'accept-language'] = f'zh-CN,zh;q={str(random.choice(range(6, 9)) / 10)},en;q={str(random.choice(range(6, 9)) / 10)},en-GB;q={str(random.choice(range(6, 9)) / 10)},en-US;q={str(random.choice(range(6, 9)) / 10)}'
                headers['ect'] = random.choice(['3g', '4g', '5g'])
                headers['rtt'] = str(random.choice(range(100, 400, 50)))
                headers['viewport-width'] = str(random.choice(range(1080, 2400, 2)))

                try:
                    async with session.get(url=furl, proxy=self.tunnel_proxy,
                                           proxy_auth=self.proxy_auth, ssl=sslgen,
                                           headers=headers, cookies=cookies, timeout=20) as response:
                        html = await response.text()
                except ClientHttpProxyError as e:
                    if e.__str__().__contains__("Bandwidth Over Limit"):
                        my_logger.info("Bandwidth Over Limit！！！")
                        await asyncio.sleep(10)
                        continue
                except Exception as e:
                    # my_logger.info(traceback.format_exc())
                    my_logger.error(f"Request exception,please retry;url: {furl}, msg: {e}")
                    await asyncio.sleep(10)
                    continue
                if response.status == 404:
                    my_logger.error("Page is not exist!")
                    return ""
                if response.status == 200 and len(html) > 20000:
                    sel = Selector(text=html)
                    txt = sel.css('#centerCol::text').get().strip()
                    if txt and re.findall("[\u4e00-\u9fa5]", txt):
                        my_logger.info(f"Text of detail data contain chinese")
                        with open(f"error_page\\chinese_page{str(random.randint(1, 1000))}.html", "w",
                                  encoding="utf-8") as f:
                            f.write(html)
                        continue
                    return html
                elif response.status == 200 and len(html) < 20000:
                    html = await Verify(config=self.config).get_token(detaile_url=furl)
                    if html:
                        my_logger.info(f'Pass the verification! very good!!!---{len(html)}')
                        return html
                    else:
                        my_logger.info(f'Verification failed! i am sorry!!!')
                    error_num += 1
                    my_logger.info(f'status:{response.status}---{len(html)}---url:{furl},')
                    if 30 > i >= 20:
                        my_logger.error('Agent exception')
                        time.sleep(i * 10)
                else:
                    my_logger.info(f'status:{response.status}---{len(html)}---url:{furl},')
                    await asyncio.sleep(i * 2.5)
                    continue
            my_logger.error(
                f'[{self.task_data.get("task_id")}]-[{self.task_data.get("seller_id")}]->End retry, ignored:{furl}')
            return ""

    async def main(self, page_url) -> None:
        """
        Running main
        """
        # aiohttp默认使用严格的HTTPS协议检查。可以通过将ssl设置为False来放松认证检查
        # async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        sslgen = self.get_ssl()
        await asyncio.sleep(random.choice(range(50, 1550)) / 100)
        async with aiohttp.ClientSession() as session:
            html = await self.fetch(session=session, furl=page_url, sslgen=sslgen)
            if html:
                data = DetailParse(
                    url=page_url, response=html, task_data=self.task_data,
                    user_id=self.task_data.get('user_id'), task_id=self.task_data.get('task_id'),
                    exception_type=self.task_data.get('exception_type')).run_parse()
                self.data_list.append(data)
            else:
                my_logger.error(
                    f'[{self.task_data.get("task_id")}]-[{self.task_data.get("seller_id")}]->详情页异常:{page_url}')
                data = DetailParse(
                    url=page_url, task_data=self.task_data,
                    user_id=self.task_data.get('user_id'), task_id=self.task_data.get('task_id'),
                    exception_type=17, remark='获取产品页面异常').run_parse()
                self.data_list.append(data)

    def run(self) -> list:
        """
        Run event loop
        """
        if self.url_list:
            loop = asyncio.get_event_loop()
            tasks = [asyncio.ensure_future(self.main(url)) for url in self.url_list]
            loop.run_until_complete(asyncio.wait(tasks))
            return self.data_list
        else:
            my_logger.info(
                f'[{self.task_data.get("task_id")}]-[{self.task_data.get("seller_id")}]->Detail page of available is empty:{self.task_data.get("task_id")}')
