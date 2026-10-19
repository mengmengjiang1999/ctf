> **观前提示**
>
>
> 本篇文章部分基础原理和设置可参考《[使用Python搭建反向代理分析设备流量](https://www.freebuf.com/column/234866.html)》一文，部分原理在该文中已阐述，本文不再赘述。

书继续接上文。在愉快的搭建了反向代理展开一系列测试之后，当我测试某台IoT设备的时候，Burpsuite中收到了一个异形数据包，且设备无法正常联网，开启代理之后过一会儿就显示设备离线。  

这个数据包是在设备尝试登录云平台的时候，请求`/login`时发生的：

![image-20200515161731104.png](https://image.3001.net/images/20200519/1589852799_5ec33a7f32f56.png!small)

从Response可以看出，这个请求的响应似乎是三个数据包叠在一起了，一个是正常的Response，紧接着是两个连续的POST请求。

但是，在Python的`Requests`模块在处理Response的时候，会通过头部的`Content-Length`字段对后面的Body部分进行裁剪，导致在Burpsuite中看到的响应与实际从Python反向代理发出的不一致（实际发出的时候后面两个POST请求直接被删掉了）。

分析到这里，我初步认为是Python在处理异形Response的时候没有带上后续的请求，导致设备无法接收到预期的数据从而无法进行后续的通信。

## 使用自定义字符串验证

既然如此，在解决这个问题之前，需要先验证想法是否正确。`Requests`无法处理这种数据，且每次回复的内容都是固定的，那先尝试用 **自定义的字符串**
作为Response来进行回复，绕过`Requests`对响应包的解析（代理部分的完整代码请参见[上一篇文章](https://www.freebuf.com/column/234866.html)）：

![image-20200518102743490.png](https://image.3001.net/images/20200519/1589853100_5ec33bac49831.png!small)

先用Burpsuite代替设备尝试访问，验证这样设置的回复是否是预期的：![image-20200518103302446.png](https://image.3001.net/images/20200519/1589853151_5ec33bdf1ab96.png!small)

与之前抓包的内容一致。

开启设备，本以为可以正常了，结果发现设备端不断的在发送Login请求，而且没有任何后续的请求到达，那么说明设备端并没有认这个回复。

折腾了许久也没想明白到底是怎么回事，毕竟响应包里并没有什么认证信息，暂时排除认证失败导致的设备响应异常，直到无意间用Wireshark抓了一下包之后发现了其中的秘密：

![image-20200518143904406.png](https://image.3001.net/images/20200519/1589853276_5ec33c5cd1d5a.png!small)![image-20200518143827391.png](https://image.3001.net/images/20200519/1589853279_5ec33c5f8f14d.png!small)

先分析本机的抓包结果，可以很明显的看到一个完整的TCP交互过程，从三次握手开始，然后是协商TLS的密钥，再传输数据，最后四次挥手断开连接。数据传输阶段，也只是有三个`Application
Data`包进行了传输。

而分析路由器上抓包结果，设备端在三次握手建立连接、TLS协商后，有着大量的数据包交互，显然整个流程上与代理部分完全不同。

## 检查协议头

再次回头去看请求中的内容，在头部的`Connection`字段中发现了端倪。

回到Burpsuite中那个“异形”数据包。可以看到在Response的部分中，头部的`Connection`字段的值为`Keep-Alive`：

![image-20200519095658256.png](https://image.3001.net/images/20200519/1589853434_5ec33cfa0dd4c.png!small)

一般情况下，这个值是`Close`，如访问 **百度首页** 的请求中，Request和Response中的值：

![image-20200518145409550.png](https://image.3001.net/images/20200519/1589853466_5ec33d1a6c4f2.png!small)

而这个“异形”数据包里的`Keep-Alive`就显得有点与众不同。

通过度娘初步得知，`Connection: Keep-Alive`是长连接建立的标志，而在
**[RFC2616](https://tools.ietf.org/html/rfc2616)**
的第8章中对长连接有详细的描述。实际上这种头部定义的连接应该叫做持久连接（Persistent
Connection），即建立一次TCP连接后，利用该连接进行多次通信，减少建立TCP连接产生的负载。

> 8.1.1 Purpose  
> Prior to persistent connections, a separate TCP connection was  
> established to fetch each URL, increasing the load on HTTP servers  
> and causing congestion on the Internet. The use of inline images and  
> other associated data often require a client to make multiple  
> requests of the same server in a short amount of time.  
>  
> 在持久连接出现之前，每次请求URL时都会建立一个单独的TCP连接，(这种做法)增加了HTTP服务器的负载，并造成Internet的拥塞。  
> 在使用内联图片及其他相关数据时，客户端需要在短时间内向同一个服务端发起多次请求。

在Wikipedia上，我们常说的“短连接”和“长连接”的示意图如下（可能翻译成“多次连接”和“持久连接”会更贴近原意）：

![1920px-HTTP_persistent_connection.svg.png](https://image.3001.net/images/20200519/1589853542_5ec33d6691708.png!small)

但是，需要注意的是，虽然是允许在同一个TCP连接中传输多次数据，但模式仍是客户端发起、服务端响应，服务端并不能直接向客户端发送数据。

## WebSocket与持久连接

从路由器抓包的内容，以及文章开头提及的那个“异形”数据包来看，似乎设备与服务端的通信并不是单纯的设备端请求、服务端应答的模式，而更偏向于全双工的形式，即服务端也能向设备端主动发送数据。这里乍看起来很像WebSocket(引用自Wikipedia)：

> WebSocket 是独立的、创建在TCP上的协议。  
> Websocket 通过 HTTP/1.1 协议的101状态码进行握手。  
> 为了创建Websocket连接，需要通过浏览器发出请求，之后服务器进行回应，这个过程通常称为“握手”（Handshaking）。

![image-20200518153422059.png](https://image.3001.net/images/20200519/1589853568_5ec33d806c8d1.png!small)

而实际从代理中看到的那个“异形”数据并没有`Upgrade`头部，且`Connection`字段也不是Upgrade，那么并不是标准的WebSocket协议。

## 编写工具

经过一系列分析，现在能确定的是：

  1. 这个设备在与服务器通信的时候使用的是一个TCP连接传输多次数据

  2. 设备端并非只进行Response，而是有主动发送数据的能力

  3. 协议用的仍是基于HTTP的协议，而不是WebSocket

那么我们需要该工具能处理 **长连接（持久连接）**
，在设备侧和服务器侧均保持连接的状态，且根据双方的情况选择建立或断开连接。即任意一方在断开连接后，工具能正确关闭另一侧的连接（工具处理流量的拓扑图参见上一篇文章中的图）。

作为中间人工具，无需对请求进行处理，如判断URL，判断Method等，只需要单纯的转发即可，因此可以不用HTTP框架，直接用Socket来处理到达的TCP连接并转发。

起初打算用线程的方式来完成对两端的连接管理，一条线程负责监听设备端发送来的数据，并发送给客户端；另一条线程负责监听服务端发送的数据并转发给客户端：

![image-20200518160456346.png](https://image.3001.net/images/20200519/1589853607_5ec33da7e7aa1.png!small)

但是，直接设置线程在管理上会比较麻烦，当客户端主动断开连接时，需要通知另一线程关闭；此时还需要判断当前线程对应的另一线程中的Socket是哪一个，涉及到线程之间交互，要动用队列等，较为麻烦。

使用Python的`select.epoll`可以进行异步I/O操作，正好适用于当前的场景。epoll是一种异步I/O模型，允许以非阻塞的模式处理I/O，如TCP连接。在代码逻辑上与线程的方式最直观的区别，就是它会等待Socket连接活动，并触发事件，利用epoll提供的FD来表示当前处理的Socket连接是哪一个，对于管理服务端和客户端的连接都非常方便。

核心代码如下：

    
    
    # 解析到达的HTTP请求  
    def get_info(request):  
        if '\r\n\r\n' in request:  
            [req_list, body] = request.split('\r\n\r\n')  
        else:  
            req_list = request  
            body = ''  
        req_list = req_list.split('\r\n')  
        if len(req_list) > 1:  
            info = req_list[0]  
            req_list.remove(req_list[0])  
            headers = {}  
            for item in req_list:  
                header = item.split(': ')  
                headers[header[0]] = header[1]  
            return {"request": info,  
                    "headers": headers,  
                    "body": body}  
        else:  
            return False  
    ​  
    ​  
    def main():  
        port = 443  
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)  
          
        # 载入证书文件  
        certfile = './conf/cert.crt'  
        keyfile = './conf/cert.key'  
        context.load_cert_chain(certfile, keyfile)  
        print("Loading cert files:", certfile, keyfile)  
          
        # 建立Socket监听客户端请求  
        SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        SOCK.bind(("0.0.0.0", port))  
        SOCK.listen(100)  
          
        # 设置证书  
        tcp_server_socket = context.wrap_socket(SOCK, server_side=True)  
        tcp_server_socket.setblocking(False)  
          
        # 启用epoll  
        epl = select.epoll()  
        epl.register(tcp_server_socket.fileno(), select.EPOLLIN)  
          
        # 连接池，用来管理连接  
        fd_event_dict = dict()  
          
        # 主循环  
        while True:  
            fd_event_list = epl.poll()  
            for fd, event in fd_event_list:  
                  
                # 当新连接到达  
                if fd == tcp_server_socket.fileno():  
                    # 建立连接  
                    new_socket, client_addr = tcp_server_socket.accept()  
                    # 在epoll中注册  
                    epl.register(new_socket.fileno(), select.EPOLLIN)  
                    # 加入连接池  
                    fd_event_dict[new_socket.fileno()] = [new_socket, None]  
                # 当有数据读入  
                elif event == select.EPOLLIN:  
                    # 接收数据（Bytes）  
                    try:  
                        recv_data = fd_event_dict[fd][0].recv(4096).decode("utf-8")  
                        # 若有数据接收到  
                        if recv_data:  
                            # 判断当前这个fd有没有建立对端  
                            # 一般情况下是设备端（客户端）发起连接，此处检查有没有与服务端建立连接  
                            if fd_event_dict[fd][1] is None:  
                                # 解析HTTP请求  
                                info = get_info(recv_data)  
                                # 读取请求里的Host字段  
                                host = info["headers"]["Host"].split(":")[0]  
                                # 建立新连接  
                                new_socket = ssl.wrap_socket(socket.socket())  
                                new_socket.connect((host, port))  
                                # 注册  
                                epl.register(new_socket.fileno(), select.EPOLLIN)  
                                # 将这个fd写入当前连接的字典中  
                                fd_event_dict[fd] = (fd_event_dict[fd][0], new_socket.fileno())  
                                # 添加一个新的项  
                                fd_event_dict[new_socket.fileno()] = (new_socket, fd)  
                            # 如果有建立对端，则直接发送  
                            # socket.getpeername(): 返回发送方的IP地址和端口  
                            peer_fd = fd_event_dict[fd][1]  
                              
                            # 打印信息  
                            print("\n" + "-" * 20)  
                            print("From: %s, To: %s, fd: %s" % (fd_event_dict[fd][0].getpeername()[0], fd_event_dict[peer_fd][0].getpeername()[0], fd))  
                            print("\n" + recv_data + "\n" + "-" * 20)  
                              
                            # 发送数据  
                            fd_event_dict[peer_fd][0].send(recv_data.encode())  
                        # 没有数据则表示连接断开  
                        else:  
                            # 关闭对端socket并反注册  
                            peer_fd = fd_event_dict[fd][1]  
                            if peer_fd:  
                                fd_event_dict[peer_fd][0].close()  
                                epl.unregister(peer_fd)  
                                del fd_event_dict[peer_fd]  
                            # 关闭当前socket  
                            fd_event_dict[fd][0].close()  
                            # 反注册  
                            epl.unregister(fd)  
                            # 删除记录  
                            del fd_event_dict[fd]  
    ​  
                    # 错误处理  
                    except ssl.SSLError as e:  
                        # 关闭对端socket并反注册  
                        peer_fd = fd_event_dict[fd][1]  
                        if peer_fd:  
                            fd_event_dict[peer_fd][0].close()  
                            epl.unregister(peer_fd)  
                            del fd_event_dict[peer_fd]  
                        # 关闭当前socket  
                        fd_event_dict[fd][0].close()  
                        # 反注册  
                        epl.unregister(fd)  
                        # 删除记录  
                        del fd_event_dict[fd]  
                        print("SSL Error", len(fd_event_dict), e)  
                    except OSError as e:  
                        print("OS Error", len(fd_event_dict))

代码质量不是很高，因为也是临时测试用，就没有优化，大神勿喷~

## 实战演示

在实战之前需要指出，epoll仅在Linux系统环境下支持，在Windows下Python会提示`AttributeError: module
'select' has no attribute 'epoll'`。解决方法有两个：

一是用虚拟机，缺点是网络上可能不好设置，有些网络状况没法选桥接；二是如果是Windows 10系统，可以通过安装WSL(Windows Linux
Subsystem)来解决。WSL在文件和网络接口上与Windows都是共用的，但是可以运行Linux程序，非常好用，安装也比较便捷，随便搜索一下都有一大把教程，安装和使用在此不再赘述。

提示：在Linux环境下操作网络需要管理员权限，因此需要加`sudo`命令，否则会报错！

### DNS欺骗

在查看之前，需要先引导流量到本机上，因此需要DNS欺骗。方法仍是利用极路由插件设置，将目标域名的IP设置成本机IP即可。

![image-20200518164513484.png](https://image.3001.net/images/20200519/1589853654_5ec33dd646866.png!small)

这里说明一下，一般来说访问网络连接都会用域名的形式，但如果测试目标头很铁就是要用IP的方式，那么DNS欺骗就没用了（都没解析DNS骗啥！），这时候只能选择ARP攻击，将流量引导到本机，再设置iptables端口转发。

**另外一个要说明的地方，如果在路由器上做DNS欺骗，PC和被测目标都会被欺骗（这就是传说中的“连自己都骗”吗），因此需要在PC端手动修改Hosts文件来避免自己被欺骗从而无法正常将数据转发出去。**
以上图中的`www.bbb.com`为例，在本机的hosts文件中添加真实解析：

![image-20200519091131549.png](https://image.3001.net/images/20200519/1589853686_5ec33df66fcc1.png!small)

此外，如果你使用的是WSL，那么需要在WSL中修改而不是Windows中。

> 小提示：
>
> DNS解析顺序优先级为 **本地缓存** > **Hosts文件** > **路由器DNS** > **ISP DNS服务器**

### 流量监听

设置好DNS欺骗之后，重启目标设备，此时设备会请求目标域名的DNS，路由器会回复我们设置的值（即本机IP），此时流量是发往PC端的，再由Python进行转发到真实服务器。逻辑图大致如下：

![image-20200519092531330.png](https://image.3001.net/images/20200519/1589853800_5ec33e6862eee.png!small)

打开工具，等待设备连接（如果设备流量没走工具转发，可以尝试重启设备以清空DNS缓存），即可在控制台看到流量信息：

![image-20200519093541545.png](https://image.3001.net/images/20200519/1589853806_5ec33e6e98290.png!small)

这里可以明显看到从服务端推送过来的数据，也和之前在Wireshark中查看的内容吻合。

接下来即可在原来的代码基础上，对数据发送的部分进行魔改，来完成篡改、伪造消息的操作。因为这部分代码定制化较高，且写的不完善，在此就不放出了，大家可以各显神通来完成这部分逻辑。

