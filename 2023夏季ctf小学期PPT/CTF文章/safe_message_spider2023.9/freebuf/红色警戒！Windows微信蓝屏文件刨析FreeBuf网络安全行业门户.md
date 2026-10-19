## 样本

![](https://image.3001.net/images/20210121/1611222652_60094e7cd9b971dde0f13.png!small)

核心代码为：file:///globalroot/device/condrv/kernelconnect

## 受灾画面

![](https://image.3001.net/images/20210121/1611222689_60094ea13613832cda3cc.png!small)

## 分析

![](https://image.3001.net/images/20210121/1611222721_60094ec1330c4324ee883.png!small)

.url文件

url格式的文件是一种网页文件，只要接触就会触发访问

漏洞分析可见开普勒安全团队此前发的文章《Windows10使用浏览器崩溃复现及分析》，内容如下：

看到微博某位大佬发了一条漏洞

![](https://image.3001.net/images/20210121/1611222756_60094ee4d5a41aa87b45b.png!small)

## 复现

我们直接在浏览器输入这个地址：

    
    
    \\.\globalroot\device\condrv\kernelconnectbr

![](https://image.3001.net/images/20210121/1611222798_60094f0eecea14695c93a.png!small)

成功复现，电脑蓝屏：

![](https://image.3001.net/images/20210121/1611222827_60094f2b852fadccfa794.png!small)

## 分析

看报错为：system_service_exception

![](https://image.3001.net/images/20210121/1611222861_60094f4d098c53d8ba31d.png!small)

造成这个报错的官方反馈是：系统服务错误

在国外Bleepingcomputer论坛，我们看到一篇这样的文章：

    
    
    https://www.bleepingcomputer.com/news/security/windows-10-bug-crashes-your-pc-when-you-access-this-location/

![](https://image.3001.net/images/20210121/1611222908_60094f7c59ea9f92ec572.png!small)

文章指出：

自10月以来，Windows安全研究员 Jonas Lykkegaard 在推特上发表了很多次推文，讲述了一条路径，该路径会立即导致Windows
10崩溃并在进入Chrome地址栏中时显示BSOD。

当开发人员想要直接与Windows设备进行交互时，他们可以将Win32设备命名空间路径作为各种Windows编程功能的参数传递。例如，这允许应用程序直接与物理磁盘进行交互，而无需通过文件系统。

Lykkegaard告诉BleepingComputer，他发现了“控制台多路复用器驱动程序”的以下Win32设备名称空间路径，他认为该路径用于“内核/用户模式ipc”。当以各种方式打开路径时，即使来自低特权用户，也会导致Windows
10崩溃。

    
    
    \\.\globalroot\device\condrv\kernelconnect

连接到该设备时，开发人员应传递“ attach”扩展属性以与该设备正确通信。

![](https://image.3001.net/images/20210121/1611222940_60094f9ce487d1a27127f.jpg!small)

Lykkegaard发现，如果由于不正确的错误检查而尝试不通过属性而连接到路径，则会导致异常，从而导致Windows 10中的蓝屏死机（BSOD）崩溃。

更糟糕的是，特权低的Windows用户可以尝试使用此路径连接到设备，从而使计算机上执行的任何程序都很容易崩溃Windows 10。

在我们的测试中，我们已经确认此错误在Windows 10 1709版和更高版本中存在。BleepingComputer无法在早期版本中对其进行测试。

BleepingComputer上周与Microsoft联系，以了解他们是否已经知道该错误以及是否会修复该错误。

微软发言人对BleepingComputer表示：“微软对调查已报告的安全问题的客户承诺，我们将尽快为受影响的设备提供更新。”

## 威胁人员可以滥用该错误

尽管目前尚不确定此漏洞是否可用于远程代码执行或提升特权，但仍可以将其用作计算机上的拒绝服务攻击。

Lykkegaard与BleepingComputer共享了一个Windows URL文件（.url），其设置指向\\\\.\ globalroot \
device \ condrv \ kernelconnect。下载文件后，Windows
10会尝试从有问题的路径中呈现URL文件的图标，并自动使Windows 10崩溃。

![](https://image.3001.net/images/20210121/1611222998_60094fd68fc11e027b874.png!small)

此后，BleepingComputer发现了许多其他利用此bug的方法，包括在Windows登录时自动导致BSOD的方法。

在现实生活中，该漏洞可能会被威胁角色滥用，他们可以访问网络并希望在攻击过程中掩盖自己的踪迹。

如果他们具有管理员凭据，则可以远程执行访问网络上所有Windows
10设备上的此路径的命令，以使它们崩溃。在网络上造成的破坏可能会延迟调查或阻止管理控件检测到特定计算机上的攻击。

2017年，威胁参与者在台湾远东国际银行（FEIB）抢劫银行时使用了类似的攻击场景。在该攻击中，威胁行为者在网络上部署了爱马仕勒索软件，以延迟对攻击的调查。

## 防护方法

仅对windows10系统有效，其它系统不受影响

windows微信用户可关闭自动下载

![](https://image.3001.net/images/20210121/1611223032_60094ff8a3f4a32bd8645.png!small)更多方式（.html
.exe）：

    
    
    1.<html>2.<head>3.</head>4.<body>>5.<script>document.location = 6.'\\\\.\\globalroot\\device\\condrv\\kernelconnect';</script>7.</body></html>
    
    
    // BSOD.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。//#include <iostream>#include <Windows.h>int main(){WCHAR fileName[] = L"\\\\.\\globalroot\\device\\condrv\\kernelconnect";WIN32_FILE_ATTRIBUTE_DATA data;GetFileAttributesEx(fileName, GetFileExInfoStandard, &data);}

吾爱破解大牛分析：

    
    
    https://www.52pojie.cn/thread-1354077-1-1.html

![](https://image.3001.net/images/20210121/1611223511_600951d7c1bd37286fd6d.png!small)

其他利用方式XSS漏洞：

    
    
    <script>document.location = '\\\\.\\globalroot\\device\\condrv\\kernelconnect';</script><script>document.location = 'file://./globalroot/device/condrv/kernelconnect';</script>

请做好个人防护，谨防漏洞威胁。

> 本文转载自开普勒安全团队

