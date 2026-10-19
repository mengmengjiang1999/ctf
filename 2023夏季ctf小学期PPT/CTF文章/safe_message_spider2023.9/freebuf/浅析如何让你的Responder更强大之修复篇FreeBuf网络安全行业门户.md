## 前言

**渗透圈内，Responder声名远扬。去年在使用中发现了一些异常，脑子抽筋，读了smb协议和Responder源码，进而发现了Responder在实现上存在的一些问题，然后进行了修复和完善，趁着这几天有时间，进行了简单整理和分析，分享出来，希望对大家有所帮助。**

 _ ****原标题：Make your Responder stronger_ ****

我们先看两张图片

![1574348646_5dd6a7663c3cb.png!small](https://image.3001.net/images/20191121/1574348646_5dd6a7663c3cb.png!small)

图1

![1574348684_5dd6a78c6be4f.png!small](https://image.3001.net/images/20191121/1574348684_5dd6a78c6be4f.png!small)

图2

图1是我从Responder官方（其实是非官方，你懂的）GitHub（<https://github.com/lgandx/Responder>）上找到的一段话，大致意思：支持抓去NTLMv1，NTLMv2
Hash，并成功的在Windows 95 到Server 2012 RC等机器上测试，而且内建并支持了SMBv2。

图2是我在responder的配置文件截的图，大致是说：开启CaptureMultipleCredentials，可让Responder发送ACCOUNT_DISABLED当客户端想向服务器认证时，然后尝试抓去多个hash值。（这个配置从源码上看只适用于SMB1）

大家看懂了吧，那就先别下，等我说完，然后去我GitHub上<https://github.com/wreck1t/Responder>下载，因为他在骗你：

1.内建的SMBv2实现存在缺陷，在与某些常用SMB客户端交互时无法正常工作，更别提捕获Hash了。

2.CaptureMultipleCredentials开启，在与某些常用SMB客户端交互时，SMBv1也只能抓到一次Hash。

由于SMB客户端的多样性和不同客户端实现的复杂性，本文以net
use客户端为例，对Responder实现的SMBv1和SMBv2存在的问题进行解析，并进行修复。

作为一名医学生------逻辑一般，文采不行，文章难免存在纰漏之处，欢迎大家批评指正。

## 二.背景知识

### 1.Responder

由Laurent Gaffie撰写的Responder是迄今为止，在每个渗透测试人员用于窃取不同形式的凭证（包括Net-NTLM
hash）的最受欢迎的工具。它通过污染LLMNR和NBT-NS等主机解析请求，从而欺骗目标主机与其实现的恶意服务器通信，从而达到设置恶意浏览器代理，窃取凭证等目的。当网络上的设备尝试用LLMNR和NBT-NS请求来解析目的地机器时，Responder就会伪装成目的地机器。当受害者机器尝试登陆攻击者机器，responder就可以获取受害者机器用户的Net-NTLM哈希值。

### 2.SMB工作流程

2.1.首先客户端发送一个SMB negotiate protocol request请求数据报，并列出它所支持的所有SMB协议版本，如图3中No
20所示：

2.2.服务器收到请求信息后响应请求SMB2 negotiate protocol response，并列出希望使用的协议版本。如图3中 No
24所示：（明眼的同学发现中间有几个包略过了，别急，咱一会再说）

2.3.协议确定后，客户端进程使用磋商好的版本向服务器发起认证以获得访问权限。

2.4.服务器发送一个Session setup response应答数据包允许或（附带拒绝的原因）拒绝本次连接。

注：2.3和2.4的认证涉4步（NTLM认证的内容），讲起来内容比较多，网上资料也比较多，我的任务是介绍流程，让大家对SMB不太陌生。

![1574345404_5dd69abcbedd5.png!small](https://image.3001.net/images/20191121/1574345404_5dd69abcbedd5.png!small)

图3

### 3.NTLM认证（挑战响应机制）

## 三.实验环境：

> Windows 7 （默认支持smb1 smb2） ip：172.20.10.8
>
> Windows XP （默认只支持smb1） ip：172.20.10.7
>
> kali （默认自带Responder） ip：172.20.10.6

## 四.实验详情：

### 1.先说SMBv1：

1.1. 同时开启Windows
XP和Kali，配置Kali中Responder配置文件，路径：/usr/share/responder/Responder.conf。设置CaptureMultipleCredentials=On，这也是responder的默认设置，设置完成后，在终端输入responder
-I eth0，开启responder进行Hash捕获，

1.2. 来到XP，在cmd下输入net use
\\\cfca回车（当用户不输入账号密码时，windows会使用当前的用户的账号密码尝试NTLM认证，如果认证失败，客户端会要求用户输入账号密码重新认证
----这是正常流程，按照正常流程，我们是会认证两次，而responder也会捕获两次Hash。）

1.3 windows 提示：账户被禁用，然后终止，kali也只捕获到一次hash。如图4图5所示

![1574353488_5dd6ba500d27b.png!small](https://image.3001.net/images/20191122/1574353488_5dd6ba500d27b.png!small)

图4

![5.jpg](https://image.3001.net/images/20200106/1578296321_5e12e4011c9f9.jpg!small)

图5

说好的捕获多次呢，骗人。我们来看一下WireShake抓包的情况，如图6:

![1574354247_5dd6bd47bacea.png!small](https://image.3001.net/images/20191122/1574354247_5dd6bd47bacea.png!small)

就像配置文件里说的，responder返回了ACCOUNT_DISABLED"\x72\x00\x00\xc0"的响应 ，没问题啊。

为什么会出现这种情况呢？

这要归咎于SMB客户端的复杂性，不同的SMB客户端可能是由不同的团队实现。ACCOUNT_DISABLED"\x72\x00\x00\xc0"对于某些SMB客户端会导致客户端重新认证，而net
use实现SMB客户端收到ACCOUNT_DISABLED"\x72\x00\x00\xc0"的数据包，会将认证状态打印到屏幕上，然后中断正常的再次认证流程。

经过查阅资料和实验，我们可以将它改为PASSWORD_EXPIRED
"\x71\x00\x00\xc0"，因为它有更好的兼容性（其实能改的值很多，比如LOGON_FAILURE
"\x6d\x00\x00\xc0"，我们这里用PASSWORD_EXPIRED "\x71\x00\x00\xc0"），客户端会进行再次认证。

1.4 回到kali，打开终端，输入vi /usr/share/responder/servers/SMB.py.作如下图7更改

![1574354830_5dd6bf8e28bb8.png!small](https://image.3001.net/images/20191122/1574354830_5dd6bf8e28bb8.png!small)

图7

1.5 删掉Responder.db，重启Responder.回到windows xp重新认证。你会发现，哈哈哈，成功了！如图8图9

![1574355107_5dd6c0a3d8677.png!small](https://image.3001.net/images/20191122/1574355107_5dd6c0a3d8677.png!small)

图8

![6.jpg](https://image.3001.net/images/20200106/1578296454_5e12e48601e52.jpg!small)

图9

### 2.再来SMBv2:

2.1 同时开启Windows 7和Kali，启动Responder，然后windows 7 系统cmd下net use
\\\cfca.你会发现什么也抓不到，只进行了对LLMNR解析的响应。又要如图，，，如图10 图11

![1574356075_5dd6c46b14158.png!small](https://image.3001.net/images/20191122/1574356075_5dd6c46b14158.png!small)

图10

![1574356098_5dd6c4823c283.png!small](https://image.3001.net/images/20191122/1574356098_5dd6c4823c283.png!small)

图11

来，我们分析一下WireShark抓到的包。

![1574356333_5dd6c56d50f89.png!small](https://image.3001.net/images/20191122/1574356333_5dd6c56d50f89.png!small)

图12

如图12所示，客户端正常进行了认证（No 2945，No 2946，No
2947），只是responder未对客户端进行响应，所以造成了客户端出现“system error 64 ”错误，但理论上，net-ntlm
hash已经到达服务器了，最少也要解析一次吧，不然多浪费。

本着不浪费的与原则，我迅速在代码中定位到了该数据包（No 2947）的代码，如图13，而包含hash的包的MessageID抓包结果是3.如图14

![1574357032_5dd6c828194d7.png!small](https://image.3001.net/images/20191122/1574357032_5dd6c828194d7.png!small)

图13

![1574357290_5dd6c92a8f2c5.png!small](https://image.3001.net/images/20191122/1574357290_5dd6c92a8f2c5.png!small)

图14

是不是以为改为3，就完了？

那你就单纯了

我们应该做的是把' and GrabMessageID(data)[0:1] == "\x02"删掉。

为什么这么做呢？来来来，协议的东西，还是让微软大大告诉你吧，如图15

![屏幕快照 2020-01-06
下午2.06.01.png](https://image.3001.net/images/20200106/1578292132_5e12d3a4317da.png!small)

图15

大致意思是说，SMB2支持两种Negotiate：Multi-Protocol Negotiate和SMB2-only
Negotiate。他们的不同是：Multi-Protocol Negotiate支持多版本SMB，而SMB2-only Negotiate只支持SMB2。

当使用Multi-Protocol Negotiate时，包含hash的数据包ID为3；使用MB2-only
Negotiate时，包含hash的数据包ID为2.

微软在实现在支持多版本的SMB客户端时，首先会用Multi-Protocol
Negotiate进行协商，一旦确定服务器和客户端共同支持的SMB版本（假设是SMB2）后，后续认证才会用SMB2-only
Negotiate。为什么这样做？兼容性 兼容性 兼容性，重要的事情说三遍，愣头青才会上来就用SMB2-only
Negotiate。想想我微软大大也不会这么干。

所以无论是等于2还是等于3，都会有问题产生。删掉便成为我能想到的最好的策略。

我们来看看改后SMBv2的效果，该图16图17：

![1574357917_5dd6cb9da5a99.png!small](https://image.3001.net/images/20191122/1574357917_5dd6cb9da5a99.png!small)

图16

![7.jpg](https://image.3001.net/images/20200106/1578296564_5e12e4f429501.jpg!small)

图17

2.2 洗洗睡吧，我去睡了，再见

## 五.参考材料

> 1.<https://github.com/lgandx/Responder>
>
>
> 2.<https://3gstudent.github.io/3gstudent.github.io/Windows%E4%B8%8B%E7%9A%84%E5%AF%86%E7%A0%81hash-> NTLM-hash%E5%92%8CNet-NTLM-hash%E4%BB%8B%E7%BB%8D/>
>
> 3.<https://docs.microsoft.com/en-us/openspecs/windows_protocols/MS-> WINPROTLP/e36c976a-6263-42a8-b119-7a3cc41ddd2a>
>
> 4.<https://support.microsoft.com/zh-cn/help/2696547/detect-enable-disable-> smbv1-smbv2-smbv3-in-windows-and-windows-server>
>
> 5.<https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-> smb2/a9d8e20e-00d0-45ec-bf8b-ad2c1ac2d805>

 ***本文原创作者：Wreck1t，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

