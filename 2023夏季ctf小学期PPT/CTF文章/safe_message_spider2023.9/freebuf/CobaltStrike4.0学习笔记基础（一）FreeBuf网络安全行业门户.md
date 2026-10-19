# **Cobalt Strike 4.0** 学习笔记-基础（一）

## 一、前言

记录自己的学习，分享给更多人的，是让自己印象加深的最好方式。

哈哈，菜鸟一枚，希望大家多多指教

## 二、基础概念

### 1、什么是Cobalt Strike ？

Cobalt Strike是一个为对手模拟和红队设计的平台主要是侧重于后渗透。

后渗透即为完成想要在目标网络中达到的目的的一个攻击步骤。

注：PTES（渗透测试执行标准），这个标准大家可以参考一下，标准的渗透测试执行标准

PTES 对于后渗透的标准是：确定受损机器的价值，并保持对机器的控制以备后

### 2、分布式和团队行动

![image](https://image.3001.net/images/20210420/1618917387_607eb80b43ddd4aa2c6cd.png!small)

 **这是cs一个亮点** ，它可构造多个服务器联动行动，

 **2.1、一个服务器连接团队：**

  * 使用相同的会话

  * 分享主机、捕获的数据和下载的文件

  * 通过一个共享的事件日志交流  
2.2、客户端连接多个服务端：

进行分工合作，通过Cobalt Strike →新建连（New Connection）,当连接到多个团队服务器，一个切条会出现在窗口底部

![image](https://image.3001.net/images/20210420/1618917449_607eb849f3adb7ac554f4.png!small)  
![image](https://image.3001.net/images/20210420/1618917524_607eb894e8649bc26b18e.png!small)

团队服务器分工合作：

  * 架构多台服务器列如：钓鱼服务器，侦查服务器，后渗透服务器，攻击服务器，长控服务器

  * 分解整个攻击链，避免单点失败，方便服务器之间的权限传递

### 3、基本功能介绍

 **3.1、文件目录**

![image](https://image.3001.net/images/20210420/1618917597_607eb8dd8ea387b8698d5.png!small)

    
    
    agscript 			拓展应用的脚本`
    c2lint 				用于检查 profile 的错误异常
    teamserver 			服务端程序
    cobaltstrike，cobaltstrike.jar 	客户端程序 (java 跨平台)`
    logs 				目录记录与目标主机的相关信息`
    update，update.jar 	用于更新 CS`
    third-party 		第三方工具`
    

#### **3.2、服务端**

  * 启动./teamserver [/path/to/c2.profile] [YYYY-MM-DD]

    *  **必需，团队服务器IP**

    *  **必需，连接服务器的密码（建议强密码，容易被爆破）**

    *  **< path/to/c2.profile >可选参数 指定C2通信配置文件**

    *  **可选参数 所有payload的终止时间**

####  **3.3、客户端**

  * 双击启动

    * 服务器IP

    * 默认端口50050 (可在teamserver 文件中修改端口，建议修改)

    * 连接的客户端名字

    * 团队服务器配置的密码

![image](https://image.3001.net/images/20210420/1618917620_607eb8f4e7b9b19bd84a4.png!small)

注：第一次连接至此团队服务器， Cobalt Strike 会询问你是否承认这个团队服务器的 SHA256 hash，点击ok就行。

####  **3.4、界面功能介绍**

本人英语不才，整了一个中文版，哈哈！来个中英文互相介绍。

#####  **3.4.1、首页**

![image](https://image.3001.net/images/20210420/1618917710_607eb94eddb48d95dafde.png!small)

#####  **3.4.2、Cobalt Strike模块**

![image](https://image.3001.net/images/20210420/1618917731_607eb963cbb0f6a183291.png!small)

    
    
    New Connection 	新的连接(支持连接多个服务器端)
    Preferences 	偏好设置(设置Cobal Strike界面、控制台、以及输出报告样，TeamServer连接记录等)
    Visualization 	可视化(展示输出结果的形式)
    xxx Interfaces 	xxx接口
    Listenrs 	监听器(创建Listener)
    Script Manager 	脚本管理
    Close 		关闭
    

##### **3.4.3 、视图（view）模块**

![image](https://image.3001.net/images/20210420/1618917782_607eb99635891f7d54f39.png!small)

    
    
    Applications 	应用(显示受害者机器的应用信息)
    Credentials 	凭证(通过hashdump或Mimikatz抓取过的密码都会储存在这里)
    Downloads 		文件下载
    Event Log		日志(主机上线记录以及团队协作聊天记录)
    Keystrokes 		键盘记录
    Proxy Pivots 	代理信息
    Screenshots 	屏幕截图
    Script Console 	脚本控制台
    Targets 		显示目标主机
    Web Log 		Web日志
    

##### **3.4.4 、攻击（Attacks）**

![image](https://image.3001.net/images/20210420/1618917803_607eb9abcb4a5b6444326.png!small)

    
    
    生成后门（Packages）
    HTML Application 	  生成恶意的HTA木马文件
    MS Office Macro 	  生成office宏病毒文件
    Payload Generator 	  生成各种语言版本的payload
    USB/CD AutoPlay 	  生成利用自动播放运行的木马文件
    Windows Dropper 	  捆绑器，能够对文档类进行捆绑
    Windows Executable 	  生成可执Payload
    Windows Executable(S) 把包含payload,Stageless生成可执行文件(包含多数功能)
    
    钓鱼攻击（WEB Drive-by）
    Scripted Web Delivery 	提供Web服务，便于下载和执行PowerShell Payload.
    Signed Applet Attack 	启动一个Web服务以提供自签名Java Applet的运行环境
    Smart Applet Attack 	自动检测Java版本并利用已知的exploits绕过security
    System Profiler 		用来获取一些系统信息
    
    邮件钓鱼 （Spear Phish） 这个模块得实战出真理哈哈！
    

另外两个模块就不介绍了，看看图吧

![image](https://image.3001.net/images/20210420/1618917836_607eb9ccc98f6f5780bb8.png!small)![image](https://image.3001.net/images/20210420/1618917850_607eb9da266c12beb548a.png!small)

### 4、会话界面

Cobalt Strike 有多种可视化展示 ，可通过，工具栏进行切换。

  * 目标栏：展示了每个目标的ip地址，最左侧表示了它的操作系统，带有红色闪电的表示此目标有一个通信的会话

![image](https://image.3001.net/images/20210420/1618917909_607eba150d13eafaeb14d.png!small)

  * 会话表：显示了那些Beacon回到了这台CS在这里，你将看到每个 Beacon 的外网 IP 地址、内网 IP 地址、该 Beacon 的出口监听器、此 Beacon 最后一次回连的时间，以及其他信息

注释：Beacon 是 Cobalt Strike 用于模拟高级威胁者的 payload

![image](https://image.3001.net/images/20210420/1618917931_607eba2b15e24295debe9.png!small)

  * Pivot 图：每一个 Beacon 会话都有一个对应的图，防火墙图标代表你 Beacon payload 的流量出口点。 **绿色虚线表示使用了** **HTTP** **或** **HTTPS** **连接出网。黄色虚线表示使用** **DNS** **协议出网**

![image](https://image.3001.net/images/20210420/1618917949_607eba3dc251f49dc03b7.png!small)

### 5、控制台

它是与Beacon会话、脚本等交互，也可以通过控制台与其他队友进行交流。

  * tab键可以补全命令

![image](https://image.3001.net/images/20210420/1618917965_607eba4da2925d3105831.png!small)

具体命令参数见下

    
    
    beacon> help
    argue                     进程参数欺骗
    blockdlls                 阻止子进程加载非Microsoft DLL
    browserpivot              注入受害者浏览器进程
    bypassuac                 绕过UAC提升权限
    cancel                    取消正在进行的下载
    cd                        切换目录
    checkin                   强制让被控端回连一次
    clear                     清除beacon内部的任务队列
    connect                   Connect to a Beacon peer over TCP
    covertxxx                 部署Covert xxx客户端
    cp                        复制文件
    dcsync                    从DC中提取密码哈希
    desktop                   远程桌面(VNC)
    dllinject                 反射DLL注入进程
    dllload                   使用LoadLibrary将DLL加载到进程中
    download                  下载文件
    downloads                 列出正在进行的文件下载
    drives                    列出目标盘符
    elevate                   使用exp
    execute                   在目标上执行程序(无输出)
    execute-assembly          在目标上内存中执行本地.NET程序
    exit                      终止beacon会话
    getprivs                  Enable system privileges on current token
    getsystem                 尝试获取SYSTEM权限
    getuid                    获取用户ID
    hashdump                  转储密码哈希值
    help                      帮助
    inject                    在注入进程生成会话
    jobkill                   结束一个后台任务
    jobs                      列出后台任务
    kerberos_ccache_use       从ccache文件中导入票据应用于此会话
    kerberos_ticket_purge     清除当前会话的票据
    kerberos_ticket_use       Apply 从ticket文件中导入票据应用于此会话
    keylogger                 键盘记录
    kill                      结束进程
    link                      Connect to a Beacon peer over a named pipe
    logonpasswords            使用mimikatz转储凭据和哈希值
    ls                        列出文件
    make_token                创建令牌以传递凭据
    mimikatz                  运行mimikatz
    mkdir                     创建一个目录
    mode dns                  使用DNS A作为通信通道(仅限DNS beacon)
    mode dns-txt              使用DNS TXT作为通信通道(仅限D beacon)
    mode dns6                 使用DNS AAAA作为通信通道(仅限DNS beacon)
    mode http                 使用HTTP作为通信通道
    mv                        移动文件
    net                       net命令
    note                      备注
    portscan                  进行端口扫描
    powerpick                 通过Unmanaged PowerShell执行命令
    powershell                通过powershell.exe执行命令
    powershell-import         导入powershell脚本
    ppid                      Set parent PID for spawned post-ex jobs
    ps                        显示进程列表
    psexec                    Use a service to spawn a session on a host
    psexec_psh                Use PowerShell to spawn a session on a host
    psinject                  在特定进程中执行PowerShell命令
    pth                       使用Mimikatz进行传递哈希
    pwd                       当前目录位置
    reg                       Query the registry
    rev2self                  恢复原始令牌
    rm                        删除文件或文件夹
    rportfwd                  端口转发
    run                       在目标上执行程序(返回输出)
    runas                     以其他用户权限执行程序
    runasadmin                在高权限下执行程序
    runu                      Execute a program under another PID
    screenshot                屏幕截图
    setenv                    设置环境变量
    shell                     执行cmd命令
    shinject                  将shellcode注入进程
    shspawn                   启动一个进程并将shellcode注入其中
    sleep                     设置睡眠延迟时间
    socks                     启动SOCKS4代理
    socks stop                停止SOCKS4
    spawn                     Spawn a session 
    spawnas                   Spawn a session as another user
    spawnto                   Set executable to spawn processes into
    spawnu                    Spawn a session under another PID
    ssh                       使用ssh连接远程主机
    ssh-key                   使用密钥连接远程主机
    steal_token               从进程中窃取令牌
    timestomp                 将一个文件的时间戳应用到另一个文件
    unlink                    Disconnect from parent Beacon
    upload                    上传文件
    wdigest                   使用mimikatz转储明文凭据
    winrm                     使用WinRM横向渗透
    wmi                       使用WMI横向渗透
    

基础的学习就先到这，如果有不足欢迎大家评论指出，本人小菜菜。

以上使用的技术仅用于学习交流目的。

> 参考连接：[Cobalt Strike mannual 4.0]，Cobalt Strike 官网  
> https://blog.csdn.net/qq_34801745/article/details/109391166

