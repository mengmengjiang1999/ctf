![](https://image.3001.net/images/20200212/1581499546_5e43c49ac4915.jpg!small)

**作者在测试Facebook的近期推出的某个新应用中（出于保密原因此处不便公开），存在跨站Websocket
Hijacking漏洞，攻击者利用该漏洞可以劫持使用该新应用的用户Websocket
连接，之后构造恶意的Websocket信息，可实现对目标受害者的Facebook账号劫持。**

因为该项Facebook新近推出的应用还处于测试阶段，只有少数安全人员可以受邀进行访问测试，所以以下漏洞解释中已对应用名称进行了隐匿，且暂不提供相关的漏洞利用代码。

##  漏洞原因

由于该项Facebook新近推出的应用托管在facebook.com的子域名之下，并允许其本地IP地址（如0.0.0.1/8 或
192.168.1.1/8）包含成为Origin主机头，该应用基于随机数的安全登录（随机数在登录页面中生成然后在后续的某个websocket消息中被发送验证），随机数用于建立获取有效的websocket连接会话，这里并不依赖Cookie信息进行用户身份验证。

但当测试授权机制的另一个bug时，我发现了一个变化，按之前的分析来看，授权机制也应该用随机数来验证登录，但此处却开始用了用户的Facebook全局Cookie来验证用户身份。

以下为用Facebook内部的本地IP地址成功构造为Origin主机头建立的Websocket连接：

![](https://image.3001.net/images/20200212/1581499447_5e43c4373b9a3.png!small)综上分析来看，由于Origin主机头仅允许本地IP地址，因此与受害者在同一本地网段的攻击者可构造恶意Websocket连接，通过DNS欺骗（Spoofing）或点对点发送给受害者，实现对受害者Facebook的账号劫持。

另外，也可以在受害者手机中的安装恶意APP来启动无权限限制的HTTP服务，然后向受害者同网段的其他IP地址的Facebook用户发送经过构造的deep-link形式的恶意URL链接，实现扩大化攻击。

##  漏洞复现

1、为了更好的说明利用，我访问REDACTED.facebook.com，然后保存主页，这里要连同其中处理websocket通信的Javascript脚本文件一起保存。因为Websocket通信消息是加密的，且这里的Javascript脚本文件是经过编码的，有些难懂，且在后续的攻击利用中要用到其中一些稍作修改的Javascript脚本文件。之后，我用包含这些修改的Javascript脚本文件启动了一个HTTP服务；

2、利用上述启动的http服务，我向同一网段的受害者发送了一个恶意链接之后，其中涉及的脚本会与REDACTED.facebook.com服务端建立起一个Websocket连接，然后会在登录阶段的身份验证时需要用到用户的Cookie信息（由于Websocket不受限于SOP或CORS策略，所以这对本地IP来说是可行的）

3、作为POC测试，受害者在访问了上述包含有本地IP的恶意链接之后，就会看到自己成功登录到了Facebook账户，而在Javascript脚本文件中，却包含了一个攻击Payload，可以当受害者登录成功后向攻击者发送一个特定的websocket，以进行Facebook账户的绑定邮箱或手机号的添加，以此实现对受害者Facebook账户的劫持。该攻击针对安卓手机APP用户亲测有效，iOS中未测试过。

##  漏洞上报和处理进程

> 2019.12.10 漏洞初报
>
> 2019.12.10 Facebook确定漏洞有效
>
> 2019.12.17 Facebook修复漏洞
>
> 2020.1.2 Facebook奖励了 12,500$

***参考来源：[ysamm](https://ysamm.com/?p=363)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

  

