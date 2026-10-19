## **概述** ****

在奇安信威胁情报中心日常样本监控流程中发现，近期Emotet僵尸网络活动剧增。大量垃圾邮件被投放，经过溯源Emotet在今年6月份时曾经销声匿迹，C
&C活动骤减，经过几个月的休整后现又卷土重来。在此提醒广大用户不要轻易打开未知邮件，提高安全意识。

##  **样本分析** ****

文件名|  20190920_188705_0081.doc  
---|---  
MD5| 03bc503ba6b2444ca2500ed64844ea7f  
VT上传时间| 2019/09/20  
  
![图片.png](https://image.3001.net/images/20190923/1569229704_5d888b882c970.png!small)

附件doc中含有恶意宏，运行后会释放并运行恶意jse文件。Jse文件会下载并执行emotet。

![图片.png](https://image.3001.net/images/20190923/1569229730_5d888ba2d33c6.png!small)

通过VT可以看出投放了相当多的网站：

![图片.png](https://image.3001.net/images/20190923/1569229739_5d888bab10341.png!small)

下载得到的emotet loader为MFC编写，会读取资源中的加密shellcode并解密为下一层loader：

![图片.png](https://image.3001.net/images/20190923/1569229766_5d888bc619aee.png!small)

本层loader会直接加载内存中的下一层明文dll：

![图片.png](https://image.3001.net/images/20190923/1569229782_5d888bd6a8be8.png!small)

Dll同样直接内存加载下一层明文exe：

![图片.png](https://image.3001.net/images/20190923/1569229791_5d888bdf2d4b4.png!small)

本层明文exe为emotet本体，运行之后首先会带参数重启自身，之后将自身复制到系统路径并创建服务。

![图片.png](https://image.3001.net/images/20190923/1569229799_5d888be724aa9.png!small)

整体流程：

![图片.png](https://image.3001.net/images/20190923/1569229806_5d888bee82440.png!small)

之后收集系统信息，例如主机名，受感染机器上的所有进程等，使用Deflate算法压缩后，进行RSA+AES加密，进行Base64编码后发送到远程服务器上，并准备下载后续的Payload。

![图片.png](https://image.3001.net/images/20190923/1569229813_5d888bf54ef66.png!small)

WireShark截图：

![图片.png](https://image.3001.net/images/20190923/1569229818_5d888bfa2c904.png!small)

后续的payload为TrickBot。

![图片.png](https://image.3001.net/images/20190923/1569229933_5d888c6d49cfc.png!small)

根据不同的时间和地区下载的payload有变化：PandaBanker，Ryuk，Wacatac等恶意软件。

##  **同源分析** ****

Emotet最初是由2014在野外被发现，其最初被设计为银行木马窃取用户敏感信息和重要数据，早期的Emotet分发方式单一化，仅仅通过JS恶意代码进行传播，最近几年，Emotet经过若干个版本的迭代之后，分发渠道越来越规范化，组织化，体系化：通过商贸信，漏洞，或者伪装成正规软件并上传到第三方下载站诱导用户下载等等，代码功能也发生了重大的变化，从原来的银行木马变成了恶意软件分发商，通过内置的RSA公钥从C
&C服务器下载其他的恶意软件如PandaBanker、TrickBot银行木马或者Ryuk勒索病毒。同时受害者分布也从早期的欧美国家扩大到亚太地区。

此次新活动的样本大都伪装成正规软件。

![图片.png](https://image.3001.net/images/20190923/1569229943_5d888c7770675.png!small)

且此次投放的Emotet外层均使用MFC编写，左边为老版本的外层，右边为新捕获的外层：

![图片.png](https://image.3001.net/images/20190923/1569229953_5d888c8182d89.png!small)

最后一层为EmotetPayload，不同Hash的Emotet最后解出来的EmotetPayload都是相同的，这里我们使用BiniDiff，比较了老版本版的EmotetPayload和最新捕获的EmotetPayload，之间的不同。

![图片.png](https://image.3001.net/images/20190923/1569229960_5d888c88cd24b.png!small)

代码结构发生了较大的变化，代码混淆以及复杂度变高，增加了反调试和自校验，核心DownLoader功能依然不变。奇安信威胁情报中心将对现有的流行家族进行持续的追踪和预警，目前奇安信集团全线产品，包括天眼、SOC、态势感知、威胁情报平台，支持对涉及emotet的攻击活动检测，并且奇安信安全助手支持对该组织的样本进行拦截。

## **IOC** ****

文件Hash

d27f692276898374f578ab6d207ab063

3a74a93e7831d0953b5cefb9c98505f1

aaedf631838a59d0ecf35c31a5ba788e

C&C IP

190.106.97.230

186.75.241.230

149.167.86.174

181.143.194.138

192.241.250.202

149.167.86.174

181.164.8.25  

URL

hxxp://186.75.241.230/walk/img/sess/  
hxxp://149.167.86.174:990/pnp/report/sess/

  
  

