![](https://image.3001.net/images/20220303/1646308039_6220aac7713464597ea59.png!small)

## 关于openSquat

openSquat是一款开源的智能化OSINT公开资源情报工具，该工具可以帮助广大研究人员检测和识别特定的网络钓鱼域名或域名占用问题。

## 功能介绍

 **该工具支持检测下列安全问题：**

> 网络钓鱼活动
>
> 域名占用/域名抢占
>
> 误植域名/URL劫持
>
> 域名比特错误
>
> IDN域名同态技术攻击
>
> Doppenganger域
>
> 其他跟域名相关的欺诈攻击

 **关键功能如下：**

> 自动更新新注册的域（每天一次）
>
> 计算单词相似度的Levenshtein距离
>
> 获取活动和已知的网络钓鱼域名
>
> IDN域名同态技术攻击检测
>
> 与VirusTotal的集成
>
> 与Quad9 DNS服务集成
>
> 使用不同级别的置信阈值进行微调
>
> 将输出保存为不同格式（txt、JSON和CSV）
>
> 可以与其他威胁情报工具和其他安全工具集成

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地，并安装相关的依赖组件：

    
    
    git clone https://github.com/atenreiro/opensquat
    
    pip install -r requirements.txt

注意：请确保已经在设备环境中安装并配置好Python 3.6+和pip3。

## 工具更新

如果需要更新当前的工具版本，直接在命令行终端中切换到项目目录下，然后运行下列命令即可：

    
    
    git pull
    
    pip install -r requirements.txt

## 工具使用

首先，我们需要使用自定义关键词来修改“keywords.txt”中的内容。

使用默认配置运行：

    
    
    python opensquat.py

查看工具帮助选项：

    
    
    python opensquat.py -h

搜索网络钓鱼活动中特定的术语（可能存在假阳性）：

    
    
    python opensquat.py -k generic.txt

启用DNS验证

    
    
    python opensquat.py --dns

子域名搜索：

    
    
    python opensquat.py --subdomains

检查域名的开放端口80/443：

    
    
    python opensquat.py --portcheck

网络钓鱼验证（网络钓鱼数据库）：

    
    
    python opensquat.py --phishing phish_results.txt

保存JSON格式输出：

    
    
    python opensquat.py -o example.json -t json

保存CSV格式输出：

    
    
    python opensquat.py -o example.csv -t csv

启动证书透明度检测：

    
    
    python opensquat.py --ct

周期搜索-搜索从上个月开始注册的域名（默认：天）

    
    
    python opensquat.py -p month

调整阈值，值越低，误报率越高（0:非常高；1:高（默认）；2:中等；3:低；4:非常低）

    
    
    python opensquat.py -c 2

开启所有验证选项：

    
    
    python opensquat.py --phishing phishing_domains.txt --dns --ct --subdomains --portcheck

## 工具运行截图

![](https://image.3001.net/images/20220303/1646308123_6220ab1b99027c5de710e.png!small)

## 工具演示视频

 **视频地址：** 【[ _点我观看_](https://asciinema.org/a/361931)】

## 项目地址

 **openSquat：** 【[ _GitHub传送门_](https://github.com/atenreiro/opensquat)】

## 参考资料

> [ _https://opensquat.com/_](https://opensquat.com/)
>
> [ _https://telegram.me/opensquat_bot_](https://telegram.me/opensquat_bot)
>
> [ _https://phishydomains.com/_](https://phishydomains.com/)

