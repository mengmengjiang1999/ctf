## 概要

 **Juicy
Potato是一个本地特权提升工具，是[RottenPotatoNG](https://github.com/breenmachine/RottenPotatoNG)的加强版。RottenPotatoNG及其变体利用了基于在127.0.0.1:6666上具有MiTM侦听器的BITS服务，以及当你拥有SeImpersonate或SeAssignPrimaryToken权限时的特权提升链。在Windows构建审核期间，我们找到了一个设置，其中有意禁用了BITS并使用了6666端口。**

因此，我们决定武器化[RottenPotatoNG](https://github.com/breenmachine/RottenPotatoNG)。

有关更多内容，你可以参考 [Rotten Potato - 从服务帐户到SYSTEM的权限提升
](https://foxglovesecurity.com/2016/09/26/rotten-potato-privilege-escalation-from-service-accounts-to-system/)这篇文章。

我们发现除了BITS之外，还有一些我们可以滥用的COM服务器。只需满足以下条件即可：

> 可由当前用户实例化，通常是具有模拟（ impersonation）权限的“服务用户”
>
> 实现IMarshal接口
>
> 以特权用户身份运行（SYSTEM，Administrator，...）

经过一些测试，我们在几个Windows版本上获得并测试了大量[有趣的CLSID列表](https://ohpe.github.io/juicy-potato/CLSID/)。

## JuicyPotato 的功能

###  **Target CLSID**

选择你想要的任何CLSID。在这里，你可以找到多个windows版本的CLSID列表。

###  **COM Listening port**

定义你喜欢的COM侦听端口

###  **COM Listening IP address**

在任意IP上绑定服务器

###  **Process creation mode**

取决于模拟用户的权限，有以下三个选择：

> CreateProcessWithToken (需要SeImpersonate权限)
>
> CreateProcessAsUser (需要SeAssignPrimaryToken权限)
>
> both

###  **Process to launch**

如果利用成功，则启动可执行文件或脚本

###  **Process Argument**

自定义已启动的进程参数

###  **RPC Server address**

对外部RPC服务器进行身份验证

###  **RPC Server port**

如果你想要对外部服务器进行身份验证，并且防火墙阻止135端口，那么这将非常有用...

###  **TEST mode**

主要用于[测试](https://ohpe.github.io/juicy-potato/Test/)目的，即测试CLSID。

##  **使用**

    
    
    T:\>JuicyPotato.exe
    JuicyPotato v0.1
    
    Mandatory args:
    -t createprocess调用: <t> CreateProcessWithTokenW, <u> CreateProcessAsUser, <*> try both
    -p <program>: 运行程序
    -l <port>: COM服务器侦听端口
    
    
    Optional args:
    -m <ip>: COM服务器侦听地址 (默认 127.0.0.1)
    -a <argument>: 传递给程序命令行参数 (默认 NULL)
    -k <ip>: RPC服务器IP地址 (default 127.0.0.1)
    -n <port>: RPC服务器侦听端口 (default 135)
    -c <{clsid}>: CLSID (default BITS:{4991d34b-80a1-4291-83b6-3328366b9097})
    -z 仅测试CLSID并打印令牌的用户

## 截图

![Juicy
Potato本地特权提升工具](https://image.3001.net/images/20180820/1534722323_5b7a01139a3aa.png!small)

如果用户具有SeImpersonate或SeAssignPrimaryToken权限，那么你将最终提升为SYSTEM。

另外，你几乎不可能防止对所有这些COM服务器的滥用行为。你或许可以考虑通过DCOMCNFG来修改这些对象的权限，但这样做的难度非常的大。

实际的解决方案是，保护在* SERVICE帐户下运行的敏感帐户和应用程序。停止DCOM是最有效的做法，但这可能会对操作系统底层产生严重的影响。

## 相关参考

> [Rotten Potato - Privilege Escalation from Service Accounts to
> SYSTEM](https://foxglovesecurity.com/2016/09/26/rotten-potato-privilege-> escalation-from-service-accounts-to-system/)
>
> [Windows: DCOM DCE/RPC Local NTLM Reflection Elevation of
> Privilege](https://bugs.chromium.org/p/project-> zero/issues/detail?id=325&redir=1)
>
> [Potatoes and Tokens](https://decoder.cloud/2018/01/13/potato-and-tokens/)
>
> [The lonely Potato](http://decoder.cloud/2017/12/23/the-lonely-potato/)
>
> [Social Engineering the Windows Kernel by James
> Forshaw](https://www.slideshare.net/Shakacon/social-engineering-the-windows-> kernel-by-james-forshaw)

 *******参考来源：[github](https://ohpe.github.io/juicy-potato/)，** **FB小编 secist
编译，转载请注明来自FreeBuf.COM**

