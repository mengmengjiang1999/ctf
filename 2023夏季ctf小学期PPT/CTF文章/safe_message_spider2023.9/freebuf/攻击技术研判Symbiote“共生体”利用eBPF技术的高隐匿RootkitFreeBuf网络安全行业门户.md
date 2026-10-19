## **情报背景**

Symbiote意为“共生体”，区别于一般的恶意程序，Symbiote没有独立的二进制，而是以共享库so文件的形式寄生于受感染的进程中。作为一个用户态Rootkit,Symbiote从文件、进程、流量等层面对自身进行了隐藏，使其成为分析者眼中“几乎不可能检测的威胁”。本文将对Symbiote中使用的防御规避技术进行分析研判，重点剖析其进程劫持隐匿与eBPF注入技术。

![1660209101_62f4c7cd49d3e94f308ed.bmp!small?1660209104168](https://image.3001.net/images/20220811/1660209101_62f4c7cd49d3e94f308ed.bmp!small?1660209104168)

图 Symbiote的检测对抗手段

 **组织名称**

|

未知  
  
---|---  
  
 **相关工具**

|

Symbiote  
  
 **战术标签**

|

防御规避  
  
 **技术标签**

|

LD_PRELOAD、eBPF  
  
 **情报来源**

|

https://www.intezer.com/blog/research/new-linux-threat-symbiote/  
  
##  **01** 攻击技术分析

 **亮点1：LD_RRELOAD劫持加载并在ldd中隐藏**

为了将自身注入合法进程，symbiote使用了名为LD_PRELOAD（T1574.006）的攻击方式，将自身路径设置为LD_PRELOAD的环境变量，植入所有运行中的进程内。通过这种方式Symbiote对一系列重要API进行hook，达到执行恶意逻辑和隐藏自身的目的。

通过对execve的hook，Symbiote实现对所有进程创建行为的监测。并对LD_TRACE_LOADED_OBJECTS变量设置为1的进程的输出进行篡改。

![1660209137_62f4c7f1d76bde0cf2a8b.png!small?1660209139315](https://image.3001.net/images/20220811/1660209137_62f4c7f1d76bde0cf2a8b.png!small?1660209139315)

图 对环境变量进行检测

![1660209154_62f4c8028ce850357e9fa.png!small?1660209155943](https://image.3001.net/images/20220811/1660209154_62f4c8028ce850357e9fa.png!small?1660209155943)

图 从输出结果中隐藏自身

LD_TRACE_LOADED_OBJECTS环境变量将使得动态链接器ld.so检视程序所有的动态链接库，并在控制台打印。Ldd正是利用该原理获取程序所有依赖的bash脚本，本身只完成了设置环境变量的工作。因而监视该环境变量可对这类获取动态依赖的工具进行有效识别和规避，隐藏自身存在。

![1660209166_62f4c80e7a288142a72e9.png!small?1660209167958](https://image.3001.net/images/20220811/1660209166_62f4c80e7a288142a72e9.png!small?1660209167958)

图 LD_TRACE_LOADED_OBJECTS环境变量使动态链接器ld.so输出动态库信息

 **亮点2：利用eBPF篡改流量完成流量隐藏**

BPF（Berkeley Packet
Filter）是类Unix系统数据链路层的一种原始接口，提供原始链路层封包收发。Tcpdump等用户态网络监控程序可通过提供一个过滤程序对所有网络数据包进行过滤，该过滤程序将在内核态虚拟机执行，减少从内核态向用户态拷贝数据的性能损失。eBPF（extended
Berkeley Packet Filter）则基于经典BPF进行了重构，增加了JIT等现代化的功能。

自NSA武器库泄露的高隐匿后门Drewdrop是利用eBPF技术进行隐蔽通信与流量隐藏的典型代表。在此类后门中，eBPF被用于在内核层面对所有流量进行监听和篡改，等候来自控制端的触发解析其中的指令并执行。由于不创建对外连接或监听端口，相较于传统后门具有较强的隐蔽性。

![1660209179_62f4c81bc73ed65fe1d2d.png!small?1660209181313](https://image.3001.net/images/20220811/1660209179_62f4c81bc73ed65fe1d2d.png!small?1660209181313)

图 植入的eBPF 字节码片段

Symbiote通过劫持setsockopt函数对eBPF字节码加载过程进行劫持，在待执行的eBPF字节码之前拼接额外代码。这些额外代码将Symbiote相关的通讯端口的流量进行了隐藏，这使得tcpdump等网络嗅探工具无法捕获到其通讯流量，达到流量隐藏的目的。

##  **02** 总结

作为高隐匿的新型Linux后门木马，Symbiote以其防御规避技术见长，对文件、进程和流量层的常见检测点进行了针对性对抗。基于环境变量的检测方式，有效识别了ldd在内的一类依赖ld.so特性的依赖库检测工具，成功规避了针对动态链接库的监测。动态劫持并注入eBPF字节码的操作在篡改结果的同时保留了其他正常流量，更不易引起分析人员警惕，也是一种值得警惕的eBPF利用手法。

