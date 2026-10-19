***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一、漏洞背景

 **近日，Linux
git中发布一个commit补丁，该补丁对应的漏洞是一个本地提权漏洞CVE-2019-8912，漏洞影响范围较广。根据git中的commit信息可知，该漏洞出现在内核'crypto/af_alg.c'中的af_alg_release函数中，可以通过sockfs_setattr函数触发，漏洞类型是use
after free，可以导致本地代码执行进行权限提升。**

## 二、漏洞影响版本

    
    
    Linux 2 .6 ~ linux 4.20.11
    
    Red Hat Enterprise Linux 7，Package： kernel-alt
    
    Debian，Release：Jessie，Version：3.16.56-1+deb8u1
    
    Debian，Release：Jessie (security)，Version：3.16.56-1
    
    Debian，Release：stretch，Version：4.9.144-3
    
    Debian，Release：stretch (security)，Version：4.9.110-3+deb9u6
    
    Debian，Release：buster，Version：4.19.16-1
    
    Debian，Release：sid，Version：4.19.20-1

## 三、Linux Crypto模块简介

Linux内核从版本2.5开始引入了加密机制，为内核提供加密功能，应用包括：硬件加密设备驱动、内核代码签名、硬件随机数生成器、文件系统加密等。从版本2.6.6之后，内核源码提供了丰富的密码学算法支持，并可以通过配置编译选项将加密算法作为模块编入内核。内核编译配置如下图所示：

![](https://image.3001.net/images/20190226/1551159607_5c74d137b8d26.png!small)

但是该加密功能提供的API接口只能在内核层进行使用，用户层无法调用。2010年，有位维护者向Linux Crypto维护组提交了一份CrypatoAPI
用户接口，类似于netlink，基于socket进行通信，便于用户层访问内核加密子系统。功能实现代码在文件crypto/af_alg.c中。

## 四、漏洞原理及溯源

漏洞存在于crypto
模块中的af_alg_release()函数中。af_alg_release()函数在进行对象释放时，未将对象置空。对应commit：9060cb719e61b685ec0102574e10337fa5f445ea补丁代码如下，补丁添加了一行代码：sock->sk
= NULL; 。

![](https://image.3001.net/images/20190226/1551159630_5c74d14ec3259.png!small)

在未添加补丁之前，如果该sock->sk引用计数是1，当调用sock_put()进行释放后没有置空，就直接返回，会产生一个sock->sk悬挂指针。

为了分析这个漏洞的前因后果，先分析下相关的socket代码。对每个新创建的socket，Linux内核都将在sockfs中创建一个新的inode。Sockfs_*系列函数就是用来操作sockfs文件系统的。Sockfs_setattr()函数就是设置socket文件属性的。在net/socket.c文件中sockfs_setattr()函数将会使用sock->sk对象。

根据提交的commit：9060cb719e61b685ec0102574e10337fa5f445ea细节可知，在该漏洞披露之前，Linux已经修复了sock_close()和sockfs_setattr()之间的条件竞争漏洞，对应commit为6d8c50dcb029872b298eea68cc6209c866fd3e14，具体先看下sockfs_setattr()函数中的补丁。补丁代码如下：

![](https://image.3001.net/images/20190226/1551159660_5c74d16c83643.png!small)

行544，首先判断sock->sk是否为空，如果不为空，行545再将用户层传进来的iattr->ia_uid赋值为sock->sk->sk_uid。然后看sock_close
()函数中的补丁。补丁代码如下：

![](https://image.3001.net/images/20190226/1551159686_5c74d1864e84d.png!small)

行1186，替换成了新函数__sock_release()，该函数多了一个参数inode。__sock_release()函数实现如下：

![](https://image.3001.net/images/20190226/1551159701_5c74d1959c3fa.png!small)

行601，对inode进行判断，如果不为空，然后调用inode_lock()函数对其进行上锁。其实该inode本身和要进行释放的socket对象是对应的。行603，调用ops中release()函数进行释放操作。这个ops中release()函数只是一个函数指针，最终会根据用户注册哪种套接字类型决定。行604，再次判断inode是否为空，如果不为空，再进行解锁。通过对inode加锁，防止在对socket对象释放时进行其他操作。

从commit：6d8c50dcb029872b298eea68cc6209c866fd3e14提供的细节可知，sock_close()函数和sockfs_setattr()函数之间的条件竞争可以通过用户层fchownat()函数引发。根据man手册可知，该函数是用于设置文件属性的，例如uid和gid，在内核中对应的sockfs_setattr()函数，如下图所示：

![](https://image.3001.net/images/20190226/1551159741_5c74d1bd83cf5.png!small)

细节中描述，该函数不会保持文件fd的引用计数，这也是导致存在条件竞争的原因。根据前文可知，sockfs_setattr()函数其实就是设置UID才操作sock->sk对象的。

如果再继续向前追溯的话，从commit：86741ec25462e4c8cdce6df2f41ead05568c7d5e提供的细节可知UID的来龙去脉。该补丁提交于2016年。由于socket
协议中的结构体structsock在大多时候都是和用户层的sockets一一映射的，sockets对应的内核结构体为structsocket。考虑到方便操作，便通过向struct
sock添加一个sk_uid字段来简化对struct socket中的UID的匹配，也因此添加了一个关键函数。如下图所示：

![](https://image.3001.net/images/20190226/1551159765_5c74d1d57e4ac.png!small)

由此可知，本来存在于sock_close()和sockfs_setattr之间的条件竞争已经被修复，由于crypto/af_alg.c中af_alg_release()函数没有将释放后的sock->sk及时置空，导致前面所做的安全补丁全部失效。

## 五、安全建议

目前该漏洞补丁已经给出，请及时升级到最新版本。

>
> <https://github.com/torvalds/linux/commit/9060cb719e61b685ec0102574e10337fa5f445ea>

 ***本文作者：启明星辰积极防御实验室（ADLab），转载请注明来自FreeBuf.COM**

