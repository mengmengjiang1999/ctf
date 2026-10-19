利用window7攻击window2003

1、在Windows 7安装IIS服务，访问www.baidu.com或其他任意站点，保存首页文件至本地wwwroot文件夹中；

![](https://image.3001.net/images/20210422/1619101388_608186cc7271646b86932.png!small)

![](https://image.3001.net/images/20210422/1619101451_6081870b9710c3999abcd.png!small)

2、在Windows 7使用“Cain & Abel”软件对Windows server 2003实施DNS欺骗攻击；

![](https://image.3001.net/images/20210422/1619101495_60818737b220c5a71b1e3.png!small)

![](https://image.3001.net/images/20210422/1619101509_60818745e945b350e8a4d.png!small)

点黄色按钮开启毒化![](https://image.3001.net/images/20210422/1619101522_60818752ce2a9570cbaa7.png!small)

输入欺骗域名和window7的ip地址：![](https://image.3001.net/images/20210422/1619101533_6081875dd1e3abb507d8f.png!small)

3、在Windows Server 2003使用Arp命令查看网关MAC地址变化情况；

![](https://image.3001.net/images/20210422/1619101576_60818788328b1953934e1.png!small)

可以看到欺骗成功!

4、在Windows Server 2003使用浏览器访问“www.baidu.com”，查看欺骗结果。

![](https://image.3001.net/images/20210422/1619101619_608187b33e9361c1be044.png!small)

保存百度首页为(index.htm)

![](https://image.3001.net/images/20210422/1619101632_608187c0eeb33712866e9.png!small)

![](https://image.3001.net/images/20210422/1619101666_608187e2c945996cd7583.png!small)

把它移动到最上面（优先级最高）

![](https://image.3001.net/images/20210422/1619101723_6081881b74f23fc3cf49d.png!small)

![](https://image.3001.net/images/20210422/1619101744_6081883081d02147c34f2.png!small)DNS欺骗成功！

