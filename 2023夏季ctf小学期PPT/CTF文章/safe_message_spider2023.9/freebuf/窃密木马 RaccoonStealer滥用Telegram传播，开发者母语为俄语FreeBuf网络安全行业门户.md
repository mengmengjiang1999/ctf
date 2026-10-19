Raccoon Stealer 是一个窃密木马，使用 Telegram 作为基础设施来存储和更新实际 C&C 地址。

Raccoon Stealer 具备的典型功能如下所示：

> 浏览器 Cookie、登录信息与表单数据
>
> 电子邮件客户端和即时通信软件的登陆凭据
>
> 加密钱包
>
> 浏览器插件和扩展数据
>
> 来自 C&C 的任意文件

Raccoon Stealer 在地下论坛积极推广并且持续开发维护，十分危险。最早的样本来自 2019
年四月，同月在地下论坛开始销售。根据作者的描述，后来的更新都是为了修复错误与追加功能。

## 分发

已经发现 Raccoon Stealer 通过 Buer Loader 和 GCleaner 进行分发。还有一些通过破解软件进行传播。由于 Raccoon
Stealer 是销售的，分销方式花样百出只受到想象力的限制。有些样本直接传播，有些样本使用 Themida 进行加壳，甚至有的样本连续加了五层壳。

## 技术细节

Raccoon Stealer 使用 C/C++ 通过 Visual Studio 开发，样本大小约为 580-600
kB。其代码质量低于平均水平，有些字符串加密了，有些没有。

执行后，Racoon Stealer 会检查区域设置。如果是以下地区，就不执行工作：

> 俄罗斯
>
> 乌克兰
>
> 白俄罗斯
>
> 哈萨克斯坦
>
> 吉尔吉斯斯坦
>
> 亚美尼亚
>
> 塔吉克斯坦
>
> 乌兹别克斯坦

## C&C 通信

样本中有四个值对 C&C 通信至关重要，这些值都是硬编码的：

> MAIN_KEY：在一年中修改了四次
>
> URLs：带有频道名的 Telegram Gate
>
> BotID：十六进制字符串
>
> TELEGRAM_KEY：解密从 Telegram Gate 获得的 C&C 地址的密钥

样本的基本过程如下所示：

首先通过 `MAIN_KEY`解密，解密代码如下所示：

![image.png-182.1kB](https://image.3001.net/images/20220315/1647353917_6230a03d0fefe3640db6f.png!small)解密代码

该样本中的 `MAIN_KEY`是 `jY1aN3zZ2j`，该密钥用于解密 Telegram GatesURLs 和 BotID。

接着解密 Telegram Gate URL，样本中为
`Rf66cjXWSDBo1vlrnxFnlmWs5Hi29V1kU8o8g8VtcKby7dXlgh1EIweq4Q9e3PZJl3bZKVJok2GgpA90j35LVd34QAiXtpeV2UZQS5VrcO7UWo0E1JOzwI0Zqrdk9jzEGQIEzdvSl5HWSzlFRuIjBmOLmgH/V84PCRFevc40ZuTAZUq+q1JywL+G/1xzXQdYZiKWea8ODgaN+4B8cT3AqbHmY5+6MHEBWTqTsITPAxKdPMu3dC9nwdBF3nlvmX4/q/gSPflYF7aIU1wFhZxViWq2`。

首先通过 base64 进行解码：

![image.png-170.8kB](https://image.3001.net/images/20220315/1647353918_6230a03e0fc33957dc221.png!small)解码

在利用 MAIN_KEY 使用 RC4 算法进行解密，得到 Telegram Gates 的字符串：

![image.png-78.9kB](https://image.3001.net/images/20220315/1647353918_6230a03e8fff44af5d207.png!small)解密

通过请求 Telegram Gate，利用返回的 HTML 页面获取真正的 C&C 地址。

![image.png-47.4kB](https://image.3001.net/images/20220315/1647353919_6230a03f25c0bc9ef9ca7.png!small)页面内容

页面显示了一个 Telegram 频道名称与另外一串字符串。将五个字符的前缀和六个字符的后缀删除，再通过 base64 解码获取加密的 C&C 地址：

![image.png-19.7kB](https://image.3001.net/images/20220315/1647353919_6230a03f7f6790f71b94b.png!small)加密地址

该样本的 `TELEGRAM_KEY`为 `739b4887457d3ffa7b811ce0d03315ce`，将其作为 RC4 的密钥进行解密可得到
`http://91.219.236.18/`。

通过机器 GUID 与用户名生成字符串作为 BotID，经过 RC4 加密再 base64 编码后通过 POST 请求发送给 C&C 服务器。响应也经过
base64 编码，其实为一个 JSON 文件，如下所示：

![image.png-1366.3kB](https://image.3001.net/images/20220315/1647353919_6230a03fe35fb68e841da.png!small)响应内容

将 Telegram 作为基础设施存放和更新 C&C 服务器的地址，在 Telegram 决定封杀滥用行为前都很方便可靠。

## 幕后黑手

根据地下论坛的信息，推断运营软件的相关信息。Raccoon Stealer 是由一个团队开发的，
**该团队的一些（或可能全部）成员都是以俄语为母语的人。论坛上的消息是用俄语写的，并且样本会阻止 Raccoon Stealer
以前苏联加盟国家为目标执行。**

通过样本可以推测成员名字：

> C:\Users\a13xuiop1337\
>
> C:\Users\David\

## 感染率

从 2021 年三月到 2022 年二月，系统监测到超过 25000 个 Raccoon Stealer 样本，配置超过 1300 种。

拦截样本的部分国家如下所示：

![image.png-165.1kB](https://image.3001.net/images/20220315/1647353924_6230a0442d37bba12cd47.png!small)国家统计

俄罗斯被拦截的最多，实际上样本即使执行也不会进行感染的。

![image.png-129kB](https://image.3001.net/images/20220315/1647353924_6230a044dcdb5d27cd85b.png!small)声明截图

## Telegram

发现的 1300 个不同的配置中，有 429 个使用的是独立的 Telegram 频道。有些只在单个配置中出现，有些出现了很多次。最常见的是：

> jdiamond13 – 122 次
>
> jjbadb0y – 44 次
>
> nixsmasterbaks2 – 31 次
>
> hellobyegain – 25 次
>
> h_smurf1kman_1 – 24 次

这五个最常见的频道大概占了 19%。

## Raccoon Stealer

Raccoon Stealer 通过 C&C 服务器下载的恶意文件一共收集到了 185 个，大体主要几类：

> Downloaders – 用于下载和执行其他文件
>
> Clipboard crypto stealers – 在剪贴板中修改加密钱包地址）
>
> WhiteBlackCrypt Ransomware - 勒索软件

## 下载服务器

指向其他恶意软件的链接一共有 196 个，其中：

> 43% 使用的是 HTTP，57% 使用的 HTTPS
>
> 一共使用了 83 个域名
>
> 20% 的恶意软件部署在 Discord CDN
>
> 10% 与 aun3xk17k.space 有关

## 结论

Raccoon Stealer 将来可能会被其他网络犯罪组织更广泛地使用，并且可以预见的是 Raccoon Stealer
背后的团队将进一步开发新功能，例如用于窃取数据的新软件，以及绕过安全防护软件保护措施的技术等。

## IOC

> 447c03cc63a420c07875132d35ef027adec98e7bd446cf4f7c9d45b6af40ea2b  
> f1cfcce14739887cc7c082d44316e955841e4559ba62415e1d2c9ed57d0c6232

## 参考来源

> [Avast](https://decoded.avast.io/vladimirmartyanov/raccoon-stealer-trash-> panda-abuses-telegram/)

