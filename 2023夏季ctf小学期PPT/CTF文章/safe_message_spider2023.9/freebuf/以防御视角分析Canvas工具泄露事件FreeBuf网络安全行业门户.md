  

近日，著名商业渗透框架Canvas源码泄露，
**华云安思境安全团队对该事件进行跟踪分析，并且详细分析了Canvas工具的结构以及工具内涉及到的可利用漏洞。**

![v2-e641537dcc74bf1099d07027b2f9eb04_720w.jpg](https://image.3001.net/images/20210311/1615431385_604986d9d1599cf9b3054.jpg!small)

  

##  **Immunity Canvas框架简介**

  

Immunity CANVAS是一套受信任的商业安全评估攻击框架，每月都会发布稳定版本，更新不限于稳定的1
Day漏洞利用插件，专业人员多进行渗透测试和模拟攻击。 **此次CANVAS的泄露版本为7.26，日期为2020年9月，包含上千个漏洞利用代码。**

  

CANVAS主要以漏洞利用为主，其功能完整支持攻击链生命周期，包括信息收集、权限提升、权限维持、凭证获取、横向移动、防御规避和隐蔽隧道功能。并且可以在目标系统和目标整个网络区域之间隐蔽连接，各节点的远程及本地攻击操作具备完善的攻击日志记录。

##  **Immunity Canvas 模块介绍**

  

Canvas框架主体及模块均使用python开发，在安装特定依赖后，Canvas可以安装在Windows、Linux、MacOS系统下，其中主要功能模块如下表所示：

  

![v2-c94a426f043bf143600aa9b383e4917b_720w.jpg](https://image.3001.net/images/20210311/1615431386_604986da2935c83d77b47.jpg!small)

  

![v2-cda7102994b437407f0626452e1cbfbb_720w.jpg](https://image.3001.net/images/20210311/1615431386_604986daa3ea5f96b617d.jpg!small)

  

##  **主要 Exploits 模块介绍**

  

Exp模块包含14个文件夹（clientside config fuzzer local remote server trojancommand DoS
importexport recon reporting tool web）

![v2-7f33ab7ccc3952c77ea9afc368696c7c_720w.jpg](https://image.3001.net/images/20210311/1615431386_604986daec7e7dc68af6c.jpg!small)

  

 **Remote：** 包含四个文件夹，分别为cisco、universal、unix、windows。

  

其中Unix包含多个知名的unix系统下的常用组件漏洞，共计64个。

![v2-21842127684fad54cd8c325701ef904a_720w.jpg](https://image.3001.net/images/20210311/1615431387_604986db538b0939c6a6f.jpg!small)

  

其中Windows中有多个严重漏洞（ms17-010、SMBGhost），漏洞利用插件部分通过python进行编写，共计有142个。

![v2-8a4599d79298b2ad72ce572420596601_720w.jpg](https://image.3001.net/images/20210311/1615431387_604986dba9863c50c00ad.jpg!small)

  

其中 **Web** 目录中包含一些常见web组件漏洞，共计有237个漏洞。

![v2-9e01b705995a012f86909458cc00477d_720w.jpg](https://image.3001.net/images/20210311/1615431388_604986dc0d14da139f1c8.jpg!small)

  

  

##  **远程漏洞利用功能复现**

  

 **Moudles && Search**

  

这里可以修改工具的攻击模块，实现配置中的功能。它存在多个攻击模块，包括主机发现、漏洞扫描、漏洞利用，漏洞模块目录区分较为详细，以操作系统进行分类：

![v2-a63506437107044ecfb1b919ca1a4f7d_720w.jpg](https://image.3001.net/images/20210311/1615431388_604986dc7984e570a2e77.jpg!small)

  

添加攻击目标

![v2-457952917d845cef3d71f1efd5214e19_720w.jpg](https://image.3001.net/images/20210311/1615431388_604986dcc38495220c62c.jpg!small)

  

![v2-4bfd3f9ef8dc1ef604ec1f38ae61a152_720w.jpg](https://image.3001.net/images/20210311/1615431389_604986dd2293b38848e5b.jpg!small)

  

批量探测模块探测 445端口

![v2-41d7281092307e8d385fc406a0726484_720w.jpg](https://image.3001.net/images/20210311/1615431389_604986dd5faeb6f1008b8.jpg!small)

  

通过批量探测445端口，发现多个IP开放此端口

![v2-b72d046ce062ec492deb4d1ee648ffc0_720w.jpg](https://image.3001.net/images/20210311/1615431389_604986ddb25da204a2b4a.jpg!small)

  

使用较为稳定的 ms17-010 漏洞进行攻击测试

![v2-a6ed313027b7fbb3a037517c529a3a13_720w.jpg](https://image.3001.net/images/20210311/1615431390_604986de212b901cda9f6.jpg!small)

  

  

使用ms17-010 漏洞攻击成功，返回beacon

![v2-74c7562cd8472bc32a1f7e36dbe4c3af_720w.jpg](https://image.3001.net/images/20210311/1615431390_604986dece06e0a48caf2.jpg!small)

  

  

使用命令执行功能

![v2-45ae33c35c6cb349ade35c530a1cf4da_720w.jpg](https://image.3001.net/images/20210311/1615431391_604986df366635881ee40.jpg!small)

  

## Canvas泄露的工具包相暂未发现0day

  

通过将工具包中的漏洞统计，我们发现其中老漏洞比较多，新漏洞比较少，近两年的漏洞占比小于5%，暂时未发现武器库中存在0day漏洞。

  

##  **Canvas中相关重要漏洞信息**

  

 **1.CVE-2020-0796**

微软SMBv3
Client/Server远程代码执行漏洞。该漏洞存在于srv2.sys文件中，由于SMB没有正确处理压缩的数据包，在解压数据包的时候使用客户端传过来的长度进行解压时，并没有检查长度是否合法，最终导致整数溢出。

  

 **2.CVE-2020-0688**

Exchange远程代码执行漏洞。Microsoft
Exchange在处理内存中的对象时，存在远程代码执行漏洞。攻击者可以通过发送特制电子邮件来在受影响的Exchange服务器上以系统级权限执行代码，过程中不需要其他用户交互。

  

 **3.CVE-2019-19781**

CVE-2019-19781是利用两个漏洞组合进行远程代码执行攻击，所利用的两个漏洞分别是目录遍历漏洞和文件上传漏洞。攻击者可以利用目录遍历漏洞突破/vpns/路径的权限控制，结合目录遍历漏洞实现在目标服务器上执行任意命令。

  

 **4.CVE-2019-7642**

D-Link DIR-817LW是一款无线路由器。多款D-Link产品中存在安全漏洞，该漏洞源于mydlink功能的Web界面没有要求进行身份验证。

  

 **5.CVE-2019-0708**

属于远程代码执行漏洞，无需用户交互，成功利用此漏洞的攻击者可以安装应用程序，查看、更改或删除数据或创建具有完全用户权限的新账户。利用此漏洞的任何恶意软件攻击都可能造成类似
2017年WannaCry勒索病毒攻击事件的影响。

