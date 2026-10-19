**今天给大家介绍的是一款名叫ExchangeRelayX的工具，这是一款NTLM中继工具，适用于EWS节点和On-Premise微软邮件交换服务器。**

![a.png](https://image.3001.net/images/20180915/1537005143_5b9cd6578bb15.png!small)

## ExchangeRelayX

该工具当前版本为v1.0.01，其实本质上来说它是一个PoC工具，可以演示攻击者如何基于NTLM中继攻击来攻击EWS节点和On-Premise微软邮件交换服务器，并入侵目标用户的电子邮箱。该工具可以给攻击者提供一个OWA查询接口，并访问目标用户的邮箱以及通讯录。

### 工具开发背景

本工具于Defcon
26发布，关于该工具的详细视频以及演示内容可以从这个DEMO中获取：【[DEMO传送门](https://blog.quickbreach.io/one-click-to-owa/)】。

## 工具安装

    
    
    pip install -r requirements.txt

## 工具使用

简单，暴力：

    
    
    ./exchangeRelayx.py -t https://mail.quickbreach.com

## 功能介绍

1.访问EWS服务器的原始XML数据；

2.向目标用户的邮件添加重定向规则，以实现后门安插；

3.下载目标用户邮箱中收件箱邮件和发件箱邮件的所有附件；

4.搜索目标账户的全局邮件通讯录；

5.以目标用户的身份发送带有附件的电子邮件，邮件不会存储在目标邮箱的发件箱发件箱中。

## 程序架构

本项目分为owaServer、中继服务器和HTTP攻击客户端（exchangePlugin），每一个组件都会建立不同的中继链接。

### owaServer

owaServer是一个基于Flask框架的Web服务器，默认监听<http://127.0.0.1:8000>。这个Web服务器托管静态HTML文件index.html、OWA.html和ComposeEmail.html，owaServer终端会通过JSON请求来加载和调用这些文件。当客户端向owaServer发送请求时，owaServer会生成相应的EWS调用并将其写入共享内存目录中，然后把请求发送至邮件交换服务器。最后，当owaServer获取到请求之后，会对数据进行解析并返回处理结果。

### 中继服务器

这个中继服务器基于标准的Impacket HTTP和SMB实现，它们将为每一个新的中继链接创建新的exchangePlugin实例。

### exchangePlugin

exchangePlugin实际上是一个专门发送/接收EWS服务器请求/响应的HTTP客户端。所有的exchangePlugin在初始化时都会被发送到相同的共享内存目录中，它们会使用这个目录进行内部进程通信。

## 备注

该工具在Server 2012 R2系统的Exchange 2013上测试过，所以个人认为该工具应该也适用于其他环境。

***参考来源：[ExchangeRelayX](https://github.com/quickbreach/ExchangeRelayX)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

