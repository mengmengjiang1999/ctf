## 前言

前段时间360安全卫士发表了一篇对双枪2感染释放驱动行为的分析报告，报告地址:

<http://www.freebuf.com/articles/web/167776.html>

相比于双枪一代，它增加了HIVE文件保护，新增了WFP网络功能拦截，还有保护了自身的系统回调不被修改，并且针对部分查杀驱动摘除了所有的关机回调，该驱动木马从一代后一直在更新活跃。

接下来我们将对该驱动进行再一次全面的分析，揭露它难以查杀的详细原因。

## 一、驱动初始化部分

### 1.1驱动入口函数

主要为判断初始化一些变量，然后开启初始化线程工作。

入口函数所有代码:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238707192447.png!small)  

图1

先获取Nt基地址,后续生成设备名,随机化线程地址和获取注册表操作函数用:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238707283271.png!small)  
  

图2

然后初始化一些必要函数后续用于注入DLL模块:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238707357003.png!small)  

图3

从Ntdll函数中取出SSDTIndex,在KeServiceDescriptorTable取得函数地址 :

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238707443951.png!small)  

图4

获取完成后判断下加载时机,由于该驱动重启后为Boot0驱动，判断下Ntfs文件系统驱动是否加载,:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238707577944.png!small)  

图5

创建设备名和符号链接跟应用层交互:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238707648081.png!small)  
  

图6

设备名是通过随机Nt基地址数字生成:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238707716264.png!small)  

图7

生成随机设备名，并使用这个随机设备注册关机回调，然后开启初始化线程：

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238707806956.png!small)  
  

图8

### 1.2初始化线程

线程入口开始就调用KeEnterCriticalRegion

而该函数作用为禁止内核APC,暂停线程操作调用的就是内核APC

调用这个函数后线程就无法被暂停，然后再隐藏自身线程起地址，将其设置为ntos里面的一个随机地址。

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238708259340.png!small)  
图9

然后开始挂钩模块加载回调初始化获取一些注册表函数地址并且重新创建随机文件名将自己驱动拷贝过去：

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238708388790.png!small)  

图10

然后创建三个工作队列并且将模块注入到系统进程：

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238708456404.png!small)  

图11

然后进入死循环,一直往系统中放置工作队列用于后续感染BootKit等一系列操作:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238708544183.png!small)  
  

图12

### 1.3注册表函数初始化

在初始化线程中调用了KeyHelperStartup,该函数主要为获取CmSetValueKey更底层的操作函数,函数内容为:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238708612152.png!small)  

图13

GetCellRoutineOffset 函数里面主要为获得一些硬编码偏移。

然后挂钩函数GetCellRoutine：

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238708703889.png!small)  

图14

开启线程触发调用,触发完成后恢复钩子:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238708772959.png!small)  
  

图15

触发调用函数为:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238708854751.png!small)  

图16

在挂钩函数中使用RtlWalkFrameChain栈回溯来找到CmSetValueKey等函数调用。

并且校验线程是否为触发的线程，根据调用类型CallType来查找，

![Clipboard
Image.png](https://image.3001.net/images/20180416/1523870892450.png!small)  

图17

初始化代码完成后,接下来我们开始从网络阻断，文件保护，注册表保护，模块加载禁止，改首页模块注入,BootKit感染,自身回调防护几个部分的详细分析。

## 二、网络阻断

开启线程主要是分系统挂钩网络组件Xp系统为挂钩TCPIP Win7以上注册WFP相关例程:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238709011266.png!small)  

图18

入口点先隐藏自身，将自身设置为

\\\SystemRoot\\\system32\\\drivers\\\volmgr.sys驱动。

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238709085979.png!small)  

图19

然后根据系统不同挂钩不同系统网络组件,对于XP系统：

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238709167306.png!small)

图20

Win7系统:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238709235649.png!small)  

图21

然后注册WFP回调:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238709307972.png!small)  

图22

回调函数中判断进程名字，一旦有匹配的进程名，则阻断该进程网络操作:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238709376150.png!small)  

图23

匹配是通过Hash计算进程名字:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238709438451.png!small)  

图 24

## 三、文件保护

先生成随机文件名驱动，并且将原来文件删除,删除前去除保护开关。

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238709515365.png!small)  

图25

保护开关函数为，注册表函数类似，该函数频繁被调用，我们看下具体内容:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238709593314.png!small)  

图26

将当前线程设置为信任线程，注册表和文件挂钩就会放行该线程。

清理信任线程代码为:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238709669660.png!small)  

图27

然后将一些要保护的文件设置上。

自身文件:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238709768335.png!small)  

图28

Ntfs文件:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238709853391.png!small)  

图29

FastFat文件:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/1523870992569.png!small)  

图30

设置上保护后，挂钩Ntfs正式开启保护:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238710097226.png!small)  

图 31

该函数中首先获取ntfs驱动对象:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238710163606.png!small)  

图32

备份并替换所有的Ntfs FsdDisptach:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238710236051.png!small)  

图33

备份所有FastIo操作例程:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238710317010.png!small)  

图 34

替换:

![Clipboard
Image.png](https://image.3001.net/images/20180416/1523871038968.png!small)  

图35

FastFat类似，这里我们就不看了。

挂钩函数中:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238710457528.png!small)  
  

图36

CheckTheFileIsProtectAndCompleteTheRequest函数里面调用:

![Clipboard
Image.png](https://image.3001.net/images/20180416/1523871053623.png!small)  

图37

该函数主要是否为之前初始化的保护文件列表，依然是通过文件名Hash比对的,并且查看当前线程是否为可以信任线程。

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238710602681.png!small)  

图38

如果不是则拒绝打开。

对于已经打开的文件对象,通过判断文件对象的FsContext来判断。

![Clipboard
Image.png](https://image.3001.net/images/20180416/1523871068637.png!small)  

图39

之前会先获取Hive文件对象。

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238710754349.png!small)  

图40

判断是否一致：

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238710833145.png!small)  

图41

如果为保护的文件则返回 STATUS_INVALID_PARAMETER。

Hive文件特殊处理。

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238710908982.png!small)  

图42

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238710967564.png!small)  

图43

## 四、注册表保护

先设置自身开机顺序:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238711048249.png!small)  
  

图44

获取优先启动组:

![Clipboard
Image.png](https://image.3001.net/images/20180416/1523871112695.png!small)  

图45

然后将服务写入:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/1523871120387.png!small)  

图46

写入函数为:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238711281499.png!small)  

图47

优先使用更底层的CmSetValueKey函数,然后才使用系统调用:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238711359986.png!small)  

图48

初始化保护列表:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238711447537.png!small)  

图49

注册保护回调:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/1523871154618.png!small)  

图50

回调保护中:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238711626464.png!small)  

图51

Hash比对注册表键,检测是否为保护项目:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238711691818.png!small)  

图52

如果是且不是可信进程则拒绝打开。

## 五、模块加载禁止

先设置回调:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238711808347.png!small)  

图53

分驱动和应用进程两种情况。

驱动文件判断是否需要Patch的模块。:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238711887570.png!small)  

图54

Hash跟 正则匹配aw***.sys等一些驱动。

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238711969320.png!small)  

图55

如果是则Patch入口点:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238712036627.png!small)  

图56

对于应用层进程判断是否为浏览器，如果是则禁止网盾模块加载:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238712102458.png!small)  

图57

## 六、改首页模块注入

先解密DLL，动态获取ntdll地址偏移.

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238712199136.png!small)  

图58

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238712272341.png!small)  

图59

解密文件并校验:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238712346503.png!small)  

图60

然后分别向Services.exe Explorer.exe注入。

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238712414500.png!small)  

图61

分配内存:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238712491372.png!small)  

图62

拷贝代码:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238712555253.png!small)  

图63

然后注入执行:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238712642004.png!small)  

图64

## 七、BootKit感染

### 7.1查找活动分区

目前有不少机器安装了多块硬盘，需要先找活动磁盘的活动分区。

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238712725394.png!small)  
  

图 65

然后写入BooKit组件，分三步写入，先写入引导驱动BootImage，然后写VBR，最后写入MBR,只有当前面一步操作成功后才继续下一步写入。

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238712793220.png!small)  

图66

### 7.2 BootImage写入

写入BootImage前 先找磁盘末尾空余区域，如果没有空间则写入失败。

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/1523871287377.png!small)  

图67

获取磁盘参数:

![Clipboard
Image.png](https://image.3001.net/images/20180416/1523871296170.png!small)  

图68

然后找到磁盘末尾写入位置:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238713229556.png!small)  

图69

再将BootImage加密后写入:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238713292025.png!small)  
  

图70

写入前先判断是否已经写入过了:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238713378630.png!small)  

图71

写入成功后，再写入VBR部分。

### 7.3 VBR写入

判断分区参数和是否为NTFS磁盘，仅支持Ntfs磁盘。

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238713453739.png!small)  
  

图72

然后找下VBR跳转指令:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238713523463.png!small)  

图73

查找函数为:

![Clipboard
Image.png](https://image.3001.net/images/20180416/1523871359750.png!small)  

图74

判断下是否为ESLDRLoader,如果是则删除所有项目。

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238713676412.png!small)  

图75

删除所有:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238713758467.png!small)  

图76

然后将病毒VBR压缩，合并写入:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238713822646.png!small)  

图77

并且将位置大小的参数全部异或加密保存在磁盘末尾。

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238713893638.png!small)  

图78

### 7.4 MBR写入

获取磁盘信息:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238713966325.png!small)  

图79

先将VBR写入磁盘最开始的第3个扇区后0xF个扇区，后续即使VBR被修复，MBR部分依旧可以感染VBR

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238722447076.png!small)  
图80

读取原始MBR:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238722524607.png!small)  

图81

将分区表拷贝进来，然后比对是否已经写入，如果没有则写入0号扇区:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238722612572.png!small)  

图82

### 7.4 保护BootKit

保护函数:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238722695154.png!small)  

图83

先初始化正常的VBR MBR，用系统默认的。后续如果有应用程序读取则读到这份假的内容。

MBR部分:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238722782842.png!small)  

图84

VBR部分:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238722864664.png!small)  

图85

然后再安装磁盘底层钩子:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238722939842.png!small)  

图86

挂钩中判断，写则返回拒绝.

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238723009256.png!small)  

图87

读取则返回假的数据:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238723085037.png!small)

图88

### 8 自身回调防护

LoadImage 函数保护，拷贝头部0x20个字节:

![Clipboard
Image.png](https://image.3001.net/images/20180416/1523872316758.png!small)  

图89

比对是否一致，不一致则直接恢复：

![Clipboard
Image.png](https://image.3001.net/images/20180416/1523872323522.png!small)  
  

图90

注册表回调，判断特定键值打开返回值:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238723305642.png!small)  

图91

然后重新注册上:

  
![Clipboard
Image.png](https://image.3001.net/images/20180416/15238723382720.png!small)  

图92

摘除关机回调则通过硬编码获取链表头部:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238723453098.png!small)  

图93

获取:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238723531208.png!small)  

图94

然后遍历整个链表,只要不是自身注册的随机设备就摘除该关机回调:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238723601895.png!small)  

图 95

摘除:

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238723675528.png!small)  

图96

## 总结

针对MBR和VBR系列木马泛滥的情况，360首创了针对此类顽固木马的强力查杀技术，并且能够同时自动检测和修复MBR及VBR
，发现电脑浏览器主页被反复篡改无法恢复、或出现卡慢等情况时，可使用360安全卫士进行扫描查杀，彻底清除该木马，360安全卫士已经第一时间支持该驱动木马查杀.。

![Clipboard
Image.png](https://image.3001.net/images/20180416/15238723745016.png!small)  

图97

 ***本文作者：360安全卫士，转载请注明来自FreeBuf.COM**  

