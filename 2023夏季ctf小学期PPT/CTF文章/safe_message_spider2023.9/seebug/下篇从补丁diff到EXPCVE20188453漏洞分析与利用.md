**作者：ze0r @360A-TEAM  
公众号：[360安全监测与响应中心](https://mp.weixin.qq.com/s/dcbUeegM0BqErtDufOXfoQ
"360安全监测与响应中心")  
相关阅读：[[上篇]从补丁diff到EXP--CVE-2018-8453漏洞分析与利用](https://paper.seebug.org/784/
"\[上篇\]从补丁diff到EXP--CVE-2018-8453漏洞分析与利用") **

CVE-2018-8453漏洞是一个Windows内核提权漏洞，由卡巴斯基官方于野外发现用于APT中攻击中东地区国家。

### 相关链接：

微软官方的补丁和漏洞简介可以看链接：<https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2018-8453>

卡巴斯基的分析文章链接：<https://securelist.com/cve-2018-8453-used-in-targeted-attacks/88151/>

_文末附本文相关EXP下载链接_

### 正文内容

在CVE-2018-8453分析得上篇中--[[[上篇]从补丁diff到EXP--CVE-2018-8453漏洞分析与利用]](https://paper.seebug.org/784/ "\[\[上篇\]从补丁diff到EXP--CVE-2018-8453漏洞分析与利用\]")，我们已经分析了漏洞成因，知道它是一个double-free类型的漏洞。本篇中，我们将利用这个漏洞获取SYSTEM最高权限。

我们知道，双重释放类型的漏洞，可以给我们一个多释放一次内存的机会。通过上次分析，我们发现释放的目标内存—SBTrack仅仅0x50大小，无论是利用Bitmap还是Palette对象，空间都严重不够：

![ ](https://images.seebug.org/content/images/2019/01/66010fdc-cb50-4dcf-9b5f-d4e5856400f5.jpg-w331s)

这里为了方便已经在SBTrack申请的时候，直接断点并将内存地址赋值给了伪寄存器$t0（下同）：

ba e 1 win32kfull!xxxSBTrackInit+0x59 ".echo SBTrack INIT;r eax;r
@$t0=@eax;g";

由于空间根本不够我们去部署一个GDI对象，所以需要想办法扩展这个空间。在内存管理中，对于这种动态划分的内存块，无法预知大小，就是用户态的堆、内核态的池。所以给了我们一个可利用的机会，就是虽然申请时是0x50大小，但释放时只是按照内存管理机制来释放，没有判断内存大小释放已经改变的方法。所以我们可以在第二次释放前，可以让这块内存为任意大小，也就是在二次释放前，我们重新申请到这块内存，并且申请时是一个足以容纳Palette的大小（由于bitmap在win
10 RS2中已经更改修复，所以我们选择Palette对象）。从而实现扩展目标内存大小的目的，我们想要达到如下效果：

![ ](https://images.seebug.org/content/images/2019/01/a743f6a0-5b57-4ead-be6a-949459211150.jpg-w331s)

下面来看代码实现。在系统分配池内存的时候，会按照0x1000大小来调拨内存。为了避免干扰，我们首先申请大量大块内存，让系统调拨到新的页面：

![
](https://images.seebug.org/content/images/2019/01/449d4e9e-014e-4ce9-a171-b984dee9faac.png-w331s)

每次都申请0xC10大小的内存，这么大的内存块，在系统已调拨的页面已经被占完时，只能调拨新的内存页来满足申请，而一个页面剩下的空间0x1000-0xC10不足以满足下一次申请，所以造成的结果就是每个页面都只有一个0xC10大小的空间。之后申请内存占用余下的部分，这里说一下，系统池分配的机制是，第一次在最上面，第二次在最下面，之后再申请就是从第二个往上（地址小的方向）挨个排开：

![
](https://images.seebug.org/content/images/2019/01/5b813fa1-75d7-4a06-845a-d37bc3a5eb1d.png-w331s)

这会导致一个页面中，只在中间留下了0x50大小空间。就如上图（以后均指红色那个理想图）中第二个情形。这里已经满足我们的要求，但是SBTrack不一定会放在我们部署好的页面中，因为系统中本来就存在0x50大小的间隙。所以之后我们再申请0x50大小内存，用以填补系统中本来的0x50大小间隙：

![ ](https://images.seebug.org/content/images/2019/01/ba043d00-f940-42db-aba8-8055a4a40bd4.png-w331s)

这里在申请了3000个0x50大小后，又释放了2000/2个内存，而且是跳一个释放一个，这造成一个页面是满的、相邻下一个又是有空余的，这样挨个依次排开。接下来发送消息让系统分配SBTrack，根据我们空一页、满一页的布局，SBTrack只能在这其中之一，想跑都跑不了：

![ ](https://images.seebug.org/content/images/2019/01/a024edea-ff6c-432e-a870-605ef42e7b31.png-w331s) ![
](https://images.seebug.org/content/images/2019/01/b32ff6d4-5bf9-46d2-b8dd-be8340862cff.png-w331s)

之后就是在回调到用户态中，更改FNID、SetCapture等操作释放真正的SBTrack。这里注意一下，在fnDWORDCallBack函数中，用于退出xxxSBTrackLoop函数的SetCapture调用，在各个版本的EXP中位置稍有不同，只是因为各个版本中系统对fnDWORD回调不大一样，但目的都是为了退出循环，不用在意：

![
](https://images.seebug.org/content/images/2019/01/d4088c17-bcf8-419f-a414-876af71efaae.png-w331s)
![
](https://images.seebug.org/content/images/2019/01/b8baa77a-f206-4e2d-8bcb-d062a1620f3b.png-w331s)

在发送了WM_CANCELMODE消息后，系统已经释放了真正的SBTrack，此时目标页面的布局如上图中第四种情形：

![
](https://images.seebug.org/content/images/2019/01/ac098ee8-c4c4-41c8-b288-694c71997e83.png-w331s)

可看到中间的SBTrack已经被释放，但上面的c10和下面的3a0还在，之后释放掉下面的0x3a0，由于系统管理机制要避免碎片化，以尽量满足以后大块内存申请。所以系统会对相邻的free的内存整合为一个大块0x3f0：

![
](https://images.seebug.org/content/images/2019/01/ca5f3483-da2d-4e32-99ff-1c7b406ff42c.jpg-w331s)

现在已经满足了我们理想图中的倒数第二种情形。我们已经把一个0x50大小的内存转化成了0x3f0大小的内存，这足以容纳我们的Palette对象。回翻一下漏洞分析中，在之后回到内核态后，系统会继续释放d2aabc10这块内存。所以我们在这里放的任何对象，都会被释放。那么放什么合适呢？

这里说一点故事，本人一开始想在这里直接放一个Palette更改掉大小来完成利用，在各种尝试后发现，这思路根本不对，这个坑的结果是：Palette如果被释放了，那么会在它源GDI
header的handle处（第一个DWORD）写上内存管理结构。这造成的结果是，虽然内核的句柄表还有这个句柄项，内存也指向正确，但是你却不能操作它，因为会在验证句柄阶段直接发现异常杀死线程。在苦苦分析后依然不得其法，所以只好寻找另一条路径。

这里总结一下，我们现在拥有了一个释放任意对象的能力。只需要找到一个对象：首先它是要在页会话池中分配的，然后需要用户态可以指定它的整体大小，再然后需要有API可以操作它，可以读写它的内存
----至少要可写它的内存。苦苦搜索后，没有发现。然后想到，如果有一个对象，即使它本身不是在页会话池中分配的，但如果它的某个成员是在页会话池中分配、可以控制大小、有API可以对这个成员的内存进行读写那也可以完成目的。很幸运，依据这个想法，本人找到了一个在网上并没有公布的一个系统调用：
NtGdiSetLinkedUFIs：

![
](https://images.seebug.org/content/images/2019/01/dcdb5e0f-00e8-455b-8ba3-e0dbc78abb77.jpg-w331s)

该函数首先根据a3在内核池中用PALLOCMEM2临时申请了内存，之后判断后进入了59行的XDCOBJ::bSetLinkedUFIs函数：

![
](https://images.seebug.org/content/images/2019/01/75a6f789-0c97-4b33-8ee7-7c30641fc5f0.jpg-w331s)

可以看到第11行的V5来自于该对象0xe0处的一个成员。而如果为零的话，则直接到了36行（其中a3来自于上层调用又来自于API调用的参数）调用PALLOCMEM2申请了一块用户指定大小乘以8大小的内存，只要简单看PALLOCMEM2函数的第二个参数是个tag就知道这个肯定也是在页会话池中。之后就把申请到的内存放在了0xe0处，并且在跳到19行后在自身成员中保存了a3。其中重要的是17行的memcpy，它的a2来自于上层的用户指定
----这意味着我们可以直接控制往E0处所指的内存写任意字节，完全没有改变！而如果是第二次调用此API，则根据API的参数来判断是要新申请更大内存还是直接更改已保存的内存
----这意味着我们可以第二次直接平坦的写目标内存！这完全满足我们的需求！再回头仔细看看NtGdiSetLinkedUFIs，第一个参数是一个HDC对象，第二个参数是要写的内容，第三个参数就是要写的字节数除以8。

所以利用思路如下图：

![
](https://images.seebug.org/content/images/2019/01/27fa75cb-520b-4132-ad3a-8673d4e2f1d0.png-w331s)

大致思路有了，但上面提到过，GDI对象本身头部的handle如果验证错误，线程会被杀而导致利用失败。而我们对目标内存没有读能力（其实还有另一个系统调用NtGdiGetLinkedUFIs可以用来读内存，但测试时发现首先判断了另一个成员变量，有兴趣的读者可以深入看下这个成员），所以这里需要做一点小变动，在不改动Palette前四字节的要求下，改动Palette的大小。这里提一下，palette的大小字段位于对象的0x14处：

![
](https://images.seebug.org/content/images/2019/01/f3b9c2a5-779c-40a5-8c83-a117805bb843.png-w331s)

这里eca8cc1c处的0x28就是本Palette对象的元素个数（大小），而前面的0x501是它的版本号，这里是个固定值。所以我们只需要让目标BYTES区域对准eca8cc18即可，这样写内存更改掉eca88c1c处为0xffff即可（这也是一开始申请0xC10大小而不是0xc00的原因）！

那么利用过程就变成了这样：

![
](https://images.seebug.org/content/images/2019/01/55d97bd5-c871-4c3a-bba1-77b877d41827.jpg-w331s)

这样申请palette对象后，原来的BYTES区域其实指向的是某个Palette对象+0x10的地方，正好对准了对象大小的成员。另外这里说一点，在上图中，释放了0xC10后，由于本页面已经全部都释放状态，系统其实是会回收释放整个页面，整个页面变成了未分配状态。之后再次申请0xC00大小时，这个页面又被重新调拨分配了。而这里有个小坑就是由于目标页面被释放，同时又大量申请Palette对象，这很大几率造成本页面被分配用作二级句柄表了，避免这个意外的办法就是提前申请大量对象，让系统早分配句柄表，避免干扰我们的布局：

![
](https://images.seebug.org/content/images/2019/01/fed88cb7-b7b0-4561-84ed-670670e7b13d.png-w331s)

回到主题，按照思路，我们首先申请0x3f0大小的BYTES区域：

![
](https://images.seebug.org/content/images/2019/01/f60a2d46-3a91-496f-92bd-b5e9577f8158.png-w331s)

之后返回到内核态中，目标内存被释放：

![
](https://images.seebug.org/content/images/2019/01/7c0cec16-6e2b-47b1-a5e1-198991eb5ace.jpg-w331s)

可以看到原SBTrack内存区域被释放（Usst）后，被再次分配（Gadd），最后又被释放的过程（Free状态的Gadd）。之后，我们就再次申请0xC00并且继续申请要被越界的Palette：

![
](https://images.seebug.org/content/images/2019/01/8c4ff858-5dd4-4466-866f-87a685c8ba9a.png-w331s)
![ ](https://images.seebug.org/content/images/2019/01/c36e0bfc-fdba-41ff-becf-61b655e6b883.png-w331s)

这里可以提一下，就是为什么不是理想中的C00大小而是0xB30，这里主要是考虑到，在申请越界Palette的过程中，系统其他进程也可能需要使用内存，如果正好碰到这种情形，那我们布局就会乱。所以这里预留下刚好不够一个Palette的空间，即使系统其他进程也同时申请了内存，也是会被放在前几个0xd0空隙中。最后布局如上图，这完全符合我们的需要，并且保证成功率（本人测试下，布局100%成功）！

之后调用NtGdiSetLinkedUFIs系统调用更改掉b4c21c00处Palette的大小：

![
](https://images.seebug.org/content/images/2019/01/e25ac6b9-5e6a-4a0a-a912-fa5c3608572c.png-w331s)

![
](https://images.seebug.org/content/images/2019/01/227f8961-0e43-4cf3-84e6-d28dd2b4f293.png-w331s)

![
](https://images.seebug.org/content/images/2019/01/15e13a13-08bf-4bf3-8482-328091495e13.png-w331s)

现在我们已经有了一个越界的Palette。但由于这个Palette内存地址是交叉的，所以我们还是尽量少用这个Palette，尽早切换到一个新的Palette。利用这个Palette更改下一个Palette作为Manager，再下一个作为Worker：

![ ](https://images.seebug.org/content/images/2019/01/e70e89ad-bd97-4c1a-b281-f953e8bc7f06.png-w331s)

之后就是常规操作，获取SYSTEM进程EPROCESS->获取本进程EPROCESS->复制TOKEN-->创建新进程->恢复本进程TOKEN，不再赘述：

![
](https://images.seebug.org/content/images/2019/01/196d38d1-2bcc-4618-b8a1-eb594df4e395.png-w331s)

![
](https://images.seebug.org/content/images/2019/01/0264b8dd-47a7-4567-ae5e-778161ce6e02.png-w331s)

至此，我们已经有了一个SYSTEM权限的进程。但是系统中还存在一个有问题的HDC的句柄，这个DC对象的某个成员释放会造成BSOD。在逆向了这个对象的方法后，有两个思路：一是直接找到对象，把0xe0处直接改成0即可，但这个涉及的问题是如何通过句柄找到对象地址？二是在系统的句柄表里直接找到这一项，清零。但同样的问题，如何句柄表中找到这一项？网络翻找文章，也没找到WIN10下可用的具体方法。查看win32kfull.sys+win32kbase.sys发现，这个XDCOBJ对象从句柄得到对象地址会经过HmgLockEx函数（所有GDI对象都经过这个函数转换），而该函数又各种转换。没有心思深入，即使继续深入代码也难以实现查找。于是换了一个思路：在退出进程前，先释放掉交叉的Palette，这造成XDCOBJ+0xe0处成员指向了一个Free的内存。然后再次申请大量的AcceleratorTable，这就把一个查找GDI对象的问题换成了查找普通用户句柄的问题！然后释放掉DC句柄。此时，句柄表中有一个AcceleratorTable对象指向了Free的内存。那么这个AcceleratorTable句柄如何找到呢？

在NtUserDestroyAcceleratorTable中，主要通过HMValidateHandle来获取AcceleratorTable地址，它的主要转换过程如下：

![
](https://images.seebug.org/content/images/2019/01/994a805f-a48c-4000-a0dd-3d962f15016f.png-w331s)

其中gSharedInfo+8在win10上固定为0x10，则计算方法为：*gpKernelHandleTable + 8 * (handle &
0xffff)。那么只剩最后一个问题：gpKernelHandleTable的值如何得到？由于这是win32kbase.sys的全局变量，获取win32kbase.sys+偏移的方式？一是有通用性的问题，二是获取win32kbase.sys加载地址也麻烦，所以换一个方法。我们回到HMValidateHandle函数中，这个转换过程就直接有gpKernelHandleTable。所以我们采用搜索的方式，那么它的上层函数NtUserDestroyAcceleratorTable地址如何得到呢？

由于这是直接的系统调用，所以肯定在win32k!W32pServiceTable中，查找资料发现这个调用表可以在KeServiceDescriptorTableShadow+固定偏移中找到，而KeServiceDescriptorTableShadow虽然没有导出，但它固定在KeServiceDescriptorTable-0x40处。所以这就找到了一条可通行的路径：

![
](https://images.seebug.org/content/images/2019/01/ca38a411-d422-4e0f-814e-b28cd25936bb.jpg-w331s)
![
](https://images.seebug.org/content/images/2019/01/fec85708-ee70-4f76-9803-8cdf030dca6b.png-w331s)

所以直接找到这个句柄项，清零即可：

![
](https://images.seebug.org/content/images/2019/01/b00a7f98-819e-49e0-ac4c-30570cf0627d.png-w331s)

之后即完美退出EXP：

![
](https://images.seebug.org/content/images/2019/01/e91597df-d412-46fe-a708-b9e45e5f9a69.jpg-w331s)

本文EXP下载链接：

<https://github.com/360-A-Team/cve-2018-8453-exp/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/798/>

