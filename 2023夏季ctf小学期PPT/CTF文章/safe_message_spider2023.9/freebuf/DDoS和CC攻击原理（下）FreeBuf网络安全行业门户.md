## 0、前言

本主题研究DDoS和CC的实现原理以及其具体的实现方法，并对如何检测和防护进行说明。  
文章一共分为（上）（中）（下）三篇，  
（上）主要描述DDoS基本原理和实现攻击的基础和思路；  
（中）主要列举可用于DDoS和CC的方法；  
（下）主要对攻击原理进行总结并提出目前主流的防护机制。

## 1、攻击基础

根据前两篇文章，我们知道了DDoS和CC能够实现攻击的技术基础是：源、目的ip地址伪造，数据包参数伪造。  
![image.png](https://image.3001.net/images/20211218/1639804216_61bd6d388475947fa76a7.png!small)  
下面，我们总结一下具体是什么技术使得DDoS和CC能够成为现实。

### 1.1 小包技术

![image.png](https://image.3001.net/images/20211218/1639804352_61bd6dc0835c96eda4849.png!small)

### 1.2 大量的公共服务器产生反射流量

![image.png](https://image.3001.net/images/20211218/1639804375_61bd6dd7af2bcc2f400c3.png!small)

### 1.3 僵尸网络（botnet）

目前主流的僵尸网络包括：IoT设备僵尸网络、挖矿僵尸网络等  
![image.png](https://image.3001.net/images/20211218/1639804631_61bd6ed70b515b9dea0aa.png!small)

![image.png](https://image.3001.net/images/20211218/1639804647_61bd6ee709812688308b5.png!small)

### 1.4 免费、付费发包工具、脚本

![image.png](https://image.3001.net/images/20211218/1639804664_61bd6ef8539b1c3174f18.png!small)

### 1.5 在线攻击平台

![image.png](https://image.3001.net/images/20211218/1639804683_61bd6f0b63b4778d2f2d5.png!small)

### 1.6 目标扫描--域名、IP、端口、服务

![image.png](https://image.3001.net/images/20211218/1639804699_61bd6f1bc499e9f27041b.png!small)

### 1.7 空间搜索引擎

![image.png](https://image.3001.net/images/20211218/1639804726_61bd6f367a66436b5de2f.png!small)  
以下为一些常用的搜索工具：

    
    
    https://fofa.so/
    
    
    
    https://www.zoomeye.org/
    
    
    
    https://censys.io
    
    
    
    https://www.shodan.io
    

## 2、攻击特点

### 2.1 攻击特点的总结

![image.png](https://image.3001.net/images/20211218/1639804742_61bd6f46d1c855d32cf4a.png!small)

## 3、受攻击时服务器参数情况

### 3.1 设备发现攻击时的状态图

![image.png](https://image.3001.net/images/20211218/1639804755_61bd6f534917f86b6c8aa.png!small)

1、接收的数据包类型（syn、ack、frag、icmp、http等）  
2、包速pps  
3、流量bps  
4、连接数（并发、新建）  
5、应用请求数qps  
6、丢包重传  
7、错误日志

> 说明：攻击发生时上述参数会有一个或者多个明显超过正常值。

## 4、攻击抓包示例

以下是一些来自实际攻击案例中的数据包样例，（中）篇中已描述过各种攻击手法，这里不再对每个数据包做详细讲解，感兴趣的可以私聊沟通交流。

### 4.1 syn攻击

![image.png](https://image.3001.net/images/20211218/1639804793_61bd6f7952e7ba28719f6.png!small)

### 4.2 ack攻击

![image.png](https://image.3001.net/images/20211218/1639804854_61bd6fb6ce49fe0729fef.png!small)

### 4.3 frag攻击

![image.png](https://image.3001.net/images/20211218/1639805008_61bd7050dd2f9dce0158d.png!small)

### 4.4 NTP反射攻击

![image.png](https://image.3001.net/images/20211218/1639805048_61bd7078243c8ab9b8b14.png!small)

### 4.5 3389反射攻击

![image.png](https://image.3001.net/images/20211218/1639805069_61bd708db4365b72c4352.png!small)

### 4.6 cc攻击

![image.png](https://image.3001.net/images/20211218/1639805087_61bd709f0d54a325984f5.png!small)

![image.png](https://image.3001.net/images/20211218/1639805179_61bd70fb5f13aaebd9f43.png!small)

![image.png](https://image.3001.net/images/20211218/1639805239_61bd713752d1ecd30035f.png!small)

## 5、解决方案

目前对其解决方案主要分两大类，一类是流量清洗对抗还有一类是IP分层对抗。  
IP分层主要为对不用地域不同级别用户进行IP分配，以实现攻击者攻击的IP地址不会影响到有价值的用户IP，而流量清洗者是使用清洗设备对攻击流量进行阻拦。  
通过单机串联部署模式或分层旁路部署模式将攻击流量进行分析、清洗和回馈操作。以达到保护用户网络资源、 计算资源、应用资源的目的。  
![image.png](https://image.3001.net/images/20211218/1639805326_61bd718ee49ef7864ceed.png!small)

串联部署：该部署方式通常用在较小的业务流量、部署在业务系统前针对其直接进行防护的场景。  
![image.png](https://image.3001.net/images/20211218/1639805345_61bd71a18a596c44c36ba.png!small)

旁路清洗部署  
![image.png](https://image.3001.net/images/20211218/1639805366_61bd71b6ea0d0f6a72f13.png!small)

通过对高性能DDOS设备进行集群，防御高并发量的DDOS攻击，处理峰值能够达到1T以上，并通过云统一管理平台进行集中管理和策略下放，实现多点部署，统一管控，集中防护的作用。  
![image.png](https://image.3001.net/images/20211218/1639805385_61bd71c9b881c0523a242.png!small)

通过NAT结合负载均衡的技术，以实现有效隐藏用户计算资源、网络资源及应用资源的目的，同时为用户提供云DDOS增值服务。  
![image.png](https://image.3001.net/images/20211218/1639805402_61bd71da2463edd8bf2c7.png!small)

分布式  
![image.png](https://image.3001.net/images/20211218/1639805443_61bd72037d136c2debe03.png!small)

## 6、防护机制

以下是对抗DDoS攻击的一个常规防护技术框架，一般来说，也是一个专业抗DDoS设备的常规功能。

### 6.1 防护框架

![image.png](https://image.3001.net/images/20211218/1639805515_61bd724bb6801224d21c3.png!small)

![image.png](https://image.3001.net/images/20211218/1639805536_61bd7260be75f4d5d42d9.png!small)

### 6.2 逆向验证DDoS防护

![image.png](https://image.3001.net/images/20211218/1639805562_61bd727a87bd68ab11dcc.png!small)

### 6.3 缺省DDoS防护（基本参数）

![image.png](https://image.3001.net/images/20211218/1639805590_61bd72964312e32df5f0e.png!small)

### 6.4 高级防护参数

![image.png](https://image.3001.net/images/20211218/1639805626_61bd72ba454b6ba15ebc8.png!small)

### 6.5 异常发现和告警能力

![image.png](https://image.3001.net/images/20211218/1639805644_61bd72cce369bacf204ae.png!small)

>
> 声明：文章内容均来自互联网，并且仅是对攻击原理进行理论性描述，未具体提供任何可用于直接进行攻击实现的手段，目的是为了进行学习交流，请读者们洁身自好，不要尝试利用，以免误入歧途。

