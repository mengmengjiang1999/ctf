## **前言**

在《关于进程创建分析》一文中，对一些linux命令以及进程创建、进程状态做了讲解，还做了几个小lab。在本篇文章中，将继续延续上篇文章的知识，讲解一些文件操作指令并做一些小lab。

##  **解决僵尸问题**

  * wait()函数是为了回收资源
  * wait for process to change state

###  **1）父进程还在，并且主动回收子进程资源**

  * pid_t wait (int *status)
  * status：获取子进程的退出状态

如果这里是：wait（NULL），代表父进程只回收资源，不关心子进程退出状态。

  * int x；
  * wait(&x)

 **返回值：**

成功：返回结束的子进程pid号

失败：-1

如果进程在运行态，那么wait函数就会阻塞等待子进程变成僵尸态为止。

如果子进程在僵尸态，wait函数马上返回。

例题：子进程工作时间长，父进程工作时间短。

    
    
    #include <stdio.h>#include <unistd.h>#include <stdlib.h>#include <sys/wait.h>int main(int argc,char *argv[]){pid_t x;x = fork();if(x>0){sleep(3);printf("3s:I was father ,i will wait my child\n");wait(NULL);printf("I  have wait my child\n");}if(x==0){sleep(8);printf("I will death in 8s\n");}}

###
![](https://image.3001.net/images/20220105/1641373181_61d55dfdf38475acc0c24.png!small)  
 **2）子进程工作时间短，父进程工作时间长**

这种情况会出现僵尸进程问题。

    
    
    #include <stdio.h>#include <unistd.h>#include <stdlib.h>#include <sys/wait.h>int main(int argc,char *argv[]){pid_t x;x = fork();if(x>0){sleep(8);printf("8s:I was father ,i will wait my child\n");wait(NULL);printf("I  have wait my child\n");}if(x==0){sleep(3);printf("I will death in 3s\n");}}

![](https://image.3001.net/images/20220105/1641373239_61d55e377b85d49a4f7a1.png!small)

可以看到这里是有僵尸程序的。

###  **3）父进程还在，不主动回收子进程资源**

子进程等到父进程退出为止，在寻求一个新的父亲作为父进程，帮自己回收资源。

    
    
    #include <stdio.h>#include <unistd.h>#include <stdlib.h>#include <sys/wait.h>int main(int argc,char *argv[]){pid_t x;x = fork();if(x>0){sleep(8);printf("8s:I was father ,i will wait my child\n");printf("I  have wait my child\n");}if(x==0){sleep(3);printf("I will death in 3s\n");}}

###  **4） 子进程的退出状态如何返回给父亲**

子进程在退出时，需要调用一个函数，就可以把退出状态返回给父进程。

    
    
    exit()_Exit()_exit()

这三个函数都可以使得进程退出，并且可以将退出状态返回给父进程。

exit()先清洗缓冲区，再退出。

 **导致普通进程结束：**

    
    
    #include<stdlib.h>void exit(int status)

 **参数：**

  * status ：0表示正常退出
  * 非0表示异常退出
  * Exit(),exit() 不清洗缓冲区，直接退出

##  **子进程退出状态问题**

例题：父进程去回收子进程的资源，子进程正常退出，输出 ok，异常退出，输出err

    
    
    #include <stdio.h>#include <stdlib.h>#include <unistd.h>#include <sys/wait.h>int main(int argc,char *argv[]){pid_t x;x = fork();if(x>0){sleep(1);wait(&state);if(state==0){printf("ok");}else{printf("err");  }}if(x==0)

![](https://image.3001.net/images/20220105/1641373796_61d5606480e47e9e6d5d3.png!small)

    
    
    {sleep(6);exit(0);}}

![](https://image.3001.net/images/20220105/1641373855_61d5609f19379486d3926.png!small)  
 **程序中，调用exit（）函数与执行return语句有什么区别?**

  * 如果在main函数中，exit与return语句作用是一样的。
  * 如果不在main函数中，exit就代表进程的退出，return 语句只是代表函数的返回。

##  **扇形进程个数问题**

    
    
    #include <stdio.h>#include <unistd.h>#include <stdlib.h>#include <sys/wait.h>int main (int argc ,char *argv[]){int n;printf("process mount :\n");scanf("%d",&n);int i;pid_t x;//chanshengfor(i=0;i<n;i++){x = fork();if(x>0){continue;  }if(x==0){break;}}if(x>0){for(i=0;i<n;i++){wait(NULL);  }printf("parent pid=%d\n",getpid());}if(x==0){printf("child pid = %d\n",getpid());exit(0);}}

![](https://image.3001.net/images/20220105/1641373921_61d560e1b9eba75881a68.png!small)

##  **exec函数族**

  * exec函数组接口
  * exec 执行
  * exec函数族，指的是一堆可以帮我们执行程序的函数

    
    
    execute a file #include <unistd.h>extern char **environ;int execl(const char *pathname, const char *arg, .../* (char  *) NULL */);int execlp(const char *file, const char *arg, .../* (char  *) NULL */);int execle(const char *pathname, const char *arg, .../*, (char *) NULL, char *const envp[] */);int execv(const char *pathname, char *const argv[]);int execvp(const char *file, char *const argv[]);int execvpe(const char *file, char *const argv[],char *const envp[]);

path：需要执行的那个程序的绝对路径

arg：以“,”分开所有参数，以NULL，作为结束标志（直接作为形参）

file：程序的文件名

argv：以”，“分开所有参数，以NULL作为结束标志（先放到一个数组中，再把数组作为形参）

envp：环境变量的路径

例题：让子函数实现ls -l操作

    
    
    #include <stdio.h>#include <unistd.h>#include <stdlib.h>#include <sys/wait.h>int main(int argc,char *argv[]){pid_t x;x= fork();if(x>0){sleep(2);wait(NULL);exit(0);}if(x==0){execl("/bin/ls","ls","-l",NULL);}return 0;}

结论：只要执行了exec函数族，那么进程后面的代码会被覆盖。

![](https://image.3001.net/images/20220105/1641374012_61d5613cabf5a403f366e.png!small)

可以看到并没有printf出。

##  **如何确保子进程先运行？**

    
    
    vfork()NAMEvfork - create a child process and block parentSYNOPSIS#include <sys/types.h>#include <unistd.h>  pid_t vfork(void);

fork是随机运行，vfork是父进程阻塞。

当子进程中调用exit（）函数后者是exec函数族中的接口时，就会开始运行父进程的代码。

    
    
    #include <stdio.h>#include <unistd.h>#include <stdlib.h>#include <sys/wait.h>int main(int argc,char *argv[]){pid_t x;x = vfork();if(x>0){printf("my child\n");}if(x==0){sleep(3);printf("child\n");execl("/bin/ls","ls","-l",NULL);}      }

![](https://image.3001.net/images/20220105/1641374087_61d561872a2577d244d47.png!small)

##  **父子进程之间的资源问题**

![](https://image.3001.net/images/20220105/1641374144_61d561c065d1fa7b05c85.png!small)

![](https://image.3001.net/images/20220105/1641374174_61d561de6d0f92931a292.png!small)

###  **进程之间的通信：**

进程之间的资源是分开的，进程之间的资源没有办法进行交换。

##  **linux下，有多少通信方式？**

###  **一共有4种：**

  * 管道通信：无名管道与有名管道。是一种专门用于通信的文件，一个进程往管道文件中写入，一个进程从管道文件中读出数据。
  * 信号：通过发送一些信号给进程，那么这个进程会转换为相应的状态。
  * 消息队列：一个进程负责将消息发送到队列上，另一个进程可以从消息队列中读取数据出来。读取消息的进程可以读取队列上某一个特定的数据。
  * 共享内存：两个进程使用同一片内存空间进行数据交换。 

### **什么是无名管道？**

  * 无名管道实际是一个数组，所以只能运行于一个文件中。
  * 只能作用于亲缘关系的进程，例如：父子进程。

###  **实现步骤：**

  1. 申请一个数组：读端和写段是一个文件描述符，数组应该定义为：int fd[2]，现在只是定义了数组。
  2. 使用函数接口来初始化数组，使得数组的元素变成读端和写端。

    
    
    NAMEpipe, pipe2 - create pipeSYNOPSIS#include <unistd.h>

 **返回值：**

成功0

失败-1

初始化成功

 **结果：**

fd[0]-->读端

fd[1]-->写端

 **初始化的读端与写端文件描述符等于多少？**

pipefd：一个具有2个int类型变量的数组。

例题：初始化的读端与写端的文件描述符

    
    
    #include <stdio.h>#include <unistd.h>#include <stdlib.h>#include <sys/wait.h>int main(int argc,char *argv[]){int fd[2]={0};printf("fd[0]=%d\n",fd[0]);printf("fd[1]=%d\n",fd[1]);pipe(fd);printf("fd[0]=%d\n",fd[0]);printf("fd[1]=%d\n",fd[1]);return 0;}

![](https://image.3001.net/images/20220105/1641374330_61d5627a65738456ecd03.png!small)

##  **总结**

进程这部分内容，是有很多值得研究的东西，还有资源共享、互斥、同步、锁等有关问题，使得用户使用更加方便。

