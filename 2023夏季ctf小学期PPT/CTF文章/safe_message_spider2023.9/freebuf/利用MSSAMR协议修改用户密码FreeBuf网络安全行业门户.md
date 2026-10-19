> 本文为Windows RPC利用系列文章的第一篇，主要介绍关于MS-SAMR的部分利用，在后续的文章中将继续介绍RPC在渗透测试中的应用

在渗透测试过程中，经常遇到拿到用户的NTLM哈希但无法解密出明文密码的情况。本文介绍并分析一种在仅知道域用户密码哈希时修改用户密码，并在使用完后恢复用户原密码的方法。完成相应工具实现，提出检测方法和缓解措施。

PS：本文提出的场景在实战中也有很多其他的解决办法，但本文仅讨论与changentlm、setntlm相关的内容

## 0x00 利用

考虑以下几个场景：

我们拿下域控后，经常要搜集目标架构内用户的各种信息来寻找靶标，比如登录邮箱服务器、OA、NAS等可能使用域身份认证的系统

我们收集的攻击路径中的其中一环是利用某账户重置/修改目标账户密码

我们拿到某用户hash后，同样想通过该用户账户登录某系统，但目标系统不支持pth

我们虽然拿到了修改/重置密码的权限，但我们又不想直接修改目标用户的密码，因为这样用户在登录时就会发现自己的密码被修改了，此时有两种情况：

如果我们有重置密码权限就可以使用`SetNTLM`来将用户密码重置

如果有hash的话可以使用`ChangeNTLM`修改

登录目标系统后，再将目标密码还原

### 1\. SetNTLM

该功能的效果是直接将域用户的密码或hash重置为新的密码或hash

(1) 利用条件

当前身份对要修改的用户有`Reset Password`权限![Alt
text](https://image.3001.net/images/20210819/1629345961_611dd8a98636c0ba6af84.png!small)

(2) Demo

假设我们此时拿到域控，想修改域内用户`ntlmtest`的密码来登录某系统，先Dcsync看一下用户当前的hash：

![Alt
text](https://image.3001.net/images/20210819/1629345974_611dd8b6aedf5f8a02082.png!small)

由于我们是域管了，基本上对目标用户都是有重置密码权限的，然后利用以下命令重置密码：

    
    
    lsadump::setntlm /server:<DC's_IP_or_FQDN> /user:<username> /password:<new_password>

![Alt
text](https://image.3001.net/images/20210819/1629345987_611dd8c3ab6cf5a5167ff.png!small)

登录目标系统以后，再通过以下命令还原密码：

    
    
    lsadump::setntlm /server:<DC's_IP_or_FQDN> /user:<username> /ntlm:<Original_Hash>

![Alt
text](https://image.3001.net/images/20210819/1629346000_611dd8d004f4751a6d532.png!small)

### 2\. ChangeNTLM

(1) 利用条件

需要对目标用户有`Change Password`权限，但该权限一般是`Everyone`拥有的，所以基本上拿到目标用户的hash/密码后都可以进行密码更改

![Alt
text](https://image.3001.net/images/20210819/1629346013_611dd8dddacd3a2162cd4.png!small)

（注意此处的更改密码权限并不是说可以直接任意改用户密码，而是在知道用户的密码的情况下更改一个新密码）

该方法受到域内密码策略的限制，比如域内默认的 **“密码最短使用期限”** 为1天，因此用户每天只能修改一次自己的密码

而且如果域内存在 **“强制密码历史”** 规则时，该方法在恢复原密码时便不能成功，但如果没有 **“密码最短使用期限”**
的限制的话，我们多修改几次密码直到原密码在历史中清除，然后再修改为原密码即可

![Alt
text](https://image.3001.net/images/20210819/1629346027_611dd8eb46b5d4aa04a61.png!small)

(2) Demo

修改用户test2密码：

    
    
    lsadump::changentlm /server:<DC's_IP_or_FQDN> /user:<username> /old:<current_hash> /newpassword:<newpassword>

![Alt
text](https://image.3001.net/images/20210819/1629346040_611dd8f881d4dc0792da3.png!small)

恢复原密码：

    
    
    lsadump::changentlm /server:<DC's_IP_or_FQDN> /user:<username> /oldpassword:<current_password_plain_text> /new:<original_hash>

![Alt
text](https://image.3001.net/images/20210819/1629346052_611dd904e947f4249383a.png!small)

## 0x01 原理

ChangeNTLM和SetNTLM的原理本质都是调用[MS-SAMR](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-samr/4df07fab-1bbc-452f-8e92-7853a3c7e380)协议

不同的是ChangeNTLM是调用`SamrChangePasswordUser`这一API来修改用户密码：

![Alt
text](https://image.3001.net/images/20210819/1629346066_611dd912ac3644adc3b7c.png!small)

而SetNTLM是通过`SamrSetInformationUser`来重置用户密码

![Alt
text](https://image.3001.net/images/20210819/1629346081_611dd9216ca917c33df1f.png!small)

大体过程是差不多的，只不过核心操作调用API不同，这也是为什么两种方法需要的参数、权限都不同，此处以分析ChangeNTLM为例

虽然原理本质是通过调用RPC，但mimikatz并不是直接调用RPC来修改，而是使用了一组以`Sam`开头的API，下图所示为部分API：

[Mimikatz -kuhl_m_lsadump.c#L2267](https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/kuhl_m_lsadump.c#L2267)

![Alt
text](https://image.3001.net/images/20210819/1629346094_611dd92edfc5e481586f2.png!small)

最终调用`SamiChangePasswordUser`来修改用户的密码

[Mimikatz -kuhl_m_lsadump.c#L2171](https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/kuhl_m_lsadump.c#L2171)

![Alt
text](https://image.3001.net/images/20210819/1629346115_611dd9432925b6e292154.png!small)

这些API由samlib.dll导出：

![Alt
text](https://image.3001.net/images/20210819/1629346124_611dd94c94c69c0ce1ae6.png!small)

查看`SamiChangePasswordUser`函数调用树，可以看到调用了`NdrClientCall3`，是不是很熟悉？这明显是进行RPC调用的标志（xpn在他的文章[exploring-mimikatz-part-2](https://blog.xpnsec.com/exploring-mimikatz-part-2/)里有提到过）

![Alt
text](https://image.3001.net/images/20210819/1629346138_611dd95ac513585bee2fe.png!small)

我们再看一下调用处的反编译代码，参数刚好可以和`SamrChangePasswordUser`的操作数对应

![Alt
text](https://image.3001.net/images/20210819/1629346197_611dd995bbaad95661020.png!small)

其实从流量中也可以看出调用的是MS-SAMR协议：

![Alt
text](https://image.3001.net/images/20210819/1629346211_611dd9a3b852711e78dc2.png!small)

## 0x02 实现

实现主要有两种思路，一种是跟mimikatz一样直接调用samlib.dll的导出函数，第二种是直接调用SAMR协议的API

两种方法原理一样，但前者的调用要更加简单，因为samlib里的导出函数对应了SAMR的API，其实相当于SAMR的上层实现，比如`SamiChangePasswordUser`对应`SamrChangePasswordUser`，并且参数更加简化

整个过程调用的API作用如下：

 **SamrConnect5** : 获取Server对象的句柄

 **SamrEnumerateDomainsInSamServer** : 枚举Server上的域名

 **SamrLookupDomainInSamServer** : 获取域名对应域的SID

 **SamrOpenDomain** : 获取Domain对象的句柄

 **SamrLookupNamesInDomain** : 获取指定用户的RID

 **SamrOpenUser** : 获取User对象的句柄

 **SamrChangePasswordUser** : 修改用户对象的密码

### 1\. 调用samlib的导出函数

原理前面已经提过了，直接调用samlib.dll里对应的导出函数即可，直接嫖参考mimikatz的源码即可实现，[源码戳这里](https://github.com/loong716/CPPPractice/tree/master/Set_ChangeNTLM)

### 2\. 直接调用MS-SAMR

这里以实现changentlm为例，setntlm同理

(1) C语言

微软官方已经把MS-SAMR的IDL给我们了：[[MS-SAMR] - Appendix A: Full
IDL](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-samr/1cd138b9-cc1b-4706-b115-49e53189e32e)，直接拿下来使用midl生成.h和.c文件即可（使用时还需要稍作修改）：

![Alt
text](https://image.3001.net/images/20210819/1629346231_611dd9b7b7dd95b2f69c8.png!small)

注意这里有一个坑点，如果对`SamrChangePasswordUser`只指定第5、6、7个参数的话，会产生`STATUS_LM_CROSS_ENCRYPTION_REQUIRED`错误：

![Alt
text](https://image.3001.net/images/20210819/1629346316_611dda0cc2766950f7319.png!small)

因此必须再指定`LMCross`和`NewLmEncryptedWithNewNt`这两个参数，而后者是用新密码的NTLM Hash加密新密码的LM
Hash得到的，这里我一开始很疑惑：从mimikatz的功能来看，并不需要我们传递新密码LM Hash，那么它这个加密操作是怎么完成的呢？

由于LM Hash早已在高版本Windows中弃用，于是我猜测这个LM
Hash可能跟新密码并没有关系（比如有些工具需要使用`LMHASH:NTHASH`的格式来指定hash，但LM
Hash的值是多少并没有关系），于是我直接使用新密码的NTLM Hash来加密空密码对应的LM Hash：

    
    
    ...  
    unsigned char newLM[16];  
    PCWCHAR newLMHash = "AAD3B435B51404EEAAD3B435B51404EE";  
    StringToHex(newLMHash, newLM, sizeof(newLM));  
    status = RtlEncryptLmOwfPwdWithLmOwfPwd(newLM, newNT, &NewLMEncryptedWithNewNT);  
    if (!NT_SUCCESS(status))  
    {  
    wprintf(L"[!] Calc NewLMEncryptedWithNewNT Error: %08X\n", status);  
    exit(1);  
    }  
    ...

最终成功修改目标用户的密码，Demo实现效果如下，[源码戳这里](https://github.com/loong716/CPPPractice/tree/master/ChangeNTLM_SAMR)

![Alt
text](https://image.3001.net/images/20210819/1629346246_611dd9c63953fc8d02251.png!small)

(2) Impacket

既然是调用RPC，而且刚好impacket对SAMR协议也有实现，所以也可以用impacket来写

完成后我向impacket项目提交了[Pull
Request](https://github.com/SecureAuthCorp/impacket/pull/1097)，源码可以在commit中看到

效果如下，修改用户的密码：

![Alt
text](https://image.3001.net/images/20210819/1629346259_611dd9d38e22aaa022f7e.png!small)

恢复用户原hash：

![Alt
text](https://image.3001.net/images/20210819/1629346333_611dda1d0de5fdf5e78d9.png!small)

## 0x03 检测与缓解

### 1\. ChangeNTLM

(1) 产生事件

ChangeNTLM会产生4723、4738两条日志，并且日志中的使用者和目标账户并不是同一个账户：

![Alt
text](https://image.3001.net/images/20210819/1629346344_611dda28c2cf0c5d8da5c.png!small)

![Alt
text](https://image.3001.net/images/20210819/1629346356_611dda34bdbd7f6df2f3c.png!small)

(2) 流量特征

在`SamrOpenUser`这个操作中（操作数为34），`Samr User Access Change
Password`标志位被设置为1，在该步操作中还可以看到用户对应的RID：

![Alt
text](https://image.3001.net/images/20210819/1629346368_611dda4015a001525dd2d.png!small)

以及调用`SamrChangePasswordUser`（操作数为38）：

![Alt
text](https://image.3001.net/images/20210819/1629346380_611dda4c26842d9579eae.png!small)

### 2\. SetNTLM

(1) 产生事件

SetNTLM会产生4724、4661、4738这三条日志：

![Alt
text](https://image.3001.net/images/20210819/1629346395_611dda5b1783092256b82.png!small)

![Alt
text](https://image.3001.net/images/20210819/1629346409_611dda69c4b3c44c90142.png!small)

![Alt
text](https://image.3001.net/images/20210819/1629346423_611dda77951e9bb9d4d59.png!small)

(2) 流量特征

同样在`SamrOpenUser`这个操作中（操作数为34），`Samr User Access Set
Password`标志位被设置为1，也可以看到用户对应的RID：

![Alt
text](https://image.3001.net/images/20210819/1629346438_611dda8637fba1e3bc686.png!small)

调用`SamrSetUserInformation`（操作数为37）:

![Alt
text](https://image.3001.net/images/20210819/1629346454_611dda9651956696b731f.png!small)

### 3\. 缓解措施

对于ChangeNTLM，我们可以通过设置域内密码策略来增大攻击者的利用难度：

“密码最短使用期限” >= 1天

“强制密码历史” >= 5个

而对于SetNTLM，基本是攻击者拿到较高权限时才会进行的操作，因此主要靠我们前期的一些态势感知来检测攻击者的行为，即使其拿到高权限，我们也可以通过事件迅速检测出SetNTLM行为

## 0x04 参考

<https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-samr/4df07fab-1bbc-452f-8e92-7853a3c7e380>

<https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/kuhl_m_lsadump.c#L2165>

<https://stealthbits.com/blog/manipulating-user-passwords-with-mimikatz/>

作者: Loong716@Amulab

