![](https://image.3001.net/images/20210828/1630143461_612a03e5e83623001defd.png!small)

## 关于ARTIF

ARTIF是一个新型的高级实时威胁智能框架，它基于MISP并添加了另一个抽象层，以实现根据IP地址和历史数据识别恶意Web流量。除此之外，该工具还可以通过收集、处理和关联基于不同因素的观测值来执行自动分析和威胁评分。

## 功能介绍

> 评分系统：使用威胁元数据丰富IP地址信息，其中包括了威胁评分，这个评分可以作为安全团队采取行动的阈值。
>
> 容器化：该工具使用容器进行部署，因此易于部署。
>
> 模块化体系结构：该项目基于插件，只需修改MISP中的威胁源即可轻松扩展，而且可以在线实时更新，不会导致实际服务停止运行。
>
> 警报：扩展功能与Slack无缝集成，可实现主动警报。
>
> 更好的攻击分析和可视化效果。

## 使用场景

威胁检测

日志和监控

用户配置文件

警报自动化

## 工具要求

首先，我们需要安装好MISP，这里可以直接使用源码安装，或使用预构建的AWS镜像。

安装完成之后，我们需要订阅maxmind以便为IP填充元数据，这里需要编辑docker-compose.yaml并添加子键：

    
    
    maxmind:
    
        image: maxmindinc/geoipupdate
    
        environment:
    
          GEOIPUPDATE_ACCOUNT_ID: xxxxx
    
          GEOIPUPDATE_LICENSE_KEY: xxxxxxxxxxxxxx

## 工具安装

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/CRED-CLUB/ARTIF/

然后将工作目录切换至ARTIF根目录，构建Docker，并开启Docker容器：

    
    
    sudo docker-compose build
    
    sudo docker-compose up

安装MISP，访问MISP仪表盘并获取MISP密钥。然后编辑config.yaml文件，添加MISP_KEY和MISP_URL的值。这里的MISP_KEY就是你的MISP密钥，MISP_URL即托管MISP的URL地址。

下面给出的是config.yaml样例，可以直接将其替换成你对应的值：

    
    
    credentials:
    
            MISP_URL: "https://127.0.0.1"
    
            MISP_KEY: "qwertyuiopasdfghjk"

现在，以完整绝对路径加“-s”参数运行下列命令：

    
    
    python3 /home/user/ARTIF/ip_rep/feed_ingestor/update_check.py -s

再运行一次，这次不加“-s”参数：

    
    
    python3 /home/user/ARTIF/ip_rep/feed_ingestor/update_check.py

接下来，使用Django的内置支持添加crontab：

    
    
    python3 manage.py crontab add

从ip_rep目录下启动Django服务器：

    
    
    python3 manage.py runserver

此时将打开端口8000，该端口用于从IP地址获取元数据：

    
    
    curl 127.0.0.1:8000/ip/?ip=x.x.x.x

输出结果类似如下：

    
    
    {"is_IoC": false, "is_Active": false, "metadata": {"asn": "AS165**", "country": "XXX", "org": "XXX"}, "score": 80.14671726301682, "description": "XXX", "blacklists": "", "type": "", "historical":false, verdict": "No action needed"}

## 工具使用演示

 **设置并启动Docker容器：**

![](https://image.3001.net/images/20210828/1630143523_612a04234613f0a3e69db.gif)

 **开启ARTIF：**

![](https://image.3001.net/images/20210828/1630143640_612a0498e2ecd3ac7ac1a.gif!small)

## 工具使用样例

我们需要使用update_check.py来调用ARTIF：

    
    
    ubuntu@localhost:~/ARTIF/ip_rep/feed_ingestor$ python3 /home/user/ARTIF/ip_rep/feed_ingestor/update_check.py -h
    
    usage: update_check.py [-h] [-s [S]] -k [KEY] -m MISP
    
     
    
    IP reputation program
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -s [S]                Required only for the first run

我们也可以通过运行下列命令来查看cron任务：

    
    
    python3 manage.py crontab show

默认配置下，每24小时工具都会检测一次MISP并获取最新的feed。

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/CRED-Dev/ARTIF/blob/develop/LICENSE)开源许可证协议。

## 项目地址

 **ARTIF：** 【[ _GitHub传送门_](https://github.com/CRED-CLUB/ARTIF)】

