#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import json
import datetime
import urllib2
from bs4 import BeautifulSoup
import schedule
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

# 头部设置
headers = {'Content-Type': 'application/json;charset=utf-8'}
# 修改成自己的钉钉机器人api
api_url = "https://oapi.dingtalk.com/robot/send?access_token=b8983348505xxxxxxxxxxxxxxxxxxxxxxxxxx"
# 修改成自己所在的省份和城市
weather_url = "https://tianqi.moji.com/weather/china/zhejiang/hangzhou"
# 要爬取的励志话语网址
line_url = "http://wufazhuce.com/"
# 纪念日
anniversary = '2020-02-14 00:00:00'
# 每天定时发送的时间
day_time = "8:00"





# 从钉钉官方文档中拷贝
#   如果需要@某一个用户，在atMobiles中添加用户手机号
#   如果需要@所有的用户，把isAtAll改成True
#   备注：由于钉钉目前添加了安全设置，必须要符三种安全设置（自定义关键词、加签、IP地址）中的一种。我这边选择的是自定义关键词，只需text中含有关键词即可。

def msg(text):
    json_text= {
     "msgtype": "text",
        "at": {
            "atMobiles": [
            ],
            "isAtAll": False
        },
        "text": {
            "content": text
        }
    }
    print requests.post(api_url,json.dumps(json_text),headers=headers).content


# 天气查询函数，返回相关信息
def weather():
    hearders = "User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"

    ##创建opener对象并设置为全局对象
    opener = urllib2.build_opener()
    opener.addheaders = [hearders]
    urllib2.install_opener(opener)

    ##获取网页
    html = urllib2.urlopen(weather_url).read().decode("utf-8")

    ##提取需要爬取的内容
    soup = BeautifulSoup(html, "html.parser")
    return soup.select("div.wea_tips")[0].contents[3].text


def line():
    hearders = "User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"

    ##创建opener对象并设置为全局对象
    opener = urllib2.build_opener()
    opener.addheaders = [hearders]
    urllib2.install_opener(opener)

    ##获取网页
    html = urllib2.urlopen(line_url).read().decode("utf-8")
    ##提取需要爬取的内容
    soup = BeautifulSoup(html, "html.parser")
    return soup.select(".fp-one-cita")[0].contents[1].text


# 设定要定时发送的任务
def job():
    # 获取当前时间和纪念日时间
    d1 = datetime.datetime.strptime(anniversary, '%Y-%m-%d %H:%M:%S')
    now = datetime.datetime.now()
    delta = now - d1
    deadline = delta.days + 1
    time = now.strftime('%Y年%m月%d日')

    data = "【%s】是我们在一起的第%s天。\n\n" % (time, deadline)
    data += "【天气】" + str(weather()) + "\n\n"
    data += "【每日一句】" + str(line())

    print data
    msg(data)
    print "\n\n等待下一次执行...\n\n"


if __name__ == '__main__':
    # 定时执行
    # schedule.every().day.at(day_time).do(job)
    # while True:
    #     schedule.run_pending()
    job()