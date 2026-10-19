*****本文原创作者si1ence，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
**

##  **0x0 背景**

**Njrat，又称Bladabindi，该木马家族使用.NET框架编写，是一个典型的RAT类程序，通过控制端可以操作受控端的文件、进程、服务、注册表内容，也可以盗取受控端的浏览器的保存的密码信息等内容。**

 **新版的Njrat新增了更加流行的一些功能点，如勒索压力测试，BTC钱包采集、对抗安全工具等使用新功能。**

客户端(Client)生成界面与后台控制端(Server)如图：

![图片1.png](https://image.3001.net/images/20180919/1537328691_5ba1c6339ba46.png!small)

##  **0x1 源码分析** ****

总体代码结构比上一个版本会显得更加丰富了一些，这里重点看一下新增部分的内容。

![图片2.png](https://image.3001.net/images/20180919/1537328715_5ba1c64b283e1.png!small)

##  **0x2 勒索加密与解密**

最开始是先获取了二个路径Applicationdata和Startup二个特殊路径，然后从Mypath一个输入型变量的路径开始与最开始的二个路径进行比较后，调用Crypt方法进行加密。

![3.png](https://image.3001.net/images/20180919/1537328726_5ba1c65693199.png!small)

主要加密的文件目录如下:

![4.png](https://image.3001.net/images/20180919/1537328737_5ba1c66153aa4.png!small)

加密算法主要使用了AES对称加密体制同时采用了电码本模式ECB(Electronic Codebook
Book)，过程中定义了32个Byte的密钥分组，分组密钥长度为256位。

![5.png](https://image.3001.net/images/20180919/1537328753_5ba1c671bce9e.png!small)

对称加密，解密算法与之基本一致。

##  **0x3 压力测试(DDOS)**

木马主要内置了Slowloris作为流量攻击的主体，这个玩意评价很高可以用很少的带宽实现攻击效果。

核心的调用方法如下：

![6.png](https://image.3001.net/images/20180919/1537328767_5ba1c67f6a555.png!small)

##  **0x4 U盘感染**

首先获取到系统的设备信息然后找到已经连接好类型为Removable类型的磁盘，获取到U盘的文件路径与木马母体的路径，并更改隐藏属性。

![图片1.png](https://image.3001.net/images/20180919/1537329111_5ba1c7d702a4c.png!small)

将真实存在的文件全部设置为隐藏文件，并新建Link类型的快捷方式。用户在点击link运行快捷方式的同时，将会自动触发病毒母体的运行。

![7.png](https://image.3001.net/images/20180919/1537328787_5ba1c6930f13e.png!small)

##  **0x5 排除异己**

木马运行时将会检查系统当中是否存在一些安全查杀工具与虚拟机检测，发现后讲干掉这些异己。(仿佛明白了为什么PChunter每次的进程名都是随机字符串的原因)

例举几个被监控的安全工具：

>  **Process Hacker**
>
>  **Process Explorer**
>
>  **dnSpy**
>
>  **Sandboxie Control**
>
>  **wireshark**
>
>  **SpyTheSpy**
>
>  **Reflector**

![10.png](https://image.3001.net/images/20180919/1537328918_5ba1c71631372.png!small)

##  **0x6 总结**

1\. 现在木马增加了很多对抗安全工具的方式，日常应急响应过程中需要格外仔细检查

2\.
有更多基本功能的分析比如一些通信协议、获取键盘信息、远程控制等操作可移步菠菜大佬安全分析过的文章：【[传送门](http://www.freebuf.com/articles/network/122244.html)】。

 ***本文原创作者si1ence，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

