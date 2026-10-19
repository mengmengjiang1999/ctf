## **0x01前言**

这关其实和pwn关系不大，主要考察的都是linux下一些函数的操作，考察linux的基本功。涉及到的知识点包括一些经典的函数原型、IO重定向、文件描述符、管道、环境变量、socket编程、符号链接等。

这里顺便真心安利一本书，《UNIX环境高级编程》，简称APUE书里介绍UNIX文件和目录、标准I/O库、系统数据文件和信息、进程环境、进程控制、进程关系、信号、线程、线程控制、守护进程、各种I/O、进程间通信、网络IPC、伪终端等方面的内容，还在此基础上结合函数原型介绍了多个应用示例，如果这本书啃透，正常题型linux下的pwn问题都不大。

##  **0x02**

登录后直接看源文件

![f694a3e173cb5c11bc0e9cb8dce90f56296.png](https://image.3001.net/images/20210727/1627367799_60ffa97774f0f64f828a0.png!small)

可以看到这里分成了好几关

先看第一关//argv

第一个if要求传入100个参数

第二个if要求第A个（也就是ascii的65）参数的值为’\x00’

第三个if要求第B个（也就是ascii的66）的参数值为’\x20\x0a\x0d’

这题我们写c

![f694a3e173cb5c11bc0e9cb8dce90f56424.png](https://image.3001.net/images/20210727/1627367803_60ffa97b3ad47264e13af.png!small)

这里的execve的原型为：

    
    
    int execve(const char * filename,char * const argv[ ],char * const envp[ ]);

execve()用来执行参数filename字符串所代表的文件路径，第二个参数是利用指针数组来传递给执行文件，并且需要以空指针(NULL)结束，最后一个参数则为传递给执行文件的新环境变量数组。

也就是说代码中的execve是用于执行input程序的，而作为传入的参数，最后要以null结尾，对应代码中的args[100]=NULL

看第二部分//stdio

read函数原型为ssize_t read [1] (int fd, void *buf, size_t count);

read()会把参数fd所指的文件传送count 个字节到buf 指针所指的内存中。

而题目源码中的fd的0，2分别对应的是stdin,stderr，这里是读4个字节到buf

然后调用memcmp

memcmp函数的原型为 int memcmp(const void *str1, const void *str2, size_t
n));其功能是把存储区 str1 和存储区 str2 的前 n 个字节进行比较

整理一下，代码的逻辑就是从stdin中读4个字节，与\x00\x0a\x00\xff比较，从stderr读4个字节，与\x00\x0a\x02\xff比较

那么问题来了，stdin是标准输入，我们可以直接通过输入来控制，而stderr，该怎么控制呢

答案是IO重定向

 **这里涉及管道pipe的应用**

pipe有两端，一段write写入，一端read读出，这里解题用到的就是把管道的read重定向到某一个流中，从而进程间可以进行通信。

这里我们的思路是父进程fork子进程，子进程write需要的四字节到pipe，父进程把pipe的read重定向到stdin,stderr。通过这种方式我们就可以控制stdin和stderr的内容了

先定义pipe

![f694a3e173cb5c11bc0e9cb8dce90f561290.png](https://image.3001.net/images/20210727/1627367805_60ffa97dc58481b74f047.png!small)

 **第三关//env**

strcmp()用于字符串的比较，getenv()用来取得参数envvar环境变量的内容。参数envvar为环境变量的名称，如果该变量存在则会返回指向该内容的指针。环境变量的格式为envvar=value。

正常情况下肯定没有0deadbeef的环境变量，要想if条件成立，肯定需要我们自己写一个键值对

我们可以使用setenv（）增加环境变量

setenv()原型为int setenv(const char *name,const char * value,int overwrite)

函数说明 setenv()用来改变或增加环境变量的内容。参数name为环境变量名称字符串。参数
value则为变量内容，参数overwrite用来决定是否要改变已存在的环境变量。如果没有此环境变量则无论overwrite为何值均添加此环境变量

本地写好源文件

对应代码为

    
    
    setenv("\xde\xad\xbe\xef", "\xca\xfe\xba\xbe", 1);

这时候execve传入的第三个参数为新环境变量数组，我们声明为environ

![f694a3e173cb5c11bc0e9cb8dce90f561775.png](https://image.3001.net/images/20210727/1627367811_60ffa9831fc686e3dda53.png!small)

第四关//file

打开名为”\x0a”的文件，比较前四个字节是否为”\x00\x00\x00\x00”

这关很简单，我们相应的用写权限打开该文件，写前四个字节即可

![f694a3e173cb5c11bc0e9cb8dce90f561861.png](https://image.3001.net/images/20210727/1627367811_60ffa983ecc0a3c995311.png!small)

第五关//network

代码的意思是以input这个文件作为服务器，监听C端口

通过recv来接收，如果收到的为\xde\xad\xbe\xef，则通过

我们根据对应的代码稍微修改下就可以了

![f694a3e173cb5c11bc0e9cb8dce90f561962.png](https://image.3001.net/images/20210727/1627367812_60ffa984cf9949ccc9861.png!small)

在本地编写完整的代码

![f694a3e173cb5c11bc0e9cb8dce90f561976.png](https://image.3001.net/images/20210727/1627367816_60ffa98859183f4d53beb.png!small)

![f694a3e173cb5c11bc0e9cb8dce90f561978.png](https://image.3001.net/images/20210727/1627367821_60ffa98d696d49502f523.png!small)

![f694a3e173cb5c11bc0e9cb8dce90f561980.png](https://image.3001.net/images/20210727/1627367827_60ffa9933a8146b7aff17.png!small)

通过scp上传

![f694a3e173cb5c11bc0e9cb8dce90f561990.png](https://image.3001.net/images/20210727/1627367830_60ffa9963db698c67ce26.png!small)

登录后切换到相应的路径编译源文件

![f694a3e173cb5c11bc0e9cb8dce90f562009.png](https://image.3001.net/images/20210727/1627367831_60ffa9973a7a59dbbc2a9.png!small)

直接执行是会报错的，因为当前目录下没有flag文件，我们又没有权限移动它，此时可以考虑使用符号链接的方式，通过绝对路径或者相对路径的形式指向flag。因为对符号链接文件进行读写会表现为直接对目标文件进行操作

![f694a3e173cb5c11bc0e9cb8dce90f562115.png](https://image.3001.net/images/20210727/1627367833_60ffa999889aafc0f3ec7.png!small)

这里是让/tmp/yale/flag直接指向/home/input2/flag

然后执行

![f694a3e173cb5c11bc0e9cb8dce90f562162.png](https://image.3001.net/images/20210727/1627367834_60ffa99a790bad76b3b7b.png!small)

通关

管道命令（实验主要介绍了选取命令的使用、排序命令的使用以及双向重定向命令。）

[http://www.hetianlab.com/expc.do?ec=ECID172.19.104.182014091814152800001](http://www.hetianlab.com/expc.do?ec=ECID172.19.104.182014091814152800001&pk_campaign=freebuf-wemedia)

