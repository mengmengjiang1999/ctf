# 概述

近日，阿里云安全监测到Gitlab远程代码执行(CVE-2021-22205)在野利用，其团伙不仅利用4层协议服务进行入侵，还集成了使用比较广的Web
RCE漏洞，最终通过持久化方式进行挖矿、木马后门维持，对用户主机资源、资产产生不良危害，通过攻击手法、文件命名自动确认为8220挖矿团伙最新变种。

阿里云安全持续对最新变种进行监控，发现至10月21日后传播有所上升，11月4日发现利用Gitlab远程代码漏洞进行入侵，提醒广大企业客户注意防护。

![image](https://image.3001.net/images/20211108/1636343083_61889d2bd6b19d822698a.png!small)

# 传播手段

8220挖矿团伙最新变种通过多种漏洞进行入侵和传播，利用xms、xms.ps1等脚本下载挖矿木马并执行，通过cron.d、crontab等进行持久化，通过不同方式收集key、host、user进行对外传播、横向移动。

![image](https://image.3001.net/images/20211108/1636343121_61889d5153b055647f712.jpg!small)

阶段分析

![image](https://image.3001.net/images/20211108/1636343136_61889d60a99200ef28f81.jpg!small)

# 漏洞利用分析

Gitlab远程代码执行漏洞早在2021年4月14日GitLab官方发布的安全更新中修复，利用细节未公布影响面较小，随着近期利用PoC的公布，伴随互联网中仍有大量老版本未做升级，团伙批量入侵已经造成了较大影响。

Gitlab由于存在未授权端点，故未授权情况下可进行访问，漏洞原因为Gitlab
ExifTool没有对传入的图片扩展名进行安全处理，黑客团伙通过构造特定的图片上传服务器即可在远端进行命令执行。8220挖矿团伙变种最新集成Gitlab远程代码执行漏洞(CVE-2021-22205)进行入侵，其Payload如下：

![image](https://image.3001.net/images/20211108/1636343229_61889dbdf3b2c945640df.jpg!small)

除了集成影响面较大的漏洞，变种亦利用多种流行RCE漏洞进行传播以牟取最大利益，通过云端大数据监控，已知的漏洞利用有：

![image](https://image.3001.net/images/20211108/1636343274_61889dea5dfa8cf20a3b5.jpg!small)

# 详细分析

8220挖矿团伙最新变种通过上述多种方式入侵主机后会做持久化和对外传播操作，具体分析如下。

### Linux平台

 **scan.sh分析**

利用scan2对外进行22端口扫描并保存结果到/tmp/ssh_vulnnew.txt文件中，而后筛选过滤至/tmp/ips_check文件，最终调用hxx进行SSH扫描和暴力破解登录，成功后下载xms并执行。

![image](https://image.3001.net/images/20211108/1636343370_61889e4a22d3182219a91.jpg!small)

scan.sh会调用弱密码簿，其中pas存储了5848个弱账号密码，pas2存储了10490个弱账号密码。

![image](https://image.3001.net/images/20211108/1636343467_61889eab542bacb4af3e4.png!small)

####  **xms分析**

xms为bash脚本，主机被入侵后会进行下载并执行。脚本会对已知挖矿木马进行卸载、卸载EDR终端、写crontab持久化、横向移动等操作，并最终执行挖矿木马。

如图xms会判断是否已经进行矿池通信，如果没有则下载xmrig挖矿程序并保存dbused文件名且执行。

![image](https://image.3001.net/images/20211108/1636343497_61889ec9ad696b38e2170.png!small)

xms亦通过下载对应版本Tsunami僵尸程序到本地并命名bashirc。

![image](https://image.3001.net/images/20211108/1636343515_61889edb4bfa106c51bf3.png!small)

对应的Tsunami僵尸网络可以通过IRC协议对肉鸡进行控制，并对外发起UDP、HTTP类型的DDoS攻击。

![image](https://image.3001.net/images/20211108/1636343530_61889eea7f490b9aafb71.png!small)

通过查找主机中存储的ssh秘钥、历史记录、配置文件等进行横向移动。

![image](https://image.3001.net/images/20211108/1636343545_61889ef94cdf382f2c6d4.png!small)

### Windows平台

powershell脚本文件比较简单，结束本地特定端口的进程，而后通过下载二进制进行挖矿。

#### xms.ps1分析

通过netstat遍历进程中对外3333、4444、5555、7777、、9000连接的进程，然后通过Stop-Process结束进程。

![image](https://image.3001.net/images/20211108/1636343595_61889f2b515e4a39987e7.png!small)

远程下载wxm.exe并保存本地文件名，然后连接矿池194.5.249.24、198.23.214.117并进行挖矿。

![image](https://image.3001.net/images/20211108/1636343608_61889f3880c1403072e84.png!small)

# 安全建议

1）Gitlab远程代码执行漏洞(CVE-2021-22205)修复，可通过终端命令查看版本

    
    
    cat /opt/gitlab/embedded/service/gitlab-rails/VERSION
    

当前受影响版本如下

    
    
    11.9 <= Gitlab CE/EE < 13.8.8
    13.9 <= Gitlab CE/EE < 13.9.6
    13.10 <= Gitlab CE/EE < 13.10.3
    

如果当前版本属于上述范围，可通过该链接(<https://about.gitlab.com/update/>)进行升级

2）云防火墙利用大数据对互联网上最新出现RCE进行实时监控，从RCE披露到响应时间整体小于3小时，能够有效阻止客户资产被RCE漏洞攻击，其支持3-7层协议不仅满足对Web网站的HTTP协议的防护，同时支持4层大量TCP/UDP协议的防御。当前云防火墙默认支持对8220挖矿团伙最新变种多种远程命令执行漏洞的防御。

![image](https://image.3001.net/images/20211108/1636343694_61889f8e702292fa756b7.png!small)

3）云防火墙智能策略依据历史流量自学习，提供符合客户业务暴露面收敛的最佳实践，通过“一键下发”或“自主选择”可以实现资产的最大程度的互联网暴露收敛，避免端口对外不当暴露风险，同时有效阻止“重保模式”下网络空间测绘的扫描行为。

![image](https://image.3001.net/images/20211108/1636343757_61889fcdc98855928a9f8.jpg!small)

# IOC

##### IP

194.38.20.31

##### Domain

a.oracleservice.top  
bash.givemexyz.in  
c4k-irc.pwndns.pw  
pwn.givemexyz.in

##### URL

http://194.38.20.31/pas2  
http://194.38.20.31/redis.sh  
http://194.38.20.31/load.sh  
http://194.38.20.31/i686  
http://194.38.20.31/eii.py  
http://194.38.20.31/bashirc.i686  
http://194.38.20.31/banner  
http://194.38.20.31/sshpass  
http://194.38.20.31/sshexec  
http://194.38.20.31/scan2  
http://194.38.20.31/lan.tar.gz  
http://194.38.20.31/xms?git  
http://194.38.20.31/masscan  
http://194.38.20.31/hxx  
http://194.38.20.31/ei.py  
http://194.38.20.31/eee.py  
http://194.38.20.31/scan.sh  
http://194.38.20.31/scan  
http://194.38.20.31/pas  
http://194.38.20.31/pas2  
http://194.38.20.31/nbminer.tar.gz  
http://194.38.20.31/d.py  
http://194.38.20.31/bashirc.x86_64  
http://194.38.20.31/xms.ps1  
http://194.38.20.31/oracleservice.exe  
http://194.38.20.31/mywindows.exe  
http://194.38.20.31/wxm.exe

