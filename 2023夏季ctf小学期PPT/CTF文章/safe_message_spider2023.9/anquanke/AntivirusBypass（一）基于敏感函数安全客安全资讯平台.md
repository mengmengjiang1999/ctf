# Antivirus Bypass（一）基于敏感函数

阅读量 **416414**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-02 16:30:59

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t013104390acf76ac1b.jpg)

本篇文章是Bypass思路系列文章的第一篇，后续会持续更新有关Bypass的思路

因为工作原因，文章断断续续，时间线上会存在差异，思路及代码可行性仅供参考。

若文章中存在说的不清楚或者错误的地方 欢迎师傅们指正 感激不尽！！！

## 前言

本文将从杀软监测敏感函数进行操作，以达到Bypass的效果。

测试编译器：VS全版本

测试Demo：Win32应用程序，MFC应用程序：

在测试Demo的时候，某些杀软会杀编译器，下面附上我测试Demo时的查杀效果：

| Win32应用程序 | MFC应用程序  
---|---|---  
VC++6.0 | 5/69 | 6/69  
VS2008 | 0/68 | 0/69  
VS2010 | 3/69 | 0/68  
VS2012 | 1/69 | 2/69  
VS2013 | 3/69 | 0/68  
VS2015 | 1/68 | 1/68  
VS2017 | 0/69 | 1/69  
VS2019 | 1/68 | 1/69  
VS2022 | 2/66 | 1/67  
  
由此可以看到，尽管代码没有特征，但是某些杀软还是会报，最新的编译器也不例外，以此引入： **杀软会查杀编译器的特性** 。

**针对杀编译器特性，我们可以选用一些较为小众的语言或者杀软对语言较为友好（eg:Golang,nim）来达到Bypass的效果，或者选用较老的编译器（eg：VS2008）去达到Bypass的效果。**

在这里，我们选用Win32应用程序，一是因为VT杀软较全面查杀的结果，二是可以直观验证代码被杀与否。

下面进入到我们本次的主题：基于敏感函数去实现Bypass。

## 一、窗口隐藏

    
    
    BOOL ShowWindow(
      HWND hWnd,
      int  nCmdShow
    );
    

![](https://p0.ssl.qhimg.com/t01f0c1a11450129277.png)

最简单的用法， **SW_HIDE** 参数下是被杀的，利用虚拟键即可达到隐藏窗体的效果。

更多详情请参考：<https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes>

这里用到的编译器是VS2019，下面附上一段笔者测试的代码：

    
    
    int main()
    {
        HWND hWnd = GetForegroundWindow();//读取窗口信息
        bool f = 0;
        while (1) {
            if (GetAsyncKeyState(VK_SPACE)) ShowWindow(hWnd, f), Sleep(100), f = !f;//VK_SPACE==点击空格显示窗体
        }
    }
    

![](https://p4.ssl.qhimg.com/t01bb5d9e6f9facc594.png)

## 二、文件执行

    
    
    UINT WinExec(
      LPCSTR lpCmdLine,
      UINT   uCmdShow
    );
    

![](https://p2.ssl.qhimg.com/t0121bb1892fd126381.png)

该函数，换个编译器可实现Bypass，Pass的编译器是VS2019，Bypass的编译器是VS2017。

![](https://p5.ssl.qhimg.com/t01f8677fe6fe8706c7.png)

=========================================分割线===========================================================

    
    
    HINSTANCE ShellExecute(
      [in, optional] HWND   hwnd,
      [in, optional] LPCSTR lpOperation,
      [in]           LPCSTR lpFile,
      [in, optional] LPCSTR lpParameters,
      [in, optional] LPCSTR lpDirectory,
      [in]           INT    nShowCmd
    );
    

![](https://p4.ssl.qhimg.com/t0168d565d7bab31db0.png)

最简单的用法，用法我就不过多描述。Bypass的编译器是VS2019，下面附上一段笔者测试的Bypass代码：

    
    
    #include <windows.h>
    #include <stdio.h>
    int main()
    {
        CONST char cmd[] = "calc.exe";
        ShellExecute(0, "open", cmd, NULL, NULL, 1);
    }
    

![](https://p3.ssl.qhimg.com/t01318b2f0ebab9a3bf.png)

=========================================分割线===========================================================

    
    
    BOOL CreateProcess(
      LPCWSTR pszImageName,
      LPCWSTR pszCmdLine,
      LPSECURITY_ATTRIBUTES psaProcess,
      LPSECURITY_ATTRIBUTES psaThread,
      BOOL fInheritHandles,
      DWORD fdwCreate,
      LPVOID pvEnvironment,
      LPWSTR pszCurDir,
      LPSTARTUPINFOW psiStartInfo,
      LPPROCESS_INFORMATION pProcInfo
    );
    

![](https://p3.ssl.qhimg.com/t01d167d1a0ac9e6492.png)

下面附上一段笔者测试得Bypass代码，用到的编译器是VS2010MFC应用程序：

    
    
    STARTUPINFO si;
    PROCESS_INFORMATION 
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi
    CreateProcess(
        NULL
        , "calc.exe"//替换要控制的新进程
        , NULL
        , NULL
        , TRUE
        , 0
        , NULL
        , NULL
        , &si
        , &pi
    
    WaitForSingleObject(pi.hProcess, INFINITE);
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    

![](https://p5.ssl.qhimg.com/t01c639497ae6490555.png)

CreateProcess可完全控制新进程，在后续文章中将深入介绍CreateProcess函数，包括 **父进程欺骗、傀儡进程** 等相关知识。

执行由简到繁：Winexec ==> ShellExecute ==> CreateProcess

Winexec主要运行exe文件 ==> ShellExecute不仅可以运行exe文件还可运行已关联文件 ==>
CreateProcess可完全控制新进程

## 总结

本文内容较为简单，主要是围绕常用的敏感函数来实现Bypass，其中运用到的小技巧可以结合实际场景将其融合，最后写出适合自己的的Loader。笔者后续将会继续分享Bypass思路，希望大家有兴趣的私我，共同进步。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ShadowJe** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/260304](/post/id/260304)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [bypass](/tag/bypass)

 **+1** __8赞

 __收藏

![](https://p3.ssl.qhimg.com/t010373d19354927ed5.png) ShadowJe

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

