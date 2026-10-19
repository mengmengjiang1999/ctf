## 1.前言

golang有很多优点和缺点，但其中对于安全人员来说我觉得最大的优点就是 **可直接编译成机器码，不依赖其他库**
，因为我们经常要用到静态编译和交叉编译，当时我静态编译C
环境遇到了各种链接库先下载再编译再下载再编译的循环，现在都记忆犹新。基于这个优点特性，golang天生就适合开发RAT或者其他C/S架构软件。

但是同时这个优点也是一个非常致命的缺点，如果功能稍微多一点，客户端轻轻松松达到十几M甚至几十M，缩小了使用范围。

如果现在在搜索引擎搜索golang 和 shellcode，几乎所有的结果都是使用golang来做shellcode
loader制作免杀。而我在想另一个问题， **如何将golang程序变成体积非常小的shellcode** 。

先给出我目前已经实现的项目例子：<https://github.com/veo/vshell>

接下来我会给大家介绍一下我是如何实现的

## 2.PE to shellcode

<https://github.com/hasherezade/pe_to_shellcode>

这个项目利用了[ReflectiveDLLInjection](https://github.com/stephenfewer/ReflectiveDLLInjection)技术，可以将PE程序转换为shellcode，当然也包含了golang编译的PE程序。

使用方式也很简单：

    
    
    pe2shc.exe <path to your PE> [output path*]
    

就可以将任意exe程序转换为shellcode，

这里需要注意的是：转换后的文件还是一个exe文件，可以直接双击运行，但同时程序的内容也可以当做shellcode运行。

现在利用这个项目确实可以将golang程序很轻松的转换为shellcode，但是体积并没有减小，反而会增大1M， **目前并没有解决体积大的实际问题。**

## 3\. cobalt strike stager

我之前对cobalt strike这一块研究的较少，没有了解细致原理的情况下我就在思考一个问题，
**为什么msf和cs的shellcode可以这么短，但生成的exe却有接近500K，这么短的shellcode是如何完成这么多功能的** 。

后来我知道是使用了分段加载payload的技术，分为stage和unstage。

stage其实只是一个加载器，他需要从服务端拉取完整功能的payload在内存中运行。unstage是完整功能的payload，不需要再从服务端拉取payload。  
![image-20220914135612108.png](https://image.3001.net/images/20220914/1663138305_63217a01b95c2354c2f52.png!small)而cs生成的短的shellcode也只是加载器的shellcode，并不是完整payload的shellcode。

到这里，思路基本上就明确了。先将大的golang程序转换为shellcode，再用c/c++制作一个加载器stage去拉取这个远程的大的shellcode，完成golang程序至小体积shellcode的转换。

![image-20220914140448599.png](https://image.3001.net/images/20220914/1663138342_63217a26aabc9d2a4faa9.png!small)

## 4.stager的制作

stager其实就是通过远程下载主程序到内存中运行的加载器，像msf和cs的话他们都有http/https协议和tcp协议的stager，其中tcp协议用到了ws2_32.dll这个库，http用到了wininet.dll这个库。后续的话都有用到VirtualAlloc函数分配内存然后在内存运行。

本人开发的项目目前还没有http协议通讯的功能，所以我选择了wsock32这个库进行程序的编写，这个库本质上和ws2_32是类似甚至一样的，为了避开静态扫描所以选择了这个库。

首先，服务端我们得开辟一个下载的通道，通过socket发过来的前3个字节判断系统类型，返回不同的shellcode。

![image-20220914141630740.png](https://image.3001.net/images/20220914/1663138387_63217a53de69e4beb970b.png!small)  
后续还需要接收
ip和端口，对golang的大shellcode进行定制化的修改，也就是修改主程序内的配置信息，其中用到了网络字节序的知识，IP为4字节，端口为2字节，对字节序不了解的可以去搜一下。

![image-20220914141741451.png](https://image.3001.net/images/20220914/1663138418_63217a72cf8ace444ea0e.png!small)

网络字节序的转换这一步其实相当重要，这样就可以非常方便通过替换程序字节码的方式修改配置信息，生成不同配置的程序。

C++编写的starger按照协议 完成进行对接下载远端payload的功能，这里同样用到了网络字节序，也是为了方便生成不同配置的程序。  
![image-20220914143154335.png](https://image.3001.net/images/20220914/1663138457_63217a999483070a6b426.png!small)

通讯完成后就申请内存，下载payload至内存中，再执行。申请的内存一定要比远端主程序的shellcode要大，我这边远端的payload大概是20M，所以申请了30M内存进行写入。

![image-20220914143444736.png](https://image.3001.net/images/20220914/1663138495_63217abfe91fcd46a2e48.png!small)

Linux的话我是使用C语言进行编写的，Linux虽然有memfd_create也可以进行无文件落地加载elf程序，但是可能会有些兼容性的问题，而且Linux下杀毒软件较少，没必要做成无文件内存加载执行。所以采用了将远端payload下载到本地磁盘再执行的方案。

## 5.stager to shellcode

下一步要做的就是将C++编写的stager变成shellcode，

因为之前没有shellcode编写的基础，我使用了别人开源的一套shellcode生成框架
，<https://github.com/TonyChen56/ShellCodeFrame>，然后补习了下PE文件和shellcode的知识。

总结来说就是把用到的函数全部替换成shellcode编写的方式，然后就可以生成shellcode（说的比较简单，还是有点难度的）。

要找到函数对应的HASH，不能用双引号等等限制。

![image-20220914144446437.png](https://image.3001.net/images/20220914/1663138544_63217af09655e7d4349a5.png!small)

函数都构造好了，用自己构造后的函数再写一遍程序即可。

![image-20220914144540526.png](https://image.3001.net/images/20220914/1663138568_63217b08eb13d03de13ba.png!small)

## 6.完成功能

![image-20220914144800128.png](https://image.3001.net/images/20220914/1663141205_632185556d6458fb7413a.png!small)

