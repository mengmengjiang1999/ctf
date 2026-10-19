## 一 、概述  

**网上已经有触发漏洞的POC和本地提权EXP，还有几篇从不同角度对漏洞进行阐述的文章(包括但不限于以下几篇)，但是阅读后对内存的构造和利用过程并不理解，因此自己尝试从新调试走一遍，主要记录调试过程及其他文章中未能读懂的部分，基本原理，提权原理及协议结构等不再重复：**

> <https://blog.zecops.com/vulnerabilities/exploiting-smbghost-> cve-2020-0796-for-a-local-privilege-escalation-writeup-and-poc/>
>
> <https://paper.seebug.org/1164/>
>
> <https://mp.weixin.qq.com/s/rKJdP_mZkaipQ9m0Qn9_2Q>

##  二、配置调试环境

需要配置双虚拟机windbg preview调试，配置内核调试(目标主机)：管理员权限启动powershell或cmd，执行如下命令：

    
    
    bcdedit /set dbgtransportkdnet.dll
    
        bcdedit /dbgsettings NETHOSTIP:调试机IP PORT:50000
    
        bcdedit /debug on

![](https://image.3001.net/images/20200428/1588045080_5ea7a518308f4.png!small)调试机上的windbg设置：

![](https://image.3001.net/images/20200428/1588045121_5ea7a5418391e.png!small)

加载符号表及：

    
    
    sympath SRV*C:\Symbols*http://msdl.microsoft.com/download/symbols

.reload重新加载符号表

Lml 查看加载了哪些符号表

Bp srv2!Srv2DecompressData+0xe0，此时找不到函数定义，需要.reload符号表

!sym noisy打开加载符号过程分析

.reload /f srv2.sys

windbg ERROR_INTERNET_CANNOT_CONNECT 是需要科学上网

发现错误，在system32下面寻找srv2.sys，但实际上该文件在system32/drivers，拷贝后再次加载：

##
![](https://image.3001.net/images/20200428/1588045152_5ea7a56078209.png!small)三、调试BOSD

造成漏洞的代码位于：

Srv2.sys的Srv2DecompressData ：

![](https://image.3001.net/images/20200428/1588045181_5ea7a57d0d822.png!small)

前面2个变量相加的时候没做检查造成溢出分配一个较小的内存导致使用该内存时出现问题。

调试时使用[ZecOps](https://github.com/ZecOps)公开的BOSD poc，打开mem文件后，查看函数调用情况：

![](https://image.3001.net/images/20200428/1588045432_5ea7a6782986f.png!small)查看内存错误情况：

![](https://image.3001.net/images/20200428/1588046821_5ea7abe5cf5b0.png!small)

查看出错的内存，非法使用一块未调试![](https://image.3001.net/images/20200428/1588045462_5ea7a6961b86e.png!small)![](https://image.3001.net/images/20200428/1588045467_5ea7a69ba6e3e.png!small)

对SrvNetAllocateBuffer附近下断点：

Add ecx,eax执行之前ecx=0xffffff，

![](https://image.3001.net/images/20200428/1588046879_5ea7ac1f653e0.png!small)执行后，ecx溢出为0x239

![](https://image.3001.net/images/20200428/1588046925_5ea7ac4da6072.png!small)搜一下发现win64传参有好几种不同的说法，同过IDA查看函数的参数：

![](https://image.3001.net/images/20200428/1588045527_5ea7a6d7b82da.png!small)再对比调试器中的参数：![](https://image.3001.net/images/20200428/1588046967_5ea7ac77a1b05.png!small)确认函数的传参顺序为ecx,edx,r8,r9.

##  四、LPE过程调试

依然使用[ZecOps](https://github.com/ZecOps)公开的 poc，但是为了方便观察内存数据变化，做了如下修改：

**![](https://image.3001.net/images/20200428/1588045568_5ea7a70095086.png!small)****分析如下关键点：**

![](https://image.3001.net/images/20200428/1588045606_5ea7a726a3d4c.png!small)多次调试分析结合其他文章的讲解后得出申请用于解压缩数据的内存结构如下：

![](https://image.3001.net/images/20200428/1588045621_5ea7a73518297.png!small)内存的申请过程也有点绕，调试后发现如下顺序：

![](https://image.3001.net/images/20200428/1588045635_5ea7a743ef4a2.png!small)最终使用nt!ExAllocatePoolWithTag申请了一块0x1278大小的内存，地址开始值可以抽象为0x0000：

![](https://image.3001.net/images/20200428/1588047019_5ea7acab1cc0f.png!small)

但是SrvNetAllocateBuffer成功后的返回值为0x0000+0x1150=0x1150（0xffffd888c577c150-0xffffd888c577b000=0x1150）：

![](https://image.3001.net/images/20200428/1588047099_5ea7acfbb9a06.png!small)

，同时在0x1150的0x18出存放了0x0000+0x50（内存可以开始使用的地址）的地址

![](https://image.3001.net/images/20200428/1588047155_5ea7ad33255c7.jpg!small)申请的内存从0x0050可以开始使用，前面部分用于放未压缩的数据，后面存放压缩的数据。未压缩数据大小来自smb数据包header中的offset（0x18）参数，那么SmbCompressionDecompress函数将压缩的数据解压到0x0050+offset（0x18）开始，如果大小能覆盖到0x1168那么就可以改写内存首地址，0x1168-0x0050-0x18=0x1100，看下poc代码：

![](https://image.3001.net/images/20200428/1588045696_5ea7a7805a112.png!small)

其中len（what）=0x18，因此写入的数据长度为0x1100。

在SmbCompressionDecompress调用前下断点，第4个参数为解压后存放数据的内容地址，0x0068（0x0000+0x50+offset(0x18)）：

![](https://image.3001.net/images/20200428/1588047198_5ea7ad5e435ca.jpg!small)

同时记录0x1168地址处的内容：

![](https://image.3001.net/images/20200428/1588047231_5ea7ad7f95f4d.jpg!small)

SmbCompressionDecompress调用完毕后，0x68处内容为poc想写入的0x41：

![](https://image.3001.net/images/20200428/1588047274_5ea7adaa18caf.jpg!small)

同时0x1168处地址也被改写为token地址（0xFfffc7093924e0a0）：

![](https://image.3001.net/images/20200428/1588047308_5ea7adcc3ff91.jpg!small)SmbCompressionDecompress完毕后只是处理了压缩的数据部分，未压缩的部分接下来用Memcpy函数拷贝到内存块的首部，长度为offset（0x18），但是此时0x1168存放的内存块首部地址已经被改为token地址（0xFfffc7093924e0a0），对应rcx。

![](https://image.3001.net/images/20200428/1588047356_5ea7adfc43df3.jpg!small)因此实现了对token的改写，提权成功。

 ***本文作者：kczwa1，转载请注明来自FreeBuf.COM**

