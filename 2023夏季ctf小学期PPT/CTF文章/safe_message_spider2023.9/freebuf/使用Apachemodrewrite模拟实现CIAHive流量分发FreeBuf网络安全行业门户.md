**声明：本文仅限于技术交流，禁止恶意利用，否则后果自负！**

## 一、背景介绍

 **本文的复现场景源于2017年11月维基解密Vault 8文件曝光的CIA网络武器库之CIA
Hive[[1]](https://www.freebuf.com/wp-admin/footnote-1)工具。CIA
Hive工具的主要功能是辅助CIA其他恶意软件隐蔽控制、运行。**

CIA Hive的整体结构可以分为四层，如图 1 所示。

![](https://image.3001.net/images/20190726/1564109323_5d3a6a0b998c6.png!small)

图 1

具体关于CIA Hive各层对应详细解析请参考[[2]](https://www.freebuf.com/wp-admin/footnote-2)，本次复现场景聚焦模拟实现并验证隐藏服务器(Blot)的流量分发功能——Blot
Server根据不同来源把请求分发到事先设定好的不同服务器。即当Blot Server收到访问请求时，Blot
Server会基于对客户端证书验证结果进行流量分发。若SSL验证该访问非法，Blot会将流量分发给cover server，返回一个正常的网页。若Blot
接收到带有有效证书的流量（只有受控主机会发送带有有效证书的流量）则将此流量转发给Honeycomb，从而实现隐蔽通信和控制。

本文主要从技术角度出发，尝试使用Apache的mod_rewrite模块实现其流量分发功能，完成与CIA Hive的Blot Server相同的功能。

## 二、原理概述

### 2.1 Apache的mod_rewrite模块

2.1.1什么是mod_rewrite？

mod_rewrite是apache的一个模块，安装apache环境默认安装此模块，但通常默认不启用，需要手动启用。该模块是基于一定规则实时重写URL请求的引擎。此模块可以操作URL的所有部分，在服务器级(httpd.conf)和目录级(.htaccess)的配置都有效。

2.1.2 mod_rewrite实现流量分发思路

通过手动启用rewrite模块，进入apache配置文件apache2.conf，开启.htaccess的目录级配置，打开AllowOverride，最后在.htaccess文件中配置规则来实现流量分发。具体配置规则及配置技巧可参考<https://httpd.apache.org/docs/current/mod/mod_rewrite.html#rewritecond>和
<https://bluescreenofjeff.com/tags>。

### 2.2 x.509证书链

2.2.1 数字证书

数字证书是一种网络身份证明文件，同时还包含有公钥。证书的真伪需要一个验证方式，而验证方需要认同这种验证方式，以完成证书的颁发过程。一个https的站点需要和一个证书绑定，客户端通过维护一个“根受信任机构列表”完成站点的可信识别过程，而客户端是否信任这个站点的证书取决于客户端程序是否导入了证书颁发者的根证书。目前，X.509证书是一种通用的证书格式，符合ITU-T
X.509国际标准。

2.2.2X.509证书

通用证书格式X.509主要包含三个文件：key，csr，crt。各文件描述如下：

> key文件——服务器上的私钥文件，用于对发送给客户端数据的加密，以及对从客户端接收到数据的解密。
>
> csr文件——证书签名请求文件，用于提交给证书颁发机构（CA）对证书签名。
>
> crt文件——由证书颁发机构（CA）签名后的证书，或者是开发者自签名的证书、包含证书持有人的信息、持有人的公钥、以及签署者的签名等信息。

注：本文以复现实验为主，将采用HTTPS双向认证。其中，双向认证和单向认证原理类似，区别在于除了客户端需要认证服务端以外，增加了服务端对客户端的认证。服务端在验证客户端证书后，根据其验证结果可以提供不同的服务（如：验证合法后才转到特定服务链接）。具体可参考<https://blog.csdn.net/duanbokan/article/details/50847612>

## 三、场景复现步骤

### 3.1 Ubuntu下安装和配置基础环境

最小化环境需求：win7虚拟机 * 1(客户端验证，测试)，ubuntu虚拟机 * 1（模拟Blot Server）

注：为避免报错，建议在root账户下进行实验。

3.1.1 在ubuntu 16.04上安装apache2和openssl

    
    
    apt-getinstallapache2 
    
    apt-getinstallopenssl

3.1.2 启用Apache SSL模块

    
    
    a2enmodssl

3.1.3 启用Apache mod_rewrite模块

    
    
    a2enmodrewrite

3.1.4 自签名证书生成

证书使用openssl生成，具体生成过程请参考伪造HTTPS证书[[3]](https://www.freebuf.com/wp-admin/footnote-3)和合天在线实现-HTTPS证书伪造[[4]](https://www.freebuf.com/wp-admin/footnote-4)。最终本次实验使用https双向认证，即需要生成用于服务端和客户端验证的证书文件和对应的两对公私钥文件。

3.2 Apache下配置https双向认证步骤

3.2.1证书准备(均在ubuntu环境下使用openssl产生)

以下为快速生成步骤及命令，详细讲解请参考[[3]](https://www.freebuf.com/wp-admin/footnote-3),[[4]](https://www.freebuf.com/wp-admin/footnote-4)。

(1) 服务端认证所需证书

生成2048位的RSA密钥 .key 文件

    
    
        openssl genrsa -out ciahive.com.key

生成证书签名请求 .csr 文件

    
    
        openssl req -new -key ciahive.com.key -out ciahive.com.csr

注：需要根据提示依次填入配置信息，Common Name项需要和域名项对应（即ciahive.com）。

生成自签名证书 .crt 文件

    
    
        openssl x509 -req -days 36500 -in ciahive.com.csr -signkey ciahive.com.key -out ciahive.com.crt

(2) 客户端认证所需证书

步骤与（1）中步骤类似，以下为快捷命令：

    
    
      openssl req -new -SHA256 -newkey rsa:2048 -nodes -keyout client.key -out client.csr -subj "/C=CN/ST=Shanghai/L=Shanghai/O=11/OU=22/CN=client"
    
      openssl x509 -req -days 365 -in client.csr -signkey client.key -out client.crt
    
      openssl pkcs12 -export -cacerts -inkey client.key -in client.crt -out client.p12

(3) 最终备用证书列表如图2：

![](https://image.3001.net/images/20190726/1564109369_5d3a6a398a829.png!small)

图 2

3.2.2配置HTTPS双向认证

(1) 确认开启Apache SSL模块。

    
    
         a2enmod ssl

(2) 编辑SSL配置文件

    
    
        vim /etc/apache2/sites-enabled/default-ssl.conf

在打开的文件编辑页面指定(服务器认证)的私钥文件和签名证书的路径。

    
    
    SSLEngine on  
    SSLCertificateFile /XX/XX/XX/ciahive.com.crt  
    SSLcertificateKeyFile   
    /xx/xx/xx/ciahive.com.key

开启客户端认证，并指定用于客户端证书的路径

    
    
     SSLCACertificateFile /xx/xx/xx/client.crt  
      
     SSLVerifyClient require  
     SSLVerifyDepth 10

(3) 启用Apache默认的SSL虚拟主机

    
    
         a2ensite default-ssl

(4) 重启Apache服务

    
    
         service apache2 restart

(5) 客户端配置

1)、修改客户端的Hosts文件

由于实验域名ciahive.com并未实际注册，因此需要通过本地hosts文件(windows系统下的hosts文件路径为：C:\Windows\System32\Drivers\etc\hosts)进行解析。在hosts文件中（修改需要管理员权限）加入Apache服务器的ip及对应的域名ciahive.com。如图3.

![](https://image.3001.net/images/20190726/1564109402_5d3a6a5a83b3a.png!small)

图 3

2)、客户端安装服务器的自签名证书ciahive.com.crt为受信任的根证书颁发机构，安装结果如图4。

![](https://image.3001.net/images/20190726/1564109446_5d3a6a86a036d.png!small)

图 4

3)、向客户端添加特定证书client.p12文件，用于服务器验证客户端。安装结果如图5。

![](https://image.3001.net/images/20190726/1564109480_5d3a6aa88ee1d.png!small)

图 5

3.2.3测试https双向认证配置

通过访问[https://ciahive.com](https://ciahive.com/)来测试https双向认证配置是否成功。以下为简易验证方法。

(1)
通过未配置ciahive.com.crt证书的客户端1访问[https://ciahive.com](https://ciahive.com/)，应该是不安全连接被拦截。如图6。

![](https://image.3001.net/images/20190726/1564109512_5d3a6ac82d869.png!small)

图 6

(2) 若客户端只安装了证书ciahive.com.crt，缺少client.p12证书的客户端访问会直接连接失败，结果如图7。

![](https://image.3001.net/images/20190726/1564109562_5d3a6afaaca61.png!small)

图 7

(3)
使用已完成两个证书安装的客户端2访问[https://ciahive.com](https://ciahive.com/)，会首先提示进行客户端证书选择，如图
8。

![](https://image.3001.net/images/20190726/1564109601_5d3a6b2113af5.png!small)

图 8

(4)
确认使用client.p12作为客户端证书后，与[https://ciahive.com](https://ciahive.com/)建立安全链接。成功页面如图
9。

![](https://image.3001.net/images/20190726/1564109629_5d3a6b3da65e8.png!small)

图 9

(5) 访问[https://ciahive.com](https://ciahive.com/)出现如图
9的安全连接页面后，表示https双向认证配置成功。

### 3.3 配置apache mod_rewrite规则实现流量分发功能

3.3.1配置Apache启用mod_rewrite

(1) 开启Apache mod_rewrite模块

    
    
        a2enmod rewrite

(2) 编辑/etc/apache2/apache2.conf文件，开启支持 .htaccess文件——用于编辑转发规则。定位到如下位置：

    
    
        <Directory /var/www/>  
            Options Indexes FollowSymLinks  
            AllowOverride None  
            Require all granted  
        </Directory>

将AllowOverride None更改为AllowOverride All。

(3) 创建并编辑 .htaccess文件，文件保存路径为：/var/www/html/。编写测试规则。

1)、测试规则示例——将1.html重定向到2.html

    
    
        <IfModule mod_rewrite.c>  
            RewriteEngine on  
            RewriteRule 1.html 2.html  
        </IfModule>

2)、建立1.html空文件，在2.html里写入内容：

    
    
        <html>  
            <body>  
                Test is successful!  
            </body>  
        </html>

(4) 重启apache服务，测试网页<https://ciahive.com/1.html>，若返回页面为“Test is
successful!”则测试通过。

3.3.2编辑规则，实现流量分发功能

具体的配置规则可以按需编辑，关于 .htaccess 编写相关详细技巧请参考[[5]](https://www.freebuf.com/wp-admin/footnote-5)和[[6]](https://www.freebuf.com/wp-admin/footnote-6)。

注：本次实验环境受限，仅仅使用两台虚拟主机进行实验，特编写以下规则对CIA Hive的转发思想进行最简单的模拟。

具体的.htaccess模拟转发规则如下：

    
    
        <IfModule mod_rewrite.c>  
            RewriteEngine on    
            RewriteCond %{SERVER_PORT} !^443$  
            RewriteCond %{REQUEST_URI} ^/0.html  
            #访问0.html转换为强制https访问，且需要对客户端进行认证。  
            RewriteRule (.*) https://%{SERVER_NAME}/$1 [R]  
            #由于以配置https双认证，则只有被感染主机才拥有合法证书。  
            #认证通过后进行重定向到payload地址（可以本地或其他远程主机），即类比CIA Hive中的Honey Server  
            RewriteRule 0.html https://ciahive.com/.payload/remotepayload/payload1.html [L]  
        </IfModule>

3.3.3实际测试

(1) 模拟的正常主机(无证书)

1)、访问其他页面（除ciahive.com/0.html外所有ciahive.com及各目录文件）均正常。参照图10。

![](https://image.3001.net/images/20190726/1564109713_5d3a6b9114d1d.png!small)

图 10

2)、访问ciahive.com/0.html时被强制使用https访问，由于未获得合法证书将提示连接失败。参照图11。

![](https://image.3001.net/images/20190726/1564109744_5d3a6bb070d43.png!small)

图 11

(2)、被感染主机（已被安装ciahive.com.crt和client.p12两个证书）

1)、访问其他页面同正常主机。

2)、访问ciahive.com/0.html时被强制使用https访问。将提示选择客户端证书确认(实际攻击场景可以设计为默认，即不弹窗提示)后连接被重定向到<https://ciahive.com/.payload/remotepayload/payload1.html>页面(模拟Honey
Server)。参照图12 。

![](https://image.3001.net/images/20190726/1564109786_5d3a6bdaf3222.png!small)

图 12

## 四、实验总结

### 4.1本文复现关键：

(1) 深入理解X.509证书链和HTTPS双向认证原理。

(2) Apache及re_write模块参数正确配置。

(3) 理解CIA Hive流量转发过程，尤其是隐蔽服务器的功能。

(4) .htaccess中转发规则的实现。

### 4.2总结：

(1) 本次复现实验对于理解CIA
Hive框架有很大帮助时，同时在Apache+openssl环境搭建及其过程中遇到的各种问题，当问题逐一被解决就形成了对整个流程的清晰认识。

(2) 需要特别注意
X.509证书链及其基本原理。同时实验中采用的HTTPS的双向认证在公共站点基本不会开启，因此攻击者如果采用此类少数人关注的技术点实现攻击目的是很难被发现的。

(3) 本次复现只在基础学习理解上进行了最简单的功能实现，在.htaccess文件的转发规则的设计和整各实验设计上都还有很大的提升空间。

## 五、参考

> [[1]](https://www.freebuf.com/wp-admin/footnote-1):[维基解密公布的Vault
> 8文档](https://wikileaks.org/vault8/)
>
> [[2]](https://www.freebuf.com/wp-admin/footnote-2):[CIA
> Hive源码获取及框架解析](https://www.4hou.com/reverse/8500.html)
>
> [[3]](https://www.freebuf.com/wp-> admin/footnote-3):[伪造HTTPS证书](http://www.arkteam.net/?p=3071)
>
> [[4]](https://www.freebuf.com/wp-admin/footnote-4):[HTTPS证书伪造-> 合天在线实验](http://www.hetianlab.com/expc.do?ec=ECIDee9320adea6e062017120110232100001)
>
> [[5]](https://www.freebuf.com/wp-> admin/footnote-5):[Apache之Rewrite和RewriteRule规则梳理总结](https://www.cnblogs.com/kevingrace/p/9565123.html)
>
> [[6]](https://www.freebuf.com/wp-> admin/footnote-6):[使用mod_rewrite配置规则的心得](https://bluescreenofjeff.com/tags#mod_rewrite)

感谢：本文以实验为主，作为复现详细笔记，感谢众多大神（3gstudent、arkteam等）博客文章为我解惑，且本文也是在众多博客文章基础上实验形成的！

 ***本文作者：mumufeng06，转载请注明来自FreeBuf.COM**

