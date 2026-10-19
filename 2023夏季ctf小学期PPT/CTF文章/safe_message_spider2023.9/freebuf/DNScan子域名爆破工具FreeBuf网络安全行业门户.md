**目录**

# 一.介绍

DN-scan域名爆破工具，是一款支持多线程、可选择爆破等级等域名爆破工具。

支持操作系统：Windows

# 二.使用方法

    
    
    Usage: dn-scan.exe -d <domin_url> -l <Detect Level> -b
    
    Options:
      -h, --help    show this help message and exit
      -d DOMIN_URL  Input blasting domain name
      -l LEVEL      1.Detect 3,000 domain names
                    2.Detect 30,000 domain names
      -b            DN scan banner display

## 1.爆破子域名数量

子域名爆破数量分为两个档位，第一个档位支持子域名爆破数量为3,000，第二个档位支持子域名爆破数量为30,000。

## 2.使用方法

命令很简单，dn-scan.exe -d <爆破的域名> -l <爆破的子域名数量> -b

举例：dn-scan.exe -d baidu.com - l 1

如果不输入-l选项，默认则为1，也就是爆破3,000个子域名，想支持更多需使用第2等级

## 3.使用过程

    
    
    D:\dn-scan>dn-scan.exe -d baidu.com -l 1
    [-]invalid:ftp.baidu.com
    [*]open:www.baidu.com
    [*]open:mail.baidu.com
    [-]invalid:smtp.baidu.com
    [-]invalid:pop.baidu.com
    [*]open:m.baidu.com
    [-]invalid:webmail.baidu.com
    [-]invalid:pop3.baidu.com
    [*]open:imap.baidu.com
    [-]invalid:localhost.baidu.com
    [*]open:autodiscover.baidu.com
    [-]invalid:admin.baidu.com
    [*]open:bbs.baidu.com
    
    +------------------------+-----------------+------+
    |         Domain         |        Ip       | Code |
    +------------------------+-----------------+------+
    |     www.baidu.com      |   39.156.66.18  | 200  |
    |     mail.baidu.com     |  111.202.115.87 | 302  |
    |      m.baidu.com       |   39.156.66.95  | 200  |
    |    civil.baidu.com     |  117.185.17.208 | 301  |
    |     imap.baidu.com     |  39.156.68.181  | 200  |
    | autodiscover.baidu.com |  111.202.115.87 | 302  |
    |     bbs.baidu.com      |  112.34.111.194 | 301  |
    |    email.baidu.com     |  111.202.115.87 | 302  |
    |     test.baidu.com     |  110.242.69.167 | 200  |
    |     www2.baidu.com     |  112.34.111.153 | 200  |
    |     dev.baidu.com      |  112.34.111.60  | 301  |
    |    mobile.baidu.com    |  112.34.111.126 | 301  |
    |     www1.baidu.com     |   39.156.66.18  | 302  |
    |     img.baidu.com      |  112.34.111.158 | 302  |
    |    media.baidu.com     |  112.34.111.131 | 302  |
    |     wap.baidu.com      |   39.156.66.95  | 200  |
    |     crm.baidu.com      |  39.156.66.150  | 301  |
    |     api.baidu.com      |  112.34.113.76  | 405  |
    |    video.baidu.com     |  180.76.139.133 | 200  |
    |   download.baidu.com   |  112.34.113.31  | 302  |
    +------------------------+-----------------+------+
    Run Time: 20.51 ms

## 3.版本查看

可输入dn-scan.exe -b 查看Banner与版本信息

    
    
    ----------------------------------------------      _____  _   _        _____
     |  __ \| \ | |      / ____|
     | |  | |  \| |_____| (___   ___ __ _ _ __
     | |  | | . ` |______\___ \ / __/ _` | '_ \
     | |__| | |\  |      ____) | (_| (_| | | | |
     |_____/|_| \_|     |_____/ \___\__,_|_| |_|
    
    +-------------------------------------------+
    |    Version：1.0                           |
    |  Introduce：Domain scan                   |
    |       Help：-h or --help                  |
    |     Writer：Captain W                     |
    |       Date：3,000 OR 30,000               |
    +-------------------------------------------+

# 三.下载地址

<https://download.csdn.net/download/weixin_45621683/13993210>

