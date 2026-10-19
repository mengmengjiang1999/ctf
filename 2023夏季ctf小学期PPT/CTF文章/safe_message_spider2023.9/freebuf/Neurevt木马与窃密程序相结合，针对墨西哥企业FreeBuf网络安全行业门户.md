> 近日，思科发现攻击者正在将 Neurevt 木马和窃密程序相结合，针对墨西哥的公司发起攻击。

![image.png-233.3kB](https://image.3001.net/images/20210827/1630075416_6128fa18ec42f3dbf9fbc.png!small)

## 入侵

恶意行为从混淆的恶意 PowerShell 命令开始，该命令会下载一个 Neurevt 家族的恶意文件。

![image.png-47.4kB](https://image.3001.net/images/20210827/1630075417_6128fa198eaf6df674736.png!small)

攻击者绕过端点的 PowerShell 执行策略，下载新的可执行文件。该域名于 2021 年 6 月 21 日在 NameCheap
注册，saltoune.xyz 解析的 IP 地址为 162.213.251.176。该域名的全球遥测数据如下所示：

![image.png-79.1kB](https://image.3001.net/images/20210827/1630075418_6128fa1a110ad499deac4.png!small)

执行会创建很多文件：

![image.png-99.7kB](https://image.3001.net/images/20210827/1630075418_6128fa1a92eb607deb56d.png!small)

![image.png-48.3kB](https://image.3001.net/images/20210827/1630075419_6128fa1b71e7d30f0596d.png!small)

恶意软件创建一个线程设置注册表并执行 VBS 文件：

![image.png-39.3kB](https://image.3001.net/images/20210827/1630075420_6128fa1c0326e7cbf3d29.png!small)

WScript.exe 进程读取文件 C:\LMPupdate\set\435246.vbs并启动 Windows Shell 运行批处理文件
C:\LMPupdate\set\183.bat。

![image.png-48.9kB](https://image.3001.net/images/20210827/1630075420_6128fa1c7a823f8eee33d.png!small)

bat 脚本文件将 C:\LMPupdate\set\x0329847998重命名为加密的 RAR 文件 43939237cx.rar。运行
unpakedree.exe 使用 67dah9fasdd8kja8ds9h9sad密码提取 RAR 文件的内容。

![image.png-29.4kB](https://image.3001.net/images/20210827/1630075421_6128fa1d05c58b06cc9b1.png!small)

启动另一个脚本 48551.bat：

![image.png-276.8kB](https://image.3001.net/images/20210827/1630075421_6128fa1d94775bcca7fa9.png!small)

通过进程注入，进一步拉取可执行文件。

> <http://morningstarlincoln.co.uk/>的 IP 地址为 79.170.44.146。下载文件 SHA256 为
> 35617cfc3e8cf02b91d59209fc1cd07c9c1bc4d639309d9ab0198cd60af05d29
>
> [http://russk17.icu](http://russk17.icu/)的 IP 地址为 23.95.225.105。下载文件 SHA256
> 为 4d3ee3c1f78754eb21b3b561873fab320b89df650bbb6a69e288175ec286a68f

在前者的文件中，存在许多属于墨西哥主要金融机构的字符串。

![image.png-168.2kB](https://image.3001.net/images/20210827/1630075422_6128fa1e9d0a09780b33e.png!small)

![image.png-108.3kB](https://image.3001.net/images/20210827/1630075423_6128fa1f6c5d3df11d1ee.png!small)

恶意软件窃取凭据和双因子 Token，定义的函数调用如下所示：

![image.png-643kB](https://image.3001.net/images/20210827/1630075424_6128fa207cba4da6414cd.png!small)

## 持久化

恶意软件修改了多个注册表项：HKLM\Software\Microsoft\Windows NT\CurrentVersion\Image File
Execution Options\RSTRUI.exe、HKLM\ Software\Microsoft\Windows
NT\CurrentVersion\Image File Execution
Options\3K77573KMES7W.exe、HKCU\Software\Microscoft\Windows\CurrentVersion\Runonce、HKCU\Software\Microscoft\Windows\CurrentVersion\Run、HKLM\Software\Microscoft\Windows\CurrentVersion\Runonce。

恶意软件通过调用 GetTokenInformation 和 AdjustTokenPrivileges 来提权。

![image.png-290.9kB](https://image.3001.net/images/20210827/1630075426_6128fa223ee695dc437e7.png!small)

![image.png-390.8kB](https://image.3001.net/images/20210827/1630075427_6128fa23593ba66d1aea2.png!small)

## 检测逃避

Explorer.exe 进程禁用 Windows 防火墙，还修改Internet Explorer 安全域配置。攻击者通过允许未签名的 ActiveX
控件、关闭阻止弹出窗口和更改 Java 权限等选项来削弱 Internet Explorer 的安全性。

![image.png-36.8kB](https://image.3001.net/images/20210827/1630075428_6128fa24b8c44199a9fce.png!small)

一个注册表中存放了大量数据（HKEY_CURRENT_USER\Software\AppDataLow\Software{B56DA420-0B5E-0394-E271-7DACAF8D4BB5}\14FD1F9A\46a66dd53b3040）旨在隐藏攻击者。

![image.png-128.5kB](https://image.3001.net/images/20210827/1630075429_6128fa2529080efd5d4e9.png!small)

Explorer.exe 进程尝试连接 VirtualBox 驱动程序、 VirtualBox DLL 和 VMware DLL。此外还会使用
GetTickCount 和 IsDebuggerPresent 进行反分析。

## 发现

恶意软件会检查操作系统、枚举系统驱动、可用硬盘和目录信息、Java 运行时环境、键盘布局列表等信息。

![image.png-374.5kB](https://image.3001.net/images/20210827/1630075429_6128fa25bee9352f7bc93.png!small)

![image.png-204.9kB](https://image.3001.net/images/20210827/1630075431_6128fa277784c8effdd8a.png!small)

攻击者还可以截取失陷主机的屏幕截图。

![image.png-293.2kB](https://image.3001.net/images/20210827/1630075432_6128fa2830ed483d20b7d.png!small)

复制剪切板的数据：

![image.png-529.4kB](https://image.3001.net/images/20210827/1630075433_6128fa292b4be05c1c508.png!small)

将屏幕缓冲区的数据写入文件：

![image.png-298kB](https://image.3001.net/images/20210827/1630075434_6128fa2ac11206ae7cbc3.png!small)

通过调用 GetKeyboardLayout、ActivateKeyboardLayout 设置键盘布局并调用 GetKeyboardState 将 256
个虚拟键的状态复制到缓冲区并调用 GetKeyState 来检索键盘控制字符状态。Neurevt
会监视来自对话框、消息框、菜单或滚动条中的按键和鼠标活动的输入事件而生成的消息。

![image.png-147.6kB](https://image.3001.net/images/20210827/1630075435_6128fa2bd6e2fb360bb32.png!small)

Neurevt 还会等待来自多个对象的消息、查看消息、检查是否是 Unicode 窗口、获取消息、将虚拟键的扫描码转换为字符然后发送。

![image.png-358.6kB](https://image.3001.net/images/20210827/1630075436_6128fa2c8e971397c68b9.png!small)

## 数据渗漏

失陷主机使用 HTTP POST 将数据发送到 C&C 服务器。

![image.png-639.6kB](https://image.3001.net/images/20210827/1630075438_6128fa2e30c665ddfe632.png!small)

## 结论

这个版本的 Neurevt
恶意软件具备多种功能，一旦被感染，攻击者就可以控制失陷主机并修改系统设置进行持久化驻留。该木马可以访问操作系统、用户帐户信息、银行网站凭据、截取屏幕截图并连接到
C&C 服务器以窃取知识产权和个人信息等。该木马可能会影响个人用户和组织导致数据泄露或声誉受损，最终导致重大损失。

## IOC

> russk18.icu  
> russk19.icu  
> russk20.icu  
> russk21.icu  
> russk22.icu  
> moscow13.at  
> moscow11.at  
> 86aab09b278fe8e538d8cecd28f2d7a32fe413724d5ee52e2815a3267a988595  
> b5624eea08b241314b8bd13ee9429449c53085a6bb2bcc481655f1f28b4314122  
> 4d3ee3c1f78754eb21b3b561873fab320b89df650bbb6a69e288175ec286a68f  
> 35617cfc3e8cf02b91d59209fc1cd07c9c1bc4d639309d9ab0198cd60af05d29  
> http://saltoune.xyz/pb/aa.exe  
> https://saltoune.xyz/pb/aa.exe  
> http://morningstarlincoln.co.uk/site/bmw/studi.exe  
> http://russk17.icu/mailo/seer.exe

## 参考来源

> [TalosIntelligence](https://blog.talosintelligence.com/2021/08/neurevt-> trojan-takes-aim-at-mexican.html)

