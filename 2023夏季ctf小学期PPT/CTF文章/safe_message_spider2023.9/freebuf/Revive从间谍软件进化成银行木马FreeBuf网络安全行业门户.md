2022 年 6 月，Cleafy 研究人员发现了一个新的安卓银行木马 Revive。之所以选择 Revive
这个名称，是因为恶意软件为防止停止工作启用的一项功能名为 `revive`。

Revive 属于持续潜伏的那一类恶意软件，因为它是为特定目标开发和定制的。这种类型的恶意软件与其他 Android 银行木马各有异同，例如 TeaBot
或 SharkBot 它们都能够同时通过模块化架构攻击安装在受感染设备上的多个银行/加密应用程序。

Revive 的攻击方法与其他银行木马也是相似的，它仍然滥用 Accessibility Services
来执行键盘记录并拦截受害者的短信。这些功能就足以执行帐户接管攻击（ATO），因为此时恶意软件即可获得登录凭据和银行通过短信发送的双因子认证。

到目前为止，发现的两个 Revive 样本的杀软检出率都非常低。如图所示，第二个样本的检出率甚至为零。

![image.png-117.7kB](https://image.3001.net/images/20220701/1656664136_62beb048e7169f245d407.png!small)样本检出情况

## 技术分析

![image.png-394.9kB](https://image.3001.net/images/20220701/1656664137_62beb049cf3083503d1b5.png!small)钓鱼网站

与其他银行木马类似，Revive 也使用不同的社会工程学技巧伪装成合法应用程序，误导受害者。Revive
的恶意样本也是通过钓鱼网站进行投递的，隐藏在目标银行的新版双因子验证应用程序之后。

受害者下载了恶意软件，Revive 尝试通过弹出窗口获取辅助服务功能，用于监视和窃取受害者设备的信息。

![image.png-135.4kB](https://image.3001.net/images/20220701/1656664139_62beb04b297dedf74ac85.png!small)Revive
安装

受害者首次打开恶意软件时，Revive 要求提供短信与电话相关的两项权限。之后一个假冒的银行页面就会展示给受害者，如下所示。受害者输入凭据后，会被发送到
C&C 服务器中，之后恶意软件会将受害者重定向到合法网站。

![image.png-239.5kB](https://image.3001.net/images/20220701/1656664139_62beb04bdd21adfd47f74.png!small)凭据回传

Revive 的开发人员应该是从开源在 GitHub 上的名为 Teardroid 的窃密恶意软件修改而来，因为二者之间的程序与 C&C
的基础架构存在很多相似性。

![image.png-561.2kB](https://image.3001.net/images/20220701/1656664141_62beb04d0d571db30d571.png!small)开源
Teadroid 项目

Teardroid 是拥有很多功能的窃密恶意软件，而 Revive 删除了 Teadroid 的一些功能，并在为其添加了新功能，转向了银行木马的功能。

![image.png-1028.6kB](https://image.3001.net/images/20220701/1656664142_62beb04e22bf6842b556e.png!small)Teadroid
和 Revive 比较

其 C&C 基础设施基于 FastAPI，这是一个 Python 的 RESTful API 的开发框架。除此之外，攻击者还定制了 Teadroid
的控制面板，支持银行木马的对应功能。

下图显示了在调查分析时发现的一些相似之处：

![image.png-882.7kB](https://image.3001.net/images/20220701/1656664143_62beb04f63c248679b51e.png!small)C&C
相似性

银行木马 Revive 主要具备三个能力：

> 窃取登录凭据。通过滥用辅助服务，可以向用户显示虚假页面并记录键盘击键。
>
> 拦截受感染设备收到的所有短信，目的是获取通过短信发送给用户的双因子认证。
>
> 获取用户在设备上写入的所有内容（例如凭据、消息、电话号码等，如下所示）。这些信息保存在本地数据库中并发送回 C&C 服务器。

![image.png-321.9kB](https://image.3001.net/images/20220701/1656664144_62beb05055794d8a322ba.png!small)窃密信息回传

![image.png-352.7kB](https://image.3001.net/images/20220701/1656664145_62beb051699e910604b59.png!small)键盘记录

## 结论

现在已经有很多流行的 Android 银行木马，如 SharkBot、TeaBot 或
Oscorp/UBEL，这些恶意软件都具备很多功能、相对复杂。Revive
似乎是小型定制攻击行动，这可能更加难以拦截。这些恶意软件很多都是全新的，安全产品难以检测，而且攻击只会存在数天。研究人员尚不清楚 Revive
未来会如何演进，毕竟该恶意软件还处于早期阶段，攻击者仍能够通过各种方式对其进行改进。

## IOC

> 4240473028f88a3ef54f86f1cd387f24  
> cf704e63652c23c2d609e9a01659511c  
> 80.85.153.49  
> bbva.appsecureguide.com  
> bbva.european2fa.com

## 参考来源

> [Cleafy](https://www.cleafy.com/cleafy-labs/revive-from-spyware-to-android-> banking-trojan)

