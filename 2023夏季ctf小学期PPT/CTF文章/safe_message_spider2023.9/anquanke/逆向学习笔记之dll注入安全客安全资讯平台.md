# 逆向学习笔记之dll注入

阅读量 **282556**

|评论 **5**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-07-14 16:30:49

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0199d2a70980828b63.png)

## 概念

DLL注入指的是向运行中的其他进程强制插入特定的DLL文件。从技术细节来说，DLL注入命令其他进程自行调用LoadLibrary()
API，加载用户指定的DLL文件。DLL注入与一般DLL加载的区别在于，加载的目标进程是自身或其他进程。

可以简单理解为把你想执行的代码写在dll文件里，然后注入目标进程执行代码。

## 具体场景

dll的应用场景有很多，比如改善功能与修复bug，消息钩取，API钩取，恶意代码等场景，这里我将dll注入用于黑盒测试，方便理解dll注入的功能。

在一些比较复杂的程序里，特别是一些进行大量代码混淆的程序里，我们静态分析往往是很困难的，动态调试多种不同输入又十分耗时耗力，这种情况下黑盒测试就成了分析函数的好办法。

这里方便理解，我编写了一个特别简单的验证输入的程序：

###  main.c：

    
    
    // clang -c main.c -o main.o
    #include <stdio.h>
    #include <stdlib.h>
    
    int check(char n);
    
    int main()
    {
        char string[10];
        int answer[4] = {1, 2, 3, 4};
        puts("plz input something:");
        scanf("%s", string);
        int i;
        int result = 0;
        for (i = 0; i < 4; i++)
        {
            if (check(string[i]) == answer[i])
            {
                continue;
            }
            else
            {
                result = 1;
                break;
            }
        }
        if (result)
        {
            puts("wrong!");
        }
        else
        {
            puts("right");
        }
        system("pause");
        return 0;
    }
    

###  check.c:

    
    
    // clang -c -mllvm -fla check.c -o check.o
    int check(char n){
        if(n=='a'){
            return 3;
        }else if(n=='b'){
            return 123;
        }else if(n=='c'){
            return 456;
        }else if(n=='d'){
            return 789;
        }else if(n=='f'){
            return 1;
        }else if(n=='l'){
            return 2;
        }else if(n=='g'){
            return 4;
        }else{
            return -1;
        }    
    }
    

###  链接生成main.exe

    
    
    clang main.o check.o -o main.exe
    

通过源码我们可以清晰的看出我们需要输入的字符串为flag，check函数依次验证字符f，l，a，g，返回1,2,3,4，与answer数组做比较后验证成功，输出right。

但是check函数进行了控制流平坦化混淆，我们用ida64打开最后生成的main.exe文件看一下。

###  主函数main：

![](https://p1.ssl.qhimg.com/t0110e86fd7c5256d46.png)

可以看到主函数逻辑还是非常清晰正确的，我们接下来跟进check函数。

###  验证函数check：

![](https://p3.ssl.qhimg.com/t0120b9ff621240e816.png)

—分割线—-
![](https://p5.ssl.qhimg.com/t0146b949d15cebb9c2.png)

check函数变得特别长，上面是我随意截的两张图，可以看到由于平坦化的处理，此时的check函数原本的验证字符功能已经很难分析出来，但是我们通过check函数的参数和返回值猜测这就是一个验证字符的函数。

![](https://p3.ssl.qhimg.com/t016e14a449026dc4e1.jpg)

至于具体的功能我们就需要进行黑盒测试，也就是通过dll注入来搞清楚了。

## dll注入

跟exe有个main或者WinMain入口函数一样，DLL也有一个入口函数，就是DllMain。当使用LoadLibrary函数加载DLL时，系统会调用DLL的入口点函数。

函数定义如下：

    
    
    BOOL WINAPI DllMain(
      _In_ HINSTANCE hinstDLL, // 指向自身的句柄
      _In_ DWORD fdwReason, // 调用原因
      _In_ LPVOID lpvReserved // 隐式加载和显式加载
    );
    

接下来我们编写要注入的dll。

###  inject.c:

    
    
    #include "pch.h"
    #include <windows.h>
    #include <stdio.h>
    
    typedef int (*FUN)(char);
    
    void printcheck()
    {  
        // 获得基地址
        HMODULE baseaddr = GetModuleHandle(NULL);
        // 获得check函数地址
        FUN check = (FUN)((uintptr_t)baseaddr + 0x16A0);
        // printf("%llxn", (uintptr_t)baseaddr);
        // 进行黑盒测试
        int i;
        for (i = 0; i < 256; i++)
        {
            printf("(%d, %d)n", i, check(i));
        }
    }
    
    BOOL WINAPI DllMain(_In_ HINSTANCE hinstDLL, _In_ DWORD fdwReason, _In_ LPVOID lpvReserved)
    {
        puts("infect success!!");
        printcheck();
        return TRUE;
    }
    

我这里是用vs2019编译的release版本x64程序。

当要注入dll被目标进程成功加载后，会调用DllMain，首先输出提示信息，然后调用printcheck函数。

在printcheck函数中，首先调用GetModuleHandle函数返回本模块的句柄，其实就是我们熟知的默认加载地址0x400000。

然后加上函数偏移，获得check函数的地址。函数偏移可以在ida的汇编窗口中查看：

![](https://p1.ssl.qhimg.com/t0156b2549a070b17cb.jpg)

最后就是一个256次循环对check函数进行黑盒测试。

###  注入

在网上下载dll注入工具进行注入，我用的是[Xenos](https://github.com/DarthTon/Xenos/releases)，这里附上GitHub链接。

可以看到注入后的结果：

![](https://p1.ssl.qhimg.com/t01e914bf5346baff53.png)

我们可以获得一张check函数的传入参数，返回值的映射表，往下翻即可找到返回1,2,3,4所对应的输入：

![](https://p4.ssl.qhimg.com/t01f0303ddd75402876.jpg)

前面的数字为正确字符flag对应的ASCII码。

至此，我们就通过dll注入实现了对check验证函数的黑盒测试，帮助我们快速的分析清楚了check函数的功能。

###  验证结果

我们重新运行程序，输入flag查看输出结果：

![](https://p3.ssl.qhimg.com/t018fc88801c366e8b8.jpg)

可以看到验证通过，输出right。

## 原理

实现dll注入的方法有很多，比如创建远程线程，使用注册表，消息钩取，替换原dll等。

这里简单介绍一下最常用的方法，通过创建远程线程，即使用CreateRemoteThread函数对运行中的进程注入dll。

大致的流程如下：

###  获取目标进程句柄

    
    
    HANDLE hProcess = NULL;
    //使用dwPID进程id获取目标进程句柄（然后控制进程）
    hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, dwPID);
    

###  将dll写入目标进程分配的内存中

    
    
    HANDLE hProcess;
    LPVOID pRemoteBuf = NULL;
    DWORD dwBufSize;
    // 在目标进程内存中分配dwBufSize大小的内存
    pRemoteBuf = VirtualAllocEx(hProcess, NULL, dwBufSize, MEM_COMMIT, PAGE_READWRITE);//返回值为分配所得缓冲区的地址（目标进程内存地址）
    // 将dll写入分配的内存中
    WriteProcessMemory(hProcess, pRemoteBuf, (LPVOID)szDllPath, dwBufSize, NULL);
    

###  获取LoadLibraryW() API的地址

    
    
    HMODULE hMod = NULL;
    hMod = GetModuleHandle(L"kernel32.dll");
    LPTHREAD_START_ROUTINE pThreadProc;
    pThreadProc = (LPTHREAD_START_ROUTINE)GetProcAddress(hMod, "LoadLibraryW");
    

###  在进程中运行LoadLibraryW线程

    
    
    HANDLE hProcess = NULL, hThread = NULL;
    // 在进程中运行LoadLibraryW线程
    hThread = CreateRemoteThread(hProcess, NULL, 0, pThreadProc, pRemoteBuf, 0, NULL);
    WaitForSingleObject(hThread, INFINITE);    //等待hThread事件执行完毕
    

通常情况下利用好工具就可以实现我们想要的dll注入，不过学习原理能够帮助我们理解，同时一些重要的函数也是逆向学习过程中一定要积累的。

## 参考：

《逆向工程核心原理》书籍

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Ssss** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/210158](/post/id/210158)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [逆向工程](/tag/逆向工程)

 **+1** __4赞

 __收藏

![](https://p4.ssl.qhimg.com/t016dec6aa5f8c51105.png) Ssss

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

