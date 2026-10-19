## **什么是LLMNR？**

 **LLMNR（Link-Local Multicast Name
Resolution，链路本地多播名称解析）协议是一种基于DNS包格式的协议。它可以将主机名解析为IPv4和IPv6的IP地址。这样用户就可以直接使用主机名访问特定的主机和服务，而不用记忆对应的IP地址。该协议被广泛使用在Windows
Vista/7/8/10操作系统中。**

该协议的工作机制很简单。例如，计算机A和计算机B同处一个局域网中。当计算机A请求主机B时，先以广播形式发送一个包含请求的主机名的UDP包。主机B收到该UDP包后，以单播形式发送UDP的响应包给主机A。由于整个过程中，都是以UDP方式进行，主机A根本不能确认响应主机B是否为该主机名对应的主机，这就造成欺骗的可能。

##  **LLMNR利用介绍**

针对这个漏洞，Kali
Linux提供了Responder工具。该工具不仅可以嗅探网络内所有的LLMNR包，获取各个主机的信息，还可以发起欺骗，诱骗发起请求的主机访问错误的主机。为了渗透方便，该工具还可以伪造HTTP/s、SMB、SQL
Server、FTP、IMAP、POP3等多项服务，从而采用钓鱼的方式获取服务认证信息，如用户名和密码等。

![QQ五笔截图未命名1.png](https://image.3001.net/images/20180513/15262234383288.png!small)  

 **结合PDF获取PC Hashes**

利用bad-pdf工具生成pdf payload，没有PDF版本限制。工具下载地址：

<https://github.com/deepzec/Bad-Pdf>（工具使用里面包含详细说明）

在本地调试使用如下：

![QQ五笔截图未命名.png](https://image.3001.net/images/20180513/15262234509144.png!small)

报了两个错，如图：

![QQ五笔截图未命名5.png](https://image.3001.net/images/20180513/15262234748624.png!small)

以上两个错都是相连的（自己排错很久才找到答案），在这就说说排错的思路吧，看了下源代码，首先调用的是responder =
'/usr/bin/responder'

![QQ五笔截图未命名3.png](https://image.3001.net/images/20180513/15262234928738.png!small)

但是responder服务是肯定存在的，但是路径是不存在，如图所示：  

![QQ五笔截图未命名6.png](https://image.3001.net/images/20180513/15262235583585.png!small)

这里想到的是responder执行路径不对？带着疑问想到一个办法，试试自建目录看看，能不能运行如图：  

![QQ五笔截图未命名7.png](https://image.3001.net/images/20180513/15262235891071.png!small)

解决了路径问题，但是显示：Permission denied（权限被拒绝），那么给这个目录加上最高权限，结果如图：

![QQ五笔截图未命名8.png](https://image.3001.net/images/20180513/1526223608178.png!small)

没有把responder调用起来，这里想到的是单独运行responder，使用方法如图：

![QQ五笔截图未命名10.png](https://image.3001.net/images/20180513/1526223627560.png!small)

运行生成的pdf payload，最终利用responder结合PDF文件攻取到Hashes，如图：

![QQ五笔截图未命名9.png](https://image.3001.net/images/20180513/15262236434484.png!small)

最后其实把路径改成：/usr/sbin/responder，之前走那些都是弯路，一顿百度猛如虎，实际调用路径少个字母（不能被源代码的路径蒙蔽双眼）。

 ***本文作者：biock，转载请注明来自FreeBuf.COM**

