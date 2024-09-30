import os
import re
import ddddocr
import random
import aiohttp
import ssl
from lxml import etree
from src.utils.loggerDefine import logger_define
from configs.request_headers_and_cookies import cookies, headers

my_logger = logger_define(os.getcwd(), 'asyncio')


class Verify:
    def __init__(self, config):
        proxy_config = config['proxy_config']
        self.tunnel = f"http://{proxy_config['host']}:{proxy_config['port']}"
        self.proxy_auth = aiohttp.BasicAuth(proxy_config['username'], proxy_config['password'])

    @staticmethod
    def get_ssl() -> ssl.SSLContext:
        """修改tls加密逻辑"""
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

    @staticmethod
    async def get_field_keywords(image_name) -> ddddocr.DdddOcr.classification:
        """识别验证码"""
        ocr = ddddocr.DdddOcr()
        with open(f'.\\source\\verify_img\\{image_name}.jpg', 'rb') as f:
            img_bytes = f.read()
        field_keywords = ocr.classification(img_bytes)
        os.remove(f'.\\source\\verify_img\\{image_name}.jpg')
        return field_keywords

    @staticmethod
    async def save_imgs(img_url, image_name) -> None:
        """保存验证码图片"""
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
            async with session.get(img_url) as r:
                content = await r.read()
            with open(f'.\\source\\verify_img\\{image_name}.jpg', 'wb') as f:
                f.write(content)

    async def get_verify_comtent(self) -> str:
        """请求验证码页面"""
        for i in range(3):
            sslgen = self.get_ssl()
            timeout = aiohttp.ClientTimeout(total=20)
            try:
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
                    async with session.get(url='https://www.amazon.com/errors/validateCaptcha', cookies=cookies,
                                           ssl=sslgen,
                                           headers=headers, timeout=timeout) as resp:
                        content = await resp.text()
                        return content
            except:
                continue
        return ""

    async def get_token(self, detaile_url) -> str:
        """请求商品页面"""
        for i in range(5):
            url = 'https://www.amazon.com/errors/validateCaptcha'
            content = await self.get_verify_comtent()
            if not content:
                continue
            try:
                data = etree.HTML(content)
                amzn = data.xpath('/html/body/div/div[1]/div[3]/div/div/form/input[1]/@value')[0]
                amzn_r = re.search('https://www.amazon.com(.*)', detaile_url).group(1)
                img_url = data.xpath('/html/body/div/div[1]/div[3]/div/div/form/div[1]/div/div/div[1]/img/@app')[0]
                import hashlib
                image_name = hashlib.md5(detaile_url.encode("utf8")).hexdigest()
                await self.save_imgs(img_url, image_name)
                field_keywords = await self.get_field_keywords(image_name)
            except:
                continue
            params = {
                'amzn': amzn,
                'amzn-r': amzn_r,
                'field-keywords': field_keywords,
            }
            sslgen = self.get_ssl()
            try:
                timeout = aiohttp.ClientTimeout(total=20)
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
                    # proxy="http://" + self.tunnel,  proxy_auth=self.proxy_auth,
                    async with session.get(url=url, cookies=cookies, ssl=sslgen,
                                           headers=headers, params=params, timeout=timeout) as resp:
                        content = await resp.text()
                    if resp.status == 200 and len(content) > 20000:
                        return content
                    else:
                        continue
            except:
                continue
        return ""
