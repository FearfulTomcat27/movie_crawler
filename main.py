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
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Referer': 'https://www.6bt0.com/',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
                }
        # 所选择电影清晰度列表
        self.articulations = []

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

    # 通过关键字搜索电影
    def filter_movie_info(self,list):
        # 设置电影列表
        movies = [{
                "title" : movie.select_one("h5").text,
                "movie_path" : f"{self.domain}{movie.select_one('a')['href'][1:]}",
                "movie_post" : re.findall(r"url\((.*?)\)",movie.select_one(".bgimgcov")['style'])[0]
            }
            for movie in list]
        self.get_movie(movies)

    # 在搜索结果中选择电影
    def get_movie(self,movies):
        clear_screen()
        print("请输入您想检索的电影序号,例如:1")
        for index,movie in enumerate(movies):
            print(f"{index}.{movie['title']}")
        print("-1.返回重新搜索电影")
        mv_index = input_number()

        if mv_index == -1:
            self.search_movie()
            return

        if -1< mv_index < len(movies):
            self.get_magnets(mv_index,movies)
        else:
            print("请输入正确的电影序号，正在返回重新选择序号...")
            time.sleep(1)
            self.get_movie(movies)

    # 搜索电影
    def search_movie(self):
        clear_screen()
        print("===请输入您想搜索的电影名称===")
        keyword = input()
        print(f"正在搜索电影:{keyword}...")
        url = f"{self.domain}/search.php?sb={keyword}"
        response = self.session.get(url,headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        movie_list = soup.select(".masonry_item")
        # 如果搜索结果不为空
        if movie_list:
            self.filter_movie_info(movie_list)
        else:
            print("没有检索到相关电影")
            self.search_movie()

    # 爬取电影某个清晰度的所有磁力链接
    def magnet_cralwer(self,containers):
        # 返回包含标题、磁力链接、大小、下载地址的列表
        return [{
                "title": container.select_one(".torrent-title").text,
                "magnet": container.select("a")[1]["href"],
                "size": container.select_one(".tag-size").text,
                "download_link": f"{self.domain}{container.select('a')[2]['href']}"
            }
            # 遍历containers
            for container in containers]

    # 获取所有清晰度的磁力链接列表
    def get_magnets(self,mv_index,movies):
        response = self.session.get(movies[mv_index]['movie_path'],headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # 没有获取到磁力链接资源
        articulations = [item.text for item in soup.select(".tab_title .h5") if item]
        if articulations is None:
            print("\r没有检索到相关电影的资源列表")
            return
        self.articulations = articulations

        # 获取用户想要的清晰度
        clear_screen()
        print("请输入您想要的清晰度序号,例如:1")
        # 输出清晰度列表
        for (index,articulation) in enumerate(self.articulations):
            print(f"{index}.{articulation}")
        print("-1.获取所有清晰度资源")
        ac_index = input_number()

        result={}
        # 获取所有清晰度
        if ac_index == -1:
            # 获取清晰度tab的html元素
            tabs = soup.select(".tab__content")
            if tabs is None:
                print("没有检索到相关电影的磁力链接")
                return

            for articulation,tab in zip(articulations,tabs):
                torrents = self.magnet_cralwer(tab.select(".container"))
                result[articulation] = torrents
        # 获取某一清晰度
        elif -1< ac_index < len(self.articulations):
            # 获取当前清晰度的html元素
            tab = soup.select(".tab__content")[int(ac_index)]
            # 查找当前tab的所有磁力链接容器
            torrents = self.magnet_cralwer(tab.select(".container"))
            result[self.articulations[ac_index]] = torrents
        # 输入序号不正确
        else:
            print("请输入正确的清晰度序号，正在返回重新选择序号...")
            time.sleep(1)
            self.get_magnets(mv_index,movies)

        self.select_magnet(result,self.articulations[ac_index])
        # print(json.dumps(result,ensure_ascii=False))

    def select_magnet(self,magnet_list,ac):
        clear_screen()
        print("下面是该清晰度的所有磁力链接:")

        print("种子标题\t种子大小\t种子链接")
        for index,magnet in enumerate(magnet_list[ac]):

            print(f"{magnet['title']}\t{magnet['size']}\t{magnet['magnet']}")

    # 启动函数
    def search(self):
        self.get_cookie()
        self.search_movie()

if __name__ == "__main__":
    movie = Movie()
    movie.search()
