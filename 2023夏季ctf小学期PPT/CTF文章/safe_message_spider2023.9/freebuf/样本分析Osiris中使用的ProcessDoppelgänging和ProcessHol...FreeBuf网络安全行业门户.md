**模仿合法进程通常是恶意软件作者最喜欢使用的技术，因为这可以允许他们运行恶意模块而不被杀毒软件察觉。多么多年来，各种各样的技术层出不穷，他们也更加接近了这个目标。这个话题也被研究者和逆向工程师所津津乐道，因为其对于Windows
API的使用也非常有创意。**

**![shutterstock_1929537-900x506.jpg](https://image.3001.net/images/20180823/1535026843_5b7ea69b05841.jpg!small)**

Process Doppelgänging是一种模仿进程的新技术，该技术于去年Black
Hat会议公开，在此之后，一个叫SynAck的勒索软件被发现利用这种技术实现恶意目的，尽管Process
Doppelgänging在野并不常见，我们最近还是在Osiris银行木马（Kronos的新版本）中发现了一些类似特征。仔细分析后，我们发现原始的技术已经被进一步定制化了。

实际上，恶意软件作者已将ProcessDoppelgänging和Process
Hollowing中的技术结合使用，并选择两种技术的最佳部分来创建更强大的组合。在这篇文章中，我们仔细研究了如何在受害机器上部署Osiris，这要归功于一个有趣的Loader。

## 概览

Osiris按三个步骤加载，如下图所示：

![e706e67.png](https://image.3001.net/images/20180823/1535025889_5b7ea2e1272e7.png!small)

第一阶段加载器使用了ProcessDoppelgänging技术。然后由于第二阶段的加载器，Osiris被分发。

## 加载额外的NTDLL

运行时，初始dropper会创建一个新的进程wermgr.exe。

![dropper_run-1.png](https://image.3001.net/images/20180823/1535025919_5b7ea2fff0038.png!small)

查看注入器的进程空间中所加载的模块，我们可以看到NTDLL的一个副本：

![added_ntdll-1_.png](https://image.3001.net/images/20180823/1535025934_5b7ea30eb347e.png!small)

这是一种众所周知的技术，一些恶意软件作者使用这种技术来避免被监控并隐藏他们所调用的API。当我们仔细研究额外NTDLL调用了哪些函数时，发现更多有趣的细节。它调用了几个与NTFS事务相关的API。很容易猜到，这里采用了依赖于这种机制的Process
Doppelgänging技术。

NTDLL是一个特殊的低级DLL。基本上，它只是系统调用的封装。它与系统中的其他DLL没有任何依赖关系。由于这个原因，它可以方便地加载。其他的系统DLL（如Kernel32）在很大程度上依赖于从NTDLL导出的函数。这就是为什么许多用户区的监视工具hook并拦截NTDLL导出的函数：检查正在调用的函数，并监视是否存在任何可疑活动。

恶意软件作者显然知道这一点，所以有时，为了绕过这种机制，他们从磁盘加载新的且未hook的NTDLL副本。有几种方法可以实现这一点。我们来看看Osiris的作者是如何做到的。

通过内存映射，我们看到NTDLL副本作为image加载，与其他DLL一样。这种类型的映射是常见的由LoadLibrary函数加载DLL，或者NTDLL的低级版本LdrLoadDll的映射。不过NTDLL默认加载到每个可执行文件中，并且官方API无法再次加载相同的DLL。

通常，恶意软件作者都会手动映射副本，但这会提供不同的映射类型，并和正常加载的DLL中不一样。在这里，作者想出一个解决方法：他们使用以下函数将文件作为一个部分加载：

> ntdll.NtCreateFile – 打开ntdll.dll文件
>
> ntdll.NtCreateSection – 在文件外创建一个section
>
> ntdll.ZwMapViewOfSection – 将此部分映射到进程地址空间

![create_and_map_.png](https://image.3001.net/images/20180823/1535025999_5b7ea34f15e03.png!small)

这种做法很聪明，因为DLL被映射为一个image，所以它看起来像是以典型的方式加载的。

该DLL被进一步使用，以使注入载荷行为更加隐蔽，拥有NTDLL的新副本，所以从那里使用的功能没有被安全产品所发现。

## 与Process Doppelgänging和Process Hollowing的比较

Loader将载荷注入新进程的方式与Process Dopplegänging显示出一些重要的相似之处。但是，如果我们仔细分析它，也可以看到与去年Black
Hat所提出的存在不同之处。不同点更像Process Hollowing。

### 经典的Process Doppelgänging：

![dopel1_.png](https://image.3001.net/images/20180823/1535026039_5b7ea3773f2f6.png!small)

### Process Hollowing：

![hollowing1-1_.png](https://image.3001.net/images/20180823/1535026059_5b7ea38b6c69c.png!small)

### Osiris Loader：

![osildr1-2_.png](https://image.3001.net/images/20180823/1535026098_5b7ea3b20b278.png!small)

## 创建一个新进程

Osiris loader首先创建它将要注入的进程。该过程由Kernel32：CreateProcessInternalW中的函数创建：

![create_process_internal_.png](https://image.3001.net/images/20180823/1535026146_5b7ea3e24edea.png!small)

新进程（wermgr.exe）是在原始文件的挂起状态下创建的。它让我们想起了Process
Hollowing，这是一种更古老的进程模仿技术。在Process
Dopplegänging算法中，创建新流程的步骤需要很长，并使用不同的，未记录的API：NtCreateProcessEx：

![create_process_.png](https://image.3001.net/images/20180823/1535026172_5b7ea3fc168b6.png!small)

这种差异很重要，因为在Process
Doppelgänging中，新进程不是从原始文件创建的，而是从特殊缓冲区（section）创建的。section应该是在早期创建，使用在NTFS事务中创建的“不可见”文件。在Osiris
loader中，这个部分也会出现，但顺序是颠倒的，让我们不知是否可以将它们视为相同的算法。

创建进程后，相同的image（wermgr.exe）将映射到loader的上下文中，就像之前使用NTDLL一样。

![mapped_wermgr_.png](https://image.3001.net/images/20180823/1535026196_5b7ea41424bdd.png!small)

后来证明，loader会修补远程进程。wermgr.exe的本地副本将用于收集有关补丁的信息。

## NTFS事务的使用

现在简要介绍一下NTFS事务。这种机制通常在数据库运行时使用，它们也以类似的方式存在于NTFS文件系统中。NTFS事务将一系列操作封装到一个单元中。在事务内部创建文件时，提交事务之前任何人都无法访问它。Process
Doppelgänging使用它们来创建不可见的文件。

在分析的案例中，对NTFS事务的使用完全类似。我们只能发现所用API的细微差别。加载程序创建一个新事务，在该事务中创建一个新文件。
最初的使用了来自Kernel32的CreateTransaction和CreateFileTransacted实现。

![1_.png](https://image.3001.net/images/20180823/1535026248_5b7ea44831ddc.png!small)

首先，调用来自NTDLL的函数ZwCreateTransaction。然后作者并没有使用CreateFileTransacted，而是通过RtlSetCurrentTransaction和ZwCreateFile打开事务处理文件（创建的文件是％TEMP％\\\Liebert.bmp）。然后，dropper将新内容写入文件。类似地，其也会使用ZwWriteFile的RtlSetCurrentTransaction。

![write_file-1_.png](https://image.3001.net/images/20180823/1535026260_5b7ea454c1f54.png!small)

可以看到缓冲区包含新的PE文件：即第二阶段的载荷。通常，对于此技术，文件仅在事务中可见，并且不能由其他进程（如杀毒软件）打开。

![write_file-1_.png](https://image.3001.net/images/20180823/1535026298_5b7ea47acb1fe.png!small)

事务中的文件创建后，会用于创建特殊格式的缓存，即section。完成这些动作的函数都只能通过低级API
ZwCreateSection/NtCreateSection调用。

![rollback_transaction_.png](https://image.3001.net/images/20180823/1535026324_5b7ea4944cff0.png!small)

创建该部分后，不再需要该文件。事务被回滚（通过ZwRollbackTransaction），并且对文件的更改不会保存在磁盘上。因此，上述部分与Process
Doppelgänging的类比部分相同。通过使用从NTDLL的自定义副本调用的低级别函数，dropper的作者使其更加隐蔽。

## 从一个section到一个进程

此时，Osiris dropper创建了两个完全不相关的元素：

> 一个进程（此时包含映射的，合法的可执行文件wermgr.exe）
>
> 一个section（从事务创建）并包含恶意载荷

如果这是典型的Process
Doppelgänging，那么这种情况永远不会发生，我们会根据带有映射载荷的部分直接创建进程。那么问题出现了，dropper的作者是为什么在这一点上将元素合并在一起的呢？

如果我们跟踪执行，就可以看到在回滚事务之后调用以下函数（格式：RVA;function）：

    
    
    4b1e6;ntdll_1.ZwQuerySection
    
    4b22b;ntdll.NtClose
    
    4b239;ntdll.NtClose
    
    4aab8;ntdll_1.ZwMapViewOfSection
    
    4af27;ntdll_1.ZwProtectVirtualMemory
    
    4af5b;ntdll_1.ZwWriteVirtualMemory
    
    4af8a;ntdll_1.ZwProtectVirtualMemory
    
    4b01c;ntdll_1.ZwWriteVirtualMemory
    
    4b03a;ntdll_1.ZwResumeThread

因此，看起来新创建的部分只是作为附加模块映射到新进程中。将载荷写入内存并设置必要的补丁（例如入口点的重定向）后，将恢复该进程：

![resume_proc_.png](https://image.3001.net/images/20180823/1535026396_5b7ea4dc4e76b.png!small)

重定向执行的方式类似于Process
Hollowing的变种。远程进程的PEB已打补丁，新模块已作为一部分被添加。（由于这个原因，当进程恢复时，导入将自动加载。）

![resume_proc_.png](https://image.3001.net/images/20180823/1535026432_5b7ea500e0651.png!small)

但是，入口点重定向仅由初始模块的入口点地址处的补丁完成。单个跳转即重定向到注入模块的入口点：

![patched_ep-1.png](https://image.3001.net/images/20180823/1535026454_5b7ea5161c5e1.png!small)

如果修补入口点失败，那么加载程序会使用包含第二个入口点重定向变种，方法是在线程上下文中设置新地址（ZwGetThreadContext - >
ZwSetThreadContext），这是Process Hollowing中使用的经典技术：

![set_context_-1.png](https://image.3001.net/images/20180823/1535026478_5b7ea52e370e0.png!small)

## 第二阶段Loader

下一层(8d58c731f61afe74e9f450cc1c7987be)还不是核心部分，但是loader的下一阶段。其仅仅引入一个DLL，Kernel32。

加载最终payload的方式与平常无异，Osiris核心代码逐步解包，然后与相关依赖一起加载到Loader进程新分配的内存区域中。

![final_payload_.png](https://image.3001.net/images/20180823/1535026534_5b7ea5668243f.png!small)

自注入后，Loader会跳转到payload的入口点：

![payload_entry_point_.png](https://image.3001.net/images/20180823/1535026560_5b7ea580005f8.png!small)

应用程序的入口点与标头中保存的入口点不同。因此，如果我们转储载荷并尝试相互依赖地运行，会无法执行相同的代码。这是一种用于误导研究人员的有趣技术。

这是标头中设置的入口点RVA 0x26840：

![original_ep_.png](https://image.3001.net/images/20180823/1535026582_5b7ea5961357d.png!small)

该调用使应用程序进入无限睡眠循环：

![fake_ep_.png](https://image.3001.net/images/20180823/1535026596_5b7ea5a4c75f3.png!small)

恶意软件执行的开始的真实的入口点在0x25386，只有loader知道入口点地址。

![osiris_ep_code_.png](https://image.3001.net/images/20180823/1535026631_5b7ea5c7506b7.png!small)

## 第二阶段与Kronos Loader

使用隐藏入口点的类似技巧被原始Kronos（2a550956263a22991c34f076f3160b49）使用。在Kronos的案例中，最终的载荷被注入svchost。通过修补svchost中的入口点将执行重定向到内核：

![svchost_patch_.png](https://image.3001.net/images/20180823/1535026658_5b7ea5e2de0a9.png!small)

在这个案例中，载荷的入口点是RVA
0x13B90，而载荷标头(d8425578fc2d84513f1f22d3d518e3c3)中保存的入口点地址是0x15002。

![kronos_ep_.png](https://image.3001.net/images/20180823/1535026675_5b7ea5f348488.png!small)

Kronos入口点的代码与Osiris显示出相似之处。 然而并不完全相同：

![kronos_ep_code_.png](https://image.3001.net/images/20180823/1535026698_5b7ea60a312b1.png!small)

## 总结

第一阶段Loader受到Process
Dopplegänging的强烈启发，并以非常专业的方式实施，恶意软件作者使用相对较新的技术并与其他技术相结合，分发者经常使用第三方加密程序来打包恶意软件；第二阶段与载荷紧密耦合，在这里我们可以很肯定地说这一层是与核心一起准备的。

 ***参考来源：[Malwarebytelabs](https://blog.malwarebytes.com/threat-analysis/2018/08/process-doppelganging-meets-process-hollowing_osiris/)，Covfefe编译，转载请注明来自FreeBuf.COM**

