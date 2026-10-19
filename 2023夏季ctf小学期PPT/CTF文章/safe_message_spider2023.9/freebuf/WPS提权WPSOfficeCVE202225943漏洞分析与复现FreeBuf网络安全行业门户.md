## **漏洞概述**

WPS
Office安装时，会以管理员权限安装服务程序wpscloudsvr，该服务程序配置为手动启动，但错误配置了该服务程序所在文件夹的访问控制列表（ACL）属性，普通Users组成员仍然对该文件夹有读写权限。

##  **影响范围**

WPS Office版本小于11.2.0.10258均存在该漏洞。  
（WPS版本号看最后一组，最后一组数字大即为新版本，11.1表示个人版，11.2表示企业版，11.6和11.8表示政企定制版）

##  **利用场景**

普通Users组成员在服务程序wpscloudsvr所在文件夹放置被劫持的DLL文件，以普通用户权限启动该服务，最终DLL被服务程序加载执行，实现本地提权。

（wpscloudsvr服务程序自身并不存在DLL劫持漏洞，可使用系统DLL劫持漏洞，测试时win7 6.1.7601 sp1
32位系统存在可被利用的系统DLL劫持漏洞，win10 10.0.18363.592 64位不存在可被利用的DLL劫持漏洞）

##  **复现环境**

操作系统：Win7 6.1.7601 sp1 32位WPS Office版本：WPS Office 11.2.0.10200复现工具：Process
Explorer，Process Monitor，CFF Explorer，vs2008

##  **分析过程**

首先使用普通Users组用户登录windows系统，如下图所示。![](https://image.3001.net/images/20220424/1650778458_6264e15ab04f952db7975.png!small)安装WPS
Office
11.2.0.10200.exe程序，安装好后可以看到已经安装了一个名为wpscloudsvr的服务程序，服务程序路径为C:\ProgramData\Kingsoft\office6\wpscloudsvr.exe，该服务配置为手动启动，启动后以System权限运行，如下图所示。![](https://image.3001.net/images/20220424/1650778485_6264e1756f4270c6a2b73.png!small)![](https://image.3001.net/images/20220424/1650778492_6264e17c820f74285958f.png!small)使用icalcs命令查看服务程序所在文件夹的ACL属性，发现普通Users组成员对该路径有写入数据或者添加文件（WD）权限，如下图所示。![](https://image.3001.net/images/20220424/1650778524_6264e19c3a71c0240058f.png!small)使用CFF
Explorer查看服务程序C:\ProgramData\Kingsoft\office6\wpscloudsvr.exe的导入表，发现只有KERNEL32.dll，无可被劫持的DLL，如下图所示。![](https://image.3001.net/images/20220424/1650778543_6264e1aff1ac610d38b88.png!small)使用监控工具Process
Monitor监控服务程序C:\ProgramData\Kingsoft\office6\wpscloudsvr.exe的运行过程，发现可被劫持的DLL文件有cryptsp.dll，cryptbase.dl等，如下图所示。![](https://image.3001.net/images/20220424/1650778562_6264e1c21f0f03746c879.png!small)所以，可以用普通Users组用户权限在服务程序C:\ProgramData\Kingsoft\office6\wpscloudsvr.exe同目录下放置被劫持的cryptsp.dll文件，然后启动wpscloudsvr服务，加载运行被劫持的cryptsp.dll，实现普通用户权限提升到系统权限。

##  **复现过程**

为简单起见，复现代码借鉴自https://github.com/HadiMed/KINGSOFT-WPS-Office-LPE，演示本地提权。这里主要阐述下这部分代码的逻辑。首先需要编译被劫持的cryptsp.dll文件。在该DLL运行时，激活系统超级管理员，并修改其密码，以备后续登录使用，如下图所示。  
![](https://image.3001.net/images/20220424/1650778582_6264e1d6898d25d749dc1.png!small)然后编译exploit.exe利用程序。该程序运行时，复制编译好的cryptsp.dll文件到C:\ProgramData\Kingsoft\office6\wpscloudsvr.exe同目录下，然后启动wpscloudsvr服务程序，以便运行被劫持的cryptsp.dll文件，实现激活系统超级管理员，并修改其密码的功能，如下图所示。![](https://image.3001.net/images/20220424/1650778602_6264e1eae876e0f315c9e.png!small)  
然后使用该系统超级管理员登录系统，并此账号权限运行另一利用程序nt_sys.exe，如下图所示。![](https://image.3001.net/images/20220424/1650778628_6264e204487fe24c677b6.png!small)![](https://image.3001.net/images/20220424/1650778634_6264e20a5323a552c8ddf.png!small)最后编译nt_sys.exe利用程序。该程序运行时，首先设置自身权限为SeDebugPrivilege，然后打开winlogon.exe进程（该进程为System权限），获取其Token，最后以此Token创建C:\Windows\System32\cmd.exe进程，实现提权，如下图所示。![](https://image.3001.net/images/20220424/1650778666_6264e22abd2170a64374d.png!small)![](https://image.3001.net/images/20220424/1650778672_6264e2304200bfdf8d3b7.png!small)编译好后，应该有cryptsp.dll，exploit.exe，nt_sys.exe三个程序，将其放到同一目录下，以普通用户权限运行exploit.exe，利用该漏洞，可以实现以system权限运行cmd.exe，实现提权，如下图所示。  
 **备注：** 公众号（ **Beacon Tower Lab** ）回复“CVE-2022-25943”可获取该漏洞研究相关工具。  
 **由于传播、利用此提供的信息而造成任何直接或间接的后果及损害，均由使用本人负责，本公众号及文章作者不为此承担任何责任。**

##  **参考链接**

[https://github.com/HadiMed/KINGSOFT-WPS-Office-LPE﻿](https://github.com/HadiMed/KINGSOFT-WPS-Office-LPEhttps://jvn.jp/en/vu/JVNVU90673830/)

[https://jvn.jp/en/vu/JVNVU90673830/](https://github.com/HadiMed/KINGSOFT-WPS-Office-LPEhttps://jvn.jp/en/vu/JVNVU90673830/)

<https://www.cvedetails.com/cve/CVE-2022-25943/?q=CVE-2022-25943>[原文链接](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247484324&idx=1&sn=7effb1ea514ce6a1c8195f5772c905d8&chksm=c2a1d72df5d65e3b6cce0d4c110be831dbd67305c9d4bd42cd47e43b5ac803f6e64a4d2ff80f&token=382247621&lang=zh_CN#rd)

