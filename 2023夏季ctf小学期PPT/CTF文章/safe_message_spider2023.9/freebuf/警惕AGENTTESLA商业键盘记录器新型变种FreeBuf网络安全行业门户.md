## 一、概述

 **近日，安天CERT（安全研究与应急处理中心）发现了Agent Tesla商业键盘记录器的新型变种。Agent
Tesla原本只是个简单的键盘记录器，记录用户的每一次按键并回传至攻击者服务器。自2014年发展至今，Agent
Tesla的开发者为其添加了更多的功能，使其从一个简单的键盘记录器变成了一个具有多种功能的商业键盘记录器。Agent
Tesla会监控并收集受害者的键盘输入、剪贴板内容、屏幕截图信息以及受害主机上已安装的各种软件的凭据并采用HTTP POST的方式回传数据。当前，Agent
Tesla已在互联网上贩卖，有被滥用的风险和趋势。**

此次发现的Agent
Tesla新型变种与之前的版本功能类似，只是回传数据的方式有所改变，增加了另外两种回传数据的方式，一种是使用SMTP协议，将收集到的数据发送到攻击者的电子邮箱；另外一种是将数据传送到FTP服务器上。但经分析后发现，虽然Agent
Tesla新型变种提供了三种回传数据的方式，但只使用了邮件来回传数据，其他两种通信方式则未曾使用。

Agent
Tesla新型变种的主要攻击形式为钓鱼邮件，邮件附件中包含内嵌了恶意软件的Word文档。当用户打开文件后，便会被诱导双击文档中的蓝色图标，一旦用户双击图标，便释放出了恶意软件。Agent
Tesla新型变种威胁着个人与企业的信息、财产安全，用户应加强防范意识，减少被攻击的概率。

经验证，安天智甲终端防御系统（英文简称IEP，以下简称安天智甲）可实现对Agent Tesla新型变种以及早期各种变种的有效防御。

## 二、事件样本分析

### 2.1 样本关系

  
![Clipboard
Image.png](https://image.3001.net/images/20180507/15256725489309.png!small)

图2- 1 样本关系

本次捕获到的样本为Word文档，打开Word文档后，显示“DOUBLE CLICK TO ENABLE CLEAR
VIEW”，提示用户如果想要获取更清晰的视图就要双击这个图标，以此来诱惑用户双击运行恶意程序。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256725629464.png!small)

图2- 2 恶意文档图示

当用户双击时，会调用UpdatedPO.exe文件，该文件为可执行程序，其执行便开始了恶意代码的启动，并导致最终执行具有核心功能的恶意代码No-name2.exe（详细过程见图2-1）。本报告后续分析主要针对No-name2.exe进行。

![Clipboard
Image.png](https://image.3001.net/images/20180507/152567257433.png!small)

图2- 3 双击蓝色图标后询问是否运行程序

### 2.2 样本标签

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256725914792.png!small)

表 2 1 Word文档

### 2.3 样本功能

No-name2.exe是一个经过代码混淆处理的.Net程序。其可以记录受害主机的键盘输入、窃取剪贴板数据，捕捉受害主机屏幕截图，从受害主机摄像头获取文件，收集受害主机信息和收集已安装软件的凭据，并将以上信息全部发送给攻击者。

No-name2.exe运行后会结束系统中与自身重复的进程，然后判断受害主机系统是否为Windows7、Windows8、Windows10中的一个，以及UAC是否是开启的。若符合上述条件，则设置EnableLUA的值为0，即禁用“administrator
in Admin Approval Mode”。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256726083493.png!small)

图2- 4判断受害主机系统是否开启了UAC

No-name2.exe向C2服务器发送卸载命令，若服务器响应的数据中包含“uninstall”字符串，则程序会删除它在计算机上写入的信息并退出。接着程序向C2服务器发送更新命令。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256726237512.png!small)

图2- 5发送卸载指令

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256726336555.png!small)

图2- 6 发送更新指令

No-name2.exe会判断当前程序是否为%appdata%\DaVita Inc\DaVita
Inc.exe，若该文件夹以及文件不存在，则创建该文件夹并将当前程序复制到DaVita Inc.exe，并将文件属性设置为隐藏。设置DaVita
Inc.exe为开机自启动。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256726482605.png!small)

图2- 7 判断当前运行文件是否为DaVita Inc.exe

No-name2.exe程序在记录键盘输入时，先获取受害主机的Windows标题并将其放入一段html代码中，然后捕捉受害者的按键，并将受害者的按键转换为html代码。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256726582254.png!small)

图2- 8 窃取键盘数据内容

受害者每次更改剪贴板内容时，No-name2.exe程序便捕获剪贴板内容，然后将收集到的数据存入一段html代码中。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256726692859.png!small)

图2- 9 窃取剪贴板内容

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256726813400.png!small)

图2- 10 发送键盘记录和剪贴板内容

No-name2.exe每隔20分钟便会获取受害主机的屏幕截图并将其保存到指定的文件中（%appdata%\ScreenShot\screen.jpeg），然后使用命令“screenshots”将其发送给C2服务器。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256726948810.png!small)

图2- 11 发送受害主机屏幕截图

No-name2.exe每隔20分钟便会从受害主机的摄像头获取图片并将其保存到指定的文件中（%appdata%\CamCampture\webcam.jpeg），然后使用命令“webcam”将其发送给C2服务器。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256727042526.png!small)

图2- 12 收集摄像头图片信息并发送

No-name2.exe会收集已安装软件的凭证并发送给C2服务器。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256727159144.png!small)

图2- 13 软件凭据

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256727263419.png!small)

图2- 14 软件凭据

No-name2.exe窃取以下软件的凭证信息。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256727383129.png!small)

表 2 2 No-name2.exe针对的软件列表

### 2.4 加解密方式

在No-name.exe中，字符串进行了简单的异或加密操作，资源文件的加密方式也是由异或加密构成的。资源文件解密函数如下。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256727499338.png!small)

图2- 15 资源解密

在No-name2.exe中，使用AES加密方式将所有字符串进行了加密，如：函数名、注册表信息、参数等。字符串解密函数如下。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256727639905.png!small)

图2- 16 字符串解密

### 2.5 自保护机制

No-name2.exe会从自身的Player资源区提取一个守护程序，释放到%temp%目录中，防止UpdatedPO.exe结束运行。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256727781792.png!small)

图2- 17 生成保护程序

该守护程序也是一个.Net程序，每隔900ms检查一次UpdatedPO.exe是否正在运行，一旦UpdatedPO.exe结束运行则再次启动UpdatedPO.exe。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256727897686.png!small)

图2- 18 保护UpdatedPO.exe

### 2.6 网络通信方式

No-name2.exe有3种方式将从受害主机上获取到的信息发送给攻击者，分别是HTTP
POST、邮件和FTP。分析后发现，数据回传的方式被硬编码成了“SMTP”，所以在Agent
Tesla变种的通信过程中，实际上只使用了邮件来回传数据。在此猜测使用邮件回传数据的原因是C2服务器的URL已经被检测为“恶意网站”。为了更详细的展现此变种，本文对以上三种通信方式均进行了分析。

1、HTTP POST通信方式

No-name2.exe会构建字符串及数据包，然后以HTTP POST方式向C2服务器提交获取到的信息。参数格式如下：

![Clipboard
Image.png](https://image.3001.net/images/20180507/1525672796817.png!small)

表 2 3 命令字段解释

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256728045100.png!small)

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256728112541.png!small)

图2- 19 以HTTP POST方式提交信息

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256728175107.png!small)

图2- 20 数据包头

C2服务器接收的命令如下所示。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256728254774.png!small)

表 2 4 C2命令

2、邮件通信方式

No-name2.exe使用邮箱log****@lifftrade.com给攻击者发送邮件，收件邮箱和发件邮箱均为log****@lifftrade.com，邮件中包含了从受害主机中窃取到的信息。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256728325220.png!small)

图2- 21 以邮件的方式发送信息

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256728392267.png!small)

图2- 22 邮件信息

3、FTP通信方式

No-name2.exe还可以FTP的方式提交窃取到的信息。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256728466092.png!small)

图2- 23 以FTP方式发送信息

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256728523385.png!small)

图2- 24 FTP格式

## 三、防护建议

### 3.1 预防

恶意代码是因为用户双击蓝色图标（如下图所示）才启动的，因此，若遇到类似文档，请不要双击蓝色图标或可疑链接。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256728594690.png!small)  

图3- 1 蓝色图标

### 3.2 手动清除

1\. Agent
Tesla新型变种在运行后会在临时文件夹（C:\Users\用户名\AppData\Local\Temp\）释放UpdatedPO.exe和保护文件%s%s%s.exe（该保护文件的文件名是三个随机的字符串）。手动清除首先需要结束这两个进程。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256728667535.png!small)

图3- 2 UpdatedPO.exe和保护文件%s%s%s.exe进程

2\. 结束进程后，需要在C:\Users\用户名\AppData\Local\Temp\文件夹下找到这两个文件，然后将这两个文件删除。

![Clipboard
Image.png](https://image.3001.net/images/20180507/1525672873869.png!small)

图3- 3临时文件夹中的恶意文件

3\. 恶意代码的某些设置会在重启电脑后生效。因此重启电脑后，DaVita
Inc.exe才会出现在C:\Users\用户名\AppData\Roaming\DaVita
Inc\目录下，自启动的注册表项才能被找到。恶意代码将DaVita
Inc.exe设置成了开机自启动，需要找到注册表项HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\DaVita
Inc，并删除相关注册表。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256728808247.png!small)

图3- 4 删除此注册表项

4\. 同时，因电脑重启使DaVita Inc.exe启动并在临时文件夹下释放保护程序%s.exe，这时需要结束这些程序然后再删除DaVita
Inc.exe和%s.exe。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256728887187.png!small)

图3- 5 自启动的DaVita Inc.exe

5\.
将HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System中EnableLUA的值修改为0x1，开启被恶意代码关闭的UAC。

![Clipboard
Image.png](https://image.3001.net/images/20180507/15256728966924.png!small)

图3- 6开启UAC

### 3.3 安天智甲有效防护

经验证，安天智甲可实现对Agent Tesla变种的有效防御。

## 四、小结

通过分析发现，Agent
Tesla新型变种在对抗杀软、对抗分析部分进行了升级，使用了多层调用。在每一层的可执行程序中，使用不同的编译语言进行编译生成，该变种使用了VB，VC++，.Net三种编译器，而且使用了多种加密方式，给分析增加了难度。

从样本功能的演进来看，该家族样本的变化并不大，其主要目的都是窃取屏幕截图、键盘记录、多款软件的凭证和网络摄像头截图等，使用多种方式进行回传。但是从与安全软件的对抗来看，其进行了大量的改进升级，使用了多个可执行文件进行包裹，层层释放，几乎每层都进行了细致的加密处理，由此也可以看出攻击者的技术水平在进行不断的升级。

 *** 本文作者安天实验室，转载注明来自FreeBuf**  

