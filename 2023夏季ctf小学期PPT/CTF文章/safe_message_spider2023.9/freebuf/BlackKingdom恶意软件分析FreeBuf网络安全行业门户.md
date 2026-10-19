在2019年发现了针对Microsoft Exchange Server 漏洞的勒索软件Black Kingdom
，该恶意软件由python编码。今年再次发现其恶意活动，该勒索软件利用 Microsoft Exchange 漏洞
(CVE-2021-27065)进行传播。勒索软件使用 Python 编码并用 PyInstaller
编译为可执行文件；它支持两种密钥生成模式：动态生成密钥和硬编码密钥。

## 背景

3 月底公开报道了CVE-2021-27065 Microsoft Exchange 漏洞（称为 ProxyLogon）攻击活动中出现了名为 Black
Kingdom 的勒索软件家族。对 Black Kingdom 分析表明，它存在一些bug和关键性的加密缺陷，由于使用了硬编码密钥，受害者可利用其解密文件。
它在 2020 年还利用了其他漏洞，例如 CVE-2019-11510。

Date | CVE | Product affected  
---|---|---  
June 2020| CVE-2019-11510| Pulse Secure  
March 2021| CVE-2021-26855, CVE-2021-26857, CVE-2021-26858, CVE-2021-27065|
Microsoft Exchange Server  
  
## 技术分析

### 传播方式

该勒索软件集团在目标上成功利用该漏洞后，会在受感染的系统中安装 webshell。 webshell 使攻击者能够执行任意命令，例如下载和运行 Black
Kingdom 可执行文件。

### 休眠参数

勒索软件可以在没有参数的情况下执行，并开始加密系统，也可以加入参数运行 Black Kingdom，它会在开始加密之前进行等待。

![BlackKingdom_ransomware_01.png](https://image.3001.net/images/20210715/1626316776_60ef9fe8c4e51868fb035.png!small)

Black Kingdom 使用 Python3.7 编写并使用 PyInstaller 编译为可执行文件。大部分勒索软件逻辑都被编码到名为
0xfff.py 的文件中。

![1626315525_60ef9b05cfa72e4e78eca.png!small?1626315525954](https://image.3001.net/images/20210715/1626315525_60ef9b05cfa72e4e78eca.png!small?1626315525954)

### 排除的目录

Black Kingdom 加密时会排除某些文件夹，避免在加密期间破坏系统。

> Windows,  
> ProgramData,  
> Program Files,  
> Program Files (x86),  
> AppData/Roaming,  
> AppData/LocalLow,  
> AppData/Local.

### PowerShell 命令

在文件加密之前，Black Kingdom 使用 PowerShell 停止系统中所有包含“sql”的进程：

> Get-Service*sql*|Stop-Service-Force2>$null

完成后删除系统中的 PowerShell 历史记录，攻击者试图通过删除其活动的所有痕迹来隐藏在系统中。

###
![1626315671_60ef9b97be27eb24ef60b.png!small?1626315671787](https://image.3001.net/images/20210715/1626315671_60ef9b97be27eb24ef60b.png!small?1626315671787)加密过程

Black Kingdom 基于以下算法生成 AES-256 密钥。

![1626315733_60ef9bd5d6f31a61f8ee9.png!small?1626315738186](https://image.3001.net/images/20210715/1626315733_60ef9bd5d6f31a61f8ee9.png!small?1626315738186)

恶意软件会生成一个 64 个字符的伪随机字符串，然后获取字符串的 MD5 哈希值并将其用作 AES-256
加密的密钥。生成的密钥会发送到第三方服务，如果连接不成功，Black Kingdom 将使用代码中的硬编码密钥对数据进行加密。

以下是与第三方服务成功连接的示例：

![1626315805_60ef9c1dc647e4f519a70.png!small?1626315805940](https://image.3001.net/images/20210715/1626315805_60ef9c1dc647e4f519a70.png!small?1626315805940)

  

![1626315829_60ef9c3593c4affdeeaad.png!small?1626315829767](https://image.3001.net/images/20210715/1626315829_60ef9c3593c4affdeeaad.png!small?1626315829767)

通信数据格式如下：

> ID: Generated ID for user identification  
> Key: Generated user key  
> User: Username in the infected system  
> Domain: Domain name to which the infected user belongs

Black Kingdom 可以通过传参的方式加密单个文件，代码实现如下：

![1626315948_60ef9cacedf2040ee775c.png!small?1626315949371](https://image.3001.net/images/20210715/1626315948_60ef9cacedf2040ee775c.png!small?1626315949371)

如果没有任何参数传入，恶意软件将会枚举系统文件，然后多进程对文件进行加密。

![1626316019_60ef9cf36076b91a2cecc.png!small?1626316020009](https://image.3001.net/images/20210715/1626316019_60ef9cf36076b91a2cecc.png!small?1626316020009)

Black Kingdom 还会枚举各种驱动器号并对其进行加密，并在每个加密目录留下勒索信息。

![1626316191_60ef9d9f8685fc8717968.png!small?1626316191665](https://image.3001.net/images/20210715/1626316191_60ef9d9f8685fc8717968.png!small?1626316191665)

### 加密错误

勒索软件开发过程中出现了一些bug，例如，加密密钥管理不当，或者即使受害者支付了费用也无法恢复。 Black Kingdom 尝试将生成的密钥上传到
Mega，如果上传失败，使用硬编码密钥对文件进行加密。 如果文件已加密且系统无法与 Mega 建立连接，可以使用硬编码密钥恢复文件。

![1626316358_60ef9e46e6a1ba69a2023.png!small?1626316358967](https://image.3001.net/images/20210715/1626316358_60ef9e46e6a1ba69a2023.png!small?1626316358967)

在加密过程中，Black Kingdom 不会检查文件是否已经加密，如果系统被 Black Kingdom 感染两次，系统中的文件也会被加密两次。

### 系统清理

Black Kingdom使用 Python 清理系统日志。

![1626316443_60ef9e9b78f64b70fbb1d.png!small?1626316443490](https://image.3001.net/images/20210715/1626316443_60ef9e9b78f64b70fbb1d.png!small?1626316443490)

### 勒索信息

Black Kingdom 将桌面背景更改为勒索信息，同时使用 pyHook 禁用鼠标和键盘。

![1626316483_60ef9ec3718584f40563d.png!small?1626316483457](https://image.3001.net/images/20210715/1626316483_60ef9ec3718584f40563d.png!small?1626316483457)

> ***************************  
> | We Are Back ?  
> ***************************
>
> We hacked your (( Network )), and now all files, documents, images,  
> databases and other important data are safely encrypted using the strongest
> algorithms ever.  
> You cannot access any of your files or services .  
> But do not worry. You can restore everthing and get back business very soon
> ( depends on your actions )
>
> before I tell how you can restore your data, you have to know certain things
> :
>
> We have downloaded most of your data ( especially important data ) , and if
> you don't contact us within 2 days, your data will be released to the
> public.
>
> To see what happens to those who didn't contact us, just google : (
> Blackkingdom Ransomware )
>
> ***************************  
> | What guarantees ?  
> ***************************
>
> We understand your stress and anxiety. So you have a free opportunity to
> test our service by instantly decrypting one or two files for free  
> just send the files you want to decrypt to
> (support_blackkingdom2@protonmail.com
>
> ***************************************************  
> | How to contact us and recover all of your files ?  
> ***************************************************
>
> The only way to recover your files and protect from data leaks, is to
> purchase a unique private key for you that we only posses .
>
>  
> [ + ] Instructions:
>
> 1- Send the decrypt_file.txt file to the following email ===>
> support_blackkingdom2@protonmail.com
>
> 2- send the following amount of US dollars ( 10,000 ) worth of bitcoin to
> this address :
>
> [ 1Lf8ZzcEhhRiXpk6YNQFpCJcUisiXb34FT ]
>
> 3- confirm your payment by sending the transfer url to our email address
>
> 4- After you submit the payment, the data will be removed from our servers,
> and the decoder will be given to you,  
> so that you can recover all your files.
>
> ## Note ##
>
> Dear system administrators, do not think you can handle it on your own.
> Notify your supervisors as soon as possible.  
> By hiding the truth and not communicating with us, what happened will be
> published on social media and yet in news websites.
>
> Your ID ==>  
> FDHJ91CUSzXTquLpqAnP

### 代码分析

反编译 Python 代码后发现 Black Kingdom 的代码库起源于
[Github](https://github.com/BuchiDen/Ransomware_RAASNet/blob/master/RAASNet.py)。Black
Kingdom 修改了部分代码，添加了一些功能，例如硬编码密钥或与第三方服务 的通信。

## IOC

### 文件哈希

b9dbdf11da3630f464b8daace88e11c374a642e5082850e9f10a1b09d69ff04f  
c4aa94c73a50b2deca0401f97e4202337e522be3df629b3ef91e706488b64908  
a387c3c5776ee1b61018eeb3408fa7fa7490915146078d65b95621315e8b4287  
815d7f9d732c4d1a70cec05433b8d4de75cba1ca9caabbbe4b8cde3f176cc670  
910fbfa8ef4ad7183c1b5bdd3c9fd1380e617ca0042b428873c48f71ddc857db  
866b1f5c5edd9f01c5ba84d02e94ae7c1f9b2196af380eed1917e8fc21acbbdc  
c25a5c14269c990c94a4a20443c4eb266318200e4d7927c163e0eaec4ede780a

### 域

hxxp://yuuuuu44[.]com/vpn-service/$(f1)/crunchyroll-vpn

### YARA rules

> import "hash"  
> import "pe"  
> rule ransomware_blackkingdom {  
>  
> meta:
>
> description = "Rule to detect Black Kingdom ransomware"  
> author = "Kaspersky Lab"  
> copyright = "Kaspersky Lab"  
> distribution = "DISTRIBUTION IS FORBIDDEN. DO NOT UPLOAD TO ANY MULTISCANNER
> OR SHARE ON ANY THREAT INTEL PLATFORM"  
> version = "1.0"  
> last_modified = "2021-05-02"  
> hash = "866b1f5c5edd9f01c5ba84d02e94ae7c1f9b2196af380eed1917e8fc21acbbdc"  
> hash = "910fbfa8ef4ad7183c1b5bdd3c9fd1380e617ca0042b428873c48f71ddc857db"
>
> condition:
>
> hash.sha256(pe.rich_signature.clear_data) ==
> "0e7d0db29c7247ae97591751d3b6c0728aed0ec1b1f853b25fc84e75ae12b7b8"  
> }

## 原文链接

> [securelist](https://securelist.com/black-kingdom-ransomware/102873/)

