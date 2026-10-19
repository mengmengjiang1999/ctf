**简介**

你应该知道本文所描述的内容，因为文章主题已经很清楚描述本文的内容，众所周知，目前几乎所有的恶意软件都使用了加壳软件保护自己，这些加壳软件都使用了Anti-VM技术，这使得逆向工程师很难分析清楚它们内部实现原理。  

逆向工程是总是喜欢在虚拟机的环境下测试恶意软件，避免对实体机器的破坏，虚拟机提供了许多功能，比如可以创建虚拟机快照可以把程序的许多状态保存下来。

文章余下的部分，会展示一些使用CPUID指令检测虚拟机的流行的方法。

**为什么用CPUID?**

CPUID是一种指令级执行方法，这些方法很难被检测出来，当你单步执行的时候，很容易陷入CPUID的指令陷进，你如果单步执行的同时，又要分析程序，你最好还是使用其他技术去对抗Anti-VM技术。

下面我们看一些例子：

第一个方法：

CPUID:该指令执行会设置Eax = 1的话，会返回处理器的特征。如果是物理机Ecx的第31位值是0，否则如果是VM的话该值为1

第二个方法：

“Hypervisor”:执行CPUID时通过设置EAX =0x40000000，会从EAX、ECX、EDX返回一些虚拟化厂商的相关字符串，比如

· Microsoft: “Microsoft HV”

· VMware : “VMwareVMware”

例子：

第一个例子：

![image.png](https://image.3001.net/images/20181014/1539481902_5bc2a12e1b196.png!small)  

第一个例子设置了EAX = 1，执行CPUID指令后检查ECX的第31位值，为1的话则保存在IsUnderVM中。

第二个例子；

![image.png](https://image.3001.net/images/20181014/1539481882_5bc2a11a8a141.png!small)  

第二个个例子设置了EAX =0x40000000，执行CPUID指令后返回的ECX、EDX分别进行比较，类似第一个例子，会把结果保存在IsUnderVM中。

注意这个方法仅仅适用于VMWare，如果你希望探测其他的虚拟化产品如VirtualBx或者Hyper-v，那就要改成这些厂商自己的产品字符串。

下面是第一个实例：

![image.png](https://image.3001.net/images/20181014/1539481864_5bc2a108d7f0d.png!small)  

运行在虚拟机后的结果：

![image.png](https://image.3001.net/images/20181014/1539481852_5bc2a0fc1db3e.png!small)  

然后看看第二个例子在物理机上运行的结果

![image.png](https://image.3001.net/images/20181014/1539481837_5bc2a0ed916ac.png!small)  

对比下第二个例子在虚拟机中运行的结果：

![image.png](https://image.3001.net/images/20181014/1539481823_5bc2a0dfebd35.png!small)  

你可以清楚的看到第二个例子在俩个不同环境下运行的结果是不同的。

**如何对抗？**

你可能会想是否可以更改虚拟机中CPUID指令的返回结果呢？

当然可以，目前流行的虚拟机产品都允许修改客户机中的CPUID指令返回结果和CPU的标志信息，这是因为每当客户机里执行了CPUID指令时，VM_Exit事件就发生了，这就是修改CPUID结果绕过Anti-VM的最佳时间。

WMWare产品中，找到该虚拟机的.vmx配置文件，在最后一行加上

 **cpuid.1.ecx="0---:----:----:----:----:----:----:----"**

然后重启客户机，这样第一个例子的运行结果就和之前相反了：

![image.png](https://image.3001.net/images/20181014/1539481805_5bc2a0cd3ee58.png!small)  

绕过第二个例子方法的，需要在.vmx文件中加上一下两行（可能与你的机器有不同）：

 **cpuid.40000000.ecx="0000:0000:0000:0000:0000:0000:0000:0000"**

 **cpuid.40000000.edx="0000:0000:0000:0000:0000:0000:0000:0000** "

运行后就会得到不同的结果了。

在VirtualBox中想要得到同样的效果的话你可以在这个[页面找到答案](https://superuser.com/questions/625648/virtualbox-how-to-force-a-specific-cpu-to-the-guest)。

在本文中我描述一种对抗Anti-VM的技术，你可以通过这种技术去对抗和分析恶意程序，在后续我还会继续介绍其他的对抗Anti-VM的技术.

