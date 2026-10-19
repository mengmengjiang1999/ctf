##  **背景**

**近日，国外安全研究人员曝光了一种名为InnfiRAT的新型木马，该木马使用.NET编写，具有窃取用户信息、抓取浏览器Cookie用于窃取密码、屏幕截取、下载执行其他恶意文件等行为。除此之外，该木马还会查找主机上的加密货币钱包信息，用于窃取加密货币（莱特币和比特币）。**

##  **功能分析**

![](https://image.3001.net/images/20190919/1568856213_5d82d89512bf4.png!small)

木马进程首先检测自身路径是否为％AppData％\NvidiaDriver.exe，并且终止名为NvidiaDriver.exe的进程，将自身复制到％AppData％\NvidiaDriver.exe再次执行：

![](https://image.3001.net/images/20190919/1568856218_5d82d89aeb9eb.png!small)

以NvidiaDriver.exe重新运行后，会拼接一段base64编码的数据，解码后是一个PE文件，加载到内存中执行：

![](https://image.3001.net/images/20190919/1568856222_5d82d89eea0a7.png!small)

获取主机信息，检查Manufacturer是否包含相关字符串，以此来进行反虚拟机操作：

![](https://image.3001.net/images/20190919/1568856227_5d82d8a30392a.png!small)

创建DuplexChannelFactory来与C&C服务器进行通讯：

> tcp://62[.]210[.]142[.]219:17231/Ivictim

![](https://image.3001.net/images/20190919/1568856231_5d82d8a7ba062.png!small)

检查是否存在相关分析工具的进程，如果存在，将结束该进程：

![](https://image.3001.net/images/20190919/1568856235_5d82d8ab8b642.png!small)

创建定时任务执行木马母体：

![](https://image.3001.net/images/20190919/1568856239_5d82d8afa7481.png!small)

从指定连接下载和执行文件：

![](https://image.3001.net/images/20190919/1568856246_5d82d8b63c28a.png!small)

窃取UserProfile信息发送的C&C端：

![](https://image.3001.net/images/20190919/1568856251_5d82d8bbc2f35.png!small)

窃取下列指定浏览器的Cookie信息：

Chrome、Yandex、Kometa、Amigo、Torch、Orbitum、Opera

![](https://image.3001.net/images/20190919/1568856256_5d82d8c05f4f2.png!small)

窃取加密货币钱包信息：

![](https://image.3001.net/images/20190919/1568856261_5d82d8c5ab60a.png!small)

**IOCs**

**MD5:**

> f992dd6dbe1e065dff73a20e3d7b1eef

**URL:**

> tcp://62.210.142.219:17231/IVictim

**参考链接**

> <https://www.zscaler.com/blogs/rese>

***本文作者： 深信服千里目安全实验室，转载请注明来自FreeBuf.COM**  
  

