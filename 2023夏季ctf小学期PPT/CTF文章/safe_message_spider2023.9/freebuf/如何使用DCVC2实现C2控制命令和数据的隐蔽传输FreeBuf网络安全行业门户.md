![](https://image.3001.net/images/20230803/1691068898_64cba9e2eb7183c658cb3.png!small)

## 关于DCVC2

DCVC2是一款功能强大的数据传输工具，该工具可以通过语音信道并使用RTP分组来传输所有数据，而且整个过程不会在文字聊天中留下操作痕迹。

该工具能够与多种常见的操作系统兼容，并且能够利用Discord的语音通道发送数据以实现命令和控制操作。该工具基于[
_DiscordGo_](https://stealthbits.com/stealthaudit-for-active-directory-product/\(https:/github.com/bwmarrin/discordgo\))实现其功能，且完全通过实时协议（RTP）运行，是一款基于命令行运行的工具，这也就意味着所有的操作都需要通过Windows/Linux/OSX上的终端来执行。

## 工具要求

> 1、一个Discord账号；
>
> 2、一台Discord服务器；
>
> 3、支持在设置中将语音聊天速度提高到96kbps；
>
> 4、两个Discord bot（需要给bot提供管理员权限：【[
> _文档_](https://discordpy.readthedocs.io/en/stable/discord.html)】）；

## 工具下载

由于该工具基于Go语言开发，因此我们首先需要在本地设备上安装并配置好Go语言环境。

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/3NailsInfoSec/DCVC2.git

然后切换到项目目录中，使用go build命令完成服务器端和代理端代码编译：

    
    
    cd DCVC2
    
    go mod download
    
    go build server.go
    
    go build agent.go

## 工具使用

运行完DCVC2的服务器端和代理端之后，你将会看到两端都加入了指定的语音聊天频道：

![](https://image.3001.net/images/20230803/1691068930_64cbaa022903f74971904.png!small)

Shell命令执行：

    
    
    cmd> whoami
    
     
    
    desktop-3kjj3kj\sm00v

除了基本的Shell用法之外，DCVC2还添加了两个硬编码的附加项：

    
    
    cmd> screenshot
    
    screenshotting..............................................
    
     
    
    &
    
     
    
    cmd> download
    
    download file path>C:\Users\sm00v\Downloads\34954477.jpg
    
    ............................................................

## 项目地址

 **DCVC2** ：【[ _GitHub传送门_](https://github.com/3NailsInfoSec/DCVC2)】

## 参考资料

> [ _https://stealthbits.com/stealthaudit-for-active-directory-> product/(https://github.com/bwmarrin/discordgo)_](https://stealthbits.com/stealthaudit-> for-active-directory-product/\(https:/github.com/bwmarrin/discordgo\))
>
> [ _https://www.3nailsinfosec.com/post/using-discord-s-voice-channel-> for-c2-operations_](https://www.3nailsinfosec.com/post/using-discord-s-> voice-channel-for-c2-operations)
>
> [
> _https://discordpy.readthedocs.io/en/stable/discord.html_](https://discordpy.readthedocs.io/en/stable/discord.html)
>
> [ _https://twitter.com/sm00v_](https://twitter.com/sm00v)
>
> [ _https://github.com/sm00v_](https://github.com/sm00v)

