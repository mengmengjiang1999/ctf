**作者：SungLin@知道创宇404实验室  
时间：2019年7月30日 **

### 一．恶意邮件样本的信息与背景

在六月份的某单位HW行动中，知道创宇HW安全团队通过创宇云图APT威胁感知系统并结合腾讯御点终端安全管理系统成功处置了一起APT攻击事件。

7月份对同一样本的补充截图如下： ![
](https://images.seebug.org/content/images/2019/08/bcdddc51-7811-4002-b5be-ff935ac3e28b.jpg-w331s)

在本次APT攻击中，攻击者通过发送鱼叉式钓鱼邮件，配合社会工程学手段诱导用户运行宏代码，进而下载尾部带有恶意payload压缩包的可执行文件。通过层层释放最终运行可窃取受害人员各类机密信息、维持权限、接收远端控制的木马。

文档打开后，会诱导用户需要开启宏才能查看被模糊的图片，一旦用户点击开启宏，恶意样本将会在用户电脑上运行、潜伏、收集相应的信息、等待攻击者的进一步指令。

![
](https://images.seebug.org/content/images/2019/08/316e557e-b4b0-401e-9377-9d9a2d9926f7.png-w331s)

该APT样本整体运行流程图如下：

![
](https://images.seebug.org/content/images/2019/08/7203bca3-0f08-4705-ae85-8cf987be2dfe.png-w331s)

### 二．宏病毒文档的提取与调试

使用OfficeMalScanner解压Office文档并提取文档所带的vba宏代码，打开Office文档启用宏后，采用快捷键Alt+F11开启宏代码的动态调试。该宏代码作为实施攻击的入口，实现了恶意样本的下载和执行。本章也将分析下载和执行的整体流程。

解压该Office文档后，宏代码被封装在xl文件夹下的vbaProject.bin文件中。

![
](https://images.seebug.org/content/images/2019/08/9d2c0385-1f00-4ca8-8a22-20c422a4d573.png-w331s)
![
](https://images.seebug.org/content/images/2019/08/5704cf05-525a-4e03-b2b2-97eb420c95ba.png-w331s)

使用OfficeMalScanner这个工具的命令info从vbaProject.bin中提取宏代码，提取完后可以知道有6个宏代码，其中fdrhfaz2osd是主要的宏代码：

![
](https://images.seebug.org/content/images/2019/08/e7a50072-2da5-44de-a836-618832fff0aa.png-w331s)
![
](https://images.seebug.org/content/images/2019/08/c157e69c-8b92-4dec-8547-446a1f262927.png-w331s)

动态调试分析宏代码，首先宏代码传入两个值u和f，分别是请求的url和写入的filepath。

![
](https://images.seebug.org/content/images/2019/08/01a896dd-e52b-4da0-b5f9-8d0b7410f3c0.png-w331s)
![
](https://images.seebug.org/content/images/2019/08/e1a561ef-f18c-4082-9448-0fa17575bc74.png-w331s)
![
](https://images.seebug.org/content/images/2019/08/2d950c7c-60aa-426e-a21e-bcdf7c34c830.png-w331s)

通过调用WinHttp.WinHttpRequest模块的方法Get请求来获取Response并写入到文件gc43d4unx.exe中。

![
](https://images.seebug.org/content/images/2019/08/fd82edfb-1296-4c1e-94d0-2fbd070a93d8.png-w331s)
![
](https://images.seebug.org/content/images/2019/08/3fa75990-037c-408c-ae78-72e966a4a5bd.png-w331s)

最后通过调用WScript.Shell来启动程序gc43d4unx.exe。

![
](https://images.seebug.org/content/images/2019/08/7f3d3bbb-016c-4c48-890d-4f15e82247af.png-w331s)

### 三．gc43d4unx.exe释放pkk.exe等文件并执行

程序gc43d4unx.exe在文件的末尾存放了一个RAR的压缩文件，gc43d4unx.exe程序通过解压缩后在用户Temp目录下的29317159文件夹释放了49个文件，并以pkk.exe
xfj=eaa命令继续执行恶意样本。

压缩文件在gc43d4unx.exe中的分布情况。

![
](https://images.seebug.org/content/images/2019/08/6e0ebeb0-f655-4826-b1b0-2383eeaee52d.png-w331s)

gc43d4unx.exe主要逻辑在对话框的回调函数sub_419B4E中，识别Rar!的头部标识

![
](https://images.seebug.org/content/images/2019/08/74d255ea-54ce-4de0-99c0-cffba336a39d.png-w331s)
![
](https://images.seebug.org/content/images/2019/08/f0c74c99-717c-410d-8d27-1d6767b4807d.png-w331s)

解压缩到映射的内存文件中，然后再挨着写到各个文件中

![
](https://images.seebug.org/content/images/2019/08/884610c4-9ca1-49ed-a79b-d70131673f70.png-w331s)

在用户Temp目录下的29317159文件夹生成隐藏文件

![
](https://images.seebug.org/content/images/2019/08/b930ba41-2fcf-45d6-bc76-e14eb293d76c.png-w331s)

最后通过SHELL32.ShellExecuteExW执行qwb.vbs代码，qwb.vbs则会使用WshShell.Run运行pkk.exe
xfj=eaa。

![ ](https://images.seebug.org/content/images/2019/08/2b326057-0fc2-4bc0-beee-ed821ff8c253.png-w331s) ![
](https://images.seebug.org/content/images/2019/08/f6145d1d-c1f6-4f05-8720-44162bacda9f.png-w331s)
![
](https://images.seebug.org/content/images/2019/08/3317579c-29dc-4c8f-9788-b4d1aa06d7b1.png-w331s)

### 四．PayLoad之pkk.exe运行分析

pkk.exe是个名为AutoIt
v3的脚本软件，可以加载自定义脚本。主要是就是通过定义DllStruct，然后再通过DllCall来调用函数。qwb.vbs运行代码为WshShell.Run”pkk.exe
xfj=eaa”，通过pkk.exe加载一个叫xfj=eaa的二进制文件。

软件先判断载入的是不是DLL，xfj=eaa是个编码后的脚本，判断后程序将会尝试解码。

![
](https://images.seebug.org/content/images/2019/08/ce5b791c-0d98-4534-83a9-06da73739746.png-w331s)

解码成功后，将解码数据写入一个临时文件中，软件将会重新创建一个进程来重新加载脚本。

![
](https://images.seebug.org/content/images/2019/08/7095b140-1dc8-46a2-b51d-38d43541775c.png-w331s)

解码后的Autolt脚本，代码被混淆了。

![
](https://images.seebug.org/content/images/2019/08/6c483368-cfc9-4217-b484-bf7fb0b63d15.png-w331s)

根据混淆的脚本，只是函数名混淆，而且脚本只是一个纯文本代码，通过重写此脚本后，可以看到基本还原的Autolt脚本代码了。

![
](https://images.seebug.org/content/images/2019/08/a1055881-9bee-449e-a162-bd59e6ddd6e3.png-w331s)

Autolt软件解析完脚本后根据字符串功能通过分发函数来执行相应的函数。

![
](https://images.seebug.org/content/images/2019/08/2ff50aab-b767-4efd-95c9-009c6fba3ea9.png-w331s)
![
](https://images.seebug.org/content/images/2019/08/3a9d2181-f07a-48f7-a5c3-0b7225a32130.png-w331s)

### 五．PayLoad之Autolt脚本分析

Autolt脚本包含的功能有：检测运行环境、修改注册表、解密最终的.net木马并运行。

通过检测进程名、设备是否有D盘等操作实现反虚拟机检测

![
](https://images.seebug.org/content/images/2019/08/1b224d61-53fd-4fa4-8002-bf436b237d14.png-w331s)

注册表禁用UAC策略函数

![
](https://images.seebug.org/content/images/2019/08/c308cf11-58bf-4376-8b04-88b9a0b6d27c.png-w331s)

注册表禁用任务管理器函数

![ ](https://images.seebug.org/content/images/2019/08/b5aa5b86-5660-49be-a3ac-cbb82ac49d47.png-w331s)

注册表开启自启函数,AuEx和ExE_c的值分别是xfj=eaa、pkk.exe。

![
](https://images.seebug.org/content/images/2019/08/85368e07-8279-4220-a605-99726344929e.png-w331s)

解密.net木马：

读取K3ys这个键值和mmm.ini文件中[Data]段到[eData]，将此数据进行字符替换正则匹配。

![
](https://images.seebug.org/content/images/2019/08/db0f6fed-1f6a-4558-bd37-6f14afcbcef6.png-w331s)
![
](https://images.seebug.org/content/images/2019/08/dfed8b74-f494-49f8-a2a2-01e18dc6d0dd.png-w331s)

载入Advapi32.dll，将K3ys键值进行Hash计算获取到真正的key，后再调用CryptDecrypt函数解密，利用ollydbg动态调试dump出解密数据，解密后的数据就是一个PE结构的程序，用IDA分析程序后，为.NET程序，这个.NET程序就是最后核心木马了，Autolt脚本后续将此PE结构加载进去，创建线程去单独运行此程序。

![
](https://images.seebug.org/content/images/2019/08/767cde76-16b3-44c4-9915-b257bf2e8d44.png-w331s)

### 六．.NET木马分析

木马主要功能进行了敏感信息收集，敏感信息收集完后会判断目标主机是否符合收集目标，以判断6个人名为主，符合本机收集目标，将会通过smtp或者ftp服务器上传文件,并且也通过web服务和c&c进行信息交流等。

木马程序的基本信息：

用.net反编译工具dnSpy打开此程序，程序入口处就是在类afg.agu，此木马经我判定进行了控制流扁平化和字符串加密的混淆方式，采用工具de4dot无法进行反混淆。

![
](https://images.seebug.org/content/images/2019/08/5bebf86b-1586-4311-bb27-441b884022b1.png-w331s)

字符串的解密：

如下图所示，经过字符串加密后静态分析已经无法分析到字符串，而且可以看出控制流进行了扁平化的处理，加密字符串的入口函数为`<Module>.\u206E()`。

![
](https://images.seebug.org/content/images/2019/08/81dda22d-b350-4515-9aee-b79785f1ee8e.png-w331s)

字符串的加密方式主要是通过传入加密的索引，通过固定值的替换与拆分计算后找到对应存储在uint型数组对象\u2009的加密Data、key、IV，\u2009数组对象大概有1047个字符串加密数组，字符串加密采用AES，模式为CBC。

编写python脚本进行了字符串解密，解密后的效果如下所示：

![
](https://images.seebug.org/content/images/2019/08/1e42c17e-00bb-475c-8d13-9fe7122a67b5.png-w331s)

字符串解密核心算法如下：

![
](https://images.seebug.org/content/images/2019/08/4020569d-7867-4a4b-86d4-ae99f0aefc73.png-w331s)

入口处获取主机名进行判断是否包含以下6个主机名，攻击目标是否符合：

![
](https://images.seebug.org/content/images/2019/08/4aba3b6b-4449-4c17-b81a-33b899843b21.png-w331s)

自我复制到C:\Users\l\AppData\Roaming\MyApp\MyApp.exe，设置为系统文件，并设置为无法删除的文件Zone.Identifier，在注册表设置为自启应用并且隐藏。

![
](https://images.seebug.org/content/images/2019/08/c56d10cd-8ad7-4adb-a29c-c0626c5c5d9f.png-w331s)
![
](https://images.seebug.org/content/images/2019/08/58af5955-b5f2-4f64-8779-427f29f8c76d.png-w331s)
![
](https://images.seebug.org/content/images/2019/08/fcebe74b-6f55-44bc-9abf-2ff5abcd4f22.png-w331s)

感谢前辈的指点，此处有错误，更正如下：定时请求 <http://checkip.amazonaws.com/> 获取出口的IP。

![
](https://images.seebug.org/content/images/2019/08/37e25b73-5b3a-4e3c-9bc6-49098c64dd6e.png-w331s)

httpweb服务器进行交互，进行信息的交流包括（"update"、"info"、"uninstall"、"cookies"、"screenshots"、"keylog"）。

![
](https://images.seebug.org/content/images/2019/08/0ee061dc-e5f7-439c-a916-6d4ae394b6ff.png-w331s)

DNS查询等：

![
](https://images.seebug.org/content/images/2019/08/3b4999d6-8130-492d-97b3-33fe3b522b36.png-w331s)

进行ftp和smtp服务操作，并且绑定了一个邮箱地址 。

![
](https://images.seebug.org/content/images/2019/08/4b812ac9-2e40-4df6-b41b-f1e98299e557.png-w331s)
![
](https://images.seebug.org/content/images/2019/08/6187f59a-bcb2-4187-b0df-8925cc7a4ac2.png-w331s)

以下可能是此地址的密码：

![
](https://images.seebug.org/content/images/2019/08/414f149a-f8c5-4114-9dac-2de6297b4910.png-w331s)

收集信息如下：

系统信息 |  
---|---  
ManagementObjectSearcher managementObjectSearcher = new
ManagementObjectSearcher("root\CIMV2", "SELECT * FROM Win32_VideoController")
|  
managementObjectSearcher2 = new ManagementObjectSearcher("SELECT * FROM
Win32_Processor"); |  
浏览器 |  
---|---  
CatalinaGroup\Citrio\User Data | liebao\User Data  
Fenrir Inc\Sleipnir5\setting\modules\ChromiumViewer |
Yandex\YandexBrowser\User Data  
360Chrome\Chrome\User Data | Chedot\User Data  
Elements Browser\User Data | Epic Privacy Browser\User Data  
CocCoc\Browser\User Data | MapleStudio\ChromePlus\User Data  
Chromium\User Data | Torch\User Data  
Iridium\User Data | Comodo\Dragon\User Data  
7Star\7Star\User Data | Amigo\User Data  
BraveSoftware\Brave-Browser\User Data | CentBrowser\User Data  
Vivaldi\User Data | QIP Surf\User Data  
Kometa\User Data | Orbitum\User Data  
Sputnik\Sputnik\User Data | uCozMedia\Uran\User Data  
Coowon\Coowon\User Data |  
ftp列表 |  
---|---  
\CoreFTP\sites.idx | \FTP Navigator\Ftplist.txt  
\SmartFTP\Client 2.0\Favorites\Quick Connect\ |  
\SmartFTP\Client 2.0\Favorites\Quick Connect*.xml |
\Ipswitch\WS_FTP\Sites\ws_ftp.ini  
\cftp\Ftplist.txt | \FTPGetter\servers.xml  
\FTP Navigator\Ftplist.txt |  
Mail列表 |  
---|---  
\VirtualStore\Program Files\Foxmail\mail\ | \Opera Mail\Opera Mail\wand.dat  
Software\IncrediMail\Identities\ |  
注册表 |  
---|---  
"HKEY_CURRENT_USER\Software\FTPWare\COREFTP\Sites\" + str + "Host" |
"HKEY_CURRENT_USERSoftwareFTPWareCOREFTPSites" + str + "Port"  
"HKEY_CURRENT_USERSoftwareFTPWareCOREFTPSites" + str + "User" |
"HKEY_CURRENT_USERSoftwareFTPWareCOREFTPSites" + str + "PW"  
"HKEY_CURRENT_USERSoftwareFTPWareCOREFTPSites" + str + "Name" |  
  
http通信信息

![
](https://images.seebug.org/content/images/2019/08/23659dd5-f46a-4c27-ba8c-22a7042417f6.png-w331s)

### 七．安全建议

强烈推荐采用知道创宇云图、腾讯御点等产品，提高企业安全保护，降低外部威胁水平。

知道创宇云图威胁监测系统系列产品，实时分析网络全流量，结合威胁情报数据及网络行为分析技术，深度检测所有可疑活动。文件检测采用全面沙箱分析，通过在沙箱（Sandbox）中运行（行为激活/内容“引爆”）各种文件，分析文件行为，识别出未知威胁。网络检测与文件检测同步进行，采用情报共享机制，构筑检测生态圈，准确、快速地掌握攻击链条，以便进一步采取相关措施，将APT（高级持续性威胁）攻击阻止在萌芽状态。

腾讯御点是腾讯出品、领先国际的企业级安全服务提供者。依托腾讯19年的安全经验积累，为企业级用户提供私有云防病毒和漏洞修复解决方案。御点具备终端杀毒统一管控、修复漏洞统一管控，以及策略管控等全方位的安全管理功能，可帮助企业管理者全面了解、管理企业内网安全状况、保护企业安全。

### 八．IOC信息

domain & IP：

    
    
    animalrescueskyward.co.za
    mail.privateemail.com
    checkip.amazonaws.com
    
    129.232.200.208:443
    198.54.122.60
    52.206.161.133
    34.197.157.64
    18.211.215.84
    52.202.139.131
    34.233.102.38   
    52.6.79.229

相关 hash：

7b478598b056d1f8e9f52f5ef1d147437b7f0da5  
a73816ebcfc07d6da66de7c298a0912a3dd5d41a  
b65884f1e833ea3eec8a8be4c7057a560da4511e  
8827b2c1520fb41034d5171c5c4afd15158fd4a3  
491b221f68013a2f7c354e4bb35c91fe45a1c0c0

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1011/>

