## 一、现象描述

**近日，深信服EDR产品率先检测到一款新型Linux挖矿木马，经深信服安全专家分析，该病毒利用Confluence漏洞传播，通过定时下载对病毒体进行保活，同时由于病毒会杀掉包含“https://”、“http://”的进程，将导致用户无法下载文件及访问网页，挖矿进程会导致服务器出现卡顿等异常现象。深信服安全团队对该挖矿木马进行了详细的技术分析，并根据其母体文件名将其命名为seasame。**

感染该木马后现象如下，可以看到一个CPU占用异常高的vmlinuz进程以及3个采用7位随机字符拼凑的进程。

![](https://image.3001.net/images/20190424/1556099608_5cc032183b0a4.jpg!small)

另外，还会出现无法使用wget和curl命令，以及无法打开浏览器等问题。

![](https://image.3001.net/images/20190424/1556099612_5cc0321c323a8.jpg!small)

该病毒目前的传播途径主要是利用Confluence近期公布的远程代码执行漏洞CVE-2019-3396和CVE-2019-3398，这里提醒有安装该软件的用户需要注意进行防御。

## 二、详细分析

### 2.1 母体脚本

一些初始化变量如下，其中entropy为C&C服务器字符串的翻转，C&C服务器地址为51[.]15[.]56[.]161[:]443；变量new_bash、new_dog、new_killbot、omelette为后面要创建的文件名，均由7位随机的字符串组成，后面描述这些文件时都直接使用其对应的变量名；_b，_j等变量用于拼凑shell命令。

![](https://image.3001.net/images/20190424/1556099619_5cc0322380d7f.jpg!small)

根据是否存在vmlinuz进程及其CPU占用是否超过30%，判断系统是否已经感染，如果已经感染则杀掉其他CPU占用高于30%的进程并退出脚本：

![](https://image.3001.net/images/20190424/1556099633_5cc032313b03d.jpg!small)

下载挖矿程序omelette及母体脚本seasame到/tmp目录下，并执行挖矿程序。

![](https://image.3001.net/images/20190424/1556099641_5cc03239d1242.jpg!small)

创建crontab定时任务：

![](https://image.3001.net/images/20190424/1556099644_5cc0323ce385c.jpg!small)

创建的定时任务如下，每隔5分钟都会从C&C服务器下载母体脚本seasame到/tmp目录下并执行：

![](https://image.3001.net/images/20190424/1556099648_5cc032402c46d.jpg!small)

删除iptables命令，将wget重命名为wgetak，curl命令重命名为curlak。

![](https://image.3001.net/images/20190424/1556099650_5cc03242f26b2.jpg!small)

创建cloud_agent.service服务：

![](https://image.3001.net/images/20190424/1556099653_5cc03245f3b20.jpg!small)

cloud_agent.service服务如下，同样用于下载并执行母体脚本seasame：

![](https://image.3001.net/images/20190424/1556099657_5cc032495686e.jpg!small)

将bash命令复制到当前目录，然后分别执行3个脚本。new_dog：守护挖矿进程；new_killbot：清除除vmlinuz以外，CPU占用大于30%的进程；prot：杀掉包含“https://”、“http://”、“eval”的进程。

![](https://image.3001.net/images/20190424/1556099660_5cc0324c4e841.jpg!small)

### 2.2 挖矿程序

1.打开相应的文件，如果文件不存在，则生成相应的文件，如下所示：

![](https://image.3001.net/images/20190424/1556099663_5cc0324f3af3b.jpg!small)

2.生成/temp/ec2a6文件，如下所示：

![](https://image.3001.net/images/20190424/1556099750_5cc032a611eda.png!small)

生成的文件，如下所示：

![](https://image.3001.net/images/20190424/1556099754_5cc032aa0e714.png!small)

3.生成/var/tmp/f41，如下所示：

![](https://image.3001.net/images/20190424/1556099792_5cc032d0e20ab.png!small)

4.生成de33f4f911f20761，如下所示：

![](https://image.3001.net/images/20190424/1556099828_5cc032f45ef75.png!small)

生成的文件，如下所示：

![](https://image.3001.net/images/20190424/1556099832_5cc032f8263bf.png!small)

5.获取主机CPU信息，如下所示：

![](https://image.3001.net/images/20190424/1556099954_5cc03372aa4c9.png!small)

6.解密出相应的矿池IP地址:51.38.133.232、51.15.56.161，如下所示：

![](https://image.3001.net/images/20190424/1556099958_5cc03376d5ea8.png!small)

7.然后拼接不同的端口号，组成相应的矿池地址，如下所示：

![](https://image.3001.net/images/20190424/1556100042_5cc033ca3c120.png!small)

组合成的矿池地址列表，如下所示：

    
    
    51.38.133.232:443
    
    51.15.56.161:80
    
    51.38.133.232:21
    
    51.15.56.161:20
    
    51.38.133.232:53
    
    51.15.56.161:53
    
    51.38.133.232:162
    
    51.15.56.161:161
    
    51.38.133.232:990
    
    51.15.56.161:989
    
    51.38.133.232:1111
    
    51.15.56.161:1111
    
    51.38.133.232:2222
    
    51.15.56.161:2222
    
    51.38.133.232:3333
    
    51.15.56.161:3333
    
    51.38.133.232:4444
    
    51.15.56.161:4444
    
    51.38.133.232:8181
    
    51.15.56.161:8080
    
    51.38.133.232:25200
    
    51.15.56.161:25400

8.创建子进程，进行挖矿操作，如下所示：

![](https://image.3001.net/images/20190424/1556100052_5cc033d418925.png!small)

创建挖矿进程过程，如下所示：

![](https://image.3001.net/images/20190424/1556100055_5cc033d751c1c.png!small)

相应的进程信息，如下所示：

![](https://image.3001.net/images/20190424/1556100058_5cc033dac0daa.png!small)

top进程信息，如下所示：

![](https://image.3001.net/images/20190424/1556100062_5cc033de23def.png!small)

9.挖矿进程相关参数，如下所示：

![](https://image.3001.net/images/20190424/1556100065_5cc033e1da386.png!small)

捕获到的相应的流量数据包，如下所示：

![](https://image.3001.net/images/20190424/1556100162_5cc0344282e21.png!small)

挖矿相关流量数据包，如下所示：

![](https://image.3001.net/images/20190424/1556100166_5cc03446c044c.png!small)

矿池IP地址为矿池地址列表中的：51.38.133.232:443

10.连接远程矿池地址，如下所示：

![](https://image.3001.net/images/20190424/1556100465_5cc03571dfa19.png!small)

请求连接51.15.56.161，如下所示：

![](https://image.3001.net/images/20190424/1556100501_5cc0359535169.png!small)

获取到的流量数据，如下所示：

![](https://image.3001.net/images/20190424/1556100535_5cc035b7da0d5.png!small)

如果连接失败，则请求连接51.38.133.232，如下所示：

![](https://image.3001.net/images/20190424/1556100539_5cc035bb428e7.png!small)

返回相应的数据，如下所示：

![](https://image.3001.net/images/20190424/1556100542_5cc035beafb04.png!small)

获取到的流量数据，如下所示：

![](https://image.3001.net/images/20190424/1556100547_5cc035c3d1d4b.png!small)

拼接相应的内容，如下所示：

![](https://image.3001.net/images/20190424/1556100621_5cc0360d6189f.png!small)

然后将获取的内容，写入到/temp/yayscript.sh脚本中，并通过bash执行sh脚本，如下所示：

![](https://image.3001.net/images/20190424/1556100627_5cc036139de2f.png!small)

yayscript.sh的内容，如下所示：

![](https://image.3001.net/images/20190424/1556100630_5cc0361682911.png!small)

## 三、解决方案

病毒检测查杀

1、深信服为广大用户免费提供针对seasame病毒的专杀工具，可下载如下工具，进行检测查杀。

> 下载链接：<http://edr.sangfor.com.cn/tool/clear_seasame.sh>

![](https://image.3001.net/images/20190424/1556100638_5cc0361e606ce.jpg!small)

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

