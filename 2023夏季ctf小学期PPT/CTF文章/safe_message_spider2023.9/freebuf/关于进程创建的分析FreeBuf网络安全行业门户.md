## **前言**

最近分析了利用fork函数使一个进程创建另外一个进程，两个进程分别有自己的pid，并且能够独立完成作业，写了几个小lab对其进行测试。

##  **一些概念和指令**

进程的概念：程序时一堆待执行的代码。

> project.c ：c语言程序，存在于硬盘中
>
> project：可执行程序

关机重启之后，程序依然还在。

进程就是当程序被cpu加载时，根据每一行代码做出相应的效果，形成一个动态的过程，那个过程就是进程（存在于内存中）。

关机之后，进程就不在了。

在linux下，如何开启一个新进程：

在linux终端上执行一个程序，就可以开启一个进程。

 **进行对于系统来说需要分配的资源：**

> 分配对应的内存空间；
>
> 对于系统来说，一个进程就是一个任务，当一个进程启动后，系统分配一个任务结构体给进程，描述这个进程信息。

任务结构体：struct
task_struct{}![](https://image.3001.net/images/20211222/1640162674_61c2e572989c1bb0afad4.png!small)  
 **关于查看进程linux命令：**

1）查看整个整个系统进行ID号， ps -ef （静态）

2）top指令：

> 当前系统中进程总数
>
> 查看动态使用率

3）查看整个系统中所有进程关系：pstree

4）进程的诞生和死亡：  
![](https://image.3001.net/images/20211222/1640162809_61c2e5f9667536b09bf0f.png!small)  
![](https://image.3001.net/images/20211222/1640162825_61c2e609d53c5cfdc072f.png!small)  
 **总结：**

> 1)进程在暂停态后，收到继续信号，切换到就绪态；
>
> 2)程序中main函数执行return 语句时，代表进程结束，一定会变成僵尸态；
>
> 3)进程有且只能有一个父进程；
>
> 4)孤儿进程特征时失去父亲后，马上寻找继父；
>
> 5)祖先进程一定帮其他进程回收资源。

仔细分析此流程图，发现task_struct结构体包含着进程的状态。我们在下一篇文章会分析task_struct的源码。

##  **fork()**

 **进程的函数接口：**

单进程程序：只能一行一行的代码去执行；

多进程程序：同时执行两行代码。本来的进程产生一个新的自己子进程，fork函数可以实现多进程程序执行。

首先我们先来查看一下fork函数的使用：fork（）函数在一个运行的进程中产生另一个子进程。

    
    
    pid_t    fork(void)

成功：

父进程：子进程pid号

子进程：0

失败：

父进程：父进程pid号

没有子进程

###  **lab1**

    
    
    {printf("hello world\n");fork();//现在就有两个进程了printf("tree");return 0;}

![](https://image.3001.net/images/20211222/1640162960_61c2e6905a03dc48bf402.png!small)  
可以看到这里有两个tree，只有父进程结束后，才有命令行的出现。

所以第一个tree是子进程，第二个tree是父进程。

###  **lab2**

让父子进程做不同的事情：

    
    
    #include<stdio.h>#include<unistd.h>int main(int argc,char *argv[]){pid_t x;x= fork();if(x>0){printf("1");}else{printf("2");}}

![](https://image.3001.net/images/20211222/1640163019_61c2e6cb0c7dfab67adfc.png!small)  
可以看到子进程是有可能在父进程执行之前先执行的。

 **加入sleep**

sleep（）函数可以让一个进程进行睡眠。

在一个进程中查看自己的pid以及父进程的pid。

查看自己的pid ：getpid（）

查看父进程的pid：getppid（）

    
    
    #include <sys/types.h>#include<unistd.h>pid_t getpid(void)pid_t getppid(void)

返回值：

成功：

getpid 返回自身的pid号

getppid 返回父进程的pid号

###  **lab3打印自身的pid和child_pid**

    
    
    #include <unistd.h>#include <stdio.h>#include <stdlib.h>int main(int argc,char *argv[]){pid_t x;x = fork();if(x>0){printf("parent pid = %d\n",getpid());printf("child pid = %d\n",x);}if(x==0){printf("child pid = %d\n",getpid());printf("parent pid = %d\n",getppid());}return 0 ;}

![](https://image.3001.net/images/20211222/1640163112_61c2e7285f209dcddc1e4.png!small)  
可以看到打印的pid和ppid。

###  **lab4查看父进程的变化**

    
    
    #include <unistd.h>#include <stdio.h>#include <stdlib.h>int main(int argc,char *argv[]){pid_t x;x = fork();if(x>0){sleep(2);printf("parent %d pid will die\n",getpid());}if(x==0){sleep(1);printf("faster %d\n",getppid());sleep(4);﻿printf("faster %d\n",getppid());printf("I will down\n");}return 0 ;}

![](https://image.3001.net/images/20211222/1640163168_61c2e76003b254971fee4.png!small)  
可以看到faster pid从3164变成了1。

##  **总结**

利用sleep函数等对进程运行进行控制，以及观察pid的状态，使得更好的观察进程是如何运行的，以及进程运行的顺序。

