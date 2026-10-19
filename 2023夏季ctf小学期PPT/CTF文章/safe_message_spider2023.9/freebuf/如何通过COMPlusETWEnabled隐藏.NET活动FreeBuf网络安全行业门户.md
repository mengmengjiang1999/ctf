![0.png](https://image.3001.net/images/20200612/1591972447_5ee3925f5615e.png!small)

**在此之前，我曾研究过一些关于如何禁用ETW的技术，随后也有很多安全研究专家（比如Cneeliz、BatSec以及modexp）提供了一些比较好的改进方法以绕过这些安全检测机制。但是，这些方法都需要对ETW子系统进行修改，比如说拦截并控制对于某些函数的调用行为，或者解析并控制ETW注册表等等。**
****

但是，我们还有另外一种方法来禁用ETW，即通过在环境变量钟设置`COMPlus_ETWEnabled=0`来实现。那么在这篇文章中，我将跟大家分享关于这项技术的相关内容。

在开始之前，我需要提醒一下大家，ETW本身并不应该被视为一种安全解决方案，ETW的主要功能应该是作为调试工具来使用，但随着攻击技术和Payload执行技术的不断改进，有些防御机制开始使用ETW的功能来获取一些事件的相关信息，比如说.NET
Assembly的加载行为等等。但是`COMPlus_ETWEnabled`就有点类似于一个安全审计功能的开关，这也是本文所要阐述的核心。

## COMPlus_前缀解析

带有COMPlus_前缀的选项可以给开发人员提供很多配置选项，开发人员可以在运行时对程序进行配置，包括加载JIT、调整性能和转储某个方法的IL等等。这些选项可以通过设置环境变量或注册表键值来进行配置，但很多选项都没有文档可参考。如果你想了解每个选项的具体功能，那么你可能需要去阅读CoreCLR源中的[
_lrconfigvalues.h_](https://github.com/dotnet/coreclr/blob/master/src/inc/clrconfigvalues.h)源码文件了。但通过对该文件进行分析，你会发现其中并没有关于COMPlus_ETWEnabled的内容。

跟很多未公开的功能一样，这些选项可以给攻击者提供很多有意思的功能，而且这些选项不一定是以`COMPlus_`开头的。

## 寻找COMPlus_ETWEnabled

虽然CoreCLR源中包含了大量的设置选项，但很多都并不适用于标准的.NET Framework。为了判断哪些`COMPlus_`选项适用于.NET
Framework，我们可以在clr.dll中寻找相关的信息，比如说`clrconfigvalues.h`中列出的COMPlus_AltJit选项。

移除前缀，并在IDA中搜索一些简单的字符串，我们就可以发现`clr.dll`中可能引用到了`AltJit`：

![1.png](https://image.3001.net/images/20200612/1591972491_5ee3928b798e4.png!small)
通过追踪引用的位置，我们找到了一个名叫`CLRConfig::GetConfigValue`的方法，这个方法会将我们设置的名称以参数的形式传递，并获取对应的值：

![2.png](https://image.3001.net/images/20200612/1591972498_5ee39292d80bb.png!small)
根据上述发现的内容，我们可以找到一些在运行时访问类似选项配置的其他方法：

![3.png](https://image.3001.net/images/20200612/1591972504_5ee39298e633f.png!small)
由于微软为CLR提供了相对应的PDB文件，那么我们就可以对它们一一进行分析，并通过查看Xref来寻找潜在的引用目标：

![4.png](https://image.3001.net/images/20200612/1591972512_5ee392a0df2c6.png!small)
最后，通过对引用进行跟踪，并查看传递给`CLRConfig::GetConfigValue`的参数，我们就可以发现最终使用的选项了：

##
![5.png](https://image.3001.net/images/20200612/1591972521_5ee392a94467a.png!small)
COMPlus_ETWEnabled的功能

通过在IDA中分析CFG，我们就可以发现禁用ETW的机制了：

![6.png](https://image.3001.net/images/20200612/1591972533_5ee392b5de5fb.png!small)

在这里，我们可以清楚地看到两条代码路径，具体执行的路径取决于`CLRConfig::GetConfigValue`所返回的`COMPlus_ETWEnabled`值。如果该选项存在并且返回的值为0，那么CLR就会跳过上图中蓝色的ETW注册代码块，其中的`_McGenEventRegister`是EventRegister
API的封装函数。

通过对这些GUID进行分析，我们可以发现：

![7.png](https://image.3001.net/images/20200612/1591972551_5ee392c71a9e5.png!small)

根据这个GUID：`{e13c0d23-ccbc-4e12-931b-d9cc2eee27e4}`，根据微软提供的信息，这个GUID对应的是CLR ETW
provider：

##
![8.png](https://image.3001.net/images/20200612/1591972559_5ee392cf49b9e.png!small)
后话

希望这篇文章的内容可以给大家在日常的安全研究过程中提供一些有价值的思路。从本质上来说，我们可以通过设置`COMPlus_ETWEnabled=0`来让CLR跳过.NET
ETW provider的注册过程，从而隐蔽相关事件。

 **参考来源**

>  **[ _xpnsec_](https://blog.xpnsec.com/hiding-your-dotnet-complus-> etwenabled/)**

