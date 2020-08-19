#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time
import requests
import json
from bs4 import BeautifulSoup
import redis
import schedule


# 头部信息
headers = {'Content-Type': 'application/json;charset=utf-8'}

# 爬取的新浪热搜网址
Sina_url = 'https://s.weibo.com/top/summary'

# 填写你的钉钉群机器人url
api_url = "https://oapi.dingtalk.com/robot/send?access_token=b8983348505xxxxxxxxxxxxxxxxxxxxxxxxxx"

# 根据微博的热度来决定是否推送，微博热度大于某一个阈值就推送
ThresholdValue = 2000000


# 每几秒进行查询一次
second = 60


# 从钉钉官方文档中拷贝
#   备注：由于钉钉目前添加了安全设置，必须要符三种安全设置（自定义关键词、加签、IP地址）中的一种。我这边选择的是自定义关键词，只需text中含有关键词即可。

def msg(title, text, messageUrl):
    json_text= {
        "msgtype": "link",
        "link": {
            "text": text,
            "title": title,
            "picUrl": "https://tva1.sinaimg.cn/large/007S8ZIlly1ghv137a9g2j30xc0r2q4f.jpg",
            "messageUrl": messageUrl
        }
    }
    print requests.post(api_url,json.dumps(json_text),headers=headers).content


def down_url(url):
    header = {
        "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
    }
    res = requests.get(url, headers=header).content
    table = BeautifulSoup(res, "html.parser").table
    head = table.thead.tr.find_all('th')
    body = table.tbody.find_all('tr')
    Sina_cache = []
    Sina_bodyList = []
    # 获取字段名
    for title in head:
        Sina_cache.append(title.text)
    Sina_bodyList.append(Sina_cache)
    # 获取字段内容
    for tr in body:
        Sina_cache = []
        for td in tr.find_all('td'):
            Sina_cache.append(td.text.strip())
        href_after = tr.find('td', class_="td-02").a['href']
        # 当一条热点的标志为“荐”时，正确的url尾缀在 href_to 属性下
        if href_after == 'javascript:void(0);':
            href_after = tr.find('td', class_="td-02").a['href_to']
        href = 'https://s.weibo.com/{}'.format(href_after)
        Sina_cache.append(href)
        Sina_bodyList.append(Sina_cache)
    # 将内容中的标题和热度数值分成两列存储
    for content in Sina_bodyList:
        Sina_cache = content[1].split('\n', 1)
        content[1] = Sina_cache[0]
        if len(Sina_cache) > 1:
            content.insert(2, Sina_cache[1])
        else:
            content.insert(2, '')
    return Sina_bodyList




def job():
    # host是redis主机，需要redis服务端和客户端都启动 redis默认端口是6379
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    Sina_List = down_url(Sina_url)
    # sina 1-5 分别为：热搜排行、热搜标题、热度、状态、url
    for sina in Sina_List[2:]:
        # 如果是广告，或者是刚才发送过（在redis的缓存里面，一天后会销毁），则会过滤
        if(int(sina[2]) > ThresholdValue and r.get(sina[1])==None and sina[3]!=u'\u8350'):
            print sina
            r.set(sina[1], "1")
            r.expire(sina[1], 60 * 60 * 24) #设置key的过期时间为一个小时
            title = sina[1]
            text = "排行:" + str(sina[0]) +" | 热度:" + str(sina[2])
            messageUrl = sina[4]
            msg(title, text, messageUrl)
            print title



if __name__ == "__main__":
    # 定时执行
    # schedule.every(second).seconds.do(job)
    # while True:
    #     schedule.run_pending()
    job()