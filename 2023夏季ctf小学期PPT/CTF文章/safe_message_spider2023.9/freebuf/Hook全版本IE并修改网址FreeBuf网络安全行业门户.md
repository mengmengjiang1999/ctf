## **前言**

**好久不写文章了前期研究了对IE全版本的Hook，之前有人写过对IE的hook但是没有提及网址的修改等内容同时因为Hook
Api的问题不怎么稳定，这里我分享一种针对全版本IE，多平台的Hook方案。**

## 环境

**系统环境：Windows 10**

**编译环境：Visual Studio 2017**

**Windows SDK：10.0.17763.0**

**IE版本：Internet Explorer 11**

## 正文

不管三七二十一先导入一波引用

> #include <windows.h>  
> #include <WinInet.h>  
> #include <string>  
> #include <iostream>  
> using std::string;  
> using namespace std;  
> #pragma comment(lib,"wininet.lib")

首先我们知道http应用层的函数基本都在wininet.dll中故我们导出wininet.dll的函数列表(这里我使用的是ProcessHacker)

![](https://image.3001.net/images/20200811/1597136386.png!small)

![](https://image.3001.net/images/20200811/1597136454.png!small)

我们要对Url进行拦截修改所以先要查找和Url有关的函数，这边的Delay验证了我之前说的wininet.dll是延迟导入IAT
HOOK是无效的。![](https://image.3001.net/images/20200811/1597137148.png!small)

这里我们找到了InternetCrackUrl这个函数同时上面一个InternetConnect看上去非常有用，调试IE在该函数加断点
这里我使用的是开源的x64_dbg 输入指令bp InternetConnectW

![](https://image.3001.net/images/20200811/1597137430.png!small)这样我们可以确定IE在访问网址是必然会执行这个函数我们需要对其进行inline
hook，避免大家采坑说明一下IAT
Hook是行不通的，IE浏览器进行了DelayLoad，一开始并没有加载wininet.dll,通过查找wininet.h我们可以得到该函数的参数以及类型

    
    
    typedef HINTERNET(WINAPI *tInternetConnectWFunc)
    (
     HINTERNET     hInternet,
     LPCWSTR       lpszServerName,
     INTERNET_PORT nServerPort,
     LPCWSTR       lpszUserName,
     LPCWSTR       lpszPassword,
     DWORD         dwService,
     DWORD         dwFlags,
     DWORD_PTR     dwContext
    );

注意一定要引入wininet.h不然会有类型找不到

接下来我们需要准备一个变量来存储该函数的原调用

    
    
    tInternetConnectWFunc oInternetConnectWFunc ;

然后需要编写该函数的新回调，注意这边用到了Hook和UnHook需要现在头部声明，另外WCharToMByte这个转换函数在文章最后我会给出。

    
    
    HINTERNET WINAPI hkInternetConnectW(
     HINTERNET hInternet,//internet句柄（我是这么理解的）
     LPCWSTR lpszServerName,//服务器名
     INTERNET_PORT nServerPort,//端口
     LPCWSTR lpszUserName,
     LPCWSTR lpszPassword,
     DWORD dwService,
     DWORD dwFlags,
     DWORD_PTR dwContext
    )
    {
     UnHook();//先解除hook取得返回值后在重新Hook
     oInternetConnectWFunc = (tInternetConnectWFunc)GetProcAddress(GetModuleHandle(L"wininet.dll"), "InternetConnectW");//通过wininet.dll获取原函数并转换成我们声明好的类型
     LPCWSTR url = lpszServerName;
     if (WCharToMByte(url).find("*****.com") == string::npos)//此处判断是否是某地址不是强制修改为某地址
     {
      url = L"*****.com";
     }
     HINTERNET rest = oInternetConnectWFunc(hInternet, url, nServerPort, lpszUserName, lpszPassword, dwService, dwFlags, dwContext);//再次强调现货区返回值在恢复hook
     InHook();
     return rest;
    }

接下来是InLineHook非常简单

    
    
    BYTE oldAddress[5];
    BYTE newAddress[5] = { 0xE9 };
    void InHook()
    {
     memcpy(oldAddress, InternetConnectW, 2); //保存原字节
     BYTE pByte[2] = { 0xEB,0xF9 }; //优化以防重复Hook
     if (*(BYTE*)InternetConnectW == 0xEB)
      return;
    
     // 计算偏移
     DWORD Offset = (DWORD)hkInternetConnectW - (DWORD)InternetConnectW;
     *(DWORD*)(newAddress + 1) = Offset;
     
     DWORD Protect;
     VirtualProtect((LPVOID)((DWORD)InternetConnectW - 5), 7, PAGE_EXECUTE_READWRITE, &Protect);//修改内存属性
    
     // 修改函数地址数据
     memcpy((LPVOID)((DWORD)InternetConnectW - 5), newAddress, 5);
     memcpy(InternetConnectW, pByte, 2);
     
     VirtualProtect((LPVOID)((DWORD)InternetConnectW - 5), 7, Protect, &Protect);// 还原内存属性
    }
    
    
    
    void UnHook()
    {
     DWORD Protect;
     VirtualProtect(InternetConnectW, 2, PAGE_EXECUTE_READWRITE, &Protect);
     memcpy(InternetConnectW, oldAddress, 2);
     VirtualProtect(InternetConnectW, 2, Protect, &Protect);
    }

最后就是dll的入口

    
    
    BOOL APIENTRY DllMain( HMODULE hModule,
                           DWORD  ul_reason_for_call,
                           LPVOID lpReserved
                         )
    {
        switch (ul_reason_for_call)
        {
        case DLL_PROCESS_ATTACH:
      InHook();
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
        }
        return TRUE;
    }

最后是讲LPCESTR 转换成string的函数，该函数需要放在最上面，或者先声明在调用

    
    
    string WCharToMByte(LPCWSTR lpcwszStr)
    {
     string str;
     DWORD dwMinSize = 0;
     LPSTR lpszStr = NULL;
     dwMinSize = WideCharToMultiByte(CP_OEMCP, NULL, lpcwszStr, -1, NULL, 0, NULL, FALSE);
     if (0 == dwMinSize)
     {
      return FALSE;
     }
     lpszStr = new char[dwMinSize];
     WideCharToMultiByte(CP_OEMCP, NULL, lpcwszStr, -1, lpszStr, dwMinSize, NULL, FALSE);
     str = lpszStr;
     delete[] lpszStr;
     return str;
    }

到这里基本就完成了，这边值得注意的是ie11有多个进程主进程是64位每个标签的子进程是32位故此我们需要编译成Release x86
和x64两个版本，注入我这边测试是使用ProcessHacker进行注入的

![](https://image.3001.net/images/20200811/1597139114.png!small)

需要对ie的所有进程进行注入，如果自己编写注入器的话需要注意x86和x64的区分注入方法非常多这里我就不多做累述了，值得注意的是虽然Proccess
Hacker是驱动级任务管理器，但是部分进程他还是无法直接注入的，需要大家自己编写注入代码。

最后附上效果图

![](https://image.3001.net/images/20200811/1597139695.png!small)无法上传视频对效果图简单说明一下tab栏显示的是tb实际上却是bd，对于其他浏览器不一定直接使用InternetConnectW，但是大家也可以通过此方法调试浏览器后写出方法。

补充：最终效果的gif图更明显的看出效果。

![](https://image.3001.net/images/20200814/1597387497.gif!small)

## 后记

本文的代码虽然是片段式的，但组合后可直接运行，不直接贴完整代码，也是希望大家可以自己动手完全理解原理和技术点。下期将为大家带来一篇通俗易懂的Hook技术以及防Hook的文章，对于两年前的基于注入的进程防杀也会补上（这次不会跳票啦，之前因为某些原因没有继续写下去）。

关于有朋友提到过不了检测我这边放一张我本地杀软的图商业杀软ESET SMART SECURITY 旗舰版

![](https://image.3001.net/images/20200814/1597387695.png!small)

