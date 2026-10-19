**原创： Drac0nids **合天智汇  

知己知彼，百战不殆；不知彼而知己，一胜一负；不知彼，不知己，每战必殆--《孙子·谋攻篇》

信息搜集一直是渗透测试中重要的一个环节，下面是笔者关于信息搜集中可能会用到的一些工具和在线平台的一些总结，如有错误还望指出。

子域名收集  

##

 **下面都以[www.cuit.edu.cn](http://www.cuit.edu.cn)作为范例**

0x01：通过GoogleHacking

site:cuit.edu.cn

  
![图片.png](https://image.3001.net/images/20180705/15307605339180.png!small)  

###  

0x02：通过枚举子域名工具Sublister

###  

从github上面下载

gitclone <https://github.com/aboul3la/Sublist3r.git>

收集cuit.edu.cn的子域名，并输出到subdomain.txt中

pythonsublist3r.py -d cuit.edu.cn -o subdomains.txt

  
![图片.png](https://image.3001.net/images/20180705/15307605499633.png!small)  

![图片.png](https://image.3001.net/images/20180705/15307605707472.png!small)  

0x03：通过子域名爆破工具wydomain下载

gitclone <https://github.com/ring04h/wydomain.git>

库依赖安装

pipinstall -r requirements.txt

字典穷举cuit.edu.cn的子域名，并输出到cuit.txt中

pythondnsburte.py -d cuit.edu.cn -f dnspod.csv -o cuit.txt

  
![图片.png](https://image.3001.net/images/20180705/15307605692681.png!small)  

通过API查询cuit.edu.cn的子域名，并输出到subdomain.txt中

pythonwydomain.py -d cuit.edu.cn -o subdomain.txt

  
![图片.png](https://image.3001.net/images/20180705/15307608556648.png!small)

操作系统识别  

##

操作系统识别

##

0x01：nmap

nmap-O xxx.xx.xx.xxx

  
![图片.png](https://image.3001.net/images/20180705/15307609174899.png!small)  

##  

##

网站后台目录扫描

  
网站后台目录扫描  

##

0x01：dirsearch

###  

下载

gitclone <https://github.com/maurosoria/dirsearch.git>

该工具在python3环境下运行，通过-h命令查看用法

python3dirsearch.py -h

  
![图片.png](https://image.3001.net/images/20180705/15307619973531.png!small)  

我们通过-u参数指定url，通过-e参数指定要查找的文件的后缀（php,asp,html等），我们可以指定多个后缀用逗号隔开，也可以直接用*扫描所有文件

python3dirsearch.py -u <http://www.cuit.edu.cn> -e *

![图片.png](https://image.3001.net/images/20180705/15307620248663.png!small)

python3dirsearch.py -u <http://www.baidu.com> -e *

![图片.png](https://image.3001.net/images/20180705/15307620429204.png!small)

0x02：DirBuster下载地址

(运行需要java环境)

<https://sourceforge.net/projects/dirbuster/files/DirBuster>(jar +
lists)/1.0-RC1/

在高级AdvanceOption中可以设置不扫描的文件类型

  
![图片.png](https://image.3001.net/images/20180705/15307620557040.png!small)  

最基础的用法：设置好目标url，线程数，字典，要搜索的文件后缀

  
![图片.png](https://image.3001.net/images/20180705/15307620623899.png!small)  

点击start（有些时候我们可能会找不到start，这时我们将软件的高度拉高一点就可以看到了）

![图片.png](https://image.3001.net/images/20180705/15307620743922.png!small)  

稍微高级一点的用法就是urlFuzz，我们选择的字典中的值会替换{dir}，然后再拼接到目标url后面，那么我们可以更加灵活的来fuzz某些目录了，而且还可以用来fuzzurl中的get参数名或者值。

  
![图片.png](https://image.3001.net/images/20180705/15307620849570.png!small)  

（注：本文属于合天原创投稿奖励，未经允许，禁止转载！）  
  

