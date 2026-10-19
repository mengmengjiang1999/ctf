BYOB是个开源项目，提供构建和运行基本僵尸网络的框架，以加深现代僵尸网络的理解。  

该库包含4个主要部分：

## 服务器

  
usage: server.py [-h] [-v] [--host HOST] [--port PORT] [--database DATABASE]  

控制服务器

  * 基于控制台的用户界面：简化的控制台界面，用于通过反向TCP shell远程控制客户端主机，提供对客户端主机的直接终端访问

  * 持久性SQLite数据库：轻量级数据库，用于存储有关客户端主机的标识信息，允许反向TCP shell会话通过断开任意持续时间并启用长期侦察来保持

  * 客户端 - 服务器体系结构：本地安装的所有python软件包/模块都自动可供客户端远程导入，而无需将其写入目标计算机的磁盘，允许客户端使用需要未安装在目标计算机上的软件包的模块

## 客户端

`usage: client.py [-h] [-v] [--name NAME] [--icon ICON] [--pastebin API]
[--encrypt] [--obfuscate] [--compress] [--compile] host port [module [module
...]]`

使用有效负载，远程导入生成完全不可检测的客户端

  * 远程导入：从服务器远程导入第三方软件包，而无需将其写入磁盘或下载/安装它们

  * 不写入磁盘：客户端从不向磁盘写入任何内容 - 甚至不是临时文件（进行零IO系统调用），因为远程导入允许将任意代码动态加载到内存中并直接导入到当前正在运行的进程中

  * 零依赖（甚至不是Python本身）：客户端只运行python标准库，从服务器远程导入任何非标准软件包/模块，并可以使用独立的python解释器编译成为任何平台/格式化的可移植二进制可执行文件体系结构，允许它在任何东西上运行，即使目标主机上缺少Python本身

  * 只需单击一下即可添加新功能：`./byob/modules/`当您的命令和控制服务器运行时，您要复制到目录的任何python脚本，模块或程序包将自动变为可远程导入并可由每个客户端直接使用

  * 编写自己的模块：`./byob/modules/`目录中提供了一个基本模块模板，使您自己编写模块成为一个简单，无障碍的过程

  * 在不增加文件大小的情况下运行无限模块：使用远程导入添加无限功能，而无需向客户端的文件大小添加单个字节

  * 完全可更新：每个客户端将定期检查服务器是否有可用于远程导入的新内容，并且如果添加/删除了任何内容，将动态更新其内存资源

  * 平台无关：一切都是用Python（与平台无关的语言）编写的，生成的客户端可以选择编译成可移植的可执行文件（Windows）或捆绑到独立的应用程序（macOS）中

  * 绕过防火墙：客户端通过反向TCP连接连接到命令和控制服务器，这将绕过大多数防火墙，因为默认过滤器配置主要阻止传入连接

  * 针对防病毒的反措施：通过阻止来自产生已知防病毒产品名称的进程来避免被防病毒软件分析

  * 加密有效负载以防止分析：主客户端有效负载使用随机256位密钥加密，该密钥仅存在于与其一起生成的有效负载stager中

  * 防止逆向工程：默认情况下，如果检测到虚拟机或沙箱，客户端将中止执行

## 模块

  
11个远程导入的开发后模块  

  1. Keylogger（`byob.modules.keylogger`）：记录用户的击键和输入的窗口名称
  2. 屏幕截图（`byob.modules.screenshot`）：截取当前用户桌面的截图
  3. 网络摄像头（`byob.modules.webcam`）：查看实时流或从网络摄像头捕获图像/视频
  4. Ransom（`byob.modules.ransom`）：加密文件并生成随机BTC钱包以支付赎金
  5. Outlook（`byob.modules.outlook`）：从本地Outlook客户端读取/搜索/上传电子邮件
  6. Packet Sniffer（`byob.modules.packetsniffer`）：在主机网络上运行数据包嗅探器并上传.pcap文件
  7. Persistence（`byob.modules.persistence`）：使用5种不同的方法在主机上建立持久性
  8. 电话（`byob.modules.phone`）：从客户端智能手机读取/搜索/上传短信
  9. Escalate Privileges（`byob.modules.escalate`）：尝试UAC绕过以获得未经授权的管理员权限
  10. 端口扫描程序（`byob.modules.portscanner`）：扫描本地网络以查找其他在线设备和打开端口
  11. Process Control（`byob.modules.process`）：list / search / kill / monitor当前正在主机上运行的进程

## 核心

  
生成器和服务器使用的6个核心框架模块  

  1. Utilities（`byob.core.util`）：许多模块使用的各种实用程序函数
  2. Handlers（`byob.core.handlers`）：请求处理程序以从客户端接收已完成任务的结果
  3. 安全性（`byob.core.security`）：Diffie-Hellman IKE和3种加密模式（AES-256-OCB，AES-256-CBC，XOR-128）
  4. Loaders（`byob.core.loaders`）：从服务器远程导入任何包/模块/脚本
  5. Payloads（`byob.core.payloads`）：反向TCP shell，旨在远程导入依赖项，包和模块
  6. Stagers（`byob.core.stagers`）：生成独特的有效载荷分级器以防止分析和检测
  7. Generators（`byob.core.generators`）：所有动态生成客户端生成器代码的函数
  8. Database（`byob.core.database`）：处理命令和控制服务器与SQLite数据库之间的交互

GitHub：https://github.com/colental/byob

