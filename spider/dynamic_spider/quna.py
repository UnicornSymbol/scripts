#coding:utf-8
# import datetime
import codecs
import datetime
from bs4 import BeautifulSoup

from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

class QunaSpider(object):
    def get_hotel(self,driver,to_city,fromdate,todate):
        ele_toCity = driver.find_element_by_name('toCity')
        ele_fromdate = driver.find_element_by_id('fromDate')
        ele_toDate = driver.find_element_by_id('toDate')
        ele_search = driver.find_element_by_class_name('search-button')
        ele_toCity.clear()
        ele_toCity.send_keys(to_city)
        ele_toCity.click()
        ele_fromdate.clear()
        ele_fromdate.send_keys(fromdate)
        ele_toDate.clear()
        ele_toDate.send_keys(todate)
        ele_search.click()
        page_num = 0
        time.sleep(5)
        print(driver.page_source)
        while True:
            try:
                WebDriverWait(driver,10).until(
                    EC.title_contains(to_city)
                )
            except Exception as e:
                print(e)
                break
            time.sleep(5)
            js = "window.scrollTo(0, document.body.scrollHeight);"
            driver.execute_script(js)
            html_const = driver.page_source
            soup = BeautifulSoup(html_const,'html.parser')
            infos = soup.find_all(class_="item_hotel_info")
            print(infos)
            f = codecs.open(to_city+fromdate+'.html','a','utf-8')
            for info in infos:
                f.write(str(page_num)+'--'*50)
                content = info.get_text().replace(" ","").replace("\t","").strip()
                for line in [ln for ln in content.splitlines() if ln.strip()]:
                    f.write(line)
                    f.write('\r\n')
            f.close()
            try:
                next_page = WebDriverWait(driver,10).until(
                    EC.visibility_of(driver.find_element_by_css_selector(".item.next"))
                )
                next_page.click()
                page_num += 1
                time.sleep(10)
            except Exception as e:
                print(e)
                break

    def crawl(self,root_url,to_city):
        today = datetime.date.today().strftime('%Y-%m-%d')
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow = tomorrow.strftime('%Y-%m-%d')
        driver = webdriver.PhantomJS()
        driver.set_page_load_timeout(50)
        driver.get(root_url)
        driver.implicitly_wait(10)
        self.get_hotel(driver,to_city,today,tomorrow)


if __name__ == '__main__':
    spider = QunaSpider()
    spider.crawl('http://hotel.qunar.com',"上海")
