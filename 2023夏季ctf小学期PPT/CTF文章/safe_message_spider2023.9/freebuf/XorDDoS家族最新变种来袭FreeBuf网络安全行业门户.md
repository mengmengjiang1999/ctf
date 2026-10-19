## 概述

**最近接到某客户反馈Linux服务器存在异常流量和可疑进程，深信服EDR安全团队迅速出击，捕获到了相应的恶意样本，通过分析确认此样本是Linux.XorDDoS恶意样本的最新变种，感染方式和远程恶意服务器地址均发生了改变。**

此样本在VT上的截图信息，如下所示：

![图片.png](https://image.3001.net/images/20180526/15272997823228.png!small)

## 样本简介

2014年9月底，MalwareMustDie发现Linux.XorDDoS，它构成了分布式拒绝服务攻击的僵尸网络，Linux.XorDDoS恶意家族主要特点是，用暴力猜解目标主机ssh弱密码的方式，入侵目标主机，然后执行相应的shell脚本安装Linux.XorDDoS恶意家族以及恶意RootKit感染客户主机。

Linux.XorDDoS运行之后，会通过fork创建子进程，然后结束掉父进程，并创建相应的守护进程，然后删除自身，拷贝自身到相应的目录下，同时样本运用了“多态”的方式，在相应的目录不断生成随机文件名的恶意程序，运行之后又删除自身，导致安全人员在查找相应的恶意程序时，总是定位不到相应的文件，进程列表也不断发生改变，同时Linux.XorDDoS会利用RootKit技术隐藏相应的IP地址端口号，然后通过与远程服务器进行通信，返回相应的数据包，解密之后，对相应的服务器IP地址发起DDOS攻击。

## 样本分析

1.查看恶意样本文件类型，为Linux32位程序，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272997897638.png!small)

2.通过反汇编，查看Main函数如下所示：

![图片.png](https://image.3001.net/images/20180526/15272997959563.png!small)

病毒会先设置相应的环境变量：

/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:/usr/X11R6/bin，然后再通过解密函数对相应的字符串进行解密，得到相应的文件目录或文件路径：

    
    
    /boot  /var/run/sftp.pid   /lib/udev/udev  /lib/udev/  /var/run

同时解密出配置文件的URL地址如下：

<http://info.3000.uc.com/config.rar>

解密字符串的函数如下所示：

![图片.png](https://image.3001.net/images/20180526/15272998008004.png!small)

查看ida里的xorkeys，我们可以得到它的加解密的key，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272998044821.png!small)

Key的值为：BB2FA36AAA9541F0

3.能过解密函数，解密出daemonname，daemonnname字符串如下所示：

![图片.png](https://image.3001.net/images/20180526/15272998091921.png!small)

解密过程如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272998143159.png!small)

相应的反汇编代码如下：

![图片.png](https://image.3001.net/images/20180526/15272998199365.png!small)

解密之后的命令行如下：

![图片.png](https://image.3001.net/images/20180526/15272998259265.png!small)

4.创建相应的守护进程，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272998521649.png!small)

相关的反汇编代码如下：

![图片.png](https://image.3001.net/images/20180526/15272998575962.png!small)

5.获得自身进程文件的路径，判断是否在/boot目录下，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272998624483.png!small)

如果不是在/boot下，则创建恶意程序运行主体的目录/boot，并拷贝自身的/boot，同时创建相应的备份文件目录/lib/udev，同时拷贝自身到/lib/udev/udev，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272998673585.png!small)

通过get_self得到自身进程的程序，如下下图所示：

![图片.png](https://image.3001.net/images/20180526/15272998813111.png!small)

最后通过remove删除自身，然后再运行/boot下的恶意程序，文件名为随机的10个字母组成，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272998848526.png!small)

6.获取进程的共享内存，然后执行后面的恶意操作，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272998896690.png!small)

7.这个样本包含安装rootkit的代码，但并未执行，而是能过安装脚本进行rootkit安装的，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272998927770.png!small)

![图片.png](https://image.3001.net/images/20180526/15272998977918.png!small)

代码在执行的时候默认跳过了安装RootKit恶意的代码段

8.加载自启动服务项，先将在/boot中运行的主恶意程序，写入到/etc/init.d/随机文件名启动项中，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272999222313.png!small)

![图片.png](https://image.3001.net/images/20180526/15272999262194.png!small)

然后将cron的内容写入到/etc/cron.hourly/cron.sh中，并将之前的自启动项写入到rc*.d文件中，然后再删除相应的rc*.d/S90**********文件，创建相应的符号连接，更新rc.d配置项，同时将之前生成的cron.sh写入到/etc/crontab定时器任务中，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272999318201.png!small)

写入之后的文件内容如下所示：

![图片.png](https://image.3001.net/images/20180526/15272999357613.png!small)

里面S90**********随机生成的文件名，内容如下所示:

![图片.png](https://image.3001.net/images/20180526/15272999395053.png!small)

9.检测是否存在rootkit恶意驱动程序，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272999433087.png!small)

10.修改自身文件的用户属性，然后能过解密函数解密出远程恶意服务器的网址，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272999488.png!small)

相应的反汇编代码如下：

![图片.png](https://image.3001.net/images/20180526/15272999523220.png!small)

解密出来的网址如下：

> 23.234.52.54:5009
>
> zxchk.xicp.net:5009

将解密出来的网站加入到恶意服务器列表之中，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272999579290.png!small)

11.对解密出来的恶意网站，能过RootKit恶意程序隐藏相应的网络端口，如下图所示：

![图片.png](https://image.3001.net/images/20180526/1527299961260.png!small)

当存在RootKit驱动模块的时候，发送相应的RootKit执行的命令编号0x9748712，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272999712270.png!small)

12.创建线程，执行恶意网络连接操作，通过uname获得主机的相关信息，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272999752340.png!small)

然后再构造相应的数据包，并发送到远程恶意服务器，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272999802376.png!small)

13.解密相应的返回数据包的数据，如下图所示：

![图片.png](https://image.3001.net/images/20180526/1527299985557.png!small)

解密返回的数据包代码如下：

![图片.png](https://image.3001.net/images/20180526/15272999884695.png!small)

通过解析出来的不同命令执行不同的操作：

1)添加DDOS任务，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272999937778.png!small)

然后创建线程，对解密出来的IP地址，执行DDOS攻击，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15272999987687.png!small)

DDOS攻击的方式主要为dns,syn两种方式，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15273000052674.png!small)

执行DDOS攻击，通过WireShark网络抓包，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15273000103005.png!small)

![图片.png](https://image.3001.net/images/20180526/15273000144821.png!small)

![图片.png](https://image.3001.net/images/20180526/15273000173374.png!small)

DDOS服务器的IP地址：

> 103.198.73.176
>
> 59.56.66.67

2)创建线程，下载程序，并执行，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15273000233.png!small)

下载程序并执行,相应的反汇编代码，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15273000265302.png!small)

3)创建线程，更新文件，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15273000307889.png!small)

更新程序的反汇编代码，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15273000341598.png!small)

14.解密出相应的URL地址，然后执行daemondown无限循环下载，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15273000468566.png!small)

相应的反汇编代码如下：

![图片.png](https://image.3001.net/images/20180526/15273000892570.png!small)

15.后面就是恶意程序的“多态”和“驻留”机制了，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15273000936633.png!small)

删除自身，然后拷贝/lib/udev/udev程序到/boot下的随机程序，并执行

![图片.png](https://image.3001.net/images/20180526/15273000989171.png!small)

删除相应的自启动项，然后拷贝/lib/udev/udev程序到/boot下的随机程序，并执行

16.查看进程列表，如下图所示：

![图片.png](https://image.3001.net/images/20180526/1527300107180.png!small)

查看恶意进程的文件，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15273001126533.png!small)

恶意程序会通过上面的“多态”和“驻留”的方式，不断的在/boot下创建随机恶意程序名，然后执行，再不断的自删除相应的自启项，然后再创建恶意进程，再不断删除，循环执行，如下图所示，执行ls时，/boot下的恶意程序会不断的变化，如下图所示：

![图片.png](https://image.3001.net/images/20180526/15273001179622.png!small)

## 清理样本

> 1) 清除/lib/udev/目录下的udev程序
>
> 2) 清除/boot下的随机恶意文件（10个随机字符串数字）
>
> 3) 清除/etc/cron.hourly/cron.sh和/etc/crontab定时器文件相关内容
>
> 4) 如果有RootKit驱动模块，需要卸载相应的驱动模块，此次恶意程序主要它来隐藏相关的网络IP端口
>
> 5) 清除/lib/udev目录下的debug程序

## IOC

MD5

> 0B3456561B7942AA67403CDDC1FAD2BD

URL

> zxchk.xicp.net:5009
>
> 23.234.52.54:5009

 *** 本文作者千里目安全实验室，转载注明来自FreeBuf.COM**  

