# **综** **述** ****

2019年7月10日，在微软7月补丁发放的第一天，eset发布文章“windows-zero-day-cve-2019-1132-exploit”披露了APT团伙buhtrap使用windows 0day
CVE-2019-1132进行攻击的一次在野活动，之后SHIVAM
TRIVEDI于7月25对外放出了该漏洞相关的exp利用，本文针对该漏洞及buhtrap攻击使用的样本进行分析，以便于大众了解buhtrap这个在国内鲜为人知的APT团伙。

Buhtrap是一个常年针对俄罗斯金融企业相关的攻击团伙，其2014年就开始了相关的活动，而这也是buhtrap的第一次0day攻击活动，但是实际上早在2016年3月GROUP
IB就针对buhtrap发布了文章“BUTHRAP The evolution of targeted attacks against financial
institutions”，如下图所示就是GROUP IB总结的Buhtrap在2014年，2015年两年内的战绩。

![图片.png](https://image.3001.net/images/20190808/1565252948_5d4bdd5495454.png!small)

# **漏洞部分** ****

该部分使用SHIVAM TRIVEDI分享的相关exp代码，感谢SHIVAM TRIVEDI的分享。

##  **分析** ****

编译对应exp，运行之后效果如下所示，获得了一个管理员权限的shell。

![图片.png](https://image.3001.net/images/20190808/1565252971_5d4bdd6b6682f.png!small)  

利用代码的主函数中一开始创建了三个menu菜单，并通过AppendMenuA创建对应下拉子菜单，然后创建两个窗口，一个为主窗口，一个用于辅助后续利用的hunt窗口。

![图片.png](https://image.3001.net/images/20190808/1565252983_5d4bdd77f272f.png!small)  

之后分别设置消息hook和事件hook函数。![图片.png](https://image.3001.net/images/20190808/1565252995_5d4bdd83b02d6.png!small)

在消息hook回调函数中监控对应的WM_NCCREATE消息，当监控到对应的消息时，通过SendMessage针对指定的menu发送MN_CANCELMENUS消息，该消息会取消对应的菜单。

在事件hook回调函数中，首先保存所有触发菜单的hwnd到hwndMenuList中，并发送MN_OPENHIERARCHY消息，该消息将导致打开对应的子菜单。

![图片.png](https://image.3001.net/images/20190808/1565253015_5d4bdd9732c40.png!small)  

之后对第一个hMenuList[0]菜单调用函数TrackPopupMenuEx，用于弹出显示该菜单，调用完成之后将导致hMenuList[0]子菜单hMenuList[1]的ppopupmenuRoot被设置为null，之后设置0地址，将偏移0x1c的位置设置为hunt窗口的内核地址+0x12，hunt窗口的内核地址通过xxHMValidateHandle的方式获取，该内核地址泄露的方式在win10
rs4之后被微软修复。

![图片.png](https://image.3001.net/images/20190808/1565253029_5d4bdda5cf235.png!small)  

这里一个最大的疑问就在于为什么TrackPopupMenuEx函数执行之后，对应的hMenuList[1]中的ppopupmenuRoot会被设置为null。

在解决这个问题前，我们需要对windows中的菜单对象有所了解，其中涉及到的内容主要包括：菜单对象，菜单层叠窗口对象和弹出菜单对象，菜单状态对象（以下几个菜单相关对象主要来自于小刀子同学之前的文章，文章对菜单对象分析得很详细，感兴趣的同学可以看看，见参考链接2）

菜单对象：菜单对象是菜单的实体，在内核中以结构体tagMENU的形式存在，用于描述菜单实体的菜单项，项数，大小等静态信息，但本身并不负责菜单在屏幕中的显示，通过用户调用CreateMenu函数时在内核中创建，通过函数DsetroyMenu调用或进程结束时销毁。

菜单层叠窗口对象（以下简称菜单窗口对象）：菜单窗口对象是窗口结构体tagWND对象的特殊类型，当需要在屏幕中的显示某个菜单时，如通过窗口区域右键鼠标，内核中将调用相关的服务函数根据目标菜单对象创建对应类型为MENUCLASS的菜单窗口对象，其主要负责描述菜单在屏幕中的显示位置，样式等动态信息，其扩展区域关联对应的弹出菜单对象。

弹出菜单对象:弹出菜单对象为菜单窗口对象的扩展对象，用来描述其所代表的菜单的弹出状态，以及菜单窗口对象，菜单对象，子菜单或父菜单的菜单窗口对象等用户对象的相互关系。

当某个菜单在屏幕中弹出，菜单窗口对象和关联的弹出菜单对象被创建，

菜单状态对象:该结构体用来存储和当前活跃菜单状态相关的详细信息，包括上下文菜单弹出坐标，关联的位图表面对象的指针，窗口设备上下文对象，之前的上下文菜单结构体的指针，及其他一些成员域。

菜单窗口对象实际是tagWND对象的特殊类型，其中比较重要的是偏移0x14处的bServerSideWindowProc，该字段用于标记对应的窗口对象是否在内核态执行，如果能修改该标记位，即能实现让我们的窗口对应的回调处于内核态的执行权限，从而实现提权（类似的提取方式在CVE-2019-0808，CVE-2017-0263种都被使用），其偏移0xB0的位置为WndExtra
Data Section，在这里指向了对应关联的弹出菜单对象。

![图片.png](https://image.3001.net/images/20190808/1565253063_5d4bddc785473.png!small)  

弹出菜单对象如下所示，其中偏移0x20
ppopupmenuRoot标记了第一个弹出菜单对象，如第一个菜单对象的ppopupmenuRoot就是自身，这也是漏洞中被设置为null的位置。

偏移0x24的位置为ppmDelayedFree，该成员域用来将所有被标记为延迟释放状态的弹出菜单对象连接起来，以便在菜单的弹出状态终止时将所有弹出菜单对象统一销毁，根弹出菜单对象的ppmDelayedFree作为链表的入口，即第一个节点。

![图片.png](https://image.3001.net/images/20190808/1565253093_5d4bdde533183.png!small)  

菜单状态对象偏移0处的pGlobalPopupMenu指向对应的弹出菜单对象。

![图片.png](https://image.3001.net/images/20190808/1565253101_5d4bdded9a0a3.png!small)  

如下图所示漏洞代码中第一个菜单的弹出菜单对象如下所示，该弹出菜单对象的地址为0xfd78d628，其ppopupmenuRoot指向向了自身，同样为0xfd78d628.

![图片.png](https://image.3001.net/images/20190808/1565253275_5d4bde9b01ff0.png!small)  

第二个菜单对象关联的弹出菜单对象为0xfd6f3a68，其ppopupmenuRoot就指向了第一个菜单的弹出菜单对象。

![图片.png](https://image.3001.net/images/20190808/1565253292_5d4bdeac16510.png!small)  

漏洞利用中通过函数来TrackPopupMenuEx弹出hMenuList[0]菜单，TrackPopupMenuEx在内核中通过xxxTrackPopupMenuEx实现，xxxTrackPopupMenuEx首先通过xxxCreateWindowEx创建对应的菜单窗口对象tagMENUWND[0]。其中弹出菜单对象也会伴随着一起生成。xxxCreateWindowEx中会发送对应的WM_NCCREATE，并被我们的hook回调捕获。

![图片.png](https://image.3001.net/images/20190808/1565253304_5d4bdeb866886.png!small)  

xxxCreateWindowEx之后，通过菜单窗口对象获取对应的弹出菜单对象，在偏移0xB0的位置，并设置对应的弹出菜单对象中的值，如下图中就设置该弹出菜单对象的ppopupmenuRoot，之后通过xxxMNAllocMenuState创建对一个对应的菜单状态对象。

![图片.png](https://image.3001.net/images/20190808/1565253329_5d4bded1d141a.png!small)  

xxxMNAllocMenuState中将弹出菜单对象设置到菜单状态对象偏移为0x0的位置。

![图片.png](https://image.3001.net/images/20190808/1565253344_5d4bdee0eb654.png!small)  

之后xxxWindowEvent(6, v51, -4, 0,
0);发送事件EVENT_SYSTEM_MENUPOPUPSTART，该事件会被我们的事件hook捕获。

![图片.png](https://image.3001.net/images/20190808/1565253358_5d4bdeee2101a.png!small)

这里需要注意xxxWindowEvent发送事件EVENT_SYSTEM_MENUPOPUPSTART之后才进入到

xxxMNLoop函数中，该函数可以理解会对应菜单的消息循环处理函数，因此之后我们在菜单窗口对象创建时发送的WM_NCCREATE被应用层hook捕获时，应用层发送的MN_CANCELMENUS还没有被处理，其会在xxxMNLoop中被处理。当所有菜单消息处理之后，xxxMNLoop结束才会运行之后的xxxUnlockMenuState。

前面提到当菜单窗口对象创建的时候，会发送对WM_NCCREATE，并被我们的hook回调捕获，在回调中判断对应的消息是否为WM_NCCREATE，并确保hMenuList[0]菜单生成，且hMenuList[1]菜单没有生产，如果条件满足，则向hMenuList[0]菜单发送MN_CANCELMENUS，这里的bEnterEvent变量需要在第一个事件回调函数中才会被设置为true，因为当事件回调触发时才表明xxxWindowEvent发送事件EVENT_SYSTEM_MENUPOPUPSTART，对应的菜单窗口对应已经创建。

![图片.png](https://image.3001.net/images/20190808/1565253380_5d4bdf0413951.png!small)  

该消息最终通过win32k!xxxMenuWindowProc派发给hMenuList[0]菜单，其在内核中通过xxxRealMenuWindowProc派发到xxxMNCancel处理

![图片.png](https://image.3001.net/images/20190808/1565253390_5d4bdf0e6efef.png!small)

xxxMNCancel函数首先设置hMenuList[0]的弹出菜单对象fDestroyed字段，并调用函数xxxMNCloseHierarchy。

![图片.png](https://image.3001.net/images/20190808/1565253401_5d4bdf1950eea.png!small)

函数xxxMNCloseHierarchy中首先判断fHierarchyDropped的值，该字段标记当前菜单对象已弹出子菜单，由于我们xxxMNCancel时对应的子菜单hMenuList[1]还没有创建，从而确保对应的这个字段的判断并不成立，从而直接跳过判断，如果在判断成立的情况下将会获取hMenuList[0]对应弹出菜单对象偏移0x1c处的spwndNextPopup，该变量指向下一个弹出菜单对象（如果hMenuList[1]创建的话就是hMenuList[1]的弹出菜单对象，但是这里没有），并发送MN_CLOSEHIERARCHY消息，而我们这里直接跳过了。

![图片.png](https://image.3001.net/images/20190808/1565253416_5d4bdf2854eb7.png!small)

xxxTrackPopupMenuEx尾部通过xxxWindowEvent(6, v51, -4, 0,
0);发送了事件EVENT_SYSTEM_MENUPOPUPSTART，这将被我们的事件hook回调捕获。

![图片.png](https://image.3001.net/images/20190808/1565253432_5d4bdf384e488.png!small)

在事件回调中我们向hMenuList[0]发送MN_SELECTITEM，MN_SELECTFIRSTVALIDITEM
MN_OPENHIERARCHY消息，MN_SELECTITEM，MN_SELECTFIRSTVALIDITEM会导致最终选中hMenuList[0]的下一个菜单hMenuList[1]，之后通过MN_OPENHIERARCHY将打开对应的菜单窗口，即hMenuList[1]。

![图片.png](https://image.3001.net/images/20190808/1565253460_5d4bdf5442e72.png!small)  

MN_OPENHIERARCHY消息在内核中最终通过xxxRealMenuWindowProc派发给函数

xxxMNOpenHierarchy。

![图片.png](https://image.3001.net/images/20190808/1565253472_5d4bdf602b35f.png!small)

xxxMNOpenHierarchy同样通过xxxCreateWindowEx创建hMenuList[1]的菜单窗口对象。

![图片.png](https://image.3001.net/images/20190808/1565253479_5d4bdf672055b.png!small)

获取hMenuList[1]的弹出菜单对象，并设置相关字段，这里需要注意的是该弹出菜单对象被设置到对应ppopupmenuRoot的弹出菜单对象的ppmDelayedFree链表中，而这里ppopupmenuRoot就是hMenuList[0]的弹出菜单对象，也就是对应的hMenuList[0]的弹出菜单对象的ppmDelayedFree的第一个节点指向了hMenuList[1]的弹出菜单对象

![图片.png](https://image.3001.net/images/20190808/1565253488_5d4bdf70cb50d.png!small)

之后调用函数HMAssignmentLock

![图片.png](https://image.3001.net/images/20190808/1565253499_5d4bdf7b035a8.png!small)

此时第一次针对hMenuList[0]的xxxTrackPopupMenuEx函数执行到尾部的xxxUnlockMenuState，其参数为对应的hMenuList[0]的菜单状态结构，菜单状态结构偏移0x0的位置指向了hMenuList[0]的弹出菜单对象。

![图片.png](https://image.3001.net/images/20190808/1565253505_5d4bdf81ad71a.png!small)

xxxUnlockMenuState经过一系列调用，最终执行到MNFlushDestroyedPopups，MNFlushDestroyedPopups中通过传入的hMenuList[0]的弹出菜单对象获取对应的ppmDelayedFree链表，并循环遍历，如上所述该链表中保存了对应的子菜单的弹出菜单对象，之后判断遍历的弹出菜单对象fDestroyed是否设置（这里ppmDelayedFree链表的第一个节点就是hMenuList[1]的弹出菜单对象），这里需要注意的是由于我们之前在xxxMNCancel函数时，xxxMNCloseHierarchy中处理hMenuList[0]时，由于对应的fHierarchyDropped字段没有设置，当时hMenuList[1]子菜单还没有创建，因此跳过了其中的if语句，因此没有向对应的子菜单发送MN_CLOSEHIERARCHY，因此我们的hMenuList[1]弹出菜单对象fDestroyed是没有设置的，因此并没有执行下图中的if语句，而是进入了else
if，在其中直接将对应的popumenuroot设置为了null，从而导致hMenuList[1]菜单的弹出菜单对象中的popumenuroot为空。

![图片.png](https://image.3001.net/images/20190808/1565253518_5d4bdf8e31454.png!small)

此时当我们通过hMenuList[1]调用TrackPopupMenuEx时，最终同样会进入到xxxMNOpenHierarchy，过程和第一次一致。

![图片.png](https://image.3001.net/images/20190808/1565253527_5d4bdf97aac28.png!small)

xxxMNOpenHierarchy中最后调用到函数HMAssignmentLock，此时第一个参数会获取hMenuList[1]弹出菜单对象的ppopupmenuRoot，由于之前第一次TrackPopupMenuEx调用已经将hMenuList[1]弹出菜单对象的ppopupmenuRoot设置为null，因此这里传入的值其实为0x1c的值，因此上述代码中通过设置null地址将0x1c的位置设置为hunt窗口对象偏移加0x12的位置，注意这里并不是直接设置为对应bServerSideWindowProc的偏移0x18，是因为后续利用处还有一个+4的操作。

![图片.png](https://image.3001.net/images/20190808/1565253537_5d4bdfa159aaf.png!small)

如下所示传入的0x1c处的值最终被函数HMUnlockObject使用，使其+4并进行dec的操作，将导致bServerSideWindowProc位设置

![图片.png](https://image.3001.net/images/20190808/1565253544_5d4bdfa83a627.png!small)

一旦hunt窗口的bServerSideWindowProc被设置，此时我们相当于使用内核态执行对应的应用层hunt回调，在对应回调中执行shellcode，来替换对应的进程令牌，实现权限提升。

![图片.png](https://image.3001.net/images/20190808/1565253552_5d4bdfb021e6b.png!small)

整个过程如下所示，简单来说就是在根菜单xxxTrackPopupMenuEx调用时，通过hook，在根菜单生成，子菜单未生成时的WM_NCCREATE消息中取消根菜单，之后在xxxTrackPopupMenuEx发送EVENT_SYSTEM_MENUPOPUPSTART事件时，通过hook
发送消息MN_SELECTITEM MN_SELECTFIRSTVALIDITEM
MN_OPENHIERARCHY，迫使根菜单弹出子菜单，导致xxxMNOpenHierarchy调用，生成子菜单的弹出菜单对象，并链入到对应的根菜单的ppmDelayedFree链表中。根菜单xxxTrackPopupMenuEx最后调用xxxMNEndMenuState，遍历ppmDelayedFree，由于取消根菜单时，子菜单没有创建，对应的fDestroyed没有设置，最终只是将子菜单的弹出菜单对象的ppopupmenuRoot字段设置为null，从而导致之后的null地址利用。

![图片.png](https://image.3001.net/images/20190808/1565253576_5d4bdfc8daba3.png!small)

这里一个需要注意的就是第一次hMenuList[0]菜单对象调用TrackPopupMenuEx时，我们在hook消息和事件的过程中几个重要消息的先后顺序：

1\.
xxxCreateWindowEx调用创建菜单窗口对象，发送WM_NCCREATE到应用层，被我们的消息回调捕获，回调中向hMenuList[0]菜单对象发送MN_CANCELMENUS消息。

2\. xxxWindowEvent(6, v51, -4, 0,
0)发送EVENT_SYSTEM_MENUPOPUPSTART事件，被我们的事件回调捕获，回调中向hMenuList[0]菜单对象发送

MN_SELECTITEM/MN_SELECTFIRSTVALIDITEM/MN_OPENHIERARCHY

3\.
hMenuList[0]菜单对象xxxMNLoop消息循环启动，以此处理收到的消息，首先是MN_CANCELMENUS，导致hMenuList[0]菜单对象取消，之后

MN_SELECTITEM/MN_SELECTFIRSTVALIDITEM/MN_OPENHIERARCHY导致针对hMenuList[1]处理消息MN_OPENHIERARCHY

4\.
hMenuList[0]菜单对象取消后导致xxxMNLoop处理完消息后结束，执行xxxUnlockMenuState，最终hMenuList[1]弹出菜单对象ppopupmenuRoot被设置为null。

##  **调试** ****

如下所示hMenuList[0]调用xxxTrackPopupMenuEx，对应的tagPOPOUPMENU弹出窗口对象为0xfe7034a8，此时fDesktroyed没有被设置。

![图片.png](https://image.3001.net/images/20190808/1565253619_5d4bdff367c96.png!small)  

WM_NCCREATE被应用层hook代码捕获，并对该菜单发送了MN_CANCELMENUS，导致进入xxxMNCancel

![图片.png](https://image.3001.net/images/20190808/1565253626_5d4bdffa71cfd.png!small)

xxxMNCancel之前，对应的hMenuList[0] tagPOPOUPMENU fDestroyed字段。

![图片.png](https://image.3001.net/images/20190808/1565253638_5d4be0062c5f1.png!small)

执行之后，hMenuList[0] tagPOPOUPMENU fDestroyed字段被设置。

![图片.png](https://image.3001.net/images/20190808/1565253647_5d4be00fcbf28.png!small)

xxxTrackPopupMenuEx继续执行，xxxWindowEvent(6, v51, -4, 0,
0)发送EVENT_SYSTEM_MENUPOPUPSTART事件，被我们设置的事件hook捕获，并针对hMenuList[0]菜单发送MN_OPENHIERARCHY，进入函数xxxMNOpenHierarchy，在xxxMNOpenHierarchy中创建hMenuList[1]对应的tagMENUWND/tagPOPUPMENU。

![图片.png](https://image.3001.net/images/20190808/1565253658_5d4be01a65550.png!small)

hMenuList[1] 的tagPOPUPMENU如下所示

![图片.png](https://image.3001.net/images/20190808/1565253666_5d4be0225a49b.png!small)

hMenuList[1] 的tagPOPUPMENU ppopupmenuRoot 字段首先被设置为 hMenuList[0]
tagPOPUPMENU，同时hMenuList[1] tagPOPUPMENU被链入到hMenuList[0] tagPOPUPMENU
的ppmDelayedFree中。

![图片.png](https://image.3001.net/images/20190808/1565253677_5d4be02d175cb.png!small)

xxxTrackPopupMenuEx继续向下执行，xxxUnlockMenuState中，hMenuList[0]
tagMENUWND遍历ppmDelayedFree，ppmDelayedFree保存了hMenuList[1]
tagPOPUPMENU，由于对应的fDestroyed没有设置，因此直接将hMenuList[1]
tagPOPUPMENU的ppopupmenuRoot置null。

![图片.png](https://image.3001.net/images/20190808/1565253685_5d4be0355a5f6.png!small)

对应的函数调用如下所示

![图片.png](https://image.3001.net/images/20190808/1565253693_5d4be03d44b24.png!small)

之后通过hMenuList[1]调用xxxTrackPopupMenuEx，最终在函数HMAssignmentLock中，如下所示hMenuList[1]
tagPOPUPMENU 的ppopupmenuRoot字段为0，最终会将0x1c处的值作为第一个参数传入

![图片.png](https://image.3001.net/images/20190808/1565253701_5d4be04530534.png!small)

而0x1c处的值被我们设置为了hunt窗口对象+0x12的位置，我们的目标是最终设置bServerSideWindowProc的值

![图片.png](https://image.3001.net/images/20190808/1565253708_5d4be04cc60d7.png!small)

最终进入函数HMUnlockObject，可以看到第一个参数就是我在0x1c位置布置的hunt tagWnd+0x12.

![图片.png](https://image.3001.net/images/20190808/1565253716_5d4be0547bd41.png!small)

此时将tagWnd+0x12的地址+4，并将地址中对应的值减一，这将导致0x18处的bServerSideWindowProc值被设置。

![图片.png](https://image.3001.net/images/20190808/1565253724_5d4be05c35a2c.png!small)

减一之后。

![图片.png](https://image.3001.net/images/20190808/1565253730_5d4be062c2a5f.png!small)

可以看到此时hunt tagWnd对象的bServerSideWindowProc字段已经被设置。

![图片.png](https://image.3001.net/images/20190808/1565253737_5d4be0695aa3c.png!small)

此时向hunt窗口发送指定消息，触发shellcode执行并替换进程令牌以实现越权。

![图片.png](https://image.3001.net/images/20190808/1565253743_5d4be06f8eb6a.png!small)

这里有一个疑问，就是如果使用我之前的老版本的win7测试，发现漏洞并不能触发，看了下代码发现老版本的win32k.sys驱动中的xxxTrackPopupMenuEx函数中，并没有调用xxxUnlockMenuState导致。

![图片.png](https://image.3001.net/images/20190808/1565253755_5d4be07b1c0e3.png!small)

可以看到对应的tagPOPUPMENU并没有设置为null。

![图片.png](https://image.3001.net/images/20190808/1565253762_5d4be082c0ed6.png!small)  

但是这并不是意味着老版本的win32k中没有xxxUnlockMenuState，实际上只是在xxxTrackPopupMenuEx中没有调用而已.

![图片.png](https://image.3001.net/images/20190808/1565253774_5d4be08e5ec5b.png!small)

##  **补丁对比** ****

微软的补丁修改中直接将xxxMNOpenHierarchy中HMAssignmentLock触发函数前设置了null监控，防止传入对应null地址。

![图片.png](https://image.3001.net/images/20190808/1565253780_5d4be09476444.png!small)  

#  **恶意代码部分** ****

Eset在其文章中给出两个该组织投递的恶意样本，具体的md5如下，虽然这两个攻击样本都不是0day事件中使用的样本，但是eset的文章中提到攻击中使用的手法是一致的，因此从这些样本中我们能看看这个团伙在攻击中使用样本的一些特点。

b54b618a9a6abd879e6703a9a4a53e94

f36fe1716c9e38fa39186b63339ebee6

##  **b54b618a9a6abd879e6703a9a4a53e94** ****

该样本打开之后如下所示：

![图片.png](https://image.3001.net/images/20190808/1565253798_5d4be0a62713c.png!small)  

点击确认宏运行之后，真正的载荷如下所示

![图片.png](https://image.3001.net/images/20190808/1565253806_5d4be0ae7673c.png!small)  

可以看到是企业合同相关的内容。

![图片.png](https://image.3001.net/images/20190808/1565253814_5d4be0b68f58d.png!small)  

Vbs恶意代码会将对应的恶意exe及实际诱饵文档拷贝到office目录下，如下图所示诱饵文档为myfile.rtf。

![图片.png](https://image.3001.net/images/20190808/1565253822_5d4be0be3bdfc.png!small)  

对应的恶意exe伪装为putty程序。

![图片.png](https://image.3001.net/images/20190808/1565253831_5d4be0c76eb34.png!small)  

实际的诱饵和恶意exe是写到控件中的。

![图片.png](https://image.3001.net/images/20190808/1565253839_5d4be0cf1f1ec.png!small)  

如下所示，释放到office目录下的诱饵和恶意exe。

![图片.png](https://image.3001.net/images/20190808/1565253879_5d4be0f7b3905.png!small)  

该putty实际上是通过nsis打包的安装文件，通过7zip打开如下所示：

$0：实际的恶意代码

$PLUGINSIDR:辅助nsis脚本的插件，实际就是一个写好的dll

[NSIS].nsi:具体的nsis脚本

![图片.png](https://image.3001.net/images/20190808/1565253885_5d4be0fdc4f50.png!small)  

可以看到nsis是windows下安装程序的制作程序，需要注意的是nsis中是通过脚本语言来描述安装程序的行为和逻辑的，这就给了攻击者很大的操作空间，我们可以在第二个样本中看到。

![图片.png](https://image.3001.net/images/20190808/1565253894_5d4be1069d928.png!small)  

该样本的nsis脚本很简单，一开始通过HideWindow字段标记该次安装为隐藏安装，之后调用fun_3，fun_3将压缩包中$0目录下的文件释放到指定目录，通过插件CreateMutex创建互斥量38A81F7C-266A-4509-82E2-34C6E0956EF7，最后调用fun_0.

![图片.png](https://image.3001.net/images/20190808/1565253902_5d4be10e2ae8d.png!small)  

fun_0中将avz.exe设置开机启动，并运行。

![图片.png](https://image.3001.net/images/20190808/1565253910_5d4be1166405d.png!small)

释放的恶意代码目录如下：

Avz.exe:该文件是一个白文件，通过其加载对应update.dll及winspool.drv文件

Update.dll:该文件是一个密码窃取工具，主要用于窃取受害者机器上浏览器，邮箱等凭据

Winspool.drv:一个buhtrap常用的后门

![图片.png](https://image.3001.net/images/20190808/1565253918_5d4be11ea39a1.png!small)  

###  **W** **inspool.drv** ****

Winspool.drv是一个dll，由avz.exe加载，对应的入口如下所示：

![图片.png](https://image.3001.net/images/20190808/1565253925_5d4be1255c478.png!small)

样本中使用的字符串都通过加密算法加密，一共使用了三种加密手段，且每个字符使用不同的密钥，调用时的堆栈也有所区别，以增加安全人员的分析成本。

![图片.png](https://image.3001.net/images/20190808/1565253932_5d4be12cc138a.png!small)

主函数中的fun_HooksysApi用于hook系统api
showwindow/createwinodwex/shell_notifyicona，如下所示fun_Hookapi函数中依次传入hook目标api地址，用于保存hook
api头部内容的内存地址，hook回调函数。

![图片.png](https://image.3001.net/images/20190808/1565253939_5d4be133dd4ef.png!small)  

fun_Hookapi中首先保存了目标api的前几个字节的内容。通过VirtualProtect修改目标api内存页属性，写入对应的jmp
hook指令，最后VirtualProtect再次调用，以恢复之前的内存页属性。

![图片.png](https://image.3001.net/images/20190808/1565253946_5d4be13aed166.png!small)

fun_StoretheOriginaddress中直接通过memcpy的方式保存hook 目标api前几个字节的内容。

![图片.png](https://image.3001.net/images/20190808/1565253953_5d4be141d5419.png!small)

如下所示CreateWindowEx的hook效果如下：

![图片.png](https://image.3001.net/images/20190808/1565253962_5d4be14a6fa68.png!small)

但是看过对应的hook回调函数，就会发现实际上这个样本中的hook没有作用，如下所示，hook回调的任务就是将执行流又传递给系统api，因此这里猜测这个hook
api的功能目前应该还只是测试阶段，而攻击者应该是希望通过hook api的方式来转移样本的执行流程，类似银行木马icedid的操作。

![图片.png](https://image.3001.net/images/20190808/1565253969_5d4be151bc48e.png!small)

对应的主线程中的代码如下所示，一共再次启动了三个线程其中

线程一：主线程

线程二：键盘记录

线程三：类似守护线程。

![图片.png](https://image.3001.net/images/20190808/1565253977_5d4be159a5247.png!small)

fun_Connectcc中解密出对应的cc

![图片.png](https://image.3001.net/images/20190808/1565253984_5d4be16060efd.png!small)

主线程函数如下所示:

![图片.png](https://image.3001.net/images/20190808/1565253992_5d4be1687a965.png!small)

fun_ForsmartCard中用于读取和电脑设备连接的smart card信息

![图片.png](https://image.3001.net/images/20190808/1565253999_5d4be16fcd23c.png!small)

和cc连接，并下载对应的payload，payload猜测有包含后续smartcad dump相关的内容。

![图片.png](https://image.3001.net/images/20190808/1565254009_5d4be179815f8.png!small)

加载后续的payload，支持exe和dll。

![图片.png](https://image.3001.net/images/20190808/1565254018_5d4be182abb89.png!small)

线程二创建了一个窗口，被设定了对应的窗口回调。

![图片.png](https://image.3001.net/images/20190808/1565254025_5d4be18982636.png!small)  

窗口回调中通过GetRawInputData的方式实现键盘记录

![图片.png](https://image.3001.net/images/20190808/1565254032_5d4be1907e76d.png!small)  

需要注意的是该键盘记录只记录指定的进程，如下所示

![图片.png](https://image.3001.net/images/20190808/1565254041_5d4be1994e9e0.png!small)

线程三中监控系统中是否存在互斥量38A81F7C-266A-4509-82E2-34C6E0956EF7，该互斥量由一开始的nsis脚本创建。

![图片.png](https://image.3001.net/images/20190808/1565254048_5d4be1a0f1eba.png!small)

加载模块update.dll。

![图片.png](https://image.3001.net/images/20190808/1565254055_5d4be1a7a6d8e.png!small)

###  **U** **pdate.dll** ****

Update.dll相关的窃取目标如下所示:

![图片.png](https://image.3001.net/images/20190808/1565254068_5d4be1b42569f.png!small)  

##  **f36fe1716c9e38fa39186b63339ebee6** ****

该恶意文档打开如下所示，诱饵文档的内容是用户如何通过一系列操作看到文档的真实内容，但是这些操作实际是执行恶意宏的过程。

![图片.png](https://image.3001.net/images/20190808/1565254075_5d4be1bbd2e88.png!small)  

该样本同样通过恶意vbs执行释放文件，如下所示。

![图片.png](https://image.3001.net/images/20190808/1565254085_5d4be1c55635f.png!small)  

确认运行之后的真实内容。

![图片.png](https://image.3001.net/images/20190808/1565254092_5d4be1cca9f9d.png!small)

主要是一份采购清单。

![图片.png](https://image.3001.net/images/20190808/1565254098_5d4be1d214fe7.png!small)  

释放的恶意exe同样是一个nsis的安装程序，但是这个样本相较前一个就比较复杂了

$PLUGINSDIR:辅助nsis脚本运行的插件，这个样本中使用了多个插件

$TEMP:保存了对应的凭据窃取工具，和前一个样本一致

$0:一段用于load 的shellcode

$0_1: Meterpreter

[NSIS].nis:对应的nsis脚本

![图片.png](https://image.3001.net/images/20190808/1565254106_5d4be1dacaf8c.png!small)  

$PLUGINSDIR中的插件如下所示：

Createmutex.dll:用于设置互斥量相关的操作，这也是前一个样本中使用到的唯一一个插件

nsExec.dll:用于辅助nsis脚本执行cmd命令

System.dll:用于辅助nsis脚本调用系统api

![图片.png](https://image.3001.net/images/20190808/1565254113_5d4be1e195745.png!small)  

Nsis脚本同样通过HideWindow设置隐藏安装，之后调用函数func_516.

![图片.png](https://image.3001.net/images/20190808/1565254119_5d4be1e79c3b0.png!small)  

该nsis脚本为了获取更为强大的功能，通过调用插件System.dll的方式来调用windows系统api，如下函数就直接调用了VirtualAllocEx函数。

![图片.png](https://image.3001.net/images/20190808/1565254127_5d4be1efd2dfc.png!small)

func_516经过一系列处理之后调用函数fun_389.

![图片.png](https://image.3001.net/images/20190808/1565254133_5d4be1f5c6989.png!small)

fun_389设置开机启动，并修改了防火墙的过滤规则，以允许恶意代码和cc的通信，之后调用fun_224.

![图片.png](https://image.3001.net/images/20190808/1565254144_5d4be200aebbd.png!small)

文档释放的最终nsis安装包。

![图片.png](https://image.3001.net/images/20190808/1565254151_5d4be2073ceed.png!small)  

通过nsis设置了具体的开机启动项

![图片.png](https://image.3001.net/images/20190808/1565254160_5d4be210300d6.png!small)

fun_224用于在内存中直接加在两段shellcode，具体步骤如第一个红框所示。

![图片.png](https://image.3001.net/images/20190808/1565254167_5d4be217081c5.png!small)  

最终shellcode $0,$0_1通过一个线程启动。

![图片.png](https://image.3001.net/images/20190808/1565254175_5d4be21f4d7a5.png!small)

Shellcode如下所示:

![图片.png](https://image.3001.net/images/20190808/1565254180_5d4be224a9871.png!small)

第一段load shellcode

![图片.png](https://image.3001.net/images/20190808/1565254188_5d4be22ca50d4.png!small)  

第二段包含Meterpreter的shellcode

![图片.png](https://image.3001.net/images/20190808/1565254197_5d4be235364d4.png!small)

# **参考链接** ****

[ _https://pwnrip.com/exploiting-cve-2019-1132-another-null-pointer-dereference-in-windows-kernel/_](https://pwnrip.com/exploiting-cve-2019-1132-another-null-pointer-dereference-in-windows-kernel/)

 _https://www.anquanke.com/post/id/102377?from=timeline#h3-6_ __

[ _https://www.welivesecurity.com/2019/07/11/buhtrap-zero-day-espionage-campaigns/_](https://www.welivesecurity.com/2019/07/11/buhtrap-zero-day-espionage-campaigns/)

[ _https://www.welivesecurity.com/2019/07/10/windows-zero-day-cve-2019-1132-exploit/_](https://www.welivesecurity.com/2019/07/10/windows-zero-day-cve-2019-1132-exploit/)

[
_https://blog.csdn.net/mfkjq/article/details/53307987_](https://blog.csdn.net/mfkjq/article/details/53307987)

[ _https://baike.baidu.com/item/nsis_](https://baike.baidu.com/item/nsis)

[ _https://www.group-ib.com/brochures/gib-buhtrap-report.pdf_](https://www.group-ib.com/brochures/gib-buhtrap-report.pdf)

