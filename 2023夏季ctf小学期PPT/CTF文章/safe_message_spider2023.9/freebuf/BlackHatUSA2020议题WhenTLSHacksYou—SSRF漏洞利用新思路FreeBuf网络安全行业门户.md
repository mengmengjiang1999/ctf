本文作者：中兴沉烽实验室_jqz

## 0x00 背景介绍

2020年BlackHat大会上，Joshua Maddux介绍了一种针对SSRF的新颖利用思路，得到了广泛的关注。此类攻击是通过构造一个HTTPS
Server，使TLS
session中携带攻击载荷，攻击行为触发主要通过一个受限的SSRF漏洞（甚至一个钓鱼网页），结合TLS协议和DNS协议的特性，把攻击报文发到受害者内网的TCP服务中，达到SSRF漏洞攻击面扩大的效果。本文将针对此攻击进行较深入介绍和演示，供大家学习参考。

在演示该攻击方式之前，我们首先介绍以下关键知识：

> SSRF
>
> SSDNS Rebind
>
> TLS session resumption

## 0x01 SSRF

SSRF漏洞是一个常见的web安全漏洞，通过提交一段精心构造的请求信息，发送给服务器，欺骗服务器读取本地文件、探测内网信息、攻击内网其他服务器等。

攻击行为可以通过多种信息实现，取决于服务对协议的支持情况：

> file://
>
> dict://
>
> TFTP://
>
> http://
>
> https://
>
> Gopher://  
> 其中通过Gopher协议，我们可以构造的TCP上层报文，和大部分的TCP
> 服务器通信，比如MySQL、PostgreSQL、Redis、Memcached、SMTP，大大拓展了SSRF漏洞的攻击面。

## 0x02 DNS Rebinding

### 0x021 DNS TTL

DNS TTL 用来定义DNS解析数据在缓存中存放的时间，生存时间一到期，名称服务器就丢弃原有的缓存数据，并从权威名称服务器获取新的数据。假如一个域名的
TTL 为10s，当我们在这10s内，对该域名进行多次 DNS 请求，DNS 服务器，只会收到一次请求，其他的都是缓存。

详细的TTL设置参考RFC2181对DNS TTL的描述：

> It ishereby specified that a TTL value is an unsigned number, with a minimum
> value of 0, and a maximum value of 2147483647. That is, a maximum of 2^31 -> 1. When transmitted, this value shall be encoded in the less significant 31
> bits of the 32 bit TTL field, with the most significant, or sign, bit set to
> zero.

在DNS应答报文中，TTL字段一共4个字节，其中低31位是有效位，数值范围为0到2^31 -1，这里以百度域名解析应答为例，DNS应答报文设置了TTL值为249s（000000f9）：

![image-20210410110649940.png](https://image.3001.net/images/20210421/1618994610_607fe5b2b7178dcac69ae.png!small)

### 0x022 DNS Rebinding

通常的SSRF防御措施是通过以下防御机制实现的：

![81138e5f4403b0c5b7b1dc96bcd650ff.png](https://image.3001.net/images/20210421/1618994697_607fe609d7d146d0f6aad.png!small)

这种SSRF防御思路上，通常会对目标url进行解析，“获取IP地址”然后进行ip判断，如果ip地址在正常范围内，则进入下一个逻辑，“服务端请求URL”。

因此，DNS
Rebindind的攻击思路，是申请一个域名，构造一个DNS服务器，将域名解析到该DNS服务器，同时设置DNS服务器的应答包围TTL为0，在“获取ip地址”的逻辑中响应正常的ip地址，绕过了检测，与此同时由于TTL为0，因此在“服务端请求URL”步骤中，需要重新进行DNS解析，此时DNS服务器应答的ip地址为希望攻击的ip。

实验步骤如下：

设置域名解析的服务器为自定义的DNS服务器  
![image-20210409160200259.png](https://image.3001.net/images/20210421/1618994711_607fe617a9d772f1f1158.png!small)

启动自定义的DNS服务器

![image-20210412103906596.png](https://image.3001.net/images/20210421/1618994724_607fe6240ee58c1749dde.png!small)

![image-20210412103838731.png](https://image.3001.net/images/20210421/1618994733_607fe62dbe7f44db0f502.png!small)

浏览器访问域名  
在本地127.0.0.1地址启动http server

![image-20210412104819282.png](https://image.3001.net/images/20210421/1618994743_607fe63792a072ab45b1a.png!small)

![image-20210412104858444.png](https://image.3001.net/images/20210421/1618994753_607fe641ab29815c5a876.png!small)

访问目标域名，结果响应结果为本地http服务

![image-20210409160012125.png](https://image.3001.net/images/20210421/1618994788_607fe6641f60b1fb93ef0.png!small)

抓包观察DNS响应结果  
在DNS服务器的打印结果中，也可以看到，第一次解析结果为真实ip，后续的解析结果为127.0.0.1

![image-20210412101552195.png](https://image.3001.net/images/20210421/1618994797_607fe66ddc6501d9b1d46.png!small)

抓包观察响应结果，第一次DNS应答为正常的ip，TTL设置为0

![image-20210412105438502.png](https://image.3001.net/images/20210421/1618994828_607fe68c6f2f45d7c0def.png!small)

后续的响应结果为127.0.0.1

![image-20210412105537284.png](https://image.3001.net/images/20210421/1618994841_607fe69967ebeb97a762f.png!small)

### 0x023 结果分析

通过浏览器实验是符合预期的，但是该攻击还存在一些局限性：

1.在真实的应用环境中，java默认的TTL值为10s，这个配置会导致DNS Rebinding攻击失败，可以通过修改配置来完成实验。

    
    
    java.security.Security.setProperty("networkaddress.cache.negative.ttl" , "0");
    

也可以设置https server来耗尽TTL的时间。  
2\. Linux环境中，默认不进行dns缓存，windows中会进行dns缓存。  
3\. PHP环境中默认TTL为0

## 0x03 TLS session resumption

### 0x031 TLS 握手

TLS握手包括以下过程：

![unnamed.jpg](https://image.3001.net/images/20210421/1618994858_607fe6aa3972bc1570ddd.jpg!small)

步骤如下：

> 1.Client 发送 ClientHello；Server 回复 Server Hello
>
> 2.Client 回复最终确定的 Key，Finished；Server 回复 Finished
>
> 3.握手完毕，Client 发送加密后的 HTTP 请求；Server 回复加密后的 HTTP 响应

在此过程中需要消耗两个RTT（Round-Trip Time），抓包分析：

![image-20210412113636583.png](https://image.3001.net/images/20210421/1618994877_607fe6bdc5a6a3bbdc566.png!small)

第一个RTT中，客户端发送了Client Hello，服务器响应了Server Hello，同时发送了自己的证书和公钥。

第二个RTT中，客户端计算出了加密key，并使用服务器公钥加密了key，发送给服务器，服务器使用私钥解密数据获取了key，握手完成。

### 0x032 session resumption

session resumption是指将第一次通过握手协商出来的key保存起来，在后续的请求中直接使用，这样可以节省传送的开销。如下图所示：

![image-20210412141255228.png](https://image.3001.net/images/20210421/1618994890_607fe6ca4c1e32507abb0.png!small)

可以看到使用session resumption后，节省了一次RTT。

实现session resumption有两种主要方案：

 **session id**

session id用于复用连接信息来减少TLS握手的次数，其机制是在Server Hello时返回session
id，客户端在下次建立连接时发送的Client Hello包里可以包含此session_id来恢复之前的会话。

参考rfc5246

> The ClientHello message includes a variable-length session identifier. If
> not empty, the value identifies a session between the same client and server
> whose security parameters the client wishes to reuse. The session identifier
> MAY be from an earlier connection,this connection, or from another currently
> active connection. The second option is useful if the client only wishes to
> update the random structures and derived values of a connection, and the
> third option makes it possible to establish several independent secure
> connections without repeating the full handshake protocol. These independent
> connections may occur sequentially or simultaneously; a SessionID becomes
> valid when the handshake negotiating it completes with the exchange of
> Finished messages and persists until it is removed due to aging or because a
> fatal error was encountered on a connection associated with the session. The
> actual contents of the SessionID are defined by the server.
>
> opaque SessionID<0..32>;

服务端存储session id并存储与之对应的状态，如加密套件，master key等信息。如果服务端拿客户端传过来的session
id能拿到对应的信息，就表示此session id有效，并尝试恢复会话。

 **session ticket**

session ticket用来减少客户端和服务端协商密钥等信息的交互次数(由原来的两次交互减少为一次交互)，ClientHello会发送空的session
ticket插件来表示支持session ticket。服务端如果希望使用此机制，会在ServerHello中返回空的session
ticket扩展，接着在协商完成之后在Change Cipher Spec包之前发送New Session Ticket包。

ClientHello的存储ticket，服务端尝试从中解析出对应主密钥，如果此ticket验证通过，则服务端就重用session状态。

## 0x04 攻击思路

结合以上知识，在遇到一个非通用的SSRF漏洞时，我们可以尝试使用以下思路，将非通用的SSRF漏洞变成通用SSRF漏洞：

![image-20210412150504630.png](https://image.3001.net/images/20210421/1618994912_607fe6e0b18889b84a429.png!small)

> 1.准备DNS Rebinding，部署DNS server，使第一次解析的dns地址为ip A，后续解析的地址为希望攻击的地址ip B；
>
> 2.部署https server，在client端与server端进行握手时，设置server hello中的session
> id字段为攻击payload；
>
> 3.https server响应重定向状态码，触发第二次域名解析，此时该域名解析为ip B；
>
> 4.触发client的TLS session resumption；
>
> 5.client向ip B发送client Hello报文，由于触发session resumption，会向ip
> B发送带有payload的session id；
>
> 6.ip B收到攻击报文，攻击完成。

 **说明**

1、在步骤4中，触发session resumption，client会进行相关的检查，以curl源码为例：

可以看到只检查了域名、端口、协议

![image-20210412153358822.png](https://image.3001.net/images/20210421/1618994924_607fe6ec19e6fb0cb2c6f.png!small)

在curl_ssl_session结构体中，同样未对ip进行定义

![image-20210412153713335.png](https://image.3001.net/images/20210421/1618994934_607fe6f64e921696240d4.png!small)

这就为DNS Rebinding创造了条件。

2、在实际的环境中并非所有的client都支持tls session，以下是支持tls session的client列表：

![image-20210412154631960.png](https://image.3001.net/images/20210421/1618994943_607fe6ff61512572bba1a.png!small)

3、并非所有的攻击目标都适合，由于在步骤5中发送的报文是标准的client
hello报文，因此需要被攻击目标在tcp报文的时候具备容错性。在设置payload报文的时候，也需要尽量使用0x0d、0x0a来与其他字段隔离。

## 0x05 攻击实践

### 0x051 配置DNS Server

dns server设置第一次解析的ip地址为真实的ip，后续请求利用https server的响应301重定向，重新解析，从而解析为期望攻击的ip

![image-20210413142320832.png](https://image.3001.net/images/20210421/1618994962_607fe71268235a40a86ee.png!small)

### 0x052 配置https服务

设置session_id list,设计列表中的每个元素长度为DNS 应答中session字段长度

![image-20210413140618293.png](https://image.3001.net/images/20210421/1618994975_607fe71fbf005639dfa37.png!small)

设置https server 10s休眠时间，同时进行301重定向，重用session id

![image-20210413141924133.png](https://image.3001.net/images/20210421/1618994983_607fe727a1f2180734e14.png!small)

生成https server私钥和证书

    
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout private.key -out server.crt
    

![image-20210413185329323.png](https://image.3001.net/images/20210421/1618994995_607fe733d07f317473a0e.png!small)

启动https server

    
    
    python3 tls.py server --max-ver tls1.2 -k ./private.key -c ./server.crt 0.0.0.0:11211
    

### 0x053 模拟内网的memcached业务

使用docker在内网ip上部署memcached服务

![image-20210413145602448.png](https://image.3001.net/images/20210421/1618995009_607fe7410d23eee21cf03.png!small)

### 0x054 触发攻击

####  **场景一，使用curl访问https server**

    
    
    curl -4 -kvL https://https.server:11211
    

观察curl请求信息，经过了301重定向，在301重定向的过程中，client进行了session resumption

![image-20210413115459539.png](https://image.3001.net/images/20210421/1618995022_607fe74e3efb2f6db3c31.png!small)

最后恶意的dns server响应了期望攻击的ip地址，client向目标ip发送了client hello报文，报文中的session
id携带了payload

![image-20210413115920131.png](https://image.3001.net/images/20210421/1618995035_607fe75ba273a285afdfe.png!small)

查看dns server解析结果，看到了多次解析结果

![image-20210413153917902.png](https://image.3001.net/images/20210421/1618995045_607fe76549f2362600673.png!small)

检查memcached服务，攻击成功！

![image-20210413120033866.png](https://image.3001.net/images/20210421/1618995055_607fe76fd7f301b31d3f2.png!small)

#### 场景二，使用真实的SSRF漏洞环境

部署SSRF漏洞场景，限制请求协议为HTTPS、HTTP，代码如下：

    
    
    <?php
    function curl($url){
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, True);
        curl_setopt($ch,CURLOPT_SSL_VERIFYPEER, False);
        curl_setopt($ch, CURLOPT_SSLVERSION,'all');
        curl_setopt($ch, CURLOPT_PROTOCOLS, CURLPROTO_HTTP | CURLPROTO_HTTPS);  // 限制为HTTPS、HTTP协议
        curl_setopt($ch, CURLOPT_HEADER, 0);
        curl_exec($ch);
        curl_close($ch);
    }
    
    $url = $_GET['url'];
    curl($url);
    ?>
    
    
    
    root@kali:/var/www/html# ls -l
    total 4
    -rw-r--r-- 1 root root 526 Apr 13 14:49 ssrf.php
    

启动apache服务

    
    
    systemctl start apache2.service
    

清除memcachd中的所有键值

![image-20210413190433952.png](https://image.3001.net/images/20210421/1618995070_607fe77ecd3f159f6d068.png!small)

触发SSRF漏洞

    
    
    curl http://192.168.9.191/ssrf.php?url=https://https.server:11211
    

查看dns server解析结果，依然看到了多次解析结果，第一次为真实ip

![image-20210413190315603.png](https://image.3001.net/images/20210421/1618995081_607fe7895fee8e283ad01.png!small)

检查memcached服务，攻击成功！

![image-20210413184456226.png](https://image.3001.net/images/20210421/1618995091_607fe79383cf7150e18df.png!small)

### 0x055 报文分析

以场景一为例

 **DNS 解析过程分析**

在抓包过程中，client端和dns server一共有两次交互，第一次dns应答为真实的ip，第二次为期望攻击的ip

![image-20210414093534008.png](https://image.3001.net/images/20210421/1618995109_607fe7a5ade2d92ee855c.png!small)

同时可以看到dns应答中的ttl值被设置为0

![image-20210413193258517.png](https://image.3001.net/images/20210421/1618995123_607fe7b357fcdffecabf5.png!small)

 **HTTPS 请求报文分析**

在第一个server hello报文中，设置session id 为payload

![image-20210413204054381.png](https://image.3001.net/images/20210421/1618995141_607fe7c5ac8bf3437cfe2.png!small)

后续的tls握手中，使用了session resumption，client 使用第一次server hello报文中的session
id来进行会话复用，节约一个RTT

![image-20210414092612031.png](https://image.3001.net/images/20210421/1618995151_607fe7cf67fe9dd307252.png!small)

最后由于dns server 解析地址为内网地址，client向目标机器发送client hello报文，session id 携带payload

![image-20210414093303089.png](https://image.3001.net/images/20210421/1618995161_607fe7d92c6f211e9ee16.png!small)

## 0x06 总结

HTTPS协议目的是为了对传输报文进行加密，防止中间人攻击，但是为了提高通信效率，对client、server端进行优化，导致了攻击行为的发生，在曾经的SSRF漏洞利用过程中，通过该议题的学习，HTTPS协议也需要被重视起来。

一些可行的预防措施：

> client端禁止HTTPS session resumption；
>
> session resumption 验证ip；
>
> 防止dns rebinding，使用第一次解析后的ip地址替换域名访问目标应用

