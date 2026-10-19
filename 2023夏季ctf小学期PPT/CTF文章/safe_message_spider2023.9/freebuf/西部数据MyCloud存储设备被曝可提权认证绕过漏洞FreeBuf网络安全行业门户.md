**![西部数据My
Cloud存储设备被曝可提权认证绕过漏洞](https://image.3001.net/images/20180925/1537850738_5ba9bd72ea9d3.png!small)****近期，网络设备漏洞研究团队exploitee.rs公布，西部数据
My Cloud 网络存储设备存在一个认证绕过漏洞（
CVE-2018-17153），未授权的远程或本地网络攻击者可以利用该漏洞，无需密码就能提权成为admin管理员身份，获取对 My
Cloud设备的完全控制权。 **

## 漏洞介绍

该漏洞能可使得未授权用户能创建与其IP地址相关联的管理员会话，然后进一步利用，可以实现管理员特权命令执行，获取对My Cloud
存储设备的控制。该漏洞是研究者通过逆向CGI二进制文件时发现的。

当My Cloud设备管理员授权认证登录后，会产生一个与其IP地址关联的相应的服务端（ server-side）会话，然后该会话会在HTTP请求中以发送username=admin的cookie形式去调用验证性CGI模块，接着，被调用的验证性CGI模块需要对当前与用户IP关联的会话有效性进行检查校验。

未授权的攻击者可以创建一个不需验证的有效会话，被调用的network_mgr.cgi CGI模块中包含了一个名为 cgi_get_ipv6
的命令，当CGI模块被调用时，其参数标志为1时，该命令会启动一个与用户IP绑定关联的管理员会话。通常来说，一些后续命令的调用执行需要管理员权限，但如果攻击者把cookie中的username设置为admin，也就是username=admin之后，则该会话就相当于管理员权限，间接绕过了验证授权限制。

## 存在漏洞的My Cloud版本

exploitee研究人员分析，该漏洞目前可以成功在固件版本为2.30.172，型号为WDBCTL0020HWT的 My Cloud
存储设备上复现，主要影响固件版本为2.30.xxx的设备，由于 My Cloud
的多个系列设备开发代码都大同小异，因此，其它型号的设备也非常可能存在该漏洞。可能存在漏洞的型号和对应固件版本设备为：

> My Cloud FW 2.30.196
>
> My Cloud Mirror Gen2 FW 2.30.196
>
> My Cloud EX2 Ultra FW 2.30.196
>
> My Cloud EX2100 FW 2.30.196
>
> My Cloud EX4100 FW 2.30.196
>
> My Cloud DL2100 FW 2.30.196
>
> My Cloud DL4100 FW 2.30.196
>
> My Cloud PR2100 FW 2.30.196
>
> My Cloud PR4100 FW 2.30.196

## 漏洞利用POC

首先，攻击者需要在POST请求中把自己的IP地址和会话关联；

之后，设置username=admin和cmd=cgi_get_ipv6&flag=1：

    
    
    POST /cgi-bin/network_mgr.cgi HTTP/1.1
    
    Host: wdmycloud.local
    
    Content-Type: application/x-www-form-urlencoded
    
    Cookie: username=admin
    
    Content-Length: 23
    
    cmd=cgi_get_ipv6&flag=1

接下来，请求需要管理员权限的My
Cloud服务端，如cgi_get_ssh_pw_status；把以上cookie信息设置在浏览器中，执行服务端请求之后，可以发现已经具备管理员权限。如下图所示：

最新的Metasploit漏洞利用模块 -[
https://pastecry.pt/dUHB3e#PewMuk%3AUt2Ek3Bee4Rej2Syz5Mek](https://pastecry.pt/dUHB3e#PewMuk%3AUt2Ek3Bee4Rej2Syz5Mek)  

有安全研究者向记者透露，还可以通过恶意广告形式（malvertising campaigns），用跨站漏洞技巧去入侵My Cloud
的NAS网络存储设备，这种方式还能入侵那些不联网的My Cloud设备。

## 该漏洞被发现的前后

据悉，该漏洞问题其实早在2017年4月9日就被安全团队exploitee.rs在去年Def Con上的设备漏洞集锦《[All Your Things Are
Belong To Us!](https://download.exploitee.rs/file/generic/Exploiteers-DEFCON25.pdf)》中披露过，但当exploitee向西部数据反馈后，西部数据却拒绝承认和修复该漏洞，因此，毫无办法的exploitee团队只好在今年8月编写出了漏洞利用的Metasploit模块，并以对外公布了该漏洞。

> 2017.4.9 exploitee团队发现漏洞
>
> 2017.4.10 exploitee团队向西部数据上报该漏洞
>
> ......没有下文....
>
> 2018.9.17 exploitee团队向CVE请求公布漏洞
>
> 2018.9.18 CVE官方给定漏洞编号CVE-2018-17153
>
> 2018.9.18 exploitee团队公布漏洞细节

而据了解，该漏洞在去年也被Securify公司研究员Remco Vermeulen上报过，但西部数据最终也并未成功修复。

## 后续

截至发稿前，记者发现，目前有1,870个曝露互联网的西部数据My Cloud设备，其中大多数处于欧洲，而且这个数据还在不断增加。

> 2018.9.18 16:31 西部数据在Twitter声称已经在着手制作针对CVE-2018-17153的固件更新
>
> 2018.9.18
> 西部数据针对CVE-2018-17153释出了[补丁更新](https://support.wdc.com/knowledgebase/answer.aspx?ID=25952&s)

***参考来源：[securify](https://www.securify.nl/advisory/SFY20180102/authentication-bypass-vulnerability-in-western-digital-my-cloud-allows-escalation-to-admin-privileges.html) /
[bleepingcomputer](https://www.bleepingcomputer.com/news/security/my-cloud-nas-devices-vulnerable-to-auth-bypass-for-over-a-year/)，clouds编译，转载请注明来自FreeBuf.COM**

