import requests
from bs4 import BeautifulSoup
import re
import json
import time

from utils import input_number,clear_screen

class Movie():
    # 初始化Movie类，传入关键字
    def __init__(self):
        # 初始化域名、会话、请求头、资源列表
        self.domain = "https://www.6bt0.com"
        # 创建一个会话
        self.session = requests.Session()
        # 请求头
        self.headers = {
                    'Accept': 'application/json, text/plain, */*',
                    'Referer': 'https://www.6bt0.com/',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
                }

    # 请求首页获取cookie
    def get_cookie(self):
        response = self.session.get(self.domain,headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        # 获取script标签中的文本
        script = soup.select('script')[0].text
        # 在文本中查找匹配项
        pattern = r"document\.cookie = \"(.*?)\";"
        cookies = self.strToJson(re.findall(pattern, script)[0])
        self.session.cookies.update(cookies)

    # 将str转换为json
    def strToJson(self,str):
        return {pair.split('=')[0]: pair.split('=')[1] for pair in filter(None, str.split(';'))}

    # 在搜索结果中选择电影
    def get_movie(self,movies):
        clear_screen()
        print("请输入您想检索的电影序号,例如:1")
        for index,movie in enumerate(movies):
            print(f"{index}.{movie['title']}")
        print("-1.返回重新搜索电影")
        mv_index = input_number()

        if mv_index == -1:
            return self.search_movie()

        if -1< mv_index < len(movies):
            self.get_magnets(movies[mv_index])
        else:
            print("请输入正确的电影序号，正在返回重新选择序号...")
            time.sleep(1)
            self.get_movie(movies)

    def search_movie(self):
        clear_screen()
        print("===请输入您想搜索的电影名称===")
        keyword = input()
        print(f"正在搜索电影:{keyword}...")
        url = f"{self.domain}/prod/core/system/getVideoList?sb={keyword}&page=1"
        response = self.session.get(url,headers=self.headers)
        data = response.json()
        movies = [{
            "id": movie['id'],
            "title": movie['title']
        }
        for movie in data['data']]
        self.get_movie(movies)

    # 获取所有清晰度的磁力链接列表
    def get_magnets(self,movie):
        response = self.session.get(f"{self.domain}/prod/core/system/getVideoDetail/{movie['id']}",headers=self.headers)
        data = response.json()
        link_list = data['data']['ecca']
        ac_list = []

        clear_screen()
        print("请输入您想要的清晰度序号,例如:1")
        for (index,key) in enumerate(link_list):
            ac_list.append(key)
            print(f"{index}.{key}")

        ac_index = input_number()

        if ac_index <len(ac_list):
            # 将结果转换为只含title、link、size的列表
            result = [{
                'title':item['zname'],
                'link':item['zlink'],
                'size':item['zsize']
            }
            for item in link_list[ac_list[ac_index]]]
            # 输出结果
            self.select_magnet(result)
        else:
            print("请输入正确的清晰度序号，正在返回重新选择序号...")
            time.sleep(1)
            self.get_magnets(movie)

    # 打印结果
    def select_magnet(self,list):
        clear_screen()
        print("下面是该清晰度的所有磁力链接:")

        print("种子标题\t种子大小\t种子链接")
        for index,magnet in enumerate(list):

            print(f"{magnet['title']}\t{magnet['size']}\t{magnet['link']}")

    # 启动函数
    def search(self):
        self.get_cookie()
        self.search_movie()

if __name__ == "__main__":
    movie = Movie()
    movie.search()
