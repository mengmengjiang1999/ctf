Uptycs 的研究人员近日发现了一个新的恶意软件构建工具 KurayStealer，被用于出售给犯罪分子使其更方便构建恶意软件。KurayStealer
是使用 Python 编写的，提供密码窃取和屏幕截图功能，通过 webhook 将窃密数据发送到攻击者的 Discord 频道。KurayStealer
有两个版本：免费版本与 VIP 版本。根据各方情报汇总，该恶意软件构建工具的创建者应该是西班牙裔。

## 发现 KurayStealer

Uptycs 威胁情报系统在 2022 年 4 月 27 日检测到了 KurayStealer 的第一个样本。根据分析与研究，KurayStealer 于
2022 年 4 月 23 日通过名为 `Portu`的 Youtube 和 Discord 频道首次发布广告宣传。

## 窃密行动

最早被发现的 KurayStealer 名为 c2.py。使用 Python 编写，可以在 Python 3.0 下运行。执行后，KurayStealer
会使用 `wmic csproduct get UUID`来检查 UUID：

![image.png-38.4kB](https://image.3001.net/images/20220526/1653564112_628f62d08a29768cd284e.png!small)UUID
检查

根据 UUID 与 pastebin 中的 UUID 列表进行比对，确定用户是免费用户还是 VIP 用户：

![image.png-108.9kB](https://image.3001.net/images/20220526/1653564112_628f62d0db6388f5af7fb.png!small)构建工具

根据用户类别与 webhook 的输入，KurayStealer 会在机器中释放名为 `DualMTS.py`或者
`DualMTS_VIP.py`的文件。以下都使用免费版本演示 KurayStealer 的功能。

DualMTS.py 尝试将 BetterDiscord 中的字符串 `api/webhooks`替换为 `Kisses`，以绕过
BetterDiscord 保护发送 webhook。

![image.png-58kB](https://image.3001.net/images/20220526/1653564113_628f62d152018ab15bafd.png!small)绕过
BetterDiscord 保护

接着，DualMTS.py 尝试使用 python 模块 `pyautogui`进行屏幕截图。除此之外，还会通过 ipinfo 获取机器所在位置。

![image.png-68.7kB](https://image.3001.net/images/20220526/1653564113_628f62d198c497f804031.png!small)屏幕截图

窃取 21 个软件的密码与 Token，包括 Discord、Lightcord、Discord PTB、Opera、Opera
GX、Amigo、Torch、Kometa、Orbitum、CentBrowser、7Star、Sputnik、Vivaldi、Chrome
SxS、Chrome、 Epic Privacy Browser、Microsoft Edge、Uran、Yandex、Brave、Iridium。

KurayStealer 在收集了计算机名称、地理位置、IP 地址、密码凭据以及屏幕截图后，通过 webhook 发送到 Discord：

![image.png-131.4kB](https://image.3001.net/images/20220526/1653564114_628f62d20dacd990c2ec2.png!small)凭据发送

## 威胁情报

分析了代码后，可以找到 Suleymansha & Portu 的编写声明。但是在 GitHub
等多个公开仓库中可以发现类似的声明，这一声明并不能说明作者身份。

KurayStelaer 提供了多个窃密程序作为组件使用，并且使用 Discord 作为 C&C 的信道来收集窃密数据。代码中还包含有攻击者的
Discord 频道邀请链接，该频道介绍了 KurayStelaer 的 VIP 版本信息。

![image.png-65.5kB](https://image.3001.net/images/20220526/1653564114_628f62d269226f614f2d4.png!small)VIP
版本

查看频道信息，Discord 用户 `portu`在个人资料中提供了 Discord 链接、Shoppy 链接和 YouTube 链接。

![image.png-118.2kB](https://image.3001.net/images/20220526/1653564114_628f62d2df707f8a58ba5.png!small)用户信息

通过 YouTube 发现用户位于西班牙，用户也上传了 KurayStealer 的演示视频。

![image.png-98.2kB](https://image.3001.net/images/20220526/1653564115_628f62d34fcbf1a85aa77.png!small)YouTube
信息

而在 Shoppy 中则显示了攻击者的其他攻击工具与商业产品。

![image.png-49kB](https://image.3001.net/images/20220526/1653564115_628f62d3ab43cc12d26a6.png!small)Shoppy
信息

在撰写本文时，攻击者已经删除了 YouTube 视频。攻击者的 Discord 频道在 2022 年 4 月 26 日发布了有关正在开发勒索软件的公告。

## 结论

根据情况分析，研究人员认为攻击者仍然会更新窃密程序甚至是其他类型的恶意软件。

## IOC

> 8535c08d7e637219470c701599b5de4b85f082c446b4d12c718fa780e7535f07 (c2.py)  
> 09844d550c91a834badeb1211383859214e65f93d54d6cb36161d58c84c49fab
> (DualMTS.py)  
> 30b61be0f8d2a8d32a38b8dfdc795acc0fac4c60efd0459cb3a5a8e7ddb2a1c0 (C2.exe)

## 参考来源

> [Uptycs](https://www.uptycs.com/blog/kuraystealer-a-bandit-using-discord-> webhooks)

