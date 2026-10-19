在edr或者其他类型的安全软件我们通常要监测当前系统的内核驱动的加载，通常使用的方法是PsSetLoadImageNotifyRoutine设置模块加载回调例程来监控ring3模块以及ring0模块的加载，回调函数
eLoadImageNotifyRoutine 的第二个参数判断，如果 PID是0 ，则表示加载驱动，如果PID非零，则表示加载DLL。此方法的优点是：

>  **更底层**
>
>  **方法简单通用**

缺点当然也就是函数太底层，第二就是方法太通用几乎做过进程、线程监控的搞安全内核开发的人基本都晓得，也很容易被发现，而且也会被摘链，而失效。

本篇文章将会探索一种新方法去监测并且控制内核模块的加载。首先我们要讲解内核加载驱动的过程。

写一个demo的驱动，然后使用VMware双机调试来调试驱动。(VMware双机调试的方法如果不会可以baidu)

![1604329148_5fa01ebce1c6d9c8cd99e.png!small](https://image.3001.net/images/20201102/1604329148_5fa01ebce1c6d9c8cd99e.png!small)

连接被调试虚拟机后，在windbg里输入sxe ld demo驱动的名字.sys

![1604329175_5fa01ed717c42dab4c03f.png!small](https://image.3001.net/images/20201102/1604329175_5fa01ed717c42dab4c03f.png!small)

然后go，如果加载系统要加载这个驱动windbg会自动停下来。

![1604329218_5fa01f027572bdeaa0008.png!small](https://image.3001.net/images/20201102/1604329218_5fa01f027572bdeaa0008.png!small)

然后输入kb

![1604329230_5fa01f0e269703b306a59.png!small](https://image.3001.net/images/20201102/1604329230_5fa01f0e269703b306a59.png!small)

可以看到内核里加载的时候会开启一个单独的线程去加载驱动

    
    
    # RetAddr           : Args to Child                                                           : Call Site
    
    00 fffff800`04b1748d : fffff880`0456b8a0 fffff880`031ac0d0 00000000`00000001 fffff800`04b74dfe : nt!DebugService2+0x5
    
    01 fffff800`04b74ecb : fffff880`031ac000 fffffa80`016de070 fffff880`0456b9b8 00000000`00000007 : nt!DbgLoadImageSymbols+0x4d
    
    02 fffff800`04e47bfd : fffffa80`00eeee20 fffff8a0`0000001c fffff800`04d84a30 fffff880`0456b888 : nt!DbgLoadImageSymbolsUnicode+0x2b
    
    03 fffff800`04e6286b : fffff880`031ac000 fffff880`0456b8f8 00000000`00000000 fffff880`0456b8d8 : nt!MiDriverLoadSucceeded+0x2bd
    
    04 fffff800`04e64ebd : fffff880`0456b9b8 00000000`00000000 00000000`00000000 00000000`00000000 : nt!MmLoadSystemImage+0x80b
    
    05 fffff800`04e65875 : 00000000`00000001 00000000`00000000 00000000`00000000 fffffa80`0231c1e0 : nt!IopLoadDriver+0x44d
    
    06 fffff800`04a8b161 : fffff800`00000000 ffffffff`8000077c fffff800`04e65820 fffffa80`006db040 : nt!IopLoadUnloadDriver+0x55
    
    07 fffff800`04d21166 : 00000000`00000000 fffffa80`006db040 00000000`00000080 fffffa80`006b71d0 : nt!ExpWorkerThread+0x111
    
    08 fffff800`04a5c486 : fffff800`04bf6e80 fffffa80`006db040 fffffa80`006da680 00000000`00000000 : nt!PspSystemThreadStartup+0x5a
    
    09 00000000`00000000 : fffff880`0456c000 fffff880`04566000 fffff880`0456ae60 00000000`00000000 : nt!KiStartSystemThread+0x16

这是调试的时候被断点断下来的堆栈，我们需要回到加载驱动的地方，所以要打开源代码，在驱动的入口点DriverEntry按F9设置断点。

![1604329309_5fa01f5de4f41c8cf02cf.png!small](https://image.3001.net/images/20201102/1604329309_5fa01f5de4f41c8cf02cf.png!small)

然后f5继续执行，之后就会停在驱动的入口点

![1604329328_5fa01f70d400b71c4e71b.png!small](https://image.3001.net/images/20201102/1604329328_5fa01f70d400b71c4e71b.png!small)

紫红色表示已经运行到断点位置。

当我们使用!process 命令时会看到当前上下文是system

![1604329364_5fa01f94016b969369917.png!small](https://image.3001.net/images/20201102/1604329364_5fa01f94016b969369917.png!small)

再次使用kb可以发现现在执行到入口点的栈的上下文是

![1604329381_5fa01fa54f61d21ff8f07.png!small](https://image.3001.net/images/20201102/1604329381_5fa01fa54f61d21ff8f07.png!small)

01 fffff880`0456b960 fffff800`04e65875 nt!IopLoadDriver+0xa07

02 fffff880`0456bc30 fffff800`04a8b161 nt!IopLoadUnloadDriver+0x55

03 fffff880`0456bc70 fffff800`04d21166 nt!ExpWorkerThread+0x111

04 fffff880`0456bd00 fffff800`04a5c486 nt!PspSystemThreadStartup+0x5a

05 fffff880`0456bd40 00000000`00000000 nt!KiStartSystemThread+0x16

可以发现在 nt!IopLoadDriver+0xa07的位置是执行入口点

使用U命令，可以查看汇编代码

fffff800`04e6546e 488bd6 mov rdx,rsi

fffff800`04e65471 488bcb mov rcx,rbx

fffff800`04e65474 ff5358 call qword ptr [rbx+58h]

fffff800`04e65477 4c8b15627bdaff mov r10,qword ptr [nt!PnpEtwHandle
(fffff800`04c0cfe0)]

fffff800`04e6547e 8bf8 mov edi,eax

call qword ptr [rbx+58h]这句代码就是执行被加载驱动的模块入口点函数

看汇编代码第一个参数rcx就是rbx,大致我们可以明确的就是rbx就是DriverEntry的DRIVER_OBJECT参数，所以就有了rbx+58h就是DRIVER_OBJECT的DriverInit，为了印证我们的猜测，在IDA下看rbx就是DRIVER_OBJECT的结构体，而这里的call执行的就是DriverInit

![1604329436_5fa01fdcb851fda695f95.png!small](https://image.3001.net/images/20201102/1604329436_5fa01fdcb851fda695f95.png!small)

Call v29->DriverInit(v29, v32);

有了这样的过程，我们是不是就可以探索新的方法去控制驱动的加载呢？答案是肯定的。查看IDA，可以发现在执行驱动入口点之前这个过程内核会处理很多东西，比如分配内存啊，创建驱动的内核对象啊，驱动的权限的判断，创建内核镜像啊等等操作，凡是可以控制的地方我们都可以研究下，今天我们主要研究是内核Object这个东西，众所周知windows内部管理着很多的Object，windows专门有个内核对象管理器，我们通常说的文件、进程、线程、管道、油槽、内核Image等等都属于Object,windows在使用额时候总是会先CreateObject
然后在插入这个Object到object管理器中，成功了才会继续执行，所以在加载内核模块镜像的时候也一定会创建一个Object，然后在插入这个对象。

因为DRIVER_OBEJCT就是一个Object，我们可以通过追踪DRIVER_OBEJCT的生成来劫持控制驱动的加载。

查看IDA分析过程，对IopLoadDriver的函数分析可以发现，在调用入口点之上确实有个ObInsertObject的函数，而且该函数插入的就是DERIVER_OBJECT对象

![1604329456_5fa01ff03365f4e5d159b.png!small](https://image.3001.net/images/20201102/1604329456_5fa01ff03365f4e5d159b.png!small)

v10 = ObInsertObject(v21, 0i64, 1u, 0, 0i64, &Handle);

有了这个函数我们就可以控制对象了，怎么控制呢？答案很简单，对象的回调函数。

 **ObInsertObject** 的函数内部是会经过每种对象类型对象的回调函数设置的。

下面分析怎么到达过滤回调callback的

在ObInsertObject内部会先调用 **ObInsertObjectEx** 函数

![1604329520_5fa02030cb12cdff89902.png!small](https://image.3001.net/images/20201102/1604329520_5fa02030cb12cdff89902.png!small)

在 **ObInsertObjectEx** 内部会调用 **ObpCreateHandle**

![1604329540_5fa02044eac44964cc1e5.png!small](https://image.3001.net/images/20201102/1604329540_5fa02044eac44964cc1e5.png!small)

此时的第一个参数是0，而在 **ObpCreateHandle** 函数内部会调用

v51 = **ObpPreInterceptHandleCreate** (Objecta, Attributes, &v70,
&ThreadCallbackListHead);

![1604329568_5fa020608652f827c5309.png!small](https://image.3001.net/images/20201102/1604329568_5fa020608652f827c5309.png!small)

 **ObpPreInterceptHandleCreate** 函数就是我之前说的在调用当前对象类型的callback函数。

![1604329583_5fa0206fea26c00bc0fa2.png!small](https://image.3001.net/images/20201102/1604329583_5fa0206fea26c00bc0fa2.png!small)

所以调用路径是

![1604329592_5fa02078aa43aaff9a188.png!small](https://image.3001.net/images/20201102/1604329592_5fa02078aa43aaff9a188.png!small)

有 **ObInsertObject** 就一定会有 **ObCreateObject** 这个函数，往上继续翻阅就会看到

![1604329612_5fa0208ca0027cccb5b31.png!small](https://image.3001.net/images/20201102/1604329612_5fa0208ca0027cccb5b31.png!small)

v10 = ObCreateObject(

KeGetCurrentThread()->PreviousMode,

IoDriverObjectType,

&ObjectAttributes,

0,

0i64,

0x188u,

0,

0,

&v74),

创建的是 **IoDriverObjectType** 这种类型的对象，理论上是可以在代码上对 **IoDriverObjectType**
注册callback，而且这个对象微软是可以外部直接链接的，不需要使用搜索的方法去寻找这个对象类型，下面就是检验理论猜想。

在之前的demo实例在加上一段代码注册回调

    
    
    Globals.ob_operation_registrations.ObjectType = IoDriverObjectType;
    
    Globals.ob_operation_registrations.Operations |= OB_OPERATION_HANDLE_CREATE;
    
    Globals.ob_operation_registrations.Operations |= OB_OPERATION_HANDLE_DUPLICATE;
    
    Globals.ob_operation_registrations.PreOperation = CBTdPreOperationCallback;
    
    Globals.ob_operation_registrations.PostOperation = CBTdPostOperationCallback;
    
    Globals.ob_registration.Version                    = ObGetFilterVersion();
    
    Globals.ob_registration.OperationRegistrationCount = 1;
    
    //CBObRegistration.Altitude                   = CBAltitude;
    
    
    
    
    Globals.ob_registration.RegistrationContext        = NULL;
    
    Globals.ob_registration.OperationRegistration      = &(Globals.ob_operation_registrations);
    
    
    
    
    Status = ObRegisterCallbacks (
    
    &(Globals.ob_registration),
    
    &(Globals.registration_handle)       // save the registration handle to remove callbacks later
    
    );
    
    if ( NT_SUCCESS(Status))
    
    {
    
    Globals.ob_protect_installed = TRUE;
    
    }

然后继续使用双机调试，在入口点下断点

![1604329658_5fa020ba7b66817d50998.png!small](https://image.3001.net/images/20201102/1604329658_5fa020ba7b66817d50998.png!small)

进入断点后，继续单步F10，执行过注册后status返回0表示注册成功

![1604329704_5fa020e81a3bc7503f0f7.png!small](https://image.3001.net/images/20201102/1604329704_5fa020e81a3bc7503f0f7.png!small)

显示驱动启动成功

![1604329721_5fa020f953373b3573667.png!small](https://image.3001.net/images/20201102/1604329721_5fa020f953373b3573667.png!small)

在我们设置的回调函数的地方下断点，看看加载驱动的时候是否会进入回调

在虚拟机里安装sysmon这个软件，他是会加载一个文件驱动的。

![1604329733_5fa02105a14c254cb8e7c.png!small](https://image.3001.net/images/20201102/1604329733_5fa02105a14c254cb8e7c.png!small)

成功断下来了

![1604329744_5fa02110e7031b6c957eb.png!small](https://image.3001.net/images/20201102/1604329744_5fa02110e7031b6c957eb.png!small)

查看PreInfo->Object

使用dt nt!_DRIVER_OBJECT PreInfo->Object

![1604329761_5fa021211334c0fc0384a.png!small](https://image.3001.net/images/20201102/1604329761_5fa021211334c0fc0384a.png!small)

确实是sysmon的驱动sysmonDrv,他的入口点是sysmonDrv+1e058

看来这个方法确实有效，接下来我们要把driver_init设置为0，尝试修改

Eq xxxxxxx 0 修改成0

![1604329771_5fa0212b372c76b221574.png!small](https://image.3001.net/images/20201102/1604329771_5fa0212b372c76b221574.png!small)

接下来直接f5

成功蓝屏

![1604329780_5fa02134d25031452acd6.png!small](https://image.3001.net/images/20201102/1604329780_5fa02134d25031452acd6.png!small)

因为我们把入口点设置为0，所以一到执行入口点就蓝屏，说明我们可以从代码上控制驱动加载。Kb后显示堆栈，驱动执行路径

![1604329792_5fa0214027930c4eefd29.png!small](https://image.3001.net/images/20201102/1604329792_5fa0214027930c4eefd29.png!small)

    
    
    # RetAddr           : Args to Child                                                           : Call Site
    
    00 fffff800`042b3477 : fffffa80`029c81c0 fffffa80`029c81c0 00000000`00000000 00000000`000007ff : 0x0
    
    01 fffff800`042b3875 : 00000000`00000001 00000000`00000000 00000000`00000000 fffffa80`029c82f8 : nt!IopLoadDriver+0xa07
    
    02 fffff800`03ed9161 : fffff8a0`00000000 ffffffff`80000f54 fffff800`042b3820 fffffa80`00711680 : nt!IopLoadUnloadDriver+0x55
    
    03 fffff800`0416f166 : 00000000`00000000 fffffa80`00711680 00000000`00000080 fffffa80`006ed1d0 : nt!ExpWorkerThread+0x111
    
    04 fffff800`03eaa486 : fffff800`04044e80 fffffa80`00711680 fffffa80`00711b60 00000000`00000000 : nt!PspSystemThreadStartup+0x5a
    
    05 00000000`00000000 : fffff880`0457a000 fffff880`04574000 fffff880`04578590 00000000`00000000 : nt!KiStartSystemThread+0x16

也就是call 0 ，我们设置的驱动入口下面我就方便修改demo驱动代码去控制驱动的加载了入口点。

在CBTdPreOperationCallback的函数里加一个修改DriverInit的数值，然后赋值为我们自定义的FakeDriverEntry函数

![1604329808_5fa02150c94314672494e.png!small](https://image.3001.net/images/20201102/1604329808_5fa02150c94314672494e.png!small)![1604329808_5fa02150c94314672494e.png!small](https://image.3001.net/images/20201102/1604329808_5fa02150c94314672494e.png!small)

![1604329825_5fa021613558f4a84e946.png!small](https://image.3001.net/images/20201102/1604329825_5fa021613558f4a84e946.png!small)实现FakeDriverEntry函数如下：

![1604329836_5fa0216cf304c3f134fe7.png!small](https://image.3001.net/images/20201102/1604329836_5fa0216cf304c3f134fe7.png!small)

下面再次开启双机调试，同样在虚拟机里执行sysmon –i

![1604329851_5fa0217bda1bdeaa3a3f4.png!small](https://image.3001.net/images/20201102/1604329851_5fa0217bda1bdeaa3a3f4.png!small)

![1604329863_5fa0218751c49b138d5cf.png!small](https://image.3001.net/images/20201102/1604329863_5fa0218751c49b138d5cf.png!small)

断点断在了回调函数的DRIVER_OBJECT* pDriverObj = DRIVER_OBJECT*)PreInfo->Object;

查看PDriverObj对象

![1604329882_5fa0219ab9e439b636638.png!small](https://image.3001.net/images/20201102/1604329882_5fa0219ab9e439b636638.png!small)

U 入口点的函数 **u 0xfffff880`02ac2058**

![1604329896_5fa021a80b8f3cdc97f79.png!small](https://image.3001.net/images/20201102/1604329896_5fa021a80b8f3cdc97f79.png!small)

下面单步执行后会修改sysmonDrv驱动的DriverInit入口点

同时在FakeDriverEntry下断点

![1604329906_5fa021b2f33fa48b7213c.png!small](https://image.3001.net/images/20201102/1604329906_5fa021b2f33fa48b7213c.png!small)

直接f5, 断点就直接断在了我们的Fake函数里

![1604329918_5fa021be569577f553c30.png!small](https://image.3001.net/images/20201102/1604329918_5fa021be569577f553c30.png!small)

使用kb命令查看堆栈

![1604329942_5fa021d60ad26fb7480dd.png!small](https://image.3001.net/images/20201102/1604329942_5fa021d60ad26fb7480dd.png!small)

确实执行了call，继续F5，这时我们观察sysmon命令行返回

![1604329956_5fa021e4dfd7ae522f296.png!small](https://image.3001.net/images/20201102/1604329956_5fa021e4dfd7ae522f296.png!small)

 **Sysmon installed.**

 **SysmonDrv installed.**

 **StartService failed for SysmonDrv**

 **Failed to start the driver:**

 **Stopping the service failed:**

 **Sysmon的驱动加载失败了，说明成功的控制了驱动的加载，从而证明了这种方案的可行** 。

总结，有些知识是已经众所周知的，但是更多的新的方法是需要我们在这些知识点反复研究反复揣摩，反复猜想，然后加以论证，才能获得意想不到额结果，当然今天这个注册回调不是随便就可以注册的，需要反复逆向去修改标志位实现的hack的方法去实现注册回调，具体读者自行研究，我这里只提供方法可行性。

