​Hook也就是钩子，在Windows中大部分的应用程序都是基于消息机制，会根据不同的消息使用消息过程函数完成不同的功能。而钩子是一种消息处理机制，它可以比你的应用程序先获得消息，可以用来截获、监视系统的消息，改变执行流程实现特定的功能。对于全局钩子来说，它会影响所有应用程序，所以钩子函数必须在DLL中实现。  

 **本文由锦行科技的安全研究团队提供，旨在帮助大家深入了解全局钩子的应用。**

 **1** **函数介绍  
**

#####  **SetWindowsHookEx**

 **作用：**  
将程序定义的钩子函数安装到挂钩链中，安装钩子的程序可以监视系统是否存在某些类型的时间，这些事件与特定线程或调用线程所在的桌面中的所有线程相关联。

 **函数声明：  
**

    
    
    HHOOK WINAPI SetWindowsHookEx（  
    _In_ int        idHook,  
    _In_ HOOKPROC     lpfn,  
    _In_ HINSTANCE    hMod,  
    _In_ DWORD        dwThreadId  
    ）

 **参数：  
** idHook:  
安装的钩子程序的类型，具体值参考官方手册

lpfn：  
指向钩子程序过程的指针，若参数dwThreadId为0或者指示了一个其他进程创建的线程之标识符，则参数lpfn必须指向一个动态链接中的挂钩处理过程。否则，参数lpfn可以指向一个与当前进程相关的代码中定义的挂钩处理过程。

hMod：  
包含由lpfn参数指向的钩子过程的DLL句柄。

dwThreadId：  
与钩子程序关联的线程标识符，如果为0，则钩子过程与系统中所有线程相关联。

 **返回值：**  
成功：返回钩子过程句柄  
失败：返回NULL

#####  **UnhookWindowsHookEx**

 **作用：**  
卸载钩子  
 **函数声明：**

    
    
    BOOL WINAPI UnsetGlobalHook（  
    _In_ HHOOK hhk  
    ）

 **参数：**  
hhk:  
卸载的钩子句柄

 **2** **实例代码  
**

使用IDE：VS2019  
创建一个DLL项目

pch.h:

    
    
    #include "framework.h"  
    extern "C" _declspec(dllexport) int SetGlobalHook();  
    extern "C" _declspec(dllexport) LRESULT GetMsgProc(int code, WPARAM wParam, LPARAM lParam);  
    extern "C" _declspec(dllexport) BOOL UnsetGlobalHook();  
    #endif //PCH_H

dllmain.cpp

    
    
    HMODULE g_hDllModule = NULL;  
      
    BOOL APIENTRY DllMain( HMODULE hModule,  
    DWORD  ul_reason_for_call,  
    LPVOID lpReserved  
    )  
    {  
    switch (ul_reason_for_call)  
    {  
    case DLL_PROCESS_ATTACH: {  
    g_hDllModule = hModule;  
    break;  
    }  
    case DLL_THREAD_ATTACH:  
    case DLL_THREAD_DETACH:  
    case DLL_PROCESS_DETACH:  
    break;  
    }  
    return TRUE;  
    }

钩子过程：

 **SetGlobalHook()** : 设置全局钩子，WH_GETMESSAGE为监视发送到消息队列的消息的钩子，第二个参数则为钩子的回调函数。

 **GetMsgProc()**
：钩子的回调函数，CallNextHookEx表示将当前钩子传递给下一个钩子，若返回值为0，表示中断钩子传递，对钩子进行拦截。

 **UnsetGlobalHook()** ：卸载钩子

 **共享内存**
：由于全局钩子是以DLL形式加载到进程中，进程都是独立的，要将进程句柄传递给其他进程，可以使用共享内存突破进程独立性，使用"/SECTION:mydata,RWS"设置为可读可写可共享的数据段。

pch.cpp:

    
    
    #include "pch.h"  
    #include <windows.h>  
    #include <stdio.h>  
    extern HMODULE g_hDllModule;  
    // 共享内存  
    #pragma data_seg("mydata")  
    HHOOK g_hHook = NULL;  
    #pragma data_seg()  
    #pragma comment(linker, "/SECTION:mydata,RWS")  
    //钩子回调函数  
    LRESULT GetMsgProc(int code, WPARAM wParam, LPARAM lParam){  
    return ::CallNextHookEx(g_hHook, code, wParam, lParam);  
    }  
      
    // 设置钩子  
    BOOL SetGlobalHook() {  
    g_hHook = SetWindowsHookEx(WH_GETMESSAGE, (HOOKPROC)GetMsgProc, g_hDllModule, 0);  
    if (NULL == g_hHook) {  
    return FALSE;  
    }  
    return TRUE;  
    }  
      
    // 卸载钩子  
    BOOL UnsetGlobalHook() {  
    if (g_hHook) {  
    UnhookWindowsHookEx(g_hHook);  
    }  
    return TRUE;  
    }

![](https://image.3001.net/images/20210907/1631008639_6137377f7e8e6941c526f.png!small)最终生成Dll1.dll

创建c++空项目  
编译下面代码，将Dll1.dll放在生成的exe下，运行

hook.cpp:

    
    
    #include <windows.h>  
    #include <stdio.h>  
      
    typedef BOOL(*PEN_HOOKSTART)();  
    typedef BOOL(*PEN_HOOKSTOP)();  
      
    int main() {  
    //加载dll  
    HMODULE hDll = LoadLibrary(L"./Dll1.dll");  
      
    if (NULL == hDll)  
    {  
    printf("LoadLibrary Error[%d]\n", ::GetLastError());  
    return 1;  
    }  
      
    BOOL isHook = FALSE;  
      
    //导出函数地址  
    PEN_HOOKSTART SetGlobalHook = (PEN_HOOKSTART)GetProcAddress(hDll, "SetGlobalHook");  
      
    if (NULL == SetGlobalHook)  
    {  
    printf("SetGlobalHook:GetProcAddress Error[%d]\n", GetLastError());  
    return 2;  
    }  
      
    PEN_HOOKSTOP UnsetGlobalHook = (PEN_HOOKSTOP)GetProcAddress(hDll, "UnsetGlobalHook");  
      
    if (NULL == UnsetGlobalHook)  
    {  
    printf("UnsetGlobalHook:GetProcAddress Error[%d]\n", GetLastError());  
    return 3;  
    }  
      
    isHook=SetGlobalHook();  
      
    if (isHook) {  
    printf("Hook is ok!\n");  
    }  
    else {  
    printf("Hook is error[%d]\n", GetLastError());  
    }  
      
    system("pause");  
      
    UnsetGlobalHook();  
      
    FreeLibrary(hDll);  
      
    return 0;  
    }

![](https://image.3001.net/images/20210907/1631008654_6137378e902178fe79d8d.png!small)

 **3** **查看效果  
**

使用Process
Explorer查看dll：![1631008700_613737bc33af8782edc5d.png!small](https://image.3001.net/images/20210907/1631008700_613737bc33af8782edc5d.png!small)

可以看到已经注入了Dll1.dll

