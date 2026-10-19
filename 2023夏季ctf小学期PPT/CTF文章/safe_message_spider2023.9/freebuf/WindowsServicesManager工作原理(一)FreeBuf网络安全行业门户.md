Windows Services Manager这个组件的工作原理比我之前想的还诡异.这里简单说一下”服务”是怎么被管理的

R3下如果你不直接操控服务注册表而是用API如OpenServiceA、CreateServiceA这些API后,会调用到RPC,发往RPC服务端 -services.exe

## handle不是真handle

我们都知道 OpenService、CretaeService这些函数在没有错误的时候都会返回一个句柄.在服务端里面是这样实现的:

![](https://image.3001.net/images/20211229/1640760271_61cc03cfa6492c2e52c00.png!small)

服务端申请一个heap内存->创建一个内核对象,交给内核管理->返回ScServiceObject  
在使用其他的API比如ChangeServiceConfig、DeleteService这些API的时候,客户端需要提供一个之前OpenService、CretaeService函数返回的句柄,这没什么.但是到了服务端也就是services.exe的时候,这个”句柄”就是一个heap内存地址

## 微软判断句柄是否有效的”高级”方法

以RDeleteService为例,微软通过一个叫做ScIsValidServiceHandle的函数判断句柄是否有效:

![](https://image.3001.net/images/20211229/1640760313_61cc03f99730bfeae3114.png!small)实际上这个判断就是判断内存是否可用,内存前几个字节是否等于特定的签名:

![](https://image.3001.net/images/20211229/1640760338_61cc04121c64f5d34a964.png!small)

其中48726573h是一个签名,char后叫做”Hres”  
但是网上的openNt的签名不知道是微软故意的还是怎么的,是跟WIN7的不一样的(也可能是年代太久远改了)  
网上的:

![](https://image.3001.net/images/20211229/1640760362_61cc042a1044ac277c180.png!small)

这波很高级

## 句柄变成结构

在服务端参数传进来的句柄从SC_HANDLE会变成一个叫做LPSC_HANDLE_STRUCT的结构,你可以简单粗暴的这样理解:

> LPSC_HANDLE_STRUCT serviceHandleStruct = (LPSC_HANDLE_STRUCT)hService;

这个”LPSC_HANDLE_STRUCT”长这样:

    
    
    typedef struct  _SC_HANDLE_STRUCT {
        DWORD Signature;     // For block identification to detect some app errors
        DWORD Flags;        // See definitions above
        DWORD AccessGranted; // Access granted to client.
        union {              // Object specific data
            struct {
                LPWSTR DatabaseName;            // Name of database opened
            } ScManagerObject;
            struct {
                LPSERVICE_RECORD ServiceRecord; // Pointer to service record
            } ScServiceObject;
        } Type;
    
    } SC_HANDLE_STRUCT, * LPSC_HANDLE_STRUCT;

请注意,网上的是错的,网上的OPEN NT结构长这样:

<https://github.com/Hengle/windows_nt_3_5_source_code/blob/d2894c9125ff1c14028435ed1b21164f6b2b871a/windows_nt_3_5_source_code/NT-782/PRIVATE/WINDOWS/SCREG/SC/SERVER/SCOPEN.H#L52>

    
    
    typedef struct  _SC_HANDLE_STRUCT{
        DWORD Signature;     // For block identification to detect some app errors
        DWORD AccessGranted; // Access granted to client.
        union {              // Object specific data
    
            struct {
                LPWSTR DatabaseName;            // Name of database opened
            } ScManagerObject;
    
            struct {
                LPSERVICE_RECORD ServiceRecord; // Pointer to service record
            } ScServiceObject;
    
        } Type;
    
    } SC_HANDLE_STRUCT, *LPSC_HANDLE_STRUCT;

这个是错的。  
之后,服务端会通过这个SC_HANDLE_STRUCT结构,检查其中的权限:

![](https://image.3001.net/images/20211229/1640760465_61cc0491e5b30d6b1797b.png!small)

然后从内核删除

![](https://image.3001.net/images/20211229/1640760484_61cc04a4bd32cff7f8a07.png!small)

  

