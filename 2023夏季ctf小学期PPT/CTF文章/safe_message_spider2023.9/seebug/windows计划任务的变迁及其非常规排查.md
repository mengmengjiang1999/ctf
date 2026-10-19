**作者：rep_Su@青藤实验室  
原文链接：<https://mp.weixin.qq.com/s/aS5MRwnYR5pqE1PmKiH24w>**

之前我们分享了一篇 [windows
计划任务隐藏新姿势分享](https://mp.weixin.qq.com/s/ktGug1VbSpmzh9CEGKbbdw)，看到留言感兴趣的是计划任务的排查，因此又出了一篇详细的排查教程，希望对大家有所帮助。

## 研究背景

在 server 2012 上使用 schtasks 创建计划任务时，我意外的发现，当分别使用参数 `/mo` 和 `/ri`
时，计划任务创建的方式有所不同，具体如下图：

![](https://images.seebug.org/content/images/2021/02/04/1612428643000-1.png-w331s)

![](https://images.seebug.org/content/images/2021/02/04/1612428644000-2.png-w331s)

我在其参数说明中也未见对此现象的具体描述

![](https://images.seebug.org/content/images/2021/02/04/1612428644000-3.png-w331s)  
![](https://images.seebug.org/content/images/2021/02/04/1612428644000-4.png-w331s)

且在计划任务管理器上发现其区别似乎只在于触发器的不同。抱着一探究竟的想法，我花了一周左右的时间研究并整理了此文，来为 windows
计划任务的相关问题提供些绵薄之力。

本文中所研究的计划任务均由 **schtasks.exe** 创建。

## 探索原因

为了一探究竟，在 server 2012 上，我分别对两种启动流程进行了追踪，在初步的了解之后，我发现随着 windows
系统的变迁，计划任务的相关进程的启动和计划任务的创建有旧版和新版之分，为了更好的理解，结合研究的内容下述依次对新旧版进行大致的说明。

### 旧版的计划任务

#### 进程启动

通过对计划任务的监控，我发现，在 server 2012 上，计划任务进程的启动，主要依赖于计划任务文件的读取和注册表项配置的访问。当使用参数 `/ri`
时，计划任务进程创建的堆栈如下图所示:  
![](https://images.seebug.org/content/images/2021/02/04/1612428644000-5.png-w331s)  
我发现此时其进程创建的关键模块为 schedsvc，通过堆栈可以大致看出此类计划任务进程的创建由 schedsvc 管理， schedsvc 会启动回调
job，从队列中捕获到并启动计划任务的 job，进而创建计划任务进程。

在 schedsvc.dll 中，我可以清晰的看到，计划任务进程创建时，实际上创建的是 taskeng.exe
进程，这也解释了为什么我看到此类计划任务的父进程是 taskeng。  
![](https://images.seebug.org/content/images/2021/02/04/1612428644000-6.png-w331s)  
在这一参数创建的计划任务进程启动时，我发现，schedsvc.dll 与 taskeng 分工明确，schedsvc.dll
主要负责注册表中对应计划任务的读取及更新，其中比较关键的行为是： **schedsvc
会负责从计划任务的job队列中启动计划任务，并且将计划任务进程的执行时间写入注册表项 DynamicInfo中** 。

写入注册表项DynamicInfo的过程如下  
![](https://images.seebug.org/content/images/2021/02/04/1612428644000-7.png-w331s)  
![](https://images.seebug.org/content/images/2021/02/04/1612428644000-8.png-w331s)  
![](https://images.seebug.org/content/images/2021/02/04/1612428644000-9.png-w331s)  
写入注册表的值如下  
![](https://images.seebug.org/content/images/2021/02/04/1612428644000-10.png-w331s)  
写入后注册表中对应项的值如下  
![](https://images.seebug.org/content/images/2021/02/04/1612428644000-11.png-w331s)  
通过分析，我发现，在 DynamicInfo 注册表项中记录的二进制偏移+c处的内容正是其计划任务执行的 UTC 时间信息。  
![](https://images.seebug.org/content/images/2021/02/04/1612428644000-12.png-w331s)  
通过对计划任务进程行为的追踪，我发现，每次计划任务进程被创建时，DynamicInfo 注册表项均会被更新，即通过对注册表中的 DynamicInfo
的监控及其中时间数据的解析，我可以知道某计划任务的进程在某时刻被执行，从而定位到对应的计划任务。 而 **taskeng则主要负责
\Windows\System32\Tasks 目录下的计划任务文件的读取及启动对应的计划任务进程**

Task 文件读取如下  
![](https://images.seebug.org/content/images/2021/02/04/1612428644000-13.png-w331s)  
计划任务进程创建如下  
![](https://images.seebug.org/content/images/2021/02/04/1612428644000-14.png-w331s)
当将参数更改为 `/mo` 时，我发现此时的进程创建的堆栈完全改变了，如下图

![](https://images.seebug.org/content/images/2021/02/04/1612428644000-15.png-w331s)  
可以看到，之前的 schedsvc 模块已经完全看不到了，取而代之的是 UBPM 和
EventAggregation，UBPM全称是统一后台进程管理器。它是自 Windows 7 和 Windows Server 2008 R2
引入的一种新的调度引擎，关于其更多的介绍，可以参考文末参考链接。而 EventAggregation，其描述为“用户态的 Event Aggregation
库”（Event Aggregation User Mode Library）  
![](https://images.seebug.org/content/images/2021/02/04/1612428644000-16.png-w331s)  
从搜索引擎中，我暂未找到关于其更详细的介绍，只知道其大致为事件聚合相关的用户态库，通过对计划任务进程行为的分析，我可以看到，在计划任务进程启动的过程中，其主要扮演着对计划任务事件的处理、通知以及信号分发的角色。

结合相关堆栈，我初步认为 UBPM 主要负责捕获被称之为 Trigger 的信号，当 Trigger 到达时，便会执行对应的 TriggerActions
启动计划任务进程，这一部分会在后文 **现代的计划任务中** 进行部分说明。

在 winserver
2012，根据UBPM的代码逻辑，计划任务进程启动时会在如下路径生成对应的计划任务ID的服务日志文件，并将计划任务的报告信息写入文件中。  
![](https://images.seebug.org/content/images/2021/02/04/1612428644000-17.png-w331s)  
其中记录的依然是计划任务进程执行的时间信息，依旧为 UTC 时间。  
![](https://images.seebug.org/content/images/2021/02/04/1612428644000-18.png-w331s)  
实际上，这也为我提供了一个找到 **旧版 UBPM 调度引擎** 启动的对应计划任务的方法，我可以直接在
`\Windows\System32\LogFiles\Scm` 文件夹，找到最新的文件，再根据文件名，在注册表中定位到计划任务的ID，从而定位到计划任务。

#### 计划任务的创建

对于上述提到的 `/ri` 和 `/MO` 的这两个参数，计划任务创建的过程大致相同，在 server 2012 上，负责计划任务创建的关键模块为
schedsvc，在计划任务创建的过程中其会执行一系列操作，这里只简要对其中的关键行为进行说明，暂不做进一步挖掘。在后文中的 **现代的计划任务中**
也会做部分补充。  
获取task文件夹的安全描述符进行权限检查
![](https://images.seebug.org/content/images/2021/02/04/1612428644000-19.png-w331s)  
读取对应注册表项的中的关键项信息  
![](https://images.seebug.org/content/images/2021/02/04/1612428644000-20.png-w331s)

![](https://images.seebug.org/content/images/2021/02/04/1612428644000-21.png-w331s)

![](https://images.seebug.org/content/images/2021/02/04/1612428645000-22.png-w331s)  
创建计划任务文件  
![](https://images.seebug.org/content/images/2021/02/04/1612428645000-23.png-w331s)  
设置对应计划任务在注册表中各子项的值  
![](https://images.seebug.org/content/images/2021/02/04/1612428645000-24.png-w331s)

![](https://images.seebug.org/content/images/2021/02/04/1612428645000-25.png-w331s)  
即在计划任务创建的过程中，schedsvc 主要负责获取相关计划任务的安全权限并对其进行检查，随后会对关键的注册表项
`TaskCache\Tasks\{ID}` 进行读取并创建计划任务文件，然后根据对关键注册表项的读取结果，再将注册表的各对应子项写入计划任务的相关内容。

### 现代的计划任务

然而，当我把目光聚焦到较新的操作系统时，我发现变化已然发生。

#### 进程启动

在较新的windows版本中（此测试版本为win10 19042.685），我发现在相关的 schedsvc
模块中旧版中的相关进程启动函数逻辑已经找不到了，之前的 taskeng 的执行逻辑也不复存在了。
![](https://images.seebug.org/content/images/2021/02/04/1612428645000-26.png-w331s)  
取而代之的是，无论采用是 `/MO` 还是 `/RI` 参数创建计划任务，计划任务的执行流程都统一由 UBPM 管理，其执行流程也和 server 2012
上的略有不同，其堆栈情况如下  
![](https://images.seebug.org/content/images/2021/02/04/1612428645000-27.png-w331s)  
我可以看到 UBPM 依然在 Trigger 到达后，会对其进程处理，但是实际上多了一层封装  
![](https://images.seebug.org/content/images/2021/02/04/1612428645000-28.png-w331s)  
经过分析，此处，handle 函数的参数 a3 是一个 UBPM_TRIGGER_CONSUMER_BLOCK 结构体，此结构体随后会被作为参数传递到
UbpmpPerformTriggerActions函数。a3+0x18 偏移处是一个 UBPM_INPUT_ACTION_PARAMS
结构体，此值会被传入 UbpmpLaunchExeAction 函数的第一个参数用来启动对应的计划任务 action。最终
UBPM_INPUT_ACTION_PARAMS 结构体会在 UbpmpLaunchExeAction 函数中进行解析后作为参数传递给
UbpmpLaunchOneTask 用来启动计划任务进程。  
![](https://images.seebug.org/content/images/2021/02/04/1612428645000-29.png-w331s)  
在 UBPM_INPUT_ACTION_PARAMS 结构体中记录了计划任务名称，计划任务内容等相关信息如下：
![](https://images.seebug.org/content/images/2021/02/04/1612428645000-30.png-w331s)  
但是由于这些相关的结构体均未文档化，想要对其结构体进行进一步更详细的逆向分析需要耗费较长的时间，这也不是本文的目的，因此此处不做过多的展开。  
通过对进程创建过程中的行为的跟踪发现，现代的计划任务进程启动的过程中，更多的依赖于注册表内容的读取而非计划任务文件的读取，单纯靠计划任务文件的检测已经很难有所效果。  
此外，server 2012 中提到UBPM模式下的 scm 路径下的日志文件也不复存在，取而代之的是报告信息被写入到注册表 DynamicInfo
项中。与taskeng 中的启动流程中的操作极为相似，其中依然包含计划任务进程的时间信息，在偏移+C处为其时间信息，依然采用的 UTC 时间。  
![](https://images.seebug.org/content/images/2021/02/04/1612428645000-31.png-w331s)

![](https://images.seebug.org/content/images/2021/02/04/1612428645000-32.png-w331s)  
![](https://images.seebug.org/content/images/2021/02/04/1612428645000-33.png-w331s)  
这也意味着，在 **现代的 UBPM 调度引擎** 启动的计划任务中，对计划任务的检测方向已经转移到了注册表中。我需要对注册表 DynamicInfo
项中的数据进行解析，从而来确定某ID对应的计划任务进程在某一时刻曾被启动。

#### 计划任务的创建

在现代的计划任务创建的流程中，我发现对计划任务创建进行管理的关键模块依然是 schedsvc.dll，但与 server 2012 上的也有所不同，由于
schedsvc 模块功能多样且复杂，此处重点对 SchRpcEnumTasks 和 SchRpcRegisterTask 做一下补充说明。

在计划任务创建的过程中，schedsvc的SchRpcEnumTasks，SchRpcRegisterTask
函数起到关键作用。SchRpcEnumTasks 函数会对计划任务的关键注册表进行检索。
**SchRpcEnumTasks主要负责对`TaskCache\\Tree`注册表下各项计划任务的的SD（由于较新的系统上，注册表项中已引入 SD
子项，此处不再通过文件获取SD而是直接读取注册表下的读取），ID，Index等内容进行检索。**

SchRpcEnumTasks 实际调用的是 RpcServer::EnumFolder 函数，在 EnumFolder 函数中首先会调用
RegTreeEntryOpen 来打开目标计划任务在 tree 中的对应注册表。  
![](https://images.seebug.org/content/images/2021/02/04/1612428645000-34.png-w331s)  
其后，在 RpcServer::EnumFolder 函数中，其会调用 JobStore::RegJobSecurityQuery 对 SD 进行检索，调用
JobStore::RegGetTreeInfo 对 ID 和 Index 进行检索，同时还会做一些权限的获取行为，调用
FolderEnumerator::FindNext 进行循环遍历。  
![](https://images.seebug.org/content/images/2021/02/04/1612428645000-35.png-w331s)

![](https://images.seebug.org/content/images/2021/02/04/1612428645000-36.png-w331s)  
**SchRpcRegisterTask负责管理具体计划任务的创建注册行为。** SchRpcRegisterTask 实际调用的是
RpcServer::RegisterTask 函数，在其中经过一系列的判断后，会调用 RegTaskEntryCreate
函数进行计划任务注册表项的实际创建和值的设置或调用 UpdateTaskEntry 进行更新。  
![](https://images.seebug.org/content/images/2021/02/04/1612428645000-37.png-w331s)  
其关键函数调用及对应注册表项与函数的创建关系大致如下图，其中箭头代表 API
调用，圆圈代表设置的注册表项，从上到下为大致的执行流程逻辑，通过这些函数关系，我可以进一步探索对应注册表项里数据的更多含义，由于关系较为复杂，限于篇幅和时间，此处仅将其重要流程图做以展示，不做更多的展开。
![](https://images.seebug.org/content/images/2021/02/04/1612428645000-38.png-w331s)  
当大部分注册表项相关值设置完毕后，schedsvc 会调用 JobStore::XmlSaveTaskFile 函数将计划任务的内容写入到对应的 tasks
文件夹中的文件中，如 `\Windows\System32\Tasks\test`。  
![](https://images.seebug.org/content/images/2021/02/04/1612428645000-39.png-w331s)

![](https://images.seebug.org/content/images/2021/02/04/1612428645000-40.png-w331s)

![](https://images.seebug.org/content/images/2021/02/04/1612428646000-41.png-w331s)  
至此计划任务基本创建完毕。

## 计划任务的检测与排查

在前文中，我断断续续的提到了部分关于计划任务检测与排查的思路，在这里，我做下简单的总结，结合前文内容，我可以将计划任务分为两大类。

### 计划任务ID的获取

对比 server 2012 与 win10
中的计划任务的创建与启动情况，我发现，在现代的计划任务中，微软对注册表的青睐显然更高一些，通过对计划任务进程创建的追踪我发现，在
**传统的以taskeng进程启动的计划任务与现代的UBPM方式启动的计划任务的这一类**
方式中，在计划任务进程启动时，关于计划任务的执行时间信息均会被即时地记录在 `TaskCache\Tasks\{ID}\DynamicInfo`
注册表项中。  
对于此类计划任务，我可以通过 sysmon 这类工具进行主动检测。设置简单的规则对 DynamicInfo 注册表进行检测，随后通过 sysmon
的日志进行确认排查  
当系统中有计划任务启动时，命中的 sysmon 规则效果如下图：  
![](https://images.seebug.org/content/images/2021/02/04/1612428646000-42.png-w331s)  
此外，结合上述分析，我也可以自己写代码对对应注册表项进行遍历解析，获取计划任务的执行时间。核心代码如下：  
![](https://images.seebug.org/content/images/2021/02/04/1612428646000-46.png-w331s)  
代码获取到计划任务内容如下：  
![](https://images.seebug.org/content/images/2021/02/04/1612428646000-47.png-w331s)

在 **旧版的UBPM启动的这一类计划任务中**
，由于微软贴心地为我提供了对应的计划任务日志文件，这使得我可以直接通过文件的修改时间信息对计划任务进行定位，对应的文件路径通常为
`\Windows\System32\Tasks\\{ID}`，如下：  
![](https://images.seebug.org/content/images/2021/02/04/1612428646000-43.png-w331s)

### 定位注册表中的计划任务

通过前文的方式获取到计划任务的ID后，我就可以直接通过 ID 在注册表中搜索或直接在 `\Schedule\TaskCache\Tasks\{ID}`
注册表位置找到对应注册表项，如下：  
![](https://images.seebug.org/content/images/2021/02/04/1612428646000-44.png-w331s)  
在其中我可以看到关于计划任务的具体信息，在一定的情况下，只借助注册表中的计划任务信息，计划任务也可以被正常启动。因此，当排查到恶意的计划任务项时，我需要同时清理
`C:\Windows\System32\Tasks\` 目录下的计划任务文件和上图中的对应 ID 的计划任务注册表内容。

### 通过windows系统日志排查计划任务

此外，通过windows系统自带的事件查看器，我也能对计划任务进行定位和排查启动的计划任务的相关事件，再通过对应的计划任务事件名在注册表
Schedule\TaskCache\Tree{name}或C:\Windows\System32\Tasks\ 目录下找到对应计划任务获取到对应的计划任务
ID  
![](https://images.seebug.org/content/images/2021/02/04/1612428646000-48.png-w331s)
![](https://images.seebug.org/content/images/2021/02/04/1612428646000-45.png-w331s)  
获取到 ID 后，再按照前文所述内容进行进一步的定位操作即可。

## 小结

从传统的 taskeng 及旧版的 UBPM
的混合使用到现代的UBPM，我可以看到，微软似乎更倾向于从普通文件的记录转换到注册表中的统一管理，实际上，在现代的计划任务中，单纯的通过检测计划任务的文件，对于计划任务的实时检测来说是收益甚微的，因此，这也在提醒我在计划任务的检测中，我的检测重心也应该向注册表倾斜。实际上，关于计划任务相应注册表的各项含义还可以做进一步的挖掘来对计划任务做更深的了解，但由于篇幅和时间所限，本次研究在一些地方也只是浅尝辄止。

本文仅从 schtasks
创建的计划任务出发，对旧版的计划任务和现代的计划任务的相关过程和关键行为做了简单的分析，并结合分析情况对计划任务的检测提出了一些建议以作抛砖引玉之用，文中若有不恰之处也欢迎讨论指正。

## 参考

<https://techcommunity.microsoft.com/t5/ask-the-performance-team/windows-7-windows-server-2008-r2-unified-background-process/ba-p/374206>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1479/>

