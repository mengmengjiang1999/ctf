这是在绿盟的时候扫出来的一个漏洞，在这里记录一下它的原理，验证方法及利用过程。

## 1️⃣漏洞验证

> ip: X.X.X.X, TTL>220s

![image](https://image.3001.net/images/20210818/1629295315_611d12d395c7688b757e4.png!small)

## 2️⃣漏洞利用

Kali上安装测试工具SlowHttpTest

    
    
    sudo apt-get install slowhttptest
    

**Slow headers攻击**

    
    
    slowhttptest -c 1000 -H -g -o my_header_stats -i 10 -r 200 -t GET -u https://x.x.x.x -x 24  -p 3
    

![image](https://image.3001.net/images/20210818/1629295317_611d12d5075503d88ee75.png!small)

**Slow body攻击**

    
    
    slowhttptest -c 3000 -B -g -o my_body_stats -i 110 -r 200 -s 8192 -t FAKEVERB -u https://x.x.x.x -x 10 -p 3
    

![image](https://image.3001.net/images/20210818/1629295318_611d12d6b7a027b84b283.png!small)

**Slow read攻击**

    
    
    slowhttptest -c 8000 -X -r 200 -w 512 -y 1024 -n 5 -z 32 -k 3 -u https://x.x.x.x -p 3
    

![image](https://image.3001.net/images/20210818/1629295320_611d12d83d7032400eb73.png!small)

工具使用参数：

    
    
    -g 在测试完成后，以时间戳为名生成一个CVS和HTML文件的统计数据 
    -H SlowLoris模式 
    -B Slow POST模式 
    -R Range Header模式 
    -X Slow Read模式 
    -c number of connections 测试时建立的连接数 
    -d HTTP proxy host:port 为所有连接指定代理 
    -e HTTP proxy host:port 为探测连接指定代理 
    -i seconds 在slowrois和Slow POST模式中，指定发送数据间的间隔。 
    -l seconds 测试维持时间 
    -n seconds 在Slow Read模式下，指定每次操作的时间间隔。 
    -o file name 使用-g参数时，可以使用此参数指定输出文件名 
    -p seconds 指定等待时间来确认DoS攻击已经成功 
    -r connections per second 每秒连接个数 
    -s bytes 声明Content-Length header的值 
    -t HTTP verb 在请求时使用什么操作，默认GET
    -u URL 指定目标url 
    -v level 日志等级（详细度） 
    -w bytes slow read模式中指定tcp窗口范围下限 
    -x bytes 在slowloris and Slow POST tests模式中，指定发送的最大数据长度 
    -y bytes slow read模式中指定tcp窗口范围上限 
    -z bytes 在每次的read()中，从buffer中读取数据量
    

## 3️⃣漏洞由来

> DDOS——CC攻击——缓慢的HTTP DOS攻击

一句话总结：DDOS、CC攻击的变种

## 4️⃣攻击原理

对任何一个开放了HTTP访问的服务器HTTP服务器，先建立了一个连接（三次握手），指定一个比较大的content-length，然后以非常低的速度发包，比如1-10s发一个字节，然后维持住这个连接不断开。如果客户端持续建立这样的连接，那么服务器上可用的连接将一点一点被占满，从而导致拒绝服务。

![image](https://image.3001.net/images/20210818/1629295322_611d12da4cf7786168e91.gif!small)

只要Web服务器开放了Web服务，那么它就可以是一个靶子，HTTP协议在接收到request之前是不对请求内容作校验的，所以即使你的Web应用没有可用的form表单，这个攻击一样有效。

![image](https://image.3001.net/images/20210818/1629295324_611d12dc9042076a91993.png!small)

在客户端以单线程方式建立较大数量的无用连接，并保持持续发包的代价非常的低廉。实际实验中一台普通PC可以建立的连接在3000个以上。这对一台普通的Web
server，将是致命的打击。更不用说结合肉鸡群做分布式DoS了。

## 5️⃣慢速攻击分类

慢速HTTP拒绝服务攻击主要有三种攻击类型，分别是Slow headers、Slow body、Slow read。

 **Slow headers**  
Web应用在处理HTTP请求之前都要先接收完所有的HTTP头部，因为HTTP头部中包含了一些Web应用可能用到的重要的信息。攻击者利用这点，发起一个HTTP请求，一直不停的发送HTTP头部，消耗服务器的连接和内存资源。抓包数据可见，攻击客户端与服务器建立TCP连接后，每30秒才向服务器发送一个HTTP头部，而Web服务器再没接收到2个连续的\r\n时，会认为客户端没有发送完头部，而持续的等等客户端发送数据。

![image](https://image.3001.net/images/20210818/1629295325_611d12dddc3f286fdbff4.png!small)![image](https://image.3001.net/images/20210818/1629295326_611d12de8c342ea45fe56.png!small)

 **Slow body**  
攻击者发送一个HTTP POST请求，该请求的Content-Length头部值很大，使得Web服务器或代理认为客户端要发送很大的数据。服务器会保持连接准备接收数据，但攻击客户端每次只发送很少量的数据，使该连接一直保持存活，消耗服务器的连接和内存资源。抓包数据可见，攻击客户端与服务器建立TCP连接后，发送了完整的HTTP头部，POST方法带有较大的Content-Length，然后每10s发送一次随机的参数。服务器因为没有接收到相应Content-Length的body，而持续的等待客户端发送数据。  
![image](https://image.3001.net/images/20210818/1629295327_611d12df337fe60e95284.png!small)

![image](https://image.3001.net/images/20210818/1629295327_611d12dfcfddaa9037484.png!small)

 **Slow read**  
客户端与服务器建立连接并发送了一个HTTP请求，客户端发送完整的请求给服务器端，然后一直保持这个连接，以很低的速度读取Response，比如很长一段时间客户端不读取任何数据，通过发送Zero
Window到服务器，让服务器误以为客户端很忙，直到连接快超时前才读取一个字节，以消耗服务器的连接和内存资源。抓包数据可见，客户端把数据发给服务器后，服务器发送响应时，收到了客户端的ZeroWindow提示（表示自己没有缓冲区用于接收数据），服务器不得不持续的向客户端发出ZeroWindowProbe包，询问客户端是否可以接收数据。

![image](https://image.3001.net/images/20210818/1629295328_611d12e0b62b1c086524f.png!small)![image](https://image.3001.net/images/20210818/1629295329_611d12e180e42d7ca7d4a.png!small)

## 6️⃣解决办法

> 官方解决方法

针对不同的Server其对慢速http拒绝服务攻击防范方法也不同：

### WebSphere

 **1、限制 HTTP 数据的大小**  
在WebSphere Application Server 中进行如下设置：

任何单个 HTTP 头的默认最大大小为 32768 字节。可以将它设置为不同的值。

HTTP 头的默认最大数量为 50。可以将它设置为不同的限制值。

另一种常见的 DOS 攻击是发送一个请求，这个请求会导致一个长期运行的 GET 请求。WebSphere Application Server Plug-in 中的 ServerIOTimeoutRetry 属性可限制任何请求的重试数量。这可以降低这种长期运行的请求的影响。

设置限制任何请求正文的最大大小。

 **2、设置keepalive参数**

打开ibm http server安装目录，打开文件夹conf，打开文件httpd.conf,查找KeepAlive值，改ON为OFF,其默认为ON。

这个值说明是否保持客户与HTTP SERVER的连接，如果设置为ON，则请求数到达MaxKeepAliveRequests设定值时请求将排队，导致响应变慢。

详见参考链接：

    
    
    http://www.ibm.com/developerworks/cn/websphere/techjournal/1210_lansche/1210_lansche.html#new-step32
    

### Weblogic

 **1、在配置管理界面中的协议- >一般信息下设置 完成消息超时时间小于200**  
 **2、在配置管理界面中的协议- >HTTP下设置 POST 超时、持续时间、最大 POST 大小为安全值范围。**

    
    
    http://docs.oracle.com/cd/E12890_01/ales/docs32/integrateappenviron/configWLS.html#wp1101063
    

### Nginx

 **1、通过调整$request_method，配置服务器接受http包的操作限制；**  
**2、在保证业务不受影响的前提下，调整client_max_body_size,**`client_body_buffer_size,``client_header_buffer_size,large_client_header_buffersclient_body_timeout,``client_header_timeout`的值，必要时可以适当的增加；  
 **3、对于会话或者相同的ip地址，可以使用HttpLimitReqModule and
HttpLimitZoneModule参数去限制请求量或者并发连接数；**  
 **4、根据CPU和负载的大小，来配置worker_processes 和 worker_connections的值，公式是：max_clients =
worker_processes * worker_connections。**

### Apache

建议使用mod_reqtimeout和mod_qos两个模块相互配合来防护。  
1、mod_reqtimeout用于控制每个连接上请求发送的速率。配置例如：  
#请求头部分，设置超时时间初始为10秒，并在收到客户端发送的数据后，每接收到500字节数据就将超时时间延长1秒，但最长不超过40秒。可以防护slowloris型的慢速攻击。

    
    
    RequestReadTimeout header=10-40,minrate=500
    

#请求正文部分，设置超时时间初始为10秒，并在收到客户端发送的数据后，每接收到500字节数据就将超时时间延长1秒，但最长不超过40秒。可以防护slow
message body型的慢速攻击。

    
    
    RequestReadTimeout body=10-40,minrate=500
    

需注意，对于HTTPS站点，需要把初始超时时间上调，比如调整到20秒。

示例：

    
    
    LoadModule reqtimeout_module modules/mod_reqtimeout.so
    <IfModule reqtimeout_module>
            RequestReadTimeout header=10-40,minrate=500 body=10-40,minrate=500
    </IfModule>
    

2、mod_qos用于控制并发连接数。配置例如：  
 **当服务器并发连接数超过600时，关闭keepalive**  
QS_SrvMaxConnClose 600  
 **限制每个源IP最大并发连接数为50**  
QS_SrvMaxConnPerIP 50  
这两个数值可以根据服务器的性能调整。  
更多关于qos_module配置参考：

    
    
    http://mod-qos.sourceforge.net/dos.html
    

示例：

    
    
    LoadModule qos_module modules/mod_qos.so
    <IfModule qos_module>
    QS_SrvMaxConnClose 600
    QS_SrvMaxConnPerIP 50
    </IfModule>
    

### IHS服务器

请您先安装最新补丁包，然后启用mod_reqtimeout模块，在配置文件中加入：

    
    
    LoadModule reqtimeout_module modules/mod_reqtimeout.so
    

为mod_reqtimeout模块添加配置：

    
    
    <IfModule mod_reqtimeout.c>
    RequestReadTimeout header=10-40,MinRate=500 body=10-40,MinRate=500
    

对于HTTPS站点，建议header=20-40,MinRate=500。  
参见：

    
    
    http://www-01.ibm.com/support/docview.wss?uid=swg21652165
    

### F5负载均衡

F5负载均衡设备有相应的防护模块，如无购买可参考附件中的详细配置过程。  
关于F5的慢速攻击防护配置，请参考以下链接：

    
    
    https://support.f5.com/kb/en-us/solutions/public/10000/200/sol10260.html
    https://devcentral.f5.com/articles/mitigating-slow-http-post-ddos-attacks-with-irules-ndash-follow-up
    

### IIS服务器

IIS可配置相关网站的Web.config如下：  
1、WebLimits设置：

    
    
    <configuration>
        <system.applicationHost>
            <webLimits connectionTimeout="00:00:30"
            headerWaitTimeout="00:00:10"
            dynamicIdleThreshold="150"
            minBytesPerSecond="512"
        />
        </system.applicationHost>
    </configuration>
    

参考以下链接：

    
    
    https://docs.microsoft.com/en-us/iis/configuration/system.applicationhost/weblimits#configuration
    

2、headerLimits设置：

    
    
    <configuration>
     <system.webServer>
      <security>
       <requestFiltering>
        <requestLimits>
         <headerLimits>
         <add header="Content-type" sizeLimit="100" />
         </headerLimits>
        </requestLimits>
       </requestFiltering>
      </security>
     </system.webServer>
    </configuration>
    

参考以下链接：

    
    
    https://docs.microsoft.com/en-us/iis/configuration/system.webserver/security/requestfiltering/requestlimits/headerlimits/﻿

