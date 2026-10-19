![](https://image.3001.net/images/20220711/1657544447_62cc1eff8bddb775bd0dd.png!small)

## 关于PowerGram

PowerGram是一款功能强大的跨平台Telegram
Bot工具，该工具基于纯PowerShell开发，支持在Windows、Linux和macOS系统上运行。如需使用PowerGram，只需要安装PowerShell
4或更高版本并连接网络即可。

Bot和Telegram服务器之间的所有通信连接都会使用HTTPS进行加密，但所有的请求都是以GET方法发送的，因此拦截起来是比较容易的。

## 工具要求

> PowerShell 4.0或更高版本

## 工具获取

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/JoelGMSec/PowerGram

或者直接访问该项目的【[ _GitHub首页_](https://github.com/JoelGMSec/PowerGram)】下载工具的zip文件。

## 工具帮助信息

    
    
    .\PowerGram -h
    
     
    
      ____                         ____                      
    
     |  _ \ __ __      __ __ _ __ / ___|_ __ __ _ _ __ ___   
    
     | |_) / _ \ \ /\ / / _ \ '__| |  _| '__/ _' | '_ ' _ \  
    
     |  __/ (_) \ V  V /  __/ |  | |_| | | | (_| | | | | | |
    
     |_|   \___/ \_/\_/ \___|_|   \____|_|  \__,_|_| |_| |_|
    
     
    
      ------------------- by @JoelGMSec -------------------  
    
     
    
     Info:  PowerGram is a pure PowerShell Telegram Bot
    
            that can be run on Windows, Linux or Mac OS
    
     
    
     Usage: PowerGram from PowerShell
    
            .\PowerGram.ps1 -h 显示帮助信息
    
            .\PowerGram.ps1 -run 开启PowerGram Bot
    
     
    
            PowerGram from Telegram
    
            /getid 通过Bot获取你的聊天ID
    
            /help  显示所有可用的命令
    
     
    
     Warning: All commands will be sent using HTTPS GET requests
    
              You need your Chat ID & Bot Token to run PowerGram

## 工具使用

在使用之前，我们需要将相关的参数选项和令牌写入到工具的配置文件中：

![](https://image.3001.net/images/20220711/1657544516_62cc1f44be035eb0cf329.png!small)

配置完成后，我们可以使用下列命令启动Bot，并等待接收执行命令。出于安全因素考虑，我们添加了一个白名单机制，以保证Bot不会处理未经授权的用户命令：

    
    
    PowerGram.ps1 -run

如需将用户添加到白名单中，我们需要为新创建的Bot打开一个私聊框，并写入/getid以获取用户的唯一标识符：

![](https://image.3001.net/images/20220711/1657544526_62cc1f4eba2c7c9587e83.png!small)

最后，我们只需要将我们的聊天ID写入到相应的变量中即可。此时，我们的基础配置便完成了。

接下来，我们需要关闭任何正在运行的PowerGram实例并重新启动它以加载我们在代码中引入的新变量。完成后，我们将收到类似于以下内容的欢迎消息：

![](https://image.3001.net/images/20220711/1657544533_62cc1f559bcd35e524e44.png!small)

下图显示的是Bot支持的所有操作命令：

![](https://image.3001.net/images/20220711/1657544540_62cc1f5ca4ade4a05aeda.png!small)

    
    
    /hi =使用此命令，我们将知道 PowerGram 是否正在运行
    
    /help =在聊天窗口中显示此帮助消息
    
    /wakeonlan =通过 WOL 打开同一网络上的 PC
    
    /upload =该命令将允许我们上传文件
    
    /download =此命令将允许我们下载文件
    
    /exec =通过 PowerShell 远程执行代码
    
    /getid =返回我们的聊天 ID
    
    /kill =关闭远程 PowerGram 进程

## 工具运行截图

![](https://image.3001.net/images/20220711/1657544555_62cc1f6b4c125a4ec58e7.png!small)![](https://image.3001.net/images/20220711/1657544563_62cc1f734113a6f01e765.png!small)

![](https://image.3001.net/images/20220711/1657544571_62cc1f7bcf3e4e0b3c3f4.png!small)

![](https://image.3001.net/images/20220711/1657544579_62cc1f831ae95e703b0a0.png!small)

![](https://image.3001.net/images/20220711/1657544587_62cc1f8b34a5faf61b2ca.png!small)

![](https://image.3001.net/images/20220711/1657544594_62cc1f92e5819c36cc69c.png!small)

![](https://image.3001.net/images/20220711/1657544602_62cc1f9a83f023d9fc3ac.png!small)

![](https://image.3001.net/images/20220711/1657544609_62cc1fa1863417f2dec73.png!small)

  

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/JoelGMSec/PowerGram/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **PowerGram** ：【[ _GitHub传送门_](https://github.com/JoelGMSec/PowerGram)】

## 参考资料

> [ _https://darkbyte.net/powergram-un-sencillo-bot-para-telegram-escrito-en-> powershell_](https://darkbyte.net/powergram-un-sencillo-bot-para-telegram-> escrito-en-powershell)
>
> [ _https://darkbyte.net/_](https://darkbyte.net/)
>
> [ _https://twitter.com/JoelGMSec_](https://twitter.com/JoelGMSec)
>
> [ _https://docs.microsoft.com/es-es/powershell/scripting/install/installing-> powershell-on-linux?view=powershell-7.2_](https://docs.microsoft.com/es-> es/powershell/scripting/install/installing-powershell-on-> linux?view=powershell-7.2)

