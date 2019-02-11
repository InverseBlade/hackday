import requests
import re
from bs4 import BeautifulSoup
import math
import lxml
import time
import random
import pymysql.cursors

headers = {
    'Host': 'www.bilibili.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0'
}


headers1 = {
    'Host': 'api.bilibili.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0'
}


connect = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'db': 'bilibili',
    'charset': 'utf8mb4',
}
db = pymysql.connect(**connect)
cursor = db.cursor()
# sql = "delete from anima"
# cursor.execute(sql)
# db.commit()

# https://api.bilibili.com/x/web-interface/archive/stat?aid=16277457
# https://api.bilibili.com/cardrich?&mid=9117212

# url = 'https://www.bilibili.com/index/rank/all-3-1.json' #动画
# https://www.bilibili.com/index/rank/all-3-3.json音乐
# https://www.bilibili.com/index/rank/all-3-129.json 舞蹈
# https://www.bilibili.com/index/rank/all-3-4.json 游戏
# https://www.bilibili.com/index/rank/all-3-119.json 鬼畜

url_list = [
    ['https://www.bilibili.com/index/rank/all-3-1.json', 'comics'],
    ['https://www.bilibili.com/index/rank/all-3-3.json', 'music'],
    ['https://www.bilibili.com/index/rank/all-3-129.json', 'dance'],
    ['https://www.bilibili.com/index/rank/all-3-4.json', 'game'],
    ['https://www.bilibili.com/index/rank/all-3-119.json', 'demon'],
    ['https://www.bilibili.com/index/rank/all-3-36.json', 'tech'],
]


def gethtml(url):
    try:
        if 'api' in url:
            response = requests.get(url, headers=headers1)
        else:
            response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)


def gethtml1(url):
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        r.encoding = 'UTF-8'
        return r.text
    except:
        pass


def parse_page(json, category):
    if json:
        items = json['rank']['list']
        # return items
        i = 1
        for item in items:
            if i >= 50:
                pass
            i += 1
            time.sleep(random.randint(0, 2))
            # print(item)
            try:
                video = {}
                video['id'] = item.get('aid')
                video['mid'] = item.get('mid')
                url = 'https://api.bilibili.com/x/web-interface/archive/stat?aid='+video['id']
                info = get_upinfo(gethtml(url))
                video['favo'] = info['favo']
                video['coins'] = info['coin']
                video['dan'] = info['dan']
                url = 'https://api.bilibili.com/cardrich?&mid={}'.format(video['mid'])
                fan = getfans(gethtml(url))
                video['fan'] = fan['fans']

                url = 'https://api.bilibili.com/x/v2/reply?&type=1&oid={}'.format(video['id'])
                info2 = get_commentnum(gethtml(url))
                video['commentnum'] = info2['number']
                video['pic'] = item.get('pic')
                video['title'] = item.get('title')
                video['play'] = item.get('play')
                video['url'] = 'https://www.bilibili.com/video/av'+video['id']

                html = gethtml1((video['url']))
                info1 = getintro(html)
                video['fp'] = info1['fp']
                video['intro'] = info1['intro']
                video['score'] = cal(video)
                print(video)


                sql = "insert into hkd_video(category,title,image_src,web_src,introduct,score) values(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\')".format(category,video['title'],video['pic'],video['url'],video['intro'],video['score'])
                cursor.execute(sql)
                db.commit()
                del video['play']
                del video['commentnum']
                del video['coins']
                del video['dan']
                del video['favo']
                del video['fp']
                del video['id']
                del video['mid']
                yield video
            except:
                pass


def cal(video):
    a = (200000+video['play'])/(2*video['play'])
    if a >= 1:
        a = 1
    b = (video['play']*50)/(video['play']+video['commentnum']*50)
    c = video['coins']*2000/video['play']
    # d = (video['favo']*20+video['coins']*10)/(video['play']+video['coins']*10+video['commentnum']*50)

    video['play'] = (video['play']*4/(video['fp']+3)*a) / math.log10(video['fan'])
    video['commentnum'] = video['commentnum']*b
    video['coins'] = video['coins']*c
    video['favo'] = video['favo']*20
    video['dan'] = video['dan']*0.2

    allpoint = (video['play']+video['commentnum']+video['coins']+video['favo']+video['dan'])
    return allpoint

def get_commentnum(json):
    if json:
        items = json.get('data')
        items = items['page']
        info = {}
        info['number'] = items['acount']
        return info


def get_upinfo(json):
    if json:
        items = json['data']
        info = {}
        info['favo'] = items.get('favorite')
        info['share'] = items.get('share')
        info['coin'] = items.get('coin')
        info['dan'] = items.get('danmaku')
        return  info

def getfans(json):
    if json:
        items = json.get('data')
        items = items['card']
        fan = {}
        fan['fans'] = items.get('fans')
        return fan


def getintro(html):
    inf = {}
    soup = BeautifulSoup(html)
    ps = soup.find('div', class_='v-plist')
    i = 0
    for p in ps.find_all('option'):
        i = i + 1
    if i == 0:
        i = i+1
    inf['fp'] = i
    info = BeautifulSoup(html).find('div', class_='v_desc report-scroll-module report-wrap-module')
    inf['intro'] = info.string
    return inf


if __name__ == "__main__":
    for url, category in url_list:
        json = gethtml(url)
        # print(json)
        content = parse_page(json, category)
        # print(content)
        for m in content:
            print(m)
        # url = 'https://www.bilibili.com/video/av16002547/'
        # getintro(gethtml1(url))
