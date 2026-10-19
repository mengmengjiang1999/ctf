本文是接续《[利用Frida手动绕过Android APP证书校验](https://www.freebuf.com/column/233260.html)
》和《[泄露的网站证书和私钥？来做些有趣的实验吧！](https://www.freebuf.com/column/231634.html)
》这两篇文章的后续，将这两篇文章中提到的技术进行了简化和实现和拓展，提供一种新的测试思路。  

## 故事的开始

书接上文。在使用Apache配置了反向代理，利用Proxifier转发流量并使用Burpsuite抓包后，发现这一流程非常麻烦，且难以在其他领域复现。比如测试目标是IoT设备，无法接入设备修改Hosts文件，则较难引导流量。

虽然说ARP攻击也是可以完成的，但是很容易在局域网内引起网络拥堵、丢包等情况：总是会觉得设备响应变慢，用Wireshark抓包的时候看到一大片重传包（不知道是不是哪里设置的不对，如果有大佬知道还烦请指点一二）。

因此想到使用DNS欺骗的方法来引导流量，并搭建反向代理，在出口上指定Proxy到Burpsuite，这样就可以在一个程序里完成全部操作，省时省力。

## DNS欺骗

这里的DNS欺骗其实是有歧义的。一般意义上说DNS欺骗，大体就是两种：篡改Hosts和本地DNS劫持。

 **篡改Hosts** ：这种方法并不通用，很多设备都无法修改Hosts文件，如IoT设备、未Root的安卓/iOS设备等。

 **本地DNS劫持**
：这种方式使用ARP引导流量，过滤出其中的DNS请求，将要篡改的域名进行响应。一般用Ettercap工具去做（如果一定要劫持推荐试试Bettercap），但是仍然没跳出ARP的范畴。

因此这里选用了一个门槛略高但方式更加温和的思路：伪造DNS服务器。

门槛高是因为这种方式需要接触设备/路由器，将其中的首选DNS服务器地址设置成本机的IP，而温和是因为这种方式并不会对局域网流量造成任何影响。使用ARP攻击，局域网内会有大量的假ARP请求，且目标机器的流量全部会经过本机，而我们感兴趣的可能只是其中很小很小很小的一部分。

## 开始动手

既然确定了思路，下面就是动手环节了，先搭建一个DNS服务器。

### 写一个简易DNS服务器

为什么要自己写一个？不用现成的？

这两个疑问可能是很多人（包括我自己）都会提出的，毕竟重复造轮子是一件很没有意义和效率的事情。但是基于我找到的DNS服务器搭建都是很复杂的方案，比如`Bind9`，`Windows
Server`等等，尝试过后发现复杂且难用（压根就没配置成功过），于是一气之下就打算自己写一个。

原理很简单，在本地监听53端口，当流量到达的时候按照DNS的协议解析，将要查询的域名提取出来，根据本地的规则匹配后返回IP，并封装成DNS应答发送出去。

![image-20200423164654717.png](https://image.3001.net/images/20200424/1587695256_5ea24e98bcb18.png!small)

在查询DNS解析协议的时候，发现网上竟然有类似的Python代码，虽然说性能肯定不行，但是毕竟承载的设备数量不多，自己测试用肯定没问题。

于是拿来主义，Copy过来源码，简单调试一下，成功！

在此声明一下，这段源码在很多不同的博客或社区都有转载，但是无一例外都没注明作者。在进一步搜索之后，某一个博客页面上转载的代码里有一句注释，表明这个代码的作者是`@author:
RobinTang`，不知道我这样使用是否侵权~原始代码如下：

    
    
    '''  
    Created on 2012-10-15  
    @author: RobinTang  
    '''  
    ​  
    import socketserver  
    import struct  
    ​  
    # DNS Query  
    class SinDNSQuery:  
        def __init__(self, data):  
            i = 1  
            self.name = ''  
            while True:  
                d = data[i]  
                if d == 0:  
                    break;  
                if d < 32:  
                    self.name = self.name + '.'  
                else:  
                    self.name = self.name + chr(d)  
                i = i + 1  
            self.querybytes = data[0:i + 1]  
            (self.type, self.classify) = struct.unpack('>HH', data[i + 1:i + 5])  
            self.len = i + 5  
        def getbytes(self):  
            return self.querybytes + struct.pack('>HH', self.type, self.classify)  
    ​  
    # DNS Answer RRS  
    # this class is also can be use as Authority RRS or Additional RRS  
    class SinDNSAnswer:  
        def __init__(self, ip):  
            self.name = 49164  
            self.type = 1  
            self.classify = 1  
            self.timetolive = 190  
            self.datalength = 4  
            self.ip = ip  
        def getbytes(self):  
            res = struct.pack('>HHHLH', self.name, self.type, self.classify, self.timetolive, self.datalength)  
            s = self.ip.split('.')  
            res = res + struct.pack('BBBB', int(s[0]), int(s[1]), int(s[2]), int(s[3]))  
            return res  
    ​  
    # DNS frame  
    # must initialized by a DNS query frame  
    class SinDNSFrame:  
        def __init__(self, data):  
            (self.id, self.flags, self.quests, self.answers, self.author, self.addition) = struct.unpack('>HHHHHH', data[0:12])  
            self.query = SinDNSQuery(data[12:])  
        def getname(self):  
            return self.query.name  
        def setip(self, ip):  
            self.answer = SinDNSAnswer(ip)  
            self.answers = 1  
            self.flags = 33152  
        def getbytes(self):  
            res = struct.pack('>HHHHHH', self.id, self.flags, self.quests, self.answers, self.author, self.addition)  
            res = res + self.query.getbytes()  
            if self.answers != 0:  
                res = res + self.answer.getbytes()  
            return res  
    # A UDPHandler to handle DNS query  
    class SinDNSUDPHandler(socketserver.BaseRequestHandler):  
        def handle(self):  
            data = self.request[0].strip()  
            dns = SinDNSFrame(data)  
            socket = self.request[1]  
            namemap = SinDNSServer.namemap  
            if(dns.query.type==1):  
                # If this is query a A record, then response it  
    ​  
                name = dns.getname();  
                if namemap.__contains__(name):  
                    # If have record, response it  
                    dns.setip(namemap[name])  
                    socket.sendto(dns.getbytes(), self.client_address)  
                elif namemap.__contains__('*'):  
                    # Response default address  
                    dns.setip(namemap['*'])  
                    socket.sendto(dns.getbytes(), self.client_address)  
                else:  
                    # ignore it  
                    socket.sendto(data, self.client_address)  
            else:  
                # If this is not query a A record, ignore it  
                socket.sendto(data, self.client_address)  
    ​  
    # DNS Server  
    # It only support A record query  
    # user it, U can create a simple DNS server  
    class SinDNSServer:  
        def __init__(self, port=53):  
            SinDNSServer.namemap = {}  
            self.port = port  
        def addname(self, name, ip):  
            SinDNSServer.namemap[name] = ip  
        def start(self):  
            HOST, PORT = "0.0.0.0", self.port  
            server = socketserver.UDPServer((HOST, PORT), SinDNSUDPHandler)  
            server.serve_forever()  
    ​  
    # Now, test it  
    if __name__ == "__main__":  
        sev = SinDNSServer()  
        sev.addname('www.aa.com', '192.168.0.1')    # add a A record  
        sev.addname('www.bb.com', '192.168.0.2')    # add a A record  
        sev.addname('*', '0.0.0.0') # default address  
        sev.start() # start DNS server  
    ​  
    # Now, U can use "nslookup" command to test it  
    # Such as "nslookup www.aa.com"

这段代码在Win Python 3.7环境下是没问题，可以正常响应，但是有两个问题：

  1. 只能对域名进行精准匹配，无法使用`*`通配符；

  2. 对于没有指定的域名，若设置了`default address`，则会一律返回该地址，否则就不回复

在使用过程中，我需要让这个服务器对于我没指定的地址回复真实地址，这样可以保证被欺骗设备的其他业务是正常的（业务间可能存在关联性，某一业务无法访问可能导致其他业务停止），同时通配符可以减少统计域名的麻烦，也不会漏掉流量。

针对以上两点，对源代码进行了部分的修改（修改详情可参考文末的连接）。

### 写一个反向代理服务器

虽然使用Apache + Proxifier可以转流量，但是用到的工具多不易排错，且当需要修改配置时，Apache配置文件的查询、新增都相对麻烦。

反向代理转发的思路也很简单：因为DNS欺骗，客户端会把流量发到本机，因此

  1. 本机监听端口，将收到的HTTP(S)流量解析；

  2. 取出Host字段中的目标域名、端口，重组新的请求发出；

  3. 获取服务端响应

  4. 发送给客户端

![image-20200423171132217.png](https://image.3001.net/images/20200424/1587695273_5ea24ea9c65cb.png!small)

既然要求便捷且不考虑性能，直接用Python的`http.server`模块构建一个HTTP服务器接收请求即可。

重写`http.server.BaseHTTPRequestHandler`模块，对其中的HTTP方法处理进行重写即可：

    
    
    class MyHandler(http.server.BaseHTTPRequestHandler):  
        def req(self):  
            try:  
                if isinstance(self.request, ssl.SSLSocket):  
                    scheme = "https://"  
                else:  
                    scheme = "http://"  
                      
                # 根据Host信息重组URL  
                self.url = scheme + self.headers["host"].strip("\n") + self.path  
    ​  
                # 判断是否有HTTP Body  
                if self.headers.__contains__('Content-Length'):  
                    data = self.rfile.read(int(self.headers['Content-Length']))  
                else:  
                    data = ""  
    ​  
                req = requests.Request(method=self.command, url=self.url, headers=self.headers, data=data)  
                s = requests.Session()  
                prepped = req.prepare()  
    ​  
                # 将请求通过代理发送出去  
                r = s.send(prepped, verify=False,proxies=proxies, allow_redirects=False, stream=True)  
    ​  
                # 设置对客户端的响应头  
                self.send_response(r.status_code)  
                for key in r.headers:  
                    self.send_header(key, r.headers[key])  
                self.end_headers()  
    ​  
                # 写入Response Body，写完后会自动发出这个请求  
                self.wfile.write(r.content)  
            except IOError as e:  
                print(e)  
                self.send_error(404, 'file not found: %s' % self.path)  
            except Exception as e:  
                print(e)  
    ​  
        def do_GET(self):  
            self.req()  
    ​  
        def do_POST(self):  
            self.req()  
    ​  
        def do_HEAD(self):  
            self.req()  
    ​  
        def do_OPTIONS(self):  
            self.req()  
    ​  
        def do_PUT(self):  
            self.req()  
    ​  
        def do_DELETE(self):  
            self.req()  
    ​  
        def do_MOVE(self):  
            self.req()  
    ​  
        def do_TRACE(self):  
            self.req()

`http.server.BaseHTTPRequestHandler`模块会读取当前请求的`HTTP
Method`，并调用`do_xxx`函数来进行处理。在这里我们并不需要对不同Method进行差异化处理，我们只想安安静静把他们转发出去，因此下面的`do_xxx`全部都调用`req()`统一进行处理。

完整代码已上传Github：<https://github.com/mactavishmeng/mitmserver>

Github上的版本是将DNS服务器和反代服务器集成在一起，通过配置文件`mitmserver.json`来进行配置：

    
    
    {  
      "proxies" : {"http": "http://127.0.0.1:8080",  
                   "https":"http://127.0.0.1:8080"},  
      "dns_list" : [  
            {"host": "www.baidu.cn", "address": "192.168.1.3"},  
            {"host": "*.baidu.cn", "address": "192.168.1.3"},  
            {"host": "www.google.com", "address": "192.168.1.3"}  
        ],  
      "dns_query_enable" : true,  
      "http_list" : [  
            {"address":"0.0.0.0", "port":80, "ishttps":false},  
            {"address":"0.0.0.0", "port":443, "ishttps":true, "certfile":"./certificate.crt", "keyfile":"./private_key.key"}  
        ]  
    }

在这个配置文件中可以轻易的对各个部分进行方便的调整，如配置的代理，本地监听的HTTP(S)端口，证书，DNS列表等。

## 实战验证

实际使用中，整个流程的核心有两点：DNS如何欺骗，HTTPS证书是否是真的。

### 配置DNS

虽然上面说了那么多，还写了一个DNS服务器， **但是如果你的路由器支持插件，可以自定义hosts** ，实际上是不需要这么麻烦的。比如我借到的这台极路由：

![image-20200423193023221.png](https://image.3001.net/images/20200424/1587695287_5ea24eb7d0292.png!small)

直接用插件强行更改设备的DNS查询结果，不过有些路由器不支持修改Hosts，并不通用。

  1.  **手机、PC等可直接修改网络配置的设备**

对于手机APP来说，可以直接在“无线局域网”中将IP设置修改为“静态”，在DNS服务器部分配置IP为本机即可。以安卓为例：

![image-20200423173255950.png](https://image.3001.net/images/20200424/1587695297_5ea24ec122c77.png!small)

  2.  **IoT设备等无法直接修改配置的设备**

而IoT设备因为无法在设备上操作，需要在路由器上设置， _如果能获得控制权的话 ; - )_

将路由器的DNS设置为本机IP即可（不同路由器界面可能不同，但原理是一样的）：

![image-20200423192754552.png](https://image.3001.net/images/20200424/1587695319_5ea24ed7e6b4d.png!small)  

至此，设备端DNS欺骗的前置步骤完成。

### 配置反向代理

打开`mitmserver.json`，修改其中的监听端口的配置。

如这里监听的APP通信，它与三个域名进行HTTPS通信，其中两个域名访问443，一个域名访问9988。此时配置列表里需打开两个监听端口（443、9988），并将`"ishttps"`的值设置为`true`，表示这个端口监听HTTPS。后面的`certfile`和`keyfile`部分填入证书和私钥文件的路径。

如果你没有这两个文件，可以从Burpsuite等抓包工具中导出，或使用openssl工具生成自签名证书。

### 开始抓包

在本机上配置好要监听的端口、要劫持的域名、填入Burpsuite的地址后，即可开始抓包。

因为手头上没有合适的能公开的IoT设备，因此以安卓APP为例，其原理是一致的。

APP已经做了证书校验的绕过，所以这里的HTTPS证书是随意找了一个来配置的（毕竟已经绕过校验）。配置文件如下：

![image-20200424101749926.png](https://image.3001.net/images/20200424/1587695404_5ea24f2c437f6.png!small)

配置DNS。这里偷懒没有去路由器上配置，直接在手机上配了，因此在运行日志里看到的请求源是手机的IP。如果在路由器上配置，则日志中的请求IP会是网关的IP。

运行起来：

![image-20200424102218780.png](https://image.3001.net/images/20200424/1587695415_5ea24f37436c7.png!small)

对应在Burpsuite中拦截到的请求：

![image-20200424102421991.png](https://image.3001.net/images/20200424/1587695419_5ea24f3b6af5a.png!small)

这样，仅需一个py文件就完成了全部的流程，简单方便，且增减配置只需要修改JSON的配置即可，比起在Apache的conf文件中改来改去方便的多。

#  

