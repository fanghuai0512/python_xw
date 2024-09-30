import os
import random
import time
import requests
from requests import Response
from src.utils.tls_util import get_tls
from src.utils.loggerDefine import logger_define
from configs.request_headers_and_cookies import cookies, headers

logging = logger_define(os.getcwd(), 'GetResponse')


def get_response(url: str, proxies=None) -> Response:
    """
    Send request
    """
    while True:
        try:
            headers['downlink'] = str(float(random.choice(range(50, 200, 5)) / 100))
            headers['viewport-width'] = str(random.choice(range(1024, 2400, 2)))
            headers['sec-ch-viewport-width'] = headers['viewport-width']
            headers['dpr'] = str(random.choice(range(10, 20)) / 10)
            headers['sec-ch-dpr'] = headers['dpr']
            headers['ect'] = random.choice(['3g', '4g', '5g'])
            headers['rtt'] = str(random.choice(range(100, 200, 50)))
            headers['accept-language'] = \
                f'zh-CN,zh;q={str(random.choice(range(6, 9)) / 10)},en;q={str(random.choice(range(6, 9)) / 10)},' \
                f'en-GB;q={str(random.choice(range(6, 9)) / 10)},en-US;q={str(random.choice(range(6, 9)) / 10)}'
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:" + get_tls()
            _response = requests.get(url, headers=headers, cookies=cookies, timeout=30, proxies=proxies)
        except Exception as e:
            logging.info(f"requests error, msg: {e}")
            time.sleep(3.5)
            continue
        if _response.status_code == 200 and len(_response.text) > 10000:
            return _response
        elif "amazon" not in url:
            return _response
        else:
            logging.info(f'Retry {url}')
            logging.info(f'{_response.status_code}---{len(_response.text)}--{url}')
            time.sleep(random.choice(range(50, 1050)) / 100)

# if __name__ == '__main__':
#     url = "https://www.baidu.com"
#     response = get_response(url)
#     print(len(response.text))
