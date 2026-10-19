# **漏洞信息**

##  **1** **漏洞简介**

 **漏洞名称** ：Microsoft Windows Win32k本地提权漏洞

 **漏洞编号** ：CVE-2015-2546

 **漏洞类型** ：UAF

 **影响范围** ：Windows 7 Service Pack 1

Windows Vista SP2

Windows Server 2008 sp2

Windows Server 2008 r2 x64 sp1

 **CVSS3.0** ：N/A

 **CVSS2.0** ： 6.9

  

##  **2** **组件概述**

win32k.sys是Windows的多用户管理的sys文件

MicrosoftWindows是美国微软（Microsoft）公司发布的一系列操作系统。kernel-modedrivers是其中的一个内核驱动管理软件。Graphics是其中的一个图形驱动器组件。MicrosoftWindows内核模式驱动程序中存在特权提升漏洞，该漏洞源于程序没有正确地处理内存中的对象。本地攻击者可利用该漏洞在内核模式下运行任意代码。

  

##  **3 影响版本**

Windows 7 Service Pack 1

Windows Vista SP2

Windows Server 2008 sp2

Windows Server 2008 r2 x64 sp1

  

##  **4 解决方案**

http://technet.microsoft.com/security/bulletin/MS15-097

  

##  **漏洞复现**

###  **1 环境搭建**

Windows：Windows 7 sp1 x86

win32k.sys：6.1.7601.17154

  

###  **2 复现过程**

获取exp，编译cpp文件，获得可执行文件。在编译过程中，只有x86的编译成功了，x64的暂未成功。

  

之后在靶机上面执行exp

![](https://image.3001.net/images/20201127/1606448299_5fc074abb162c8d5f1035.png!small)​

  

##  **漏洞分析**

  

###  **1 基本信息**

● 漏洞文件：win32k.sys

● 漏洞函数：xxxMNMouseMove

● 漏洞对象：pPopupMenu

  

###  **2 背景知识**

在xxxMNMouseMove函数中，xxxSendMessage(pwnd,
0x1F0,…)发起了一次用户模式回调。在这次回调中，攻击者可以销毁Menu窗口，释放tagPOPUPMENU对象并占位重用。当回调返回内核之后，补丁前的xxxMNmouseMove并没有对已释放的pPopupMenu进行验证。之后pPopupMenu被传入xxxMNHideNextHierarchy，xxxMNHideNextHierarchy会对tagPOPUPMENU.spwndNextPopup发送消息，攻击者创建合适的对象占用被释放的tagPOPUPMENU内存，构造好tagPOPUPMENU.spwndNextPopup的数据，即可实现内核任意代码执行。

  

###  **3 补丁对比**

bindiff进行比较，可以发现在调用SendMessage函数之后增加了一层判断。

![](https://image.3001.net/images/20201127/1606448301_5fc074adbd1b17100ef77.png!small)​

下面两图时补丁前与补丁后的IDA反汇编代码。

![](https://image.3001.net/images/20201127/1606448302_5fc074ae36bfb7e51e634.png!small)​

![](https://image.3001.net/images/20201127/1606448303_5fc074af39e0ca4075211.png!small)​

反汇编可以看到，第81行加了一个判断，

tagWND+0xb0处存放的是pPopupMenu的指针。这里检测回调之后tagMENUWND->pPopupMenu是否被修改，因为攻击是在回调的过程中，将shellcode写入指定的地址，回调完成后，UAF使用了这块空间，执行了shellcode。

  

###  **4 漏洞分析**

###  **4.1 静态分析**

 **4.1.1 补丁分析**

分析补丁代码，我们可以追踪a2的值是怎样传递的，首先分析，a2的含义。

63行，v7的值赋值给a2，v7又是通过safe_cast_fnid_to_PMENUWND以v6当作参数来获取的。

![](https://image.3001.net/images/20201127/1606448303_5fc074afe60e94a482b64.png!small)​

再跟进看一下safe_cast_fnid_to_PMENUWND，该函数的作用是检查窗口对象是否为FNID_MENU(fnid =
0x29C)，如果通过safe_cast_fnid_to_PMENUWND检查，则表明这的确是一个类为#32768的菜单窗口对象。

![](https://image.3001.net/images/20201127/1606448304_5fc074b05dbeb9ce53bc2.png!small)​

 **为什么通过safe_cast_fnid_to_PMENUWND检查，则表明这的确是一个类为#32768的菜单窗口对象？**

在 Windows 内核中，菜单对象在屏幕中的显示通过窗口 tagWND 对象的特殊类型 #32768(MENUCLASS)
菜单窗口对象来实现，菜单窗口对象末尾的扩展区域中存储指向关联的弹出菜单 tagPOPUPMENU 对象的指针。

![](https://image.3001.net/images/20201127/1606448304_5fc074b0bb3c681242080.png!small)​

我们在往回看一下v6是在哪里赋值的，通过xxxMNFindWindowFromPoint来进行赋值，xxxMNFindWindowFromPoint函数的作用是得到菜单窗口对象指针ptagWND，所以v6的值是ptagWND。

![](https://image.3001.net/images/20201127/1606448305_5fc074b150cfa64f7a257.png!small)​

所以a2的值为ptagWND。

查找资料发现：safe_cast_fnid。to_PMENUWND()的输出将会是PMENUWND结构。PMENUWND结构的定义如下：

查找资料发现：safe_cast_fnid。to_PMENUWND()的输出将会是PMENUWND结构。PMENUWND结构的定义如下：

    
    
    typedef struct tagMENUWND {
    
    WND wnd; 
    
    PPOPUPMENU ppopupmenu;
    
    } MENUWND, *PMENUWND;

那么ptagWND+176所代表的位置存放的是其pPopupMenu的指针。因此可以推断出这几句是检查回调之后tagMENUWND->pPopupMenu是否被修改。

 **4.1.2 漏洞触发流程**

首先是通过xxxMNFindWindowFromPoint创建个窗口句柄v6，然后将v6赋值给v7，这样现在v7的值也为窗口句柄。

![](https://image.3001.net/images/20201127/1606448305_5fc074b1acb7d96915a40.png!small)​

这里在51行做了一个判断，假如v7不为窗口类型的话，则退出，这样我们就不能在前面设置钩子来更改v7的值了。

![](https://image.3001.net/images/20201127/1606448306_5fc074b2238aeb7720fcb.png!small)​

然后在第59行给v9进行赋值，该值为v7+0xb0，代表的含义为pPopupMenu的指针，在4.1补丁分析的章节也已经推断出来了。

![](https://image.3001.net/images/20201127/1606448306_5fc074b28330b8d377eae.png!small)​

然后就到达了第68行，通过SendMessage进行一个异步消息的发送，之后程序进入到用户态 。

![](https://image.3001.net/images/20201127/1606448302_5fc074ae36bfb7e51e634.png!small)​

在这次回调的过程中，我们可以释放掉tagMENUWND的空间，从而销毁了tagPOPUPMENU的空间，之后我们再重新申请这一块空间fake。并将shellcode写入到这块空间中（这时，tagPOPUPMENU的所分配的堆空间和我们申请的fake的堆空间是用一块空间，这样，再次调用tagPOPUPMENU这块空间时，将会执行shellcode），当回调返回内核时，补丁前的xxxMNmouseMove并没有对已经释放掉的pPopupMenu进行验证，之后pPopupMenu被传入xxxMNHideNextHierarchy。

![](https://image.3001.net/images/20201127/1606448307_5fc074b39532f07a98280.png!small)​

这里面v9的值，就是pPopupMenu，我们已经通过UAF将它所指向的那块空间的值的内存空间改变了。

![](https://image.3001.net/images/20201127/1606448309_5fc074b501ff73937bbcd.png!small)​

这里将v9传入xxxMNHideNextHierarchy函数中，xxxMNHideNextHierarchy会对tagPOPUPMENU.spwndNextPopup发送消息。

这里面的tagPOPUPMENU.spwndNextPopup是a1+12，我们可以创建合适的对象占用被释放的tagPOPUPMENU内存，构造好tagPOPUPMENU.spwndNextPopup的数据，这样我们恶意构造的数据就可以通过SendMessage进行执行，这样就可以造成内核态任意代码执行。

![](https://image.3001.net/images/20201127/1606448309_5fc074b573b689a4f8f4a.png!small)​

  

 **4.2 动态分析**

 **4.2.1 漏洞调试**

函数调用栈：

![](https://image.3001.net/images/20201127/1606448310_5fc074b60344810fe8aa1.png!small)​

在刚刚的静态分析也已经大致阐述了，要想达到漏洞的利用点，那么必须通过xxxMNFindWindowFromPoint得到ptagWND，并且这个ptagWND窗口对象必须是FNID_MENU(fnid
= 0x29C)，这样就可以走到漏洞部分。

  

首先在xxxMNMouseMove处下断点，然后运行exp。

![](https://image.3001.net/images/20201127/1606448310_5fc074b675dcf80e4a12f.png!small)​

这里执行过了xxxMNFindWindowFromPoint，该函数的返回值通过esi进行存取，这里esi的值为 **0x9d99f580** 。

![](https://image.3001.net/images/20201127/1606448310_5fc074b6ddd50221cb9da.png!small)​

接着向下走，在这里，将ebx赋值为dword ptr[esi+0xb0h]，在上面静态分析也已经提到过，这个值是上面v9的值，这里的值为：
**0xfe83f988** 。

![](https://image.3001.net/images/20201127/1606448311_5fc074b7ad194089eaa64.png!small)​

然后继续向下执行，这时ebx的值和dword ptr[esi+0xb0]的值是相同的。

![](https://image.3001.net/images/20201127/1606448312_5fc074b8846a94fb7dbde.png!small)​

当执行完成0x9d8b9538这条call指令时，ebx的值没有改变，但是dword ptr[esi+0xb0]所指向位置的值却为0了。

![](https://image.3001.net/images/20201127/1606448313_5fc074b90cd2a9e6dc062.png!small)​

我们跟进这个xxxSendMessage中，看看里面执行了哪些操作。

![](https://image.3001.net/images/20201127/1606448313_5fc074b9ba54c5b13d23c.png!small)​

![](https://image.3001.net/images/20201127/1606448314_5fc074ba60bd08c9fdf4d.png!small)​

之后进入xxxSendMeassageTimeout，在这里调用了hook。

![](https://image.3001.net/images/20201127/1606448314_5fc074baed9fdc0831395.png!small)​

进入xxxCallHook函数，在这里调用了两个函数，PhkFirstValid函数的作用是可以找到第一个钩子函数。

![](https://image.3001.net/images/20201127/1606448315_5fc074bb736f778f6b078.png!small)​

然后将ebx作为参数传入到xxxMNHideNextHierarchy中。

![](https://image.3001.net/images/20201127/1606448315_5fc074bbf3391e28ebc21.png!small)​

之后一路走到第二个xxxSendMessage处，跟进。

![](https://image.3001.net/images/20201127/1606448316_5fc074bcc96073de7ca22.png!small)​

传入的值为0x5，这个值就是tagPopupMenu的值,也就是exp所占用零表空间写入的值，f构造了fake
popupmenu，之后执行了shellcode。

![](https://image.3001.net/images/20201127/1606448317_5fc074bd5978840ef792a.png!small)​

 **4.2.2 补丁调试**

当系统打上微软漏洞补丁之后，执行到指定位置处。

这里要分出两种情况，执行出来的结果是不一样的。

 **第一种**

通过命令行来进行执行。

![](https://image.3001.net/images/20201127/1606448318_5fc074be46383f66470bd.png!small)​

当执行到xxxMNFindWindowFromPoint函数并未执行时，eax的值为0xa1d37a94。

![](https://image.3001.net/images/20201127/1606448318_5fc074beb8d58c170561c.png!small)​

但是之后执行完成这个call之后，函数的返回值却是0，在上面已经分析过这个函数的路程，当这个值为0的时候是不会走到漏洞函数中去的，所以这样自然不会成功，但是这就和这个漏洞无关了。具体出现这种情况的原因不明。

![](https://image.3001.net/images/20201127/1606448319_5fc074bfac12c6c1ee4e7.png!small)​

 **第二种**

直接双击程序进行运行。

还是到刚刚的那一步，这时的eax值为0xa1d97a94。

![](https://image.3001.net/images/20201127/1606448320_5fc074c0aa31b7922bb9b.png!small)​

之后进行下一步，这时eax的值就不为0了，也就是说过了那个不为0的验证了，也就是说现在的逻辑有可能走到我们的漏洞逻辑。

![](https://image.3001.net/images/20201127/1606448321_5fc074c16120287696b55.png!small)​

经过调试，事实上也确实进入到了我们的漏洞逻辑，并且可以发现，后面有了微软增加的判断执行逻辑。

![](https://image.3001.net/images/20201127/1606448322_5fc074c259ba0abc8d2bc.png!small)​

之后继续向下调试，按理来说MS-PATCH会将漏洞拦下， **但是exp把这个判断过了** 。

![](https://image.3001.net/images/20201127/1606448323_5fc074c368ea04eddca6f.png!small)​

当MS-PATCH失效，exp将执行成功时， **xxxMNHideNextHierarchy的逻辑里的一步有效性验证将exp拦下了** 。

![](https://image.3001.net/images/20201127/1606448324_5fc074c463bcc1e78b98a.png!small)​

对应的伪代码是这种形式，其中if判断将我们的exp拦下了。

![](https://image.3001.net/images/20201127/1606448325_5fc074c55ccd3f2c067c5.png!small)​

这两种exp执行的方式都和微软的MS-PATCH思路相悖。

  

##  **5 EXP流程**

exp思路

  

1\. 创建一个有弹出式菜单的正常主窗口

2\. 在某个固定地址Addr1分配内存，并在Addr1上构造一个fake_tag
WND。其中fake_tagWND->bServerSideWindowProc置为1，fake_tagWND->lpfnWndProc指向Ring0ShellCode。

3\. 用Accelerator Table对象制作出内存空洞。

4\. 创建类名为”#32768”的窗口MenuWindow1，并用SetWindowLong替换其WndProc。

5\. 创建消息钩子，并在HookProc中处理MN_FINDWINDOWFROMPOINT消息和MN_SETTIMERTOOPENHIERARCHY消息。

6\. 向主窗口发送WM_SYSCOMMAND消息或者模拟鼠标事件。

7\. 系统创建的正常菜单窗口收到MN_FINDWINDOWFROMPOINT消息，返回MenuWindow1的句柄。

8\. HookProc收到MN_SETTIMERTOOPENHIERARCHY消息，销毁MenuWindow1，并创建Accelerator
Table对象占用tagPOPUPMENU释放的内存。

9\. Fake_tagWND收到0x1E4消息，执行Ring0ShellCode。

  

#  **参考链接**

  

http://xlab.baidu.com/cve-2015-2546%ef%bc%9a%e4%bb%8e%e8%a1%a5%e4%b8%81%e6%af%94%e5%af%b9%e5%88%b0exploit/

https://www.anquanke.com/post/id/84911

#  **深信服千里目安全实验室**

  

深信服科技旗下安全实验室，致力于网络安全攻防技术的研究和积累，深度洞察未知网络安全威胁，解读前沿安全技术。

