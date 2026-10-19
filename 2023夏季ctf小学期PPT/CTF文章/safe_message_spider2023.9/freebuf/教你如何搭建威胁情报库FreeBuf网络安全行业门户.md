## ****一、前言 ****  

**威胁情报是一种基于数据的，对组织即将面临的攻击进行预测的行动。预测（基于数据）将要来临的的攻击。威胁情报利用公开的可用资源，预测潜在的威胁，可以帮助你在防御方面做出更好的决策。
在企业或政府乃至国家，拥有一个高准确度，大数据量的威胁情报库是至关重要的。**

##  **二、简介**

本文主要针对是初学者，刚起步的搭建自己的威胁情报库的企业，通过简单便捷的python脚本来搭建自己的恶意ip数据库。此恶意数据库的IP来源于国外较为权威的威胁情报。本文只是讲述其中的黑名单ip如何搜集，方向还可以拓展为恶意域名，恶意证书，可用类似方法。之所以要收录国外的开源情报威胁库，更大程度上是因为国内各个网络安全公司不会将自己的数据库分享，也是用与我一样的思路爬取国外信息为主。

##  **三、黑名单IP（C＆C，恶意软件，垃圾邮件，网络爬虫）**

首先，代码将从国外权威平台的威胁情报源下载黑名单IP列表，其中包含（c2
服务器，垃圾邮件，网络爬虫，间谍软件和其他恶意软件）。并且在收集含有黑名单ip的文件同时，还需要聚合筛选数据，只提取重要可用的数据。

我们需要将下面的命令写入cron中，可用来每5分钟自动下载一次黑名单IP  

    
    
    """  
    crontab -e  
    """

在配置文件中添加下面三行

    
    
    """  
    */5 * * * * cd && wget <http://osint.bambenekconsulting.com/feeds/c2-ipmasterlist.txt>  
    */5 * * * * cd && wget reputation.alienvault.com/reputation.data  
    */5 * * * * cd && wget <https://myip.ms/files/blacklist/general/latest_blacklist.txt>

![](https://image.3001.net/images/20190820/1566265698_5d5b51629a1e3.png!small)

在Home中，创建新py文件叫merge.py  

    
    
    """  
    Filename: merge.py  
    Arthor:Mike  
    Date:2019.8.5  
    """

打开文件

    
    
    c2=open("c2-ipmasterlist.txt","r")  
    bl=open("latest_blacklist.txt","r")  
    reputation=open("reputation.data","a")

以行来分开下载的数据

 ****

    
    
     **for** line **in** c2:  
      ip = line.split(',')  
      reputation.write(ip[0]+ ",c2\n")  
     **for** line **in** bl:  
      ip = line.split()  
      **try** :  
        reputation.write(ip[0]+ "\n")  
      **except** :  
        **pass**

 ****

在执行代码之前，还需要添加一个命令在cron文件中，它会用下面的命令每5分钟导入黑名单IP列表:

打开cron的配置文件  

    
    
    crontab -e

添加运行每5分钟一次的merge.py文件，用于拓展黑名单数据量。

然后再重启cmikewhorontab服务：

    
    
    service cron restart

这张截图显示merge.py所结合的恶意ip，域名的总文件

![](https://image.3001.net/images/20190820/1566265689_5d5b5159c95df.png!small)

再次创建新py文件，检查IP是否被列入收录中的黑名单。

    
    
    import mmap

打开IP收录文件，检测流量中的IP是否在黑名单中

    
    
    file = open("reputation.data")  
    IP ='207.241.231.146'  
    s = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)  
     **if** s.find(IP) != -1:  
      print "This "+IP+" is blacklisted"  
      file.close()

##  **四、总结**

本文简单地描述如何利用开源威胁情报，帮助我们更好的防护网络不受到恶意的攻击。阅读者可以展开思维，通过爬虫技术去搜集各个情报源的C2数据库。

##  **五、提示**

经提示因为配置文件不同，可能造成一些同学无法启动crontab。这里为更详细的教程图解帮助大家配置威胁情报库。

###  **开启crontab日志**

crontab默认情况下是不执行开启日子的，所以一开始写完后，不能执行，想查看日志，却找不到。所以先开启定时任务的日志来查看

修改rsyslog服务，将 /etc/rsyslog.d/50-default.conf 文件中的 #cron.* 和#daedon.* 前的 # 删掉；

![](https://image.3001.net/images/20190820/1566265711_5d5b516f52d4c.png!small)

用以下命令重启rsyslog服务：

    
    
    service rsyslog restart

然后再重启crontab服务：

    
    
    service cron restart

 ***本文作者：mikewho，转载须注明来自FreeBuf.COM**

