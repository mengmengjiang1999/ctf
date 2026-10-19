***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **微软近日对外披露了两个0day漏洞详情，其中一个漏洞存在Adobe阅读器中，可被利用导致任意代码执行；另一个漏洞则允许任意代码在Windows
kernel内存中提权执行。**

微软称由于该漏洞利用目前还处于初期阶段，且官方都已发布了补丁，建议大家及时进行安装，赶在被大规模利用前修复，未雨绸缪。同时，建议排查初期样本的IOC（文末附修复补丁链接和IOC）。

**CVE** | CVE-2018-4990 | CVE-2018-8120  
---|---|---  
**类型** | 远程代码执行 | 本地提权  
**官方评级** | Critical | Important  
**影响产品** | Acrobat DCAcrobat Reader DC | Windows 7Windows Server 2008  
**POC** **样本** | 有 | 有  
**在野攻击** | 暂无 | 暂无  
**修复补丁** | 有 | 有  
  
这两个漏洞利用样本最早是由ESET分析人员在今年3月发现并报告给了微软，在ESET和微软的共同努力下发现了以上两个0day漏洞。以下漏洞利用分析过程是基于以下样本进行：  

SHA-256:4b672deae5c1231ea20ea70b0bf091164ef0b939e2cf4d142d31916a169e8e01

##  **漏洞利用概况**

Adobe Acrobatand Reader漏洞存在于PDF文档中，伪装成暗含JavaScript漏洞利用代码的恶意JPEG
2000图像，漏洞利用路径如下图所示：

![fig-1-overview-exploit-process.png](https://image.3001.net/images/20180705/15307655969858.png!small)

图1. 漏洞利用流程图

如上图所示，漏洞利用过程分以下阶段：

1.JavaScript枚举堆喷射（heap spray）内存；

2.恶意JPEG 2000图片触发一个越界访问操作；

3.一旦堆喷射枚举越界内存，就会调用访问操作；

4.访问操作导致vftable进程崩溃；

5.已崩溃的vftable进程将代码执行转移至返回导向编程（ROP）链；

6.ROP链将代码执行转移到shellcode；

7.通过反射DLL加载来进行EoP模块加载；

8.PE模块启动已加载完成的Win32k EoP漏洞利用程序；

9.一旦EoP漏洞利用成功，就会在Startup文件夹中释放一个名为.vbs的文件，作为下载其他payloads的PoC恶意软件。

###  **恶意JPEG 2000图片**

恶意图片中被嵌入了以下恶意标签，如图：

![fig-2-malicious-JPEG-2000-stream.png](https://image.3001.net/images/20180705/15307656262695.png!small)

图2. 恶意JPEG 2000图片

下图所示的CMAP &
PCLR标签中均含有恶意值，CMAP数组(0xfd)的长度小于PCLR标记中引用的索引值（0xff），从而导致了越界内存释放漏洞的利用。

![fig-3-out-of-bounds-index-CMAP-array.png](https://image.3001.net/images/20180705/15307657197613.png!small)

图3. CMAP数组的越界索引  

结合JavaScript中的堆喷射技术，越界漏洞利用就会导致vftable进程的崩溃。

![fig-4-vftable-corruption-ROP-chain-to-code-execution.png](https://image.3001.net/images/20180705/15307657883035.png!small)

图4. ROP链中的vftable进程崩溃导致代码执行

JavaScript中的编码包含了shellcode和PE模块。

![fig-5-shellcode-in-javascript.png](https://image.3001.net/images/20180705/15307658045145.png!small)

图5. JavaScript中的shellcode

###  **反射DLL加载进程**

Shellcode（以下提到的伪代码）通过反射DLL加载PE模块，这是高级攻击活动里试图在内存中躲避检测时的常用技巧。Shellcode搜索PE初始记录，解析PE分区，并将它们复制到新分配的内存区域，然后将控制权传递给PE模块中的入口点。

![fig-6-copying-PE-sections-to-allocated-memory.png](https://image.3001.net/images/20180705/15307658211004.png!small)

图6. 复制PE分区到新分配的内存中

![fig-7-passing-control-to-an-entry-point-in-the-loaded-dll.png](https://image.3001.net/images/20180705/15307658411641.png!small)

图7. 把控制权传递给已加载的DLL模块中的入口点

###  **Win32k** **提权漏洞利用**

Win32k提权（EoP）漏洞利用是从已加载的PE模块中运行，利用新的Windows漏洞CVE-2018-8120对Windows 7
SP1系统进行攻击，Win 10及更新的产品不受该漏洞影响。该漏洞利用NULL页面来传递恶意记录，并将任意数据拷贝至任意内核位置，对于运行Windows
8及更新系统的x64位平台所受影响也相对较小。

![fig-8-EoP-exploit-flow.png](https://image.3001.net/images/20180705/15307658548188.png!small)

图8. EoP漏洞利用流程图

漏洞利用的主要过程如下：

1.漏洞利用根据sgdt指令调用NtAllocateVirtualMemory进程，以便在NULL页面分配虚假的数据结构；

2.把格式错误的MEINFOEX结构传递至SetImeInfoEx Win32k 内核函数；

3.SetImeInfoEx进程获取NULL页面上的虚假数据结构；

4.使用虚假的数据结构把恶意指令拷贝到GDT（全球描述符表）上的+0x1a0中；

5.通过调用FWORD指令来调入虚假的GDT入口指令；

6.成功调用虚假GDT入口指令；

7.这些指令运行从内核模式内存空间的用户模式中分配的shellcode；

8.修改shellcode进程中EPROCESS.Token，获取SYSTEM权限。

格式有误的IMEINFOEX结构结合NULL页面的虚假数据，就可导致GDT入口崩溃，如下图所示：

![fig-9-corrupted-gdt-entry.png](https://image.3001.net/images/20180705/1530765876714.png!small)

图9. GDT入口崩溃

已损坏的GDT具有通过调用FWORD指令调用入口运行的实际指令。

![fig-10-patched-gdt-entry-instructions.png](https://image.3001.net/images/20180705/15307658919692.png!small)

图10. 已修复的GDT入口指令

从这些指令返回后，EIP（扩展指令指针）返回具有内核特权的用户空间中的调用者代码，后续代码将通过修改SYSTEM的进程令牌来实现当前进程的提权。

![fig-11-process-token-pointer.png](https://image.3001.net/images/20180705/1530765904133.png!small)

图11. 替换进程令牌指针

###  **可持续性**

提权后，漏洞利用代码会在本地Startup文件夹中释放一个.vbs文件，即PoC恶意软件。

![fig-12-code-that-drops-the-vbs-file-to-the-startup-folder.png](https://image.3001.net/images/20180705/15307659375494.png!small)

图12. 释放.vbs文件到Startup文件夹的代码信息

###  **防御建议**

及时部署针对以上0day漏洞的安全补丁：

CVE-2018-4990 | Adobe Acrobatand Reader可用的安全更新 | APSB18-09

<https://helpx.adobe.com/security/products/acrobat/apsb18-09.html>

CVE-2018-8120 | Win32k提权漏洞

<https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8120>

如工作环境不需要，则禁用Adobe Acrobat and Acrobat Reader中的JavaScript；

加强终端对利用PDF附件进行鱼叉式钓鱼攻击和其他社工攻击的防范意识。

###  **IoC信息** （SHA-256）：

d2b7065f7604039d70ec393b4c84751b48902fe33d021886a3a96805cede6475

dd4e4492fecb2f3fe2553e2bcedd44d17ba9bfbd6b8182369f615ae0bd520933

4b672deae5c1231ea20ea70b0bf091164ef0b939e2cf4d142d31916a169e8e01

0608c0d26bdf38e064ab3a4c5c66ff94e4907ccaf98281a104fd99175cdf54a8

 ***参考来源：[Microsoft
Cloudblogs](https://cloudblogs.microsoft.com/microsoftsecure/2018/07/02/taking-apart-a-double-zero-day-sample-discovered-in-joint-hunt-with-eset/)，秋雨绸缪编译，转载请注明来自FreeBuf.COM**  

