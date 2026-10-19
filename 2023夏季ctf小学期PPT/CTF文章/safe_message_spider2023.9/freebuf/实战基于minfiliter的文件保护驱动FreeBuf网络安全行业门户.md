## 前言

云山雾隐@研发团队最近需要实现一个文件保护功能，以防止文件被删除。

经调研及测试，微软的minifilter可以满足功能且实现相对简单；因此仅以此文总结经验，供大家共同学习与讨论。

## 关于minfiliter

[minifilter](https://docs.microsoft.com/en-us/windows-hardware/drivers/ifs/filter-manager-concepts)是微软继sfilter后推出的过滤驱动框架，相比sfilter更容易使用，需要程序员做的编码也更简洁。minifilter驱动是通过向过滤管理器（Filter
Manager）驱动进行注册时需过滤的操作，提供指定格式的回调函数让过滤管理器来进行调用即可。对于每一种操作，minifilter都可以注册一个preOperation和postOperation的回调函数，而我们在回调函数中可以实现很多功能，如：文件加密、备份等。

## 开发

本次测试演示使用的开发环境为vs2019，安装对应版本的WDK，然后新建项目，选择filter driver:filesystem mini-filter创建项目即可。

### 代码解析

项目创建成功后，会有3个文件：

  * inf安装文件

  * 版本资源文件

  * 初始化代码文件

我们先修改一下inf文件，将注释的Class和ClassGuid字段打开，否则会编译报错。进入初始化代码文件中可以看到已有一套简单的模板，模版代码实现整个框架，我们只需要在对应的函数中去实现自己的功能，步骤如下：

1.找到初始化文件中的Callbacks[]数组，这里面已经包含了所有需要过滤的请求及回调函数，我们从中选择自己需要的，此处我们要实现文件保护，就只需要过滤IRP_MJ_CREATE和IRP_MJ_SET_INFORMATION的请求即可；把IRP_MJ_OPERATION_END
作为结束标志，放到数组的最后：

    
    
    CONST FLT_OPERATION_REGISTRATION callbacks[] = {  
    {IRP_MJ_CREATE,           0, PreOperationCallback, NULL},  
    {IRP_MJ_SET_INFORMATION,  0, PreOperationCallback, NULL},  
    {IRP_MJ_OPERATION_END                                  }  
    }

  

2.DriverEntry：相当于main函数，会按序执行以下步骤:

  * 执行minifilter驱动的一切所需的全局初始化

  * 调用FltRegisterFilter注册minifilter驱动

  * 调用FltStartFiltering发起过滤

    
    
    NTSTATUS  
    DriverEntry (  
    _In_ PDRIVER_OBJECT DriverObject,  
    _In_ PUNICODE_STRING RegistryPath  
    )  
    {  
    NTSTATUS status;  
    ​  
    UNREFERENCED_PARAMETER( RegistryPath );  
      
    //Register with FltMgr to tell it our callback routines  
    status = FltRegisterFilter( DriverObject,  
    &FilterRegistration,  
    &gFilterHandle );  
    ​  
    FLT_ASSERT( NT_SUCCESS( status ) );  
    ​  
    if (NT_SUCCESS( status )) {  
    //Start filtering i/o  
    status = FltStartFiltering( gFilterHandle );  
    if (!NT_SUCCESS( status )) {  
    FltUnregisterFilter( gFilterHandle );  
    }  
    }  
    ​  
    return status;  
    }

  

3.FilterUnload：用于在用户态程序控制minifilter驱动的卸载。

    
    
    NTSTATUS FilterUnload(_In_ FLT_FILTER_UNLOAD_FLAGS Flags)  
    {  
    UNREFERENCED_PARAMETER(Flags);  
    PAGED_CODE();  
    ​  
    //若有：关闭一切内核模式通信服务器端口句柄.  
    //这里踩过坑，由于没有关闭端口，导致驱动无法stop  
    /*if (g_ServerPort)  
    {  
    FltCloseCommunicationPort(g_ServerPort);  
    }*/  
    ​  
    //调用FltUnregisterFilter 来注销这个minifilter驱动.  
    FltUnregisterFilter(gFilterHandle);  
    ​  
    //执行一切所需的全局cleanup，若有  
    //do something  
    ​  
    return STATUS_SUCCESS;  
    }

  

4.PreOperationCallback：

过滤前的回调函数是本次功能的主要实现位置，我们已经注册了对应请求的回调函数，触发请求时就会调用，实现如下：

    
    
    DECLARE_CONST_UNICODE_STRING(TXT, L"txt");  
    ​  
    FLT_PREOP_CALLBACK_STATUS  
    PreOperationCallback(  
    _Inout_ PFLT_CALLBACK_DATA Data,  
    _In_ PCFLT_RELATED_OBJECTS FltObjects,  
    _Flt_CompletionContext_Outptr_ PVOID* CompletionContext  
    )  
    {  
    if (FLT_IS_IRP_OPERATION(Data)) {  
    //判断是否是删除操作  
    if (Data->Iopb->Parameters.Create.SecurityContext->DesiredAccess & DELETE){  
    //若是，解析Data数据，获取文件信息，判断是否是我们要保护的txt类型文件  
    PFLT_FILE_NAME_INFORMATION name_info;  
    if (NT_SUCCESS(FltGetFileNameInformation(  
    data,  
    FLT_FILE_NAME_NORMALIZED |  
    FLT_FILE_NAME_QUERY_ALWAYS_ALLOW_CACHE_LOOKUP,  
    name_info ))) {  
    //Parse file name information  
    if (NT_SUCCESS(FltParseFileNameInformation(name_info))) {  
    if (RtlEqualUnicodeString(&name_info->Extension, &TXT, TRUE))){  
    FltReleaseFileNameInformation(name_info);  
    Data->IoStatus.Status = STATUS_ACCESS_DENIED;  
    //已处理完毕，不再往下层发送  
    return FLT_PREOP_COMPLETE;  
    }  
    }  
    }  
    }  
    }  
    ​  
    //返回值是FLT_PREOP_SUCCESS_NO_CALLBACK，表示不调用postOperationCallback  
    return FLT_PREOP_SUCCESS_NO_CALLBACK;  
    }

完成以上函数的开发即可生成一个简易的文件保护驱动，当然也可以在此基础上继续完善，如增加通信等。下面我们在Windows虚拟机中打开测试模式：通过inf文件安装，sc
start 启动驱动，对需实现的功能进行测试。

## 部署

驱动开发完成后对其功能的测试是基于Windows测试模式下进行的，实际使用时需要在正常的模式下安装，这就需要对驱动签名。关于驱动签名、签名前的认证、测试环境的搭建和测试流程此前已有文章详细介绍，请参考[《避坑
|
Windows驱动签名经验贴》](https://yunshanwuyin.com/BlogDetail?Id=2rw2depz3jhghnskrsg9874p)此处主要介绍minifilter驱动如何通过HLK认证。

## HLK认证

将需要测试的驱动程序部署在HLK client上，在HLK server进行控制，HLK
server会对client执行各种自动化操作，并在server上生成测试结果。如在测试过程中遇到以下问题，可以尝试我们提出的对应解决方案。

### 1.server端找不到client端安装的驱动

看看inf文件中的StartType字段是否是1；若不是，修改为1，让驱动随系统启动加载。再重新编译驱动，卸载client端驱动，安装新编译的驱动并重启环境，即可解决。

### 2.测试用例未完全通过

第一次测试时，部分用例失败，测试结果如下：

![](https://image.3001.net/images/20220516/1652688487_62820667d09b7dff52ad7.png!small)

通过日志和[官方文档](https://docs.microsoft.com/en-us/windows-hardware/test/hlk/testref/filter-driver-tests)可知，需要在client端部署不同的文件系统。

在client端部署环境，参考如下：

![](https://image.3001.net/images/20220516/1652688538_6282069a446503c3287bf.png!small)

Windows自带的分区工具只支持NTFS CNTFS FAT6 FAT32这几种文件系统，可通过以下命令修改文件系统类型：

    
    
    format N: /FS:UDF  
    如果出现 enter current volume label for drive N：这样的提示输入  
    先使用 vol N：获取磁盘N的卷标  
    然后输入，继续下一步

环境准备完成：![](https://image.3001.net/images/20220516/1652688560_628206b0d482712708c99.png!small)

重新测试，关于文件系统的用例即可全部通过。

### 3.权限问题造成的测试失败

仍有部分用例失败，查看日志是权限的问题造成的，如下：

![](https://image.3001.net/images/20220516/1652688587_628206cb12d496890666c.png!small)

修改注册表中HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System路径下的键值：EnableLUA从1修改为0，然后重启，问题即可解决。

再重跑测试用例，用例全部通过，打包提交进行签名，签名完成后就可以正常安装了。

  

以上，仅为云山雾隐@研发团队在本次测试过程中遇到的问题，欢迎大家留言讨论、一起交流学习。

