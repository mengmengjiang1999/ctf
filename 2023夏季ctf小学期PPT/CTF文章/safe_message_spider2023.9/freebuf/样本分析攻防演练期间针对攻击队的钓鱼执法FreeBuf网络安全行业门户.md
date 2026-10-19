### **X达OA反序列化命令执行漏洞利用工具样本分析**

攻防演练期间，矢安科技安全研究部在社交媒体、代码托管平台、公众号、IM群组等渠道检测到大量漏洞利用样本。其中部分样本“换汤不换药”，依然使用历史payload，部分样本编译为exe，其中捆绑了后门。

在攻防演练接近尾声时，防守成员利用部分攻击成员“最后冲刺”的心理，公开投递了部分捆绑后门的样本。现针对名为“X达OA-list接口反序列化命令执行漏洞.exe”的样本进行分析。

##  ** **基本信息：****

 **名** **称**

|

 **X** **达** **OA-list** **接口反序列化命令执行漏** **洞**  
  
---|---  
  
MD5

|

faecf40069ebc6460ecf49f661914c15  
  
壳

|

无壳  
  
大小

|

17.5 KB  
  
位数

|

64位  
  
#  ** **样本分析**** ** **：****

首先对样本进行简单分析，查看样本字符串信息：

![1659925719_62f074d7269c7bdb68876.gif!small](https://image.3001.net/images/20220808/1659925719_62f074d7269c7bdb68876.gif!small)![1659925729_62f074e1bcc8344ab3531.gif!small](https://image.3001.net/images/20220808/1659925729_62f074e1bcc8344ab3531.gif!small)

发现有创建管道、创建线程的函数，并且格式化的字符串信息。

#  ** **动态运行：****

在虚拟机中动态运行查看效果：

![1659925786_62f0751aceab57d048653.gif!small](https://image.3001.net/images/20220808/1659925786_62f0751aceab57d048653.gif!small)

运行后没有界面反馈，查看其运行的基本信息：![1659925800_62f07528316c299e82210.gif!small](https://image.3001.net/images/20220808/1659925800_62f07528316c299e82210.gif!small)

根据上面创建线程的函数，判断exe可能创建线程进行一些操作![1659925814_62f075366c110e2e01d16.gif!small](https://image.3001.net/images/20220808/1659925814_62f075366c110e2e01d16.gif!small)

通过443端口访问远程地址，可能有如下可能

1.下载新的样本执行

2.样本连接C2服务器

#  ** **调试分析：****

64位程序放入IDA中进行分析：进入主函数查看：![1659925866_62f0756aa00b27d6b3da3.gif!small](https://image.3001.net/images/20220808/1659925866_62f0756aa00b27d6b3da3.gif!small)

主函数较简单，经分析得知sub_401795()为关键函数；

进入关键函数sub_401795()分析，![1659925879_62f0757756d13ce746d71.gif!small](https://image.3001.net/images/20220808/1659925879_62f0757756d13ce746d71.gif!small)

首先可以看到，第一个红框中定义了几位字符，并结合sprintf函数的格式化字符串信息可知，此处是创建管道的字符串信息，并且管道名称MSSE-xxx-server，其 ‘xxx’ 是通过GetTickCount()函数获取开机以来的时间，并和0x26AA运算后得到的结果，作为XXX的名字。

接着创建了线程，线程的起始地址为sub_401685()，跟进函数查看：![1659925892_62f075847dbd4e83660b6.gif!small](https://image.3001.net/images/20220808/1659925892_62f075847dbd4e83660b6.gif!small)

unk_404014()函数:![1659925907_62f07593700a345aabe51.gif!small](https://image.3001.net/images/20220808/1659925907_62f07593700a345aabe51.gif!small)

nNumberOfBytesToRead()函数：![1659925918_62f0759e0e5554f8ae8e2.gif!small](https://image.3001.net/images/20220808/1659925918_62f0759e0e5554f8ae8e2.gif!small)

为dword数据，值为0x39F，进入sub_4015D0()函数查看，可以看到其通过CreateNamePipeA()函数创建管道：![1659925932_62f075ac5635f0dc0a216.gif!small](https://image.3001.net/images/20220808/1659925932_62f075ac5635f0dc0a216.gif!small)

其中ConnectNamedPipe()函数来维持管道，直到遇见CreateFile()函数，该函数才会返回非零的值，后面WriteFile()函数才会执行，否则该线程一直等待：![1659925945_62f075b9a59c31d69f7e4.gif!small](https://image.3001.net/images/20220808/1659925945_62f075b9a59c31d69f7e4.gif!small)

从后面WriteFile()函数可以看到，之前数据通过管道进行传输，而

nNumberOfBytesToWrite()则为一次传输的数据量。

继续往下分析其他函数：![1659925962_62f075cae08ccddc1b07c.gif!small](https://image.3001.net/images/20220808/1659925962_62f075cae08ccddc1b07c.gif!small)

进入sub_401742()函数：

![1659925987_62f075e3a128ccd474d5a.gif!small](https://image.3001.net/images/20220808/1659925987_62f075e3a128ccd474d5a.gif!small)

在行x64dbg中调试发现，此处Sleep函数执行后，刚刚的线程才开始执行，先分析sub_4016A2()函数：![1659926000_62f075f0243d72f8ac58f.gif!small](https://image.3001.net/images/20220808/1659926000_62f075f0243d72f8ac58f.gif!small)

如前文所述，遇到CreateFileA函数管道开始传输的数据，在这里接受管道传输的数据。

最后分析sub_40152E()函数：![1659926014_62f075fe7f9ec410cb9e8.gif!small](https://image.3001.net/images/20220808/1659926014_62f075fe7f9ec410cb9e8.gif!small)

v0为通过malloc()函数分配的内存指针，指向接收到的未知数据
nNumberOfBytesToRead()值为39F，进入unk_404008()函数：![1659926024_62f0760896763ae38f54c.gif!small](https://image.3001.net/images/20220808/1659926024_62f0760896763ae38f54c.gif!small)![1659926030_62f0760eb3063a6c62bab.gif!small](https://image.3001.net/images/20220808/1659926030_62f0760eb3063a6c62bab.gif!small)

可以看到将接收到的未知数据：

第一位和 ‘4’ 异或；

第二位和 ‘0x3C’ 异或第三位和 ‘0x97’ 异或第四位和 ‘0xCE’ 异或；

…

依次循环，将数据进行解密，解密后的数据地址就是下面CreateThread()函数的线程地址；

以上功能基本分析完成，但是发现程序有主动联网行为，访问了远程IP地址，可知是在创建的线程中执行。

#  ** **调试线程：****

由上面静态分析可知，创建线程的时候会用到函数VirtualAlloc()创建内存空间，用于存储解密后的数据在x64dbg中，查找跨模块调用，可以看到VirtualAlloc()函数：![1659926061_62f0762de59a5021aff33.gif!small](https://image.3001.net/images/20220808/1659926061_62f0762de59a5021aff33.gif!small)

在这里下断点，F9执行，F8步过VirtualAlloc()函数：![1659926076_62f0763cd3a9a11415e2d.gif!small](https://image.3001.net/images/20220808/1659926076_62f0763cd3a9a11415e2d.gif!small)

函数VirtualAlloc()返回值在rax寄存器中，内存的空间地址是0x20000转到0x20000地址，下硬件执行断点，F9执行![1659926086_62f076467d49846c08a41.gif!small](https://image.3001.net/images/20220808/1659926086_62f076467d49846c08a41.gif!small)

程序在0x20000地址处停止，前面一部分汇编代码是检测字符串是否完成，检测PE标识是否被修改：![1659926100_62f0765415d9c4818be31.gif!small](https://image.3001.net/images/20220808/1659926100_62f0765415d9c4818be31.gif!small)

该部分用于从各dll文件中获取需要的API地址，查找到对应函数后，由0x200C4地址处的jmp
rax指令调用函数，由于不是使用call指令，所以返回时会直接返回到下面call
rbp指令的下一条指令，其中rbp的值都是0x2000A：![1659926111_62f0765f4ba0198187fef.gif!small](https://image.3001.net/images/20220808/1659926111_62f0765f4ba0198187fef.gif!small)

每个call
rbp指令都会查找API并执行执行的过程中可得到IP地址，![1659926126_62f0766e8dbdf5830f85b.gif!small](https://image.3001.net/images/20220808/1659926126_62f0766e8dbdf5830f85b.gif!small)

依次会执行一下函数，

LoadLibraryExA 加载了wininet.dll

InternetOpenA 初始化应用程序对 WinINet 函数的使用

InternetConnectA 打开47.113.192.46:443站点的http会话

HttpOpenRequestA 创建http请求句柄，请求 _https://47.113.192[.]46:443/OuET_

InternetSetOptionA 设置 Internet 选项  
  
---  
  
![1659926150_62f076863d9a74a12debe.gif!small](https://image.3001.net/images/20220808/1659926150_62f076863d9a74a12debe.gif!small)

HttpSendRequestA 将指定的请求发送到 HTTP
服务器：![1659926162_62f076928c32a35793dc1.gif!small](https://image.3001.net/images/20220808/1659926162_62f076928c32a35793dc1.gif!small)

从http请求到的数据读取，并存储到VirtualAlloc申请到的内存里，之后程序会跳转到0x37D0000区执行，先是检测个别字符串的完整度，然后查找MZ和PE标志，随后会查找以下函数的地址：

GetModuleHandleA() 检索指定模块的模块句柄。该模块必须已由调用进程加载。

GetProcAddress() 从指定的动态链接库 (DLL) 中检索导出函数(也称为过程)或变量的地址。

LoadLibraryA() 将指定的模块加载到调用进程的地址空间中。指定的模块可能会导致加载其他模块。

LoadLibraryExA() 将指定的模块加载到调用进程的地址空间中。指定的模块可能会导致加载其他模块。

VirtualAlloc() 在调用进程的虚拟地址空间中保留、提交或更改页面区域的状态。此函数分配的内存自动初始化为零。

VirtualProtect() 在调用进程的虚拟地址空间中更改对已提交页面区域的保护。  
  
---  
  
可以看到查找了6个函数，首先使用VirtualAlloc()分配了一块内存空间，然后将上面找到的MZ和PE标志对应的PE文件存入该内存空间中。使用LoadLibraryExA()函数加载KERNEL32.DLL动态库，并且使用GetProcAddress()获取函数的地址，获取的函数地址会存入PE文件中，修复后为dll文件，将dll文件dump出来进行分析：![1659926231_62f076d70b0a8d6e7b8da.gif!small](https://image.3001.net/images/20220808/1659926231_62f076d70b0a8d6e7b8da.gif!small)

#  ** **DLL**** ** **文件分析**** ** **：****

在x64调试中发现，修复完dll文件后会执行该文件的一个导出函数：![1659926251_62f076eb9d13d2a7d56ff.gif!small](https://image.3001.net/images/20220808/1659926251_62f076eb9d13d2a7d56ff.gif!small)

跟进导出函数查看：![1659926260_62f076f492fee194626f5.gif!small](https://image.3001.net/images/20220808/1659926260_62f076f492fee194626f5.gif!small)

导出函数里面调用了_DllMainCRTStartup()函数，继续跟进：![1659926271_62f076ff2bb3254971535.gif!small](https://image.3001.net/images/20220808/1659926271_62f076ff2bb3254971535.gif!small)

可以看到调用了DLLMain()函数：![1659926285_62f0770d9b9e20832d183.gif!small](https://image.3001.net/images/20220808/1659926285_62f0770d9b9e20832d183.gif!small)

主要的远控操作在sub_225CA74()中：![1659926297_62f07719407ddaf633415.gif!small](https://image.3001.net/images/20220808/1659926297_62f07719407ddaf633415.gif!small)

sub_2263A30()函数中获取了系统的版本信息以及主机的相关信息。

主要查看网络操作sub_255DF30函数：

![1659926318_62f0772e0a486200e7019.gif!small](https://image.3001.net/images/20220808/1659926318_62f0772e0a486200e7019.gif!small)

首先函数sub_22653C8()中获取了Cookie的信息，图如下：![1659926329_62f07739d5f8c7dab852d.gif!small](https://image.3001.net/images/20220808/1659926329_62f07739d5f8c7dab852d.gif!small)

访问该服务器，从服务器中接收数据（远控指令），执行相应的远控操作。

但是因为截止撰文时远控服务器并没有开启，无法接收远控的指令，只能静态分析一些远控的操作。

文件操作：![1659926341_62f0774525588c422153c.gif!small](https://image.3001.net/images/20220808/1659926341_62f0774525588c422153c.gif!small)

通过循环获取文件目录：

进程操作：![1659926354_62f07752df1210a9f8ecb.gif!small](https://image.3001.net/images/20220808/1659926354_62f07752df1210a9f8ecb.gif!small)![1659926359_62f077579de3c91652c30.gif!small](https://image.3001.net/images/20220808/1659926359_62f077579de3c91652c30.gif!small)

通过循环输出进程列表中的所有进程信息以及一些常见的远控操作，典型的Cobalt Strike行为。

#  ** **总结**** ** **：****

攻击队成员迫切想要得分获取成果，但也要在钓鱼防守方成员的时候防范来自防守方的投毒。

