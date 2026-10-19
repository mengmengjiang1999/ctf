## 0x01 - 介绍

这篇文章是 ETW 绕过技术讨论的第 1/5 篇：

  * 红队开发-事件追踪ETW (1/5)-基础知识
  * 红队开发-事件追踪ETW (2/5)-两种API补丁
  * 红队开发-事件追踪ETW (3/5)-升级版：修补EtwpEventWriteFull
  * 红队开发-事件追踪ETW (4/5)-通过HBPs无需patch的ETW绕过
  * 红队开发-事件追踪ETW (5/5)-ETW跟踪会话劫持绕过ETW

事件追踪 Event Tracing for Windows (ETW)
是Windows系统内置的强大事件跟踪机制。它可以收集在系统上不同事件和活动的详细信息。这些事件可以是由系统本身发起的（例如加载一个DLL）或者由用户发起的（例如打开一个文件）。

用户模式 (user mode) 和内核模式 (kernel mode)
生成的事件都会被记录到日志文件里。所以我们自己或者其他应用程序可以通过检查这些日志文件来获得关键信息以了解系统里发生的事情。简而言之，在分析入侵事件和入侵手法上
ETW 对于防守方(包括EDR)来说是个有价值的信息来源。所以，安全软件通常都会注册订阅 (subscribe) ETW
事件来实时检测和防止攻击者。这些安全解决方案会用不同的规则和算法来判定一个事件构不构成恶意的意图。

## 0x02 - ETW 构架

![](./img/5565498133465670142.png)

上图描述了 ETW 的组件构成。注意追踪文件的扩展名是 `.etl`，由开启的会话生成。

根据[微软的文档](https://learn.microsoft.com/en-us/windows-hardware/test/weg/instrumenting-your-code-with-etw#etw-architecture)，ETW
由以下4个主要组件组成：

  * **提供程序 (Providers)** \- 提供程序是最上级组件，他们负责生成事件。提供程序可以是用户模式应用、内核模式驱动程序，或 Windows 内核本身。每个提供程序由一个独有的 GUID 作为标识。我们可以通过 `logman query providers` 来获取查看系统里 ETW 提供程序。下图显示了部分 ETW 提供程序。我们会在之后篇幅进一步讲解和使用 `logman` 工具。

![](./img/1109621217083477176.png)

  * **(跟踪)会话 (Tracing session)** \- “ETW 会话基础结构充当中间代理，将事件从一个或多个提供程序中继给使用者。 会话是一个内核对象，它将事件收集到内核缓冲区中，并将其发送到指定的文件或实时使用者进程。 可以将多个提供程序映射到单个会话，让用户能够从多个源收集数据。” 简而言之，ETW 会话可作为一个了一个中心容器来负责从单个或者多个 ETW 提供程序中收集和管理事件。 ETW 会话可以通过 `logman query -ets` 来获取，如下图所示。

![](./img/1238842732799435882.png)

  * **控制器 (Controllers)** \- 控制器负责“启动”、“停止”或"更新"跟踪会话。当一个会话被启用后，指定的 ETW 提供程序就可以开始发送事件给这个会话，这时使用者 (consumers) 也可以读取这些事件了。

  * **使用者 (Consumers)** \- 使用者是一个应用连接到 ETW 会话来读取已记录的跟踪文件，或者实时捕获活动跟踪会话中的事件并处理事件。一个会话可以不需要任何使用者并保持运行。此外，ETW 使用者可以连接到多个会话，这样使用者可以同时读取多种类型的日志事件（例如系统事件和网络事件）。  
Windows 的事件查看器和资源监视器都是内置的 ETW 使用者应用。

## 0x03 探索ETW用户模式API

刚刚讲过的 ETW 组件都是内置在 Windows 内核中的，给予了整个 Windows 基于事件的跟踪和监视功能。在用户模式里，ETW 的功能通过相关的
WinAPIs 来提供访问，开发者可以用这些 WinAPIs 来跟 ETW 设施互动并得益于 ETW 的追踪能力。用户模式只需要利用这些 WinAPIs
来注册和取消注册提供程序 (Providers)、写入事件到会话中、和配置想要追踪的事件。

部分 ETW WinAPIs 有：

  * [EventWrite](https://learn.microsoft.com/en-us/windows/win32/api/evntprov/nf-evntprov-eventwrite) 和 [EventWriteEx](https://learn.microsoft.com/en-us/windows/win32/api/evntprov/nf-evntprov-eventwriteex) \- 编写/写入一个 ETW 事件。它们分别对应 `EtwEventWrite` 和 `EtwEventWriteEx`。
  * [StartTraceA](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-starttracea) 和 [StopTraceA](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-stoptracea) \- 启动和停止一个 ETW 跟踪会话。
  * [QueryAllTraces](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-queryalltracesa) \- 获取（权限内）所有 ETW 跟踪会话的属性和统计信息。

ETW 的规避手段可以通过 patch 或者 hook 这些 WinAPIs 来修改其执行方式和内部执行链路。这些 ETW 函数一般都从
`Advapi32` DLL 导出。

## 0x04 内核层的 ETW

`ntoskrnl.exe` 是我们熟知的操作系统内核可执行文件，包含了 NT 内核的执行层面和负责硬件抽象、句柄管理、和内存管理等。内核通过 EtwTi
函数来管理 ETW。Ti 表示 "threat intelligence" - 威胁情报。

通过查阅[资料](https://jsecurity101.medium.com/uncovering-windows-events-b4b9db7eac54)了解到，当我们在用户模式下调用 `WriteProcessMemory` 会对应执行
`NtWriteVirtualMemory`，随之会调用
`MiReadWriteVirtualMemory`，最后，`EtwTiLogReadWriteVm` 会被调用来记录读写操作。

我们可以通过 IDA 来看看 `MiReadWriteVirtualMemory` 的流程。

![](./img/2634206512712004236.png)

通过查找 `MiReadWriteVirtualMemory` 我们发现
`NtReadVirtualMemory`、`NtWriteVirtualMemory`、和`NtReadVirtualMemoryEx` 都会调用
`MiReadWriteVirtualMemory`。

`EtwTiLogReadWriteVm` 就是我们要找的 EtwTi 函数用于记录读写操作。

## 0x05 其他EtwTi函数

![](./img/6801864098282210799.png)

EtwTi 函数的命名通常会告诉我们什么事件会被记录。以下是几个稍微详细点的解释：

  * `EtwTiLogSetContextThread` \- 这个函数被 `PspSetContextThreadInternal` 和 `PspWow64SetContextThread` 调用。当我们要更新线程的 context 的时候这个函数就会被触发。

  * `EtwTiLogSuspendResumeProcess` \- 多个内核函数都会调用这个 EtwTi函数，其中 `PsMultiResumeProcess` 和 `PsSuspendProcess` 是我们最关心的。当我们要挂起和恢复执行进程的时候会触发此函数。

  * `EtwTiLogAllocExecVm` \- 这个函数从 `MiAllocateVirtualMemory` 里被调用. 当我们分配可执行内存空间的时候会被触发。

  * `EtwTiLogProtectExecVm` \- 我们使用 `NtProtectVirtualMemory` 来更新内存权限为可执行的时候会被触发。

## 0x06 绕过/规避 EtwTi 的监视

从用户模式下规避 Etw 的威胁情报功能(EtwTi) 没有从内核模式下那么容易。后续文章会讨论一些绕过 ETW 日志的技巧。这里推荐阅读这两篇文章来增加对
EtwTi的进一步理解

  * [Introduction to Threat Intelligence ETW](https://undev.ninja/introduction-to-threat-intelligence-etw/)

  * [Uncovering Windows Events blog](https://posts.specterops.io/uncovering-windows-events-b4b9db7eac54)

## 0x07总结

我们目前对 ETW 有一些基本了解了，接下来我们会深入几种 ETW 绕过和规避手段。

