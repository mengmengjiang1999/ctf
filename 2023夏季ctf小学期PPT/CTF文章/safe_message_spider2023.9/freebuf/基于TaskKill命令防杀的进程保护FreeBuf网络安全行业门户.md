*****本文原创作者：Satan Spenser，本文属FreeBuf原创奖励计划，未经许可禁止转载**  
**

 **大家都知道任务管理器杀死进程的方法是TerminateProcess，对此类方法的进程保护可以采用全局hook TerminateProcess 以及
OpenProcess函数来实现，这里不多做介绍在以后的文章中会详细说明。**

今天讨论的是对于系统命令taskkill杀死进程的保护方法。使用taskkill命令关闭计算器进程我们可以看到如下返回结果：

![image.png](https://image.3001.net/images/20180410/15233319277492.png!small)  

显然这不是调用OpenProcess后使用TerminateProcess关闭进程。对于这类的方法一般而言只能用过SSDT
HOOK的方式在R0中进行拦截，而进入R0的正规方法基本只有写驱动，从WIN7开始驱动需要签名过的才能安装，所以这里给大家提供一个R3层拦截taskkill关闭受保护进程的方法。

首先我们知道taskkill在执行的时候也会产生一个进程，理论上说只需要不让这个进程启动，就可以实现拦截，最简单粗暴的方法就是检测taskkill.exe进程是否存在，只要存在马上使用TerminateProcess杀死该进程，但是这种方法用户体验非常不好，影响了正常使用，所以需要对taskkill命令参数进行过滤，从而实现指定进程的保护。

接下来介绍具体步骤。

1.检测taskkill进程是否存在如果存在注入dll。

    
    
    int bufPid = 0;
    int nowPid = (int)GetProcessIDByName("taskkill.exe");
    if (nowPid != 0 && bufPid != nowPid)
    {
        //此处注入dll
        bufPid = nowPid;
    }  
    

2.在dll中读取taskkill的commandline检测被保护进程关键字（进程名，pid）是否存在，如果存在强制干掉taskkill进程，代码中只实现了基于进程名的检测，基于pid的，可获取被保护进程名对pid进行匹配。

    
    
    LPWSTR *szArglist;
    int nArgs;
    szArglist = CommandLineToArgvW(GetCommandLineW(), &nArgs);
    for (int i = 0; i<nArgs; i++)
    {
        if (wcscmp(szArglist[i], L"notepad.exe") == 0)
        {
            TerminateProcess(GetProcessHandleByID((int)GetProcessIDByName("taskkill.exe")), 0);
        }
    }  
    

对于GetProcessIDByName函数的实现如下：

    
    
    DWORD GetProcessIDByName(const char* pName)
    {
        HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (INVALID_HANDLE_VALUE == hSnapshot) {
            return NULL;
        }
        PROCESSENTRY32 pe = { sizeof(pe) };
        for (BOOL ret = Process32First(hSnapshot, &pe); ret; ret = Process32Next(hSnapshot, &pe)) {
            if (strcmp(pe.szExeFile, pName) == 0) {
                CloseHandle(hSnapshot);
                return pe.th32ProcessID;
            }
        }
        CloseHandle(hSnapshot);
        return 0;
    }  
    

最终效果如下：

![image.png](https://image.3001.net/images/20180410/1523333985791.png!small)  

可以看到计算器进程是没有受保护的可以直接关闭，而notepad.exe则无响应。

 ***本文原创作者：Satan Spenser，本文属FreeBuf原创奖励计划，未经许可禁止转载**

