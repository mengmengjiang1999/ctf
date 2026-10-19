Win10（攻击机）IP:192.168.100.115

Win server 2008R2（边缘机）IP1:192.168.100.108 IP2:192.168.233.129

Win server 2012（内网机）IP1:192.168.233.140 IP2:192.168.50.139

Win 7（内网机）IP:192.168.50.140

在内网渗透中，通过frp单层代理拿到了深层的服务器，但还是有服务器不能访问时可以使用多层代理。

在win10中使用mstsc测试是否能够直接连接50.140

无法直接连接

![](https://image.3001.net/images/20211006/1633502091_615d438b77c56f25209f0.png!small)

在攻击机开启frp服务端

![](https://image.3001.net/images/20211006/1633502212_615d4404bbcf2aff68b5a.png!small)

![](https://image.3001.net/images/20211006/1633502294_615d445602b664b008d43.png!small)

在已经被拿下的服务器win 7设置frp服务端和客户端来进行端口转发，将远程的5555端口转换成本地的5555端口

启动客户端与攻击机连接

![](https://image.3001.net/images/20211006/1633502340_615d448466048c03f65e5.png!small)

攻击机服务端成功收到![](https://image.3001.net/images/20211006/1633502374_615d44a63ccf5f6a3c495.png!small)

启动客户端与win server 2012连接

![](https://image.3001.net/images/20211006/1633502396_615d44bcb1d4ad9fc33f6.png!small)

![](https://image.3001.net/images/20211006/1633502435_615d44e32b1b9ed8308ae.png!small)

在win server
2012上启用frp客户端这里进行socks隧道连接![](https://image.3001.net/images/20211006/1633502476_615d450cbd6f29615a350.png!small)

Win server 2008收到win server
2012的请求![](https://image.3001.net/images/20211006/1633502504_615d45287c08c3beafb85.png!small)

至此隧道就搭建完成。

在攻击机上使用proxifier工具进行代理

对代理进行连通信测试![](https://image.3001.net/images/20211006/1633502531_615d4543a33cb5c32c795.png!small)

再次使用mstsc进行访问

成功。

![](https://image.3001.net/images/20211006/1633502556_615d455ce3acc600f545a.png!small)

参考：https://kdfans.vip/2021/09/10/%E5%86%85%E7%BD%91%E7%A9%BF%E9%80%8F/

