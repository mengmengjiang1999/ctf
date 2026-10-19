# 背景

最近发现一个命令执行风险；  
一开始提供修复建议，是对特殊字符进行过滤，但是业务侧没有办法过滤，因为输入点是没有办法限制的，然后提供另一个方案是将用户的输入写到配置文件中，然后再进行操作，而不是直接拼接用户的输入；但是提供的方案没有被采纳，所以就有了下文的分析；

本文以Linux环境为背景，只分析C语言的命令执行漏洞。

# C的命令执行漏洞分析

## 漏洞简介

wiki百科上描述：任意代码执行（简称ACE）是指攻击者能够让目标电脑或目标进程中执行任意命令或代码[1]。如果系统有地方可以被黑客利用以执行任意代码，则此处被称为任意代码执行漏洞。特别设计利用此一漏洞的程式，称为任意代码执行漏洞利用。可以通过网络（尤其是通过互联网等广域网）让目标电脑（远程电脑）执行任意代码的能力称为远程代码执行（RCE）。

wiki的描述比较偏于云端的场景，这里场景就是指用户通过浏览器或者其他辅助程序提交数据，由于执行端没有针对执行函数进行过滤，导致在没有指定绝对路径的情况下执行命令。

## 漏洞成因

在了解漏洞成因之前先看一下C语言在Linux环境中可以执行shell命令的函数；分别是system，popen和exec家族函数。

    
    
    exec()							# 在当前进程中执行命令，其后所有的代码将被清空，不能执行
    system() = fork + exec			# 在子进程中执行指令
    popen()  = fork + exec + pipe		# 重定向子进程的标准输入或输出，提供控制子进程输入或输出的能力
    

关于exec()家族

  * l 代表函数取一个参数列表

    
    
    execl ("/bin/sh", "sh", "-c", command, (char *) 0);
    

  * v 代表函数取一个 agrv[] 向量

    
    
    char *argv[] = {"sh", "-c", command, (char *) 0};
    execv("/bin/sh", argv);
    

  * p 代表通过 PATH 环境变量来查找可执行文件，因此只用提供文件名

    
    
    execlp ("sh", "sh", "-c", command, (char *) 0);
    

  * e 代表使用指定的环境变量，函数取一个 envp[] 数组

    
    
    char *env_init[] = { "USER=unknown", NULL };
    execle("/bin/sh", "sh", "-c", command, (char *) 0, env_init);
    

实例代码

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    
    int main(int argc, char *argv[])
    {
        if (argc < 2) {
            printf("usage: %s param1 [param2 ...[param n]]\n", argv[0]);
            return -1;
        }
    
        char cmdbuf[128] = {0};
        snprintf(cmdbuf, sizeof(cmdbuf), "ls %s", argv[1]);
    
        char cmd[128] = {0};
        snprintf(cmd, sizeof(cmdbuf), argv[1]);
    
        puts("call system function:");
        system(cmdbuf);
    
        puts("\ncall popen function:");
        FILE *fp = popen(cmdbuf, "r");
        char readbuf[2048] = {0};
        fread(readbuf, 1, 2048, fp);
        puts(readbuf);
        pclose(fp);
    
        int pid = fork();
        if (pid > 0) {
            sleep(1);
        } else if (pid == 0) {
            //puts("call execl function:");
            //execl("/bin/sh", "sh", "-c", cmdbuf, NULL);
    
            //puts("call execl function:");
            //execl("/bin/ls", cmd, NULL);
    
            //puts("call execve function:");
            //execve("/bin/ls", argv, NULL);
    
            puts("call execvp function:");
            execvp("/bin/ls", argv);
        }
        return 0;
    }
    

测试结果，

![Untitled.png](https://image.3001.net/images/20230510/1683711354_645b657aa7d5e605c83f1.png!small)  
![Untitled
1.png](https://image.3001.net/images/20230510/1683711375_645b658f41e9fe686613f.png!small)  
![Untitled
2.png](https://image.3001.net/images/20230510/1683711389_645b659d4dd39e17a1cd7.png!small)![Untitled
3.png](https://image.3001.net/images/20230510/1683711391_645b659fae09eb5282627.png!small)![Untitled
4.png](https://image.3001.net/images/20230510/1683711396_645b65a41eb2cb2e8304f.png!small)![Untitled
5.png](https://image.3001.net/images/20230510/1683711399_645b65a77312d0f081e96.png!small)

一开始以为参考文章说的没错，自己测试也确实如文章示例一样，然后我试了一下别的playload发现可以绕过了，文章中说通过execve参数注入命令是不会解析执行的，跟自己测试的情况是对不上的；研究此的背景是，研发不采用我提供的修复方案，使用文章中所说的这种修复方式，因为不了解，所以学习一下；

![Untitled
6.png](https://image.3001.net/images/20230510/1683711405_645b65adb9b034136cdb0.png!small)  
那么如果使用execve的方式不能完全修复，针对此类情况有什么较好的修复方案呢；

# 命令执行修复方案

在执行命令前，对入参进行过滤，对敏感字符进行转义处理；

其实按理说，只要参数是用户可控的都应该这么处理；

然后有些特殊场景，无法过滤的，可以看一下能否写到配置文件中，然后在进行配置的方式，而不是通过拼接命令执行用户输入的内容；

# 命令执行常见的绕过方式

## 管道符

### “;”

WIndows：

![Untitled
7.png](https://image.3001.net/images/20230510/1683711427_645b65c3c0b2d1098c823.png!small)

Linux：

![Untitled
8.png](https://image.3001.net/images/20230510/1683711451_645b65db548e2e2a999d3.png!small)

### “|”

![Untitled
9.png](https://image.3001.net/images/20230510/1683711456_645b65e0f0c89c09c879f.png!small)

![Untitled
10.png](https://image.3001.net/images/20230510/1683711462_645b65e607b8cf2e15782.png!small)

### “||”

![Untitled
11.png](https://image.3001.net/images/20230510/1683711466_645b65ea8dbd6e02c2358.png!small)

![Untitled
12.png](https://image.3001.net/images/20230510/1683711470_645b65eec12c1e9c31c62.png!small)

### “&”

![Untitled
13.png](https://image.3001.net/images/20230510/1683711477_645b65f5182350076ea01.png!small)  
![Untitled
14.png](https://image.3001.net/images/20230510/1683711481_645b65f9745516d0568ed.png!small)

### “&&”

![Untitled
15.png](https://image.3001.net/images/20230510/1683711488_645b66001ce5bdc57e5d9.png!small)

![Untitled
16.png](https://image.3001.net/images/20230510/1683711492_645b6604b715e916bc329.png!small)

## linux下绕过空格

    
    
    {cat,flag.txt}
    cat${IFS}flag.txt
    cat$IFS$9flag.txt
    cat<flag.txt
    cat<>flag.txt
    ca\t fl\ag.txt
    

![Untitled
17.png](https://image.3001.net/images/20230510/1683711502_645b660e00ee595e9a901.png!small)

#### 参考

[命令注入漏洞介绍（下篇） -FreeBuf网络安全行业门户](https://www.freebuf.com/articles/web/276505.html)

[命令注入漏洞介绍（上篇） -FreeBuf网络安全行业门户](https://www.freebuf.com/articles/web/276503.html)

[C 语言执行 shell 命令的三种方式总结_lylhw13_的博客-CSDN博客_c
执行命令](https://blog.csdn.net/m0_47696151/article/details/119378730)

 **漏洞悬赏计划：涂鸦智能安全响应中心（https://src.tuya.com）欢迎白帽子来探索。**

