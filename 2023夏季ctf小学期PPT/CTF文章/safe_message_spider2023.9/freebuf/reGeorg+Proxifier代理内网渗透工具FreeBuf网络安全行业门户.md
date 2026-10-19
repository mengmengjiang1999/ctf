# **0x00介绍**

reGeorg是reDuh的继承者，利用了会话层的socks5协议，结合Proxifier使用效率更高，Proxifier是一款功能非常强大的socks5客户端，可以让不支持通过代理服务器工作的网络程序能通过HTTPS或SOCKS代理或代理链。该文件下支持php，asp，jsp，aspx

![1598690052.png!small](https://image.3001.net/images/20200829/1598690052.png!small)

 **0x01适用场景**

例如有一台主机运行了web服务IP映射到公网任何人都可以任意访问，还有一台主机是内网中的主机外部访问不到。假设在公网的web主机已经上传了webshell，但无法反弹shell，无法直接将内网主机通过端口映射到外网主机。

reGeorg这时就起作用了，通过上传reGeorg文件在web服务运行，使得攻击者发出的请求以及目标机器的响应经web服务的http转发，达到攻击者可以和内网主机进行通信的效果。

![1598690065.png!small](https://image.3001.net/images/20200829/1598690065.png!small)

 **0x02使用方法**

通过reGeorg+Proxifier实现在本地远程登录内网PC主机

reGeorg下载地址：

https://github.com/sensepost/reGeorg

1.下载上传tunnel到web服务器，web服务器使用什么编程语言，就上传什么语言的tunnel脚本，这里有PHP|JSP|ASPX|ASHX等语言可以选择，这里选择PHP文件上传

![1598690082.png!small](https://image.3001.net/images/20200829/1598690082.png!small)

2.访问tunnel.nosocket.php这个文件当出现Georg says, 'All seems fine'表示脚本运行正常

![1598690125.png!small](https://image.3001.net/images/20200829/1598690125.png!small)

3.在攻击机上使用python2运行reGeorgSocksProxy.py脚本配置代理，当程序卡在“Georg says, 'All seems
fine'”表示正常运行

python reGeorgSocksProxy.py -u http://192.168.10.211/tunnel.nosocket.php -p
444

![1598690148.png!small](https://image.3001.net/images/20200829/1598690148.png!small)

4.使用proxifier配置代理，运行proxifier，点击profile,然后点击proxy Server..,选择Add添加一个新代理

下载地址：https://pc.qq.com/detail/13/detail_10593.html

![1598690173.png!small](https://image.3001.net/images/20200829/1598690173.png!small)

![1598690183.png!small](https://image.3001.net/images/20200829/1598690183.png!small)

5\. 点击profile,点击Proxification Rules设置代理规则，应用程序选择python，目标主机和目标端口都任意,
动作这里会有三个状态，Direct（放行），Block（阻塞），Proxy（代理）。这里选择Direct（放行）

![1598690217.png!small](https://image.3001.net/images/20200829/1598690217.png!small)

6.配置完成后右击“mstsc.exe”，选择“proxifier”-》proxy socks5 127.0.0.1进行远程连接

![1598690250.png!small](https://image.3001.net/images/20200829/1598690250.png!small)

7.输入内网IP通过用户名密码成功登录服务器。

![1598690264.png!small](https://image.3001.net/images/20200829/1598690264.png!small)

![1598690283.png!small](https://image.3001.net/images/20200829/1598690283.png!small)

 **0x03** **reGeorg+proxychains代理Linux内网**

1\. 下载安装reGeorg

git clone https://github.com/sensepost/reGeorg.git

![1598690307.png!small](https://image.3001.net/images/20200829/1598690307.png!small)

2\. 和windows一样上传对应语言脚本tunnel文件，在linux上运行reGeorgSocksProxy.py文件

python reGeorgSocksProxy.py -u http://192.168.10.211/tunnel.nosocket.php -p
4561 //端口随便指定，但是不能冲突

![1598690315.png!small](https://image.3001.net/images/20200829/1598690315.png!small)

3.使用vim配置proxychains //linux代理工具

vim /etc/proxychains.conf

![1598690351.png!small](https://image.3001.net/images/20200829/1598690351.png!small)

4.使用proxychains代理远程登录windows

proxychains rdesktop -g 1440x900 172.17.17.7:3389 //-g后面代表要使用的分辨率

![1598690363.png!small](https://image.3001.net/images/20200829/1598690363.png!small)

