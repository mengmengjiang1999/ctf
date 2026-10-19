萌新在这个平台上的第一篇文章，本文中可能有大多语言非专业术语或者写错的地方， 大佬们轻喷

最近灵机乍现，想着写个小工具用于信息收集，于是就有了这篇文章的诞生

目前的话写了一个子域名收集工具，后续还在完善，那么话不多说开始介绍一番

地址: <https://github.com/ro4lsc/GTL>

## GTL (Get Target Link)

### What can it do?  
它可以获取指定文本中域名(例如: targets.txt)的子域名，并将可以访问的link放到result.txt，子域名放到subdomain.txt

### How to use?  
编辑一个targets.txt，写入需要探测的域名，使用参数-f指定文件

**Usage:**

    
    
    python3 GTL.py -f targets.txt 

吼吼，目前也只是能够获取子域名的链接并且探测是否可以访问，当然一个好的工具不仅仅如此，最近还是比较忙的，后续的话，当然是开发一个端口信息收集脚本+web服务容器指纹识别脚本，哈哈，这也只是想法，实现估计还差得远呢

看到这里大佬们肯定有想法了，使用crawlergo+xray不就是漏扫了吗，hh，我也是有这个想法的，github上已经有大佬实现了，当然也可以直接用那位大佬的脚本配合我这个脚本还是很方便的

这里先放张运行截图

![](https://image.3001.net/images/20200810/1597054802.png!small)

既然都已经到这份上了，那就谈谈我的设计想法吧

程序结构:

├── Core  
│ ├── GetSubdomain.py  
│ └── __init__.py  
├── GTL.py  
├── Script  
│ ├── CheckDomain.py  
│ ├── UseGetSubdomain.py  
│ └── __init__.py

一共四个py文件，那么首先先介绍GTL.py

GTL.py是程序的主要执行程序，是拿来调用各个模块的，目前的话好像没什么好介绍的

GetSubdomain.py中调用了6个接口，用于获取子域名，其内容大多都是将获取的子域名进行处理，然后在调用的时候，return出来

**注: 这里的六个接口是由[国光](https://www.sqlsec.com)大佬的文章中得知**

    
    
    # 爱站
    https://baidurank.aizhan.com/baidu/{domain}/
    
    # 百度云观测
    http://ce.baidu.com/index/getRelatedSites?site_address={domain}
    
    # hackertarget
    https://api.hackertarget.com/hostsearch/?q={domain}
    
    # IP138
    https://site.ip138.com/{domain}/domain.htm
    
    # crt.sh SSL 证书反查
    https://crt.sh/?q=%25.{domain}
    
    # 千寻
    url = 'https://www.dnsscan.cn/dns.html'
    datas = {"ecmsfrom": '8.8.8.8', "show": 'none', "keywords": domain}

UseSubdomain.py用于调用GetSubdomain模块，将获取后的子域名进行去重处理，最终放到subdomain.txt中

Checkdomain.py则是打开subdomain.py，使用多线程访问链接，并将成功访问的链接放到result.txt

程序的主体流程大概就是这样

## 缺陷

目前的工具还是有很多不足，例如效率比较低，UseGetSubdomain.py中调用程序获取子域名的时候是使用的循环，如果使用多线程or多进程效率肯定会提高很多，工具的功能还是比较单一，当然后续肯定会升级滴。

希望大佬们能给我点点star，这也将成为我的最大动力

写的不对的地方，望大佬轻喷。

