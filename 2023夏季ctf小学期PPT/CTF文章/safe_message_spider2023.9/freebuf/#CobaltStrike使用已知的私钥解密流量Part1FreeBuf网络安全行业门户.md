博客系列：Cobalt Strike：流量解密

  * Cobalt Strike: 使用已知的私钥解密流量 - Part 2
  * Cobalt Strike: 使用进程内存解密流量 - Part 3
  * Cobalt Strike：使用已知的私钥解密流量-Part 1（当前部分）
  * Cobalt Steike: 解密被掩盖的流量 - Part 4
  * Cobalt Strike: 解密DNS流量 - Part 5

 _我们发现6个流氓软件Cobalt Strike的私钥，可以用来将C2网络流量进行解密_

Cobalt Strike信标（客户端）和Cobalt
Strike团队服务器（C2）之间的通信是用AES加密的（即使通过HTTPS进行）。AES密钥由信标生成，并使用加密的元数据blob（默认为cookie）传达给C2。

RSA加密被用来[加密这个元数据](https://research.nccgroup.com/2020/06/15/striking-back-at-retired-cobalt-strike-a-look-at-a-legacy-vulnerability/)：信标有C2的公钥，C2有私钥。

![image](https://image.3001.net/images/20220405/1649127690_624bb10a20e457ff7e4d7.jpg!small)

图1：C2 流量

公钥和私钥都存储在.cobaltstrike.beacon_keys文件中。这些密钥是在Cobalt
Strike团队服务器软件第一次使用时产生的。在我们对面向互联网的Cobalt
Strike服务器进行指纹识别时，发现许多不同的服务器都在使用公钥。这就意味着它们使用相同的私钥，因此它们的.cobaltstrike.beacon_keys文件是共享的。

我们验证了一个可能的解释：是否有被破解的Cobalt
Strike版本，由恶意行为者使用，其中包括一个.cobaltstrike.beacon_keys？这个文件不是合法的Cobalt
Strike软件包的一部分，因为它是在第一次使用时产生的。

查遍了VirusTotal，我发现了10个破解版的Cobalt
Strike：ZIP文件中包含了一个名字是.cobaltstrike.beacon_key的文件，再总的这10个文件包中，我解压出来6种不同的RSA钥匙对。其中2个密钥对已经在互联网上流传了：在我们采集指纹的Cobalt
Strike服务器（1500多个）中，有25%使用这2个密钥对中的一个。这一关键信息现在包括在工具[1768.py](https://blog.didierstevens.com/2021/10/11/update-1768-py-version-0-0-8/)中，该工具由Didier Stevens开发，用于提取Cobalt Strike信标的配置。

只要一个公钥与已知的私钥被提取出来时，该工具就会标注出来。

![image](https://image.3001.net/images/20220405/1649127706_624bb11a3e4227cd61960.jpg!small)  
图2：1768.py 从beacon中解压出的配置信息

至少，这一信息进一步确认了样本来自于一个恶意的Cobalt Strike服务器（而不是红队服务器）。

使用选项verbose，私钥信息也会显示出来。

![image](https://image.3001.net/images/20220405/1649127719_624bb127cda932f3f82fa.jpg!small)

图3：添加verbose选项能够显示私钥信息

这可以被用于解密元数据，以及C2流量（这方面的后面细讲）

![image](https://image.3001.net/images/20220405/1649127732_624bb134e7c506f5fa08b.jpg!small)

图4：解密元数据

在后面的博客文章中，我将展示关于如何使用私钥解析元数据和解密C2数据流的一些细节。

 **关于作者**

Didier Stevens是一位为NVISO工作的恶意软件分析专家。Didier是SANS Internet Storm
Center的高级处理员和微软的MVP，他开发了许多流行的工具来协助进行恶意软件分析。你可以在[Twitter](https://twitter.com/DidierStevens)和[LinkedIn](https://be.linkedin.com/in/didierstevens)找到Didier。

