![](https://image.3001.net/images/20200805/1596641555.jpg!small)

## HawkScan

HawkScan是一款针对网站的网络侦察和信息收集工具，并且同时支持Python 2.x和Python 3.x环境。

该脚本使用了“WafW00f”项目来在第一阶段执行Web应用防火墙检测。

项目地址：【[ _GitHub传送门_](https://github.com/EnableSecurity/wafw00f)】

该脚本使用了“Sublist3r”项目来执行子域名扫描任务。

项目地址：【[ _GitHub传送门_](https://github.com/aboul3la/Sublist3r)】

该脚本使用了“waybacktool”项目来检测waybackmachine。

项目地址：【[ _GitHub传送门_](https://github.com/Rhynorater/waybacktool)】

除此之外，该工具还能够在扫描一个纯JS实现的网站时，自动激活JS，并且支持添加Dockerfile。

## 功能介绍

  * URL模糊测试和目录/文件检测
  * 针对所有扫描到的文件进行备份/旧文件测试(index.php.bak, index.php~ ...)
  * 检查Header信息
  * 检查DNS信息
  * 检查whois信息
  * User-agent随机化
  * 提取文件
  * 扫描跟踪
  * 检查目标网站中的@mail，判断 @mail是否泄露
  * CMS检测，版本+漏洞
  * 子域名检测
  * 备份系统 (如果脚本停止运行，则会记录当前进程以便下次开启扫描)
  * Web应用防火墙检测
  * 添加个人前缀
  * 自动更新脚本
  * 自定义扫描输出文件 (scan.txt)
  * 检查Github
  * 递归扫描目录/文件
  * 使用认证Cookie执行扫描任务
  * 支持--profil选项绕过profil页面
  * HTML格式报告
  * 同时支持Python 2.x和Python 3.x环境
  * 支持“rate-limit”选项，以防止目标App不稳定 (--timesleep)
  * 检测waybackmachine
  * 根据检测情况自动添加扫描线程，最大为30
  * 在源代码页面中扫描S3 Bucket
  * 判断是否可绕过Web应用防火墙
  * 判断是否可扫描“localhost”主机
  * Dockerfile支持
  * 激活纯JS站点的JavaScript

## 工具安装&配置

首先，广大用户需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/c0dejump/HawkScan.git

接下来，使用下列命令完成工具依赖组件的安装配置：

    
    
    pip(3) install -r requirements.txt

如果pip3命令执行出现问题的话，可以尝试使用下列命令：

    
    
    sudo python3 -m pip install -r requirements.txt

如果在安装“dryscrape”库的过程中遇到问题，请参考这篇【[ _文档_](https://www.it-swarm.dev/fr/python/pip-install-dryscrape-echoue-avec-error-errno-2-ce-fichier-ou-repertoire-srcwebkit-server/827034588/)】解决。

## 工具使用

    
    
    usage: hawkscan.py [-h] [-u URL] [-w WORDLIST] [-s SUBDOMAINS] [-t THREAD] [-a USER_AGENT] [--redirect] [-r] [-p PREFIX] [-o OUTPUT] [--cookie COOKIE_] [--exclude EXCLUDE] [--timesleep TS] [--auto]
    
    optional arguments:
    
     -h, --help         显示帮助信息和退出
    
     -u URL             待扫描的URL地址[必须]
    
     -w WORDLIST        用于URL模糊测试的字典，默认为dico.txt
    
     -s SUBDOMAINS      子域名扫描
    
     -t THREAD          URL模糊测试所使用的线程数量，默认为20
    
     -a USER_AGENT      选择user-agent
    
     --redirect          设置扫描重定向响应 (301/302)
    
     -r                 递归目录/文件      
    
     -p PREFIX          在字典中添加扫描前缀    
    
     -o OUTPUT          将扫描结果输出至site_scan.txt     
    
     -b                 添加一个备份文件扫描，例如'exemple.com/~exemple/, exemple.com/ex.php.bak...'              
    
     -H HEADER_         修改HEADER              
    
     --exclude EXCLUDE  通过定义一个页面或响应码状态类型来排除某个页面                                   
    
     --timesleep TS     如果扫描过程中目标站点不稳定，可以使用timesleep/rate-limit选项
    
     --auto             根据目标站点响应状态自动增加扫描线程，最大为30
    
     --update           工具自动更新

## 使用样例

### 基础使用：

    
    
    python hawkscan.py -u https://www.exemple.com -w dico_extra.txt

### 使用重定向：

    
    
    python hawkscan.py -u https://www.exemple.com -w dico_extra.txt -t 5 --redirect

### 添加备份文件扫描：

    
    
    python hawkscan.py -u https://www.exemple.com -w dico_extra.txt -t 5 -b

### 排除指定的扫描页面：

    
    
    python hawkscan.py -u https://www.exemple.com -w dico_extra.txt -t 5 --exclude https://www.exemple.com/profile.php?id=1

### 排除响应码：

    
    
    python hawkscan.py -u https://www.exemple.com -w dico_extra.txt -t 5 --exclude 403

## 项目地址

HawkScan：【[ _GitHub传送门_](https://github.com/c0dejump/HawkScan)】

