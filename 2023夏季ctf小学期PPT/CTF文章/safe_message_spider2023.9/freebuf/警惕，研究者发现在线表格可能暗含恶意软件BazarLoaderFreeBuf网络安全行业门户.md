尽管钓鱼邮件仍然是传统的攻击途径，但攻击者也一直并未放弃寻找新攻击方式。最近，研究人员发现 BazarLoader 通过在线表格发起攻击。

BazarLoader 被认为与网络犯罪组织 Wizard Spider 关系极为密切，该组织开发了 Trickbot 银行木马和 Conti
勒索软件而广为人知。

在 2021 年时，BazarLoader 曾假借盗版内容进行传播。攻击者威胁要对持续侵犯版权的行为采取法律行动，恶意软件被描述为不当行为的证据。

## 在线表格

在 2021 年 12 月至 2022 年 1 月间，研究人员发现攻击者并不是直接发送钓鱼邮件发起攻击，而是通过在线表格实现攻击。

攻击者伪装成加拿大豪华建筑公司的员工，寻求产品的报价。攻击者选用该方法有两个目的：

> 将流量伪装成合法流量
>
> 通过合法发件人发送，逃避了恶意邮件检测

攻击者只需要等着目标公司的受害者主动送上门即可。

## 发送恶意样本

通过电子邮件确认身份后，攻击者将以项目谈判的名义引诱受害者下载恶意文件。

![image.png-79.8kB](https://image.3001.net/images/20220323/1648013573_623ab105e219339785efd.png!small)电子邮件

攻击者通常是使用文件共享服务 TransferNow 和 WeTransfer 进行样本投递。

![image.png-233.8kB](https://image.3001.net/images/20220323/1648013574_623ab106555fc1c54e1eb.png!small)样本下载

## BazarLoader 恶意软件

攻击者共享的是 .iso 文件，其中包含两个伪装成不同文件类型的文件。看上去其中一个是指向所在文件夹的快捷方式，另一个是带有合法 Windows 文件名的
.log 文件。实际上，一个是 Windows 的 LNK 文件，另一个是 DumpStack.log 文件。

![image.png-280.3kB](https://image.3001.net/images/20220323/1648013574_623ab106f1101ddf7325b.png!small)通过
TransferNow 发送的恶意软件

快捷方式允许创建者指定命令行参数在受害者设备上执行操作，攻击者常常利用该类型的文件进行攻击。

![image.png-88.8kB](https://image.3001.net/images/20220323/1648013575_623ab107b56d89370b237.png!small)ISO
文件

LNK 文件会使用 `regsvr-32.exe`打开终端运行 `DumStack.log`，后者为 BazarLoader 的 DLL 文件。

![image.png-407.3kB](https://image.3001.net/images/20220323/1648013576_623ab108259b118450476.png!small)LNK
文件

DLL 通过进程注入 `svchost.exe`来逃避检测，并且使用 443 端口与 C&C 服务器 13.107.21.200 进行通信。

![image.png-37.6kB](https://image.3001.net/images/20220323/1648013577_623ab1091ca665f3a69af.png!small)进程

![image.png-206.9kB](https://image.3001.net/images/20220323/1648013577_623ab109ae272b16434ba.png!small)建立连接

![image.png-110.5kB](https://image.3001.net/images/20220323/1648013578_623ab10a5a8ed7b46ec23.png!small)建立连接

调查时部分 C&C 服务器已经关闭，无法下载后续载荷。根据数据关联，可以发现相关的恶意软件链接。

![image.png-242.4kB](https://image.3001.net/images/20220323/1648013578_623ab10ad4b47ff08c6cc.png!small)关联图

与 IP 地址相关的恶意软件如下所示：

![image.png-68.2kB](https://image.3001.net/images/20220323/1648013579_623ab10b8d70bd1665bcd.png!small)恶意样本

## 总结

攻击者会冒充知名企业创建相似域名来获取受害者的信任，例如将 .com 顶级域名更改为 .us。

BazarLoader 通常作为多阶段恶意软件中的一环，后续可以部署 Conti 勒索软件或者 Cobalt Strike 恶意样本。

## IOC

> 104.215.148.63  
> 45.15.131.126  
> 148.163.42.203  
> 45.41.204.150  
> 193.169.86.84  
> 76.6.231.20  
> 131.253.33.200  
> 72.21.91.29  
> 97806F6DA402F135FA0556ADF5809D6D3BC629E967A0771B9FEB5BA55267D560  
> 8395B26BE4A7D57F9B60839257C3E7B9E6756DBBEB818DE6575987D6E041C8FD  
> CE6E63191588E449DE4AB45FF4D32E1BBD1C67681C74C32DE3A4DB63331278CC

## 参考来源

> [Abnormal](https://abnormalsecurity.com/blog/bazarloader-contact-form)

