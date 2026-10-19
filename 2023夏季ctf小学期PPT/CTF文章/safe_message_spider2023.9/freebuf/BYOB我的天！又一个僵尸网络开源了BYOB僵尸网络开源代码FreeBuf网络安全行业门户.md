## 严正声明：本项目仅供教育目的使用，请不要将其用于非法目的。  

## 前言

 **大家没看错！现在，又有一个僵尸网络开源了自己的，这个僵尸网络就是BYOB！**

![](https://image.3001.net/images/20181110/1541862491_5be6f45b0f81b.png!small)

## BYOB（搭建你自己的僵尸网络）

BYOB是一个开源项目，该项目给研究人员和开发者提供了一个能够搭建和操作基础僵尸网络的框架。大家都知道，僵尸网络每年都会感染数百万台联网设备，为了研究现代僵尸网络的威胁能力和应对方案，大家可以根据各自对复杂恶意软件的理解，基于该框架来研究现代僵尸网络。

在该框架的帮助下，开发人员可以轻松实现自己的代码并添加新的工具和功能，整个过程无需自己从零编写RAT或C2服务器。

> 注：RAT的核心功能是在目标主机内存中加载C2托管的任意代码/文件，并在无需触碰目标磁盘的情况下执行恶意代码。

## 客户端

该框架能够生成无法被检测到的Payload以及不受限制的后渗透模块。

1、 远程导入：从服务器端远程导入第三方数据包，而无需将其写入目标磁盘或下载安装。

2、 无需触碰磁盘：客户端不会向目标磁盘写入任何数据，包括临时文件在内。因为远程导入的任意代码是在目标内存中动态加载的，并直接导入进当前运行的进程中。

3、
无需依赖组件：客户端运行的是Python标准库，并会从远程服务器动态导入第三方非标准库，然后通过标准Python编译器进行代码编译，所以无需安装其他依赖组件。

4、
一键添加新功能：只要你的C2服务器处于运行状态，任何你拷贝到./byob/modules/目录的Python脚本、模块或数据包都可以自动导入到每一个远程客户端上。

5、 开发自己的模块：目录./byob/modules/中已经提供了一份基础的模块模版，大家可以根据自己的需要来自定义修改。

6、 完全可升级：每一个客户端都会定期检查服务器是否推送了新版本。

7、 平台依赖：所有的功能都是用Python编写的，客户端可以根据自己所在的平台来编译出可执行程序（Windows或macOS）。

8、 绕过防火墙：客户端通过反向TCP连接来与C2服务器通信，这样可以绕过大多数防火墙。

9、 防逆向分析：默认配置下，如果检测到了虚拟机或沙盒环境，客户端会放弃执行。

10、Payload加密：主要的客户端Payload采用了一个256位随机密钥来进行加密。

## 模块化

客户端可以远程导入后渗透模块。

1、 键盘记录(byob.modules.keylogger)：记录目标用户的击键信息。

2、 屏幕截图(byob.modules.screenshot)：获取目标用户屏幕截图。

3、 摄像头(byob.modules.webcam)：查看摄像头实时画面/视频。

4、 勒索(byob.modules.ransom)：加密文件，并勒索比特币。

5、 Outlook(byob.modules.outlook)：从本地Outlook账号读取、搜索和加载邮件信息。

6、 数据包嗅探(byob.modules.packetsniffer)：嗅探主机网络的数据包或上传.pcap文件。

7、 持续感染(byob.modules.persistence)：使用了5种不同的方法实现主机的持续感染。

8、 智能手机(byob.modules.phone)：从目标手机中读取、搜索和上传文字消息。

9、 提权(byob.modules.portscanner)：尝试绕过UAC并实现管理员提权。

10、端口扫描(byob.modules.process)：扫描本地网络的开放端口。

11、进程控制(byob.modules.icloud)：枚举、监控和终止目标主机的运行进程。

12、iCloud(byob.modules.spreader)：探测macOS主机登录的iCloud账号。

## 服务器端

远程命令控制服务器提供了数据库和命令控制台。

1、 基于命令行的用户接口：命令行接口可以通过反向TCPShell访问和控制目标主机。

2、 SQLite数据库：轻量级数据库用于存储客户端主机的识别信息。

3、 客户端-服务器架构：所有的Python包和模块都可以通过服务器来让客户端自动加载。

### 核心

生成器和服务器端使用了下列核心框架模块：

1、 Utilities (byob.core.util): 提供了很多实用函数。

2、 Security (byob.core.security):Diffie-Hellman IKE(AES-256-OCB, AES-256-CBC,
XOR-128)。

3、 Loaders (byob.core.loaders):从服务器端远程导入数据包、模块和脚本。

4、 Payloads (byob.core.payloads):通过反向TCPshell远程导入依赖组件、数据包和模块。

5、 Stagers (byob.core.stagers): 生成唯一的Payload以避免安全分析和检测。

6、 Generators(byob.core.generators): 动态生成功能代码。

7、 Database (byob.core.database):处理C2服务器和SQLite数据库之间的交互。

8、 Handler (byob.core.handler):HTTP POST请求处理器，负责处理远程文件上传。

## 项目地址

> GitHub：【[传送门](https://github.com/malwaredllc/byob)】

 ***
参考来源：[byob](https://github.com/malwaredllc/byob)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

