Heartbleed heart出血漏洞（CVE-2014-0160）

 ** **目的：**** 检测目标系统是否存在CVE-2014-0160漏洞，利用该漏洞获取网页cookie值

 ** **目标系统（vulhub靶机）：****

 ** **1.**** 启动环境，进入路径为cd /home/vulhub/vulhub-master/openssl/heartbleed

2.搭建及运行漏洞环境 docker-compose build

docker-compose up -d

3.环境启动后，访问https://192.168.1.131即可查看到test页面

 **
**![](https://image.3001.net/images/20201202/1606877782_5fc70256255bf521ae37b.png!small)****

 ** **Kali渗透：****

  1. Kali开启msfconsole加载模块，拿到敏感数据（Cookie）

![](https://image.3001.net/images/20201202/1606877816_5fc7027860231adc32db3.png!small)

 **
**红笔标记处为获取到的cookie：![](https://image.3001.net/images/20201202/1606877852_5fc7029c6bf39a2997a03.png!small)****

对比正确：

![](https://image.3001.net/images/20201202/1606877900_5fc702cc3c83ae7818fbb.png!small)

