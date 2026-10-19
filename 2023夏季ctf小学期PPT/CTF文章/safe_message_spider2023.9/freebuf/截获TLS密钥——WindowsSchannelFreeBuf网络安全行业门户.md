## 简介

这篇文章是研究在终端上劫持进程来截获TLS密钥以用于解密的方式，主要是使用SChannel组件的Windows应用的TLS流量，如IIS，RDP，IE以及旧版的Edge，Outlook，Powershell及其他，不包括使用OpenSSL或NNS（基本上除了IE和旧版Edge的所有浏览器都在使用）。

### SChannel

 **SChannel** 也被称为Secure Channel
23，是一个windows子系统，当windows应用程序想要做任何与TLS相关的事情时，比如与远程服务器建立一个加密会话，或接受来自客户端的TLS连接，就会使用Schannel，

从体系来看，SChannel实现了Security Support Provider Interface
(SSPI)接口，是微软提供的SSP包之一。SSP包还包括CredSSP、Negotiate、NTLM、Kerberos和Digest24等等。

SChannel使用示例：

 **HTTPS连接**

> 由IE，Edge，powershell的`InvokeWebRequest`发起的
>
> 由IIS web server收到的

 **RDP连接**

> 客户端的mstsc.exe
>
> 服务器上的终端服务（svchost.exe中的termsrv.dll）

到LDAP服务器的动态目录的 **LDAPS连接**

当服务器HTTPS lisener开启时的 **部分WinRM（PS remoting）连接** ，PS remoting还支持使用TLS客户端证书的SSL
authentication，启用时也通过schannel实现。

之前提到过其他浏览器，如Firefox和谷歌Chrome使用其他库来处理TLS，即NSS和OpenSSL，因此它们的流量超出了本文的范围。但是NSS和OpenSSL都是开源的，都有文档记录了导出secrets的方法；对于Firefox和Chrome，密钥导出是内置的，可以通过使用`SSLKEYLOGFILE`环境变量激活。

## TLS1.2流量解密及临时密钥

这项研究并不依赖协议的漏洞或脆弱性，而是基于完全控制建立或接受连接的应用程序或操作系统的情况下，我们能够检索出所使用的任何密钥和secrets，来获得解密TLS流量所需的信息。

关于TLS的内部工作原理1的第2.2节已经总结的很好了。因此本文不会非常详细地进行介绍。快速过一下TLS1.2连接及加密中的关键概念：

 **临时密钥**

每当创建一个 **TLS会话**
时，都会有许多密钥与此连接相关联。一些密钥可能用于加密，另一些用于消息验证。对于不同的方向(客户端到服务器和服务器到客户端)有不同的密钥。与服务器TLS证书密钥等长期密钥相对，这些密钥称为
**临时密钥** 以强调它们是短期的。

 **完全正向保密**

所有密码套件可以根据是否支持 **完全正向保密** （Perfect Forward
Secrecy，PFS）25来进行分类。当使用非PFS密码套件时，任何加密连接都可以使用其捕获流量和服务器TLS私钥对进行解密。相反，对于PFS密码套件，你需要相关会话的临时密钥才能解密它。

 **主密钥 master key**

形成临时密钥的过程有多个步骤。在TLS1.2中，开始时服务器和客户端一起生产一些关键素材，称之为 **Pre-Master Secret** ，再扩充到
**Master Secret** ，然后依次生成一组用于加密和认证的密钥和IV—— **write keys** 和 **MAC keys**
。MAC密钥只使用或非AEAD密码。

 **TLS session tickets**

多个独立的TLS连接可以属于同一个TLS会话，因此无需每次都计算密钥。以前的方法是使用 **session ID** ，服务器向客户机发送session
ID，然后由客户机在后续连接上使用。服务器应该存储与会话关联的密钥，因此此方法需要占用服务器上大量内存。因此后来提出了 **TLS session
tickets**
(rfc5077)，服务器向客户端发送一个加密的会话状态，使用只有服务器知道的密钥进行加密，然后客户端在下一个连接上发送回来，并由服务器解密。所有这意味着，尽管临时密钥本应在连接后销毁，但实际上它们可能在服务器和客户端的内存中都持久存在。有关TLS
session tickets的安全性影响，请参见12

 **SSL keylog文件**

为了解密一个TLS流量dump，需要一种方法来  
对于TLS 1.2，提供此信息的标准方法是通过由OpenSSL和NSS23共同支持的 **ssl keylog文件**
，keylog文件的每一行由常量标签字符串、标识TLS会话的值和secrets的值组成。作为参考，可以在4中找到Wireshark的keylog解析例程

> 获取每个会话使用的secrets
>
> 将这些密钥和会话关联起来

 **client random 和 session id**

TLS1.2的keylog文件支持会话的 **pre-master** 或 **master secrets** 。会话可以通过 **client
random** (在TLS握手期间由客户端发送的随机非加密值)或 **session id**
(由服务器发送的非加密值)来标识。TLS1.2的keylog文件的示例如下:

    
    
    CLIENT_RANDOM <client_random> <master_secret>
    

## TLS1.3流量解密

上面提到的关于TLS1.2的许多内容也适用于TLS1.3。然而，secrets产生的方式有许多变化。

对于 **TLS1.2** ，我们有以下密钥生成方案:

    
    
    (1) Pre-Master Secret
    => (2) Master Secret 
    => (3) A set of write keys and IVs 
           and possibly mac keys for client and server
    

在TLS1.2中，keylog文件格式要求你提供步骤(1)或步骤(2)的secrets。

对于 **TLS1.3** ，该方案已发展成以下版本(参见RFC844634的第93页):

    
    
    (1) Input Keying Material (IKM)
    => (2) A set of Secrets: Early, Handshake, Master etc
    => (3) A set of keys and IVs
    

TLS1.3 keylog文件还要求你提供步骤(2)的secrets。与TLS
1.2不同，每个TLS会话需要多个行，每一行提供一个特定的secrets，并通过client
random将其绑定到一个TLS会话。你至少需要四个secrets：  
* 客户端和服务器握手secret  
* 客户端和服务器通信secret

一个keylog文件示例:

    
    
    CLIENT_HANDSHAKE_TRAFFIC_SECRET <client_random> <client_hs_traffic_secret>
    SERVER_HANDSHAKE_TRAFFIC_SECRET <client_random> <server_hs_traffic_secret>
    CLIENT_TRAFFIC_SECRET_0 <client_random> <client_traffic_secret_0>
    CLIENT_TRAFFIC_SECRET_0 <client_random> <server_traffic_secret_0>
    

## 密钥隔离

Windows schannel API具有 **密钥隔离**
的概念（参见5）,通过将各种机密数据存储在一个集中隔离的地方，从而使其更难以泄露。假设我们有一个进程(例如，terminal services
client,
mstsc)希望建立一个TLS连接，然而实际的TLS握手将在另一个进程中执行(即lsass.exe)，握手期间生成的secrets(即TLS1.2的pre-master和master
keys)永远不会离开lsass.exe的内存，也永远不会接触mstsc.exe。所有这些对应用程序来说都是透明的，它只使用来自schannel.dll的函数。

应用程序端的schannel .dll在幕后(参见1中的图2.6和2.7)使用 **ALPC** 连接到lsass端的schannel
.dll。ALPC调用由加载到lsass.exe中的schannel .dll副本处理，然后使用一组加密API
(CNG，6，主要在`ncrypt.dll`和`bcrypt.dll`中实现)来执行各种密钥相关的任务。

这种操作模式不是SChannel特有的，而是适用于所有实施 **SSPI**
的安全提供程序。当你调用`InitializeSecurityContext`37时，这个调用在LSA端的`SpInitLsaModeContextFn`回调中处理，然后结果被传递到它在应用端上的`SpInitUserModeContext`。因此不需要在内存中保存凭证，windows应用程序也能够使用NTLM或Kerberos身份验证。

对我们来说，这意味着 **lsass .exe**
是个好地方，在这里可以提取任何启用SChannel的应用程序所使用的所有临时TLS密钥。我们需要hook密钥创建/操作路径，或者找到一种方法能够可靠地在内存中找到它们。我们还需要以某种方式将它们绑定到一个TLS会话来利用获得的密钥，最好采用Wireshark支持的方式(即session
id或client random)。

## 目标

我们的目标是在完全控制连接的客户端或服务端上的应用程序和/或操作系统时，使用Wireshark解密SChannel TLS流量。与Jacob
Kambic的论文1的问题陈述(从内存dump中提取密钥)相比，这种方法更为灵活，因为我们不仅可以使用内存扫描，还可以使用dbg和函数hook。其他关键要求如下:

> 不依赖 **会话恢复** 和其他机制，来防止密钥在连接关闭时被清除出内存;
>
> 尽可能不依赖于 **硬编码** 的偏移量，或其他特定于Windows和/或库的特定版本的东西;
>
> 可以从连接的客户端和服务端 **两端** 提取密钥;
>
> 在不需要 **管理员权限** 的情况下提取密钥的区域，即不触及lsass.exe的内存。类似于10中提出的方法。

## 获取TLS1.2密钥

对于TLS1.2，获取client random和密钥的配对，生成一个keylog行，就可以放进wireshark解密。

## 正常（非恢复）会话

### SslGenerateMasterKey

在正常的(非恢复的)TLS1.2会话中调用`ncrypt.dll`的`SslGenerateMasterKey`函数

参考SslGenerateMasterKey13官方文档:

    
    
    SECURITY_STATUS WINAPI SslGenerateMasterKey(
    _In_  NCRYPT_PROV_HANDLE hSslProvider,
    _In_  NCRYPT_KEY_HANDLE  hPrivateKey,
    _In_  NCRYPT_KEY_HANDLE  hPublicKey,
    _Out_ NCRYPT_KEY_HANDLE  *phMasterKey,
    _In_  DWORD              dwProtocol,
    _In_  DWORD              dwCipherSuite,
    _In_  PNCryptBufferDesc  pParameterList,
    _Out_ PBYTE              pbOutput,
    _In_  DWORD              cbOutput,
    _Out_ DWORD              *pcbResult,
    _In_  DWORD              dwFlags
    );
    

如上所示，第四个参数被注释为_Out_(一种“header注释”类型14)，意味着这个指针在函数调用结束后将被密钥地址填充。

### 获取master key

跟入这个*phMasterkey指针指向的地址会进入`NcryptSslKey`结构

![1611740079_601133af75b6cb36fab77.png!small?1611740079958](https://image.3001.net/images/20210127/1611740079_601133af75b6cb36fab77.png!small?1611740079958)

在这个结构偏移0x04处包含一个非常重要的magic
value`BDDD`（参见1第77页），在偏移0x10（x64情况，在x86情况下为0x0C）处包含另一个magic
value为`5lss`结构的指针（参见1第64-68页），实验环境内存（x64）如下

![1611740123_601133dba0577f0dae6ff.png!small?1611740124458](https://image.3001.net/images/20210127/1611740123_601133dba0577f0dae6ff.png!small?1611740124458)

跟入pNcryptSslKey指针指向的地址000002a8`bcd81e70，进入`SslMasterSecret`结构，下称`SSL5\`结构

![1611740142_601133ee900752b793fb4.png!small?1611740143006](https://image.3001.net/images/20210127/1611740142_601133ee900752b793fb4.png!small?1611740143006)

参见1的第68页， **master key** 本身位于SSL5结构偏移0x1C（x64，x86为0x14），大小为48 (0x30)字节：

![1611740164_601134045810fbf96cc95.png!small?1611740164927](https://image.3001.net/images/20210127/1611740164_601134045810fbf96cc95.png!small?1611740164927)

### 获取client random

再回到`SslGenerateMasterKey`13，可以看到关于pParameterList参数的注释:

    
    
    ...
    _In_  PNCryptBufferDesc  pParameterList,
    ...
    pParameterList [in]
    
    A pointer to an array of NCryptBuffer buffers that contain 
    information used as part of the key exchange operation.
    The precise set of buffers is dependent on the protocol 
    and cipher suite that is used. At the minimum, the list
    will contain buffers that hold the client and server
    supplied random values.
    

客户端和服务端的random正是我们需要绑定密钥和会话的东西。`NCryptBuffer`和`NCryptBufferDesc`结构被记录在.NET框架的MS参考源文档，参阅17

    
    
    typedef struct _NCryptBufferDesc {
    ULONG         ulVersion;
    ULONG         cBuffers;
    PNCryptBuffer pBuffers;
    } NCryptBufferDesc, *PNCryptBufferDesc;
    
    typedef struct _NCryptBuffer {
    ULONG cbBuffer;
    ULONG BufferType;
    PVOID pvBuffer;
    } NCryptBuffer, *PNCryptBuffer;
    

跟入pParamterList指针导`NcrytBufferDesc`，在偏移0x04获得`NCryptBuffer`的数量，在偏移量0x08获得指向NCryptBuffer结构数组的指针:

![1611740191_6011341f55493eded8f02.png!small?1611740191808](https://image.3001.net/images/20210127/1611740191_6011341f55493eded8f02.png!small?1611740191808)

跟入pBuffers指针

![1611740215_60113437c8d217c37ee80.png!small?1611740216245](https://image.3001.net/images/20210127/1611740215_60113437c8d217c37ee80.png!small?1611740216245)

在pBuffers结构数组偏移0x04处是该缓冲区的数据类型：

> BufferType=0x14=20时，为 **NCRYPTBUFFER_SSL_CLIENT_RANDOM**
>
> BufferType=0x15=21时，为 **NCRYPTBUFFER_SSL_SERVER_RANDOM**

当BufferType为0x14时，在偏移0x08处是指向client random数据的指针

![1611740239_6011344f42d2c9c497ea3.png!small?1611740239765](https://image.3001.net/images/20210127/1611740239_6011344f42d2c9c497ea3.png!small?1611740239765)

## 使用RSA握手的正常（非恢复）会话

### SslImportMasterKey

上面的方式适用于使用PFS密码(即Diffie-Hellman密钥交换)进行密钥交换的场景，也适用于使用非PFS加密套件（RSA）的Windows客户端。但是当windows服务器接受非PFS加密套件的连接时并不会调用`SslGenerateMasterKey`函数，用于9中的`ncrypt!NCryptDeriveKey`也不例外。这是因为基于RSA密钥交换的master
key并不是在Diffie -Hellman交换期间计算，而是由客户机生成并发送到服务器，由服务器的公钥来加密（这也是为什么它不是前向安全性——只要有服务器私钥任何时候都能解密)。

在这种情况下，另一个函数`ncrypt!SslImportMasterKey`26包含了我们要找的东西。给定一个私钥`hPrivateKey`，由客户端发送master
key（通过服务器的公钥加密）`pbEncryptedKey`，master key将被解密并将其写入`phMasterKey`:

    
    
    SECURITY_STATUS WINAPI SslImportMasterKey(
    _In_  NCRYPT_PROV_HANDLE hSslProvider,
    _In_  NCRYPT_KEY_HANDLE  hPrivateKey,
    _Out_ NCRYPT_KEY_HANDLE  *phMasterKey,
    _In_  DWORD              dwProtocol,
    _In_  DWORD              dwCipherSuite,
    _In_  PNCryptBufferDesc  pParameterList,
    _In_  PBYTE              pbEncryptedKey,
    _In_  DWORD              cbEncryptedKey,
    _In_  DWORD              dwFlags
    );
    

### 获取client random

与`SslGenerateMasterKey`一样，第四个参数`pParamterList`包含了指向client random的指针，此处不再赘述

![1611740321_601134a183acedff8dca2.png!small?1611740321881](https://image.3001.net/images/20210127/1611740321_601134a183acedff8dca2.png!small?1611740321881)

### 获取 master key

第三个参数`*phMasterKey`包含了指master key的指针

![1611740359_601134c71d3516fd7e53c.png!small?1611740359664](https://image.3001.net/images/20210127/1611740359_601134c71d3516fd7e53c.png!small?1611740359664)

## 使用TLS Session Hash的会话

当试图从`Ssl{Generate,Import}MasterKey`的args获得client_random时，有时会发现它并没有没有在`pParameterList`中传递。

官方文档26说

> 列表至少将包含包含客户端和服务端提供的random的缓冲区，但在某些情况下，它只包含类型为22和25的缓冲区。

类型22是 **NCRYPTBUFFER_SSL_HIGHEST_VERSION** ，没啥用。

类型25是 **NCRYPTBUFFER_SSL_SESSION_HASH** 。即使用session hash的情况。

### Session Hash

在派生master key的过程中使用 client/server random会引发一些特定类型的滥用，因此发展出了一个名为 **TLS Session
Hash** 和 **Extended Master Secret** 的TLS扩展(RFC 762727)。当启用这个扩展时，计算master
secret将包含握手消息内容的hash（ClientHello, ServerHello），而不只是client/server
random。不过Wireshark不支持使用Session Hash将密钥绑定到会话。

当然，当我们试图从服务器连接中获取密钥时，我们会得到Session Hash而不是client
random。如果远程服务器支持并愿意使用，这也可用于客户端连接。因此我们需要寻找一种新的方式，在不基于现有的`pParameterList`或TLS
session id的方式来提取client random。

### SslHashHandshake

当我们深入挖掘`SslHashHandshake`28的文档时我们会发现：

> ncrypt.dll/SslHashHandshake函数是生成SSL握手hash的三个函数之一，三个函数包括：
>
> 1\. 函数被调用时获得一个hash句柄
>
> 2\. 函数可以被hash句柄调用任意次数，以向hash中添加数据
>
> [ **3\. SslComputeFinishedHash**](https://docs.microsoft.com/en-> us/windows/win32/seccng/sslcomputefinishedhash)函数被hash句柄调用时获得散列数据摘要

在使用RFC 7627 session hash方式时，TLS1.3和TLS1.2会调用这个函数。

第一次调用是在client hello，用 **msg_type == 1** 和 **version == 0x0303** 表示

需要注意的是，TLS1.2和TLS1.3的版本都是0x0303，这是TLS 1.3中的向后兼容性

    
    
    SECURITY_STATUS WINAPI SslHashHandshake(
    _In_    NCRYPT_PROV_HANDLE hSslProvider
    _Inout_ NCRYPT_HASH_HANDLE hHandshakeHash,
    _Out_   PBYTE              pbInput,
    _In_    DWORD              cbInput,
    _In_    DWORD              dwFlags
    );
    

重点关注第三个和第四个参数

> pbInput [out]  
> 包含需要被hash的数据的缓冲区地址
>
> cbInput [in]  
> pbInput 缓冲区大小（bytes）

### 获取client random

首先跟踪ncrypt.dll/SslHashHandshake函数，跟进第3个参数pbInput指针获取待哈希数据的缓冲区地址（以下称buffer），跟进第4个参数cbInput获取缓冲区长度

![1611740414_601134feee0ec5d8267a2.png!small?1611740415563](https://image.3001.net/images/20210127/1611740414_601134feee0ec5d8267a2.png!small?1611740415563)

跟入buffer地址，先读入1字节格式的msg_type从第4字节开始读入2字节的version，若msg_type为1并且version为0x0303时，从第6字节开始读入32字节的client
random

![1611740457_601135298126efb0086a5.png!small?1611740458363](https://image.3001.net/images/20210127/1611740457_601135298126efb0086a5.png!small?1611740458363)

![1611740485_601135450c423ca7c062b.png!small?1611740486114](https://image.3001.net/images/20210127/1611740485_601135450c423ca7c062b.png!small?1611740486114)

## 获取TLS1.3密钥

根据RFC 844634第92-94页，在正常(非恢复)握手期间将生成以下内容:

> 两个 handshake traffic secrets
>
> 两个 application traffic secrets
>
> 一个 exporter master secret
>
> 一个 resumption master secret

每个traffic secrets用于生成一个write
key和IV。一个SslExpandTrafficKeys调用后，会调用两次SslExpandWriteKey，分别计算客户端和服务端的
**secrets** 。这个调用会发生两次，一次用于 handshake traffic secrets，另一次用于 application
traffic secrets。

从ghidra可以发现，`CTls13Context::GenerateHandshakeWriteKeys`和`CTls13Context::GenerateApplicationWriteKeys`两个地方都调用了`CTls13Context::ExpandTrafficAndWriteKeys`。

使用ghidra反编译`schannel!CTls13Context::ExpandTrafficAndWriteKeys`，该函数包含一个`SslExpandTrafficKeys`调用，接着调用两次`SslExpandWriteKey`:

    
    
    ulong __thiscall
    ExpandTrafficAndWriteKeys
      (CTls13Context *this,__uint64 param_1,__uint64 param_2,__uint64 param_3,__uint64 *param_4,
      __uint64 *param_5,__uint64 *param_6,__uint64 *param_7,eSslErrorState *param_8)
    
    {
    // <SNIP>
    uVar1 = (*(code *)__imp_SslExpandTrafficKeys)(param_1,param_2,param_3,param_4,param_5,0,0);
    if (uVar1 == 0) {
    if (this[0xa9] != (CTls13Context)0x0) {
    uVar1 = (*(code *)__imp_SslExpandWriteKey)
                      (param_1,*param_4,param_6,0,(ulonglong)param_5._4_4_ << 0x20);
    if (uVar1 != 0) {
      *param_8 = 0x25e;
      return uVar1;
    }
    uVar1 = (*(code *)__imp_SslExpandWriteKey)
                      (param_1,*param_5,param_7,0,(ulonglong)param_5._4_4_ << 0x20);
    if (uVar1 != 0) {
      *param_8 = 0x25f;
      return uVar1;
    }
    }
    uVar1 = 0;
    }
    // <SNIP>
    }
    

`SslExpandTrafficKeys`将生成的两个密钥放到了第4个和第5个参数中。之前提到过，该函数会调用两次，第一次生成handshake
traffic secrets，第二次生成application traiffic secrets。

### SslExpandTrafficKeys

如图，hook函数`SslExpandTrafficKeys`，跟入第4、第5个参数，两个都会进入一个`NcryptSslKey`结构（BDDD结构），与TLS1.2中一样，`pNcryptSslKey`包含了指向密钥结构体地址的指针

![1611740525_6011356de27225f1dc090.png!small?1611740526370](https://image.3001.net/images/20210127/1611740525_6011356de27225f1dc090.png!small?1611740526370)

跟入偏移0x10（x64，x86中为0x0C），进入了SSL3结构体，而不是TLS1.2中的TLS5结构体。见1第73页。

![1611740547_60113583c7879813810cb.png!small?1611740548232](https://image.3001.net/images/20210127/1611740547_60113583c7879813810cb.png!small?1611740548232)

![1611740567_60113597b28c7b02e6b75.png!small?1611740568490](https://image.3001.net/images/20210127/1611740567_60113597b28c7b02e6b75.png!small?1611740568490)

SSL3结构指向RUUU结构，而RUUU结构又指向MSKY结构，而MSKY结构最终指向我们要找的secrets。

偏移0x20（x64，x86下为0x1C）包含指向RUUU Bcrypt Key结构体的指针

![1611740585_601135a936619e9478be1.png!small?1611740585613](https://image.3001.net/images/20210127/1611740585_601135a936619e9478be1.png!small?1611740585613)

阅读mimikatz源代码42可以找到RUUU结构

    
    
    typedef struct _KIWI_BCRYPT_HANDLE_KEY {
    ULONG size;
    ULONG tag;  // 'UUUR'
    PVOID hAlgorithm;
    PKIWI_BCRYPT_KEY key;
    PVOID unk0;
    } KIWI_BCRYPT_HANDLE_KEY, *PKIWI_BCRYPT_HANDLE_KEY;
    

在偏移0x10（x64，x86为0x0C）出跟入指针进入到MKSY结构

![1611740603_601135bb8e2692d0b3bdf.png!small?1611740603943](https://image.3001.net/images/20210127/1611740603_601135bb8e2692d0b3bdf.png!small?1611740603943)

在偏移0x10处包含密钥的长度，会根据密钥算法的不同而变化，在偏移0x18处包含我们需要的密钥。

![1611740620_601135ccccc52e0a27d26.png!small?1611740621279](https://image.3001.net/images/20210127/1611740620_601135ccccc52e0a27d26.png!small?1611740621279)

第一调用产生的是 **HANDSHAKE_TRAFFIC_SECRET** ，第二次调用产生的是 **TRAFFIC_SECRET_0**

### SslExpandExporterMasterKey

对于TLS1.3，还要额外hook`SslExpandExporterMasterKey`。虽然目前不确定wireshark目前是否需要使用它，但是openssl的keylog函数确实把它打印到keylog中了。

![1611740643_601135e38b33d7f89b847.png!small?1611740643925](https://image.3001.net/images/20210127/1611740643_601135e38b33d7f89b847.png!small?1611740643925)

跟入第4、第5个参数进入BDDD结构，剩下的步骤和`SslExpandTrafficKeys`一样。

![1611740675_6011360353ee87fc48c78.png!small?1611740675727](https://image.3001.net/images/20210127/1611740675_6011360353ee87fc48c78.png!small?1611740675727)

到最后获得 **EXPORT_SECRET**

## 参考

> [1] Jacob M. Kambic. Cunning With CNG: Soliciting Secrets from Schannel -> [Whitepaper from DEFCON
> 24](https://media.defcon.org/DEF%20CON%2024/DEF%20CON%2024%20presentations/DEF%20CON%2024%20-%20Jkambic-> Cunning-With-Cng-Soliciting-Secrets-From-Schannel-WP.pdf), [Slides from
> BlackHat USA
> 2016](https://www.blackhat.com/docs/us-16/materials/us-16-Kambic-Cunning-> With-CNG-Soliciting-Secrets-From-SChannel.pdf), [“Extracting CNG TLS/SSL
> artifacts from LSASS memory” by Jacob M.
> Kambic](https://docs.lib.purdue.edu/open_access_theses/782/)
>
> [2] MDN: [NSS Key Log Format](https://developer.mozilla.org/en-> US/docs/Mozilla/Projects/NSS/Key_Log_Format)
>
> [3] OpenSSL man page:
> [SSL_CTX_set_keylog_callback](https://www.openssl.org/docs/man1.1.1/man3/SSL_CTX_set_keylog_callback.html)
>
> [4] Wireshark source code: [SSLKEYLOG parsing, wireshark/packet-tls-> utils.c](https://github.com/wireshark/wireshark/blob/master/epan/dissectors/packet-> tls-utils.c#L5355)
>
> [5] Microsoft Docs: [Key Storage and
> Retrieval](https://docs.microsoft.com/en-us/windows/win32/seccng/key-> storage-and-retrieval)
>
> [6] Microsoft Docs: [Cryptography API: Next
> Generation](https://docs.microsoft.com/en-us/windows/win32/seccng/cng-> portal)
>
> [7] StackExchange: [Decryping TLS packets between Windows 8 apps and
> Azure](https://reverseengineering.stackexchange.com/a/213)
>
> [8] StackExchange: [Is it possible to decrypt an SSL connection (short of
> bruteforcing)?](https://reverseengineering.stackexchange.com/a/2695)
>
> [9] Choi, H., & Lee, H. (2016) [Extraction of TLS master secret key in
> windows. 2016 International Conference on Information and Communication
> Technology Convergence
> (ICTC)](https://ieeexplore.ieee.org/document/7763558). The paper is
> available on sci-hub if you search for its DOI.
>
> [10] Microsoft TechNet Forums: [Obtaining SSLKEYLOGFILE-like data from Edge
> et al (Schannel clients)](https://social.technet.microsoft.com/Forums/en-> US/4041d78a-21bb-44fd-9a96-6579ea8129d1/obtaining-sslkeylogfilelike-data-> from-edge-et-al-schannel-clients)
>
> [11] GitHub - NytroRST/NetRipper: [Smart traffic sniffing for penetration
> testers](https://github.com/NytroRST/NetRipper)
>
> [12] Filippo Valsorda: [We need to talk about Session
> Tickets](https://blog.filippo.io/we-need-to-talk-about-session-tickets/)
>
> [13] Microsoft Docs: [SslGenerateMasterKey function
> (Sslprovider.h)](https://docs.microsoft.com/en-> us/windows/win32/seccng/sslgeneratemasterkey)
>
> [14] Microsoft Docs: [Header Annotations](https://docs.microsoft.com/en-> us/windows/win32/winprog/header-annotations)
>
> [15] GitHub - droe/sslsplit: [Transparent SSL/TLS
> interception](https://github.com/droe/sslsplit)
>
> [16] Microsoft Docs: [x64 software
> conventions](https://docs.microsoft.com/en-us/cpp/build/x64-software-> conventions)
>
> [17] MS .NET Reference Source: [NCryptBuffer
> structure](https://referencesource.microsoft.com/#system.core/System/Security/Cryptography/NCryptNative.cs,258b810a8a142eb5,references)
>
> [18] Windows SDK: [NCRYPTBUFFER_SSL_* constans in
> ncrypt.h](http://www.gaclib.net/CodeIndexDemo/Gaclib/ncrypt.h.html)
>
> [19] The blog of a gypsy engineer: [How does TLS 1.3 protect against
> downgrade attacks?](https://blog.gypsyengineer.com/en/security/how-does-> tls-1-3-protect-against-downgrade-attacks.html)
>
> [20] RFC 5246: [The Transport Layer Security (TLS) Protocol Version
> 1.2](https://tools.ietf.org/html/rfc5246.html)
>
> [21] Frida: [A world-class dynamic instrumentation
> framework](https://frida.re/)
>
> [22] Microsoft Docs: [x64 stack usage](https://docs.microsoft.com/en-> us/cpp/build/stack-usage?view=vs-2019)
>
> [23] Microsoft Docs: [Secure Channel](https://docs.microsoft.com/en-> us/windows/win32/secauthn/secure-channel)
>
> [24] Microsoft Docs: [SSP Packages Provided by
> Microsoft](https://docs.microsoft.com/en-us/windows/win32/secauthn/ssp-> packages-provided-by-microsoft)
>
> [25] Wikipedi@: Forward Secrecy
> (https://en.wikipedi@.org/wiki/Forward_secrecy把@改成a)
>
> [26] Microsoft Docs: [SslImportMasterKey function
> (Sslprovider.h)](https://docs.microsoft.com/en-> us/windows/win32/seccng/sslimportmasterkey)
>
> [27] RFC 7627: [Transport Layer Security (TLS) Session Hash and Extended
> Master Secret Extension](https://tools.ietf.org/html/rfc7627)
>
> [28] Microsoft Docs: [SslHashHandshake function
> (Sslprovider.h)](https://docs.microsoft.com/en-> us/windows/win32/seccng/sslhashhandshake)
>
> [30] Microsoft: [News on TLS1.3 experimental support in Windows
> 10](https://docs.microsoft.com/en-us/windows/whats-new/whats-new-> windows-10-version-1909#transport-layer-security-tls)
>
> [31] GitHub - microsoft/msquic: [Testing
> instructions](https://github.com/microsoft/msquic/blob/master/docs/TEST.md)
>
> [32] IETF draft: [Using TLS to Secure
> QUIC](https://tools.ietf.org/html/draft-ietf-quic-tls)
>
> [33] GitHub - microsoft/msquic: [SCHANNEL TLS Implementation for
> QUIC](https://github.com/microsoft/msquic/blob/master/src/platform/tls_schannel.c)
>
> [34] RFC 8446: [The Transport Layer Security (TLS) Protocol Version
> 1.3](https://tools.ietf.org/html/rfc8446)
>
> [35] GitHub - dotnet/runtime: [TLS1.3 does not work on Windows · Issue
> #1720](https://github.com/dotnet/runtime/issues/1720)
>
> [36] Naughter blog: [SSLWrappers + TLS v1.3
> support](https://naughter.wordpress.com/2019/05/23/tls-v1-3-support-finally-> on-windows/)
>
> [37] Microsoft Docs: [InitializeSecurityContextW function
> (sspi.h)](https://docs.microsoft.com/en-us/windows/win32/api/sspi/nf-sspi-> initializesecuritycontextw)
>
> [38] Windows SDK: [SEC_TRAFFIC_SECRETS definition in
> ntifs.h](https://www.codemachine.com/downloads/win10.1903/ntifs.h)
>
> [39] Windows SDK: [SECBUFFER_TRAFFIC_SECRETS definition in
> sspi.h](https://github.com/susahom/YC/blob/d00467cf2682143e216acf29d4e7b1c350c319ec/Windows%20Kits/10/Include/10.0.18362.0/shared/sspi.h#L375)
>
> [40] RFC 5705: [Keying Material Exporters for Transport Layer Security
> (TLS)](https://tools.ietf.org/html/rfc5705)
>
> [41] Peter Wu: [sslkeylog.c for keylogging apps that use
> OpenSSL](https://git.lekensteyn.nl/peter/wireshark-notes/tree/src)
>
> [42] GitHub - gentilkiwi/mimikatz: [kuhl_m_crypto_extractor.c - a TODO line
> which mentions MSKY magic
> tag](https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/crypto/kuhl_m_crypto_extractor.c#L419))

SSL Magic| Size（x86）| Size（x86）| Function  
---|---|---|---  
ssl1| 0xE4| 0x139| SslpValidateProvHandle  
ssl2| 0x24| 0x30| SslpValidateHashHandle  
ssl3| ?| ?| < none >  
ssl4| 0x18| 0x20| SslpValidateKeyPairHandle  
ssl5| 0x48| 0x50| SslpValidateMasterKeyHandle  
ssl6| 0x18| 0x20| SslpValidateEphemeralHandle  
ssl7| ?| ?| < none >

