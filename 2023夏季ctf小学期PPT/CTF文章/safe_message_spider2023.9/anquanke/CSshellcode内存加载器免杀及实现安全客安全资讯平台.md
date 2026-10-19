# CS shellcode内存加载器免杀及实现

阅读量 **487613**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-16 14:30:41

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0170d551d564de9f8a.jpg)

> 相关代码以及免杀项目实现:  
> [https://github.com/crisprss/Shellcode_Memory_Loader](https://)

## 0x01.前言

前段时间看到小刚师傅的文章分享了几个加载器的相关实现,本篇文章在此基础上扩展了一些加载器实现的思路,并使用C#结合反射注入的方式实现发现免杀效果挺不错,最近用Golang结合内存加载以及其他免杀细节的方式重构了一遍,基本能过常见杀软和Defender,因此在这里记录一下内存免杀的思路以及相关实现细节,已将Golang实现上传至项目

## 0x02.何为内存加载免杀

免杀的方式多种多样,例如分离免杀、通过反射等方式,但其本质其实是一种特征码免杀技术,首先我们要知道
**特征码查杀恶意病毒是运用程序中某一段或几段64字节以下的代码作为判别程序病毒的主要依据**

分离免杀之所以能获得很好的效果就是因为shellcode加载器本身并不包含恶意代码，自然也不会包含恶意软件的特征码，而只有当加载器运行时，它才会从程序之外加载shellcode执行,通过这种方式能够有效避免基于特征码的查杀方式,当然也是偏静态的

那么基于shellcode的分离免杀,PE文件同样也能实现,将PE文件以某种加密方式进行存储后使用加载器读取PE文件并且解密,最后放入到内存当中执行,那么该程序被识别为恶意程序的可能性就大大降低了,实际上反射DLL注入也是基于这样,通过从内存中而不是在磁盘加载DLL,这样避免了文件落地

试想我们开辟一块内存,然后直接将shellcode写入到对应的内存中并且该内存是可读可写可执行的状态,那么这种方式太容易被AV所查杀,因此当我们如果是利用Windows自身提供的API来将加密或者封装好的shellcode写入到内存执行的话,将会大大增加查杀的难度

## 0x03.通过UUID方式实现内存加载

利用UUID向内存写入shellcode的方式早在17年就已经出现,不过在近一年中国内也是利用较多,俺在今年HVV中查到的样本还有利用UUID方式免杀的(x

###  3.1 UUID是什么

通用唯一识别码(UUID),是用于计算机体系中以识别信息数目的一个128位标识符，根据标准方法生成，不依赖中央机构的注册和分配，UUID具有唯一性。

> 这里注意一下UUID是一种标准而GUID是UUID标准的一种具体实现

###  3.2 如何转换UUID

Python的官方文档中记录了UUID转换的函数以及相关原型和用法  
[https://docs.python.org/3/library/uuid.html](https://)  
这里要注意的是`uuid.UUID`函数接受一个16个字节的byte,因为前文说过uuid是一个128位的标识符也就是16字节,当剩余字节数不满16个可添加`\x00`补充字节数

![](https://p1.ssl.qhimg.com/t01580a430d05133601.png)

如果我们要将shellcode转为UUID格式,注意就需要将全部的`shellcode`全部转化为uuid  
最后`shellcode`转为UUID的效果就是这样:

![](https://p4.ssl.qhimg.com/t0104f4ea740589a28b.png)

###  3.3 UUID如何写入内存

我们从MSDN上关注下这两个API函数  
 **1.UuidFromStringA**

![](https://p4.ssl.qhimg.com/t01fcb2654c46d7a98b.png)

我们需要提供两个参数,指向UUID字符串的指针,这里也就是我们之前转换后的UUID字符串,后一个参数可以理解为就是内存中的一块区域,将UUID转化成二进制写入到了这一块内存区域中,因此这一块内存通过转化后已经写入shellcode

> 注意该API是调用了动态链接库，因此我们在使用过程中也需要进行链接:  
>

因此利用的时候,首先我们需要创建一块内存,这里使用`HeapCreate`创建内存,然后申请内存的大小,并且设置该内存为可读可写可执行,注意申请内存的大小`len(shellcode)*16`

因为有多少UUID转化为二进制后就会有多少个16字节,因此申请内存时也需要注意这个问题

在实现过程中还需要考虑一些细节上的实现,例如在申请内存的API函数选择上,传统的`VirtualAlloc/HeapAlloc`等方式可能已经被杀软Hook,在这里我经过多次比对,在`RtlCopyMemory`和`ZwAllocateVirtualMemory`中选择了后者,使用内核层面Zw系列的API，绕过杀软对应用层的监控

![](https://p3.ssl.qhimg.com/t015257794298b6367b.png)

这里比较粗暴的设置了申请内存的大小为`0x100000`,然后我们要对每一个UUID逐个调用`UuidFromStringA`函数写入到我们申请的内存中

> 注意每一次UUID的转换都会伴随内存地址都会增大16字节  
>

###  3.4 如何执行内存中的shellcode

其实执行的方式也有多种多样,一方面我们可以直接调用Golang的syscall包从底层来直接执行

> syscall包包含一个指向底层操作系统原语的接口。

尽管 Go 语言具有cgo这样的设施可以方便快捷地调用 C 函数，但是其还是自己对系统调用进行了封装，以`amd64`架构为例， Go
语言中的系统调用是通过如下几个函数完成的：

    
    
    // In syscall_unix.go
    func Syscall(trap, a1, a2, a3 uintptr) (r1, r2 uintptr, err Errno)
    func Syscall6(trap, a1, a2, a3, a4, a5, a6 uintptr) (r1, r2 uintptr, err Errno)
    func RawSyscall(trap, a1, a2, a3 uintptr) (r1, r2 uintptr, err Errno)
    func RawSyscall6(trap, a1, a2, a3, a4, a5, a6 uintptr) (r1, r2 uintptr, err Errno)
    

在这里介绍另外一种通过函数回调方式执行shellcode的函数`EnumSystemLocalesA`

![](https://p0.ssl.qhimg.com/t0181f71cdba94d820f.png)

**细节1**  
为了避免直接调用syscall,我们可以通过利用这种较为冷门的API函数来执行内存中的shellcode同样可以避开杀软的监控,通过callback方式来触发执行shellcode的方式可以参考:  
 **<https://www.freebuf.com/articles/web/269158.html>**

    
    
    1.EnumTimeFormatsA
    2.EnumWindows
    3.EnumDesktopWindows
    4.EnumDateFormatsA
    5.EnumChildWindows
    6.EnumThreadWindows
    7.EnumSystemLocales
    8.EnumSystemGeoID
    9.EnumSystemLanguageGroupsA
    10.EnumUILanguagesA
    11.EnumSystemCodePagesA
    12.EnumDesktopsW
    13.EnumSystemCodePagesW
    

其中的函数在MSDN中也有对应的说明和其他方法的实现,例如以`EnumSystemLocalesA`为例,就有`EnumSystemLocalesW`和`EnumSystemLocalesEx`均可以替代进行回调

![](https://p1.ssl.qhimg.com/t014a58047c9a3a9307.png)

最后回调即可:

![](https://p3.ssl.qhimg.com/t0120e711bafea3ce5c.png)

最终的免杀效果尚可

![](https://p4.ssl.qhimg.com/t0125f7bd66b69643fd.png)

![](https://p0.ssl.qhimg.com/t0112d93970e81ecb5f.png)

免杀项目实现已上传到Github上

## 0x04.利用MAC实现内存加载

我们知道在这里实现内存加载的一种方式就是去寻找各种API,MSDN上提供了各式各样的API,如果某一种API函数实现了某种可逆的变形并且最终写入到二进制指针当中,那么也就实现了内存加载

###  4.1 MAC是什么

MAC地址也叫物理地址、硬件地址，由网络设备制造商生产时烧录在网卡的EPROM一种闪存芯片，通常可以通过程序擦写。IP地址与MAC地址在计算机里都是以二进制表示的，IP地址是32位的，而MAC地址则是48位（6个字节）的

###  4.2 如何将shellcode转为MAC

`RtlEthernetStringToAddressA和RtlEthernetAddressToStringA`便是其中的一种  
分别从MSDN中查看两个API函数的相关信息:  
 **RtlEthernetAddressToStringA函数原型**

    
    
    NTSYSAPI PSTR RtlEthernetAddressToStringA(
      const DL_EUI48 *Addr,
      PSTR           S
    );
    

![](https://p5.ssl.qhimg.com/t01da178b2a5632e24a.png)

>
> 注意6个字节转换一个mac值，\x00是一个字节,当使用该函数后6个字节会变成18-1(`\x00`)个字节,即17个字节,当剩余字节数不满6个需要添加`\x00`补充字节数，必须将全部的shellcode全部转化为mac值

因此需要每隔六个字节进行一次转换，内存地址递增17,直到转换完所有的shellcode为止

![](https://p3.ssl.qhimg.com/t01389f2895e472061c.png)

针对转MAC的方式其实是这样转换的:

    
    
    \xfc\x48\x83\xe4\xf0\xe8
    =>
    FC-48-83-E4-F0-E8
    

因此将shellcode转为MAC也可以不用上面的写法,不过在这里就还是使用小刚师傅的脚本利用原生Win API转shellcode

###  4.3 如何将MAC还原为shellcode写入内存

前文提到的两个函数其实是一个可逆的过程,因此我们只要使用`RtlEthernetStringToAddressA`便可以将MAC值从字符串形式转为二进制格式

    
    
    FC-48-83-E4-F0-E8
    =>
    \xfc\x48\x83\xe4\xf0\xe8
    

![](https://p5.ssl.qhimg.com/t01dac1d5879f63eace.png)

这里需要提供3个参数,这里我们第一二个参数都为指向shellcode转化为MAC后的指针即可,第三个参数传入接收的内存指针

那么我们同样需要申请内存中一块可读可写可执行的空间,在这里我选择另外一种方式

为了逃避检测申请内存的行为，可以采用 **渐进式加载模式**
，也就是申请一块可读可写不可执行的内存，再使用`VirtualProtect`函数将内存区块设置为可执行，从而规避检测。

**细节2**  
在这里用小刚师傅分享的`AllocADsMem`函数来替代`HeapAlloc`申请指定大小的内存空间,因为类似`VirtualAlloc/HeapAlloc`等API被杀软Hook的情况很常见,利用冷门的API能够有效避开杀软的探测

![](https://p0.ssl.qhimg.com/t01d4f96e942c906e22.png)

参数是要分配的内存大小，成功调用则返回一个指向已分配内存的非NULL指针，
如果不成功，则返回NULL,该内存空间是可读可写不可执行的,因此我们还需要调用`VirtualProtectEx`来实现将该内存空间设置为可执行

因此写入内存的步骤也就比较清晰了:

  * 1.使用AllocADsMem申请len(shellcode)*6的空间大小的内存
  * 2.对每一个MAC字符串都调用`RtlEthernetStringToAddressA`写入到刚申请的内存中
  * 3.每一次调用结束后写入一个mac二进制需要将指针移动6个字节,内存地址都会增加6个字节
  * 4.调用`VirtualProtectEx`将该区域的内存设置为可执行

![](https://p2.ssl.qhimg.com/t0106b14311bdb60dd5.png)

最后同样可以使用回调函数执行内存,这里使用`EnumSystemLocalesW`

**细节3**  
在今年DEFCON
29中介绍了golang的一些作为红队使用语言的优势，议题主要介绍的是题主自己用golang实现的一系列红队工具，外加一些其他的补充,其中就有从内存中加载DLL动态链接库,个人认为就是类似于反射DLL注入的方式,然后进行调用，相当于实现了自己的`LoadLibrary`而不需要调取系统的`LoadLibrary`  
 **<https://github.com/Binject/universal/>**  
在实现中我也用到了该项目:

    
    
    var ntdll_image []byte
    ntdll_image, err = ioutil.ReadFile("C:\\Windows\\System32\\ntdll.dll")
    ntdll_loader, err := universal.NewLoader()
    ntdll_library, err := ntdll_loader.LoadLibrary("main", &ntdll_image)
    _, err = ntdll_library.Call("RtlEthernetStringToAddressA", uintptr(unsafe.Pointer(&u[0])), uintptr(unsafe.Pointer(&u[0])), addrptr)
    

通过上述代码避免了直接使用`Loadlibrary`或者`NewLazySystemDLL`懒加载的方式来导入动态链接库,这样杀软并不会在导入表中也检测不到我们使用了`RtlEthernetStringToAddressA`函数

最终的免杀效果和UUID类似,虽然VT上显示会被微软查杀,但测试的时候最新Windows
Defender也能过,不是很理解,但是个人认为免杀效果比UUID可能好点

![](https://p0.ssl.qhimg.com/t015b417af06390719d.png)

![](https://p5.ssl.qhimg.com/t01698a383ab46fea5b.png)

## 0x05.利用Ipv4方式实现内存加载

既然Windows中存在处理MAC的相关函数,笔者因此想到肯定存在IPV4的相关处理函数,我们定位到MSDN关于`IP2String.h`的相关介绍上:

![](https://p1.ssl.qhimg.com/t01abb03e039e4677f9.png)

###  5.1 IPV4是什么

IPv4是一种无连接的协议，操作在使用分组交换的链路层（如以太网）上。此协议会尽最大努力交付数据包，意即它不保证任何数据包均能送达目的地，也不保证所有数据包均按照正确的顺序无重复地到达。

**IPv4使用32位（4字节）地址** ，因此地址空间中只有4,294,967,296（232）个地址。

###  5.2 如何将shellcode转为Ipv4格式

因此可以看到在这里我们同样可以利用IPV4的方式实现内存加载，同样使用到了两个API函数:`RtlIpv4AddressToStringA/RtlIpv4StringToAddressA`  
第一个函数的函数原型如下:

    
    
    NTSYSAPI PSTR RtlIpv4AddressToStringA(
      [in]  const in_addr *Addr,
      [out] PSTR          S
    );
    

![](https://p0.ssl.qhimg.com/t01b36e7189113424ae.png)

此函数可以将二进制转化为IPV4的格式

>
> 注意4个字节转换一个Ipv4值，\x00是一个字节,当使用该函数后4个字节会变成16-1(`\x00`)个字节,即15个字节,当剩余字节数不满4个需要添加`\x00`补充字节数，必须将全部的shellcode全部转化为Ipv4值

![](https://p2.ssl.qhimg.com/t01990ad256c2233c6a.png)

当使用如上图所示代码,我们便能够将byte类型的shellcode转化为Ipv4格式:

    
    
    b'\xfc\x48\x83\xe4\'
    =>
    252.72.131.228\x00
    

注意这里如果没有到15个字节则会以自动以`\x00`进行补充,最后一个字节即第16个字节是字符串结束符

###  5.3 如何将Ipv4还原为shellcode写入内存

这里就是使用到了第二个API函数:`RtlIpv4StringToAddressA`  
函数原型如下:

    
    
    NTSYSAPI NTSTATUS RtlIpv4StringToAddressA(
      [in]  PCSTR   S,
      [in]  BOOLEAN Strict,
      [out] PCSTR   *Terminator,
      [out] in_addr *Addr
    );
    

![](https://p0.ssl.qhimg.com/t01ef686519f08c5f71.png)

因此这里还原写入shellcode的步骤为:

  * 1.申请一片内存,其内存大小应该是`len(shell_ipv4)*4`,因为该函数还原后每一个IPv4就会变成对应的4个字节
  * 2.通过`RtlIpv4StringToAddressA`将每次的4个字节写入到内存中,此时内存在递增4个字节
  * 3.使用`VirtualProtectEx`将内存设置为可执行

![](https://p3.ssl.qhimg.com/t0170576ddac6d25ce0.png)

**细节4**  
这里使用了比较简单的反沙箱技术,当今大多数真实机具有4GB以上的RAM,我们可以检测RAM是否大于4GB来判断是否是真实的运行机器,同样大多数真实机拥有4核心cpu，许多在线检测的虚拟机沙箱是2核，我们可以通过核心数来判断是否为真实机器或检测用的虚拟沙箱，当然反沙箱还有更多高端操作以及其他判断源，例如可以从系统开机时间、临时文件夹的文件数目

例如我们编写如下一个程序,将收集好的信息通过`socket`回调给服务器,然后服务器监听对应的端口即可:

我们主要获取CPU核心数和物理内存数,以某沙箱为例:

可以看到该沙箱的环境为1核2G,并且其桌面都是一些随机命名的检测文件等,因此这就可以作为我们反沙箱的要点:

这里我们判断4核2G之下就为虚拟机,如果是虚拟机我们就直接退出,不在继续进行相关操作,对于一般的沙箱而言也能够有效避免被沙箱获得IP或者网络通信情况

使用该内存加载方式和前两者区别同样不大,市面上主流杀软都能够过,免杀效果尚好。

## 0x06.结语

最后,有心的师傅们可能注意到MSDN中不仅提供了IPv4的相关转换函数,IPv6自然也存在对应的转换函数,因此利用IPv6同样也能够进行内存加载达到免杀的目的,不过在这里有兴趣的师傅可以自己去实现,最后免杀项目使用Golang进行开发,C#实现效果也很好,不过这里就不再展开赘述,只是分享内存免杀的一种思路和一些免杀细节的实现

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Crispr** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/262666](/post/id/262666)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [渗透测试](/tag/渗透测试)
  * [红蓝对抗](/tag/红蓝对抗)
  * [免杀](/tag/免杀)

 **+1** __15赞

 __收藏

![](https://p4.ssl.qhimg.com/t01f727a088f341ab8f.png) Crispr

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

