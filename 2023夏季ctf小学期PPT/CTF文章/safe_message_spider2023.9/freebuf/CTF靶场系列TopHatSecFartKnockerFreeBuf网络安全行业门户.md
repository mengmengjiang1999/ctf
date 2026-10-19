# 下载地址

注：只能使用vmbox打开，新增一张网卡修改为桥接模式

    
    
    https://download.vulnhub.com/tophatsec/FartKnocker.ova
    

#

# 实战演练

查找靶机IP

![image.png](https://image.3001.net/images/20191020/1571566685_5dac345dbdb52.png!small)  

扫描靶机开放端口

![image.png](https://image.3001.net/images/20191020/1571566766_5dac34ae31c15.png!small)浏览器打开80端口

![image.png](https://image.3001.net/images/20191020/1571566791_5dac34c713779.png!small)点击wooah超链接，就会下载了一个网络数据包，使用wireshark打开，看到访问的端口好像是端口敲门服务的默认三个端口

![image.png](https://image.3001.net/images/20191020/1571567076_5dac35e4d9e8f.png!small)使用nmap相继敲击这几个端口

![image.png](https://image.3001.net/images/20191020/1571567160_5dac3638ae7c6.png!small)再重新扫描全部端口，发现了一个8888端口开启了

![image.png](https://image.3001.net/images/20191020/1571567248_5dac3690d46e4.png!small)nc过去，回显到一个url

![image.png](https://image.3001.net/images/20191020/1571567497_5dac378984907.png!small)打开浏览器，输入url

![image.png](https://image.3001.net/images/20191020/1571567548_5dac37bc6aef3.png!small)超链接还是一个网络数据包，找到了一个头像

![image.png](https://image.3001.net/images/20191020/1571567660_5dac382caed79.png!small)下面那段不知道什么东西来的，百度翻译一下

![image.png](https://image.3001.net/images/20191020/1571567766_5dac3896e0ad1.png!small)  

按照提示，我使用nc分别敲击1，3，3，7，最后nc1337端口，回显了一个url路径

![image.png](https://image.3001.net/images/20191020/1571568346_5dac3ada78d81.png!small)浏览器打开上面的url，发现了一串base64加密的字符串

![image.png](https://image.3001.net/images/20191020/1571571280_5dac4650ab32a.png!small)

    
    
    root@kali:~# echo "T3BlbiB1cCBTU0g6IDg4ODggOTk5OSA3Nzc3IDY2NjYK" | base64 -d
    Open up SSH: 8888 9999 7777 6666
    root@kali:~# Open up SSH: 8888 9999 7777 6666

按照提示敲击这些端口就可以打开ssh，出现了一个账号和密码

![image.png](https://image.3001.net/images/20191020/1571571545_5dac475954c7a.png!small)登录不进去

![image.png](https://image.3001.net/images/20191020/1571572787_5dac4c331227d.png!small)使用sftp进去

![image.png](https://image.3001.net/images/20191020/1571572894_5dac4c9eb2857.png!small)文件内容

    
    
    root@kali:~# cat nachos 
    Great job on getting this far.
    
    Can you login as beavis or root ?

找到了一个网络数据包

![image.png](https://image.3001.net/images/20191020/1571573097_5dac4d698c73a.png!small)

打开没发现什么东西  
![image.png](https://image.3001.net/images/20191020/1571573542_5dac4f26b8818.png!small)后来查了一下资料，ssh需要shell才可以操作

![image.png](https://image.3001.net/images/20191020/1571573637_5dac4f85da249.png!small)  

系统枚举表明它可能容易受到[CVE-2015-1328的](https://people.canonical.com/~ubuntu-security/cve/2015/CVE-2015-1328.html)攻击，[CVE-2015-1328](https://people.canonical.com/~ubuntu-security/cve/2015/CVE-2015-1328.html)是在用户名称空间内使用overlayfs挂载进行的本地特权升级。允许本地用户利用此漏洞获得系统上的管理特权。

利用过程（CVE-2015-1328）：

![image.png](https://image.3001.net/images/20191020/1571573768_5dac50087dbe8.png!small)  

