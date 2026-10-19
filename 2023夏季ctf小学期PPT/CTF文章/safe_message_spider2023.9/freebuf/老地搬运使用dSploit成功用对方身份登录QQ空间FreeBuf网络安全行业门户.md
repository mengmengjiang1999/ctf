0x0 前言

WIFI 中使用 dsploit 来ARP攻击

dsploit 官方：<http://www.dsploit.net/> 点击右边的download 就可以下载了  
  
手机环境： 华为荣耀3C 安卓4.2.2 118B

条件：使用DSPLOIT 已经安装busybox pro 并都有ROOT权限

0x0 正片

DSPLOIT 主要还是可以针对无线网络环境使用 ，哪怕对方是有线或者台式机，只要与无线网络在同一网段内都可sniffer

dsploit 个人使用主要功能是以下三个

![image.png](https://image.3001.net/images/20181114/1542175160_5bebb9b82e439.png!small)  

password sniffer 字面意思就是嗅探 密码的 但是仅针对明文表单传输的密码 如果像银行有SSL 传输的加密的是无法截获的。

session hijacker 就是可以用对方的SESSION 值 用对方的身份去登陆网页 比如QQ空间 新浪微博 淘宝网（淘宝二次登陆还是需要密码的）等
目前测试新浪微博和QQ空间成功。

KILL connections 简单说 让对方所有的网络连接断开

点击MITM 就到上面这界面的了 本人演示的session hijacker 进入后点击start

如果出现QQ.COM 就可以选择并登陆

注意点击红色选框部分。。。后面不赘述

  

![image.png](https://image.3001.net/images/20181114/1542175259_5bebba1b2208b.png!small)  

![image.png](https://image.3001.net/images/20181114/1542175274_5bebba2abb70f.png!small)![image.png](https://image.3001.net/images/20181114/1542175297_5bebba41d893a.png!small)  

  

![image.png](https://image.3001.net/images/20181114/1542175374_5bebba8ea2da5.png!small)这样就达到了对方QQ空间  

  

其实 QQ空间 的域名 是 user.qzone.qq.com 就是qq.com 二三级域的问题。。

因为 dsploit 内置没有 获得session 输入路径的功能 很多找到根目录网站的时候都需要自己 点击寻找

其他网站也以此类推。 然后有什么肯德基 WIFI 等 公众场合请慎重使用。

目前已经发现使用dsploit 的问题 可能会导致目标主机 一定时间 无法访问网页 但是能上QQ 一般只要禁用 再启用网卡 多半能解决问题

这算是一个给妹子修电脑的理由。 看你皮不皮。。

