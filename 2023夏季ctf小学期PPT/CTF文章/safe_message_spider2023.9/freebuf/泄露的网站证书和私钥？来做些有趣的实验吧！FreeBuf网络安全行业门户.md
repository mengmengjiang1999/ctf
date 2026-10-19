**网站配套有APP，因为做了`SSLPinning`，因此用`Burpsuite`代理抓包会报错：**

`The client failed to negotiate a TLS connection to xxx.com:443 : Remote host
closed connection during handshake`

既然这样，利用泄露的证书和私钥来一个“完美”中间人不就行了！

## 基本概念

在正式实战之前，先介绍一下接下来用到的技术中的一些基本概念：正向代理、反向代理、DNS解析和HTTPS证书。

### 正向代理和反向代理

代理分为正向和反向两种。

 **正向代理**
，也被称之为转发代理，是一种比较常见的代理方式。一般情况下，正向代理（转发代理）用于某个区域的网络（如公司内网）无法直接访问互联网环境，或者被墙等原因，需要借助正向代理服务器来间接的访问。需要使用正向代理的主机需要配置代理服务器的IP。

![image.png](https://image.3001.net/images/20200326/1585227678_5e7ca79ee60fe.png!small)

比如常用的`Burpsuite`，就可以看做正向代理服务器，在使用的时候需要把浏览器的代理地址配置到`Burpsuite`指定的IP和端口上，如默认配置的`127.0.0.1:8080`。

 **反向代理**
是一种客户端无感知的代理方式，一般用在负载均衡或业务转发的场景中。比如某网站有两台服务器，`服务器A`为Web服务器，`服务器B`为邮件服务器。因此在总的出口上配置反向代理，对于`<http://example.com/web>`的请求就转发到`服务器A`，而`<http://example.com/mail>`的请求就转发到`服务器B`。

![2020-03-17_192900.png](https://image.3001.net/images/20200326/1585226353_5e7ca2711150d.png!small)

总的来说， **正向代理** 是隐藏客户端，对于服务器来说发起访问的是代理服务器；而 **反向代理**
是隐藏了服务端，比如上面的例子中，用户只对`<http://example.com>`有感，而对背后的两台实际处理业务的服务器无感。

反向代理的实现有很多，常见的是`Apache`或`Nginx`。

详细的解释可参见：[代理与反向代理，以及其应用场景](https://blog.csdn.net/hungry0_0/article/details/78928082)和[Nginx正向代理与反向代理](https://www.jianshu.com/p/ae76c223c6ef)。

### HTTPS证书

HTTPS证书如果展开细说，内容实在有点多，涉及到对称加密、非对称加密、公钥基础设施（PKI）等等概念。此处默认大家已经了解这些概念，不再过多叙述，感兴趣的可参考[HTTPS系列干货（一）：HTTPS
原理详解](https://zhuanlan.zhihu.com/p/27395037)。

此处需提及的是，在申请HTTPS证书后，一般会得到两个文件：`.crt`的证书文件，和`.key`的私钥文件。证书文件是会在请求的时候发到客户端的，私钥文件是用来解密客户端协商密钥的加密数据的。

### DNS投毒

上文中提到过，投毒方式有很多种，当然也各有优劣。

  *  **DNS劫持** ：在实际攻击中可以使用`bettercap`进行DNS投毒的操作。这种方法对受害者无感，且无需接触受害者设备。

  *  **修改DNS服务器** ：在有接触路由器或受害者设备的情况下可用此种方式。如果路由器自动分配DNS，则可以直接修改规则将分配的首选DNS设置到攻击者布置的DNS服务器的IP上。

DNS服务器搭建，有条件可以选用`Windows Server`进行（原生自带），或者使用软件`ISC BIND
9`来进行，这类教程网上很多，在此不在赘述。

  *  **修改Hosts文件** ：一般在本地测试或者验证的时候用这种方式，操作简单，影响面小（仅有本机会被影响）。

本次实验即选用修改Hosts文件的方式，简单快捷。

关于修改Hosts，在`Windows`和`Linux`平台不过多介绍，因为测试了`Android
APP`，因此踩了个小坑：文件位于`/etc/hosts`（或`/system/etc/hosts`，两个路径实际相同），因为回车符`\n`的问题，编辑的时候可能会导致系统无法识别而解析失败。两种方法解决：

  1. 通过`adb pull /etc/hosts`命令将文件下载到PC、删除安卓系统中的hosts文件，用`Emeditor`之类的软件修改后再用`adb push hosts /etc/hosts`上传回去就好

  2. 用`adb shell`连接进入命令行后通过输入命令：
    
        echo -e \\n >> hosts  
    echo 192.168.1.x www.example.com >> hosts

来写入hosts文件。多个域名时就重复上面的命令多次即可。

## 攻击准备

首先，需要事先进行一些准备工作。

攻击的前提，需要获取到目标站点的私钥文件，即上节中提到的`.key`文件。实际的测试过程中，很幸运的在某个配置备份文件中发现了，且有效期还有一年多，足以做很多奇奇怪怪的事了~

其次，构想一下整个攻击的网络模型。由于是一个中间人攻击，因此主要有三方：受害者（`victim`，简称V），中间人（`Man-in-the-Middle`，简称M）和服务器（`Server`，简称S）。主要的思路是，要引导 `V` 的流量经过 `M` 转发到 `S`。其中 `M`
需要有解开HTTPS密文的能力。

![image-20200326190216345](https://image.3001.net/images/20200326/1585226431_5e7ca2bf60d70.png!small)

是不是乍一看觉得，这不是`Burpsuite`或者`SSLStrip`干的事吗！

但是！这些工具都有一个致命缺陷：会有“站点不安全”的警告！

![image-20200324212039174](https://image.3001.net/images/20200326/1585226440_5e7ca2c8d73cc.png!small)

如果是日常测试，或者安全研究可以通过 **安装证书解决** ，但是其他场景下无法安装证书，或者软件做了 **HTTPS证书绑定** ，这种方式就失效了。

虽然说证书绑定可以通过各种方法绕过，比如Android App可以用`Xposed`框架的`Just Trust Me`、`SSL
Unpinning`之类的插件，但是有些情况下这些通用插件不起作用，又懒得hook（比如我）而“恰巧”获取到了网站证书……

攻击的拓扑图大致如下：

![image-20200326191141220](https://image.3001.net/images/20200326/1585226451_5e7ca2d393b36.png!small)

在 `M` 上搭建反向代理，并投毒DNS，让 `V` 访问服务器 `example.com` 的时候将IP地址解析成 `M` 的地址。这样流量到达 `M`
的时候通过反向代理。

由于反向代理上配置了证书，因此在流量到达时会尝试进行密钥协商，并处理加密流量。此时，反向代理出口的流量即为明文状态，攻击者即可对此部分流量进行拦截、修改和查看等，再转发到真实服务器上。

## 实战

### DNS投毒

上文中提到过，投毒方式有很多种，当然也各有优劣。

 **DNS劫持** ：在实际攻击中可以使用`bettercap`进行DNS投毒的操作。这种方法对受害者无感，且无需接触受害者设备。

 **修改DNS服务器**
：在有接触路由器或受害者设备的情况下可用此种方式。如果路由器自动分配DNS，则可以直接修改规则将分配的首选DNS设置到攻击者布置的DNS服务器的IP上。

DNS服务器搭建，有条件可以选用`Windows Server`进行（原生自带），或者使用软件`ISC BIND
9`来进行，这类教程网上很多，在此不在赘述。

 **修改Hosts文件** ：一般在本地测试或者验证的时候用这种方式，操作简单，影响面小（仅有本机会被影响）。

本次实验即选用修改Hosts文件的方式，简单快捷。

### 反向代理

反向代理的架设方法很多，比如利用`Nginx`或者`Apache`。由于电脑上装了`xampp`，本次使用`Apache`作为反向代理服务器。下面的配置基于`xampp
v3.2.4`的默认配置。

  1. 将证书（后缀`.crt`）和私钥（后缀`.key`）文件复制到xampp路径下。记住这两个文件的路径。比如：
    
        F:\xampp\apache\conf\ssl.crt\test.crt  
    F:\xampp\apache\conf\ssl.key\test.key

这个是按照`Apache`默认存放证书的位置放进去的。当然放在哪不重要，因为这两个文件的位置是要在配置中指定的。

  2. 进入`xampp`安装目录，编辑\apache\conf\httpd.conf`文件，添加配置：
    
        <VirtualHost *:443>  
        ServerName  example.com  
        ServerAlias example.com  
        SSLEngine on  
        SSLProxyEngine On  
        SSLProxyVerify none  
        SSLProxyCheckPeerCN off  
        SSLProxyCheckPeerName off  
        SSLProxyCheckPeerExpire off  
        SSLCertificateFile "F:\xampp\apache\conf\ssl.crt\test.crt"  
        SSLCertificateKeyFile "F:\xampp\apache\conf\ssl.key\test.key"  
        <Proxy *>  
           Order deny,allow  
           Allow from all  
        </Proxy>  
        ProxyPreserveHost On  
        ProxyRequests Off  
        ProxyPass /  https://example.com/  
        ProxyPassReverse / https://example.com/  
    </VirtualHost>

其中`example.com`是目标服务器的域名，两个文件路径就是第一步拷贝进来的证书和私钥的地址。

  3. 启动`Apache`，此时访问`<https://127.0.0.1>`，会显示“此站点不安全”的警告，点忽略后会显示`example.com`(第二步中配置的域名)的内容。

这样就算反向代理配置成功。

### 控制流量

反向代理出口流量就是明文的了，如果不去管它，会自动被代理转发到服务端。因此这里需要一个机制去拦截、查看和修改流量，达到操纵流量的目的。

本实验在`Windows`平台下进行，因此使用的是Win平台的软件，Linux平台可找同类软件替换，毕竟真理是不会变的嘛。

[
**Proxifier**](https://baike.baidu.com/item/proxifier/10859305?fr=aladdin)是一款功能非常强大的socks5客户端，可以让不支持通过代理服务器工作的网络程序能通过HTTPS或SOCKS代理或代理链。通过这个软件，可以将`Apache`中的流量转发出来。

关于这个软件的安装使用不过多做介绍，只说一下 **代理规则**
的配置。这里对`Apache`的全部流量进行拦截，因此在“应用程序”栏中填写`httpd.exe`（这个是`Apache`处理请求的进程），如下：

![image-20200326200451393](https://image.3001.net/images/20200326/1585226467_5e7ca2e3abc21.png!small)

流量最终是被代理到`Burpsuite`上，因为这款软件对数据包修改比较友好，比如`Repeater`、`Intruder`等模块都可以方便的对请求进行重放、暴破等。

### 流量操纵

这部分其实不用过多介绍，运行起来之后只需要在`Burpsuite`中查看获取的流量并进行操作即可。

至此，整个中间人过程完毕，虽然有点繁琐（反代接`Proxifier`再接`Burp`），应该可以再优化，但奈何本人才疏学浅，只能想到这种方式来利用，希望有大神可以指点。

在中间人端（`M`端）流量的关系如下：

![image-20200326202158832](https://image.3001.net/images/20200326/1585226479_5e7ca2efcbd9d.png!small)

## 结语

这种中间人攻击的方式利用难度很大，但是可以完美的对抗证书认证类的校验，比如APP校验服务端证书。可以利用的场景也比较有限（临近网络）。

写此文的目的有两个，一是分享一下整个攻击的过程，毕竟这种类型的攻击并没有太多提及；二是提醒一下泄露了网站证书的管理员，不要以为仅仅删除了泄露出去的备份文件就安全了，证书泄露的后果还是很严重的。

