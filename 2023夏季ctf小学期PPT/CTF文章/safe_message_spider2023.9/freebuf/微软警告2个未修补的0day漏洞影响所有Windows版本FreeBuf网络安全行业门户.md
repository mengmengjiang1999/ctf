**昨天，微软发布了一个新的安全公告，提醒数十亿Windows用户——两个新的未修复的0day漏洞将使黑客远程控制目标计算机。  
**

目前，这两个漏洞已经在有限的针对性攻击中使用。

![1583940004_Microsofts-tuesday-patch-mistakenly-reveals-details-of-a-0day-flaw-780x455.jpg](https://image.3001.net/images/20200324/15850185526066.jpg!small)

## 影响范围

影响Windows操作系统的所有受支持版本，包括Windows 10、Windows8.1、WindowsServer
2008/2012/2016/2019版本，甚至包括已经停止支持的Windows 7版本。

## 漏洞详情

两个漏洞位于WindowsAdobe Type
ManagerLibrary中，这是一种字体解析软件，不仅可以在使用第三方软件时解析内容，还可以在无需用户打开文件的情况下被Windows资源管理器用来在“预览窗格”或“详细信息窗格”中显示文件的内容。

漏洞主要源于Adobe Type Manager Library不当地处理了特制的多主体字体（Adobe Type1
PostScript格式），从而允许远程攻击者诱使用户打开特制文档或在Windows预览窗格中查看文档，以此来在目标系统上执行任意恶意代码。

目前尚不清楚这个漏洞会否被含有特制恶意OTF字体的网页触发，但攻击者可以通过多种其他方式利用这两个漏洞，例如通过Web分布式创作和版本控制（WebDAV）客户端服务。

此外，据Microsoft提供的信息，在运行受支持的Windows
10版本设备上，成功利用这两个0day漏洞只导致在权限有限且功能有限的AppContainer沙箱上下文中执行代码。

## 解决方法：暂无补丁

微软已经意识到了这个问题，并在开发补丁程序，预计会在4月14日发布，而在补丁发布之前，建议用户采取系列缓解措施：

> 在Windows中禁用预览窗格和详细信息窗格（禁用后，Windows资源管理器将不会自动显示OpenType字体）
>
> 禁用WebClient服务（禁用后，将阻止Web分布式创作和版本控制客户端服务）
>
> 重命名ATMFD.DLL（Adobe Type Manager字体驱动程序的文件名）

在实施缓解措施后仍然存在受到远程攻击者的攻击的可能，因此，在打开任意程序之前，建议先进行确认。

 ***本文作者：kirazhou，转载请注明来自FreeBuf.COM**

