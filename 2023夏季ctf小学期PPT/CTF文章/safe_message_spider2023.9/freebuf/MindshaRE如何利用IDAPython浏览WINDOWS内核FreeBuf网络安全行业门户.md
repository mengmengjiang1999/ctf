![1.png](https://image.3001.net/images/20180529/15275827102608.png!small)

## 写在前面的话

**当我去参加安全会议时，我总喜欢跟大神们讨论关于逆向工程方面的东西。因为这样我就可以从别人的经验中了解到他们是如何自动化实现那些繁琐操作的了。值得一提的是，很多人已经习惯使用IDA的人却不喜欢使用内置的API来完成他们的工作。为了改变这个现状，今天我准备给大家演示IDA配合上Python之后会有怎样强大的效果。**

在这篇文章中，我将给大家介绍如何利用IDA Python来枚举Windows的系统调用表。

### 背景知识

Windows系统中所有发生的系统调用都会被分配一个ID，这个ID是一个唯一值，用于标识一个系统调用在执行时具体使用的是哪一个函数。在不同的Windows版本中，这些ID的变化可能会非常大，对于Windows
10来说，每一个发行版本中的这些ID都不同。但是对于普通应用程序而言，由于使用的是用户模式下的代码库，因此ID不会变化。

接下来，我将给大家演示如何手动枚举调用表，然后再演示如何通过Python实现自动化枚举。

## 手动枚举Windows系统调用表

在解析系统调用表时我们还有三个重要的符号需要识别：表的基址、表的大小和参数在栈中所占的字节大小。对于ntoskrnl.exe来说，这三个参数的名称分别为：KiServiceTable、KiServiceLimit和KiArgumentTable。对于win32k.sys来说，这三个参数就变成了W32pServiceTable、W32pServiceLimit和W32pArgumentTable。在32位系统架构中，这些符号名称中都会包含下划线。

比如说，我们来看一看Windows 7
64位版本中ntoskrnl.exe（版本6.1.7601.24117）的信息。KiServiceLimit数据如图1所示：

  
![2.png](https://image.3001.net/images/20180529/15275827286344.png!small)根据这些信息，我们可以看到这里有401个系统调用（0x191）。KiServiceTable数据如图2所示：

  
![3.png](https://image.3001.net/images/20180529/15275827344815.png!small)根据图2的数据，我们就可以将函数和它们的ID手动映射出来了。其中，NtMapUserPhysicalPagesScatter对应的ID为0x0000，NtWaitForSingleObject对应的ID为0x0001，NtCallbackReturn对应的ID为0x0002，后面的依此类推。

这里有两种特殊情况需要专门处理。如果我们分析的是win32k.sys，在枚举函数ID时需要在表地址上加0x1000。同样的，对于64位Windows10（build
1607）我们也需要进行不同的处理。在这个版本的系统中，系统调用表包含了四个字节的函数偏移量。

下面给出的是版本号为10.0.17134.48的ntoskrnl.exe信息。KiServiceTable数据如图3所示：

  
![4.png](https://image.3001.net/images/20180529/15275827432091.png!small)这也就意味着，我们需要每次读取四个字节的值，然后将它们与基地址相加。

## 利用IDA完成自动化映射

首先我们来看一看需要调用的IDA函数：

> 1\. idaapi.get_imagebase：这个函数将会在我们所查看的模块中返回基地址。
>
> 2\. idc.GetInputFile：该函数可以返回IDB加载的文件名称。
>
> 3\. idc.BADADDR：这是一个值为-1（无符号整形）的常量，我们还可以用它来判断当前系统为32位还是64位模式。
>
> 4\. idc.Name：该函数可以返回给定地址的名称。
>
> 5\. idc.LocByName：它的功能跟idc.Name正好相反，它用于返回给定名称的地址。
>
> 6\. idc.Dword：该函数能返回给定地址的四字节值。
>
> 7\. idc.Qword：该函数可返回给定地址的八字节值。
>
> 8\. idautils.DataRefsFrom：该函数可根据任意数据引用枚举给定地址。

首先，我们需要确定正在分析的对象是ntoskrnl.exe还是win32k.sys：

  
![5.png](https://image.3001.net/images/20180529/15275827584537.png!small)接下来，我们需要判断使用哪一个符号名称，并判断是否需要在变量中添加下划线：

![6.png](https://image.3001.net/images/20180529/15275827687479.png!small)

如果表不存在，LocByName将返回BADADDR，所以我们就可以利用这一点来测试符号名称是否存在或是否需要添加下划线。

得到了正确的符号名称之后，我们需要获取表的实际大小：

![7.png](https://image.3001.net/images/20180529/15275827792876.png!small)

首先获取LocByName的地址，然后利用Dword获取地址值。下面给出的是64位Windows 10的处理方法：

![8.png](https://image.3001.net/images/20180529/15275827906025.png!small)

DataRefsFrom将会利用数据引用来遍历表的基地址，但如果目标是新版本的Windows
10系统，我们就需要在基地址上加上相应的值。接下来需要做的就是从表的基地址开始读取连续的值。我们可以使用Qword函数处理64位版本，用Dword处理32位版本。下面给出的是输出结果样本：

![9.png](https://image.3001.net/images/20180529/1527582806378.png!small)

### 工具下载

完整源码获取：【[GitHub传送门](https://raw.githubusercontent.com/thezdi/scripts/master/enumerate_service_table.py)】

## 总结

逆向工程分析本来就是一个枯燥乏味的工作，但任务的自动化实现却能够在无聊中添加一些趣味。希望大家能够喜欢这篇文章，并在日常工作中发现IDA和Python的更多功能。

 ***
参考来源：[zerodayinitiative](https://www.zerodayinitiative.com/blog/2018/5/21/mindshare-walking-the-windows-kernel-with-ida-python)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

