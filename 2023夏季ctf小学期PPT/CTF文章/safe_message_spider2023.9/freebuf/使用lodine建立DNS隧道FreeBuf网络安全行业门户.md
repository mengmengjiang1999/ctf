****

**![flat-800x800-075-f.u2.jpg](https://image.3001.net/images/20180720/153207263867.jpg!small)**

**最近我在我的一个VPS上设置了DNS隧道。这项技术对于绕过captive
portals（强制登录门户），过滤器等非常有用。由于DNS是互联网不可或缺的重要服务，因此在大多数网络中通常都会放行53端口的进出数据流量。**

虽然有时这些DNS请求仅限于白名单服务器或特定域，但你通常会发现DNS几乎是完全不受限制的，如果我们能控制管道的两端，那么我们就可以通过隧道来传输数据。

我们可以在端口53上设置一个SSH服务器或其它类似服务器，但在某些情况下ssh协议会被过滤，从而导致隧道建立失败。因此，通过DNS建立隧道才是我们最好的选择。

## Iodine

为此，我们将用到一款名为[iodine](http://code.kryo.se/iodine/)的工具。Iodine是一款DNS隧道制造工具，通过一台DNS服务器就可以为我们建立一个IPv4的数据通道，该工具常被渗透测试人员用于防火墙绕过等场景。

Iodine由我们在服务器上运行的DNS
daemon（守护进程）组成，该守护进程侦听传入的DNS请求并解包隧道数据。另外，我们还有一个客户端用于处理隧道的另一端。

##  **注册DNS服务器**

首先，我们要做的就是将我们的服务器注册为DNS服务器。为此，我们需要一个域名。[GoDaddy](https://godaddy.com/)上有一些非常便宜的域名，并且支持隐私选项。这样也避免了我们的个人详细信息，被通过whois轻松地查找到。

获取域名后，我们必须在域名控制面板中为其配置NS记录，例如：

    
    
    t1		IN	NS	ourdomain.com.		; note the dot!

如果你手头已有一个现成的域，并希望你的iodine服务器能够使用其它的服务器，那么你可以先设置子域并注册iodine服务器的IP，然后将你的NS记录指向此子域即可。

    
    
    t1		IN	NS	t1ns.ourdomain.com.		
    t1ns		IN	A	<iodine-server-ip>

##  **设置daemon（守护进程）**

接下来我们要做的是在服务器上安装iodine。如果你当前使用的系统是基于debian的发行版，那么你可以像我一样使用apt install
iodine命令进行安装。

使用以下命令运行iodine daemon：

    
    
    iodined -fcP secretpassword 10.0.1.1 ourdomain.com

> -f 在前台运行
>
> -c 禁用检查所有传入请求的客户端IP地址
>
> -P secretpassword 客户端和服务器之间用于身份验证的共享密钥详情
>
> 10.0.1.1 是服务器将在tun接口客户端上提供的IP。客户端将在该范围内给出下一个IP。
>
> ourdomain.com 是我们之前设置的DNS服务器的域名。

如果你想要将iodine设置为在启动时运行，你可以使用以下命令启用该服务：

    
    
    update-rc.d iodine enable

以及

    
    
    service iodine start

来启动该服务。但你会发现此时启动会失败。想要顺利启动服务，我们必须要在/etc/defaults/iodine文件中设置daemon参数，如下：

> START_IODINED true
>
> IODINED_ARGS -c 10.0.1.1 ourdomain.com
>
> IODINED_PASSWORD secretpassword

##  **配置检查**

基本配置完成后，我们可以通过[iodine check](http://code.kryo.se/iodine/check-it/)页面来检查我们的配置是否正确。

如果配置无误但仍无法正常工作，那么请检查流量是否有被服务器上的防火墙捕获的情况。

##  **运行客户端**

在客户端机器上，我们只需运行iodine客户端即可。iodine的安装方法与上面是一样的，然后运行：

    
    
    iodine -fP secretpassword ourdomain.com

你应该能够看到像Connection setup complete, transmitting data这样的输出信息。

DNS隧道已成功建立！

##  **设置代理**

为了使我们的浏览器或其他工具能够使用隧道，我们必须设置代理。我们将利用SSH动态端口转发，在本地创建SOCKS代理，所有的数据流量都将使用DNS
tunnel并通过SSH连接到我们的服务器。

通过以下命令来设置代理：

    
    
    ssh -N -D 8080 user@10.0.1.1

> -N 指示SSH不要启动shell，因为我们只是想创建代理
>
> -D 设置动态端口转发，SOCKS代理端口为8080
>
> user 我们服务器上的用户
>
> 10.0.1.1 tun接口上的iodine服务器

设置完成后，我们就可以在浏览器中使用代理了。例如我们可以使用Firefox或Chrome中的FoxyProxy。如果一切顺利，你应该能够在浏览器中检查你的IP并获取你服务器的IP。

 ***参考来源：[jmpesp](https://jmpesp.me/dns-tunnelling-with-iodine/)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

