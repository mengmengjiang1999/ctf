## 靶机概述

Kali地址：192.168.16.54

靶机地址：192.168.16.98

目标：获取根外壳程序ie（root @ localhost ：〜＃），然后获取/ root下的标志。

难度：中等

## 提权过程

1、扫描存活主机ip：arp-scan 192.168.16.0/24

![](https://image.3001.net/images/20201010/1602320235_5f81776b01cf79fe3b9ff.png!small)2、扫描主机开放端口：nmap
-p 1-65535 192.168.16.98

![](https://image.3001.net/images/20201010/1602320281_5f817799c42abae082371.png!small)

3、访问80端口：网站就一个土豆图片，没有任何交互点。

![](https://image.3001.net/images/20201010/1602320322_5f8177c270a13959612ce.png!small)

4、使用目录扫描发现了info.php文件。

![](https://image.3001.net/images/20201010/1602320467_5f8178532500d31b14148.png!small)5、之前端口扫描发现开放了7120端口，百度后也没有对此端口的描述，猜测可能是修改后的ssh端口，尝试登录后果不其然。

![](https://image.3001.net/images/20201010/1602320589_5f8178cdc7758ac0a0b19.png!small)6、使用hydra进行ssh爆破成功。用户名：potato
密码：letmein

![](https://image.3001.net/images/20201010/1602320688_5f8179308a95123540982.png!small)7、登录成功后查看系统内核版本为Ubuntu
3.13.0，这是一个较老版本，存在提权漏洞。直接使用exp。

![](https://image.3001.net/images/20201010/1602320922_5f817a1ad4d1470c4fe66.png!small)8、搜索Ubuntu
3.13.0利用exp：searchsploit Ubuntu 3.13.0

![](https://image.3001.net/images/20201010/1602321056_5f817aa041beed6516568.png!small)9、使用Xftp将37292.c文件上传至tmp目录下

![](https://image.3001.net/images/20201010/1602321107_5f817ad3710e6ac2b1169.png!small)

8、执行exp提权到root成功，找到Flag！

![](https://image.3001.net/images/20201010/1602321221_5f817b455789041e3b1b1.png!small)

