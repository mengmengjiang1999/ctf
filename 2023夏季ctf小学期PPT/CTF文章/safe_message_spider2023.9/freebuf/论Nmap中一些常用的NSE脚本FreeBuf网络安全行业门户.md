![1_jTRGkDhYnDXgvFz9I1uELA.png](https://image.3001.net/images/20190807/1565190115_5d4ae7e35549e.png!small)

**在这篇文章中，我们将研究最著名的渗透工具之一 Nmap 一款标志性的跨平台扫描器。它的原意为Network
Mapper（网络映射器），具有相当强大的扫描功能，几乎适用于任何渗透场景。不少人甚至认为它就是全球最好的扫描软件。除了常规的网络扫描，Nmap还可根据NSE
(Nmap scripting
Engine)的脚本进行大量渗透工作，这种脚本是基于Lua编程语言，有点像javascript。正是NSE，使得Nmap不再普通。**

首先，我们扫描目标主机，检测开放的端口：

    
    
    root@kali:~# nmap site.test.lan
    Starting Nmap 7.70 ( https://nmap.org ) at 2019–05–31 11:58 MSK
    Nmap scan report for site.test.lan (192.168.60.50)
    Host is up (0.000030s latency).
    Not shown: 995 closed ports
    PORT STATE SERVICE
    21/tcp open ftp
    22/tcp open ssh
    80/tcp open http
    90/tcp open dnsix
    3306/tcp open mysql
    MAC Address: 6E:93:12:AA:1F:6D (Unknown)
    

接着，让我们瞄准80端口，通常web服务就在这里。一旦启用Nmap中的http-enum脚本，它将收集web服务的所有有用的信息，就如漏洞扫描器Nikto一般:

`nmap site.test.lan --script http-enum`

## 信息收集

![1.png](https://image.3001.net/images/20190807/1565190290_5d4ae892ea10a.png!small)

从上图中，我们可以了解到该站点使用了WordPress。于是，我们可以使用针对WordPress的脚本http-wordpress-enum进行深度扫描。这个脚本还会确定网站使用了多少和WordPress相关的插件。

`nmap -p80 --sc ript http-wordpress-enum --script-args http-wordpress-enum.search-limit=all site.test.lan`

![2.png](https://image.3001.net/images/20190807/1565190355_5d4ae8d3d69d1.png!small)

一般来说，标准的Nmap中集成了近600个脚本，如果没有你需要的，也可以自己编写脚本。

## 权限

假如我们想在站点上寻找登录授权页面，还可使用如下脚本http-auth-finder。

![3.png](https://image.3001.net/images/20190807/1565190443_5d4ae92b32e07.png!small)

你也可以使用命令参数--script=auth，所有和授权有关的脚本都将被启用，对目标主机进行探测。而一旦找到和登录授权有关的页面，我们就可以尝试使用类似于http-form-brute的脚本爆破出一些账户密码：

`nmap -p-80 --script=http-form-brute --script-args=http-form-brute.path=/wp-login.php site.test.lan`

![4.png](https://image.3001.net/images/20190807/1565190488_5d4ae9580a66d.png!small)

从上图可以看到，网站site.test.lan的管理员密码为12345。

对于WordPress来说，Nmap已做的足够出色，它获取了大量和渗透有关的信息，而如果想对WordPress进行更深一步的漏洞探测，你也可以使用已集成在kali
linux中的WPScan，这款软件有大量专门针对WordPress的PoC。

## SSH

此外，我们也可以对22端口（SSH服务）进行密码爆破，涉及脚本为ssh-brute  

`nmap -p22 --script ssh-brute site.test.lan`

![5.png](https://image.3001.net/images/20190807/1565190549_5d4ae995a7b23.png!small)

## FTP

而通常开放在21端口的FTP服务也往往是爆破对象，我们可以先使用脚本ftp-syst获取一些服务信息:  

`nmap -p21 --script ftp-syst site.test.lan`

![6.png](https://image.3001.net/images/20190807/1565190610_5d4ae9d29e341.png!small)

之后使暴力破解脚本得到FTP服务的用户密码:  

`nmap -p21 192.168.60.50 --script ftp-brute --script-args
userdb=/root/user.txt,passdb=/root/pass.txt`

![7.png](https://image.3001.net/images/20190807/1565190659_5d4aea03bea83.png!small)

## MySQL

Nmap也可对MySQL服务（通常开放在端口3306上）进行扫描爆破，脚本mysql-info将探测出一些MySQ服务的详细信息(需要带上命令参数-sV
-sC)：  

`nmap -p3306 -sV -sC site.test.lan`

  
![8.png](https://image.3001.net/images/20190807/1565190706_5d4aea32d0866.png!small)

你可以看到MySQL服务的协议版本号、流标识符、状态和密码salt等信息。更重要的是，你还可以列出有效的MySQL用户：  

`nmap -p3306 --script mysql-enum site.test.lan`

![9.png](https://image.3001.net/images/20190807/1565190746_5d4aea5aadccf.png!small)

在得到有效用户名后，你就可以配合密码字典进行密码暴力破解。

希望这篇文章能对你有所帮助，感谢阅读。

 ***参考来源：[Medium](https://medium.com/@Pentestit_ru/nse-or-backside-of-nmap-bf6789009120)，线性代数lzh编译整理，转载请注明来自 FreeBuf.COM**

