##  0x00 前言

 **Pigat即Passive Intelligence Gathering Aggregation
Tool，翻译过来就是被动信息收集聚合工具，既然叫聚合工具，也就是说该工具将多款被动信息收集工具结合在了一起，进而提高了平时信息收集的效率。**

早在半个月前便萌生了开发这个工具的想法，但是一直没有时间，正好最近有时间了，就简单写一下。

因为我没有太多的开发经验，所以这款工具难免存在需要改进的地方，因此希望各位大佬能够多多反馈这款工具存在的问题，一起完善这个工具。

##  0x01 工具原理及功能概述

这款工具的原理很简单，用户输入目标url，再利用爬虫获取相关被动信息收集网站关于该url的信息，最后回显出来。

目前该工具具备8个功能，原该工具具备7个功能，分别为收集目标的资产信息、CMS信息、DNS信息、备案信息、IP地址、子域名信息、whois信息，现加入第8个功能：如果在程序中两次IP查询目标URL的结果一致，那么查询该IP的端口，即端口查询功能。

##  0x02 工具简单上手使用

###  1、查看帮助信息

    
    
    # python pigat.py -h

![](https://image.3001.net/images/20191112/1573528373_5dca23351eaba.png!small)

###  2、指定url进行信息获取

如果只指定url这一个参数，没有指定其他参数，则默认获取该url的所有信息

    
    
    # python pigat.py -u teamssix.com

![](https://image.3001.net/images/20191111/1573462276_5dc921041a973.png!small)

![](https://image.3001.net/images/20191111/1573462289_5dc921113e310.png!small)

###  3、指定url进行单项信息获取

    
    
    # python pigat.py -u baidu.com --assert

![](https://image.3001.net/images/20191111/1573462313_5dc921296a9e9.png!small)

###  4、指定url进行多项信息获取

    
    
    # python pigat.py -u teamssix.com --ip --cms

![](https://image.3001.net/images/20191111/1573462323_5dc92133bbc97.png!small)

##  0x03 工具获取

> GitHub地址：<https://github.com/teamssix/pigat>

 ***本文作者： TeamsSix，转载请注明来自FreeBuf.COM**  
  

