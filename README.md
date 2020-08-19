# DingDingRobot
钉钉机器人实现微博推送、定时发送纪念日、定时发送天气、励志话语、统计小红书粉丝数、统计大众点评粉丝数

## 依赖

**python2.7**

```
pip install -r requirements
```

## 使用方法

1、修改好自己的钉钉机器人api

2、在pycharm中运行

3、如需定时运行，则将main中定时执行代码段的注释给删掉

## 部署到vps运行

```shell
#持久化运行
nohup python -u test.py > test.log 2>&1 &
```

![运行情况](https://tva1.sinaimg.cn/large/007S8ZIlly1ghuxgi6qzij310k04gmzm.jpg)

如上图所示，得到一个进程号，来查看进程运行情况，运行如下代码：

`ps -A | grep python`

## 注意

由于钉钉目前添加了安全设置，必须要符三种安全设置（自定义关键词、加签、IP地址）中的一种。我这边选择的是自定义关键词，只需text中含有关键词即可。



## 参考

[钉钉官方文档](https://ding-doc.dingtalk.com/doc#/serverapi3/iydd5h)

