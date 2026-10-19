前言：分享一下有关信息收集方面的操作，如有不正，请大佬轻喷斧正。  
第一次写文章，思路可能会有点乱，主要目的是分享打点前和打点时如何进行信息收集

# 完整流程

总结一下信息收集的全部过程，为什么放在最前面是因为想先将信息收集的框架，从什么地方开始，到收集什么东西，到哪里去收集这些东西，并列出相应的工具。带着思路往下看，也许能记得更牢一点。

## 从什么地方开始

这一步主要是先明确自己的目标，假如是挖专属src，那么在正文内会标注出漏洞收集的范围。如果是公益src，就看发现的目标是域名还是ip。  
目标是域名，先从挖掘子域名之类的地方开始，可以使用OneForAll、shuize、在线挖掘工具、网络测绘引擎等。碰到域名可能是CDN的情况，还要想办法找到目标的真实地址，例如邮件、旁站、子域名等。  
目标是IP，可以眼看IP的C段，若是只有IP找不到归属的情况，可以去ICP备案或者IP反查域名处查找，加入找到域名，可以重复上面的步骤，若是只有IP，可以看logo、查ICON、打点成功后观察有无能证明归属的。  
网站打点时，路径、js、指纹、敏感信息等尤为重要。爆破路径如：dirsearch、御剑。js：JsFinder。指纹：Ehole、在线指纹探测。敏感信息：例如员工账号、手机号码、github敏感信息等。账号可能在网站页面就已经标出来了，比如说页脚的技术支持人员：123XXXX1234（XX），或是在登录界面时，发现不存在用户、密码错误、账号被冻结的返回包不一样。也可以拿到账号。或是爱企查、whois之类地方拿到的邮箱，扫描时拿到的邮箱，都有可能成为突破口

# 资产收集

一般而言，比如收集src的信息又或是攻防演练的信息，能够明确的知道目标的域名，因此先由域名起分享  
以domain.com为例

## 子域名收集

### OneForALL

python3 oneforall.py --target domain.com run  
可以收集网站url、端口、存活、是否为cdn等进行收集  
![image.png](https://image.3001.net/images/20221212/1670783859_63962373142330e1db333.png!small)

### 水泽

可以收集子域名、github敏感信息（需要key）、联和网络测绘引擎（需要key）、自动进行host碰撞，有漏洞验证功能（感觉是图一乐）  
python3 ShuiZe.py -d domain.com 收集单一的根域名资产  
python3 ShuiZe.py --domainFile domain.txt 批量跑根域名列表  
python3 ShuiZe.py -c 192.168.1.0,192.168.2.0,192.168.3.0 收集C段资产  
python3 ShuiZe.py -f url.txt 对url里的网站漏洞检测  
python3 ShuiZe.py --fofaTitle XXX大学 从fofa里收集标题为XXX大学的资产，然后漏洞检测  
python3 ShuiZe.py -d domain.com --justInfoGather 1 仅信息收集，不检测漏洞  
python3 ShuiZe.py -d domain.com --ksubdomain 0 不调用ksubdomain爆破子域名  
![image.png](https://image.3001.net/images/20221212/1670816796_6396a41cbbb16b6aa5bd5.png!small)

### 在线子域名挖掘工具

优点是无需自己扫描，缺点是根据网站的字典以及探测方式，收集的结果可能有遗漏  
![image.png](https://image.3001.net/images/20221212/1670783563_6396224bb03eb64efc763.png!small)

### 网络测绘引擎

使用语法domain="domain.com"  
![image.png](https://image.3001.net/images/20221212/1670784555_6396262b66e170322c809.png!small)  
或是使用icon查询  
![image.png](https://image.3001.net/images/20221212/1670784657_63962691411ae6f163a92.png!small)  
个人感觉hunter子域名查询有点东西，能找到水泽和OneForAll都没爆破出来子域名  
![image.png](https://image.3001.net/images/20221212/1670784985_639627d952aaa8041b66e.png!small)  
以及其他的查询语法，这里就不过多介绍了

## 微信公众号

可以使用搜狗搜索  
![image.png](https://image.3001.net/images/20221212/1670819987_6396b093c8fbe1e011c87.png!small)

## IP/C段信息收集

如何找IP和C段不过多赘述，浅谈一下利用方法

### 水泽

python3 ShuiZe.py -c 192.168.1.0,192.168.2.0,192.168.3.0

### Goby

![image.png](https://image.3001.net/images/20221212/1670816698_6396a3ba24e774fa7063d.png!small)

### Vscan

漏扫工具，可以探测端口以及漏洞验证并收集网站信息、探测指纹  
会对 127.0.0.1 进行http常用端口扫描，扫描完端口后对端口地址进行检测  
vscan -host 127.0.0.1

不会对 127.0.0.1 进行端口扫描，而是直接对 http://127.0.0.1:7001 地址进行检测  
vscan -host http://127.0.0.1:7001

对 192.168.1.1/24 C段进行端口扫描，扫描完端口后对端口地址进行检测  
vscan -host 192.168.1.1/24

对 ips.txt 内的 ip/域名/c段/url地址 进行逐行检测(如果有url地址，则不会进行端口扫描)  
vscan -l ips.txt  
![image.png](https://image.3001.net/images/20221212/1670830869_6396db15180dfbdfa461e.png!small)

### IP反查域名

![image.png](https://image.3001.net/images/20221212/1670821173_6396b535bf5933098c8a0.png!small)

### ICP备案

![image.png](https://image.3001.net/images/20221212/1670821339_6396b5db4d40b069dfaf9.png!small)

## 指纹探测

### Ehole

便于收集url的指纹，会有专门有一个重点资产的列表，还可以探测网站存活  
![image.png](https://image.3001.net/images/20221212/1670817057_6396a521a31a3e301ec55.png!small)

### Wappalyzer

浏览器插件，用于打点时候的信息收集  
![image.png](https://image.3001.net/images/20221212/1670817210_6396a5baaafc775fe72fc.png!small)

### ShiroScan & FastJsonScan

burpsuite被动扫描工具，一般放着当不存在好了，等摸完打点没有头绪的时候点进来，说不定有惊喜  
![image.png](https://image.3001.net/images/20221212/1670817398_6396a676ef3a675ee45e2.png!small)

## 敏感信息收集

### 账号

#### 网站的页脚

一些网站的页脚，有像这样的技术支持的电话号码，像这种很有可能是存活账号  
![image.png](https://image.3001.net/images/20221212/1670817728_6396a7c062d60a7721cf9.png!small)

#### 网站的返回

像是本应返回账号或密码错误的地方，但返回的却是详情信息，可以爆破账号拿到存活的账号  
![image.png](https://image.3001.net/images/20221212/1670817961_6396a8a98270f778ce26a.png!small)  
可以明显看到，没有账号和密码错误和已经账号被锁定的返回是不一样的  
![image.png](https://image.3001.net/images/20221212/1670818040_6396a8f8a2c7aada16a5b.png!small)  
![image.png](https://image.3001.net/images/20221212/1670818061_6396a90ddbc584cc7939c.png!small)  
![image.png](https://image.3001.net/images/20221212/1670818094_6396a92e9ef67634307c9.png!small)

#### whois

一般whois可能会对邮箱进行打码处理，可以尝试使用科学的whois，有可能能拿到有用的email  
![image.png](https://image.3001.net/images/20221212/1670820412_6396b23cacadd42f2c05d.png!small)

#### Exchange

通过脚本爆破账号，在爆破之前需要先去搜集邮箱的命名格式  
![image.png](https://image.3001.net/images/20221212/1670820688_6396b3504e5d276baedf8.png!small)

### 路径

#### dirsearch

![image.png](https://image.3001.net/images/20221212/1670818382_6396aa4ebce0fb805ac77.png!small)

#### FindSomething

浏览器插件，可以看到路径和一些js  
![image.png](https://image.3001.net/images/20221212/1670818473_6396aaa9b564fbeaa4022.png!small)

#### JsFinder

用来匹对网站中的一些JS接口

#### 御剑目录扫描

![image.png](https://image.3001.net/images/20221212/1670818686_6396ab7eb9c2da203b0ed.png!small)

### 网盘

浏览器搜索网盘查询，随便选一个点进去，然后查询是否有放在网盘上的备份包或使用手册资料的  
![image.png](https://image.3001.net/images/20221212/1670819569_6396aef1295f9280bec21.png!small)

### github敏感信息

得看有没有幸运儿上传自己的源码或网址配置了  
![image.png](https://image.3001.net/images/20221212/1670819766_6396afb6c8c65354a9ecd.png!small)

## 供应链

之前跟着打hw时学到的，可能讲的不完全正确，主要分享另一种信息收集思路

### 企业标讯

看中标信息，在里面选择供应链打  
![image.png](https://image.3001.net/images/20221212/1670819012_6396acc45c16db2220586.png!small)  
实际感觉：比较盲目，成功率低，也可能是我姿势不对

### 模板 or 技术支持

截图只是做个示例，实际打点时可以对这些表明模板或技术支持来源的供应链作为模板  
![image.png](https://image.3001.net/images/20221212/1670819316_6396adf4eb9a37bfa5849.png!small)

