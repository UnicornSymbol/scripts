# coding:utf-8

import requests

class HtmlDownloader(object):
    def download(self,url):
        if url is None:
            return None
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
        headers = {'User-Agent': user_agent}
        res = requests.get(url,headers=headers)
        if res.status_code==200:
            res.encdoing = 'utf-8'
            return res.text
        return None
