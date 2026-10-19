2023 年 3 月，研究人员在 PyPI 上发现了 6 个旨在窃取 Windows
用户的应用程序凭据、个人隐私数据与加密钱包信息。本次攻击确认是对攻击团伙 W4SP 的模仿，该组织之前曾利用恶意软件包发起过多次供应链攻击。

## PyPI 中发现新的恶意软件包

研究人员发现的 6 个恶意软件包，都缺少与之关联的 GitHub
存储库。合法软件包通常都会有与之关联的存储库，而恶意软件包为了隐藏代码则通常不会关联。执行后，恶意软件包会收集敏感数据并将其发送到第三方 URL。

软件包的开发者是新创建的，只上传了一个软件包，而且没有提供任何其他信息，这通常很难说明是有信誉的开发者。这些软件包的开发者用户名都是相同的模式（如
Anne1337、Richard1337 等），每个账户都只上传了一个软件包。

后续的攻击与之前披露的 W4SP
攻击团伙类似，该组织专门利用开源生态系统中的漏洞进行攻击。不仅利用未授权访问窃取敏感信息，也利用自动化工具发起漏洞利用攻击。

## 发现

上传软件包的用户账户都是在上传软件包不久前才创建的，没有创建其他任何软件包。这些软件包被下载了数百次，目前 PyPI 官方已经删除对应的账户。

![image.png-155.7kB](https://image.3001.net/images/20230713/1689227896_64af9278ccac5a72d90a0.png!small)开发者页面

这些账户都会使用 1337 作为后缀，这说明攻击者可能是利用自动化方式创建这些用户。

包名| 开发者| 恶意链接| 下载量  
---|---|---|---  
ligitgays| Anne1337| hxxps://paste.bingner[.]com/paste/o27gb/raw| 191  
xboxredeemer| Richard1337| hxps://paste.bingner[.]com/paste/47rpu/raw| 160  
syntax-init| Debbie1337| hxxps://paste.bingner[.]com/paste/q77t3/raw| 140  
xboxlivepy| Christopher1337| hxxps://paste.bingner[.]com/paste/jr7ow/raw| 153  
Ligitkidss| Sara1337| hxxps://paste.bingner[.]com/paste/9mzzs/raw| 158  
tls-python| Kevin1337| hxxps://paste.bingner[.]com/paste/97vnn/raw| 240  
  
## 自定义包入口点

攻击与此前披露的 W4SP 攻击团伙类似，根据相似之处，分析人员判断这是一次模仿攻击。

本次攻击并没有 W4SP 那么复杂，例如：

  * 攻击不针对任何特定组织
  * 没有创建拼写错误的流行软件包对应的恶意软件包
  * 后续攻击未加密，检测并不困难
  * W4SP 先前攻击的大部分代码都可以下载，可以重新利用

这些软件包没有包含明显的恶意代码，而是经过精心设计，具有在安装或执行过程中触发的特定入口点。结合免费文件托管服务与自定义入口点，使得检测与发现此类威胁变得更有挑战。

尽管攻击较简单，但可能会非常有效。攻击代码植入在安装文件中，意味着攻击在软件包安装过程中就已经开始了。

攻击者自称 `@EVIL$ STEALER`，并且变换了很多名称：

  * ANGEL Stealer
  * Celestial Stealer
  * Fade Stealer
  * Leaf $tealer
  * PURE Stealer
  * Satan Stealer
  * @skid Stealer

## 恶意代码

所有软件包中的 setup.py 都是相同的，包含以下代码片段，通过远程 URL 下载数据。

![image.png-204.6kB](https://image.3001.net/images/20230713/1689227898_64af927a249c4c5a8f5b8.png!small)setup.py
恶意代码

攻击者首先使用 _ffile 对象创建临时文件，并且使用 write 写入文件内容。众所周知，使用 NamedTemporaryFile
写入临时文件可以隐藏恶意代码，不会被反病毒软件或者其他安全软件检测到。

该文件的内容通过 urllib.request 中的 urlopen 函数下载而来，然后使用 exec
函数执行文件的内容。写入完成后，文件就会被管理。随后，尝试使用 start 命令执行该文件。执行成功后，调用 setup
函数创建软件包。如前所述，start 命令也是攻击者绕过安全限制最常见的方法之一。

## 后续阶段的 W4SP 窃密

所有恶意软件包在后续阶段中，攻击者使用了 1.1.6 版本的 W4SP Stealer。该版本与此前的版本类似，使用各种技术来提取、解密浏览器凭据（密码与
Cookie），并将这些数据回传到 Discord webhook。

恶意代码定义了一个 DATA_BLOB 类，用于存储 CryptUnprotectData 函数的数据。此函数可以解密受 Windows 数据保护
API（DPAPI）保护的数据，例如密码与 API 密钥等敏感数据。代码尝试使用 CryptUnprotectData 和 DecryptValue
函数进行解密，后续通过 Discord Webhook 回传到 C&C 服务器。

![image.png-316.7kB](https://image.3001.net/images/20230713/1689227899_64af927b51b6c8849c6f0.png!small)解密
DPAPI 的数据

下图为部分恶意代码，攻击者试图收集有关受害者的信息，包括 IP 地址、用户名、国家/地区代码。

![image.png-156.5kB](https://image.3001.net/images/20230713/1689227900_64af927c9eae54ca46c46.png!small)检索受害者相关信息

攻击者与 Discord API 交互检索用户的好友列表，并且收集用户拥有的徽章信息。

![image.png-190.2kB](https://image.3001.net/images/20230713/1689227901_64af927d61790f9a48ed8.png!small)检索
Discord 好友列表

随后，使用预先准备好的 Discord Webhook，尝试通过 HTTP 请求将受害者信息回传。

![image.png-43.4kB](https://image.3001.net/images/20230713/1689227902_64af927e75aabdf069074.png!small)Discord
Webhook

最后，攻击者将会验证受害者的机器是否值得攻击。如果确认机器合适，则会将 DETECTED 变量设置为 True，并将受害者信息回传到服务器。

![image.png-73.3kB](https://image.3001.net/images/20230713/1689227903_64af927f7b31620054e1b.png!small)检索
Cookie

## PyPI 作为恶意软件包的目标

PyPI 是一个被广泛使用的存储库，其上托管着数量惊人的 Python 软件包。但与此同时，攻击者也将目光对准了
PyPI，利用其庞大的用户群来传播恶意软件。

PyPI 去中心化的特性使得检测这些恶意软件包变得非常艰难，但一旦成为这些恶意软件包的受害者可能会带来巨大的损失。

2023 年 5 月 20 日，PyPI 宣布由于平台上的恶意攻击、恶意用户不断增加，暂时停止了新软件包的注册与上传。

## 结论

开源软件的兴起以及包管理器的普及，使得攻击者比以往任何时刻都想要把恶意软件包放入整个系统中。恶意软件包带来的威胁日益严重，攻击者将恶意软件包伪装成合法软件，进行数据窃密、网络控制等。

软件开发人员必须在开发过程中就考虑到软件安全问题，通过代码审查、自动化测试与渗透测试等方式，在部署前发现问题。

除技术手段外，提高软件安全意识与用户教育水平也有助于降低恶意软件包带来的风险。为开发人员与最终用户进行定期培训，有助于阻止攻击。总之，需要各方的集体努力才能确保恶意软件包不会对网络安全造成损害。

## IOC

> hxxps://paste.bingner[.]com/paste/o27gb/raw  
> hxps://paste.bingner[.]com/paste/47rpu/raw  
> hxxps://paste.bingner[.]com/paste/q77t3/raw  
> hxxps://paste.bingner[.]com/paste/jr7ow/raw  
> hxxps://paste.bingner[.]com/paste/9mzzs/raw  
> hxxps://paste.bingner[.]com/paste/97vnn/raw

## 参考来源

> [Unit42](https://unit42.paloaltonetworks.com/malicious-packages-in-pypi/)

