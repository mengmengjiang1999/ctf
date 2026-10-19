> 作者：anhkgg

> 日期：2019年11月3日

很多时候，可能会对某个软件进行DLL劫持。

而这个软件是否存在DLL劫持漏洞，需要去分析验证。

比如通过IDA查看导入的DLL，或者LoadLibrary的DLL，然后慢慢排除某些KnownDlls，排除某些绝对路径加载的DLL...

或者通过Windbg分析。

虽然技术难度不高，但是挺费事的。

本篇文章分享我找DLL劫持的方法，不一定是最佳，不过很方便。

### 1

首先，通过windbg启动软件，设置（默认开启的）：

    
    
    Debug->Event Filters->Load module，勾选Output
    

然后go运行。这样我们可以看到运行后，软件导入表导入的DLL，以及LoadLibrary加载的DLL的所有文件，如下所示：

    
    
    ModLoad: 75090000 750cb000   C:\Windows\system32\rsaenh.dll
    
    ModLoad: 757c0000 757cc000   C:\Windows\system32\CRYPTBASE.dll
    
    ModLoad: 778b0000 778da000   C:\Windows\system32\imagehlp.dll
    
    ModLoad: 77860000 778a5000   C:\Windows\system32\WLDAP32.dll
    

### 2

写一个测试的DLL，只用下面的代码：

    
    
    BOOL APIENTRY DllMain( HMODULE hModule,
    
                           DWORD  ul_reason_for_call,
    
                           LPVOID lpReserved
    
                         )
    
    {
    
        char path[MAX_PATH] = { 0 };
    
        switch (ul_reason_for_call)
    
        {
    
        case DLL_PROCESS_ATTACH:
    
            OutputDebugStringA(path);
    
            OutputDebugStringA("success!");
    
            MessageBoxA(NULL, "success!", "Tips", MB_OK);
    
            ExitProcess(0);
    
            break;
    
        case DLL_THREAD_ATTACH:
    
        case DLL_THREAD_DETACH:
    
        case DLL_PROCESS_DETACH:
    
            break;
    
        }
    
        return TRUE;
    
    }
    

然后讲DLL改名成劫持目标DLL，放到软件目录下，运行验证即可。

如果出现提示`success`则表示该目标DLL劫持成功。

### 3

如果DLL太多了，一一验证排除肯定很麻烦，所以程序员又要写代码了。

写一个自动批量验证的工具，基本思路如下：

  * 把windbg拿到的dll列表保存下来

  * 准备好测试DLL，DLL中加入写log功能

  * 分析dll列表，一一把测试DLL拷贝为目标dll，启动软件

  * 然后把log提取出来，可以看到成功劫持的dll

![1.png](https://image.3001.net/images/20191104/1572835676_5dbf915ce97d4.png!small)  

  

工具界面如上，一键验证所有DLL，分分钟拿到结果。

工具会分享到<https://github.com/anhkgg/anhkgg-tools>下，欢迎使用，如有bug，请联系我。

QQ交流群：[753894145](https://jq.qq.com/?_wv=1027&k=5ww6tlB)

如果觉得内容还不错，欢迎关注公众号：[汉客儿](https://mp.weixin.qq.com/s/qaKCG1RkBOnr3SkG9Oc1pA)。

