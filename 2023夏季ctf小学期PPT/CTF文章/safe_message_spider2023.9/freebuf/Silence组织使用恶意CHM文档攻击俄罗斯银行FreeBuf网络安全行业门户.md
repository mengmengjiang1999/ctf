**在2018年11月，我们跟进了一条推文，提到在CHM中传播的潜在恶意代码（Microsoft Compiled HTML
Help）。初步分析引起了我们的威胁分析和情报团队的注意，特别是俄罗斯联邦和白俄罗斯共和国的员工。**

此次行动针对的是金融行业，尤其是是俄罗斯联邦和白俄罗斯共和国金融行业的工作人员。此次行动背后的行为者是Silence团伙，这是一个相对较新的威胁团伙，自2016年中期以来一直在运营。到目前为止，我们已确定的被攻击的企业包括：

> NBD Bank Russia：提供零售和商业服务的俄罗斯银行。
>
> Zapsibkombank（Zapadno-Sibirskiy Kommercheskiy Bank）：西西伯利亚商业银行（WSCB），位于俄罗斯。
>
> FPB（Finprombank）：同样位于俄罗斯。
>
> MSP银行（МСПБанк）：专注于为中小企业提供融资的俄罗斯联邦国家银行。
>
> MT Bank（МТБанк）：Meridian trade Bank，也是唯一一家位于白俄罗斯的实体银行。

![1.png](https://image.3001.net/images/20190130/1548837279_5c51619fe9068.png!small)

主向量由恶意CHM文件表示。尽管CHZ是一种“过时”的格式，但它过去曾被有效地用于运行恶意代码。在这种情况下，除了运行本机OS二进制文件以收集与其目标相关的信息之外，它还用于下载属于感染链的组件。

## Silence团伙如何传播

此次攻击利用鱼叉式网络钓鱼电子邮件进行传播，邮件由俄语编写，并带有一个名为“Contract_12112018.Z”（2018年11月12日合同）的压缩附件。

对附件进行解压后，得到一个名为“ **Contract_12112018.chm** ”的文件，其内容是银行开户协议，其执行代表感染过程的第一步。

![2.png](https://image.3001.net/images/20190130/1548837287_5c5161a7c837b.png!small)

此邮件会伪造成是由俄罗斯各家银行的官方地址发送的，调查结果显示，大多发送地址都是俄罗斯联邦央行，邮件内容如下：

    
    
    “Good day!
    I, Skurtov Andrei Vladimirovich,
    Head of Interbank Operations and
    Correspondent Relations of PJSC “FinServisBank”.
    We negotiated the opening and maintenance of correspondent accounts in rubles and freely convertible currencies.
    I ask you to consider the application as soon as possible to open and maintain accounts.
    I attach the archive with the contract. Please fill it in and send it to me.
    Thank you in advance, waiting for an answer.
    

`Respectfully,Head of Interbank Operations andCorrespondent Relations of PJSC
“FinserviceBank”Nizhny Novgorod region, Sarov, Silkin street, 13”`

## 恶意组件

在下图中，我们重建了Silence小组使用的完整CHM感染链，分为三个主要阶段：

1.下载启动感染链所需的初始payload（VBScript）；

2.由受感染计算机上的初始有效负载执行的活动，以及主要恶意软件组件的下载；

3.信息收集和交付给C＆C。

![3.png](https://image.3001.net/images/20190130/1548837295_5c5161afc12b5.png!small)

编译的HTML帮助文件(contract_12112018.chm)的文件结构类似于超文本页面，需要通过本地Microsoft
Windows程序“HH.exe”打开。CHM文件包含一个名为start.htm的文件和恶意payload，用于启动cmd.exe和mshta.exe从IP
下载恶意VBscript（称为“ li ”）146.0.72.139。这是感染链的第一阶段。

下图显示了用于启动 **mshta** 的命令行，该命令行下载并运行恶意VBS文件：

![4.jpg](https://image.3001.net/images/20190130/1548837303_5c5161b72da8e.jpg!small)

感染链的第二阶段继续执行“li”文件中包含的指令，主要负责：

复制一份cmd.exe和PowerShell.exe将它们分别重命名为`ejpejpff.com`和`ejpejpf.com`，并将它们保存在`%TEMP%`文件夹中。

使用参数 **-nop -W hidden -noninteractive -c** 调用ejpejpf.com（这是 **Powershell.exe**
的副本）来：

> 1.下载Base64编码的“flk”payload，并将其保存到`%TEMP%`文件夹中，格式为“ejpej .txt”；
>
> 2.解码并保存为“ejpejp.com”；
>
> 3.执行“ejpejp.com”。

![5.jpg](https://image.3001.net/images/20190130/1548837339_5c5161dbdcad8.jpg!small)

感染链的第三个也是最后一个阶段，将继续执行“ejpejp.com”，负责：

> 在`\AppData\Roaming\`中将自身复制为conhost.exe，该文件名也是合法的Console Windows
> Host经常调用的文件名，这么做可能是为了逃避检测；
>
>
> 将引用添加到`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`作为持久性方法运行；
>
> 运行System Information Discovery；
>
> 恶意文件的元数据描述为“MS DefenderApplicationController”。

我们已经确认该应用程序是Silence团伙使用的木马变种，该木马负责收集每个受害者电脑的信息，是通过以下4个Windows系统二进制文件进行收集的：

> system.exe：执行“System Information”以收集有关受害者计算机配置和操作系统的详细信息，例如：产品ID，硬件功能和安全信息；
>
> net.exe：“Net View”用于收集有关局域网的信息以及启动/停止IPv6协议服务；
>
> whoami.exe：用于获取用户的当前域和用户名；
>
> ipconfig.exe：用于收集TCP / IP网络配置设置。

所有这些信息都存储在“INFOCONTENT.TXT”文件中，文件保存在％ProgramData％中，并上传到IP
146.0.72.188托管的服务器，该服务器是Silence团伙用于此次行动的C2。以下是使用[ReaQta-Hive](https://reaqta.com/hive/)重建攻击的详细步骤。

![6.png](https://image.3001.net/images/20190130/1548837350_5c5161e606681.png!small)

完整的攻击链在[VirusTotal](https://www.virustotal.com/gui/file/1135813663bf9c747a1cca7312aef97d345d231df5cdeb314cb8606017d26d86/behavior/ReaQta-Hive)。

##  **网络基础设施**

如上所示，此次攻击行动通过运行本机的几个二进制文件来收集目标银行基础设施的情报。

通信过程使用两个IP地址进行：第一个是146.0.72.139，它是下载攻击链不同部分的直接通道；第二个是通过IP地址146.0.72.188与C2进行通信，将采集到的信息进行过滤。这两个ip都位于荷兰。

![7.jpg](https://image.3001.net/images/20190130/1548837356_5c5161ec3b004.jpg!small)

## 归因

我们想要分享为什么我们认为Silence团伙是这次攻击背后的因素：

> 其操作方式和感染载体(CHM)是Silence最新操作的典型特征；
>
> CHM的内部结构是Silence团伙攻击的常见结构；
>
> 下载的二进制文件与Silence使用的二进制文件相匹配(Truebot的变体)；
>
> 鱼叉式网络钓鱼活动中使用的语言是一样的；
>
> 目标主要为东欧和俄罗斯；
>
> 目标类型（金融机构）与Silence集团通常选择的目标相匹配；
>
> 在之前Silence小组的攻击中发现的TTP与此处分析的攻击相匹配。

这些因素使我们得出结论，Silence团伙（或附属团体）很可能是此次攻击背后的原因。

## 结论

我们收集的情报显示，这次攻击行动只是冰山一角，其攻击目标仍是主要在俄罗斯境内运作的金融机构。从感染过程、攻击链和操作结构来看，Silence团伙虽然还很年轻，但已经成为一个越来越有组织、越来越危险的银行恶意软件的传播源。

我们的分析是使用ReaQta-Hive进行的:端点可见性和威胁搜索能力是每个旨在降低网络攻击风险的威胁组织的需求。这类威胁显示了攻击者的速度有多快、适应性有多强，而检测、包含和响应的结构化流程对于防止对业务连续性的破坏和中断至关重要。

## Mitre Att＆ck

T1193：Spearphishing附件

T1223：编译的HTML文件

T1105：远程文件复制

T1043：常用端口

T1170：Mshta

T1036：伪装

T1059：命令行界面

T1086：Powershell

T1064：脚本

T1140：反混淆/解码文件或信息

T1060：注册表运行键/启动文件夹

T1082：系统信息发现

##  **IOCs**

    
    
    SHA1 CHM文件 
    20055FC3F1DB35B279F15D398914CABA11E5AD9D 
    D83D27BC15E960DD50EAD02F70BD442593E92427 
    2250174B8998A787332C198FC94DB4615504D771 
    9D4BBE09A09187756533EE6F5A6C2258F6238773 
    D167B13988AA0B277426489F343A484334A394D0 
    26A8CFB5F03EAC0807DD4FD80E80DBD39A7FD8A6 
    290321C1A00F93CDC55B1A22DA629B3FCF192101 
    2CD620CEA310B0EDB68E4BB27301B2563191287B 
    E5CB1BE1A22A7BF5816ED16C5644119B51B07837 
    SHA1 Dropped files
    290321C1A00F93CDC55B1A22DA629B3FCF192101
    2CD620CEA310B0EDB68E4BB27301B2563191287B
    E5CB1BE1A22A7BF5816ED16C5644119B51B07837
    IP地址 
    146.0.72.139 
    146.0.72.188
    

***参考来源：[reaqta](https://reaqta.com/2019/01/silence-group-targeting-russian-banks/)，由周大涛编译，转载请注明来自FreeBuf.COM**

