如果你做完了上次的例子，那么一定会学到许多东西，当然里面有些知识点我们并没有完全讲透彻，因为笔者认为该屏蔽的知识点就要屏蔽，讲的太多反而掩盖了一篇文章的核心原理。能够单独提出来写一篇文章的，都可以说能够代表某种思想，本文讲的也是另一种比较精妙的技巧。

## 原理

记得上两篇文章的两个例子，我们都是通过栈溢出，想办法覆盖掉返回地址，使得程序的流程跳转到我们构造好的后门函数，那么 stack
pivot，是劫持栈指针指向攻击者所能控制的内存处，然后再在相应的位置进行 ROP。

这时候我们有一个疑惑，既然有能够覆盖返回地址的方法不用，为什么要用这种方式呢，废话，肯定原来那种方式被限制了才有了这种劫持栈的方式。

## 实验

### 准备

题目：本次我们使用的是pwnable.kr里的一个题目simple-login，可以在这里下载到题目：<https://github.com/sonysame/pwnable.kr_simple-login>  
虚拟机：Ubuntu 17.04 32bit, gcc, socat  
宿主机：IDA7.0, Python + pwntools

### 分析

按照惯例，我们用IDA打开simple-login分析下题目的流程和溢出点，阅读程序伪代码，注释中已经详细解释，首先输入一个Base64，然后将其解码并将结果拷贝到了全局变量input中，最后再调用auth()函数进行验证，如果验证通过则执行correct()这个后门函数  
![](https://image.3001.net/images/20201123/1606097226_5fbb194a4b16e7c275553.jpg!small)

如下图，我们来看看auth()函数，发现首先将全局变量中解码好的结果通过memcpy拷贝到了缓冲区[ebp-0x8]中，然后计算了缓冲区[ebp-0x14]的md5值返回为字符串指针存储到s2中，并与固定字符串进行比对。经过我们的分析发现，并没有办法控制[ebp-0x8]的内容，进行md5哈希碰撞更是超越了本题的范围，想要覆盖函数返回的RIP但是输入的字节长度只能是12个字节以内，那怎么办呢？  
![](https://image.3001.net/images/20201123/1606097241_5fbb1959cd74f37934782.jpg!small)

我们不要悲观，仔细看看还能输入12个字节，并且能够覆盖掉原来保存的ebp，再继续分析，我们发现函数末尾有leave指令，我们知道leave指令等价于（mov
esp, ebp; pop
ebp），再往上一层函数main()，我们同样发现有leave的存在，那么我们就可以通过这两次leave来将程序劫持到我们想要劫持到地方去，画图表示一下：  
![](https://image.3001.net/images/20201123/1606097280_5fbb198034bd6f345a434.jpg!small)再详细描述下上图，请注意0x080492BA处的memcpy：我们的Payload在.bss节区的全局变量保存，该memcpy将全局变量input中的Payload拷贝到了当前栈帧的buf中（图左）；程序跳转之后跳转到了图右全局变量的位置。也就是我们将栈劫持到了全局变量的地址处。

### 调试

好了，讲了太多道理可能有点迷糊了，其实PWN说白了就是要多动手实践，我们不妨将上述思路直接构造为Payload，动态的将整个过程复现在我们面前，Payload如下

    
    
    #!/usr/bin/python3
    from pwn import *
    import base64 
    
    context.update(arch = 'i386', os = 'linux', timeout = 1)
    io = remote("127.0.0.1", 10001)
    
    payload = b"aaaa"               #padding
    payload += p32(0x08049284)      #system("/bin/sh")地址
    payload += p32(0x0811eb40)      #新的esp地址
    io.sendline(base64.b64encode(payload))
    io.interactive()
    io.close()
    

环境部分不多说和《第一个PWN》一样，我们下断点到0x080492BA处，走一步，如下图  
![](https://image.3001.net/images/20201123/1606097301_5fbb199598cda42a0b002.jpg!small)经过第一次leave后  
![](https://image.3001.net/images/20201123/1606097325_5fbb19ad7c990fea74ad7.jpg!small)经过第二次leave后，我们发现已经劫持成功，此时F9跑起来就可以获得Shell了。  
![](https://image.3001.net/images/20201123/1606097346_5fbb19c25b1a5686759da.jpg!small)有始有终，获取flag成功。  
![](https://image.3001.net/images/20201123/1606097363_5fbb19d3e839d56e59503.jpg!small)

## 小结

有些例子刚开始可能不好理解，但是一旦自己动手做一遍甚至好多遍，那就能够领略到其中的精髓了。

