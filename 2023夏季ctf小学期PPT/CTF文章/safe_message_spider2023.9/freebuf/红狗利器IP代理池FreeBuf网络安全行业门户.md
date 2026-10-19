## 背景

使用Python自动生成Clash配置文件，实现FUZZ自动切换IP。现在蓝狗IP速度太太太太太太太太快了，估计当年用Burp爆破封堵IP的日子就想哭。不要问我为啥不用飞鱼，太贵了。

## 接口支持

品易HTTP：<http://http.py.cn/>

后续根据反馈进行增加

## 使用指南

### 购买IP地址池

该推荐余额套餐的方式进行购买，脚本配合余额支付更划算。  
<http://http.py.cn/pay/?paytype=banlance>

### 获取API接口

套餐后，选择》API购买》直接提取，推荐配置如下：

1.余额消费。

2.使用时长选择，建议选择25分钟-180分钟。

3.抽取数量建议为5-10，土豪随意。

4\. 推荐多种不同类型的精品，并选择提高自己的风格。

5.目前该代理协议仅支持SOKCS5连接。

6.数据格式选择Json格式，方便脚本解析。

7.选择属性全部勾选，否则会发生错误。

8.IP去重365天。

![](https://image.3001.net/images/20220516/1652661136_62819b9085744cd2193b5.jpg!small)

### 部署说明

项目地址：<https://github.com/Mustard404/Auto_proxy>

将Auto_proxy代码（Auto_proxy_example.yaml, Auto_proxy.py,
proxyIgnoreList.plist目录）拷贝到Clash配置文件下。

> Windows 默认：Clash\Data\profiles\
>
> Mac默认：~/.config/clash/

![](https://image.3001.net/images/20220516/1652661147_62819b9b4282e8a92bffb.jpg!small)

修改auto_proxy.py相关配置，主要参数如下。

> test_url：需要监控测试的IP地址。
>
> py_api：上一步获取的易API接口。
>
> max_connect_error：错误连接次数，连续连接错误N次，重新获取代理。

![](https://image.3001.net/images/20220516/1652661113_62819b796c86651af84c6.jpg!small)

白敏感配置，可参考<https://www.cnblogs.com/PowerTips/p/14775956.html>

Windows：在Auto_proxy_example.yaml添加cfw-bypass配置。

Mac: 使用项目中proxyIgnoreList.plist，需要直接重启。

注：将共同获取*.taolo.taolo.一直以来可能会导致代理无效重复。

###
[](https://github.com/Mustard404/Auto_proxy#%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E)使用说明

在Clash目录下执行python3 Auto_proxy.py，同时Clash将配置选为Auto_proxy。

![](https://image.3001.net/images/20220516/1652661173_62819bb5b856e7a9ad8ad.jpg!small)

将需要配置为模式：设置系统代理，当前配置方式设置

加速模式：根据监控网站选择最晚的代理。

负载模式：每个请求都会随时进行代理连接。

![](https://image.3001.net/images/20220516/1652661185_62819bc1b43bbfb48678e.jpg!small)

负载模式运行效果：

![](https://image.3001.net/images/20220516/1652661196_62819bcc7398df21a7fc1.jpg!small)

当运行禁载异常时，会进行提示“IP已被封，重新获取代理”，此时Clash提示“重配置文件”，需手动点击更新。

![](https://image.3001.net/images/20220516/1652661207_62819bd77aa6ca10c7050.jpg!small)

###
[](https://github.com/Mustard404/Auto_proxy#%E4%BD%BF%E7%94%A8%E6%95%88%E6%9E%9C)使用效果

该效果模式为负载模式，测试目录，其他工具请自行测试。

靶机端： python3 -m http.server 8000

攻击端： python3 dirsearch.py​​ -u
[http://XXXX:8000](http://x.x.x.x:8000/)\--proxy=
[http://127.0.0.1:7890](http://127.0.0.1:7890/)

![](https://image.3001.net/images/20220516/1652661217_62819be196266d268218c.jpg!small)

10个IP爆破目录，就问你慌不慌！

## 其它

后来发现可以通过腾讯云函数进行IP代理池免费获取，但是实际使用中存在经常断线，消费告警等问题（应该是云函数默认配置的日志资源），各位老板按照自己喜好来弄。

SCF_云函数IP代理池：﻿<https://github.com/shimmeris/SCFProxy>

