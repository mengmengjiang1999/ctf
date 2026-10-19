![](https://image.3001.net/images/20210927/1632700167_61510707c7539933e389a.png!small)

## 关于Penelope

Penelope是一款功能强大的Shell处理工具，该工具的主要功能是在利用RCE漏洞的过程中，替代netcat并作为Shell捕捉器来使用。该工具可以在Linux和macOS上工作，只需要安装并配置好Python
3环境即可。该工具没有任何的第三方依赖，使用起来非常简单，跨平台性也很好。

## 功能介绍

> 自动将Shell更新为PTY；
>
> 记录与目标的交互历史信息；
>
> 从目标下载文件；
>
> 将文件上传至目标设备；
>
> 将预设脚本上传至目标设备；
>
> 生成备份Shell；
>
> 支持多会话；
>
> 支持多个监听器；
>
> 可以通过利用漏洞导入并在同一终端上获取Shell；

Penelope通过设置“set DisablePayloadHandler
True”来禁用Metasploit的默认Shell处理器，并与Metasploit结合使用。

该工具支持Windows Shell，但还未实现自动更新功能。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/brightio/penelope.git

## 工具基础使用

    
    
    penelope.py                   # Listening for reverse shells on 0.0.0.0:4444
    
    penelope.py 5555              # Listening for reverse shells on 0.0.0.0:5555
    
    penelope.py 5555 -i eth0      # Listening for reverse shells on eth0:5555
    
    penelope.py -c target 3333    # Connect to a bind shell on target:3333

## 工具使用样例

### 使用场景一

> 在不使用参数的情况下执行Penelope，并获取反向Shell；
>
> 按下F12键来解绑会话，并切换至主菜单；
>
> 运行“recon”命令向目标设备上传预设值的特权脚本；
>
> 再次与会话交互，确认脚本已成功上传；
>
> 再次按下F12键来解绑会话，并从目标下载/etc目录；
>
> 按下Ctrl + D键盘终止会话并退出运行；

![](https://image.3001.net/images/20210927/1632700196_61510724c0c91ad35cec9.png!small)

### 使用场景二

> 添加额外的监听器并显示所有的监听器；
>
> 与会话1交互；
>
> 生成额外的备份会话；
>
> 显示所有的会话；

![](https://image.3001.net/images/20210927/1632700204_6151072cd469f4f4e83b3.png!small)

## 命令行参数

    
    
    positional arguments:
    
      PORT                  Port to listen/connect to depending on -i/-c options. Default: 4444
    
    Reverse or Bind shell?:
    
      -i , --address        IP Address or Interface to listen on. Default: 0.0.0.0
    
      -c , --connect        Bind shell Host
    
    Hints:
    
      -a, --hints           Show sample payloads for reverse shell based on the registered listeners
    
      -l, --interfaces      Show the available network interfaces
    
      -h, --help            show this help message and exit
    
    Verbosity:
    
      -Q, --silent          Show only errors and warnings
    
      -X, --extra-silent    Suppress all logging messages
    
    Logging:
    
      -L, --no-log          Do not create session log files
    
      -T, --no-timestamps   Do not include timestamps on logs
    
    Misc:
    
      -H, --no-history      Disable shell history on target
    
      -P, --plain           Just land to the menu
    
      -S, --single-session  Accommodate only the first created session
    
      -C, --no-attach       Disable auto attaching sessions upon creation
    
      -U, --no-upgrade      Do not upgrade shells
    Debug:
    
      -d, --debug           Show debug messages
    
      -NP, --no-python      Simulate python absence on target
    
      -NB, --no-bash        Simulate bash absence on target

## 菜单选项

    
    
    use [sessionID|none]
    
      Select a session
    
    sessions [sessionID]
    
      Show active sessions. When followed by <sessionID>, interact with that
    
      session
    
    interact [sessionID]
    
      Interact with a session
     
    kill [sessionID|all]
    
      Kill a session
    
    download <glob>...
    
      Download files and folders from the target
    
    open <glob>...
    
      Download files and folders from the target and open them locally 
    
    upload <glob|URL>...
    
      Upload files and folders to the target. If URL is specified then it is
    
      downloaded locally and then uploaded to the target
    
    recon [sessionID]
    
      Upload preset reconnaissance scripts to the target
    
    spawn [sessionID]
    
      Spawn a new session. Whether it will be reverse or bind, depends on
    
      the current session.
    
    upgrade [sessionID]
    
      Upgrade the session's shell to "PTY". If it fails attempts to upgrade
    
      it to "Advanced". If this fail too, then falls back to "Basic" shell.
     
    dir|. [sessionID]
    
      Open the session's local folder. If no session is selected, opens the
    
      base folder.
    
    listeners [<add|stop> <Interface|IP> <Port>]
    
      Add or stop a Listener. When invoked without parameters, it shows the
    
      active Listeners.
    
    connect <Host> <Port>
    
      Connect to a bind shell
    
    hints
    
      Show sample commands to run on the targets to get reverse shell, based
    
      on the registered listeners
    
    reset
    
      Reset the local terminal
    
    history
    
      Show menu history
    
    help [command]
    
      Show menu help or help about specific command
     
    DEBUG
    
      Open debug console
    
    SET [<param> <value>]
    
      Set options. When invoked without parameters it shows current options
    
     exit|quit|q|Ctrl+D
    
      Exit penelope

## 项目地址

 **Penelope：** 【[ _GitHub传送门_](https://github.com/brightio/penelope)】

