# 下载地址

    
    
    https://download.vulnhub.com/botchallenges/LoBOTomy.zip  
    

#  **实战演练**

使用netdiscover命令查找靶机的IP。

![image.png](https://image.3001.net/images/20190820/1566307598_5d5bf50e0fe4e.png)  

使用nmap查看靶机开放的端口

![image.png](https://image.3001.net/images/20190820/1566307605_5d5bf515f40a8.png)  

打开浏览器

![image.png](https://image.3001.net/images/20190820/1566307720_5d5bf588ac27b.png)爆破WEB目录，找到了一个M目录

![image.png](https://image.3001.net/images/20190820/1566308795_5d5bf9bb3f280.png)进入到这个页面，使用madness看看存不存在弱口令

好，成功登录进去

![image.png](https://image.3001.net/images/20190820/1566308855_5d5bf9f717a74.png)查了一下资料，原来这个系统存在SQL注入漏洞，<https://www.exploit-db.com/exploits/33655>

![image.png](https://image.3001.net/images/20190820/1566309138_5d5bfb1225acb.png)SQLMAP

![image.png](https://image.3001.net/images/20190820/1566309201_5d5bfb51ac848.png)查看root连接密码，password

![image.png](https://image.3001.net/images/20190820/1566309406_5d5bfc1e47c4f.png)试试用这个密码能不能连接ssh

成功连接

![image.png](https://image.3001.net/images/20190820/1566309457_5d5bfc516fca6.png)  

  

番外，xss漏洞测试，<https://www.exploit-db.com/exploits/33654>，填上信息就行

![image.png](https://image.3001.net/images/20190820/1566310180_5d5bff24b600d.png)

![image.png](https://image.3001.net/images/20190820/1566310209_5d5bff4172a38.png)

