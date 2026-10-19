***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 0x0 背景  

**njRAT至少自2013年以来一直存在，是最流行的恶意软件系列之一。该恶意软件内置于.NET
Framework中，可为攻击者提供对受感染系统的远程控制，利用动态DNS进行命令和控制（C＆C），并在可配置端口上使用自定义TCP协议进行通信。被称为njRAT
Lime
Edition的新恶意软件版本包括对勒索软件感染，比特币采集卡和分布式拒绝服务（DDoS）的支持，同时还能够记录击键，通过USB驱动器传播，窃取密码和锁定屏幕。**

##  **0x1 实验**

实践是检验真理的唯一标准，这里搭建了模拟了一下勒索的场景。

**IP** | **OS** | **Remark**  
---|---|---  
192.168.184.139 | Windows 2008 R2 | Victim  
192.168.184.140 | Windows 2008 R2 | Hacker  
  
现在先在攻击机上面安装好了Njrat Lime Edition版本，这个版本比上个版本的文件结构感觉更加清晰一些。

![1.JPG](https://image.3001.net/images/20180906/1536208602_5b90aedaae584.jpg!small)

设置好port与key之后运行服务端，在生成客户端的时候这里可以生成client或者downloader。

![2.JPG](https://image.3001.net/images/20180906/1536208614_5b90aee6ab3a7.jpg!small)

生成客户端的时候有了更多的选项，特别明显的地方就是多了比特币采集卡其他常用功能也都一一具备：

> **ü 隐藏文件路径**
>
> **ü U盘传播**
>
> **ü 干掉杀软**
>
> **ü 开机启动**
>
> **ü 添加注册表**
>
> **ü 守护进程**

![3.JPG](https://image.3001.net/images/20180906/1536208624_5b90aef04a190.jpg!small)

将生成好的Client在Victim机器上面运行之后服务端可以收到一个连接的sessions，展示了关于Victim上面的一些计算机信息。

![4.JPG](https://image.3001.net/images/20180906/1536208641_5b90af0135d5e.jpg!small)

对受害者进行操作就可以发现多了很多常用的功能，比如一键勒索、比特币、压力测试(slowis) 、Bypass
UAC、干掉杀软、关机删Cookie等功能，居然还有一个torrent。

![5.JPG](https://image.3001.net/images/20180906/1536208654_5b90af0eb8585.jpg!small)

这里测试一下一键勒索加密：

![6.JPG](https://image.3001.net/images/20180906/1536208665_5b90af19957fd.jpg!small)

客户端的文件被加密成了Lime结尾的文件、桌面背景也被更改：

![7.JPG](https://image.3001.net/images/20180906/1536208679_5b90af27b1f2b.jpg!small)

一键decrypt之后文件已经恢复：

![8.JPG](https://image.3001.net/images/20180906/1536208697_5b90af393e882.jpg!small)

##  **0x2 受害端的情况**

在受害端的机器上可以看到进程在运行，文件路径在APPDATA这个隐藏目录下面，且无父进程。

![9.JPG](https://image.3001.net/images/20180906/1536208714_5b90af4a17be2.jpg!small)

已经添加了开机启动项与注册表：  

![10.JPG](https://image.3001.net/images/20180906/1536208727_5b90af572ccf3.jpg!small)

最后还可以用textMessages留个言：

![11.JPG](https://image.3001.net/images/20180906/1536208744_5b90af68c70a8.jpg!small)

##  **0x3 防护建议**

1.此类攻击方式较多通过邮件附件进行传播，对于可疑的邮件附件要谨慎、谨慎、再谨慎。

2.捆绑软件安装也是常用的一种传播方式，建议到软件官网与可信第三方软件进行下载。

3.本地安装安全软件及时查杀出恶意文件。

4.安全无小事，日常需谨慎，提升安全知识，日常逛Freebuf。

 ***本文作者：si1ence，转载请注明来自FreeBuf.COM**

