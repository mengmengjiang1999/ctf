4 月 26 日，Malwarebytes 发现 **一封针对约旦外交部官员进行攻击的恶意邮件** 。该邮件携带一个恶意 Excel 文档，其中包含一个名为
`Saitama`的新后门。研究人员经过分析， **确认该攻击来源于疑似与伊朗有关的攻击组织 APT 34。**

APT34 也被称为 OilRig/COBALT GYPSY/IRN2/HELIX KITTEN，被认为是来自伊朗的攻击组织。该组织从 2014
年来一直保持活跃， **针对中东国家的金融、政府、能源、化学和电信行业发起定向攻击** 。

## 恶意邮件

恶意邮件通过 Microsoft Outlook 发送给受害者，其标题为 `Confirmation Receive
Document`（意为“确认接收文档”），Excel 附件名为 `Confirmation Receive
Document.xls`。攻击者通过徽章图标伪装是约旦政府人员：

![image.png-106.1kB](https://image.3001.net/images/20220513/1652440711_627e3e875b8ad605efa78.png!small)恶意邮件

## 恶意 Excel 文件

Excel 文件中包含恶意宏代码，文档打开就会显示图片诱使受害者启用宏。

![image.png-91.7kB](https://image.3001.net/images/20220513/1652440712_627e3e88287aa32767098.png!small)恶意文档内容

当受害者启用宏代码后，图片会被替换为约旦的国徽：

![image.png-90kB](https://image.3001.net/images/20220513/1652440712_627e3e8890f857d9d8260.png!small)恶意文档内容

此时已经触发 `WorkBook_Open()`宏执行，主要部分代码如下所示：

![image.png-216.3kB](https://image.3001.net/images/20220513/1652440713_627e3e8908e9b90d455c0.png!small)恶意宏代码

> 隐藏当前工作表并显示包含徽章图像的新工作表。
>
> 调用 `eNotif`函数，通过 DNS 协议向 C&C 服务器发送宏代码执行程度的通知。例如本步骤标识符为 `zbabz`，依据 `qw + 步骤标识
> + 随机数 + 域名`构造 DNS 请求为 `qwzbabz7055.joexpediagroup.com`。
>
> 创建 TaskService 对象并获取包含当前任务列表的任务文件夹
>
> 调用 `eNotif`函数
>
> 检查计算机是否连接鼠标设备，存在的话创建 `%APPDATA%/MicrosoftUpdate`目录；创建
> Update.exe、Update.exe.config 和 Microsoft.Exchange.WenServices.dll 文件；读取
> UserForm1.label1、UserForm2.label1 和 UserForm3.label1 中的内容进行 base64
> 解码后写入上一步创建的文件；每个文件写入完成都要调用 `eNotif`函数
>
> 检查 Update.exe
> 文件是否存在，如果写入失败攻击者尝试换用另一种[开源技术](https://gist.github.com/monoxgas/1b36031c5593ebfed3229f4424f77090)将文件写入目标位置，但该方式目前尚未启用，且函数名为
> Test 可能表示攻击者正在进行技术测试将要在未来使用
>
> 最后仍然调用 `eNotif`函数

![image.png-118.1kB](https://image.3001.net/images/20220513/1652440714_627e3e8a21bcbd57cb669.png!small)测试函数

> 使用 RegisterTask 注册名为`MicrosoftUpdate`的计划任务，该计划任务用于 update.exe 持久化

![image.png-132.5kB](https://image.3001.net/images/20220513/1652440714_627e3e8ab7d5de763f326.png!small)计划任务

## Saitama 后门

最后被释放的 Payload 为一个使用 .NET 开发的后门，其 PDB
路径为`E:\Saitama\Saitama.Agent\obj\Release\Saitama.Agent.pdb`。

Saitama 后门通过 DNS 协议进行 C&C 通信，相比 HTTP
的方法更加隐蔽。攻击者在后门中巧妙地使用了压缩、随机睡眠等规避检测的手段，将恶意流量伪装成合法流量。

![1.png-1000.8kB](https://image.3001.net/images/20220513/1652440715_627e3e8b69715245d7e4c.png!small)DNS
通信过程

该后门的另一个特点是程序执行流程为一个有限状态机：

![image.png-906.2kB](https://image.3001.net/images/20220513/1652440718_627e3e8e7d5158d130444.png!small)程序状态机可视化

其部分状态为：

### BEGIN

后门的起始状态，只接受 ALIVE 启动命令。

### ALIVE

连接 C&C 服务器获取攻击者命令，C&C 服务器使用涉及 Mersenne Twister 等转换的 PRNG 算法生成，在代码中表现为 Config
类中硬编码的子域名：

![image.png-79kB](https://image.3001.net/images/20220513/1652440721_627e3e9158c61b4cbb6ee.png!small)代码

![image.png-54.6kB](https://image.3001.net/images/20220513/1652440721_627e3e91d559c22af2ec5.png!small)连接
C&C 服务器

如果 DNS 请求失败则进入 SLEEP 状态，否则进入 RECEIVE 状态。

### SLEEP / SECOND SLEEP

该状态下后门会进入睡眠模式，攻击者为了尽可能保持隐蔽。根据不同情况，睡眠时长不同。DNS 请求失败会导致睡眠 6 到 8 个小时。

![image.png-68.6kB](https://image.3001.net/images/20220513/1652440722_627e3e923ccb73f75147c.png!small)睡眠情况

### RECEIVE

接收来自 C&C 服务器的命令，每次 DNS 请求都能够接收四个字节的命令，后门将这些命令在缓冲区中拼接起来。

### DO

该状态执行来自 C&C 服务器的命令，完整的命令列表如下所示：

![image.png-52.7kB](https://image.3001.net/images/20220513/1652440722_627e3e92902caf55617f2.png!small)命令列表

![image.png-134.4kB](https://image.3001.net/images/20220513/1652440723_627e3e9309702b9bf6934.png!small)命令列表

攻击者的命令中主要是用于侦察，一些命令中明确包含着内部 IP 和内部域名（如 `ise-posture.mofagov.gover.local`），这也表明攻击者的目标非常明确且已经对受害者内部有所了解。

## SEND AND RECEIVE

命令执行结果通过该状态回传 C&C 服务器。后门将结果数据拆分，通过多个 DNS 请求将数据带出，在首个数据包中发送缓冲区大小的信息。

![image.png-124.1kB](https://image.3001.net/images/20220513/1652440723_627e3e939c8d3e5375438.png!small)回传数据

## 归因

该样本与 APT 34 组织此前使用的样本有相似之处。根据 CheckPoint 的分析，此前的样本也是通过恶意文档注册计划任务，计划任务每隔 X
分钟启动可执行文件。二者也使用了相同的反分析技术与分布告知攻击者执行阶段的方式。

APT 34 组织经常对约旦政府发起攻击，二者攻击目标也是一致的。

DNS 通信也是 APT 34 最常用的 C&C 方式，此前也使用过各种不常见的编码方式，如 base32、base36。Saitama 后门也使用
base32 编码将数据发送到
[DNSpionage](https://blog.talosintelligence.com/2018/11/dnspionage-campaign-targets-middle-east.html)部署的服务器。

综上几点，研究人员高度置信判断该次攻击与 APT 34 有关。

## IOC

> 26884f872f4fae13da21fa2a24c24e963ee1eb66da47e270246d6d9dc7204c2b  
> e0872958b8d3824089e5e1cfab03d9d98d22b9bcb294463818d721380075a52d  
> uber-asia.com  
> asiaworldremit.com  
> joexpediagroup.com

## 参考来源

> [Malwarebytes](https://blog.malwarebytes.com/threat-> intelligence/2022/05/apt34-targets-jordan-government-using-new-saitama-> backdoor/)

