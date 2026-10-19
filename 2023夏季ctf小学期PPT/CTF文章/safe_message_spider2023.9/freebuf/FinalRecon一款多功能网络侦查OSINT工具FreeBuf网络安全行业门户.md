![a.png](https://image.3001.net/images/20190517/1558029241_5cdda3b93808b.png!small)

**今天给大家介绍的是一款名叫FinalRecon的开源情报收集工具，这是一款多合一的多功能网络侦查工具。该工具采用Python开发，遵循模块化架构，可为广大研究人员的网络侦查活动提供帮助。**

## 功能介绍

FinalRecon可提供如下所示的详细信息：

### Header信息

![b.png](https://image.3001.net/images/20190517/1558029269_5cdda3d56a970.png!small)

### WHOIS查询

![c.png](https://image.3001.net/images/20190517/1558029278_5cdda3de5a3d0.png!small)

### SSL证书细节

![d.png](https://image.3001.net/images/20190517/1558029335_5cdda41749b21.png!small)

### 网络爬虫

![e.png](https://image.3001.net/images/20190517/1558029342_5cdda41e171a4.png!small)

注：该工具支持的模块功能仍在添加中…

## 支持平台

1、 Kali Linux v2019.1

2、 BlackArch Linux

## 工具安装

    
    
    git clone <https://github.com/thewhiteh4t/FinalRecon.git> 
    
    cd FinalRecon 
    
    pip3 install -r requirements.txt

## 工具使用

    
    
    python3 finalrecon.py -h 
    
     usage:finalrecon.py [-h] [--headers] [--sslinfo] [--whois] [--crawl] [--full] 
    
                          url 
    
     FinalRecon- OSINT Tool for All-In-One Web Recon | v1.0.0 
    
     positional arguments: 
    
       url        Target URL 
    
     optional arguments: 
    
       -h, --help show this help message and exit 
    
       --headers  Get Header Information 
    
       --sslinfo  Get SSL Certificate Information 
    
       --whois    Get Whois Lookup 
    
       --crawl    Crawl Target Website 
    
       --full     Get Full Analysis, Test All Available Options

## 检测Header：

    
    
     python3 finalrecon.py --headers <url> 

## 检测SSL证书：

    
    
     python3 finalrecon.py --sslinfo <url> 

## 检测WHOIS信息：

    
    
     python3 finalrecon.py --whois <url> 

## 爬取对象：

    
    
     python3 finalrecon.py --crawl <url> 

## 完整扫描：

    
    
     python3 finalrecon.py --full <url> 

## 工具截图

![f.png](https://image.3001.net/images/20190517/1558029348_5cdda42409338.png!small)

## 项目地址

FinalRecon：【[GitHub传送门](https://github.com/thewhiteh4t/FinalRecon)】

***参考来源：[thewhiteh4t](https://github.com/thewhiteh4t/FinalRecon)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**  

