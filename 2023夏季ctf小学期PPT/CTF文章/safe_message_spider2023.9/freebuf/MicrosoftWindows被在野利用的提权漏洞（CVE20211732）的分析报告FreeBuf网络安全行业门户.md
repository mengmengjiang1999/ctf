## 背景

2021年03月10日，奇安信威胁情报中心监测发现CVE-2021-1732漏洞利用细节及POC已经被公开，故发布该漏洞分析报告。

2021年2月，微软在例行补丁日中修复了一枚在野的Windows
内核提权漏洞：CVE-2021-1732。与此同时，奇安信红雨滴团队在高级威胁狩猎中通过自研的红雨滴沙箱也自动捕获到该在野攻击样本，样本在红雨滴云沙箱上通过选择Windows
10 x64分析环境进行检测，可以准确识别到样本在运行过程中进行了提权攻击，从而最终进入了我们的分析视野。

![1619441584_6086b7b06d67679f4dff2.png!small?1619441586248](https://image.3001.net/images/20210426/1619441584_6086b7b06d67679f4dff2.png!small?1619441586248)

https://sandbox.ti.qianxin.com/sandbox/page

## 漏洞分析

捕获到的攻击样本包含以下的编译pdb

> C:\Users\Win10\source\repos\KSP_EPL\x64\Release\ConsoleApplication13.pdb

![1619441594_6086b7baa51f67fda3fe7.png!small](https://image.3001.net/images/20210426/1619441594_6086b7baa51f67fda3fe7.png!small)

在win10
1909上运行之后可以看到提权程序被提升到system权限，这里需要注意该程序直接运行完毕后就退出了，因此需要通过调试器附加运行才能看到具体的提权效果。

![1619441610_6086b7cac5b5cc9e76204.png!small?1619441612555](https://image.3001.net/images/20210426/1619441610_6086b7cac5b5cc9e76204.png!small?1619441612555)

该漏洞由CreateWindowExW函数产生，CreateWindowExW函数最终会调用到在win32kfull.sys中xxxCreateWindowEx函数，当通过该函数创建一个带扩展内存的窗口时，xxxCreateWindowEx会调用xxxClientAllocWindowClassExtraBytes以分配对应的扩展内存，并将返回值保存到poi(tagWND+0x28)+0x128的位置，而这里poi(tagWND+0x28)+0x128实际是保存了对应窗口的扩展内存的位置，但是这个位置的值有两种情况，内存指针或该内存的内核offset，而具体为哪一种方式则依赖于(tagWND+0x28)+0xE8的位置来确定，默认情况下为内存指针。

![1619441630_6086b7de4383a34b1b88e.png!small?1619441632023](https://image.3001.net/images/20210426/1619441630_6086b7de4383a34b1b88e.png!small?1619441632023)

而xxxClientAllocWindowClassExtraBytes实际分配内存的操作是通过KeUserModeCallback函数进行的内核回调生成的。

![1619441641_6086b7e9894d65ee8980f.png!small?1619441643272](https://image.3001.net/images/20210426/1619441641_6086b7e9894d65ee8980f.png!small?1619441643272)

KeUserModeCallback函数的参数原型如下所示，其中比较重要的是第一个ApiNumber，该参数指定了返回到应用层时对应的回调函数在KernelCallbackTable中的序号，并通过该序号获取对应的回调函数的地址，之后的两组参数分别为对应的回调调用的输入参数/参数长度，及回调返回时的输出参数/参数长度。

![1619441650_6086b7f2ba52c868d4a09.png!small?1619441652653](https://image.3001.net/images/20210426/1619441650_6086b7f2ba52c868d4a09.png!small?1619441652653)

KeUserModeCallback最终返回到应用层的KiUserCallbackDispatcher，该函数通过PEB获取KernelCallbackTable，这个表中记录了一系列内核返回应用层的回调函数，通过KeUserModeCallback传递的第一个参数ApiNumber寻址到目标回调函数，回调调用完毕后通过int2B
触发KiCallbackReturn返回内核。

![1619441825_6086b8a12367b21745cdb.png!small?1619441826875](https://image.3001.net/images/20210426/1619441825_6086b8a12367b21745cdb.png!small?1619441826875)

KernelCallbackTable这张表的位置默认会保存在当前的peb中，KiUserCallbackDispatcher就是通过PEB获取该表的地址，这里需要注意这张表实际是在use32.dll中，如果当前进程没有加载该dll，peb中对应的KernelCallbackTable位置则是null，因此exp中有专门引入use32.dll的操作。

![1619441848_6086b8b842ff90be38d35.png!small?1619441850071](https://image.3001.net/images/20210426/1619441848_6086b8b842ff90be38d35.png!small?1619441850071)

如下所示为KiUserCallbackDispatcher的一个伪代码，通过peb获取对应的回调并调用后，通过函数NtCallbackReturn返回内核。

![1619441870_6086b8cec47b6695bbd21.png!small?1619441872909](https://image.3001.net/images/20210426/1619441870_6086b8cec47b6695bbd21.png!small?1619441872909)

NtCallbackReturn的原型如下，其第一个参数中保存了返回的数据，最终会赋值给KeUserModeCallback的outputstring。

![1619441878_6086b8d63204fca3c5ed3.png!small?1619441880228](https://image.3001.net/images/20210426/1619441878_6086b8d63204fca3c5ed3.png!small?1619441880228)

由于这里KernelCallbackTable的位置保存在PEB中，因此可以通过代码的方式获取到该表的地址，并对表中的回调函数的地址进行替换，从而hook任意的内核到应用层的回调函数，这里如果在hook的回调函数中调用函数NtUserConsoleControl，并传入对应的创建的窗口的句柄，将会导致对应窗口的扩展内存被设置为分配内存的offset，且对应的flag标记被设置，如下所示，NtUserConsoleControl
最终在win32kfull中会调用xxxConsoleControl。

![1619441902_6086b8eedaeaec186f5cd.png!small?1619441904694](https://image.3001.net/images/20210426/1619441902_6086b8eedaeaec186f5cd.png!small?1619441904694)

xxxConsoleControl中如下所示可以看到poi(tagWND
+0x28)+0x128处最终被设置为到DesktopAlloc分配的内存空间的offset，同时对应poi(tagWND+0x28)+0xE8处的flag标记被设置为offset寻址。

![1619441926_6086b906bca10c5e66abe.png!small?1619441928531](https://image.3001.net/images/20210426/1619441926_6086b906bca10c5e66abe.png!small?1619441928531)

而这里如果我们在回调hook函数中手动调用NtCallbackReturn，由于漏洞将可以再次设置该窗口的扩展内存，由于之前NtUserConsoleControl已经将该窗口的flag设置为offset，因此这里实际上通过NtCallbackReturn二次设置该offset为任意攻击者指定的地址。

![1619441970_6086b9321db22142d2c8a.png!small?1619441972007](https://image.3001.net/images/20210426/1619441970_6086b9321db22142d2c8a.png!small?1619441972007)

因此该漏洞的实质就是，在创建一个带扩展内存的窗口时，内核中xxxClientAllocWindowClassExtraBytes的应用层回调对来自应用层返回的数据校验不严导致，通过hook
xxxClientAllocWindowClassExtraBytes，并在hook函数中调用NtUserConsoleControl/NtCallbackReturn可以将目标窗口的poi(tagWND+0x28)+0x128位置设置为任意offset，从而导致越界写入。

## 漏洞利用原理分析

具体的利用主函数如下所示，实际的利用代码在函数fun_Eprivlcore中。

![1619442007_6086b957df78d5c046c51.png!small?1619442009905](https://image.3001.net/images/20210426/1619442007_6086b957df78d5c046c51.png!small?1619442009905)

fun_Eprivlcore中首先遍历系统进程，以确认是否有卡巴斯基的杀软安装。

![1619442014_6086b95ee41835cee0253.png!small?1619442016700](https://image.3001.net/images/20210426/1619442014_6086b95ee41835cee0253.png!small?1619442016700)

之后判断运行环境是否为64位系统，该代码目前只支持64位系统，并初始化一系列偏移常量。

![1619442028_6086b96c7cf866b37de83.png!small?1619442030228](https://image.3001.net/images/20210426/1619442028_6086b96c7cf866b37de83.png!small?1619442030228)

依次动态获取/RtlGetNtVerisonNumbers/NtUserConsoleControl/NtCallbackReturn函数的地址

![1619442049_6086b98106835ec3ca600.png!small?1619442050731](https://image.3001.net/images/20210426/1619442049_6086b98106835ec3ca600.png!small?1619442050731)

通过函数RtlGetNtVerisonNumbers判断具体的win10系统版本，这里会判断具体的win10版本是否大于1709，其支持的目标涉及1709-1909，当系统版本大于1903，则会修改其中部分偏移常量的数值，并进入到fun_EOP中进行具体的提权操作。

![1619442066_6086b992b2466eebd62d9.png!small?1619442068590](https://image.3001.net/images/20210426/1619442066_6086b992b2466eebd62d9.png!small?1619442068590)

fun_EOP中调用函数fun_Init/fun_Inithwnd完成前期的初始化工作

![1619442078_6086b99ec6bc45989a01a.png!small?1619442080607](https://image.3001.net/images/20210426/1619442078_6086b99ec6bc45989a01a.png!small?1619442080607)

fun_Init中首先通过IsMenu函数搜索未导出的函数pHmValidateHandle，该函数可用于获取一个应用层窗口句柄对应的内核句柄对象在应用层的内存映射。

之后通过PEB获取kernelCallbackTable，并修改该表中xxxClientAllocWindowClassExtraBytes函数的地址，将其指向fun_HOOKClientAllocWindowClassExtraBytes，完成对应xxxClientAllocWindowClassExtraBytes函数的hook

![1619442092_6086b9ac4953cb071203d.png!small?1619442094270](https://image.3001.net/images/20210426/1619442092_6086b9ac4953cb071203d.png!small?1619442094270)

之后创建两个窗口类normalClass/magicClass，注意这里magicClass窗口类在申明的时候对应cbWndExtra扩展内存字段的大小设置为var_magicClasscbWndExtra，该值是一个随机生成的长度，而normalClass的cbWndExtra则设置为32，通过var_magicClasscbWndExtra就可以在hook函数中判断具体的回调是来自于哪一个窗口的内核回调

而这里normalClass用于生成辅助的利用窗口

而magicClass则是具体触发漏洞的窗口。

![1619442110_6086b9bedc6434e0100cf.png!small?1619442113149](https://image.3001.net/images/20210426/1619442110_6086b9bedc6434e0100cf.png!small?1619442113149)

fun_Inithwnd中通过normalClass创建10个窗口0-9，并将10个窗口句柄保存在hWnd这个数组中，同时调用var_pHmValidateHandle获取这10个窗口句柄对应的内核窗口对象在应用层的映射，并保存到v23这个数组中。

![1619442147_6086b9e3751fb3a83f749.png!small?1619442149283](https://image.3001.net/images/20210426/1619442147_6086b9e3751fb3a83f749.png!small?1619442149283)

之后通过LocalAlloc分配内存，并构造对应的fakespmenu，fakespmenu会在之后用于实现任意地址读的功能。

![1619442154_6086b9ea33abdff79a12a.png!small?1619442155931](https://image.3001.net/images/20210426/1619442154_6086b9ea33abdff79a12a.png!small?1619442155931)

构造出的fakespmenu相关内存结构如下所示，最终的目标读取地址会写入到var_OffsetrcBarleft

![1619442171_6086b9fb422e36d212890.png!small?1619442173153](https://image.3001.net/images/20210426/1619442171_6086b9fb422e36d212890.png!small?1619442173153)

依次获取第0和第1个应用层的窗口句柄，及对应的内核窗口对象的应用层映射地址，并通过映射地址获取该内核对象在内核地址中的偏移（位置在内核对象偏移0x8的位置保存），之后依次将2-0个窗口对象通过函数DestroyWindow释放，并通过函数var_NtUserConsoleControl将第0个窗口对象的扩展内存寻址设置为offset类型。

![1619442188_6086ba0c22bf9532efd2c.png!small?1619442189950](https://image.3001.net/images/20210426/1619442188_6086ba0c22bf9532efd2c.png!small?1619442189950)

如下所示r14和rsi中依次保存了0，1的窗口对象的应用层映射内存，其偏移0x8的位置为对应的内核对象在内核地址中的偏移。

![1619442231_6086ba37bfe3c7fa83c8a.png!small?1619442233614](https://image.3001.net/images/20210426/1619442231_6086ba37bfe3c7fa83c8a.png!small?1619442233614)

通过magicClass类创建窗口，这里简称为窗口2，由于magicClass窗口类中对应的cbwndExtra字段和hook函数中的一致，因此窗口2创建的过程中会触发漏洞函数xxxClientAllocWindowClassExtraBytes并最终通过内核回调进入到我们设置的hook函数中。

![1619442239_6086ba3f815dec48cc726.png!small?1619442241304](https://image.3001.net/images/20210426/1619442239_6086ba3f815dec48cc726.png!small?1619442241304)

内核中函数xxxClientAllocWindowClassExtraBytes调用前，可以看到此时窗口2对应的cbwndExtra为12a5。

![1619442249_6086ba496c871573a3c8f.png!small?1619442251259](https://image.3001.net/images/20210426/1619442249_6086ba496c871573a3c8f.png!small?1619442251259)

win10中tagWND对象的符号已经被删除，其内容也发生了相当的变化，以下为通过分析之后还原出的tagWND的重要结构，上图中的ffffff0681244870即为对应的pwnd，位于tagWND偏移0x28，其中比较重要的是

> 0x98 spmenu 窗口对应的menu菜单对象
>
> 0xc8 cbwndExtra 窗口对应扩展内存的大小
>
> 0xe8 Extra flag 窗口对象扩展内存的寻址标记，支持指针寻址，和偏移寻址，默认为指针寻址
>
> 0x128 pExtraBytes 保存扩展内存对应的位置，根据Extra flag为指针或offset偏移

![1619442279_6086ba67ed25631b0e6bc.png!small?1619442281842](https://image.3001.net/images/20210426/1619442279_6086ba67ed25631b0e6bc.png!small?1619442281842)

tagWND偏移0x18+0x80的位置为对应的内核基地址，配合上对应的内核偏移就可以计算出对应的tagWND对象pwnd在内核中的偏移。

![1619442295_6086ba77576c621952890.png!small?1619442297189](https://image.3001.net/images/20210426/1619442295_6086ba77576c621952890.png!small?1619442297189)

具体的hook函数如下，由于窗口2在创建时使用的是maginClass类，其对应的cbWndExtra符合hook函数中的过滤条件，因此触发对应的var_xxxClientAllocWindowClassExtraByteshook，进入具体的hook流程中，hook中通过函数fun_FindcurrenHwnd获取到当前窗口的hwnd，并以此调用NtUserConsoleControl，将其对应内核对象poi(tagWND2+0x28)+0xE8的处flag标记设置为offset类型寻址，之后将var_normalClassoffset0作为var_NtCallbackReturn参数返回，这将导致var_normalClassoffset0写入到窗口2poi(tagWND2+0x28)+0x128处，此时通过对var_magicClasshwnd2调用SetWindowLongW（该函数用来改变指定窗口的属性，函数也将指定的一个32位值设置在窗口的扩展内存空间的指定偏移位置）来修改扩展空间内存内容时，实际上修改的是var_normalClasshwnd0句柄对应内核对象pwnd的内容。

![1619442317_6086ba8d1577eccbceb66.png!small?1619442318826](https://image.3001.net/images/20210426/1619442317_6086ba8d1577eccbceb66.png!small?1619442318826)

NtUserConsoleControl对应的内核函数为xxxConsoleControl，如下所示会设置pwnd偏移0xE8处的扩展内存寻址flag为offset类型，并初始化对应的扩展内存pExtraBytes为对应内存的内核偏移。

![1619442327_6086ba9731e7c0a7653ed.png!small?1619442328948](https://image.3001.net/images/20210426/1619442327_6086ba9731e7c0a7653ed.png!small?1619442328948)

xxxConsoleControl调用之后的2窗口如下所示，注意此时的pExtraBytes还没有被设置指向0窗口内核对象的pwnd内核偏移。

![1619442363_6086babb554697a4bf207.png!small?1619442365460](https://image.3001.net/images/20210426/1619442363_6086babb554697a4bf207.png!small?1619442365460)

直到内核回调返回之后2窗口内核对象的pwnd.pExtraBytes字段此时才被设置为0窗口内核对象的pwnd的内核偏移，之后通过xxxSetWindowLong设置窗口2的扩展内存时，实际的操作地址将是0窗口内核对象的pwnd。至此可以通过窗口2调用xxxSetWindowLong来将窗口0的cbwndExtra字段设置为0xfffffff，以此获取越界写入的能力。

![1619442374_6086bac69caf9a863c49a.png!small?1619442376506](https://image.3001.net/images/20210426/1619442374_6086bac69caf9a863c49a.png!small?1619442376506)

漏洞触发后的2窗口内核对象的pwnd，此时扩展内存寻址flag已经设置为offset寻址，对应的pExtraBytes已经被修改为窗口0的内核对象pwnd的内核偏移。

![1619442383_6086bacf6a6cf609173ed.png!small?1619442385699](https://image.3001.net/images/20210426/1619442383_6086bacf6a6cf609173ed.png!small?1619442385699)

此时通过对var_magicClasshwnd窗口2调用SetWindowLongW，将var_normalClasshwnd0窗口0对应的tagWND0.cbWndExtra设置为0xffffff，操作结束后var_normalClasshwnd0窗口0对应的cbWndExtra将设置为0xffffff，此时var_normalClasshwnd0窗口0具备了越界写入的能力。

通过var_normalClasshwnd0窗口0调用SetWindowLongPtrA设置var_normalClasshwnd1窗口1的dwStely字段，并通过var_normalClasshwnd1窗口1调用SetWindowLongPtrA将spmenu设置为fakespmenu伪造的menu对象，用于实现任意地址读，这里将窗口1的dwStely修改为WS_CHILD将确保spmenu能进行设置，当fakespmenu设置成功之后，还会将该dwStely的类型还原，因为只有在原dwStely中，var_normalClasshwnd1才能通过调用GetMenuBarInfo依赖fakespmenu进入到特定的错误代码的代码分支，以实现具体的读取操作，总结一句话就是通过窗口0的越界写能力将窗口0设置为错误类型，并附加错误的菜单对象，以此来实现任意地址读取。

![1619442448_6086bb1075c570c88fcbc.png!small?1619442450397](https://image.3001.net/images/20210426/1619442448_6086bb1075c570c88fcbc.png!small?1619442450397)

整个利用过程中关键窗口的设置操作如下所示:

![1619442459_6086bb1b3659c96d3f027.png!small?1619442461027](https://image.3001.net/images/20210426/1619442459_6086bb1b3659c96d3f027.png!small?1619442461027)

xxxSetWindowLong对应的内核代码如下，其中if中对应扩展内存的offse寻址方式。else为指针寻址方式

![1619442477_6086bb2d20382157990d1.png!small?1619442479037](https://image.3001.net/images/20210426/1619442477_6086bb2d20382157990d1.png!small?1619442479037)

通过窗口2调用SetWindowLong，将扩展内存c8的位置设置为fffffff，由于窗口2内核对象的pwnd.
pExtraBytes已经被设置为窗口0内核对象的pwnd内核偏移，此时将直接把fffffff写入到窗口0内核对象的pwnd+0xc8处，即0窗口内核对象的pwnd.
cbwndExtra。

![1619442488_6086bb3894d36e2183f4d.png!small?1619442490539](https://image.3001.net/images/20210426/1619442488_6086bb3894d36e2183f4d.png!small?1619442490539)

如下所示获取pExtraBytes(窗口0内核对象的pwnd内核偏移)+内核基址+c8

![1619442496_6086bb4014b8ac10fb57b.png!small?1619442497880](https://image.3001.net/images/20210426/1619442496_6086bb4014b8ac10fb57b.png!small?1619442497880)

可以看到此时计算出的目标地址就是窗口0内核对象的pwnd. cbwndExtra，其原本的大小为0x20，ffffffff写入后窗口0对象将具备越界写能力。

![1619442504_6086bb48dda7c21766b9b.png!small?1619442506684](https://image.3001.net/images/20210426/1619442504_6086bb48dda7c21766b9b.png!small?1619442506684)

写入成功。

![1619442513_6086bb513d068723bf1e8.png!small?1619442515115](https://image.3001.net/images/20210426/1619442513_6086bb513d068723bf1e8.png!small?1619442515115)

之后通过窗口0调用SetWindowLongPtrA以修改窗口1的dwStely属性

![1619442523_6086bb5bbeb7f76fae40f.png!small?1619442525454](https://image.3001.net/images/20210426/1619442523_6086bb5bbeb7f76fae40f.png!small?1619442525454)

SetWindowLongPtrA和SetWindowLong的实现大同小异，如下红框所示为对应的扩展内存offset寻址的实现方式。

![1619442529_6086bb61705bfa6f0ddcc.png!small?1619442531255](https://image.3001.net/images/20210426/1619442529_6086bb61705bfa6f0ddcc.png!small?1619442531255)

进入内核xxxSetWindowLongPtr函数

![1619442535_6086bb670dd0ebd10bb17.png!small?1619442536889](https://image.3001.net/images/20210426/1619442535_6086bb670dd0ebd10bb17.png!small?1619442536889)

如下所示为窗口1内核对象的pwnd，需要修改的dwStely位置在其偏移0x18处（right红框才是正确位置）

![1619442548_6086bb741c8ab61856664.png!small?1619442550116](https://image.3001.net/images/20210426/1619442548_6086bb741c8ab61856664.png!small?1619442550116)

检测判断对应的寻址flag

![1619442557_6086bb7dcde610e586c04.png!small?1619442559702](https://image.3001.net/images/20210426/1619442557_6086bb7dcde610e586c04.png!small?1619442559702)

进入offset寻址流程，如下获取对应的内核基地址，此时的偏移15308为窗口0/1内核对象的pwnd内核偏移的差值+0x18（dwStely的pwnd偏移）。

![1619442571_6086bb8b360b44e87687b.png!small?1619442573131](https://image.3001.net/images/20210426/1619442571_6086bb8b360b44e87687b.png!small?1619442573131)

最终计算出窗口1内核的pwnd.dwStely地址，写入将其设置为WS_CHILD类型(right红框才是正确位置)。

![1619442578_6086bb9294d97995689dd.png!small?1619442580421](https://image.3001.net/images/20210426/1619442578_6086bb9294d97995689dd.png!small?1619442580421)

写入结果如下所示

![1619442585_6086bb992dd3fc6a19992.png!small?1619442586989](https://image.3001.net/images/20210426/1619442585_6086bb992dd3fc6a19992.png!small?1619442586989)

之后通过窗口1调用SetWindowLongPtrA将窗口1的spmenu设置指向前面构造的fakespmenu

![1619442592_6086bba06c1ec7036c375.png!small?1619442594236](https://image.3001.net/images/20210426/1619442592_6086bba06c1ec7036c375.png!small?1619442594236)

这里可以看到，实际上此时SetWindowLongPtrA设置的参数为-12(0xFFFFFFF4)，即为设置子窗口的新标识符。但是需要注意这里注明了该窗口不能是顶级窗口

![1619442599_6086bba7f3c5f1956fdc9.png!small?1619442601750](https://image.3001.net/images/20210426/1619442599_6086bba7f3c5f1956fdc9.png!small?1619442601750)

而当函数xxxSetWindowLongPtr对应的第二个参数不为偏移，而是特殊的负数标记id时，将会进入到函数xxxSetWindowData函数中处理，也就是我们这里的情况

![1619442607_6086bbafdbe58d02b9d70.png!small?1619442609639](https://image.3001.net/images/20210426/1619442607_6086bbafdbe58d02b9d70.png!small?1619442609639)

如下所示为对应的-12时的处理逻辑，可以看到这里会检测对应窗口的类型是否为WS_CHILD，如果是则将value(这里指向了我们构造的fakespmenu)设置到对应窗口内核对象0xa和窗口内核对象的pwnd偏移0x98位置

![1619442614_6086bbb6b609126d3dc5e.png!small?1619442616615](https://image.3001.net/images/20210426/1619442614_6086bbb6b609126d3dc5e.png!small?1619442616615)

如下所示内核调试器进入xxxSetWindowLongPtr

![1619442621_6086bbbd01c47bcd10d93.png!small?1619442622751](https://image.3001.net/images/20210426/1619442621_6086bbbd01c47bcd10d93.png!small?1619442622751)

经过判断之后进入xxxSetWindowData函数中。

![1619442628_6086bbc49c16bca9ff5a5.png!small?1619442630590](https://image.3001.net/images/20210426/1619442628_6086bbc49c16bca9ff5a5.png!small?1619442630590)

进入对应的-12分支处理逻辑。

![1619442638_6086bbce9aba9768e23b9.png!small?1619442640383](https://image.3001.net/images/20210426/1619442638_6086bbce9aba9768e23b9.png!small?1619442640383)

首先判断其是否WS_CHILD类型的窗口

![1619442645_6086bbd521a6977d6d918.png!small?1619442646974](https://image.3001.net/images/20210426/1619442645_6086bbd521a6977d6d918.png!small?1619442646974)

判断通过直接将伪造的fakespmenu赋值

![1619442655_6086bbdf208e81fc6d430.png!small?1619442656901](https://image.3001.net/images/20210426/1619442655_6086bbdf208e81fc6d430.png!small?1619442656901)

窗口1内核对象及窗口1内核对象pwnd对应赋值后如下所示

![1619442662_6086bbe6ec61b25bf7032.png!small?1619442665163](https://image.3001.net/images/20210426/1619442662_6086bbe6ec61b25bf7032.png!small?1619442665163)

之后窗口0调用SetWindowLongPtrA将窗口1的dwStely还原

![1619442668_6086bbece6020ca33d7f0.png!small?1619442670810](https://image.3001.net/images/20210426/1619442668_6086bbece6020ca33d7f0.png!small?1619442670810)

进入内核xxxSetWindowLongPtr

![1619442674_6086bbf2de8dcf27171de.png!small?1619442676617](https://image.3001.net/images/20210426/1619442674_6086bbf2de8dcf27171de.png!small?1619442676617)

如下所示窗口1的dwstely已经恢复，因此这里的操作实际上是通过窗口0的越界写入能力修改了窗口1的dwStely为WS_CHILD，这将导致可以通过窗口1以GWLP_ID调用xxxSetWindowLongPtr将窗口1内核对象的pwnd.spmenu设置指向我们的fakespmenu，之后恢复窗口1的dwStely，这就导致窗口1具备了原本dwStely=WS_CHILD时才有的spmenu属性

![1619442684_6086bbfce1c5802fd6bf6.png!small?1619442686740](https://image.3001.net/images/20210426/1619442684_6086bbfce1c5802fd6bf6.png!small?1619442686740)设置spmenu之后，由于xxxSetWindowLongPtr的特性会将写入前的内容返回，此时返回的内容为一个标准的内核结构，根据该内核结构的地址配合上后续的任意地址读取，将方便的获取ERPROCESS

![1619442699_6086bc0b9a2c78b4b5a6e.png!small?1619442701389](https://image.3001.net/images/20210426/1619442699_6086bc0b9a2c78b4b5a6e.png!small?1619442701389)

借助var_normalClasshwnd1窗口1的fakespmenu，配合GetMenuBarInfo实现任意地址读取，这里首先第一次调用GetMenuBarInfo以获取对应var_OffsetrcBarleft偏移（后文会详述），之后第二次调用GetMenuBarInfo才是用于读取对应地址的数据

![1619442715_6086bc1b2c99b440f71a5.png!small?1619442716963](https://image.3001.net/images/20210426/1619442715_6086bc1b2c99b440f71a5.png!small?1619442716963)

GetMenuBarInfo的函数原型如下所示

![1619442720_6086bc20b16a7f436a522.png!small?1619442722469](https://image.3001.net/images/20210426/1619442720_6086bc20b16a7f436a522.png!small?1619442722469)

具体参数如下所示，这里漏洞利用时idObject为0xFFFFFFFD，对应的item为1，最终结果则通过第四个参数返回

![1619442727_6086bc274c9d646d560e8.png!small?1619442729110](https://image.3001.net/images/20210426/1619442727_6086bc274c9d646d560e8.png!small?1619442729110)

第四个参数为MENUBARINFO，如下所示

![1619442733_6086bc2d2ee9444b5622f.png!small?1619442735284](https://image.3001.net/images/20210426/1619442733_6086bc2d2ee9444b5622f.png!small?1619442735284)

其中的rcBar为一个矩形结构

![1619442738_6086bc3279d32d4f428bf.png!small?1619442740240](https://image.3001.net/images/20210426/1619442738_6086bc3279d32d4f428bf.png!small?1619442740240)

这里通过idObject为0xFFFFFFFD可以看到在内核中对应函数为xxxGetMenuBarInfo，其核心为-3这个逻辑代码块。

该逻辑实际上是通过窗口内核对象0xa8处获取对应的spmenu，这里窗口1对应的spmenu指向了我们恶意构造的fakespmenu，并将该段内存映射到内核，之后通过fakespmenu.fakerect.0x28处var_OffsetrcBarleft字段中的数据和窗口内核对象的pwnd指定偏移0x58/0x5c处的数据做计算，并将结果返回对应的pmbi.rcBar这个rect矩形结构，而这个过程中由于fakespmenu中的数值是攻击者完全可控的，而pwnd指定偏移0x58/0x5c默认为0，这就导致通过这个操作可以进行任意地址读取操作，这里需要注意的是实际上dwstelye=WS_CHILD，才能设置对应的spmenu，而设置了spmenu，dwstelye=WS_CHILD的窗口正常情况下并不会进入到以下的代码分支，但是因为利用中在设置了窗口1的spmenu之后，又通过窗口0的越界写恢复了窗口1的dwStely，从而可以进入以下的错误代码分支，如下所示依次计算rect的四个坐标，并保存到变量v7中。

![1619487572_60876b5427cd5baf897b0.png!small?1619487572479](https://image.3001.net/images/20210427/1619487572_60876b5427cd5baf897b0.png!small?1619487572479)

完成最后一个bottom写入

![1619487578_60876b5a1cbd98bcac53b.png!small?1619487584445](https://image.3001.net/images/20210427/1619487578_60876b5a1cbd98bcac53b.png!small?1619487584445)

如下所示第一次会读取之前原spmenu处返回的内核结构+0x50处的数据，即下图中fffff0680825000+50处的数据。

![1619487585_60876b61acff7bdaa920a.png!small?1619487586000](https://image.3001.net/images/20210427/1619487585_60876b61acff7bdaa920a.png!small?1619487586000)

读取函数中会尝试两次调用GetMenuBarInfo

第一次调用GetMenuBarInfo以获取计算时var_OffsetrcBarleft的偏移。

![1619487597_60876b6d6584be2bc18e2.png!small?1619487597703](https://image.3001.net/images/20210427/1619487597_60876b6d6584be2bc18e2.png!small?1619487597703)

之后第二次完成真正意义上的读取，首先第一次读取如下所示，此时传入的pmbi如下所示

![1619487604_60876b749b5c3deabeef0.png!small?1619487604879](https://image.3001.net/images/20210427/1619487604_60876b749b5c3deabeef0.png!small?1619487604879)

xxxGetMenuBarInfo中进入-3的代码逻辑

![1619487611_60876b7b3a9d1757fbda2.png!small?1619487611606](https://image.3001.net/images/20210427/1619487611_60876b7b3a9d1757fbda2.png!small?1619487611606)

这里会首先判断对应dwStely，如果之前不将窗口0的dwStely恢复（恢复前为4c），则不会进入之后的代码逻辑

![1619487617_60876b812e1c16bae1406.png!small?1619487617720](https://image.3001.net/images/20210427/1619487617_60876b812e1c16bae1406.png!small?1619487617720)

之后获取窗口1内核对象+0xa8处的fakespmenu对象

![1619487623_60876b87546bae01192d5.png!small?1619487623828](https://image.3001.net/images/20210427/1619487623_60876b87546bae01192d5.png!small?1619487623828)

通过该fakespmenu，调用SmartObjStackRefBase<tagMENU>::operator将其映射到内核中。

![1619487629_60876b8d14547edceae9e.png!small?1619487629423](https://image.3001.net/images/20210427/1619487629_60876b8d14547edceae9e.png!small?1619487629423)

如下所示可以看到对应的返回的fffffe0dd36df9e0指向了var_pmenu,之后就是后续构造的var_fakerect

![1619487655_60876ba755543718a49fb.png!small?1619487655932](https://image.3001.net/images/20210427/1619487655_60876ba755543718a49fb.png!small?1619487655932)

判断GetMenuBarInfo第三个参数idItem是否大于poi(poi(var_fakerect+028)+0x2c)，这里idItem为1，poi(poi(var_fakerect+028)+0x2c)在fakespmenu构造的时候将其设置为0x10，检测通过

![1619487665_60876bb1a70f080f02e68.png!small?1619487666002](https://image.3001.net/images/20210427/1619487665_60876bb1a70f080f02e68.png!small?1619487666002)

之后获取var_fakeract偏移0的内容，并保存到返回的pmbi+0x18

![1619487673_60876bb9275c91b3ba32d.png!small?1619487673449](https://image.3001.net/images/20210427/1619487673_60876bb9275c91b3ba32d.png!small?1619487673449)

依次检测var_fakeract偏移0x40，0x44处是否为0，这里利用代码在构造fakespmenu时也依次将这两个值域进行了设置。

![1619487679_60876bbf2f5ab208e8d79.png!small?1619487679629](https://image.3001.net/images/20210427/1619487679_60876bbf2f5ab208e8d79.png!small?1619487679629)

之后再此判断窗口偏移0x1a处的数据，并进入最终的坐标计算逻辑。

![1619487685_60876bc589048e2f41e9c.png!small?1619487685897](https://image.3001.net/images/20210427/1619487685_60876bc589048e2f41e9c.png!small?1619487685897)

获取poi(poi(var_fakerect+0x58))处的var_OffsetrcBarleft，即下图中000002804f910150

![1619487692_60876bccd505950c30904.png!small?1619487693143](https://image.3001.net/images/20210427/1619487692_60876bccd505950c30904.png!small?1619487693143)

可以看到此时第一次的var_OffsetrcBarleft保存指针指向的数据是通过攻击者手动构造的

![1619487703_60876bd764ef7fd27f151.png!small?1619487703801](https://image.3001.net/images/20210427/1619487703_60876bd764ef7fd27f151.png!small?1619487703801)

之后依次计算返回pmbi.rcBar的left; top; right; bottom;

Left=poi(var_OffsetrcBarleft+0x40)+ poi(poi(tagWND1+0x28)+0x58)，即0x40+0=0

![1619487708_60876bdccf2757b45e5ef.png!small?1619487709179](https://image.3001.net/images/20210427/1619487708_60876bdccf2757b45e5ef.png!small?1619487709179)

写入到left字段

![1619487721_60876be9ea9d3ebfdd92a.png!small?1619487722256](https://image.3001.net/images/20210427/1619487721_60876be9ea9d3ebfdd92a.png!small?1619487722256)

Right=left+ poi(var_OffsetrcBarleft+0x48) = 0x40+0x44 = 0x88

![1619487726_60876beea3616cc11e701.png!small?1619487727098](https://image.3001.net/images/20210427/1619487726_60876beea3616cc11e701.png!small?1619487727098)

0x88写入right字段

![1619487731_60876bf3a79ee48aa13b3.png!small?1619487732030](https://image.3001.net/images/20210427/1619487731_60876bf3a79ee48aa13b3.png!small?1619487732030)

top=poi(var_OffsetrcBarleft+0x44)+ poi(poi(tagWND1+0x28)+0x5c)，即0x44+0=0x44

![1619487738_60876bfa16d7431552ebf.png!small?1619487738383](https://image.3001.net/images/20210427/1619487738_60876bfa16d7431552ebf.png!small?1619487738383)

写入到top字段

![1619487742_60876bfe685fd2103233e.png!small?1619487742705](https://image.3001.net/images/20210427/1619487742_60876bfe685fd2103233e.png!small?1619487742705)

Bottom = top + poi(var_OffsetrcBarleft+0x4c) =0x44+0x4c =0x90。

![1619487747_60876c03a79de2368cc45.png!small?1619487747967](https://image.3001.net/images/20210427/1619487747_60876c03a79de2368cc45.png!small?1619487747967)

写入button字段

![1619487754_60876c0a65e7eccf2a3d1.png!small?1619487754789](https://image.3001.net/images/20210427/1619487754_60876c0a65e7eccf2a3d1.png!small?1619487754789)

可以看到如下所示中，pmbi.rcBar返回的矩形实际上是通过poi(var_OffsetrcBarleft)+0x40处0x10长度的内存数据（0x40的偏移由idItem=1决定，如果等于2应该为0x40+0x60=0xa0，所以利用中默认都通过idItem=1调用GetMenuBarInfo）配合窗口内核对象的pwnd+0x58/0x5c两个字段生成，由于这里pwnd+0x58/0x5c默认为0，因此直接依赖于poi(var_OffsetrcBarleft)+0x40处的0x10内存数据，而根据公式可以发现，pwnd+0x58/0x5c为0的情况下，left，top数据实际上就是poi(var_OffsetrcBarleft)+0x40/
poi(var_OffsetrcBarleft)+0x44这连续8个字节的内容，由于poi(var_OffsetrcBarleft)指向内容为攻击者可控，只需将其值设置为des-0x40（0x40的偏移根据idItem而不同），即可实现对des地址数据的读取。

![1619487759_60876c0fe376e6c256590.png!small?1619487760245](https://image.3001.net/images/20210427/1619487759_60876c0fe376e6c256590.png!small?1619487760245)

内核返回的pmbi

![1619487765_60876c15e7e2d54089e1f.png!small?1619487766343](https://image.3001.net/images/20210427/1619487765_60876c15e7e2d54089e1f.png!small?1619487766343)

第一次读取返回的pmbi值

![1619487771_60876c1b28906b72bd149.png!small?1619487771712](https://image.3001.net/images/20210427/1619487771_60876c1b28906b72bd149.png!small?1619487771712)

第一次读取测试成功后返回的left正好就是var_OffsetrcBarleft的偏移

![1619487776_60876c2049d051d32fc78.png!small?1619487776515](https://image.3001.net/images/20210427/1619487776_60876c2049d051d32fc78.png!small?1619487776515)

这也就是为什么第一次调用时var_OffsetrcBarleft指向内存如此构造的原因，实际上每一个4字节内存都是一个偏移，Left=poi(var_OffsetrcBarleft+0x40)+
poi(poi(tagWND1+0x28)+0x58), poi(poi(tagWND1+0x28)+0x58)=0,因此left中一定返回的是对应的偏移。

![1619487780_60876c24e81c0302115f7.png!small?1619487781363](https://image.3001.net/images/20210427/1619487780_60876c24e81c0302115f7.png!small?1619487781363)

进入第二次调用将目标读取地址减去pmbi.rcBar.left中返回的偏移值ffffff0680828050-0x40

= ffffff0680828010

![1619487786_60876c2a4565d2f62956a.png!small?1619487786529](https://image.3001.net/images/20210427/1619487786_60876c2a4565d2f62956a.png!small?1619487786529)

此时更新过var_OffsetrcBarleft值后整体的fakespmenu内存如下所示var_OffsetrcBarleft指向了目标读取地址-0x40的位置。

![1619487791_60876c2f338eb8129db5d.png!small?1619487791657](https://image.3001.net/images/20210427/1619487791_60876c2f338eb8129db5d.png!small?1619487791657)

内核进入xxxGetMenuBarInfo

![1619487797_60876c3501f6b1925022c.png!small?1619487797329](https://image.3001.net/images/20210427/1619487797_60876c3501f6b1925022c.png!small?1619487797329)

检验对应窗口的dwStely

![1619487802_60876c3a2dd8cd5262096.png!small?1619487802483](https://image.3001.net/images/20210427/1619487802_60876c3a2dd8cd5262096.png!small?1619487802483)

映射对应的fakespmenu内存

![1619487808_60876c4002433152e20f2.png!small?1619487808449](https://image.3001.net/images/20210427/1619487808_60876c4002433152e20f2.png!small?1619487808449)

如下所示left读取此时获取了目标地址指向内容的低四位。

Left=poi(var_OffsetrcBarleft+0x40)+ poi(poi(tagWND1+0x28)+0x58)=
0x8385a690+0=0x8385a690

![1619487816_60876c48194de2ab6f029.png!small?1619487816535](https://image.3001.net/images/20210427/1619487816_60876c48194de2ab6f029.png!small?1619487816535)

将目标地址保存的第四位内容保存到left中

![1619487824_60876c50110a0e464fa07.png!small?1619487826628](https://image.3001.net/images/20210427/1619487824_60876c50110a0e464fa07.png!small?1619487826628)

获取对应的right，Right=left+ poi(var_OffsetrcBarleft+0x48) = 0x8385a690+0=
0x8385a690

![1619487838_60876c5ed29e184034349.png!small?1619487839240](https://image.3001.net/images/20210427/1619487838_60876c5ed29e184034349.png!small?1619487839240)

写入到right字段

![1619487846_60876c6663030538ec737.png!small?1619487846715](https://image.3001.net/images/20210427/1619487846_60876c6663030538ec737.png!small?1619487846715)

top=poi(var_OffsetrcBarleft+0x44)+ poi(poi(tagWND1+0x28)+0x5c) = 0xffffff06+0
= 0xffffff06，正好是目标读取地址的高四字节。

![1619487852_60876c6cad2063bd681a1.png!small?1619487853053](https://image.3001.net/images/20210427/1619487852_60876c6cad2063bd681a1.png!small?1619487853053)

写入到top字段

![1619487857_60876c716f330b6e57558.png!small?1619487857830](https://image.3001.net/images/20210427/1619487857_60876c716f330b6e57558.png!small?1619487857830)

Bottom = top + poi(var_OffsetrcBarleft+0x4c) =0xffffff06+0 =0xffffff06。

![1619487863_60876c774b32d31ad2403.png!small?1619487863799](https://image.3001.net/images/20210427/1619487863_60876c774b32d31ad2403.png!small?1619487863799)

写入到bottom字段

![1619487869_60876c7d232ed0a7bafeb.png!small?1619487869532](https://image.3001.net/images/20210427/1619487869_60876c7d232ed0a7bafeb.png!small?1619487869532)

此时返回后对应pmbi.rcBar

![1619487874_60876c82114cf493b1fae.png!small?1619487874388](https://image.3001.net/images/20210427/1619487874_60876c82114cf493b1fae.png!small?1619487874388)

通过left+top即可获取对应的目标地址内容。

![1619487879_60876c87e90719c34b8ea.png!small?1619487880236](https://image.3001.net/images/20210427/1619487879_60876c87e90719c34b8ea.png!small?1619487880236)

之后如下所示依次读取对应的EPROCESS及内核基址

![1619487884_60876c8cd1f014096d25b.png!small?1619487885247](https://image.3001.net/images/20210427/1619487884_60876c8cd1f014096d25b.png!small?1619487885247)

如下方式读取对应的内核基址

![1619487895_60876c973ae500b795c0c.png!small?1619487895756](https://image.3001.net/images/20210427/1619487895_60876c973ae500b795c0c.png!small?1619487895756)

如下方式读取EPROCESS

![1619487901_60876c9d5f29c50f8dea7.png!small?1619487901739](https://image.3001.net/images/20210427/1619487901_60876c9d5f29c50f8dea7.png!small?1619487901739)

通过EPROCESS获取系统token及当前进程token地址，并通过函数fun_Write进行写入

![1619487906_60876ca284a021ff59b00.png!small?1619487906926](https://image.3001.net/images/20210427/1619487906_60876ca284a021ff59b00.png!small?1619487906926)

fun_write借助窗口0 var_normalClasshwnd0，窗口1 var_normalClasshwnd1实现任意地址写入，其本质是通过窗口0
var_normalClasshwnd0的越界写入能力，调用SetWindowLongPtrA修改窗口1
var_normalClasshwnd1的扩展内存地址pExtraBytes来实现任意地址写。

![1619487912_60876ca83dbac1c66c549.png!small?1619487912561](https://image.3001.net/images/20210427/1619487912_60876ca83dbac1c66c549.png!small?1619487912561)

窗口0通过越界写 调用SetWindowLongPtrA修改窗口1的pExtraBytes为目标写入地址

![1619487931_60876cbba0215722c1ee8.png!small?1619487931945](https://image.3001.net/images/20210427/1619487931_60876cbba0215722c1ee8.png!small?1619487931945)

首先计算对应的窗口0内核对象到窗口1内核对象的pwnd. pExtraBytes的内核偏移。

![1619487936_60876cc047b997c15e130.png!small?1619487936608](https://image.3001.net/images/20210427/1619487936_60876cc047b997c15e130.png!small?1619487936608)

内核进入xxxSetWindowLongPtr

![1619487941_60876cc5f0bf88fb61e43.png!small?1619487942334](https://image.3001.net/images/20210427/1619487941_60876cc5f0bf88fb61e43.png!small?1619487942334)

函数返回后窗口1内核对象的pwnd. pExtraBytes,已经被设置为当前进程的token地址。

![1619487947_60876ccbe11e1fcc68cdf.png!small?1619487948524](https://image.3001.net/images/20210427/1619487947_60876ccbe11e1fcc68cdf.png!small?1619487948524)

此时通过窗口1直接调用xxxSetWindowLongPtr，并将参数index设置为0，将直接完成对当前pExtraBytes（当前进程token）地址的写入操作

![1619487956_60876cd45959f77d5c57f.png!small?1619487956722](https://image.3001.net/images/20210427/1619487956_60876cd45959f77d5c57f.png!small?1619487956722)

进入内核

![1619487961_60876cd9183ff0c9b4978.png!small?1619487961433](https://image.3001.net/images/20210427/1619487961_60876cd9183ff0c9b4978.png!small?1619487961433)

这里不小心步过了，重新调了下，如下所示为fun_write

![1619487973_60876ce5864545192b7fa.png!small?1619487973790](https://image.3001.net/images/20210427/1619487973_60876ce5864545192b7fa.png!small?1619487973790)

窗口1调用xxxSetWindowLongPtr完成对当前进程token的写入替换

![1619487989_60876cf5645ceb85463be.png!small?1619487989698](https://image.3001.net/images/20210427/1619487989_60876cf5645ceb85463be.png!small?1619487989698)

进入内核xxxSetWindowLongPtr

![1619487994_60876cfa9cba8f6fa447e.png!small?1619487994944](https://image.3001.net/images/20210427/1619487994_60876cfa9cba8f6fa447e.png!small?1619487994944)

窗口1内核对象的pwnd. pExtraBytes指向了当前进程的token地址，这里是pointer的扩展内存寻址方式。

![1619488000_60876d00a1bb0ce0bd6be.png!small?1619488001039](https://image.3001.net/images/20210427/1619488000_60876d00a1bb0ce0bd6be.png!small?1619488001039)

判断具体的拓展内存寻址flag

![1619488008_60876d08c84f515541cf2.png!small?1619488009134](https://image.3001.net/images/20210427/1619488008_60876d08c84f515541cf2.png!small?1619488009134)

计算目标地址，由于index为0，因此目标地址直接是pExtraBytes指向的当前进程token的地址。

![1619488015_60876d0f83003e40ec237.png!small?1619488015791](https://image.3001.net/images/20210427/1619488015_60876d0f83003e40ec237.png!small?1619488015791)

完成写入，提权完毕。

![1619488021_60876d155f2923df00ed2.png!small?1619488021693](https://image.3001.net/images/20210427/1619488021_60876d155f2923df00ed2.png!small?1619488021693)

## 参考链接

https://sandbox.ti.qianxin.com/sandbox/page

https://ti.dbappsecurity.com.cn/blog/index.php/2021/02/10/windows-kernel-zero-day-exploit-is-used-by-bitter-apt-in-targeted-attack-cn/

https://bbs.pediy.com/thread-251220.htm

https://bbs.pediy.com/thread-225296.htm

http://www.netfairy.net/?post=239

http://undocumented.ntinternals.net/index.html?page=UserMode%2FUndocumented%20Functions%2FAPC%2FNtCallbackReturn.html

http://cvr-data.blogspot.com/2016/11/lpe-vulnerabilities-exploitation-on.html

https://www.anquanke.com/post/id/184233

https://blog.csdn.net/qq_18218335/article/details/78324320

https://bbs.pediy.com/thread-104918.htm

https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getmenubarinfo

