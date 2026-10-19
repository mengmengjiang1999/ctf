**netmap.js是一款基于浏览器，用于提供主机发现和端口扫描功能的网络发现工具。**

netmap.js的执行速度也非常的快，由于其使用了[es6-promise-pool](https://github.com/timdp/es6-promise-pool)，因此它可以有效地运行浏览器允许的最大并发连接数。

## 动机

由于我正需要一个基于浏览器的端口扫描程序来处理我的工作，但我认为直接从[BeEF](http://beefproject.com/)等其他项目导入现有模块或复制粘贴它们太过简单。事实也证明，当前并没有一个像样的即用型npm模块，BeEF中的port_scanner模块（在撰写本文时）不准确，速度慢，且不适用于Chromium。

而netmap.js则是一个优化的“ping”sweeper和TCP扫描器，并且适用于所有现代的浏览器。

## 快速开始

###  **安装**

    
    
    npm install --save netmap.js

###  **查找实时主机**

让我们从家庭环境中找出网站访问者网关的IP地址：

    
    
    import NetMap from 'netmap.js'
    
    const netmap = new NetMap()
    const hosts = ['192.168.0.1', '192.168.0.254', '192.168.1.1', '192.168.1.254']
    
    netmap.pingSweep(hosts).then(results => {
      console.log(results)
    })
    
    
    {
      "hosts": [
        { "host": "192.168.0.1", "delta": 1003, "live": false },
        { "host": "192.168.0.254", "delta": 1001, "live": false },
        { "host": "192.168.1.1", "delta": 18, "live": true },
        { "host": "192.168.1.254", "delta": 1002, "live": false }
      ],
      "meta": {}
    }

主机192.168.1.1似乎当前正处于活动状态。

###  **扫描TCP端口**

让我们尝试扫描主机上开放的TCP端口：

    
    
    import NetMap from 'netmap.js'
    
    const netmap = new NetMap()
    const hosts = ['192.168.1.1', '192.168.99.100', 'google.co.uk']
    const ports = [80, 443, 8000, 8080, 27017]
    
    netmap.tcpScan(hosts, ports).then(results => {
      console.log(results)
    })
    
    
    {
      "hosts": [
        {
          "host": "192.168.1.1",
          "control": "22",
          "ports": [
            { "port": 443, "delta": 15, "open": false },
            { "port": 8000, "delta": 19, "open": false },
            { "port": 8080, "delta": 21, "open": false },
            { "port": 27017, "delta": 26, "open": false },
            { "port": 80, "delta": 95, "open": true }
          ]
        },
        {
          "host": "192.168.99.100",
          "control": "1001",
          "ports": [
            { "port": 8080, "delta": 40, "open": true },
            { "port": 80, "delta": 1001, "open": false },
            { "port": 443, "delta": 1000, "open": false },
            { "port": 8000, "delta": 1004, "open": false },
            { "port": 27017, "delta": 1000, "open": false }
          ]
        },
        {
          "host": "google.co.uk",
          "control": "1001",
          "ports": [
            { "port": 443, "delta": 67, "open": true },
            { "port": 80, "delta": 159, "open": true },
            { "port": 8000, "delta": 1001, "open": false },
            { "port": 8080, "delta": 1002, "open": false },
            { "port": 27017, "delta": 1000, "open": false }
          ]
        }
      ],
      "meta": {}
    }

起初，结果看起来似乎有点矛盾。

192.168.1.1是本地网段上的嵌入式Linux机器（路由器），唯一打开的端口是80。我们可以看到与其他关闭的端口相比，浏览器在80上的错误时间大约延长了5倍。

192.168.99.100是一个host-only
VM，开放了8080端口，google.co.uk是外部主机，443和80都为开放状态。在这种情况下，浏览器在开放端口上相对快速地抛出一个错误，而关闭的端口只是超时。

为了确定端口应该标记为打开还是关闭，netmap.js将扫描一个假定为关闭的“control”端口（默认为45000）。然后，使用控制时间确定其他端口的状态。如果比率delta/control大于设定值（默认值为0.8），则假定端口关闭（tl;dr:
与控制时间相差20%以上则表示端口已打开）。

## 限制

###  **端口黑名单列表**

浏览器维护者一个拒绝连接的端口黑名单列表（如ftp、ssh或smtp）。如果使用默认协议（HTTP）尝试使用netmap.js扫描这些端口，将会返回一个非常短暂的超时。这通常是端口关闭的标志，但对于黑名单端口，这并不意味着什么。

你可以从以下链接查看黑名单列表：

> [Chromium
> source](https://github.com/adobe/chromium/blob/master/net/base/net_util.cc)
>
> [Mozilla docs](https://developer.mozilla.org/en-> US/docs/Mozilla/Mozilla_Port_Blocking)
>
> Edge/IE（如果你找到了请将地址发送给我，非常感谢！）

在[Firefox 61](https://blog.mozilla.org/security/2018/05/07/blocking-ftp-subresource-loads-within-non-ftp-documents-in-firefox-61/)（或其他一些浏览器）之前，可以通过使用ftp协议而不是http来建立连接从而绕过这个限制。在实例化NetMap时，可以在options对象中指定协议。当使用ftp时，你应该期望打开的端口超时，关闭的端口相对较快地出错。FTP扫描还受到本文中讨论的TCP
RST数据包的限制。

“传统”协议（如ftp）的子资源请求已在Chromium中被阻塞了一段时间。

### "Ping" Sweep

netmap.js提供的“ping”扫描功能在快速查找本地网段（其他计算机，电话，路由器，打印机等）上基于 *nix的实时主机方面表现相当不错。

但由于实现的原因，当不返回TCP RST数据包时这将不起作用。典型：

> Windows机器
>
> 一些外部主机
>
> 某些网络设置，例如桥接/host-only VMs

其原因在以下理论部分进行了解释。

此限制不会影响TCP扫描功能，并且仍然可以通过尝试查找其开放端口来确定上述主机是否处于活动状态。

## 使用

###  **NetMap构造函数**

NetMap构造函数采用一个允许你配置的options对象：

> 用于扫描的协议（默认为http，请参阅端口黑名单，了解为什么要将其设置为ftp）
>
> 端口连接超时（默认为1000毫秒）
    
    
    import NetMap from 'netmap.js'
    
    const netmap = new NetMap({
      protocol: 'http',
      timeout: 3000
    })

 **pingSweep()**

pingSweep()方法用于确定给定的主机阵列是否有效，其主要是通过检查与端口的连接是否超时来实现的。在这种情况下，主机被认为是离线状态（参见["Ping"
Sweep](https://github.com/serain/netmap.js#ping-sweep)了解限制和理论的标准情况）。

该方法采用以下参数：

hosts数组要扫描的主机阵列（IP地址或主机名）；

options对象：

> maxConnections - 最大并发连接数（默认情况下Chrome上为10个，其他浏览器为17个 - 浏览器支持的最大并发连接数）
>
> 要扫描的端口（默认为45000）

它返回一个promise对象。

    
    
    netmap.pingSweep(['192.168.1.1'], {
      maxConnections: 5,
      port: 80
    }).then(results => {
      console.log(results)
    })

 **tcpScan()**

tcpScan()方法将针对一系列目标执行端口扫描。请阅读标准案例以了解它是如何做到这一点的。

该方法采用以下参数：

hosts数组要扫描的主机阵列（IP地址或主机名）；

要扫描的端口列表（1-65535之间的整数，避免以上黑名单中的端口）；

options对象：

> maxConnections - 最大并发连接数（默认为6 - 每个域浏览器允许的最大连接数）
>
> portCallback - 当完成host:port组合的扫描时要执行的回调
>
> controlPort - 要扫描的端口，以确定基线关闭端口增量（默认为45000）
>
> controlRatio - 要被视为已关闭端口的控制增量的相似性（百分比）（默认值为0.8，请参见以上示例部分）

它返回一个promise对象。

    
    
    netmap.tcpScan(['192.168.1.1'], [80, 27017], {
      maxConnections: 5,
      portCallback: result => {
        console.log(result)
      },
      controlPort: 45000,
      controlRatio: 0.8
    }).then(results => {
      console.log(results)
    })

## 理论

以下部分将为大家简要介绍模块发现技术背后的理论知识。

###  **总体思路**

此模块使用Image对象尝试请求跨源资源（测试中的一系列http://{host}:{port}
URLs）。浏览器引发错误（delta增量）或在某个超时值后缺少错误所需时间，提供了对正在审查的主机和端口状态的深入了解。

###  **标准情况**

当尝试连接到封闭端口时，活动主机通常会使用TCP RST数据包进行相对快速的响应。

如果端口是打开的，即使它没有运行HTTP服务器，由于建立了完整TCP连接的开销，以及随后意识到无法从提供的URL中获取图像中获取Image，浏览器将需要花费更长的时间来引发错误。

而离线主机则不会响应RST，也不允许建立完整的TCP连接。在超时（~90秒）之前，浏览器仍会尝试建立连接。netmap.js默认等待1000毫秒后会超时。

综上所述：

> 实时主机上的关闭端口将有一个非常短的delta增量
>
> 实时主机上的开放端口将具有稍长的delta增量
>
> 离线主机或未使用的IP地址将会超时

###  **没有TCP RST的情况**

一些主机（如google.co.uk或Windows主机）和一些网络设置（如VirtualBox host-only网络）在命中关闭端口时，并不会返回TCP
RST数据包。

在这种情况下，关闭端口通常会超时，而开放端口则会快速引发错误。

因此，当不返回RST数据包时，pingSweep()方法的实现是不可靠的。

总之，当出于任何原因未返回TCP RST数据包时：

> 实时主机上的关闭端口将超时
>
> 实时主机上的开放端口将有一个短的delta增量
>
> pingSweep()将无法区分关闭端口超时和“dead”主机超时

##  **WebSockets和Ajax**

应该有很好的文档说明，你还能够使用WebSockets和Ajax来映射网络。

我做了一次尝试（也调整了BeEF来尝试它的端口扫描模块，只使用WebSockets和Ajax）；我发现这两种方法产生的结果非常的不可靠。

如果我在这方面有所遗漏，请告诉我。

***参考来源：[GitHub](https://github.com/serain/netmap.js)，FB小编secist编译，转载请注明来自FreeBuf.COM
**  

