## **01 背景**

微软从2020年开始陆续修复了一系列Print Spooler服务中的漏洞，这些修复有时候也会影响到正常的打印功能。

到2021年10月，问题开始变得严重起来，大量安装了10月补丁的Windows 10用户发现他们不能正常的使用网络打印机了。

最常见的问题是在添加网络打印机时操作失败，错误提示“Windows无法连接到打印机”。在安装补丁之前已经添加好的网络打印机，也很可能在使用过程中碰到各种的错误。常见的错误代码有0x000006e4
、0x0000007c、0x00000709等。

![1640596240_61c98310d2be1b578bde0.png!small?1640596244302](https://image.3001.net/images/20211227/1640596240_61c98310d2be1b578bde0.png!small?1640596244302)

2021年11月的补丁并没有修复Windows 10的问题，而之前还正常的Windows 11在安装了11月补丁之后也开始出现了同样的问题。

![1640596254_61c9831eb4c2628673fe8.png!small?1640596258304](https://image.3001.net/images/20211227/1640596254_61c9831eb4c2628673fe8.png!small?1640596258304)

因此，本文对该问题的本质原因进行了分析，并尝试给出一个临时的解决方案。

##  **02** 原因分析

网事不决问Wireshark，先抓个包来看一下：

![1640596273_61c9833191b2c9f83879e.png!small?1640596275875](https://image.3001.net/images/20211227/1640596273_61c9833191b2c9f83879e.png!small?1640596275875)

这里的12号报文引起了注意：

![1640596282_61c9833a250b7cb89ede5.png!small?1640596284530](https://image.3001.net/images/20211227/1640596282_61c9833a250b7cb89ede5.png!small?1640596284530)

报文类型为Fault（3）说明之前请求的操作失败了，状态为nca_s_fault_access_denied（0x00000005）说明失败的原因是拒绝访问。

因为该报文是对之前的9号报文的响应，而9号报文的报文类型为AUTH3（16）说明是一个认证请求，所以这里的问题是RPC调用的认证失败了。

为什么认证会失败呢？来看看9号报文中的NTLM Secure Service Provider信息：

![1640596296_61c983486fc996834e841.png!small?1640596301358](https://image.3001.net/images/20211227/1640596296_61c983486fc996834e841.png!small?1640596301358)

从Domain name、User name、Host
name可以看出，这里用来认证的凭据是当前登录的本地用户的，而不是登录到打印机服务器时所用的凭据。通常情况下，本地用户的凭据对打印机服务器来说是无效的，因此这里的认证会失败。

那么为什么这里会用当前登录的本地用户来认证呢？要回答这个问题，需要先弄清楚为什么这里会进行一次认证。

从抓包来分析，客户端之所以会发出进行认证的9号报文，是因为服务端在8号报文中发起了NTLMSSP CHALLENGE：

![1640596312_61c9835831b64a422d7a7.png!small?1640596314641](https://image.3001.net/images/20211227/1640596312_61c9835831b64a422d7a7.png!small?1640596314641)

而服务端发起NTLMSSP CHALLENGE则是因为客户端在5号报文中附加了NTLMSSP NEGOTIATE：

![1640596323_61c98363f14f6b474eed3.png!small?1640596325892](https://image.3001.net/images/20211227/1640596323_61c98363f14f6b474eed3.png!small?1640596325892)

因此，这里的认证应该是在RPC Binding过程中发起的。考虑到其他的RPC调用并无此现象，只有网络打印相关操作会进行此认证，问题可能出在RPC
Binding的回调函数中。

网络打印相关的操作在win32spl.dll中实现，RPC调用NdrClientCall3的第一实参通常是winspool_ProxyInfo，这是一个MIDL_STUBLESS_PROXY_INFO类型的对象，从中可以定位到RPC
Binding的回调函数为STRING_HANDLE_bind。

![1640596340_61c983749114c4dbc0ac4.png!small?1640596343668](https://image.3001.net/images/20211227/1640596340_61c983749114c4dbc0ac4.png!small?1640596343668)

在函数STRING_HANDLE_bind的末尾，调用RpcBindingFromStringBindingW函数进行Binding之后，增加了一个对RpcBindingSetAuthInfoExW函数的调用：

![1640596350_61c9837e8cd372ad93958.png!small?1640596351999](https://image.3001.net/images/20211227/1640596350_61c9837e8cd372ad93958.png!small?1640596351999)

在安装10月补丁之前是没有这一调用的：

![1640596358_61c98386320677b195be9.png!small?1640596358812](https://image.3001.net/images/20211227/1640596358_61c98386320677b195be9.png!small?1640596358812)

正是这里对RpcBindingSetAuthInfoExW函数的调用，使得RPC调用的过程中会再进行一次认证，而这次认证会因为使用了本地用户的凭据而失败，从而使RPC调用失败，进而使得网络打印相关的操作无法正常进行。

##  **03** 解决方案

找到了问题的根本原因后，解决起来就很简单了。既然问题是由对RpcBindingSetAuthInfoExW函数的调用引起的，而安装10月补丁之前并没有这一调用，说明该调用并不是必须的，那么可以尝试跳过该函数来看一看。

对spoolsv.exe进程进行调试，将对RpcBindingSetAuthInfoExW函数的调用修改为空指令（注意这里需要将寄存器eax中的返回值清零）：

![1640596368_61c983900a8e5d77f2c40.png!small?1640596369954](https://image.3001.net/images/20211227/1640596368_61c983900a8e5d77f2c40.png!small?1640596369954)

此时再尝试添加网络打印机就可以顺利完成了，相关功能也都能正常使用了。

![1640596381_61c9839ddf7b44bedbd3c.png!small?1640596383819](https://image.3001.net/images/20211227/1640596381_61c9839ddf7b44bedbd3c.png!small?1640596383819)

微软在2021年11月22日发布的预览版补丁中修复了该问题。

![1640596389_61c983a58f81c0d7bbbe5.png!small?1640596390240](https://image.3001.net/images/20211227/1640596389_61c983a58f81c0d7bbbe5.png!small?1640596390240)

Windows 10的预览版补丁是KB5007253：

![1640596397_61c983adf39fa61a2bf14.png!small?1640596400923](https://image.3001.net/images/20211227/1640596397_61c983adf39fa61a2bf14.png!small?1640596400923)

Windows 11的预览版补丁是KB5007262：

![1640596408_61c983b81be5ea6738739.png!small?1640596410815](https://image.3001.net/images/20211227/1640596408_61c983b81be5ea6738739.png!small?1640596410815)

该补丁的处理思路跟前述解决方案是一致的，在调用RpcBindingSetAuthInfoExW函数之前，先调用IsAuthenticationRequiredForNamedPipeRpc函数来判断是否需要调用，只在特定情况下才调用该函数。

![1640596416_61c983c0359c354e58f3e.png!small?1640596417332](https://image.3001.net/images/20211227/1640596416_61c983c0359c354e58f3e.png!small?1640596417332)

IsAuthenticationRequiredForNamedPipeRpc函数根据是否加入了域分情况进行处理。在加入了域的情况下，如果RpcNamedPipeAuthentication注册表项不等于2，并且设置了RpcAuthnLevelPrivacyEnabled注册表项，则返回True。在没有加入域的情况下，如果RpcNamedPipeAuthentication注册表项等于1，则返回True。其他情况下一律都返回False。

![1640596426_61c983ca1ed040cedce04.png!small?1640596427903](https://image.3001.net/images/20211227/1640596426_61c983ca1ed040cedce04.png!small?1640596427903)

这样，在之前网络打印会出现问题的环境中，IsAuthenticationRequiredForNamedPipeRpc函数将会返回False，从而跳过对RpcBindingSetAuthInfoExW函数的调用，进而避免因为认证失败而无法进行网络打印的相关操作，临时的解决网络打印机不能正常工作的问题。

##  **04** 总结

微软2021年10月的补丁，在错误的Context中调用RpcBindingSetAuthInfoExW函数，使得网络打印相关的RPC调用因认证失败而无法执行，从而导致网络打印机不能正常工作。

跳过对RpcBindingSetAuthInfoExW函数的调用，可以临时解决该问题。

微软2021年11月的预览版补丁修复了该问题，预计12月的补丁将可以正式解决该问题。

