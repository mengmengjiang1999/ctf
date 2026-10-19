新冠疫情从 2021 年一直持续到了 2022 年，从 2021 年 4 月出现的 Delta（德尔塔）毒株到现在肆虐的 Omicron（奥密克戎）毒株，
**全球累计确诊新冠肺炎病例数量已经正式超过 3 亿** 。

攻击者并没有因为疫情给人类带来的伤痛而停止为自己谋取利益。FortiGuard **最近发现了一个名为**` **Omicron Stats.exe**`
**恶意样本，分析确认为 Redline Stealer 的变种** 。

## Redline Stealer

Redline Stealer 最早在 2020 年 3 月被公开披露，并且 **Redline Stealer
也迅速成为地下市场中非常受欢迎的窃密工具之一** 。通过 Redline Stealer 窃取的信息在暗网上以每个用户 10 美元的低价出售。

人们对于疫情蔓延的恐惧和担忧被攻击者利用，在攻击中使用与 COVID-19 有关的内容作为诱饵，容易使人们降低警惕。

在被安装了窃密工具后，受害者的账户密码和浏览的详细信息都会被发送给攻击者。包括在线支付、电子银行、文件共享或者社交网络的登录凭据等个人隐私信息。

Redline Stealer 会收集以下信息：

> 系统信息：登录名与密码、Cookie、自动填写表单、User-Agent、信用卡信息、浏览器历史记录
>
> FTP 客户端信息
>
> IM 客户端信息
>
> 通过文件路径与文件扩展名收集信息
>
> 设置阻止运行的国家/地区名单
>
> 机器信息：IP 地址、国家、城市、用户名、硬件 ID、键盘布局、屏幕截图、屏幕分辨率、操作系统、UAC 设置、User-> Agent、其他设备（如显卡）信息、反病毒软件、常用文件夹内容

发现的变种包含以上功能，还有一些新的改进。

## Omicron Stats.exe

以往 RedLine Stealer 就会通过以疫情为主题的电子邮件进行分发，本次虽然没有确定传播媒介，但推测也是通过电子邮件。
**文件名使用了近来引起确诊病例海啸的 Omicron 毒株的名字，引诱受害者点击** 。

根据 FortiGuard 的遥测数据， **该 RedLine Stealer 变种的受害者分布在 12 个国家/地区，攻击者并未针对特定目标发起攻击**
。

## 新功能

在执行 Omicron Stats.exe 后，样本将资源段中的加密数据解密出来注入 `vbc.exe`中， **数据使用 ECB 为加密模式、PKCS7
为填充模式的三重 DES 进行加密** 。

样本将自身复制到 `C:\Users\[Username]\AppData\Roaming\chromedrlvers.exe`并创建计划任务进行持久化。

> schtasks /create /sc minute /mo 1 /tn "Nania" /tr  
> "'C:\Users[Username]\AppData\Roaming\chromedrlvers.exe'" /f

紧接着，样本通过 WMI 窃取以下信息：

> 显卡名称
>
> BIOS 制造商、识别码、序列号、发布日期与版本
>
> 硬盘驱动器制造商、型号、磁头数
>
> CPU 制造商、最大时钟速度、处理器 ID 等

样本还会通过 base64 编码和异或解密 C&C 字符串，解密密钥为 `Margented`。解密后的 C&C 字符串为
`freelancer.com`和 `207.32.217.89`，样本使用其连接 C&C 服务器（207.32.217.89:14588）。

RedLine Stealer 在请求头中使用 `Authorization:
ns1=d8cc092a9e22f3fc55d63aad32150529`进行验证，并使用解密后的
`freelancer.com`阻止其他恶意软件与研究人员连接。

![image.png-77.7kB](https://image.3001.net/images/20220112/1641965573_61de6805682ba159a1eb8.png!small)RedLine
Stealer 的配置

样本会在失陷主机上搜索以下字符串，定位相关文件夹进行数据窃取：

> wallet.dat
>
> wallet
>
> Login Data
>
> Web Data
>
> Cookies
>
> Opera GX Stable
>
> Opera GX

![image.png-229.8kB](https://image.3001.net/images/20220112/1641965574_61de68064ef34723c5f66.png!small)搜索加密货币钱包的代码

样本会查找以下文件夹进行数据窃取：

> `\Telegram Desktop\tdata`
>
> 文件夹，被 Telegram 用于存储图片和会话
>
> `%appdata%\discord\Local Storage\leveldb`
>
> 文件夹，被 Discord 用于存储加入的频道和相关信息，如下文件：
>
>   1. .log 和 .db 文件
>   2. 正则`[A-Za-z\d]{24}\.[\w-]{6}\.[\w-]{27}[A-Z]`匹配的文件
>

>
> Tokens.txt，被用于 Discord 访问

![image.png-162.3kB](https://image.3001.net/images/20220112/1641965575_61de680798f757f386f92.png!small)检索指定位置文件的代码

RedLine Stealer 会尝试窃取以下浏览器数据：

> 登录数据
>
> 网络数据
>
> User-Agent 信息
>
> Cookie
>
> 扩展 Cookie
>
> 自动填充表单
>
> 信用卡信息

RedLine Stealer 还会收集以下系统信息：

> 处理器
>
> 显卡
>
> 内存
>
> 安装程序
>
> 运行进程
>
> 使用语言
>
> 用户名
>
> 安装的 Windows 版本
>
> 序列号

针对 VPN 客户端，会窃取以下 VPN 的凭据信息：

> Nord-VPN
>
> Open-VPN
>
> Proton-VPN

## C&C 基础设施

该变种将 207.32.217.89 作为 C&C 服务器，该 IP 地址由 1GSERVERS 运营。发现该变种的几周里都有一个 IP 地址经常与该 IP
地址进行通信，如下所示：

IP 地址| 开始时间| 结束时间  
---|---|---  
149.154.167.91| 2021-11-26 04:34:54| 2021-11-26 10:05:15  
149.154.167.91| 2021-12-05 12:06:03| 2021-12-05 13:19:35  
149.154.167.91| 2021-12-09 16:18:46| 2021-12-09 20:00:13  
149.154.167.91| 2021-12-22 18:38:18| 2021-12-23 11:33:58  
  
IP 地址 149.154.167.91 位于英国，是 Telegram Messenger 的一部分。 **这似乎可以表明 C &C 服务器被
RedLine Stealer 通过 Telegram 控制着**，毕竟 RedLine Stealer 还在 Telegram
上提供了专门的购买和技术支持渠道。

## 结论

RedLine Stealer
持续利用疫情相关话题展开攻击，预计这一攻击方式仍将与疫情持续存在。尽管感染不会对失陷主机产生灾难性的影响，但是被窃取的信息有可能可被其他攻击利用。

## IOC

> 15FE4385A2289AAF208F080ABB7277332EF8E71EDC68902709AB917945A36740  
> 891aba61b8fec4005f25d405ddfec4d445213c77fce1e967ba07f13bcbe0dad5  
> 216a733c391337fa303907a15fa55f01c9aeb128365fb6d6d245f7c7ec774100  
> 73942b1b5a8146090a40fe50a67c7c86c739329506db9ff5adc638ed7bb1654e  
> 2af009cdf12e1f84f161a2d4f2b4f97155eb6ec6230265604edbc8b21afb5f1a  
> bf31d8b83e50a7af3e2dc746c74b85d64ce28d7c33b95c09cd46b9caa4d53cad  
> b8ebdc5b1e33b9382433151f62464d3860cf8c8950d2f1a0278ef77679a04d3b  
> 8d7883edc608a3806bc4ca58637e0d06a83f784da4e1804e9c5f24676a532a7e  
> 1b4fcd8497e6003009010a19abaa8981366922be96e93a84e30ca2885476ccd7  
> fdeadd54dd29fe51b251242795c83c4defcdade23fdb4b-589c05939ae42d6900  
> af4bf44056fc0b8c538e1e677ed1453d1dd884e78e1d66d1d2b83abb79ff1161  
> 207.32.217.89:14588  
> 91.243.32.13:1112  
> 185.112.83.21:21142  
> 23.88.11.67:54321  
> 178.20.44.131:8842  
> 91.243.32.94:63073  
> 95.143.177.66:9006  
> 45.147.230.234:1319  
> 31.42.191.60:62868  
> 135.181.177.210:16326  
>
> hxxps://privatlab[.]com/s/s/nRqOogoYkXT3anz2kbrO/2f6ceecb-a469-40b5-94a2-2c9cc0bc8445-Ewdy5l6RAylbLsgDgrgjNjVbn  
>
> hxxps://privatlab[.]com/s/s/3Qa0YRMaVaij07Z8BqzZ/7ca69d4c-c5bb-4ab3-b5a9-87c17b7167b5-86yYgEGqbQMnoszgm0OmgGb6g  
> hxxp://data-host-coin-8[.]com/files/9476_1641477642_2883[.]exe  
> hxxp://data-host-coin-8[.]com/files/541_1641407973_7515[.]exe  
> hxxp://data-host-coin-8[.]com/files/7871_1641415744_5762[.]exe  
> hxxps://transfer[.]sh/get/HafwDG/rednovi[.]exe  
> hxxp://91[.]219.63.60/downloads/slot8[.]exe

## 参考来源

> [Fortinet](https://www.fortinet.com/blog/threat-research/omicron-variant-> lure-used-to-distribute-redline-stealer)

