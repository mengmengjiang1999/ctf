靶机地址：<http://www.vulnhub.com/entry/five86-1,417/>

本文涉及知识点实操练习：[VulnHub渗透测试实战靶场Node 1.0
](https://www.hetianlab.com/expc.do?ec=ECIDdb58-4b9d-427b-b7b3-8382c7e0a7f5&pk_campaign=freebuf-wemedia)（Node 1.0 是一个难度为中等的Boot2root/CTF挑战，靶场环境最初由 HackTheBox
创建，实验目的是获取两个flag）

## 技术点

  * `opennetadmin v18.1.1`RCE

    * `searchsploit`

    * github搜索exp

  * 破解Linux中经过HASH加密的密码

    * `crunch`生成字典

    * `john`和`hashcat`破解密码

    * `hash-identifier`查看HASH类型

  * SSH免密登陆

    * 公钥复制为`authorized_keys`

  * Linux查看当前用户权限可读文件和可执行命令

    * 查看当前用户权限可读文件`find / -type f -user www-data`

    * 可执行命令`sudo -l`

## 目标发现

nmap -sP 参数使用 ping 扫描局域网主机，目的地址为 192.168.56.5

![发现目标地址](https://image.3001.net/images/20210118/1610954987_600538eb571231ee1797c.png!small)

nmap -sS -A -v 192.168.56.5 看一下详细的扫描结果 -sS 是半开放扫描，-A 是进行操作系统指纹和版本检测，-v 输出详细情况

![输出详细情况](https://image.3001.net/images/20210118/1610954989_600538ed2082a79ee432e.png!small)

可以看到开放了 22、80、10000 三个端口，并且 80 端口存在 `robots.txt`和路径 `/ona`

## 漏洞发现与利用

访问[http://192.168.56.5](http://192.168.56.5/)是个空白页面，然后去访问 /ona，可以看到是
`opennetadmin`的管理页面，并且版本是 `18.1.1`

![访问管理页面](https://image.3001.net/images/20210118/1610954990_600538ee4d006f05f8388.png!small)

![管理页面](https://image.3001.net/images/20210118/1610954991_600538ef90c3ad8c27749.png!small)

`v18.1.1`的`opennetadmin`是存在RCE漏洞的，在github找个exp打过去就可以，<https://github.com/amriunix/ona-rce>

![在github找个exp打过去](https://image.3001.net/images/20210118/1610954992_600538f0acb283958ebda.png!small)

或者是使用 `searchsploit`，不过这里有个坑点，就是要对这个bash脚本进行转换格式，否则会报错，使用`dos2unix
47691.sh`这个命令，而且这里的shell不能转成TTY

![使用
searchsploit](https://image.3001.net/images/20210118/1610954993_600538f1b7a4365364d61.png!small)

![转换格式](https://image.3001.net/images/20210118/1610954994_600538f2d506ed4ab6f5b.png!small)

下面的问题就是如何进行提权了，经过一番测试，发现这里无法执行的命令是没有回显的，并且不能执行`cd`命令，但是可以使用`ls`和`cat`命令

![命令是没有回显](https://image.3001.net/images/20210118/1610954995_600538f3cc5dae008ed38.png!small)

![命令是没有回显](https://image.3001.net/images/20210118/1610954996_600538f48885d8da8b99d.png!small)

这里肯定是有权限控制的，可以使用`find / -type f -user www-data`命令查看这个用户可以读取的文件，除了`/proc`就是`/var/www/html/reports/.htaccess`和`/var/log/ona.log`

![查看这个用户可以读取的文件](https://image.3001.net/images/20210118/1610954997_600538f56c4a63fce6218.png!small)

读取`var/www/html/reports/.htaccess`可以找到`AuthUserFile`的路径`/var/www/.htpasswd`

![找到路径](https://image.3001.net/images/20210118/1610954998_600538f62fca12be76956.png!small)

读取这个文件如下，可以得到用户名`douglas`和HASH的密码`$apr1$9fgG/hiM$BtsL9qpNHUlylaLxk81qY1`，给的提示是`只包含aefhrt的十个字符`

![得到用户名和HASH的密码](https://image.3001.net/images/20210118/1610954998_600538f6eb6131405c62f.png!small)

    
    
    douglas:$apr1$9fgG/hiM$BtsL9qpNHUlylaLxk81qY1
    
    # To make things slightly less painful (a standard dictionary will likely fail),
    # use the following character set for this 10 character password: aefhrt 
    

先用`hash-identifier`看一下是哪个HASH，结果 hash -type : [+] MD5(APR)

![看一下是哪个HASH](https://image.3001.net/images/20210118/1610954999_600538f7b76395a404a38.png!small)

然后使用`crunch`生成对应的字典，命令格式`crunch <min-len> <max-len> [charset string]
[options]`，这里生成只包含aefhrt的10个字符，就可以使用如下命令`crunch 10 10 aefhrt -o
pass.txt`，更多的介绍可以看[Linux下的字典生成工具Crunch](sectool/170817.html)和[crunch命令详解](https://blog.csdn.net/qq_42025840/article/details/81125584)

![生成对应的字典](https://image.3001.net/images/20210118/1610955000_600538f8a754e6d8c2627.png!small)

最后就要用大名鼎鼎的`hashcat`去破解这个HASH，命令格式`hashcat [options]...
hash|hashfile|hccapxfile [dictionary|mask|directory]...`，这里使用的命令为`hashcat -m
1600 -a 0 -o res hash.txt pass.txt`

-m是HASH类别，-a是攻击方式，-o是输出结果，更多的参数可以参考[Hashcat密码破解攻略](sectool/164507.html)。这里在kali里面运行一直报错，就转移到wsl2里面了，命令`hashcat -m 1600 -a 0 -o res hash.txt pass.txt --force`

![在kali里面运行一直报错](https://image.3001.net/images/20210118/1610955001_600538f990e0830bfee86.png!small)

![密码](https://image.3001.net/images/20210118/1610955002_600538fa68b1ab09702a8.png!small)

最终密码为 `fatherrrrr`

或者这里也可以使用`john`来进行破解`john --wordlist=pass.txt hash.txt`，但是速度可能有丶问题

![进行破解](https://image.3001.net/images/20210118/1610955003_600538fb2af5ba1391dea.png!small)

使用ssh连接`ssh douglas@192.168.56.5`

![用ssh连接](https://image.3001.net/images/20210118/1610955004_600538fc2cf79a18008d4.png!small)

这里是个TTY，但还是存在权限控制，使用`sudo -l`看一下可以使用什么命令，结果是`(jen) NOPASSWD:
/bin/cp`，这里就有点奇怪了，`douglas`可以用`jen`的身份运行`cp`命令

![存在权限控制](https://image.3001.net/images/20210118/1610955005_600538fd3932cfdc74610.png!small)

先去访问一下`home`目录，发现`douglas`和`jen`这两个用户，但是只能用`jen`的`cp`命令，且没有`jen`的密码

![访问一下home目录](https://image.3001.net/images/20210118/1610955005_600538fdead36dac52f1b.png!small)

值得注意的是，如果`jen`用户下的`/home/jen/.ssh/authorized_keys`包含`douglas`的公钥，那就可以用`douglas`的`id_rsa`文件登陆`jen`的ssh，也即免密登陆`jen`的ssh。这里复制到`/tmp`目录下是因为`jen`没有权限访问`douglas`目录下的文件

    
    
    cp .ssh/id_rsa.pub /tmp/authorized_keys
    chmod 777 /tmp/authorized_keys 
    sudo -u jen /bin/cp /tmp/authorized_keys /home/jen/.ssh/
    
    

![用douglas的id_rsa文件登陆jen的ssh](https://image.3001.net/images/20210118/1610955006_600538feb2da7e5575969.png!small)

然后用ssh连接`ssh -i id_rsa jen@127.0.0.1`

![用ssh连接](https://image.3001.net/images/20210118/1610955007_600538ff919345220c728.png!small)

成功登陆`jen`，看到提示`mail`，还是先执行`echo $(find / -type f -user jen) >
1.txt`看一下，有一个`/var/mail/jen`的文件可以读取

![成功登陆jen](https://image.3001.net/images/20210118/1610955008_6005390085bdfb5f07ae6.png!small)

或者这里直接输入`mail`的命令也可以看到

![直接输入mail的命令](https://image.3001.net/images/20210118/1610955009_600539016788df741caeb.png!small)

读取一下，其内容如下

![读取其内容](https://image.3001.net/images/20210118/1610955010_60053902586ca01deff68.png!small)

关键词：`change Moss's password`、`his password is now Fire!Fire!`

接着ssh连接`moss`用户`ssh moss@127.0.0.1`

![ssh连接moss用户](https://image.3001.net/images/20210118/1610955011_60053903852ad5c374390.png!small)

在当前目录发现了一个隐藏目录`.games`，访问后发现一个`root`权限的二进制文件`upyourgame`

![二进制文件](https://image.3001.net/images/20210118/1610955012_60053904734d50b7b5862.png!small)

运行之后就发现自己神奇的变成root用户辣

![运行之后](https://image.3001.net/images/20210118/1610955013_600539057fec5fb4aa230.png!small)

最后，flag在`/root`中，为`8f3b38dd95eccf600593da4522251746`

![flag](https://image.3001.net/images/20210118/1610955014_60053906672b6cc39cfbe.png!small)

  

彩蛋时刻，其实在拿到`douglas`的密码之后就可以用虚拟机登陆，然后操作，这里是用的`moss`的账号密码，也是同样的效果

![彩蛋时刻](https://image.3001.net/images/20210118/1610955015_6005390720aae67908ec0.png!small)

