**作者：Yuebin Sun**  
**原文链接：<https://rekken.github.io/>**

## 摘要

新冠病毒疫情出不了门，在家办公这两周笔者研究了一下 macOS 的 Security Framework。

本文主要分析 Security Framework 尤其是其中 Keychain 的架构，将 Security Framework
近一两年的历史漏洞做个整理。

## Security Framework 简介

Security Framework 主要负责为 App 提供认证与授权、安全数据存储与传输（Keychain，App Transport
Security）、代码签名、加密解密功能。

第三方 App 通过引用 Security Framework，使用 Apple 提供的 API 就可以直接使用这些功能，不用关心底层实现的细节。

![Image](https://images.seebug.org/content/images/2020/04/14/1586836376000-1dnuvs.png-w331s)

但 Security Framework 都有哪些组件，又是如何构建起来的呢？

官方最近已经不再更新整体的架构图了，在 [Mac OS X Internals] 书里找到了一张整体架构图，目前来看重要组件的变化不是特别大，可以用来参考

![Image](https://images.seebug.org/content/images/2020/04/14/1586836395000-2nayyn.png-w331s)

## Keychain

Keychain 是 Security Framework 的重要组件，系统中保存的 WiFi 密码、Safari 保存的网站密码等都由 Keychain
组件负责管理。

Keychain 最早在 Mac OS 8.6 版本被引入，用于保存邮件系统（PowerTalk）的邮件服务器的登录凭据。现在的 Keychain
组件已经扩展了很多，可用于保存密码、加密密钥、证书以及 Notes，被 Apple 自身以及众多第三方应用使用。

![Image](https://images.seebug.org/content/images/2020/04/14/1586836398000-3fpzhb.png-w331s)

iOS 与 macOS 系统中的 Keychain 略微有些差异，iOS 中只有一个 Keychain，设备解锁状态时 Keychain
可以访问，设备锁定状态时 Keychain 也处于锁定状态。macOS 则不同，macOS 系统允许用户自己创建任意的 Keychain
用于私有使用，Security Framework 提供了 SecKeychain{Create, Delete, Open，…} API 用于 macOS
用户管理 Keychain。

默认状态下，macOS 系统中存在两个 Keychain:

  * ~/Library/Keychains/login.keychain-db
  * /Library/Keychains/System.keychain

其中 login Keychain 在 macOS 解锁状态时就会被解密，`System.keychain`密钥保存在
`/var/db/SystemKey`，只有 root 用户可以访问。

具体目前系统中保存的 Keychain 以及存储的信息列表可以通过 macOS 的 Keychain Access.app 应用访问并查看。

### 如何用 Keychain 存储一个网站密码

Apple 官网文档如下示例代码可以实现向 Kaychain 中存储一个网站的密码。

    
    
    static let server = "www.example.com"
    let account = credentials.username
    let password = credentials.password.data(using: String.Encoding.utf8)!
    var query: [String: Any] = [kSecClass as String: kSecClassInternetPassword,                            kSecAttrAccount as String: account,                                          kSecAttrServer as String: server,                                            kSecValueData as String: password]
    let status = SecItemAdd(query as CFDictionary, nil)

其中核心的就是 SecItemAdd 这个 API，接下来我们将一步步分析这个 API 是如何实现的。

抽象的看，保存在 query 变量中的数据通过 SecItemAdd API 传递给 Keychain Service，服务进一步会将 query
数据封装为 Keychain Item，对于其中的 password 则会被加密，Keychain Item 进一步会被保存到磁盘的 Keychain
Database。

![Image](https://images.seebug.org/content/images/2020/04/14/1586836400000-4qmlgf.png-w331s)

如果从组件的角度看，SecItemAdd API 由 Security 共享库（Security Framework 的一部分，此处为了与 Security
Framework
作区分所以叫共享库，`/System/Library/Frameworks/Security.framework/Versions/A/Security`）实现，Security
共享库会被加载进当前 App 进程，SecItemAdd API 收到数据后，进一步通过 SECURITYD_XPC 宏，将 API 调用转发至
`com.apple.securityd.xpc XPC`服务，该服务位于 secd 进程，secd 以当前用户身份运行。

![Image](https://images.seebug.org/content/images/2020/04/14/1586836422000-5pmvvg.png-w331s)

![Image](https://images.seebug.org/content/images/2020/04/14/1586836425000-6vsjro.png-w331s)

进入 secd 进程之后，会根据 operation 进入到服务消息分发
handler（securityd_xpc_dictionary_handler）（代码已被精简）,对于 SecItemAdd，operation 为
sec_item_add_id，保存新增数据的 query 会被直接传递给 `_SecItemAdd`， 除了 query 还有重要的数据结构
SecurityClient 结构体，SecurityClient 用于在后续的数据处理流程中支持访问控制检查，其中的 accessGroups 用于实现在
Web（Safari）和同一个团队开发的 App 之间共享密码，核心就是 Web 与 App 通过 Associated Domains
Entitlement 关联，感兴趣可以参考 [Supporting Associated Domains in Your
App](http://developer.apple.com/documentation/safariservices/supporting_associated_domains_in_your_app?language=objc
"Supporting Associated Domains in Your App")

    
    
    static void securityd_xpc_dictionary_handler(const xpc_connection_t connection, xpc_object_t event) 
    SecurityClient client = {
        .task = NULL,
        .accessGroups = NULL, 
        .musr = NULL,
        .uid = xpc_connection_get_euid(connection),
        .allowSystemKeychain = false,
        .allowSyncBubbleKeychain = false,
        .isNetworkExtension = false,
        .canAccessNetworkExtensionAccessGroups = false,
    };
    fill_security_client(&client, xpc_connection_get_euid(connection), auditToken));
    switch (operation)
    {
       case sec_item_add_id:
       {           
          _SecItemAdd(query, &client, &result, &error) && result);                     break; 
          }       
          // ...   
          }

`_SecItemAdd`内部就会将 query 数据转化为 Sqlite 的数据库增、删、改、查操作，最终实现对我们传递 query 的 item
插入操作。插入 `sqlite3` 的数据，password 会被加密。同时为了支持搜索，其他一些非私密数据会保持明文，这样可以支持对 `keychain`
数据库条目的搜索。至此 SecItemAdd API 新增网站密码的流程就结束了。

    
    
    static CFStringRef SecDbItemCopyInsertSQL(SecDbItemRef item, bool(^use_attr)(const SecDbAttr *attr)) {
        CFMutableStringRef sql = CFStringCreateMutable(CFGetAllocator(item), 0);     CFStringAppend(sql, CFSTR("INSERT INTO "));    CFStringAppend(sql, item->class->name);
        CFStringAppend(sql, CFSTR("("));
        bool needComma = false;
        CFIndex used_attr = 0;
        SecDbForEachAttr(item->class, attr) { 
            if (use_attr(attr)) {
                ++used_attr;
                SecDbAppendElement(sql, attr->name, &needComma);
                } 
         }
         CFStringAppend(sql, CFSTR(")VALUES(?")); 
         while (used_attr-- > 1) {  
               CFStringAppend(sql, CFSTR(",?"));
         }  
         CFStringAppend(sql, CFSTR(")")); 
         return sql;
         }

Safari 保存的这部分网站密码会被保存到 login keychain 数据库中，login keychain 等用户注销或者关机等操作时会被加密锁定。

## SecurityServer 与 SecurityAgent

系统的 login Keychain 在系统处于解锁状态时就会自动解锁，所以上面保存网站密码时并没有涉及 keychain 的解密或解锁过程。

然而对于 System Keychain 或者时自己创建的 Keychain，这就涉及到 Keychain 数据库的加解锁、加解密处理，此时就需要
Security Server 的参与。

`Security Server(/usr/sbin/securityd)` 是一个 root 身份独立运行的 daemon
服务进程，如最上面的整体架构图所示，CDSA 架构中，Security Server 为 CDSA 架构提供了 `CSP/DL
Plugin`，即负责数据的安全加密与存储。

Security Server 通过 ucsp MIG 接口提供服务，用于 client 访问 SecurityServer
内部对象。普通用户进程就可以访问此 MIG 接口。从源码中看这个服务提供了以下功能：

  * 管理请求 Security Server 的 clients（session、connection）
  * 认证(Authentication)和授权(Authrization)的管理
  * Keychain 数据库的管理，包括锁定、解锁、数据加密、数据库的创建与修改
  * 数据签名（Signature）的生成和验证
  * 数据的加密和解密（ucsp_server_encrypt， ucsp_server_decrypt)
  * Key、key pair 的生成（ucsp_server_generateKey， ucsp_server_generateKeyPair、ucsp_server_wrapKey， ucsp_server_unwrapKey）
  * Code Signing Hosting(近几天公开的 10.15 版本源码中已经删除相关接口，暂未深入确认)

可以看出 root 身份运行的 Security Server(securityd)
提供了很多高权限的敏感操作，同时也管理着大量敏感数据，因此如果可以发现这个服务进程的漏洞，那么影响也将非常大，KeySteal
就是利用该服务的漏洞实现无需密码验证访问 Keychain 保存的密码。

那么如何通过 MIG 接口与他交互呢？

在 Security 的源码中就包含了这个 ucsp MIG 接口的定义文件(OSX/libsecurityd/mig/ucsp.defs)。但很可惜，介绍
MIG 使用的文档很少，直接访问 Security Server 的文档更是没有。最终，我从 Linus Henze 写的 [KeySteal
Exploit](https://github.com/LinusHenze/Keysteal) 代码中精简了一个访问 ucsp_server_setup
接口的 Client。

通过 mig 命令行工具生成 ucspUser.c 以及 ucspServer.c
接口定义源码，解决完编译依赖的头文件定义之后，就可以通过如下的示例测试代码访问 ucsp_server_setup 接口。

    
    
    #define UCSP_ARGS    gServerPort, gReplyPort, &securitydCreds, &rcode
    #define ATTRDATA(attr) (void *)(attr), (attr) ? strlen((attr)) : 0
    
    #define CALL(func) \
        security_token_t securitydCreds; \
        CSSM_RETURN rcode; \
        if (KERN_SUCCESS != func) \
            return errSecCSInternalError; \ 
        if (securitydCreds.val[0] != 0) \
            return CSSM_ERRCODE_VERIFICATION_FAILURE; \
        return rcode#
    define SSPROTOVERSION 20000
    
    mach_port_t gServerPort;
    mach_port_t gReplyPort;
    
    CSSM_RETURN securityd_setup() { 
        mach_port_allocate(mach_task_self(), MACH_PORT_RIGHT_RECEIVE, &gReplyPort);    
        mach_port_insert_right(mach_task_self(), gReplyPort, gReplyPort, MACH_MSG_TYPE_MAKE_SEND);
        bootstrap_look_up(bootstrap_port, (char*)"com.apple.SecurityServer", &gServerPort);
        ClientSetupInfo info = { 0x1234, SSPROTOVERSION };
        CALL(ucsp_client_setup(UCSP_ARGS, mach_task_self(), info, "?:unspecified"));
    }
    
    int main(int argc, char *argv[])
    {
        mach_port_t port;
        mach_port_t bootstrap_port;
        task_get_bootstrap_port(mach_task_self(), &bootstrap_port);  
        kern_return_t kr = bootstrap_look_up(bootstrap_port,"com.apple.SecurityServer", &port); 
        securityd_setup();
        return 0;
    }

### SecurityAgent

上面的介绍中提到，Security Server 还负责认证(Authentication)和授权(Authroization)。

![Image](https://images.seebug.org/content/images/2020/04/14/1586836429000-7stqbn.png-w331s)

当 Client 请求 Security Server
发起认证(Authentication)和授权(Authroization)验证时。如果需要与用户交互（输入密码）以验证身份，Security Server
就会通过 XPC 与 Security Agent（当前用户身份运行）通信，由 Security Agent 负责弹框与用户交互。用户输入的密码凭据信息由
Security Server 接收并管理，Client 只会收到验证或授权结果的消息。这个保证整个验证过程中 Client
不会接触密码等敏感信息，同时，这种机制也可以保证如果系统增加新的身份验证或鉴权扩展时，对 client 是透明的。

![Image](https://images.seebug.org/content/images/2020/04/14/1586836433000-8kmayu.png-w331s)

## 10.14 版本至今的历史漏洞分析

了解完了上面的一些必要的系统架构内容外，我们来继续看看 macOS 10.14 版本至今的涉及 Security
框架的漏洞，方便读者朋友了解漏洞的原理以及漏洞所在的组件。

需要说明的是，因为 Apple
官方在每次漏洞修复后并不会提供漏洞的详细信息，所以以下这些都是我根据源码自己分析整理的，这也意味着整理的结果可能不一定正确，如果您发现有错误或疏漏，请不吝指出。

### CVE-2019-8604（10.14.5 版本修复）

通过对比两个版本之间的源码，发现 CVE-2019-8604 漏洞的补丁。

这个漏洞在 securityd(Security Server Daemon) 中，securityd 提供的 MIG 接口在处理 client 端传递的
dbname 时，只有 assert 检查，而 assert 在 Release 版本是不存在的，因此，client 传递一个超长的字符串（长度超过
PATH_MAX)，ucsp_server_getDbName 接口就会触发 memcpy 内存越界拷贝。

    
    
    --- a/Security-58286.251.4/securityd/src/transition.cpp
    +++ b/Security-58286.260.20/securityd/src/transition.cpp
    
    +static void checkPathLength(char const *str) {
    +    if (strlen(str) >= PATH_MAX) {
    +        secerror("SecServer: path too long");
    +        CssmError::throwMe(CSSMERR_CSSM_MEMORY_ERROR);
    +    }
    +}
    +
    
    @@ -306,15 +313,16 @@ kern_return_t ucsp_server_getDbName(UCSP_ARGS, DbHandle db, char name[PATH_MAX])
    {  
            BEGIN_IPC(getDbName) 
            string result = Server::database(db)->dbName();
    -       assert(result.length() < PATH_MAX);
    +       checkPathLength(result.c_str());
            memcpy(name, result.c_str(), result.length() + 1);   
    
            END_IPC(DL)
    }
    
    kern_return_t ucsp_server_setDbName(UCSP_ARGS, DbHandle db, const char *name)
    {
            BEGIN_IPC(setDbName)
    +       checkPathLength(name);
            Server::database(db)->dbName(name);
            END_IPC(DL)
    }

补丁中，在 `ucsp_server_{get, set}DbName`中新增对路径名字的检查（checkPathLength），防止超长的 dbName
溢出固定长度（PATH_MAX）的 name。

因为`std::string` 与 `strlen`都会被且仅能被 `“\0”`截断，所以 `setDbName` 与 `getDbName`
的处理方式就一致了。

### CVE-2019-8520 （10.14.4 版本修复）

通过对比两个版本之间的源码，发现了 CVE-2019-8520 漏洞的补丁。

该漏洞位于 `Security Server Daemon(securityd)` 中，`securityd（root）` 负责处理系统中的管理系统中的
Authroization 和 Authentication，认证或者授权过程中，如果需要与用户交互（输入密码）以验证身份，securityd 就会通过
XPC 与 Security Agent（当前用户身份运行）通信，由 Security Agent 负责弹框与用户交互。

这个漏洞就出现在 securityd 与 Security Agent 的交互过程，securityd 在接收来自 Security Agent
的数据时，通过 XPC 传入 data，data 的长度为 length，另外通过另一个字段传入 sensitivelength，拷贝的时候，从 data
的起始位置拷贝长度为 sensitivelength 的内容到新创建的 dataCopy，因此，如果传入一个超长的
sensitivelength，超过上面传入的 data 的实际长度，将导致 data 的越界拷贝，会越界读取 data 变量之后的内存。

    
    
    --- a/Security-58286.240.4/securityd/src/agentquery.cpp
    +++ b/Security-58286.251.4/securityd/src/agentquery.cpp
    
    static void xpcArrayToAuthItemSet(AuthItemSet *setToBuild, xpc_object_t input) {
        setToBuild->clear();
    
        xpc_array_apply(input,  ^bool(size_t index, xpc_object_t item) {
            const char *name = xpc_dictionary_get_string(item, AUTH_XPC_ITEM_NAME);
    
            size_t length;
            const void *data = xpc_dictionary_get_data(item, AUTH_XPC_ITEM_VALUE, &length); 
            void *dataCopy = 0;
    
            // <rdar://problem/13033889> authd is holding on to multiple copies of my password in the clear  
            bool sensitive = xpc_dictionary_get_value(item, AUTH_XPC_ITEM_SENSITIVE_VALUE_LENGTH);
            if (sensitive) {
               size_t sensitiveLength = (size_t)xpc_dictionary_get_uint64(item, AUTH_XPC_ITEM_SENSITIVE_VALUE_LENGTH);+
               if (sensitiveLength > length) {+
                 secnotice("SecurityAgentXPCQuery", "Sensitive data len %zu is not valid", sensitiveLength);+  
                 return true;+ 
                 }           
                 dataCopy = malloc(sensitiveLength); 
                 memcpy(dataCopy, data, sensitiveLength); 
                 memset_s((void *)data, length, 0, sensitiveLength); // clear the sensitive data, memset_s is never optimized away
                 length = sensitiveLength;
             } else { 
                dataCopy = malloc(length);
                memcpy(dataCopy, data, length);
             }        
             uint64_t flags = xpc_dictionary_get_uint64(item, AUTH_XPC_ITEM_FLAGS);        
             AuthItemRef nextItem(name, AuthValueOverlay((uint32_t)length, dataCopy), (uint32_t)flags); 
             setToBuild->insert(nextItem); 
             memset(dataCopy, 0, length); // The authorization items contain things like passwords, so wiping clean is important. 
             free(dataCopy); 
             return true; 
        });
    }

漏洞的修复逻辑就是加了一个对 sensitiveLength 的长度检查，保证 memcpy 的长度不超过 data。

### CVE-2019-8526（10.14.4 版本修复）

通过比对代码，发现了补丁。

    
    
    --- a/Security-58286.240.4/securityd/src/child.cpp
    +++ b/Security-58286.251.4/securityd/src/child.cpp
    @@ -57,7 +57,7 @@ ServerChild::ServerChild() 
    // 
    ServerChild::~ServerChild()
    {
    - mServicePort.destroy();
    +       mServicePort.deallocate();
    
    
    --- a/Security-58286.240.4/securityd/src/clientid.cpp
    +++ b/Security-58286.251.4/securityd/src/clientid.cpp
    @@ -45,14 +45,18 @@ ClientIdentification::ClientIdentification() 
    // Initialize the ClientIdentification.
    // This creates a process-level code object for the client.
    //
    -void ClientIdentification::setup(pid_t pid)
    +void ClientIdentification::setup(Security::CommonCriteria::AuditToken const &audit) 
    {
         StLock<Mutex> _(mLock);
         StLock<Mutex> __(mValidityCheckLock);
    -    OSStatus rc = SecCodeCreateWithPID(pid, kSecCSDefaultFlags, &mClientProcess.aref());
    -       if (rc)
    -               secinfo("clientid", "could not get code for process %d: OSStatus=%d",
    -                       pid, int32_t(rc));
    +
    +    audit_token_t const token = audit.auditToken();
    +    OSStatus rc = SecCodeCreateWithAuditToken(&token, kSecCSDefaultFlags, &mClientProcess.aref());
    +
    +    if (rc) {+        secerror("could not get code for process %d: OSStatus=%d",+                audit.pid(), int32_t(rc));
    +    } 
         mGuests.erase(mGuests.begin(), mGuests.end());
         }
    
    
     --- a/Security-58286.240.4/securityd/src/csproxy.cpp
     +++ b/Security-58286.251.4/securityd/src/csproxy.cpp
     @@ -64,13 +64,12 @@ void CodeSigningHost::reset()
             case noHosting:
                  break;  // nothing to do
             case dynamicHosting:-                  mHostingPort.destroy();- 
                  mHostingPort = MACH_PORT_NULL;
    +               mHostingPort.deallocate(); 
            secnotice("SecServer", "%d host unregister", mHostingPort.port());                break;
            case proxyHosting:
            Server::active().remove(*this); // unhook service handler
    -               mHostingPort.destroy(); // destroy receive right
    +               mHostingPort.modRefs(MACH_PORT_RIGHT_RECEIVE, -1);                           mHostingState = noHosting;  
                    mHostingPort = MACH_PORT_NULL;  
                    mGuests.erase(mGuests.begin(), mGuests.end());
    
    
    --- a/Security-58286.240.4/securityd/src/process.cpp
    +++ b/Security-58286.251.4/securityd/src/process.cpp
    @@ -40,7 +40,7 @@ 
    // Construct a Process object.
    //
    Process::Process(TaskPort taskPort,    const ClientSetupInfo *info, const CommonCriteria::AuditToken &audit)
    - :  mTaskPort(taskPort), mByteFlipped(false), mPid(audit.pid()), mUid(audit.euid()), mGid(audit.egid())
    + :  mTaskPort(taskPort), mByteFlipped(false), mPid(audit.pid()), mUid(audit.euid()), mGid(audit.egid()), mAudit(audit)
    {  
         StLock<Mutex> _(*this);
         @@ -48,6 +48,11 @@ Process::Process(TaskPort taskPort,  const    ClientSetupInfo *info, const CommonCri        =parent(Session::find(audit.sessionId(), true));
         // let's take a look at our wannabe client...
    +
    +       // Not enough to make sure we will get the right process, as
    +       // pids get recycled. But we will later create the actual SecCode using
    +       // the audit token, which is unique to the one instance of the process,
    +       // so this just catches a pid mismatch early.
            if (mTaskPort.pid() != mPid) {
                    secnotice("SecServer", "Task/pid setup mismatch pid=%d task=%d(%d)",
                                     mPid, mTaskPort.port(), mTaskPort.pid());
    @@ -55,7 +60,14 @@ Process::Process(TaskPort taskPort,  const ClientSetupInfo *info, const CommonCri        
            } 
    
            setup(info);
    -       ClientIdentification::setup(this->pid());
    +       ClientIdentification::setup(this->audit_token());

这个漏洞正是之前读过 Paper 的 KeySteal 漏洞，补丁代码位于 securityd(Security Server Daemon)
，securityd 在通过 MIG 实现 Hosting Guest Code 机制时存在问题。

从补丁中可以看出漏洞存在的两个问题：

第一个是实现 Hosting Guest Code 机制，securityd 在创建 SecCode 时，错误地使用
SecCodeCreateWithPID 这个 API，这个 API 根据 pid 标识 Client Process，因此如补丁中的注释代码所说，存在
PID Reuse 的问题。

修复的方式是 SecCodeCreateWithPID 换做 SecCodeCreateWithAuditToken 用 audit token 表示
client。关于 PID 方式有何问题，可以参考之前 Samuel Gro? 的[Don’t Trust the
PID!](http://saelo.github.io/presentations/warcon18_dont_trust_the_pid.pdf)

第二个是 Mach Port 的引用计数问题，`CodeSigningHost::reset()`调用 destory() 导致强制释放 Mach
Port，被 destory 的 Mach Port 可能仍然被某些数据结构引用，同时因为用户态进程的 Mach Port 本身是 mach port
name，其实就是个 number，既然是 number 就存在被 reuse 的可能。所以，在下次使用之前如果可以导致重新被占用，就可以实现
UAF。补丁修复也很容易，就是 destory 改为引用计数版本的 deallocate()。

### CVE-2018-4400（10.14.1 版本修复）

这个漏洞 Apple 公告中的描述是处理 S/MIME 消息时拒绝服务，对比代码，得到的了疑似补丁，不敢完全确定

    
    
    --- a/Security-58286.200.222/OSX/libsecurity_smime/lib/smimeutil.c
    +++ b/Security-58286.220.15/OSX/libsecurity_smime/lib/smimeutil.c
    @@ -733,6 +733,8 @@ SecSMIMEGetCertFromEncryptionKeyPreference(SecKeychainRef keychainOrArray, CSSM_
            cert = CERT_FindCertByIssuerAndSN(keychainOrArray, rawCerts, NULL, tmppoolp, ekp.id.issuerAndSN);
         break;
            case NSSSMIMEEncryptionKeyPref_RKeyID:
    +        cert = CERT_FindCertBySubjectKeyID(keychainOrArray, rawCerts, NULL, &ekp.id.recipientKeyID->subjectKeyIdentifier);
    +        break;
         case NSSSMIMEEncryptionKeyPref_SubjectKeyID:
             cert = CERT_FindCertBySubjectKeyID(keychainOrArray, rawCerts, NULL, ekp.id.subjectKeyID);
             break;

对证书管理及相关的数据结构暂时还不太熟悉，暂时不进一步分析了

上面这些是目前我找到的比较确定的一些漏洞及其补丁，因为 Apple 开源代码非常滞后，所以上面这些主要是 10.14.版本中涉及 `Security
Framework`的漏洞的分析。

## 总结

以上就是我这段时间研究 Security Framework 并做的分享。因为 Security Framework 比较庞大，我只重点介绍了
Keychain 以及历史上被发现漏洞比较多的 Security Server 组件。其他像 Auth
组件来得及分析，等后续对这些组件有了新的研究，我将继续分享。

如果发现上面的内容有错误，或者您也对 macOS 感兴趣，欢迎联系我 [@yuebinsun](http://twitter.com/yuebinsun
"@yuebinsun")。

## References

  1. <https://developer.apple.com/documentation/security?language=objc>

  2. <https://opensource.apple.com/>

  3. <https://www.pinauten.de/resources/KeySteal_OBTS_2019.pdf>

  4. <https://en.wikipedia.org/wiki/Keychain_(software)>

  5. <https://rekken.github.io/about>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1172/>

