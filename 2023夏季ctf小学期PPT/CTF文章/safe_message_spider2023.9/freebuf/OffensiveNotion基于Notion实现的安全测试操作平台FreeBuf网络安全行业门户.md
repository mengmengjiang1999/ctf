## 关于OffensiveNotion

OffensiveNotion是一款基于Notion笔记应用程序实现的安全测试操作平台，在该工具的帮助下，广大研究人员可以轻松记录自己的红队操作。在此之前，笔记应用程序是无法帮助我们执行后渗透任务的，但在OffensiveNotion的帮助下，笔记应用不仅能成为C2，而且还能够帮助你执行渗透测试任务。

OffensiveNotion能够将后渗透代理功能与笔记应用程序的功能以及适用性结合起来，其中的代理将负责发送数据并从Notion页面接收命令，但代理通过Notion开发者API接收指令并发送结果是，C2流量会将所有内容混合到一起以增加蓝队研究人员的取证难度。

## 功能介绍

> 1、功能完整的C2平台，基于Notion笔记应用程序构建；
>
> 2、安装简单，配置好Notion开发者API账号后，将代理发送给目标设备，然后运行即可；
>
> 3、基于Rust实现的跨平台代理，使用相同代码库为Windows和Linux构建代理客户端，并提供了Python安装/控制器脚本；
>
> 4、提供了大量功能，其中包括端口扫描、权限提升、异步命令执行、文件下载、Shellcode注入等，全部都可以在一个Notion页面上实现控制和操作；
>
> 5、完整的日志记录，能够识别出运行命令的特殊语法；
>
> 6、协同工作，允许多人同时进行安全操作；
>
> 7、移动端C2，支持使用移动设备上的应用程序向世界各地的代理发送命令；
>
> 8、隐蔽性强，C2流量进行了模糊处理，并且看起来和正常的Notion流量类似；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/mttaggart/OffensiveNotion.git

## 工具使用

首先，我们需要创建一个Notion账号【[ _传送门_](https://www.notion.so/signup)】。

接下来，访问【[ _Notion_ __
_API开发者页面_](https://developers.notion.com/)】并登陆。创建一个新的“整合用户”（New
integration），然后复制用户的API密钥。

在Notion中创建一个新的页面，该页面将作为你的“监听器”，复制URL的最后一部分，即父页面ID：

![](https://image.3001.net/images/20220501/1651397232_626e527046cda033722a0.png!small)

在Notion页面的右上角，点击“分享”和“邀请”，将Notion开发者API账号添加至该页面。

访问该项目的【[
_Releases页面_](https://github.com/mttaggart/OffensiveNotion/releases)】下载Linux调试版代理。

使用“-d”以调试模式运行发布版代理，输入对应的参数值：

    
    
    husky@ubuntu:~/Desktop/OffensiveNotion/bin/linux_debug/debug$ ./offensive_notion -d
    
    [*] Starting!
    
    Getting config options!
    
    [*] Enter agent sleep interval > 5
    
    [*] Enter agent jitter time > 0
    
    [*] Enter parent page id > [...your parent page ID..]
    
    [*] Enter API Key >
    
    [...your API key...]
    
    [*] Enter Config File Path >
    
    [leave blank]
    
    [*] Enter Log Level (1-4) >
    
    2

此时，我们的监听器将会检测监听页面：

![](https://image.3001.net/images/20220501/1651397251_626e52836a146f01b1366.png!small)

最后，运行命令即可：

![](https://image.3001.net/images/20220501/1651397261_626e528d4dc8ceb3ca9d9.png!small)

## 工具使用样例

接收客户端信息并在Notion页面中：

![](https://image.3001.net/images/20220501/1651397300_626e52b4be599bab8301e.png!small)

运行Shell命令：

![](https://image.3001.net/images/20220501/1651397308_626e52bc57fabcd939b19.png!small)

配置大量命令并进行初始的安全检测：

![](https://image.3001.net/images/20220501/1651397315_626e52c36bbc8a2c14405.png!small)

执行命令：

![](https://image.3001.net/images/20220501/1651397323_626e52cb73c5af89a209a.png!small)

![](https://image.3001.net/images/20220501/1651397329_626e52d1ca1a291f24661.png!small)

将所有的发现记录到日志中：

![](https://image.3001.net/images/20220501/1651397340_626e52dcd9c8d01cbb852.png!small)

对其他主机或子网进行端口扫描：

![](https://image.3001.net/images/20220501/1651397351_626e52e7b8e454e34e1b8.png!small)

![](https://image.3001.net/images/20220501/1651397358_626e52ee7d256cd3abaed.png!small)

提升至管理员权限：

![](https://image.3001.net/images/20220501/1651397368_626e52f8d335e7b6f4c54.png!small)

![](https://image.3001.net/images/20220501/1651397377_626e53019474a9c5c18c7.png!small)

继续使用其他方法执行渗透测试任务：

![](https://image.3001.net/images/20220501/1651397388_626e530cee6746b2d408f.png!small)

与团队成员协同合作：

![](https://image.3001.net/images/20220501/1651397397_626e5315d23198c03b934.png!small)

![](https://image.3001.net/images/20220501/1651397429_626e533568af498931b73.png!small)

使用移动设备与代理进行交互：

![](https://image.3001.net/images/20220501/1651397438_626e533e4f451d3663fc3.png!small)

## 工具使用演示

![](https://image.3001.net/images/20220501/1651397757_626e547dc6343afade3fd.gif)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/mttaggart/OffensiveNotion/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **OffensiveNotion：** 【[
_GitHub传送门_](https://github.com/mttaggart/OffensiveNotion)】

## 参考资料

> [ _https://medium.com/@huskyhacks.mk/we-put-a-c2-in-your-notetaking-app-> offensivenotion-3e933bace332_](https://medium.com/@huskyhacks.mk/we-put-> a-c2-in-your-notetaking-app-offensivenotion-3e933bace332)
>
> [ _https://www.notion.so/signup_](https://www.notion.so/signup)
>
> [ _https://developers.notion.com/_](https://developers.notion.com/)

