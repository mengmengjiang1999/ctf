被称为 RomCom 的攻击者正在利用 SolarWinds、KeePass 与 PDF Technologies
等公司的软件作为诱饵，开展一系列的攻击行动。研究人员发现攻击者通过虚假软件针对乌克兰军事机构发起攻击，并且投递 RomComRAT 远控木马。

RomCom 在攻击行动中仿冒了 SolarWinds Network Performance Monitor、KeePass Open-Source
Password Manager 与 PDF Reader Pro 这几款软件。

根据恶意网站的服务条款（TOS）与 C&C 服务器的 SSL
证书来看，乌克兰是攻击的主要目标，但包括英国在内的一些英语国家也在攻击范围内。根据地缘政治形势判断，RomCom 不像是一个以获利为主要目标的网络犯罪团伙。

## 攻击能力

RomCom 首先爬取原始网页的 HTML
代码，并且注册与合法域名相似的恶意域名。在对合法的应用程序进行投毒后，将其部署在诱饵网站上。最后，主要通过鱼叉邮件投递给受害者，某些情况下也会使用其他传播媒介。

## RomCom 武器化

### 武器化 SolarWinds Network Performance Monitor

如下显示了实际的 SolarWinds 网站与诱饵网站的区别：

![image.png-655.4kB](https://image.3001.net/images/20221109/1668005356_636bbdec1b905c01eea5f.png!small)合法
SolarWinds 网站

![image.png-562.4kB](https://image.3001.net/images/20221109/1668005357_636bbded0d18f3108497e.png!small)诱饵
SolarWinds 网站

攻击行动中，攻击者将 SolarWinds Network Performance Monitor
武器化后，引诱受害者通过诱饵网站下载免费试用版。受害者填写的申请表单是完全合法的，填写后确实有真正的 SolarWinds
的销售人员来联系受害者以跟进产品试用情况。这也使受害者相信最近下载并安装的应用程序是完全合法的。但其实，受害者已经掉入攻击者的陷阱，被植入了 RomCom
远控木马的 Dropper。

![image.png-1015.2kB](https://image.3001.net/images/20221109/1668005358_636bbdee08912a78b8051.png!small)SolarWinds-Orion-NPM-Eval.zip 的内容

恶意文件 Solarwinds-Orion-NPM-Eval.exe 的数字证书是 Wechapaisch Consulting &
Construction Limited 该组织签发的。攻击者之前在 advancedipscanner.msi
文件中也重用过相同的证书，可以参考之前的分析报告。

恶意文件 Solarwinds-Orion-NPM-Eval.exe 的资源段中嵌入了三个 64 位 PE 文件：

  * X86：其 PDB 路径为 c:\users\123\source\repos\ins_asi\win32\release\instlib.pdb，相同的 PDB 路径也在 setup.exe 文件中出现过。
  * X87：原始的 SolarWinds 安装程序。
  * X88：RomCom 远控木马 Dropper，通过 rundll32.exe 调用 fwdTst 函数即可在 C:\Users\user\AppData\Local\Temp\winver.dll 位置释放 RomCom 远控木马。

### 武器化 KeePass

近日，研究人员发现攻击者利用流行的密码管理软件 KeePass 发起新的攻击。其攻击方式与前述相同，引诱受害者通过与合法网站相似的诱饵网站来下载恶意软件。

![image.png-860.6kB](https://image.3001.net/images/20221109/1668005359_636bbdef1366e57297719.png!small)合法
KeePass 网站

![image.png-968.5kB](https://image.3001.net/images/20221109/1668005361_636bbdf1591cac6561471.png!small)诱饵
KeePass 网站

在这个攻击行动中，攻击者所使用的诱饵程序为 KeePass-2.52。网站下载的恶意文件名为 KeePass-2.52.zip，解压后其中包含如下文件。

![image.png-633.1kB](https://image.3001.net/images/20221109/1668005363_636bbdf335b506308a944.png!small)压缩文件内容

压缩文件中包含两个恶意文件：

> Setup.exe：调用 Dropper 的文件，其 PDB 为
> C:\Users\123\source\repos\ins_asi\Win32\Release\setup.pdb。
>
> hlpr.dat：该文件为 RomCom 远控木马的 Dropper。

研究人员跟踪发现，RomCom 部署恶意软件（如投毒的 KeePass 和 PDF Reader
Pro）的网站都是乌克兰语的。另外，根据诱饵网站的服务条款页特征，扩展发现也有针对英国发起攻击的网站。

> href="privacy/uk_privacy.html"
>
> href="privacy/uk_term.html"
>
> href="privacy/uk_disclaimer.html"

![image.png-381.6kB](https://image.3001.net/images/20221109/1668005364_636bbdf427099d8d3b2a3.png!small)投毒
KeePass

![image.png-515.1kB](https://image.3001.net/images/20221109/1668005364_636bbdf4eba0778400bfa.png!small)投毒
PDF Reader Pro

通过遥测，研究人员发现了在十月末注册的新 C&C 服务器，其也使用了归属于英国公司的 SSL 证书。

    
    
    Issuer: C=GB, ST=Greater London, L=Harmondsworth, O=British Government, OU=dgtlocean.com, CN=ca dgtlocean.com/emailAddress=ca(at)mail.com Issuer: C=GB, ST=Greater London, L=London, O=Government Digital Service, OU=you-supported.com, CN=ca you-supported.com/emdepth=0 C = GB, ST = British, L = Chesterfield, O = Royal Mail Group Ltd, OU = Group1, CN = Group1.A, emailAddress = server(at)mail.com

## 结论

RomCom 的攻击者正在针对乌克兰与英语区国家发起新的攻击行动，根据遥测数据很可能英国就是最新的攻击目标。

攻击者并未通过供应链攻击的方式直接入侵厂商或者其他合法公司，只是创建了与合法网站相似的诱饵网站来引诱受害者。

## IOC

> 4E4ECA58B896BDB6DB260F21EDC7760A  
> 7C003B4F8B3C0AB0C3F8CB933E93D301  
> a7172aef66bb12e1bb40a557bb41e607  
> 6310A2063687800559AE9D65CFF21B0A  
> CB933F1C913144A8CA6CFCFD913D6D28  
> D1A84706767BFB802632A262912E95A8  
> 1a21a1e626fd342e794bcc3b06981d2c  
> 8284421bbb94f3c37f94899cdcd19afd  
> 550f42c5b555893d171285dc8b15b4b5  
> ABE9635ADBFEE2D2FBAEA140625C49ABE3BAA29C44FB53A65A9CDA02121583EE  
> 246DFE16A9248D7FB90993F6F28B0EBE87964FFD2DCDB13105096CDE025CA614  
> 3252965013ec861567510d54a97446610edba5da88648466de6b3145266386d9  
> F7013CE417FCBA0F36C4B9BF5F8F6E0E2B14D6ED33FF4D384C892773508E932E  
> AC09CBFEE4CF89D7B7A755C387E473249684F18AA699EB651D119D19E25BFF34  
> 9D3B268416D3FAB4322CC916D32E0B2E8FA0DE370ACD686873D1522306124FD2  
> 596eaef93bdcd00a3aedaf6ad6d46db4429eeba61219b7e01b1781ebbf6e321b  
> 8b8dff5d30802fd79b76ee1531e7d050184a07570201ef1cd83a7bb8fa627cb0  
> 5f187393acdeb67e76126353c74b6080d3e6ccf28ae580658c670d8b6e4aacc1

## 参考来源

> [BlackBerry](https://blogs.blackberry.com/en/2022/11/romcom-spoofing-> solarwinds-keepass)

