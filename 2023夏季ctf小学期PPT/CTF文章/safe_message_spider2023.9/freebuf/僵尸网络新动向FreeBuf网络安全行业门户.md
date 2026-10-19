**最近发现一些恶意软件活动影响了许多运行Linux的设备，该平台今年刚刚解决了许多问题。对检索到的恶意软件样本的进一步分析显示，这些操作与一个名为Momentum的僵尸网络（根据在其通信通道中找到的图像命名）有关。此外发现了僵尸网络目前用于攻击其他设备和执行DDoS攻击的工具以及技术细节。**

Momentum将Linux平台按CPU体系结构划分，如ARM、MIPS、Intel、Motorola
68020等。此恶意软件的主要目的是打开后门并针对给定目标进行各种DoS攻击。该僵尸网络的后门是Mirai、Kaiten和Bashlite变体。此外它还通过各种路由器和web服务上的多个漏洞在目标设备上下载和执行shell脚本进行传播。

## Momentum工作方式分析

感染设备后，Momentum试图修改“rc”文件来实现持久控制；然后它加入command and
control（C&C）服务器并连接到名为“HellRoom”的internet中继聊天（IRC）通道以注册自身并接受命令。IRC协议是与C&C服务器通信的主要方法。僵尸网络可以通过向IRC通道发送消息来控制受感染的机器。

![](https://image.3001.net/images/20200106/1578282838_5e12af5642463.png!small)

![](https://image.3001.net/images/20200106/1578282856_5e12af680b56a.png!small)

分发服务器（如上所示）托管恶意软件。另一个服务器是僵尸网络的C&C服务器。C&C服务器最新上线时间为2019年11月18日。

一旦建立了通信线路，Momentum就可以使用各种命令进行攻击。Momentum可以部署36种不同的DoS方法，如下所示。

![](https://image.3001.net/images/20200106/1578282964_5e12afd4063c0.png!small)

![](https://image.3001.net/images/20200106/1578283004_5e12affc8fc35.png!small)

![](https://image.3001.net/images/20200106/1578283023_5e12b00fe04a4.png!small)

恶意软件使用已知的反射和放大方法，这些方法有多种目标：MEMCACHE、LDAP、DNS和Valve Source
Engine。在这些类型的攻击中，恶意软件通常会将源IP地址（受害者）欺骗到可公开访问的服务器上，从而引发大量响应使受害者不堪重负。

除了DoS攻击之外，Momentum还可以执行其他操作：在指定IP端口上打开代理、更改客户端nick、禁用或启用客户端的packeting等等。

## Momentum拒绝服务攻击

### LDAP DDoS反射

在LDAP DDoS反射中，恶意软件将目标系统的源IP地址欺骗到可公开访问的LDAP服务器，从而向目标发送大量响应。

### Memcache攻击

在Memcache攻击中，远程攻击者使用伪造源IP地址向易受攻击的UDP
memcached服务器发送恶意UDP请求。然后memcached服务器向目标发送响应。Momentum使用HTTP
GET请求下载反射文件。恶意软件在其他放大的DoS攻击中也使用相同的请求。

根据Shodan的初始数据，有42000多个memcached服务器可能受到此类攻击的影响。

僵尸网络使用以下HTTP GET请求下载反射文件：

![](https://image.3001.net/images/20200106/1578293176_5e12d7b8bb712.png!small)

### UDP-BYPASS攻击

在UDP-BYPASS攻击中，通过在特定端口上构造和卸载UDP来淹没目标主机。执行此攻击时，恶意软件会选择一个随机端口和负载，将其发送到目标主机。恶意软件使用多线程进行此攻击；每个线程都有一个端口，后跟其负载。

以下是一些端口及其负载的列表：

![](https://image.3001.net/images/20200106/1578293266_5e12d812ce3c0.png!small)

![](https://image.3001.net/images/20200106/1578293289_5e12d829797b7.png!small)

![](https://image.3001.net/images/20200106/1578293312_5e12d840e4125.png!small)

![](https://image.3001.net/images/20200106/1578293335_5e12d857a2133.png!small)

![](https://image.3001.net/images/20200106/1578293358_5e12d86e5c9a6.png!small)

![](https://image.3001.net/images/20200106/1578293383_5e12d8876051e.png!small)

上面看到的大多数脚本都用于服务发现。如果它们长时间发送到目标设备，会实现拒绝服务，使服务崩溃。

### Phatwonk攻击

phatwink攻击一次执行多个DoS方法：XMAS、一次执行所有标志、usyn（urg syn）和任何TCP标志组合。

## Momentum其他能力

通常恶意软件试图逃避检测，保持开放的沟通渠道，以及更多的持续成功的运动。Momentum还有其他功能可以帮助它传播和破坏设备：

快速流量。僵尸网络采用快速流量技术，使其指挥控制网络更具弹性。快速流量网拥有多个与域名相关联的IP地址，然后不断快速连续地更改地址，从而误导或逃避安全调查。

后门。攻击者可以向IRC通道发送命令（“BASH”、“SHD”或SH命令），恶意软件客户端将在受感染的系统上接收并执行该命令。结果将被发送回攻击者。

传播。通过尝试利用下表中列出的漏洞传播。调查中的C&C服务器显示了1232名受害者。对于其他服务器可能会有更多。

![](https://image.3001.net/images/20200106/1578294244_5e12dbe474748.png!small)

![](https://image.3001.net/images/20200106/1578294268_5e12dbfc3e093.png!small)

![](https://image.3001.net/images/20200106/1578294288_5e12dc108dc6d.png!small)

![](https://image.3001.net/images/20200106/1578294326_5e12dc36df3b8.png!small)

![](https://image.3001.net/images/20200106/1578294347_5e12dc4bb400d.png!small)

![](https://image.3001.net/images/20200106/1578294363_5e12dc5b4ba04.png!small)

## IOC

![](https://image.3001.net/images/20200106/1578294548_5e12dd14db88f.png!small)

 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/ddos-attacks-and-iot-exploits-new-activity-from-momentum-botnet/)，由Kriston编译，转载请注明来自FreeBuf.COM**

