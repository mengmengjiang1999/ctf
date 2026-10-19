![](https://image.3001.net/images/20210609/1623210265_60c039195a2f5919b5daa.png!small)

## 关于TypoDetect

TypoDetect是一款功能强大的域名检测工具，可以帮助广大蓝队研究人员、安全运维人员和企业安全部门检测跟自己域名相似的主动变异型域名，以防止网络犯罪分子利用这些域名进行网络欺诈活动，比如说网络钓鱼攻击或短信欺诈活动。

TypoDetect支持使用IANA网站最新发布的可用版本顶级域名（TLD），区块链DNS中验证的去中心化域名以及DoH服务中报告的恶意软件相关域名等。

为方便用户使用，TypoDetect默认以JSON格式或TXT格式提供分析报告，具体报告的生成格式以及显示类似域名的方法取决于用户的选择。

## 工具安装

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Telefonica/typodetect

接下来，执行工具安装并安装相关的依赖组件：

    
    
    python3 pip install -r requirements.txt

## TypoDetect运行

首先，我们需要在命令行终端中切换到项目所在根目录，然后运行下列命令：

    
    
    python3 typodetect.py -h
    
    
    usage: typodetect.py [-h] [-u UPDATE] [-t N_THREADS] [-d DOH_SERVER] [-o OUTPUT] domain
    
     
    
    positional arguments:
    
      domain                指定需要处理的域名
    
     
    
    optional arguments:
    
      -h, --help            显示帮助信息并退出
    
      -u UPDATE, --update UPDATE
    
                            (Y/N) 是否更新TLD数据库 (默认:N)
    
      -t N_THREADS, --threads N_THREADS
    
                            所要使用的线程数量 (默认:5)
    
      -d DOH_SERVER, --doh DOH_SERVER
    
                            要使用的DoH: [1] ElevenPaths (默认) [2] Cloudfare
    
      -o OUTPUT, --output OUTPUT
    
                            JSON或TXT, 报告文件类型选项 (默认:JSON)

执行简单的分析：

    
    
    python3 typodetect.py <domain>

更新IANA数据库并执行分析：

    
    
    python3 typodetect.py -u y <domain>

多线程分析：

    
    
    python3 typodetect.py -t <number of threads> <domain>

使用不同的DoH（默认使用ElevenPahts或CloudFare）：

    
    
    python3 typodetect.py -d 2 <domain>

创建TXT格式报告：

    
    
    python3 typodetect.py -o TXT <domain>

## 检测报告

在本项目的reports目录下，会保存每次执行后的扫描报告，默认格式为JSON，存储名称为扫描的域名以及日期，样例如下：

    
    
    elevenpaths.com2021-01-26T18:20:10.34568.json

JSON格式报告的数据结构如下所示，其中包含检测到的主动变异域名：

    
    
    { id:
    
        "report_DoH" : <string>
    
        "domain": <string>
    
        "A": [ip1, ip2, ...]
    
        "MX": [mx1, mx2, ...]
    
        }

每个字段包含下列信息：

    
    
    id: 变异整型ID
    
    "report_DoH": ""        - 去中心化DNS域名
    
                  "Malware" - 报告的危险域名
    
                  "Good"    - 报告的良性域名
    
    "domain": 检测到的主动域名变异Mutation detected as active.
    
    "A": 变异域名DNS中的IP地址和A记录
    
    "MX": 变异域名DNS中的IP地址或CNAME记录

## 项目地址

 **TypoDetect：** 【[ _GitHub传送门_](https://github.com/telefonica/typodetect)】

