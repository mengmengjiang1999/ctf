一、 漏洞信息

CVE-2019-0808是发生在win32k中的一个空指针解引用漏洞，根据网上的blog介绍该漏洞在win32k!xxxMNMouseMove中产生。

二、 测试环境及漏洞复现

## 测试环境

POC：[https://github.com/ze0r/cve-2019-0808-poc](https://www.sec-in.com/outLinkPage/?target=https://github.com/ze0r/cve-2019-0808-poc)  

靶机： win10 x86 SP1

## 漏洞复现

![wKg0C2I0PpCAAkfvAACZSGfv9w448.png](https://image.3001.net/images/20220722/1658472250_62da473ac0e9e3a202aaf.png!small)

三、 漏洞成因分析

## 补丁分析

通过bindiff对xxxMNMouseMove函数进行对比，发现win32k!xxxMNFindWindowFromPoint函数新增对菜单窗口对象的校验。

![wKg0C2I0PpAM3ZAAA6nQmOih8069.png](https://image.3001.net/images/20220722/1658472251_62da473b5101938e01e1c.png!small)

对win32k!xxxMNFindWindowFromPoint进行详细分析时，可以看到xxxSendMessage成功获取到菜单窗口对象句柄后，通过HMValidateHandleNoSecure获取对应的菜单窗口对象，随后直接返回。

![wKg0C2I0PuKAWp2UAAA3rdyuPtw522.png](https://image.3001.net/images/20220722/1658472251_62da473bbb79878ddba38.png!small)

而在补丁文件中，HMValidateHandleNoSecure成功获取菜单窗口对象后会进行一系列的安全检查后（保证tagWndMenu、tagWnd、tagPopuMenu、tagMenu这四个对象均存在且不为NULL）才会返回。此时也猜测到这个漏洞产生的原因大概率是空指针解引用。

![wKg0C2I0PuyAYQC3AABOk5cNEBo965.png](https://image.3001.net/images/20220722/1658472252_62da473c355edf56f1df2.png!small)

## 成因分析

在补丁分析中，我们猜测这是一个空指针解引用的洞，这里结合POC去印证。下图为执行POC后windbg抓到的cash现场，从堆栈中可以看到蓝屏触发点在win32!MNGetItem函数。

![wKg0C2I0PvqANW5PAACDCFaFaow114.png](https://image.3001.net/images/20220722/1658472252_62da473ca207e24841367.png!small)

此时进行精准定位后，就是对ecx+0x20的poi操作发生错误。

![wKg0C2I0PweAEpbJAAAtQcgR1Us440.png](https://image.3001.net/images/20220722/1658472253_62da473d1f44d9b878c66.png!small)

进一步调试后，我们发现ecx的值居然也为空！！！

![wKg0C2I0PxCAEVkAAAPyrqVFmk117.png](https://image.3001.net/images/20220722/1658472253_62da473d8c6ab10ddb94d.png!small)

结合IDA对ecx的值进行溯源, 发现其存储的值是ptagMenu。

![wKg0C2I0PxmAIbCnAABNkeRmmiM437.png](https://image.3001.net/images/20220722/1658472254_62da473e0260b98aadbca.png!small)

而ptagMenu的值是由菜单弹出对象tagPopuMenu+0x14提供的。

![wKg0C2I0PyKASHRJAAAOX8S8dUQ423.png](https://image.3001.net/images/20220722/1658472254_62da473e6bdcc7011070d.png!small)

最终，我们溯源完成后知道ptagPopuMenu的值正是由通过xxxMNFindWindowFromPoint函数中HMValidateHandleNoSecure返回的菜单窗口对象tagMenuWnd+0xb0得到的。

![wKg0C2I0PyqAcfH5AAAPWBeNryo915.png](https://image.3001.net/images/20220722/1658472255_62da473f17cb432b9721b.png!small)

至此，空指针解引用产生的原因已然明了。

四、 漏洞利用分析

漏洞利用分析部分是结合EXP，对其漏洞构造、提权利用进行详细阐述,方式为Q-A模式。

## 问题一，如何构造空的菜单对象（ptagPopupMenu->spmenu=NULL）

在漏洞成因过程中知道，tagMenu是由tagPopuMenu+0x14提供的，而tagPopuMenu是由tagMenuWnd+0xb0提供的。tagMenuWnd是在xxxMNFindWindowFromPoint在xxxSendMessage获取的弹出菜单句柄后通过HMValidateHandleNoSecure得到的。

![wKg0C2I0P1OAAtt9AAA7hEZbikc989.png](https://image.3001.net/images/20220722/1658472255_62da473f79e9e1db03742.png!small)

从windbg的堆栈可以看到漏洞函数xxxMNUpdateDraggingInfo是由xxxMNMouseMove调用的，另外在window中win32k!xxxMNMouseMove是菜单窗口过程处理函数用来处理鼠标在菜单内移动的消息，如果此时鼠标由主弹出菜单移动到了出菜单，那么在win32k!xxxMNFindWindowFromPoint内部就会通过xxxSendMessage对出菜单发送消息来获取出菜单的句柄，用来在后续代码中对出菜单发送消息来完成绘制和鼠标选中等效果。

因此在EXP对应会创建两个弹出菜单并将其设置成为非模拟态（原因是模拟态会导致其他其他菜单发生阻塞，无法正常接收消息）

![wKg0C2I0P12AGRS3AABA8cdA1M0022.png](https://image.3001.net/images/20220722/1658472255_62da473fe41d4e0da21a8.png!small)

与此同时去创建一个伪造菜单窗口（tagfakeMenuwnd->spmenu==NULL），xxxSendMessage发送消息后替换其返回值（正常应该返回hMenuSub）。Ps：CSDN中也有定义lpClassName为#32768时，创建的是菜单窗口。

![wKg0C2I0P3KAABOOAAA9ViC2W8c385.png](https://image.3001.net/images/20220722/1658472256_62da474064caa134f195c.png!small)

弹出菜单创建后，还需要一个窗口作为媒介来传递消息。

![wKg0C2I0P3qAOO78AAAt8QpuMak890.png](https://image.3001.net/images/20220722/1658472256_62da4740ccf5764328b77.png!small)

TrackPopupMenuEx的作用是在桌面上显示弹出菜单。

![wKg0C2I0P4OAbQL4AAAPGeKP690582.png](https://image.3001.net/images/20220722/1658472257_62da474143704fddb54cf.png!small)

弹出菜单以及伪造窗口等都成功创建后，我们要想办法将xxxSendMessage的返回值替换为hWndFakeMenu，这里是通过SetWindowsHookEx和SetWinEventHook实现的。

![wKg0C2I0P4qAKfsZAAAXvft9uBQ625.png](https://image.3001.net/images/20220722/1658472257_62da4741e404665818476.png!small)

下面就这两处hook的原因及作用进行详细介绍：

  1. SetWinEventHook

这里是对EVENT_SYSTEM_MENUPOPUPSTART事件进行了hook，原因是在TrackPopupMenuEx的内部实现xxxTrackPopupMenuEx中对菜单窗口（tagMenuWnd）、弹出菜单对象（tagPopupMenu）以及tagMENUSTATE创建并初始化后，会通过xxxWindowEvent向用户层发送EVENT_SYSTEM_MENUPOPUPSTART事件消息通知应用层的事件回调。

![wKg0C2I0P5SAdDVVAAAmFo8SuZ4639.png](https://image.3001.net/images/20220722/1658472258_62da47425b77c79cd3466.png!small)

当弹出菜单成功显示后，向用户层发送EVENT_SYSTEM_MENUPOPUPSTART事件。

![wKg0C2I0P5yAH52sAAAnS2QnWXY051.png](https://image.3001.net/images/20220722/1658472258_62da4742c2de915d4c9b6.png!small)

注册Event Hook后，首先在主弹出菜单（hMenuRoot）绘制完成后第一次进入此事件回调

![wKg0C2I0P6eAeMmBAACQj3HF8CM355.png](https://image.3001.net/images/20220722/1658472259_62da47434470a5468e710.png!small)

并向其发送WM_LBUTTONDOWN消息即按下左键显示出出菜单（hMenuSub）

![wKg0C2I0P6AZBuAAAZdnGdVac423.png](https://image.3001.net/images/20220722/1658472259_62da4743baea92a96329a.png!small)

出菜单的显示是我们第二次进入事件回调并向hMenuSub发送WM_MOUSEMOVE消息从而形成一个从主弹出菜单到出菜单的拖拽动作。

![wKg0C2I0P7qALLh5AAEyDGnj0A398.png](https://image.3001.net/images/20220722/1658472260_62da47444a7837b9f6589.png!small)

拖拽动作成功实现后，EXP就会顺利进行到xxxMNMouseMove函数中。

2.SetWindowsHookEx

用户层成功捕捉到由xxxMNFindWindowFromPoint中的xxxSendMessage发来的WM_MN_FINDMENUWINDOWFROMPOINT消息后通过SetWindowLongPtr将出菜单窗口对应的过程函数（DefWindowProc）更改为SubMenuProc。

![wKg0C2I0P9GAAJ3CAAAkKMbfg4624.png](https://image.3001.net/images/20220722/1658472260_62da4744d97579c7aadfe.png!small)

SubMenuProc最终返回用户态构造的窗口对象句柄hWndFakeMenu作为xxxMNFindWindowFromPoint函数调用xxxSendMessage的返回值，最终得到一个

ptagPopupMenu->spmenu=NULL的空指针。

![wKg0C2I0P9qAVPvWAAAuPJjyy3Y281.png](https://image.3001.net/images/20220722/1658472261_62da474545a9cd63d5e8c.png!small)

![wKg0C2I0P96AQ8VDAAAxMKKbhU324.png](https://image.3001.net/images/20220722/1658472261_62da4745b720f0fafd6ba.png!small)

到这为止，已经成功实现了xxxMNFindWindowFromPoint函数调用xxxSendMessage后返回的是伪造的窗口对象。但是，这并不代表着已经能够成功触发空指针解引用的操作。原因是第二次触发DisplayEventProc事件回调后，EXP向出菜单窗口发送WM_MOUSEMOVE消息时就会在R0中调用一次xxxMNMouseMove。

![wKg0C2I0PiAdqNlAAERmwx8kKo565.png](https://image.3001.net/images/20220722/1658472262_62da474630ab314d26dfe.png!small)

此时，窗口句柄虽然可以被替换但在成功替换后，xxxMNMouseMove往下执行时并不会去调用xxxMNUpdateDraggingInfo。

![wKg0C2I0PKAMvxvAAAqMEy6s9Y014.png](https://image.3001.net/images/20220722/1658472262_62da4746be48483d9347b.png!small)

通过IDA可以看到在xxxMNMouseMove中检查了tagMENUSTATE的fInDoDragDrop标志位是否置位，才会进入xxxMNUpdateDraggingInfo函数。

![wKg0C2I0PqARccOAAAc86SqbBg305.png](https://image.3001.net/images/20220722/1658472263_62da47473a81647b21036.png!small)

DisplayEventProc事件回调中虽然发送WM_MOUSEMOVE能够成功进入xxxMNFindWindowFromPoint的逻辑中，但是由于fInDoDragDrop没有被置位，因此并不能触发空指针解引用。

##
问题二，如何在xxxMNFindWindowFromPoint函数成功获取伪造窗口句柄成功后exp能够顺利进入xxxMNUpdateDraggingInfo的执行逻辑，触发空指针解引用的操作

对于这个问题，网上大神的blog给出了解决方案。我们可以通过手动调用NtUserMNDragOver函数来将fInDoDragDrop置位。

![wKg0C2I0QAAOtpnAAAeKuwEApA630.png](https://image.3001.net/images/20220722/1658472263_62da4747e86aa3cf15203.png!small)

最后还需控制窗口句柄替换时机，设置一个全局变量bOnDraging在事件回调发送xxxMNMouseMove消息时xxxMNFindWindowFromPoint的xxxSendMessage返回正确的窗口句柄。

![wKg0C2I0QCGAMAChAAAMbWHh8qo949.png](https://image.3001.net/images/20220722/1658472264_62da4748601bc8104b94f.png!small)

在我们手动调用NtUserMNDragOver后进入xxxMNFindWindowFromPoint的xxxSendMessage时替换子菜单窗口的窗口过程，因此我们的窗口过程回调需要稍作修改，并在手动调用NtUserMNDragOver前将全局变量bOnDrag置1：

![wKg0C2I0QC6AP7joAAAUEYyjfYE546.png](https://image.3001.net/images/20220722/1658472264_62da4748d6ee6d3fa9608.png!small)

至此，可以实现稳定的触发漏洞。

## 问题三，如何构造任意地址覆盖写漏洞

在漏洞成因分析中我们知道，产生崩溃的点是在xxxMNUpdateDraggingInfo->
MNGetpItem中，具体是spmenu的空指针解引用。而对于此类漏洞Win7中用户态可以通过ntdll!NtAllocateVirtualMemory函数分配零页内存利用。分配零页内存的原理比较简单，不再详述：

![wKg0C2I0QEGAfO6oAAA2Bh13Spg731.png](https://image.3001.net/images/20220722/1658472265_62da474951203be0df85f.png!small)

零页内存分配成功后，MNGetpItem函数中的对于菜单对象的取值操作并不会触发异常，我们可以看到此时pMenu的地址为0x0, pMenu->cItems
[0x00000020] 也是可控数据。

![wKg0C2I0QEqAd16GAAA9fqMSk4405.png](https://image.3001.net/images/20220722/1658472265_62da4749c222e2416ac3c.png!small)

接着在下方的if判断中uDraggingIndex < pMenu->cItems=0
不成立，导致返回pItem=0。我们需要控制程序流程走到红框分支，返回可控数据

![wKg0C2I0QFKAARtrAAAUbCNPlw181.png](https://image.3001.net/images/20220722/1658472266_62da474a3bdda8d5a39a3.png!small)

因此需要在[00000020]设置一个合适的值（这里设置为0xffffffff）进入if分支。

![wKg0C2I0QFqAEI3qAAAeGGR6MuY241.png](https://image.3001.net/images/20220722/1658472266_62da474a9e624697b2a92.png!small)

返回值为uDraggingINdex*6C+[00000034]

![wKg0C2I0QGOAaEphAABBdfgFchA479.png](https://image.3001.net/images/20220722/1658472267_62da474b15fa921fc243e.png!small)

uDraggingINdex的值可以通过wParam+0x10去获取

![wKg0C2I0QGuAETOOAAAzE8ALZzg243.png](https://image.3001.net/images/20220722/1658472267_62da474b83afa99c4887f.png!small)

[00000034]是我们可控的数据，因此MNGetpItem的返回值也是可控的。接着往下发现在xxxMNUpdateDraggingInfo->
xxxMNSetGapState存在位修改操作

![wKg0C2I0QHOAeDcuAAAuXhDWBo528.png](https://image.3001.net/images/20220722/1658472267_62da474be5721257b0d1c.png!small)

想必看到这里，我们知道此逻辑能够实现任意地地址的有限修改。具体如下：

addressToWrite = ret+0x4 = uDraggingINdex*6C+[00000034]+0x4

上述表达式addressToWrite代表着准备改写的任意地址,因此我们仅需设置[00000034]处的地址即可。

[00000034] = addressToWrite - uDraggingINdex*6C - 0x4

![wKg0C2I0QH2AP4mDAAA5edwlVec895.png](https://image.3001.net/images/20220722/1658472268_62da474c5b1061a3e7ae9.png!small)

至此，我们就实现了指定地址值的有限修改功能。

## 问题四,如何实现本地提权利用（LPE）

通过分析exp知道，准备修改的地址是一个窗口对象tagWnd+0x90处的数据即cbwndExtra的值，cbwndExtra为此窗口扩展数据的大小，此处将其修改为0x4000000一个超长buf,目的是对其相邻的窗口进行越界写。

![wKg0C2I0QIAKFOAAAPCUPthmM313.png](https://image.3001.net/images/20220722/1658472268_62da474cc6296907a06bf.png!small)

  1. 窗口对象喷射

首先申请100个窗口对象

![wKg0C2I0QJuAMoHfAAAo5EbO4862.png](https://image.3001.net/images/20220722/1658472269_62da474d3d793e7dd1622.png!small)

通过pHmValidateHandle函数泄露窗口对象的地址并且以两个窗口的地址差小于0x3fd00为判断依据去寻找两个相邻的窗口对象。

![wKg0C2I0QKOAWGm0AABgywlxTyo704.png](https://image.3001.net/images/20220722/1658472269_62da474daaf55048abd52.png!small)

![wKg0C2I0QKmAM0iAAAA7B0qMPSQ894.png](https://image.3001.net/images/20220722/1658472270_62da474e2893321ecd535.png!small)

成功找到后，将地址较高的窗口对象设置为primaryWindow，另外一个设置为secondaryWindow。

![wKg0C2I0QLKALsMoAABDJoI1Gh0481.png](https://image.3001.net/images/20220722/1658472270_62da474e9985d4dc1114f.png!small)

最后通过漏洞能力将primaryWindow的cbwndExtra修改为0x40000000。

![wKg0C2I0QLqAPvLlAAARrcWgVPk813.png](https://image.3001.net/images/20220722/1658472271_62da474f165d4de8f2c3c.png!small)

2.越界写，执行shellcode

xxxMNMouseMove执行完xxxMNUpdateDraggingInfo并且成功将primaryWindow对象的cbwndExtra字段修改为0x4000000后，继续向下执行最后会向子菜单窗口发送0x1E5消息。

![wKg0C2I0QMqAcwBcAAAdszIpnM4641.png](https://image.3001.net/images/20220722/1658472271_62da474f8014312d8c13a.png!small)

EXP成功拦截到发来的1E5消息后，开始计算primaryWindow对象末尾到secondaryWindow对象的strName.buffer的差值（offset）

![wKg0C2I0QNSANaR1AAAv7VP8Vds809.png](https://image.3001.net/images/20220722/1658472271_62da474fe752c6bf31a91.png!small)

![wKg0C2I0QNmALChQAAAb94cPDWo592.png](https://image.3001.net/images/20220722/1658472272_62da47505698fe033769c.png!small)

SetWindowLongA将secondaryWindowAddress的strName.buffer的地址修改为secondaryWindow窗口对象的0x16的地址。

![wKg0C2I0QOeAZeSVAAAYfBfem88301.png](https://image.3001.net/images/20220722/1658472272_62da4750c237d75ea3fa1.png!small)

![wKg0C2I0QOqAatdPAABJG9ztg8691.png](https://image.3001.net/images/20220722/1658472273_62da4751446d7a7185d3f.png!small)

接着用SetWindowTextA将bServerSideWindowProc置为1，从而可以在内核执行我们的窗口过程函数。

![wKg0C2I0QPOAdXKAAAdDAvUdc472.png](https://image.3001.net/images/20220722/1658472273_62da4751b40a476d0151c.png!small)

![wKg0C2I0QPeAKcAEAAAeRJ9QkiU555.png](https://image.3001.net/images/20220722/1658472274_62da4752225556b13a3b2.png!small)

修改0x16偏移的原因如下图所示：

![wKg0C2I0QPAeyx3AABeaVHKf8847.png](https://image.3001.net/images/20220722/1658472274_62da4752838a5e3247625.png!small)

最后向secondaryWindow窗口发送WM_ENTERIDLE消息执行shellcode(内核执行)。

![wKg0C2I0QReAAQDdAAA0PrncNk694.png](https://image.3001.net/images/20220722/1658472275_62da475301d9df9c27169.png!small)

    
    
    secondaryWindow成功接收到WM_ENTERIDLE消息后首先会通过cs寄存器的值去判断当前执行上下文是否在内核态，之后开始执行shellcode，替换token。
    
    

![wKg0C2I0QSaATslHAABJkQeifds532.png](https://image.3001.net/images/20220722/1658472275_62da47536be37e107d1e9.png!small)

    
    
    Shellcode中除了必要的token替换，还清空了进程的Job对象指针，这是因为在Chrome的渲染进程中，即使shellcode替换了system进程的token，当前进程的token依然会继承自Job对象，并且Job不允许Chrome渲染进程产生新进程，因此需要先清空当前进程的Job对象指针。
    

![wKg0C2I0QTuATpM3AAA7yXW6GkQ343.png](https://image.3001.net/images/20220722/1658472275_62da4753d5fe3518748f8.png!small)

    
    
    至此漏洞利用过程分析结束。
    ﻿

