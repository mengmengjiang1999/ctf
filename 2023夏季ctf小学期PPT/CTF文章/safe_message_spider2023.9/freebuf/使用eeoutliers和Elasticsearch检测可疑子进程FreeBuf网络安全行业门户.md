![](https://image.3001.net/images/20190513/15577475938320.png!small)

**通过 ee-outliers 检测可疑子进程也是检测端点恶意活动一种非常有效的方法，例如：**

> 检测调用 cmd.exe 的恶意 Microsoft Word 文档
>
> 检测电子邮件内嵌的 0-day exploit 在 Outlook 中利用 PowerShell

## 收集正确的数据

我们依赖于 osquery 来收集端点数据，使用以下查询定期收集有关我们要监控的工作站与服务器的所有信息。

    
    
    SELECT p.*, h.*, u.username, u.type as usertype, pp.name as parentname, pp.cmdline as parentcmdline FROM processes p LEFT JOIN users u ON p.uid = u.uid LEFT JOIN processes pp ON p.parent = pp.pid LEFT JOIN hash as h ON p.path = h.path;
    

该查询将会结合进程执行的几个数据点，包括用户、进程、父进程名、PID 与 PPID 等。使用这些信息，来寻找可疑的子进程启动。

## 构建检测用例

在配置文件中定义如下内容：

    
    
    ##############################
    # TERMS - RARELY SEEN CHILD PROCESS
    ##############################
    # detect processes with rare children
    [terms_rare_childname]
    es_query_filter=tags:endpoint AND meta.command.name:"get_all_processes_enriched" AND _exists_:OsqueryFilter.name AND _exists_:OsqueryFilter.parentname AND NOT OsqueryFilter.parentname.raw:""
    
    aggregator=OsqueryFilter.parentname
    target= OsqueryFilter.name
    target_count_method=within_aggregator
    trigger_on=low
    trigger_method=pct_of_avg_value
    trigger_sensitivity=1
    
    outlier_type=process execution
    outlier_reason=rare child process
    outlier_summary=rare child process {OsqueryFilter.name} for {OsqueryFilter.parentname}
    
    run_model=1
    test_model=0
    

该配置解释如下：

> es_query_filter 过滤 Elasticsearch 事件信息中所有我们想要的进程信息，排除掉所有没有父进程信息的事件
>
> aggregator 根据字段 OsqueryFilter.parentname 创建每个进程的父进程的事件的 buckets
>
> 对每个 aggregator 使用字段 OsqueryFilter.name 将特定子进程名出现的总次数计为 target 字段
>
> 如果生成的进程平均计数不到 1% 会触发一个异常值（如果 cmd.exe 仅在 adobe.exe 中生成一次，并且所有由 adobe.exe
> 生成的进程平均计数为 200，则 cmd.exe 的次数为 1 小于 200 的 1% 次，将被标记为异常值）

## 运行 ee-outliers

接下来在测试环境中最近七天事件中使用 ee-outliers，测试环境中有 50 个工作站，共产生 632788 个进程执行事件

![](https://image.3001.net/images/20190513/15577476028541.png!small)

## 分析结果

首先在直方图中绘制异常事件，ee-outliers 为每个异常值添加了置信度参数，从而标定事件从用例处理的其他事件转移的程度。

![](https://image.3001.net/images/20190513/15577476134742.png!small)

过去的七天中，一共发现 94 个异常值，大约六十万个事件，这意味着大约 0.015%
的进程事件都是异常的。听起来像是可以依靠手动分析处理的。但是为了得到这个结果，确实还要将以下内容添加到异常值配置文件中作为白名单，减少误报。

    
    
    rare_child_svchost=^.*rare child process .* for svchost\.exe.*$
    rare_child_services=^.*rare child process .* for services\.exe.*$
    

由 ee-outliers 判断的异常摘要如下：

![](https://image.3001.net/images/20190513/15577476277515.png!small)

### 罕见的从 chrome.exe 调用 cmd.exe 的情况

这个事件立刻引起的分析师的注意，为什么 Chrome 会调用 cmd.exe？查看更多详细信息后，注意到是执行如下命令。

    
    
    C:\windows\system32\cmd.exe /d /c 
    "C:\Users\CENSORED\AppData\Local\1password\app\7\\1Password.exe" 
    chrome-extension://aomjjhallfgjeglCENSORED/ --parent-window=0 
    < \\.\pipe\chrome.nativeMessaging.in.ced1670e4c8e503c > 
    \\.\pipe\chrome.nativeMessaging.out.ced1670e4c8e503c
    

可以发现，这是使用 cmd.exe 调用 1Password.exe 程序的 1Password Chrome
扩展程序。这不是恶意活动，但也不是误报，确实是罕见的活动类型。

### 罕见的从 chrome.exe 调用 7zFM.exe 的情况

与前一个类似，这是 Chrome 调用 7zip 文件管理程序自动提取下载的 ZIP 文件。

### 罕见的从 explorer.exe 调用 TightVNCViewerPortable.exe 的情况

explorer.exe 是 Windows 上许多进程的父进程，这个场景下，客户使用便携式 VNC 客户端远程连接到工作站。由于这个便携式 VNC
客户端并不是工作站上允许使用的软件的一部分，因此被标记了。因为它很少被观察到从 explorer.exe 中生成（在我们的定义中，不超过
1%）。与此类似的包括“罕见的从 explorer.exe 调用 PremierColor.exe” 与 “罕见的从 explorer.exe 调用
SUMo.exe”。

## 结论

在这篇文章中介绍了如何使用 ee-outliers
发现可疑的子进程，然后可以进一步分析恶意活动。如违反公司政策（运行未经批准的软件）、运行受感染的文档（Office
文档产生的可疑进程）以及未知攻击等异常活动都可以被识别。

 ***参考来源：[NVISO](https://blog.nviso.be/2018/12/21/detecting-suspicious-child-processes-using-ee-outliers-and-elasticsearch/)，FB 小编 Avenger 编译，转载请注明来自
FreeBuf.COM**

