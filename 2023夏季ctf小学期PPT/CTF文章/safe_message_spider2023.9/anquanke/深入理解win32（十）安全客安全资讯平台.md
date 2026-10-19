# 深入理解win32（十）

阅读量 **172791**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-27 10:00:06

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01e94717568627114f.jpg)

## 前言

在上一节里我们主要对标准空间和通用空间进行了了解，这一节我们来了解线程以及实现进程的遍历。

## 进程遍历

在实现进程的遍历之前，我们首先要了解进程这个概念：

>
> 进程（Process）是计算机中的程序关于某数据集合上的一次运行活动，是系统进行资源分配和调度的基本单位，是操作系统结构的基础。在早期面向进程设计的计算机结构中，进程是程序的基本执行实体；在当代面向线程设计的计算机结构中，进程是线程的容器。程序是指令、数据及其组织形式的描述，进程是程序的实体。

用通俗点的话来说，一个exe在双击启动后就变成了一个进程。那么我们要想实现进程的遍历，这里就需要用到windows给我们提供的几个api。进程遍历的方式有很多，这里就说一种最常用的方式。

**CreateToolhelp32Snapshot**

    
    
    HANDLE WINAPI CreateToolhelp32Snapshot( 
    DWORD dwFlags,                     //用来指定快照中需要返回的对象
    DWORD th32ProcessID );            //一个进程的ID，用来指定要获取哪一个进程的快照
                                    //若想获得系统进程列表或获取当前进程快照时可以设置成0
    

> dwFlags
>
> Specifies portions of the system to include in the snapshot. This parameter
> can be one of the following: Value Description TH32CS_SNAPALL Equivalent to
> specifying TH32CS_SNAPHEAPLIST, TH32CS_SNAPMODULE, TH32CS_SNAPPROCESS, and
> TH32CS_SNAPTHREAD. TH32CS_SNAPHEAPLIST Includes the heap list of the
> specified process in the snapshot. TH32CS_SNAPMODULE Includes the module
> list of the specified process in the snapshot. TH32CS_SNAPPROCESS Includes
> the process list in the snapshot. TH32CS_SNAPTHREAD Includes the thread list
> in the snapshot.
>
> th32ProcessID
>
> Process identifier. This parameter can be zero to indicate the current
> process. This parameter is used when the TH32CS_SNAPHEAPLIST or
> TH32CS_SNAPMODULE value is specified. Otherwise, it is ignored.

`CreateToolhelp32Snapshot`这个api主要是用来创建一个进程快照，我们知道在一个程序运行起来过后，是不能够对这个程序进行任何修改的操作的，所以我们要想拿到进程的句柄，就需要使用到`CreateToolhelp32Snapshot`这个api首先拍摄一个进程的快照

这里`CreateToolhelp32Snapshot`的`dwFlags`一般有以下几个值

    
    
    TH32CS_SNAPHEAPLIST 枚举th32ProcessID参数指定的进程中的堆。
    TH32CS_SNAPMODULE 枚举th32ProcessID参数指定的进程中的模块。
    TH32CS_SNAPPROCESS 枚举系统范围内的进程，此时th32ProcessID参数被忽略。
    TH32CS_SNAPTHREAD 枚举系统范围内的线程，此时th32ProcessID参数被忽略。
    

函数执行成功会返回一个快照句柄，否则返回INVALID_HANDLE_VALUE（-1）。那么这里我们就首先可以写出一个拍摄快照的代码，若返回`INVALID_HANDLE_VALUE`则弹框显示快照没有拍摄成功

    
    
    void InitProcess(HWND hListProcess, HWND hDlg)
    {
        PROCESSENTRY p32;
    
        HANDLE Sanpshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (Sanpshot == INVALID_HANDLE_VALUE)
        {
            MessageBoxA(hDlg, TEXT("Createsnapshot failed"), TEXT("Error), MB_OK);
        }
    }
    

**Process32First** & **Process32Next**

当快照拍摄完成之后，我们就需要进行进程的遍历，这里就用到`Process32First`和`Process32Next`这两个api

    
    
    BOOL WINAPI Process32First( 
    HANDLE hSnapshot,                 //快照句柄
    LPPROCESSENTRY32 lppe );        //向PEOCESSENTRY32结构的指针
    

>   * _hSnapshot_
>

>
> Handle to the snapshot returned from a previous call to the
> [**CreateToolhelp32Snapshot**](_wcesdk_win32_createtoolhelp32snapshot.htm)
> function.
>
>   * _lppe_ Pointer to a
> [**PROCESSENTRY32**](_wcesdk_win95_processentry32_str.htm) structure.
>

    
    
    BOOL WINAPI Process32Next( 
    HANDLE hSnapshot, 
    LPPROCESSENTRY32 lppe );
    

>   * _hSnapshot_ Handle to the snapshot returned from a previous call to the
> [**CreateToolhelp32Snapshot**](_wcesdk_win32_createtoolhelp32snapshot.htm)
> function.
>   * _lppe_ Pointer to a
> [**PROCESSENTRY32**](_wcesdk_win95_processentry32_str.htm) structure.
>

相当于我们首次遍历进程的时候使用到`Process32First`然后后面遍历的过程使用到`Process32Next`即可，注意两个api的第二个值都是一个指针，指向的是`PROCESSENTRY32`这个结构体，`PROCESSENTRY32`结构体的结构如下

    
    
    typedef struct tagPROCESSENTRY32 { 
    {
        DWORD dwSize;             //结构的长度，需要预先设置
        DWORD cntUsage;            //进程的引用记数 
        DWORD th32ProcessID;    //进程ID
        DWORD th32DefaultHeapID;//进程默认堆的ID
        DWORD th32ModuleID；    //进程模块的ID
        DWORD cntThreads；        //进程创建的线程数
        DWORD th32ParentProcessID；//进程的父线程ID
        LONG pcPriClassBase；    //进程创建的线程基本优先级
        DWORD dwFlags；            //内部使用
        CHAR szExeFile[MAX_PATH];//进程路径
    }PROCESSENTRY32;
    

我们主要关注的是`dwSize`、`th32ProcessID`和`szExeFile[MAX_PATH]`，即结构长度、进程ID以及路径，我们知道在windows里面分为内核层和用户层，但是有内核层是不能够直接操作的，那么这时候就只能使用PID去调用。

实现代码如下

    
    
    #include "stdafx.h"
    #include <stdio.h>
    #include <stdlib.h>
    #include <windows.h>
    #include <Tlhelp32.h>
    
    int main(int argc, char *argv[])
    {
        PROCESSENTRY32 pe32;
        pe32.dwSize = sizeof(pe32);
        HANDLE hSnapshot_proc = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (hSnapshot_proc != INVALID_HANDLE_VALUE)
        {
            BOOL check = Process32First(hSnapshot_proc, &pe32);
            while (check)
            {
                printf("进程PID = %d 进程名 = %s\n", pe32.th32ProcessID, pe32.szExeFile);
                check = Process32Next(hSnapshot_proc, &pe32);
            }
        }
        CloseHandle(hSnapshot_proc);
        system("pause");
        return 0;
    }
    

实现效果如下

![](https://p1.ssl.qhimg.com/t016b4f8f1bd9da7bd2.jpg)

## 线程

**线程** （英语：thread）是操作系统能够进行运算调度的最小单位。大部分情况下，它被包含在进程之中，是进程中的实际运作单位。

我们平时所看到的exe只是一个程序，而当程序跑起来之后才叫进程，而一个进程里面至少含有一个线程，也就是说必须要有线程才能让程序跑起来。

比如这里写一个循环输出

![](https://p0.ssl.qhimg.com/t015dbb5c5c54c5c92e.png)

这里可以看到进程的线程数为1

![](https://p1.ssl.qhimg.com/t0136c26636134aab5f.png)

**CreateThread**

是windows下创建线程的api，我们这里使用`CreateThread`创建一个线程实现循环输出

    
    
    DWORD WINAPI ThreadProc(
      LPVOID lpParameter   // thread data
    )
    {
        for (int i = 0 ; i < 1000 ; i++)
        {
            Sleep(1000);
    
            printf("--------------\n");
    
            return 0;
        }
    }
    
    void TestThread()
    {
        HANDLE hThread = ::CreateThread(NULL,0,ThreadProc,NULL,0,NULL);
    
        ::CloseHandle(hThread);
    }
    
    int main(int argc, char* argv[])
    {
        TestThread();
    
        for (int i = 0 ; i < 1000 ; i++)
        {
            Sleep(1000);
    
            printf("++++++++++++++\n");
        }
    
        return 0;
    }
    

![](https://p3.ssl.qhimg.com/t017873e2ba860f6058.png)

再看下`CreateThread`的结构，如下所示

    
    
    HANDLE CreateThread(                
      LPSECURITY_ATTRIBUTES lpThreadAttributes, // 安全属性 通常为NULL                
      SIZE_T dwStackSize,                       // 参数用于设定线程可以将多少地址空间用于它自己的堆栈                
                                                   // 每个线程拥有它自己的堆栈
      LPTHREAD_START_ROUTINE lpStartAddress,    // 参数用于指明想要新线程执行的线程函数的地址                
      LPVOID lpParameter,                       // 线程函数的参数                
                                                // 在线程启动执行时将该参数传递给线程函数
                                                // 既可以是数字，也可以是指向包含其他信息的一个数据结构的指针
      DWORD dwCreationFlags,                    // 0 创建完毕立即调度  CREATE_SUSPENDED创建后挂起                
      LPDWORD lpThreadId                        // 线程ID                 
    );                                            // 返回值：线程句柄
    

这里创建的线程是在0环里面创建，但是我们这里在3环是不能够访问到0环的内存的，所以这里操作系统给我们返回的是线程句柄供我们操作内核层里的内存进行操作

    
    
    HANDLE hThread = ::CreateThread(NULL,0,ThreadProc,NULL,0,NULL);
    
    ::CloseHandle(hThread);
    

这里注意一下，`CreateThread`这个API我们最好在前面加两个`::`以表示`CreateThread`这个API为全局变量。这里的`CloseHandle`只是把创建线程时候的编号给关闭了，线程仍然存在

这里使用一下`lpParameter`这个参数，假如我传一个参数2进去，这里有一个错误的写法，就是`lpParameter`这个指针直接指向x所在的内存地址，这里理论上是取得到x的值的，但是因为x是一个局部变量，在main函数里调用一次`TestThread()`函数之后，堆栈就会进行销毁，所以x的值就不存在了

![](https://p4.ssl.qhimg.com/t0154f3e4293303cfaf.png)

这里解决方法直接把x当作全局变量即可

![](https://p5.ssl.qhimg.com/t01f09234c43d7c4dff.png)

我们知道`lpParameter`这个参数为`LPVOID`即指针类型，所以需要对x这个参数进行强制转型

    
    
    DWORD WINAPI ThreadProc(
      LPVOID lpParameter   // thread data
    )
    {
        int p = (int)lpParameter;
    
        for (int i = 0 ; i < 1000 ; i++)
        {
            Sleep(1000);
    
            printf("--------------%d-----------------\n", p);
    
            return 0;
        }
    }
    
    void TestThread()
    {
        int x = 2;
    
        HANDLE hThread = ::CreateThread(NULL,0,ThreadProc,(void*)x,0,NULL);
    
        ::CloseHandle(hThread);
    }
    

![](https://p5.ssl.qhimg.com/t01c58d6fdcf1b52537.png)

向线程函数传递变量的两种方式：

> 全局变量&线程参数

这里为了增强对线程的理解，我们试着使用`CreateProcess`创建线程创建文本框并点击开始后，每隔一秒钟，文本框中的值减1

![](https://p2.ssl.qhimg.com/t01490f37d6a9fce107.png)

创建窗口并给文本框赋初值为1000，把句柄`hEdit`定义成全局变量

![](https://p3.ssl.qhimg.com/t017ca7a1c2b17fe5e5.png)

    
    
        case WM_INITDIALOG:
            {
    
                hEdit = GetDlgItem(hDlg, IDC_EDIT);
    
                SetWindowText(hEdit, "1000");
    
                break;
            }
    

获取文本框内容

    
    
    TCHAR szBuffer[10];
    memset(szBuffer, 0 , 10);
    
    //获取文本框内容
    GetWindowText(hEdit, szBuffer, 10);
    

![](https://p4.ssl.qhimg.com/t01860485b2436e822a.png)

![](https://p1.ssl.qhimg.com/t01c9e24d2a14321749.png)

将文本框的内容转换为整数

    
    
    DWORD dwTimer;
    sscanf(szBuffer, "%d", &dwTimer);
    

![](https://p4.ssl.qhimg.com/t01790c861b2b54b94e.png)

![](https://p1.ssl.qhimg.com/t011dea0656bf705098.png)

整数自减

    
    
    dwTimer--;
    

整数转回字符串

    
    
    memset(szBuffer, 0 , 10);
    sprintf(szBuffer, "%d", dwTimer);
    

写回文本框

    
    
    SetWindowText(hEdit, szBuffer);
    

演示效果如下

![](https://p2.ssl.qhimg.com/t016d241545a5625c40.png)

![](https://p4.ssl.qhimg.com/t01d700d13e1faf1488.png)

创建线程实现每隔1秒自增自减

    
    
    // win32 thread.cpp : Defines the entry point for the application.
    //
    
    #include "stdafx.h"    
    
    HWND hEdit_SUB;
    HWND hEdit_ADD;
    
    DWORD WINAPI ThreadProc_SUB(LPVOID lpParameter)
    {
        TCHAR szBuffer[10];
        memset(szBuffer, 0 , 10);
    
        //获取文本框内容
        GetWindowText(hEdit_SUB, szBuffer, 10);
    
        //内容->整数
        DWORD dwTimer;
        sscanf(szBuffer, "%d", &dwTimer);
    
        while (dwTimer > 0)
        {
        //整数自减
        dwTimer--;
        Sleep(1000);
    
        //整数->字符串
        memset(szBuffer, 0 , 10);
        sprintf(szBuffer, "%d", dwTimer);
    
        //写回
        SetWindowText(hEdit_SUB, szBuffer);
        }
    
        return 0;
    }
    
    DWORD WINAPI ThreadProc_ADD(LPVOID lpParameter)
    {
        TCHAR szBuffer[10];
        memset(szBuffer, 0 , 10);
    
        //获取文本框内容
        GetWindowText(hEdit_ADD, szBuffer, 10);
    
        //内容->整数
        DWORD dwTimer;
        sscanf(szBuffer, "%d", &dwTimer);
    
        while (dwTimer <1000)
        {
        //整数自增
        dwTimer++;
        Sleep(1000);
    
        //整数->字符串
        memset(szBuffer, 0 , 10);
        sprintf(szBuffer, "%d", dwTimer);
    
        //写回
        SetWindowText(hEdit_ADD, szBuffer);
        }
    
        return 0;
    }
    
    
    BOOL CALLBACK MainDlgProc(HWND hDlg, UINT uMsg, WPARAM wParam, LPARAM lParam)
    {
        BOOL bRet = FALSE;
    
        switch(uMsg)
        {
        case WM_CLOSE:
            {
                EndDialog(hDlg, 0);
                break;
            }
    
        case WM_INITDIALOG:
            {
    
                hEdit_SUB = GetDlgItem(hDlg, IDC_EDIT_SUB);
                hEdit_ADD = GetDlgItem(hDlg, IDC_EDIT_ADD);
    
                SetWindowText(hEdit_SUB, "1000");
                SetWindowText(hEdit_ADD, "0");
    
                break;
            }
    
        case WM_COMMAND:
    
            switch (LOWORD (wParam))
    
            {
            case IDC_BUTTON:
                {
                    HANDLE hThread_SUB = ::CreateThread(NULL, 0, ThreadProc_SUB, NULL, 0, NULL);    
                    HANDLE hThread_ADD = ::CreateThread(NULL, 0, ThreadProc_ADD, NULL, 0, NULL);
    
                    //如果不在其他的地方引用它 关闭句柄                
                    ::CloseHandle(hThread_SUB);
                    ::CloseHandle(hThread_ADD);
    
                    return TRUE;
                }
    
    
            break;
            }
        }
    
        return bRet;
    }
    
    int APIENTRY WinMain(HINSTANCE hInstance,
                         HINSTANCE hPrevInstance,
                         LPSTR     lpCmdLine,
                         int       nCmdShow)
    {
         // TODO: Place code here.
    
        DialogBox(hInstance, MAKEINTRESOURCE(IDD_DIALOG_MAIN), NULL,MainDlgProc);
    
        return 0;
    }
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Drunkmars** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/266036](/post/id/266036)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [win32](/tag/win32)

 **+1** __6赞

 __收藏

![](https://p0.ssl.qhimg.com/t019bb9b9add2982923.jpg) Drunkmars

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

