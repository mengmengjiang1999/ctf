# Earthworm的使用（一级代理）

ew
全称是EarchWorm，是一套轻量便携且功能强大的网络穿透工具，基于标准C开发，具有socks5代理、端口转发和端口映射三大功能，可在复杂网络环境下完成网络穿透，且支持全平台(Windows/Linux/Mac)。该工具能够以“正向”、“反向”、“多级级联”等方式打通一条网络隧道，直达网络深处，用蚯蚓独有的手段突破网络限制，给防火墙松土。

![图片.png](https://image.3001.net/images/20230821/1692581606_64e2bee6d2132b77be0c6.png!small)

该工具已经停止维护和下载：`http://rootkiter.com/EarthWorm/`

![图片.png](https://image.3001.net/images/20230821/1692581623_64e2bef7b5f91cd282f67.png!small)

工具下载地址：`https://github.com/idlefire/ew`

![图片.png](https://image.3001.net/images/20230821/1692581639_64e2bf07c3c0029040bed.png!small)

Earthworm有六种模式，分别是：

  * ssocksd

  * rcsocks

  * rssocks

  * lcx_slave

  * lcx_listen

  * lcx_tran

ssocksd是用于普通网络环境下的正向连接，rcsocks 和 rssocks 用于反向连接，而lcx_slave 、lcx_listen 和
lcx_tran 用于复杂网络环境的多级连接

常用参数：

  * -l：指定要监听的本地端口

  * -d：指定要反弹到的机器 ip

  * -e：指定要反弹到的机器端口

  * -f：指定要主动连接的机器 ip

  * -g：指定要主动连接的机器端口

  * -t：指定超时时长,默认为 1000

## 实验环境

现有实验环境如下所示：

身份| IP地址| 系统  
---|---|---  
黑客（本机）| 192.168.0.112| Win11  
Web服务器| 192.168.41.133| Win10  
  
现在我们可以使用黑客电脑直接连接Web服务器，却不能使用黑客电脑直接连接公司内网机器，但是Web服务器可以连接内网机器，现在我们需要在Web服务器上做代理，来让黑客电脑通过代理可以访问公司内网机器

### （一级代理）正向代理

实验拓扑图如下：

正向意思就是攻击者可以访问目标的机器，也就意味着目标的机器在公网，如下拓扑：

![图片.png](https://image.3001.net/images/20230821/1692581664_64e2bf20878d8343bd4bb.png!small)

正向连接就是黑客主动连接web服务器，在web开启监听

现在模拟一个场景，黑客可以通过互联网连接Web服务器，但不能直接连接内网，前期我们已经通过各种漏洞拿下了目标公司的Web服务器的控制权限，现在我们需要在Web服务器上上传一个Earthworm工具，然后我们黑客就可以通过Web服务器连接目标公司的内网，现在我们在Web服务器执行如下命令

    
    
    ew.exe -s ssocksd -l 1080
    

![图片.png](https://image.3001.net/images/20230821/1692581676_64e2bf2cbe3393b4e7c11.png!small)

然后我们使用黑客的电脑，使用froxyifile或者proxychains等工具进行连接

现在我们在黑客电脑上使用proxyifile进行连接

![图片.png](https://image.3001.net/images/20230821/1692581689_64e2bf39d1eeeddef3b32.png!small)

在我们测试的时候，在Web服务器上的ew工具显示此时已经有了连接的记录

![图片.png](https://image.3001.net/images/20230821/1692581701_64e2bf4540cb020d6efc6.png!small)

然后我们配置代理规则,选中我们刚刚添加的代理服务器的地址，点击确定

![图片.png](https://image.3001.net/images/20230821/1692581713_64e2bf51310dd83f21e7f.png!small)现在我们所有的流量就通过Web服务器代理了，就可以访问公司内部的网络了。这是黑客主机是Windows端的操作，那么在Linux端是如何操作的呢？

现有实验环境如下所示：

身份| IP地址| 系统  
---|---|---  
黑客（本机）| 192.168.41.132| kali  
Web服务器| 192.168.41.133| Win10  
  
在之前的文章里面我们有提到过，在Windows端我们可以使用proxyfile工具走全局代理，而在Linux系统中我们可以使用proxychains工具走全局代理，该工具在Kali系统中自带，默认配置文件的路径为`/etc/proxychains4.conf`

实验背景和之前上述的一样，现在我们在Web服务器上传ew工具

![图片.png](https://image.3001.net/images/20230821/1692581737_64e2bf69622415f3a21a7.png!small)

然后再Web服务器上执行以下的命令

    
    
    ew.exe -s ssocksd -l 1080
    

![图片.png](https://image.3001.net/images/20230821/1692581750_64e2bf76aea387af72b2a.png!small)

然后我们在kali系统修改 /etc/proxychains4.conf 文件

    
    
    vim /etc/proxychains4.conf
    

翻到最下面，将里面的内容修改

![图片.png](https://image.3001.net/images/20230821/1692581764_64e2bf84b4cf245826e63.png!small)

修改成代理服务器的地址和端口，在本实验中也就是修改成Web服务器的地址和刚刚ew工具开启的1080端口，结果如下，（现在socks4协议已经被弃用了，所以只支持socks5协议）:

![图片.png](https://image.3001.net/images/20230821/1692581780_64e2bf944bddb701be617.png!small)

然后我们保存退出，执行以下的命令

    
    
    proxychains curl baidu.com
    

![图片.png](https://image.3001.net/images/20230821/1692581792_64e2bfa03d712a78a3705.png!small)

很明显，这里我们的kali机器流量通过了Web服务器成功访问了百度，我们再来看一下Web服务器ew工具的回显也可以发现本次访问百度的流量

![图片.png](https://image.3001.net/images/20230821/1692581806_64e2bfaed09765560282f.png!small)

现在我们可以在kali使用proxychains命令去访问公司内部的网络了

### （一级代理）反向代理

反向连接适合于目标没有公网 IP 的情况，这时就需要一台公网 vps 了，这里就直接以内网地址作为演示了

实验拓扑图如下：

![图片.png](https://image.3001.net/images/20230821/1692581825_64e2bfc1e5b3b9632e831.png!small)

