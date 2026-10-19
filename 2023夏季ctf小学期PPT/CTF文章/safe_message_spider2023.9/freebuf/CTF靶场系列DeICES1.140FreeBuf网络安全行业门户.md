# 下载地址

    
    
    http://hackingdojo.com/downloads/iso/De-ICE_S1.140.iso
    

# **实战演练**

使用netdiscover命令查找靶机的IP

![image.png](https://image.3001.net/images/20190805/1565013108_5d48347491f26.png)  

使用nmap查看靶机开放的端口

![image.png](https://image.3001.net/images/20190805/1565013302_5d483536ca62b.png)在浏览器打开

![image.png](https://image.3001.net/images/20190805/1565013429_5d4835b51f863.png)爆破一下web目录

![image.png](https://image.3001.net/images/20190805/1565013484_5d4835ec948d5.png)在首页查看源代码最下面有这几行代码，就是问你有没有见到一个论坛

    
    
    <font class="hidden">
    1. Have you seen our new cool forum yet?<br><br>
    2. Do not post sensitive information to public!<br><br>
    3. Different passwords for different services. What is that for?!<br><br>
    4. What if you are able to break out of your cell and manage to enter another one?<br><br>
    5. Some things change from time to time, others don't.<br><br>
    6. Sorry, no more hints available. There where more before we had to restore a very old backup. :(</font><br><br>
    </td></table><br><font class="credit">v0.1 # 2013 by para & reV for HackingDojo.com</font></center>
    </body></html>
    

![image.png](https://image.3001.net/images/20190805/1565013666_5d4836a28f856.png)查看其中一封登录攻击的邮件，找到一个信息

![image.png](https://image.3001.net/images/20190805/1565014006_5d4837f68207f.png)

使用这个账号登录

![image.png](https://image.3001.net/images/20190805/1565017420_5d48454cb0696.png)  
爆破HTTPS服务，找到了这个目录

![image.png](https://image.3001.net/images/20190805/1565016384_5d48414012d0f.png)![image.png](https://image.3001.net/images/20190805/1565016408_5d4841585f8d3.png)使用这个账号进去登录

  

![image.png](https://image.3001.net/images/20190805/1565017612_5d48460c01613.png)找到了MYSQL密码

![image.png](https://image.3001.net/images/20190805/1565017689_5d48465956b33.png)进入phpmyadmin

![image.png](https://image.3001.net/images/20190805/1565017799_5d4846c797c9c.png)论坛的用户账号和hash

用户名| hash值| 密码  
---|---|---  
RHedley  
| 31cbbdab9f5e1ebfa7d81267c258e29b5f9e171e6fcf7b1ba3  
| tum-ti-tum  
  
admin| fd339d53bf599d4ec7281ace84a902dc2ca16c7f63cbb16261  
| 解密失败  
SWillard  
| c19038340b8f5d1fc70e9bfbc3336f7bf1e0935da5ef13d4ef  
| 解密失败  
  
![image.png](https://image.3001.net/images/20190805/1565019730_5d484e523cdb8.png)用这个用户名登录FTP服务

![image.png](https://image.3001.net/images/20190805/1565019858_5d484ed26a94a.png)下载这个文件

![image.png](https://image.3001.net/images/20190805/1565019935_5d484f1f311ce.png)下载私钥

![image.png](https://image.3001.net/images/20190805/1565020070_5d484fa695111.png)使用私钥登录ssh

![image.png](https://image.3001.net/images/20190805/1565020174_5d48500edd0a3.png)使用另外一个账号

![image.png](https://image.3001.net/images/20190805/1565020286_5d48507ed9e0f.png)找到了一个脚本

![image.png](https://image.3001.net/images/20190805/1565020360_5d4850c8efde0.png)根据脚本要求来解密

    
    
    openssl aes-256-cbc -d -in backup_webhost_130111.tar.gz.enc -out /tmp/backup_webhost_130111.tar.gz -pass pass:wpaR9V616xrDTy98L7Uje2DDU5hWtWhs
    

![image.png](https://image.3001.net/images/20190805/1565020557_5d48518da03d2.png)shadow文件

    
    
    root:!:15773:0:99999:7:::
    daemon:*:15773:0:99999:7:::
    bin:*:15773:0:99999:7:::
    sys:*:15773:0:99999:7:::
    sync:*:15773:0:99999:7:::
    games:*:15773:0:99999:7:::
    man:*:15773:0:99999:7:::
    lp:*:15773:0:99999:7:::
    mail:*:15773:0:99999:7:::
    news:*:15773:0:99999:7:::
    uucp:*:15773:0:99999:7:::
    proxy:*:15773:0:99999:7:::
    www-data:*:15773:0:99999:7:::
    backup:*:15773:0:99999:7:::
    list:*:15773:0:99999:7:::
    irc:*:15773:0:99999:7:::
    gnats:*:15773:0:99999:7:::
    nobody:*:15773:0:99999:7:::
    libuuid:!:15773:0:99999:7:::
    syslog:*:15773:0:99999:7:::
    messagebus:*:15773:0:99999:7:::
    whoopsie:*:15773:0:99999:7:::
    landscape:*:15773:0:99999:7:::
    mysql:!:15773:0:99999:7:::
    sshd:*:15773:0:99999:7:::
    sraines:$6$4S0pqZzV$t91VbUY8ActvkS3717wllrv8ExZO/ZSHDIakHmPCvwzedKt2qDRh7509Zhk45QkKEMYPPwP7PInpp6WAJYwvk1:15773:0:99999:7:::
    mbrown:$6$DhcTFbl/$GcvUMLKvsybo4uXaS6Wx08rCdk6dPfYXASXzahAHlgy8A90PfwdoJXXyXZluw95aQeTGrjWF2zYPR0z2bX4p31:15773:0:99999:7:::
    rhedley:$6$PpzRSzPO$0MhuP.G1pCB3Wc1zAzFSTSnOnEeuJm5kbXUGmlAwH2Jz1bFJU/.ZPwsheyyt4hrtMvZ/k6wT38hXYZcWY2ELV/:15773:0:99999:7:::
      
    

使用john爆破，最后得到下列的密码

Mbrown  
| Mbrown  
  
---|---  
swillard  
| brillantissimo  
  
  
提权到root

![image.png](https://image.3001.net/images/20190806/1565021204_5d4854140d9a5.png)![image.png](https://image.3001.net/images/20190806/1565021232_5d485430b8e68.png)  

