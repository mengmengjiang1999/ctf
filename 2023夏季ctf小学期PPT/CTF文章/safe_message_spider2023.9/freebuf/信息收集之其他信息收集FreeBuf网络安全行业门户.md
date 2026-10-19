  

之前我们分享了域名收集的思路和方法、信息搜集中还有诸如C段资产、端口搜集、APP搜集、小程序、公众号收集。都是获取目标有效信息的方法。本次将从以下这些方法为大家讲解。

## 段资产收集

### 网络空间搜索引擎

通过第三方搜索引擎搜索目标IP以及C段资产，来找到目标资产的IP地址

使用如下关键词来找到目标资产的IP地址

title:"知道创宇" +country:"CN" -subdivisions:"香港"

![](https://image.3001.net/images/20220628/1656395928_62ba9898232765d8b4c6a.png!small)

根据网站的ico进行搜索

iconhash:"3ae0b66d54edf1518e9111de361fdbba"

![](https://image.3001.net/images/20220628/1656395943_62ba98a7b0ef06cd55e3d.png!small)

可以根据已知网站中的一些标识来使用body搜索，如邮箱、备案号等等

body:"知道创宇"

![](https://image.3001.net/images/20220628/1656395961_62ba98b9176016fa37544.png!small)

根据搜集到的IP地址进行C段查询

cidr:"1.2.3.4/24"

![](https://image.3001.net/images/20220628/1656395976_62ba98c8c58575fbe2531.png!small)

列举一些常用的搜索引擎

  * Zomeye
  * Fofa
  * 360quake
  * shodan

## C段扫描工具

除了通过网络空间搜索引擎来搜索目标的C段资产，还可以通过一些工具进行资产搜索

  * Goby

Goby的优势是方便直观，且支持POC进行漏洞扫描，可自定义POC

![](https://image.3001.net/images/20220628/1656396007_62ba98e7327a91236363f.png!small)

  * shuize

python3 ShuiZe.py -c 192.168.1.0,192.168.2.0,192.168.3.0

水泽自带资产探活、支持漏洞验证、Host碰撞

![](https://image.3001.net/images/20220628/1656396023_62ba98f7366da3bf7421c.png!small)

  * fscan

fscan.exe -h ip/24

扫描速度快，支持漏洞验证

![](https://image.3001.net/images/20220628/1656396204_62ba99acf281d16c0fc95.png!small)

  * ALLin

python AlliN.py --host 10.1.1.1/24 -p 80 -m pscan

一款红队信息搜集工具，被动识别访问站点是否是云上站点

 ** **\****端口信息搜集

既然已经有了C段的资产，那么针对网站这里，IP开放的端口也是必须要整起来的。

  * 御剑端口扫描

![](https://image.3001.net/images/20220628/1656396230_62ba99c6a1762e021162d.png!small)  

  * fscan

fscan.exe -h 192.168.1.1 -p 1-65535

  * Nmap

nmap的使用方法就不用多说了，是一款一直都在用的工具、该工具扫描速度较慢

  * Msscan

扫描速度虽然快，但是精准度不够

masscan -p80,8000-8100 10.0.0.0/8 --rate=10000

## 存活资产探测

C段+全段口会生成很多资产，但是其中会有不能访问的，所以我们需要资产探活

  * ehole

使用方法就是，直接加IP地址段或者域名列表

EHole -l url.txt

![](https://image.3001.net/images/20220628/1656396252_62ba99dc89c4a7852388a.png!small)

  * Finger

python3 Finger.py -h

![](https://image.3001.net/images/20220628/1656396268_62ba99ec6874bd9b1e348.png!small)

  * test404

![](https://image.3001.net/images/20220628/1656396325_62ba9a2566d09ad9d16be.png!small)  

## 敏感信息

在获取了目标资产，就是对目标网站的敏感信息搜集，诸如泄露的账号和路径等等

 ** **\****目录扫描

在目标资产收集完毕后，可以都某些服务进行目录扫描，可能会存在敏感信息

  * dirsearch

python3 dirsearch.py -u url -e *

![](https://image.3001.net/images/20220628/1656396310_62ba9a167dd4cbef383b6.png!small)

  * dirb

kali自带扫描工具，dirb的字典还是不错的

  * 御剑

windows下的图形化工具，显示方便

![](https://image.3001.net/images/20220628/1656396384_62ba9a6039379715934e0.png!small)

 ** **\****JS信息搜集

在JS中可能会存在某些服务的接口，测试这些接口是否有未授权等、或者也会存在一些子域名，或者测试域名在其中，或者诸如用户密码等敏感信息  
可以全局搜索http、"/、这种关键词

![](https://image.3001.net/images/20220628/1656396410_62ba9a7a25148d3725a79.png!small)  

  * JSfinder

jsfinder可以匹配网站Js中的接口和地址

![](https://image.3001.net/images/20220628/1656396423_62ba9a8731d420aafb97c.png!small)

  * Hae

burp中的插件，可以自定义正则来匹配敏感信息、比如匹配手机号等、有时js会泄露测试账号、配置等

## GitHub信息搜集

github作为全球的开发使用网站、有些开发会在上面发布公司测试的代码、或者一些测试，利用github搜索关键词，或者结合特定语法来使用，效果更佳

site:Github.com inurl:sql

site:Github.com svn username password

等等

![](https://image.3001.net/images/20220628/1656396436_62ba9a94541728aa320c0.png!small)

## 网盘信息搜集

某些人员可能上传资料到一些网盘中，没有加密码、或者密码泄露、导致信息被泄露。

https://www.feifeipan.com/

![](https://image.3001.net/images/20220628/1656396453_62ba9aa59bb26948aae34.png!small)

## 谷歌信息搜集

利用谷歌语法进行敏感信息搜集

site:xxx.com filetype:doc intext:pass

site:xxx.com filetype:xls intext:pass

site:xxx.com filetype:conf

site:xxx.com filetype:inc

filetype:log iserror.log

## 公众号、小程序搜集

在web资产有限的情况下，可以通过公众号来进行渗透。也可以获取冷门资产。

  * 利用企查查搜索公众号  
搜索相应公司，点击其知识产权

![](https://image.3001.net/images/20220628/1656396501_62ba9ad5e84ad64aba9df.png!small)  

  * 搜狗搜索

![](https://image.3001.net/images/20220628/1656396520_62ba9ae8cfe7543a35922.png!small)  

  * 直接在微信上搜索相应公众号名字、小程序

## APP信息搜集

  * 七麦APP搜索

直接搜索公司名字、或者搜索开发者名字

![](https://image.3001.net/images/20220628/1656396547_62ba9b03af433f40784e0.png!small)

  * 豌豆荚

![](https://image.3001.net/images/20220628/1656396562_62ba9b126a1f58ab354a1.png!small)  

  * 爱应用

![](https://image.3001.net/images/20220628/1656396577_62ba9b21e14752628f012.png!small)  

  

