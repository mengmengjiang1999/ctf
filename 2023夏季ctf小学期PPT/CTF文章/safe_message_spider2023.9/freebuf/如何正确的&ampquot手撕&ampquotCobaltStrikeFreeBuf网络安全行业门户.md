## 00 背景

众所周知， **Cobalt Strike** 是一款在渗透测试活动当中，经常使用的C2(Command And
Control/远程控制工具)。而Cobalt
Strike的对抗是在攻防当中逃不开的话题，近几年来该领域对抗也愈发白热化。而绝大多数厂商的查杀，也是基于内存进行，然而其检测方式的不当，导致非常容易被Bypass，包括但不限于

> • 扫描RWX内存(正常进程中的Private Data区域一般没有执行权限)  
> •DOS头  
> • 扫描特征  
> • 字符串特征  
> •ReflectiveLoader  
> • beacon.x64.dll  
> •...  
> • Beacon Config(使用前)  
> • ...

上面列出的这些方法，实际都能绕过，核心原因是，去掉这些特征可以不影响 **Cobalt Strike Beacon** 的正常运行

## 01 BeaconEye核心原理

近日有安全人员开源了一款检测Cobalt Strike Beacon的工具，名字叫 **BeaconEye** ，他的核心原理是通过扫描 **Cobalt
Strike** 中的内存特征，并进行Beacon
Config扫描解析出对应的Beacon信息，项目地址是https://github.com/CCob/BeaconEye。该项目的最大的特点是绕过难度较高(相比于其他同类型扫描工具)，接下来对工具的核心原理进行剖析。

## 02 Beacon.dll

Cobalt Strike的shellcode，实际都是通过反射加载的方式加载Beacon.dll，而Beacon.dll中存在Beacon
Config配置信息(主要定义通信目标/通信方式等)，在Cobalt Strike中对应的Resource是sleeve/beacon.dll

![image](https://image.3001.net/images/20210910/1631264077_613b1d4d0af1621924abb.jpg!small)

## 03 Beacon Config Generate

Beacon Config的生成在BeaconPayload类的exportBeaconStage函数中

![image](https://image.3001.net/images/20210910/1631264101_613b1d6577298c9efab98.png!small)

这上面指向的Settings结构体就是Beacon Config，比如var1，它代表实际通信的端口

![image](https://image.3001.net/images/20210910/1631264122_613b1d7ad663e3c0f28ee.png!small)

最终Cobalt Strike会将Settings转化为bytes数组，然后使用固定的密钥进行Xor,并对剩余空白字段填入随机字符

![image](https://image.3001.net/images/20210910/1631264913_613b2091592a00b9f577a.png!small)

最后将生成的beacon.dll嵌入到最终的PE文件中

![image](https://image.3001.net/images/20210910/1631264889_613b2079e037e828d8820.png!small)

## 04 Beacon Struct

Settings的Add系列函数，如AddShort，并不是简单的将Short类型直接追加到bytes数组中，而是追加了一个结构体

![image](https://image.3001.net/images/20210910/1631264869_613b2065092bdc07dc625.png!small)

第一个字段是index，第二个是type(short/int/...)，第三个是length，第四个则是关键的value值，因此根据这个结构即可解析在内存或在文件中的Beacon
Config

## 05 BeaconEye规则

接下来让我们看一下BeaconEye的yara规则

![image](https://image.3001.net/images/20210910/1631264846_613b204e69bd0d6d053bf.png!small)

32位的Beacon Config规则长这个样子，如果你认真阅读了前文一定会觉得很疑惑，因为按照Java当中的结构，它应该分为四个部分

`[ ID ] [ DATA TYPE ID ] [ LENGTH OF VALUE ] [ VALUE ]`

但是实际的yara规则却没有办法对上java中的Beacon Config结构，说明Beacon.dll在装载的过程中，
**并没有直接将上述数据memcpy分配到堆中** ，接下来让我们通过对beacon.dll进行逆向

![image](https://image.3001.net/images/20210910/1631264809_613b2029bee0b272b8e36.png!small)

通过dllmain跟进，发现有一个关键函数，里面首先解密了先前Beacon Config的加密数据，然后遍历Beacon
Config。首先是在拿到了Type之后， **直接往堆中分配的内存写入WORD长度的Type，然后根据Type进行判断，case
1对应Short，case 2对应Int，case 3对应Data，所以实际上最终的Beacon Config的结构是**

`DWORD DWORD [ DATA TYPE] [ VALUE ]`

因此最终的yara规则可以解读如下

![image](https://image.3001.net/images/20210910/1631264769_613b2001cf034633cdb32.png!small)

??代表通配符，实际匹配的就是beacon.dll当中真正的config结构体，到这一步，后面的结构体还原就是顺水推舟了

## 06 Bypass BeaconEye

而近日有安全人员提出在执行Cobalt Strike的Shellcode之前，通过调用 **SymInitialize**
即可实现Bypass，本着好奇的态度，笔者继续对原理进行了深入的探究

## 07 SymInitialize作用

根据官方文档的描述，SymInitialize的作用是用来初始化进程符号句柄的

![image](https://image.3001.net/images/20210910/1631264731_613b1fdbc676ce3d83e9d.png!small)

它的传参有三个

> • hProcess: 代表进程句柄
>
> • UserSearchPath: 符号文件的搜索路径
>
> • fInvadeProcess: 是否对进程中已加载的每个模块调用SymLoadModule64函数
>
> 仅仅从传参来看，并没有办法明确的判定为什么能Bypass，因此我们使用windbg进行对比抓取

## 08 Windbg调试

接下来我们分别对调用了SymInitialize和没有调用SymInitialize的Cobalt Strike的Beacon进行windbg调试，
**由于我们知道BeaconEye扫描的是堆内存，因此我们直接对比两者的堆内存**

![image](https://image.3001.net/images/20210910/1631264656_613b1f9050603a1367298.png!small)

![image](https://image.3001.net/images/20210910/1631264635_613b1f7b3d52d34541569.png!small)

从上面两张图我们可以很清晰的看到，这两个进程在堆内存中的最大的区别是，使用了SymInitialize的第一个heap区域，比没有使用SymInitialize的第一个heap区域，多了几个Segment，那为什么多了几个Segment就导致BeaconEye无法扫描呢?

## 09 Windows中Heap结构

使用windbg，执行如下命令，查看一下具体Heap的结构  
`dt !_heap`

![image](https://image.3001.net/images/20210910/1631264600_613b1f5844c72c63c84d9.png!small)

可以看到heap结构的字段非常的多，这里重点关心3个字段

> • SegmentListEntry: 存储堆段地址的双向链表
>
> • BaseAddress: 堆段起始地址
>
> • NumberOfPages: 页面的数量

那一个堆段的范围是怎么计算出来的呢?非常简单

`BaseAddress ~ BaseAddress + NumberOfPages * PageSize`

而每一个BaseAddress以及NumberOfPages，都仅仅只针对当前的堆段

## A NtQueryVirtualMemory

BeaconEye中查询内存信息实际调用的是 **NtQueryVirtualMemory** ，我们都知道Nt系列函数是Windows中
**Ring3** 进入 **Ring0** 的入口，让我们查看该函数的官方文档

![image](https://image.3001.net/images/20210910/1631264515_613b1f0352b26643faebc.png!small)

可以看到查询的信息都存到了 **MemoryInformation** 中，而 **MemoryInformation** 对应的结构体是
**MEMORY_INFORMATION_CLASS** ，MEMORY_INFORMATION_CLASS实际包含了一个
**MEMORY_BASIC_INFORMATION** ，MEMORY_BASIC_INFORMATION结构如下

![image](https://image.3001.net/images/20210910/1631264484_613b1ee4babc81406949f.png!small)

查看RegionSize的描述

![image](https://image.3001.net/images/20210910/1631264420_613b1ea4b5f36a8a10c24.jpg!small)

翻译过来的意思是，RegionSize的计算方式是，从起始地址开始，直到内存页的属性不一致为止，包含的byte数量，就是RegionSize

## B 猜想与验证

首先我们可以初步得出结论，BeaconEye当中获取堆的信息时，实际只获取了第一个堆段(因为堆段和堆段之间是不连贯的，导致内存页属性不能保持一致)，因此假设Beacon
Config没有被释放在第一个堆段中，就会导致BeaconEye检测失败，为了实现这个猜想，笔者将SymInitialize注释掉，
**转而手动调用HeapAlloc进行堆分配(当堆空间分配的足够多时，就会触发系统自动生成堆段)，如果这个猜想是正确的，那么BeaconEye将同样无法扫描**

![image](https://image.3001.net/images/20210910/1631264392_613b1e886db93a34e7650.png!small)

编译运行，再使用BeaconEye进行检测，发现已经无法检测了，猜想bingo

![image](https://image.3001.net/images/20210910/1631264383_613b1e7fb6aa2795b6ad6.png!small)

## C BeaconEye修复(伪)

现在不能检测的原因已经找到了，修复其实非常简单，前面提到过，heap结构中包含了堆段的双向链表，因此我们只需要在BeaconEye当中，遍历这个双向链表，将所有堆段地址都添加到待扫描列表中即可，以下是修复代码

![image](https://image.3001.net/images/20210910/1631264361_613b1e69d5653ed13446e.png!small)

这个时候我们重新编译，扫描原先使用了SymInitialize的Cobalt Strike Beacon，发现已经可以扫出来了

![image](https://image.3001.net/images/20210910/1631264351_613b1e5fac8e0a61d8953.png!small)

## D 为什么还是被Bypass了?

但是事情远远没有那么简单，因为我发现先前手动调用HeapAlloc的Cobalt Strike
Beacon并没有扫出来，这令我百思不得其解，为了解决问题，我的思路是先确定Beacon
Config在内存中哪个位置，这里同样使用yara进行确认(扫描完整内存)，得到具体的位置后，调试BeaconEye并判断是否读取到了对应的内存。经过一番调试，发现BeaconEye确实存在于堆段中，但是BeaconEye并没有完整的读取到堆段的所有内存，示意图如下

![image](https://image.3001.net/images/20210910/1631264329_613b1e49eee66b3884af6.jpg!small)

红色部分是 **BeaconEye实际读取到的内存** ，绿色部分是实际 **Beacon Config存放的位置**
，为什么会出现这种情况，这个时候就得继续回到Windows的内存设计上

## E HeapBlock

在Windows的堆内存当中，除了堆段以外，还有一个概念叫堆块，每一个堆段都是由多个堆块组成的，使用 **vmmap** 工具即可查看

![image](https://image.3001.net/images/20210910/1631264297_613b1e29db3c4eef0746c.png!small)

不难发现每一个堆段包含了大量的堆块，这也解释了为什么BeaconEye会检测失效，因为堆块和堆块之间存在属性不一致的内存页，导致只能读取部分内存空间

而在实际的进程当中，堆块对应的结构体是_HEAP_ENTRY

![image](https://image.3001.net/images/20210910/1631264240_613b1df0600ee5b38e13f.png!small)

但是在_HEAP_SEGMENT当中，只有 **FirstEntry** 和 **LastValidEntry**
，这两个字段的含义是指向第一个以及最后一个堆块

![image](https://image.3001.net/images/20210910/1631264217_613b1dd98e57fc950ae18.png!small)

而经过阅读相关资料，发现并没有链表将所有堆块串联起来(无论堆块是何种状态)，因此堆块的位置需要手动计算，
**这里存在一个小插曲，就是windows实际是加密了_HEAP_ENTRY这个结构的，加密方式是Xor，而Xor的密钥则在_HEAP结构的0x88(x86是0x50)，因此在计算堆块大小时，需要手动解密Size**

## F BeaconEye修复(真)

在之前的修复代码上，我们手动计算所有堆块的地址，并添加到待扫描列表当中，代码如下(方便演示这里只写了x64部分)

![image](https://image.3001.net/images/20210910/1631264193_613b1dc1bc9bd21c4ac85.png!small)

编译修复的BeaconEye，重新扫描手动调用了HeapAlloc去Bypass原版BeaconEye的Beacon，发现已经可以扫描了

![image](https://image.3001.net/images/20210910/1631264175_613b1daf3119ee866ada5.jpg!small)

## 10 结语

目前这个加强修复版的代码，可以通杀Cobalt
Strike全版本(3.x的yara规则需要修改)，这对攻击方来说提出了更高的挑战以及要求。目前该检测功能已经集成到即将发布的 **牧云**
新版本当中，也欢迎大家来申请试用体验更强大的主机安全产品。  
另外， **牧云团队**
正在招聘主机安全领域的产品安全研究员，如果你和我一样，喜欢研究红蓝对抗，并希望将它落地到产品当中，欢迎投递简历，投递邮箱为jingyuan.chen@chaitin.com

## 11 参考资料

> • https://wbglil.gitbook.io/cobalt-strike/cobalt-strike-gong-ji-fang-> yu/untitled-1  
> • 《Windows Internals 6 part 1》

