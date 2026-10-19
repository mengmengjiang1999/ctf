## ****背景概述****

近日，深信服安全团队追踪一则Windows 10 condrv.sys存在内存损坏漏洞的信息， ** **漏洞等级**** ** **为**** **
**高危**** 。该漏洞是由于Windows 10中condrv设备不正确的设置导致异常。

攻击者可利用该漏洞，通过在浏览器的地址栏中打开特定路径或构造恶意快捷方式进行钓鱼攻击，最终导致Windows 10蓝屏崩溃。

 ** **该漏洞当前暂无官方解决方案，**** ** **深信服**** **
**EDR轻补丁功能第一时间支持免疫该漏洞，EDR用户可升级至V3.2.33版本，开启轻补丁漏洞免疫功能进行一键防护**** 。

##  ** **漏洞**** ** **分析****

调试查看漏洞堆栈：

![](https://image.3001.net/images/20210121/1611199495_6008f407c2b2769c0addc.png!small)

从堆栈可以看出当打开此路径的时候，进入内核的对象管理器依次解析对象目录，直到解析到\device\condrv发现这是个设备对象，且设备对象类型是有ParseProcedure例程的。

故调用设备对象的ParseProcedure，即函数IopPraseDevice。函数内部在处理完请求时尝试去关闭这个文件对象，如下图：

![](https://image.3001.net/images/20210121/1611199509_6008f4151d3a17c1aa9dd.png!small)

关闭文件对象就会对相应的驱动发送IRP_MJ_CLEANUP IRP，驱动为condrv.sys。

蓝屏的直接原因如下：

![](https://image.3001.net/images/20210121/1611199522_6008f422c885307403d87.png!small)

即从IRP中获取文件对象FILE_OBJECT，然后获取FILE_OBJECT的FCB即FsContext成员。但此时FsContext为NULL，所以就导致了空指针引用的问题。

![](https://image.3001.net/images/20210121/1611199533_6008f42d39868e5b1867a.png!small)

##  ** **根因分析****

我们可以认为这个文件对象是“非法”的, 那么可能从创建初始化的时候就可能出现问题。

对内核有了解的应该知道，如果要引用设备对象那么必然会对设备对象所在的驱动发送IRP_MJ_CREATE。我们找到condrv.sys
使用IDA载入，查看反汇编如下：

![](https://image.3001.net/images/20210121/1611199580_6008f45c32669fae67f51.png!small)

它会循环比较文件名是不是预定义的几个，如果是，则调用预定义的创建回调函数，如下：

![](https://image.3001.net/images/20210121/1611199592_6008f468d2b3139276f97.png!small)

Poc里面打开的是kernlcontect所以IRP_MJ_CREATE最终会调用函数CdCreateKernelConnection， 查看该函数如下：

![](https://image.3001.net/images/20210121/1611199607_6008f477561716272d75d.png!small)

第一个判断是如果先前模式是usermode则返回0xc000022，即拒绝访问；也就是设计之初内核是不允许用户直接使用这个符号链接的。

但是问题出就出在这个直接返回拒绝，因为这是在处理IRP。它没有设置IRP的状态码以及调用IoCompleteRequest结束IRP。导致当IRP返回时，其IoStatus.Status为0。（0表示成功）

![](https://image.3001.net/images/20210121/1611199631_6008f48f59448daa32bf3.png!small)

而在函数IopPraseDevice中是以IoStatus.Status为准,所以IopPraseDevice
错误的认为IoCalldriver是成功的，进而引发后续错误地关闭文件对象从而导致蓝屏。手动测试修改IoStatus.Status为失败值，蓝屏消失。

##  ** **总结****

通过详细的根因分析可以得到漏洞的成因，是由于condrv的驱动开发人员在处理IRP例程的时候，没有正确处理IRP，对失败情况忘记设置状态码，从而导致系统崩溃。

##  ** **影响范围****

目前受影响的操作系统版本：Windows 10

##  ** **官方解决方案****

产品当前官方暂未发布受影响版本的对应补丁，建议受影响的用户及时关注更新官方的安全补丁（及时更新升级到最新版本）。链接如下：<https://www.microsoft.com/zh-cn/software-download/windows10>

