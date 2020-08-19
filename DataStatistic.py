#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: aiker@gdedu.ml
# My blog http://m51cto.51cto.blog.com
import requests
import re
import urllib2
import datetime
import json
import sys
from bs4 import BeautifulSoup
import re
import redis
import schedule
import os
reload(sys)
sys.setdefaultencoding("utf-8")


# 头部设置
headers = {'Content-Type': 'application/json;charset=utf-8'}
# 修改成自己的钉钉机器人api
api_url = "https://oapi.dingtalk.com/robot/send?access_token=b8983348505xxxxxxxxxxxxxxxxxxxxxxxxxx"
# 大众用户界面点评网址，后面那个是大众点评的用户id
dazhong_url = "https://m.dianping.com/userprofile/1799576002"
# 小红书用户界面网址，后面那个是小红书的id
xiaohongshu_url = "https://www.xiaohongshu.com/user/profile/593950f26a6a693fbc4f1814"
# 每隔几天发送一次
day = 3
# 每天的几点钟发送
time = "21:00"



# 从钉钉官方文档中拷贝
#   如果需要@某一个用户，在atMobiles中添加用户手机号
#   如果需要@所有的用户，把isAtAll改成True
#   备注：由于钉钉目前添加了安全设置，必须要符三种安全设置（自定义关键词、加签、IP地址）中的一种。我这边选择的是自定义关键词，只需text中含有关键词即可。
def msg(text):
    json_text= {
     "msgtype": "text",
        "at": {
            "atMobiles": [
                "180xxxx7260"
            ],
            "isAtAll": False
        },
        "text": {
            "content": text
        }
    }
    print requests.post(api_url,json.dumps(json_text),headers=headers).content


#从大众点评上爬下来涨粉数据
def dazhongdianpin():
    hearders = "User-Agent","Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
    par = '(<script>)(.*?)(</script>)'    ##正则匹配，匹配出网页内要的内容

    ##创建opener对象并设置为全局对象
    opener = urllib2.build_opener()
    opener.addheaders = [hearders]
    urllib2.install_opener(opener)

    ##获取网页
    html = urllib2.urlopen(dazhong_url).read().decode("utf-8")
    # print html


    soup = BeautifulSoup(html, "html.parser")
    titles = soup.select("body script")
    title = titles[1]
    # print comments

    #print title
    ##提取需要爬取的内容
    flowerCount = re.findall(r'"flowerCount":\d+\.?\d*', str(title))[0].split(":")[1]
    followCount = re.findall(r'"followCount":\d+\.?\d*', str(title))[0].split(":")[1]
    fansCount = re.findall(r'"fansCount":\d+\.?\d*', str(title))[0].split(":")[1]

    # print flowerCount
    # print followCount
    # print fansCount
    # return [flowerCount,followCount,fansCount]

    # host是redis主机，需要redis服务端和客户端都启动 redis默认端口是6379
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    if r.get("public_comment_fans") == None:
        r.set("public_comment_fans","0")
    if r.get("public_comment_likes") ==None:
        r.set("public_comment_likes","0")


    data =  "小屁桃日记在「大众点评」上获得%s个赞，有%s位粉丝，已关注%s人。\n距离上次报告增长了【%d】个粉丝，增加了【%d】个赞。"%(flowerCount, fansCount, followCount, int(fansCount) - int(r.get("public_comment_fans")), int(flowerCount) - int(r.get("public_comment_likes")))
    r.set("public_comment_fans", fansCount)
    r.set("public_comment_likes", flowerCount)

    return data


#从小红书上爬下来涨粉数据
def xiaohongshu():
    hearders = "User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"

    par = '(<meta name="description" content=")(.*?)(">)'  ##正则匹配，匹配出网页内要的内容


    ##创建opener对象并设置为全局对象
    opener = urllib2.build_opener()
    opener.addheaders = [hearders]
    urllib2.install_opener(opener)

    ##获取网页
    html = urllib2.urlopen(xiaohongshu_url).read().decode("utf-8")

    soup = BeautifulSoup(html, "html.parser")
    text = str(soup.select("meta")[1]).split('"')[1].split("，来「小红书」")[0]



    # host是redis主机，需要redis服务端和客户端都启动 redis默认端口是6379
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    if r.get("little_red_book_fans") == None:
        r.set("little_red_book_fans","0")
    if r.get("little_red_book_notes") ==None:
        r.set("little_red_book_notes","0")

    # 找到数字的正则表达式
    data = re.findall(r"\d+\.?\d*", text)
    text = text + "。\n距离上次报告增长了【%d】个粉丝，更新了【%d】篇笔记。"%( int(data[1]) - int(r.get("little_red_book_fans")),int(data[0])-int(r.get("little_red_book_notes")))
    r.set("little_red_book_fans", data[1])
    r.set("little_red_book_notes", data[0])

    return text



# 设定好要执行的任务
def job():
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    text = xiaohongshu() + "\n\n" + dazhongdianpin() + "\n\n截至 %s ฅฅฅ\n"%(time)
    print text
    msg(text)
    print "\n等待下一次任务...\n"



if __name__ == '__main__':
    # 定时发送
    # schedule.every(day).days.at(time).do(job)
    # while True:
    #     schedule.run_pending()
    job()