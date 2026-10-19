由于 Go 良好的跨平台特性，在多个操作系统与架构上都能运行，所以最近使用 Go 语言编写的恶意软件越来越多，每周都会发现大量的新样本。

在四月末，研究人员通过蜜罐发现了两个新的变种（[Backdoorit](https://www.virustotal.com/gui/file/34366a8dab6672a6a93a56af7e27722adc9581a7066f9385cd8fd0feae64d4b0)和
[Caligula](https://www.virustotal.com/gui/file/fe7369b6caf4fc755cad2b515d66caa99ff222c893a2ee8c8e565121945d7a9c)），发现时在
VirusTotal 上无检出。

![image.png-98.3kB](https://image.3001.net/images/20220718/1658121068_62d4eb6c9f1b1bc624c27.png!small)Backdoorit样本检出

![image.png-52.1kB](https://image.3001.net/images/20220718/1658121069_62d4eb6d5c9b59de2cb84.png!small)Caligula样本检出

Backdoorit 与 Caligula 都是为多处理器架构编译的、跨平台 Go 恶意软件程序。

## Backdoorit

Backdoorit（版本 1.1.51562578125）是一个使用 Go 语言开发的跨平台远控木马，支持 Windows 与 Linux
操作系统。在代码中，该恶意软件也被称为 backd00rit。

其 analyse-full 命令主要是窃取与 Minecraft 相关文件和 Visual Studio 与 Intellij 的项目。

恶意软件不仅局限于这些文件，某些命令（upload、basharchive、bashupload 等）支持窃取任意文件，某些命令（run、run-binary 等）支持运行任意命令，某些命令（screenshot、ssfile 等）支持获取屏幕截图。

Backdoorit 开发者的母语应该不是英语，而是俄罗斯语。代码中的注释与字符串都是使用语法不正确的英文书写，还有一些使用俄文书写的字符串。

![image.png-32.9kB](https://image.3001.net/images/20220718/1658121070_62d4eb6e188474f0de5b8.png!small)代码注释

攻击者还针对 VimeWorld 文件进行窃取，这是一个提供 Minecraft 服务器的俄罗斯项目，这也能佐证攻击者来自俄罗斯。

![image.png-21.9kB](https://image.3001.net/images/20220718/1658121070_62d4eb6ee4116ec2e5365.png!small)针对
VimeWorld 攻击

Backdoorit 运行后会检索环境信息，例如操作系统与用户名，然后不断尝试连接 C&C 服务器。

该恶意软件通过一组函数（backd00r1t_logging_*）记录所有执行的操作，这些日志通过 uploadlogs 和 uploadlogs-file
命令上传到 C&C 服务器，在异常的情况下可以自动上传。

遇到异常（backd00r1t_backdoor_handlePanic）时，会执行以下操作：

> 将日志发送到 C&C 服务器 /api/logsC&CJSONbackd00r1t_api_SendLogs
>
> 关闭与 C&C 服务器的连接
>
> 尝试重新连接

与 C&C 服务器连接后，攻击者会获取环境上下文数据。函数 backd00r1t_backdoor_SocketConnectionHandle
负责处理所有支持的命令，并调用 backd00r1t_backdoor_printMotd 显示此类信息：

> 上次连接时间
>
> Backdoorit 版本
>
> 进程信息
>
> 活动连接
>
> 用户名
>
> 用户目录
>
> 用户 ID
>
> 登录
>
> Gid
>
> 进程路径
>
> 模块自启动状态

Backdoorit 允许攻击者远程执行命令。analyse-full 命令可以将
Desktop、Documents、Downloads、Minecraft、VimeWorld、Visual Studio 与 IntelliJ
相关文件数据生成一个 report.txt 文件，并且上传到 [Bashupload](http://bashupload.com/)上，该服务最大可以上传
50GB 的文件。

攻击者可以通过 run-binary 命令下载并执行其他恶意软件，也可以通过 shell 命令执行任意命令。

kill-switch 命令会删除恶意软件本身，并且利用 CVE-2021-24098 漏洞使 Windows 操作系统崩溃。还能够通过
CVE-2021-28312 破坏硬盘 NTFS 信息，这会使文件信息（大小、时间、权限、数据内容）完全丢失，也就丢失了感染的证据。

Backdoorit 支持的完整命令列表为：

> shell：生成可交互终端，Windows 平台使用 PowerShell、Linux 平台使用 Bash
>
> help：显示帮助信息
>
> toggle-path：启用或禁用切换路径
>
> bell：启用或禁用铃声
>
> clear-fallback：清空屏幕
>
> background-logs：确定缓冲区大小，为存储日志
>
> backdoor：显示远控木马信息
>
> clear-code：重置字体样式
>
> clear-color：重置 Shell 着色
>
> colors/color：启用或禁用 Shell 着色
>
> un-export：删除环境变量
>
> export：添加环境变量
>
> mkdir：创建文件夹
>
> exit：退出
>
> wcd：打印工作目录
>
> motd：打印状态信息
>
> get-asset：访问资产
>
> extract-asset：将资产提取到指定路径
>
> safe：禁用安全模式
>
> open-file：打开文件
>
> open：在浏览器中打开指定 URL
>
> list-windows-disks：列出磁盘信息
>
> cp：拷贝文件
>
> rm：删除文件
>
> cd：更改目录
>
> ls：显示文件信息
>
> cat：读取文件
>
> checkupdates：检查更新
>
> exploit：使用漏洞利用
>
> autostart：进行持久化
>
> autostart-update：更新持久化
>
> exec：执行带有参数的命令
>
> sysinfo：显示系统信息
>
> Screenshot/ssfile/screen：创建屏幕截图
>
> archiveapi：创建压缩文件，上传并删除本地文件
>
> Create-archive：创建压缩文件
>
> Uploadapi：将文件上传到指定服务器
>
> uploadlogs-file：上传日志文件
>
> uploadlogs：以JSON格式上传日志文件
>
> upload：将文件上传到服务器
>
> bashupload：将文件上传到 baseupload
>
> bashdownload：通过 baseupload 下载
>
> bashupload-parse：上传文件并获取链接地址
>
> basharchive：创建压缩文件并上传到 baseupload
>
> download：下载文件
>
> bashdownload：通过 URL 下载文件
>
> run：下载脚本并运行
>
> run-binary：下载脚本并运行，只支持 Windows 平台
>
> cls：清空屏幕
>
> $STOP：终止 Backdoorit 运行
>
> analyse-full：将所有相关文件信息合并上传

可见恶意软件还支持 checkupdates 命令，预计很快就能够看到 Backdoorit 的新版本。

## Caligula

Caligula 是一个新出现的 IRC 跨平台恶意程序，能够执行 DDoS 攻击。

该恶意软件是用 Go 语言编写的，针对多种架构进行编译：

> Intel 80386 32-bit
>
> ARM 32-bit
>
> PowerPC 64-bit
>
> AMD 64-bit

目前通过 WSL 环境中的 os_user_Current 函数确定底层操作系统是 Linux 还是 Windows。

![image.png-44.6kB](https://image.3001.net/images/20220718/1658121071_62d4eb6f6fdf39e24d7b2.png!small)部分代码

Caligula 基于 [Hellabot](https://github.com/whyrusleeping/hellabot)开发而来，该 Bot
能够在不丢失与 C&C 服务器的连接的情况下进行更新升级。

Caligula 重用了很多开源代码，包括 log15、fd、go-shellwords、go-isatty 和 go-colorable 等。

在野发现的样本都使用固定的信息连接 IRC 服务器：

> 主机：45.95.55.24:6667
>
> 频道：#caligula
>
> 用户名：由平台、当前用户和一个伪随机数组成，例如 [LINUX]kali-11066

如下所示，加入 Caligula IRC Net v1.0.0 僵尸网络：

![image.png-31.9kB](https://image.3001.net/images/20220718/1658121072_62d4eb7003d40b2c67272.png!small)部分代码

Caligula IRC Net v1.0.0 僵尸网络对外提供以下功能：

![image.png-21.3kB](https://image.3001.net/images/20220718/1658121072_62d4eb7083beb1a58eacf.png!small)各种攻击方式

其源代码文件如下所示：

> /root/irc/bot/attack/attack.go
>
> /root/irc/bot/attack/methods.go
>
> /root/irc/bot/attack/parser.go
>
> /root/irc/bot/attack/flags.go
>
> /root/irc/bot/network/header.go
>
> /root/irc/bot/network/ip.go
>
> /root/irc/bot/network/tcp.go
>
> /root/irc/bot/routine/timedRoutine.go
>
> /root/irc/bot/attack/methods/httpflood.go
>
> /root/irc/bot/attack/methods/sshflood.go
>
> /root/irc/bot/attack/methods/synflood.go
>
> /root/irc/bot/attack/methods/tcpflood.go
>
> /root/irc/bot/attack/methods/udpflood.go
>
> /root/irc/bot/handle.go
>
> /root/irc/bot/singleInstance/singleinstance.go
>
> /root/irc/bot.go

## 结论

由于原生的跨平台支持，与开发效率较高的特性，攻击者越来越青睐使用 Go 语言开发恶意软件，特别是针对 Linux 操作系统的恶意软件。

自然而然的，很多恶意程序相继在 GitHub 上开源，并且被攻击者广泛利用。

## IOC

> 34366a8dab6672a6a93a56af7e27722adc9581a7066f9385cd8fd0feae64d4b0
>
> 147aac7a9e7acfd91edc7f09dc087d1cd3f19c4f4d236d9717a8ef43ab1fe6b6
>
> 1945fb3e2ed482c5233f11e67ad5a7590b6ad47d29c03fa53a06beb0d910a1a0
>
> 4a1bb0a3a83f56b85f5eece21e96c509282fec20abe2da1b6dd24409ec6d5c4d
>
> 6cfe724eb1b1ee1f89c433743a82d521a9de87ffce922099d5b033d5bfadf606
>
> 71b2c5a263131fcf15557785e7897539b5bbabcbe01f0af9e999b39aad616731
>
> 99d523668c1116904c2795e146b2c3be6ae9db67e076646059baa13eeb6e8e9b
>
> fe7369b6caf4fc755cad2b515d66caa99ff222c893a2ee8c8e565121945d7a9c
>
> 97195b683fb1f6f9cfb6443fbedb666b4a74e17ca79bd5e66e5b4e75e609fd22
>
> edcfdc1aa30a94f6e12ccf3e3d1be656e0ec216c1e852621bc11b1e216b9e001

## 参考来源

> [Avast](https://decoded.avast.io/davidalvarez/go-malware-on-the-rise/)

