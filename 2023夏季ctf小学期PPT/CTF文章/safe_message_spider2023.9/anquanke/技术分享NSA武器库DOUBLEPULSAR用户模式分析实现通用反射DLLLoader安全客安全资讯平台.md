# 【技术分享】NSA武器库：DOUBLEPULSAR用户模式分析实现通用反射DLL Loader

阅读量 **133959**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-05-22 14:26:12

 **x**

##### 译文声明

本文是翻译文章，文章来源：countercept.com

原文地址：<https://countercept.com/our-thinking/doublepulsar-usermode-analysis-generic-reflective-dll-loader/>

译文仅供参考，具体内容表达以及含义原文为准。

****

翻译：[ **myswsun**](http://bobao.360.cn/member/contribute?uid=2775084127)

**稿费：200RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

  

**0x00 前言**

我们之前分析发布了一篇文章“[DOUBLEPULSAR
payload的内核payload的分析](http://bobao.360.cn/learning/detail/3881.html)”，其细节是关于内核模式shellcode如何使用异步APC注入DLL。然而，实际上内核payload不能做到加载DLL，但是可以设置包含用户模式shellcode的APC调用来实现加载DLL。

我们感兴趣的是这个payload能适用任意DLL，但是没有使用LoadLibrary。避免使用LoadLibrary可以更隐蔽的加载，因为它避免了需要写入文件到磁盘，还能避免LoadLibrary被监控，同时也能避免在PEB（通常包含所有加载的DLL的列表）中留有痕迹。虽然这种方式现在遍地可见，但是目前为止，我们还没注意到任何公开的代码可以用这种方式加载任意DLL的（现有代码需要的自定义构建支持加载的DLL）。DOUBLEPULSAR是不同的，它的实现非常完美，几乎能加载任何DLL。另外，几乎支持任何版本的Windows。

本文的技术细节使用用户模式的DOUBLEPULSAR，且提供了一个测试工具，其充分利用了独立的shellcode，因此很容易看到行为和检测。该工具不使用内核代码，只有用户层的loader来注入任意DLL。尽管这个shellcode有32位的版本，但是目前我们只分析了64位的版本。

  

**0x01 细节**

下面是shellcode的步骤的详细描述。

1\. call-pop被用来自定位，因此shellcode能使用静态偏移

2\. 通过匹配哈希模块名定位需要的API函数，通过哈希函数名匹配导出函数

3\. 解析DLL头得到关键元数据

4\. 如果可能，在优选的基址上分配合适大小的内存。任何以该基址的偏移都被保存，以供后用。

5\. DLL的每个节被拷贝到内存中合适的位置

6\. 处理导入函数，加载依赖库（使用LoadLibrary），填充IAT

7\. 重定位，修复偏移

8\. 使用RtlAddFunctionTable设置异常处理（SEH）

9\. 基于DLL头，设置每个节的内存保护属性为合适的值

10\. 使用DLL_PROCESS_ATTACH为参数调用DLL入口点

11\. 解析需要的序号函数并调用

12\. 得到需要的函数后，使用DLL_PROCESS_DETACH为参数调用DLL入口点

13\. 使用RtlDeleteFunction移除异常处理

14\. 将整个DLL内存设为可写，并清零

15\. 释放DLL内存

16\. shellcode清0自己，除了函数末端，其保证APC优雅的返回

在shellcode开头能看到call-pop组合，下个指令被调用，返回地址立即被移出到寄存器中。这使得代码能找到它自己的地址，并使用该地址的静态偏移来找到它自己的缓冲区。

当进入到一个循环，得到shellcode中偏移0xF0C的值，通过rdx和rcx传入到一个函数中。这个函数将调用find_func，定位shellcode需要的Windows
API函数。得到一个模块名的哈希值（在RDX中）和一个函数名的哈希（rcx中）。因为这些只是名字，他们可以被硬编码，且在不同版本的Windows中不会改变。

从TEB的PebLdr字段中定位到加载的模块，循环搜索模块哈希值。注意模块名哈希通过rdx压入栈，作为一个正常函数的序言，shellcode能从栈中访问它。

当匹配到后，转到函数搜索循环中，和上述方式相同，但是使用的是模块导出表的导出函数名。通过解析内存中的模块头，找到包含各种映像目录入口的RVA的IMAGE_DIRECTORY_ENTRY_ARRAY，其中包含存有导出函数的IMAGE_DIRECTORY_ENTRY_EXPORT。通过加上模块基址，RVA能够转化为真实的地址。PE头的解析在shellcode非常常见。

IMAGE_DIRECTORY_ENTRY_EXPORT结构包含了各种数组的RVA。AddressOfFunctions是导出函数的RVA数组。AddressOfNames这些函数的ASCII名字的平行数组。AddressOfNameOrdinals是另一个包含函数序号信息的平行数组。迭代这些数组能得到需要的函数地址，保存这些函数地址。

函数地址保存在栈中结构中。这个结构用来保存各种东西，如shellcode执行需要的函数指针。通常使用rsi访问它。结构的格式如下，也显示了循环解析的函数（其他值稍后会初始化）。

函数指针在每次调用find_func后被写入这个结构：

你也能通过rbp看见另一个引用结构，在shellcode缓冲区的一个空白内存块中，初始值为0。这个结构显示如下，在shellcode的偏移0x368处。

在定位到shellcode需要的函数后，DLL被复制到新创建的内存中，并清0
shellcode缓冲区。这将导致不能定位到DLL的位置，但是有个临时的位置保存了DLL的原始数据。这充分利用了之前定位的一个函数，kernel32!VirtualAllocStub（VirtualAlloc的一个简单包装）。

DLL的大小来自shellcode末尾写入的值，在shellcode和shellcode缓冲区中的DLL的中间。这是shellcode中仅有的2个自定义的值之一，另个加载DLL后应该调用的函数序号。Shellcode缓冲区的布局如下：

这些值通过开头的pop-call指令来得到相关地址引用，将shellcode缓冲区偏移0x25的地址写入到rbp中。因此我们能在shellcode缓冲区内存中通过[rbp+0xF5D]获取到DLL的大小。

解析DLL头以判断DLL的架构（32位还是64位）。如果是错误的架构，shellcode将停止运行，避免有任何错误。一些有用的值会被保存以供后用，如Section头和IMAGE_DATA_DIRECTORY_ARRAY的指针。

分配加载DLL的空间。这个区域的大小不是DLL的大小，因为它会占用磁盘，但是能从DLL头中的SizeOfImage中获得，以便能正确加载进内存。使用头中优选基址调用VirtualAlloc，但是如果这个不可靠，会在其他地方分配空间。

保存优选基址的偏移，用于重定位。

根据DLL的SizeOfImage字段，将DLL头拷贝到新创建的内存区域。之后，在一个循环中将每个节拷贝到正确的位置。这使用头中的字段NumberOfSections来循环遍历所有的节头，从每个节头中的PointerToRawData、SizeOfRawData和VirtualAddress，定位DLL节的原始数据，并拷贝到加载的DLL中的正确位置。

导入函数现在加载了。在进程的开头，分配另一个内存，但是这只用来给函数用，但是貌似从没使用过。这可能是历史功能，不再需要了。

解析导入表，使用LoadLibrary加载每个库。这个不太隐蔽，但是我么假设用户能避免依赖库，或者只使用Windows库（更可能被忽略，认为是合法库）。使用IMAGE_DIRECTORY_ENTRY_ARRAY中的IMAGE_DIRECTORY_ENTRY_IMPORT定位导入表，其指针早前在解析DLL头时已经保存了。遍历导入表，解析每个库名的偏移并调用LoadLibrary加载它。

每个库的导入函数使用导入表的FirstThunk来确定，其在IMAGE_IMPORT_BY_NAME结构中有个偏移，或者依赖序号。FirstThunk的值是针对位掩码0x8000000000000000（IMAGE_ORDINAL_FLAG64）做检查的；如果设置了这个值，在地位包含序号，否则，是通过名字导入的，且能定位到函数字符串的偏移。然后调用GetProcAddress得到函数地址。

在这个处理过程中，rbp引用的空间被用于临时保存确定的东西，如最新的FirstThunk值和IMAGE_IMPORT_BY_NAME的偏移。

然后再写回地址到FirstThunk中，作为绑定导入。

我们也能看到一个函数调用充分利用了早前分配的神秘的内存。然而，这个调用不可达，因为在这个调用前rax被设为1才调用，如果为0就跳过调用。这很奇怪，因为它似乎是个永远不会用到的函数。

在处理导入函数后，加载的DLL的头中的基地址被更新，以用来我们最终加载真实的基址。

现在处理重定位，以解决关于DLL基址的任何偏移。IMAGE_DIRECTORY_ENTRY_BASERELOC从头中可以找到，用于遍历所有的重定位项，必要时进行重定向。只处理IMAGE_REL_AMD64_ADDR32NB,
IMAGE_REL_AMD64_SECTION 和 IMAGE_REL_AMD64_ABSOLUTE的重定位。

遍历每个重定位表，得到每块的入口，检查头4个字节以判断重定位的类型。根据类型，后12字节作为重定位的值，并且将重定位值用于更新基于优选基址的偏移。

使用IMAGE_DIRECTORY_ENRTY_EXCEPTION和调用RtlAddFunctionTable设置异常处理。

根据Section头，调用VirtualProtect将每个节的内存保护属性设为合适的值。

使用头中的AddressOfEntryPoint定位到DLL的入口点，然后以DLL_PROCESS_ATTACH（值为1）为参数调用函数入口点让DLL知道被加载了。完成过程如下：

现在DLL被加载了，需要调用的函数的序号也得到了，调用该函数。使用从自定位的call-pop指令中的地址获得序号值，和之前的DLL大小一样，但是这是在shellcode缓冲区偏移0xF86处。

从DLL头中得到序号基值，这是库中的序号的起始值。将所需要的序号减去起始值能得到位于导出函数数组AddressOfFunctions中的任意函数的索引。这提供了函数的RVA，加上基址就得到了函数的真实地址。

函数有一些栈空间和寄存器rcx，rdx和r8中的参数。当然如果函数不需要任何参数，这些参数的存在和栈空间将会不同，但是任何自定义的DLL可能希望利用这些。Shellcode返回值保存在栈中，即使它从不被使用。

在函数返回后，清理。卸载dll，并清零内存。首先使用DLL_PROCESS_DETACH(值0)为参数调用函数入口点。

使用RtlDeleteFunctionTable清理异常处理。

将DLL内存设为可写，以便清零，然后释放内存。VirtualProtectStub需要一个指向lpflOldProtect参数的可写指针，即使我们不关心它的值，但是必须提供，因此使用rbp引用的空间。

然后shellcode清零自身，除了一个允许函数正确返回的函数结语。这是这种方式的一个小缺陷。

  

**0x02 内存痕迹**

在使用DOUBLEPULSAR执行DLL加载后，有大量的内存痕迹能用于检测。首先在开头分配的内存中，从shellcode缓冲区中拷贝DLL从来没被清零或释放。这有点不同寻常，因为只要稍微处理下就能做到清除内存，甚至这块内存区域的权限还保留了PAGE_EXECUTE_READWRITE，和整块DLL的拷贝。

事实上，这块内存区域不需要执行权限，因为它只用于读写。这非常奇怪，因为可读可写可执行的全些是非常值得怀疑的，在合法进程中很少需要这个。通常只在漏洞利用中使用。同时未修改的MZ头更加让人怀疑。而且，这块内存似乎并不一定需要，因为只需使用自定位的call-pop指令就足够从shellcode缓冲区中直接加载DLL。

也可能这块内存区域是由一个老的不复杂的反射加载器遗留的，使用新技术后它没有被重构。不管怎样，在内存中你将得到一个可以的包含DLL拷贝的内存区域。如果payload执行多次后你将看见几个这种内存区域、

另一种内存痕迹更加难于避免。就是通过APC调用执行的shellcode的主函数的结语。因为需要确保函数返回清理，且要避免进程崩溃。尽管有方法使它更小，但是完全避免还是很有挑战性。

当你看到具有PAGE_EXECUTE_READWRITE权限的几乎包含全是0的内存区域时，在偏移0xF70处的内容如下：

在这之后，是两个32位的整数，第一个是注入的dll的大小，第二个是DLL中执行的序号。当然这两个值每次都会不同，不能作为静态特征。但是可以用来处理执行的DLL（一直在RWX的内存块中）和DLL中执行的函数。

  

**0x03 测试用户模式的DOUBLEPULSAR注入器的payload**

我们发布了小的测试工具以用于调用DOUBLEPULSAR payload的用户模式的DLL加载机制。将使用shellcode注入一个DLL到你选择的进程中。

有趣的是，shellcode足够通用，能以各种方式触发。举个例子，该工具使用相似的方式插入一个用户模式的APC到内核payload中，但是也可以使用CreateRemoteThread等更常见的DLL注入方式触发shellcode（但是不能避免使用LoadLibrary）。

下面截图是工具的使用，注入DLL到calc.exe进程中弹出对话框。

执行后，能看到两块PAGE_EXECUTE_READWRITE属性的内存区域。

这些区域中的一个是几乎都是0，但是在0xF70处有个小的结语。另一个包含了原始的DLL。

本文翻译自countercept.com [原文链接](https://countercept.com/our-thinking/doublepulsar-usermode-analysis-generic-reflective-dll-loader/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **root** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86138](/post/id/86138)

安全客 - 有思想的安全新媒体

本文转载自: [countercept.com](https://countercept.com/our-thinking/doublepulsar-usermode-analysis-generic-reflective-dll-loader/)

如若转载,请注明出处： <https://countercept.com/our-thinking/doublepulsar-usermode-analysis-generic-reflective-dll-loader/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) root

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

