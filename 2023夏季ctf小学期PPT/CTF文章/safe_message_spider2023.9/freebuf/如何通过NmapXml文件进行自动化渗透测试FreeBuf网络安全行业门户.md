**今天，小编将教大家如何在Pentest-Machine的帮助下，通过一份Nmap
XML文件来实现[自动化渗透测试](https://www.kitploit.com/search/label/Pentesting)。**

![1111111111111.png](https://image.3001.net/images/20181114/1542174528_5bebb740b719a.png!small)

## Pentest-Machine

Pentest-Machine是一款自动化渗透测试辅助工具，分析命令执行完成后，它会将对应的输出结果打印到终端上，同时将结果分别存储到对应的output-by-service/和output-by-host/目录中。

### >HTTP

>whatweb

>WPScan（只有当[whatweb](https://www.kitploit.com/search/label/WhatWeb)返回的结果是[WordPress](https://www.kitploit.com/search/label/WordPress)时才执行）

>EyeWitness主动登录尝试

>轻量级dirb目录爆破

### >DNS

>Nmap NSE DNS区域传送和DNS递归查询

### >MySQL

>轻量级[patator](https://www.kitploit.com/search/label/Patator)爆破

### >PostgreSQL

>轻量级patator爆破

### >MSSQL

>轻量级patator爆破

### >SMTP

>Nmap NSE smtp枚举用户和smtp开放中继

### >SNMP

>轻量级patator爆破

>snmpcheck（如果patator成功找到了一个字符串）

### >SMB

>enum4linux -a

>nmap NSE SMB枚举共享、SMB漏洞ms08-067、SMB漏洞ms17-010

### >SIP

>nmap NSE SIP枚举用户、SIP方法

>svmap

### >RPC

>showmount -e

### >NTP

>nmap NSE ntp-monlist

### >FTP

>轻量级patator爆破

### >Telnet

>轻量级patator爆破

### >SSH

>轻量级patator爆破

### >WordPress4.7

>XSS内容上传

## 工具安装

    
    
    ./setup.sh
    
    source pm/bin/activate

## 工具使用

首先，读取[Nmap](https://www.kitploit.com/search/label/Nmap) XML文件：

    
    
    sudo ./pentest-machine -x nmapfile.xml

配合主机列表hostlist执行Nmap扫描，然后Nmap会根据扫描结果来扫描前1000个TCP端口和前100个UDP端口，并对目标主机的运行服务进行枚举，最终的分析结果会以pm-nmap.[xml/nmap/gnmap]的形式存储在当前的工作目录中：

    
    
    sudo ./pentest-machine -l hostlist.txt

使用-s参数，可以跳过patator暴力破解以及所有的SIP或HTTP命令，该参数后面还可以跟其他的协议名称：

    
    
    sudo ./pentest-machine -s patator,sip,http -x nmapfile.xml

## 工具下载

Pentest-Machine：<https://github.com/DanMcInerney/pentest-machine>

 ***参考来源：[kitploit](https://www.kitploit.com/2018/10/pentest-machine-automates-some-pentest.html?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+PentestTools+%28PenTest+Tools%29)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

