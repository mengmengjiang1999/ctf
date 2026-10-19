无文件落地的木马主要是一段可以自定位的shellcode组成,特点是没有文件，可以附加到任何进程里面执行。一旦特征码被捕获甚至是只需要xor一次就能改变特征码.由于传统安全软件是基于文件检测的,对目前越来越多的无文件落地木马检查效果差.

**基于内存行为特征的检测方式,可以通过检测执行代码是否在正常文件镜像区段内去识别是否是无文件木马.由于cobaltstrike等无文件木马区段所在的是private内存,所以在执行loadimage回调的时候可以通过堆栈回溯快速确认是否是无文件木马**

检测只需要40行代码:

> 在loadimagecallback上做堆栈回溯
>
> 发现是private区域的内存并且是excute权限的code在加载dll,极有可能,非常有可能是无文件木马或者是shellcode在运行
    
    
    void LoadImageNotify(PUNICODE_STRING pFullImageName, HANDLE pProcessId, PIMAGE_INFO pImageInfo)
    {
        UNREFERENCED_PARAMETER(pFullImageName);
        UNREFERENCED_PARAMETER(pProcessId);
        UNREFERENCED_PARAMETER(pImageInfo);
        if (KeGetCurrentIrql() != PASSIVE_LEVEL)
            return;
        if (PsGetCurrentProcessId() != (HANDLE)4 && PsGetCurrentProcessId() != (HANDLE)0) {
            if (WalkStack(10) == false) {
    
                DebugPrint("[!!!] CobaltStrike Shellcode Detected Process Name: %s\n", PsGetProcessImageFileName(PsGetCurrentProcess()));
                ZwTerminateProcess(NtCurrentProcess(), 0);
                return;
            }
        }
        return;
    }

堆栈回溯:

    
    
    bool WalkStack(int pHeight)
    {
        bool bResult = true;
        PVOID dwStackWalkAddress[STACK_WALK_WEIGHT] = { 0 };
        unsigned __int64  iWalkChainCount = RtlWalkFrameChain(dwStackWalkAddress, STACK_WALK_WEIGHT, 1);
        int iWalkLimit = 0;
        for (unsigned __int64 i = iWalkChainCount; i > 0; i--)
        {
            if (iWalkLimit > pHeight)
                break;
            iWalkLimit++;
            if (CheckStackVAD((PVOID)dwStackWalkAddress[i])) {
                DebugPrint("height: %d address %p \n", i, dwStackWalkAddress[i]);
                bResult = false;
                break;
            }
        }
        return bResult;
    }

使用:

编译好驱动,加载驱动,之后运行测试看看:

普通生成(x32与x64)测试:

![](https://image.3001.net/images/20210726/1627230103_60fd8f9770d3938d3d792.png!small)

基于VirtualAlloc的C代码测试:

![](https://image.3001.net/images/20210726/1627230145_60fd8fc1c017cbc88dd6d.png!small)

测试结果:

![](https://image.3001.net/images/20210726/1627230167_60fd8fd7118350ead7043.png!small)基于powershell的测试:

![](https://image.3001.net/images/20210726/1627230190_60fd8fee0b3598c816cd2.png!small)

基于python的测试

![](https://image.3001.net/images/20210726/1627230212_60fd9004d382ea0c2bd17.png!small)

测试结果:

![](https://image.3001.net/images/20210726/1627230237_60fd901d9c7eba2099c95.png!small)

弊端:  
目前已知的ngentask.exe、sdiagnhost.exe服务会触发这个检测规则(看样子是为了执行一些更新服务从微软服务端下载了一些shellcode之类的去运行).如果后续优化则需要做一个数字签名校验等给这些特殊的进程进行加白操作.这是工程问题,不是这个demo的问题  
一如既往的 github:  
<https://github.com/huoji120/CobaltStrikeDetected>

