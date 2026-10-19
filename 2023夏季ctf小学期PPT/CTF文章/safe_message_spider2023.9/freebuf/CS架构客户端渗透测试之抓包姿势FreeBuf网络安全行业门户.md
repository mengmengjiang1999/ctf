## 背景

由于工作需要，最近一直接触c/s架构的安全性测试，作为初入职场的小白，在这里给大家分享一下关于c/s架构渗透测试的抓包心得，哪里有缺漏妄各位大佬们指正。

 **什么是C/S架构？**

![图片.png](https://image.3001.net/images/20210207/1612667066_601f58bac7dce5b2dfabc.png!small)
C/S（Client-Server），即服务器/客户机结构。C/S结构通常采取两层结构。

客户机负责完成与用户的交互任务，通过局域网与服务器相连，接受用户的请求，并通过网络向服务器提出请求，对数据库进行操作。

服务器则负责数据的管理，接受客户机的请求，将数据提交给客户机，客户机将数据进行计算并将结果呈现给用户。客户机负责完成与用户的交互任务，通过局域网与服务器相连，接受用户的请求，并通过网络向服务器提出请求，对数据库进行操作。

C/S结构是一种软件系统体系结构，也是生活中很常见的。比如我们手机或电脑中安装的微信、QQ、腾讯视频、酷狗音乐等应用程序就是C/S结构。

好，概念介绍到这里，下面开始我们的正题——C/S测试之抓包姿势。

### C/S架构测试之抓包技巧

在项目测试过程中，最初遇到C/S客户端抓包失败的情况，导致测试无法正常进行，后来才知道其相关原因。

 **原因分析：**

> 1、b/s使用的协议如：http、https ； c/s使用的协议如：TCP、HTTP(S)、TDS等。
>
> 2、像B/S测试常用的web抓包代理工具：burpsuite、fiddler等，大多支持http协议、https协议。对于其他协议不好抓取。
>
> 3、大多数C/S架构客户端没有代理配置功能,而导致代理工具无法生效。

 **抓包方法**

###### 情况一 ：客户端走的是http协议或https协议，但无代理功能。

可以使用burpsuite或fiddler代理工具结合proxifer实现对客户端的数据抓包。

proxifier是一款功能非常强大的socks5客户端，可以让不支持通过代理服务器工作的网络程序能通过HTTPS或SOCKS代理或代理链。

以下以burpsuite+proxifier抓包，进行说明：

**第一步：**打开burpsuite，并对burpsuite进行配置。  
![图片.png](https://image.3001.net/images/20210208/1612750028_60209ccc4628e11844136.png!small)正常的话，porxy模块下，拦截功能是默认打开的。o地址也是默认127.0.0.1:8080启用的。  
![图片.png](https://image.3001.net/images/20210208/1612750107_60209d1be938031c0878f.png!small)options子模块，配置的代理地址也是默认127.0.0.1:8080启用的。  
![图片.png](https://image.3001.net/images/20210208/1612750292_60209dd45d560b9c0d424.png!small)**第二步:**打开proxifier  
![图片.png](https://image.3001.net/images/20210208/1612750500_60209ea4bc251588750a7.png!small)对porxifier先进行代理服务器配置：打开配置文件模块-代理服务器，添加代理服务器  
![图片.png](https://image.3001.net/images/20210208/1612750751_60209f9f108353d0069d8.png!small)![图片.png](https://image.3001.net/images/20210208/1612750707_60209f73035844d7a4264.png!small)配置好后，可点击检查按钮，验证是否与burpsuite连接成功。  
![图片.png](https://image.3001.net/images/20210208/1612751022_6020a0ae51f6519027b79.png!small)对proxifier进行代理规则配置：打开配置文件模块-代理规则，添加新规则，应用程序填写需要代理的客户端的文件名，这里以微信客户端为例，如：WeChat.exe。目标主机、目标端口默认，动作选择新加入的代理地址：127.0.0.1，配置好后点击确认。  
![图片.png](https://image.3001.net/images/20210208/1612751199_6020a15fed0576e97d620.png!small)打开微信，随机打开页面，burp成功拦截请求。  
![图片.png](https://image.3001.net/images/20210208/1612752202_6020a54a2e9d134916631.png!small)

###### 情况二：客户端走的是非http(s)协议，并无代理配置功能

这里推荐使用wireshark，wireshark是非常流行的网络封包分析软件，功能十分强大。可以截取各种网络封包，显示网络封包的详细信息。包括
HTTP、TCP、UDP 等网络协议包。  
![图片.png](https://image.3001.net/images/20210208/1612752722_6020a7527efecd780990b.png!small)在这里可通过在过滤器中输入过滤规则，实现快速定位想要查询的数据流量。  
![图片.png](https://image.3001.net/images/20210208/1612752817_6020a7b167e0d0b6a8af3.png!small)![图片.png](https://image.3001.net/images/20210208/1612754335_6020ad9f268e68d622baa.png!small)  
![图片.png](https://image.3001.net/images/20210208/1612754360_6020adb8c98ce3f5f640a.png!small)![图片.png](https://image.3001.net/images/20210208/1612754401_6020ade12707efbf9749e.png!small)  
![图片.png](https://image.3001.net/images/20210208/1612754419_6020adf3e2810b8c445e2.png!small)数据分析：可在封包列表中选定其中想要分析的封包数据，在封包详细信息中或右击数据选择追踪流，查看其请求响应信息。  
![图片.png](https://image.3001.net/images/20210208/1612754589_6020ae9d5f1ff53fb9ef5.png!small)

###### 情况三：若是tcp流量

推荐使用Echo Mirage工具，其工具专门拦截tcp流量。  
![图片.png](https://image.3001.net/images/20210208/1612754915_6020afe33c7026fe23c0c.png!small)单击rules查看规则，默认有了两条规则，可以用来拦截所有的出入流量  
![图片.png](https://image.3001.net/images/20210208/1612755016_6020b0485acd367cd90e9.png!small)![图片.png](https://image.3001.net/images/20210208/1612755034_6020b05a8cd489fb5e6e3.png!small)

