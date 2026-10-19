![](https://image.3001.net/images/20201105/1604547585_5fa3740134ec9e81acec8.png!small)

## Browsertunnel

Browsertunnel这款工具可以帮助广大研究人员利用DNS协议来从目标用户的浏览器中提取各种数据。该工具主要基于dns-prefetch实现其功能，而dns-prefetch这种功能旨在通过在后台为指定域执行DNS查找来减少网站的感知延迟。DNS流量实际上并不会出现在浏览器的调式工具中，也不会被页面的内容安全策略（CSP）屏蔽，而且通常不会被企业防火墙或代理检测到，因此它是在首先情况下进行数据窃取的最为理想的媒介。

实际上，这是一种很古老的技术了。DNS信道本身可以追溯到九十年代，而研究人员Patrick Vananti在2016年还专门写过一篇关于dns-prefetch的[ _文章_](https://blog.compass-security.com/2016/10/bypassing-content-security-policy-with-dns-prefetching/)。但是到目前为止，Browsertunnel是第一款完全开源，并且支持客户端和服务器设备交互使用的工具。因为dns-prefetch不会将任何数据返回给客户端JavaScript，因此通过Browsertunnel实现的传输数据只能是单项发送的。另外，有些浏览器默认禁用了dns-prefetch功能，那么在这种场景下，Browsertunnel就无法正常工作了。

![](https://image.3001.net/images/20201105/1604547603_5fa3741394be06076bf80.png!small)

## 工具组成

  * 一个服务器端，服务器端似乎用Golang开发，作为一台授权DNS服务器来使用，可以收集并解码Browsertunnel发送的消息；
  * 一个小型JavaScript库，可以在html/目录中找到，能够解码并发送来自于客户端的消息；

## 工作机制

Browsertunnel可以将字符串编码进一个子域名中，并通过DNS来发送任意字符串。当目标用户的浏览器尝试去对域名进行递归解析时，这些信息便会被转发至Browsertunnel的服务器端：

![](https://image.3001.net/images/20201105/1604547623_5fa37427053f1899abe5f.png!small)

如果需要传输的数据量过大（253个字节），那么一个域名肯定是不够的，那么这些信息将会被分割成多个部分，然后再由服务器端负责进行重新拼装和解码：

![](https://image.3001.net/images/20201105/1604547640_5fa37438a4bee3994126b.png!small)

## 工具安装和使用

首先，我们需要设置DNS记录来代表我们服务器的子域名。比如说，如果你的服务器IP地址为192.0.2.123，而你想要通过子域名t1.example.com来发送数据的话，那么你的DNS配置应该如下：

    
    
    t1 IN NS t1ns.example.com.
    
    t1ns IN A 192.0.2.123

在你的服务器端，使用go
get命令安装Browsertunnel。或者说，你也可以自行在设备上编译Browsertunnel项目，然后把代码拷贝到服务器端：

    
    
    go get github.com/veggiedefender/browsertunnel

接下来，使用browsertunnel命令运行Browsertunnel，指定你想要用来传输数据的子域名：

    
    
    browsertunnel t1.example.com

如需获取Browsertunnel的完整使用方式，可以使用-help参数：

    
    
    $ browsertunnel -help
    
    Usage of browsertunnel:
    
      -deletionInterval int
    
         seconds in between checks for expired messages (default 5)
    
      -expiration int
    
         seconds an incomplete message is retained before it is deleted (default 60)
    
      -maxMessageSize int
    
         maximum encoded size (in bytes) of a message (default 5000)
    
      -port int
    
         port to run on (default 53)

现在，你就可以开始测试你自己的DNS信道了。你可以使用我给大家提供的演示页面：【点我访问】。或者，大家也可以使用下列命令将该项目源码克隆至本地，然后在本地加载html/index.html来进行测试。如果一切正常的话，大家就可以看到服务器端输出的信息了。

    
    
    git clone https://github.com/veggiedefender/browsertunnel.git

## 真实场景下

对于真实场景下的Browsertunnel使用，大家可能还需要根据情况来对代码进行一些调整：

  * 将消息写入数据库，而不是直接打印输出；
  * 转换或重写客户端以支持更老版本的浏览器；
  * 根据我们的数据流量，调整域名的ID字段；
  * 对消息进行身份验证或加密以实现数据传输的保密性和防篡改，别忘了DNS是一个明文协议；

## 项目地址

Browsertunnel：【[
_GitHub传送门_](https://github.com/veggiedefender/browsertunnel)】

