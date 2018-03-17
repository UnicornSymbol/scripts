#coding:utf-8

from data_output import DataOutput
from html_downloader import HtmlDownloader
from html_parser import HtmlParser
from url_manager import UrlManager

class Spider(object):
    def __init__(self):
        self.manager = UrlManager()
        self.downloader = HtmlDownloader()
        self.parser = HtmlParser()
        self.output = DataOutput()

    def crawl(self,root_url):
        self.manager.add_new_url(root_url)
        while(self.manager.has_new_url() and self.manager.old_urls_size()<100):
            try:
                new_url = self.manager.get_new_url()
                html = self.downloader.download(new_url)
                #print(html)
                new_urls,data = self.parser.parser(new_url,html)
                #print(new_urls)
                self.manager.add_new_urls(new_urls)
                self.output.store_data(data)
                print("已经抓取%s个链接" % self.manager.old_urls_size())
            except Exception as e:
                print("crawl failed: %s" % e)
        self.output.output_html()


if __name__=='__main__':
    spider = Spider()
    spider.crawl("http://baike.baidu.com/view/284853.htm")
