## 关于CVE-Tracker

CVE-Tracker是一款功能强大的CVE漏洞信息收集和更新工具，该工具基于自动化ps脚本实现其功能，可以帮助广大研究人员轻松获取到最新发布的CVE漏洞信息。

CVE-Tracker采用PowerShell开发，可以在操作系统启动的时候自动运行Microsoft
Edge浏览器，并导航到两个CVE漏洞源URL，然后将浏览器切换到全屏模式并显示最新的CVE漏洞信息。

## 工具价值

作为一名安全研究人员，我们必须随时追踪最新发布的CVE漏洞信息，以便充分了解互联网上的新威胁或漏洞。实际上，这是我们日常生活中的一项常规任务。那么，我们为什么不把打开浏览器的整个过程自动化，并导航到我们的CVE漏洞源来检查最新的CVE呢？没错，CVE-Tracker的目的就是在PowerShell脚本的帮助下，将上述过程以自动化的形式实现。

在目前所有的线上CVE资源中，CVE-Tracker选择了下列两个URL作为CVE漏洞源，并引入了脚本中：

> https://cvetrends.com/
>
> https://cve.circl.lu/

注意：如果你想要修改CVE漏洞源URL地址，你可以直接使用编辑器打开项目中的cve.ps1文件，然后修改其中的URL地址即可。当然了，你也可以添加更多的漏洞源URL。

## 技术分析

当你在运行脚本时，该工具将会在下面的目录中创建一个*.bat文件（CVE_Track.bat），该脚本将允许我们自动化实现CVE漏洞信息的获取和更新：

    
    
    C:\Users\<UserName>\\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/4D0niiS/CVE-Tracker.git

下载完成后，解压代码文件即可。如果你的操作系统不允许直接执行脚本的话，可以使用下列命令解决：

    
    
    Set-ExecutionPolicy -ExecutionPolicy Bypass

除此之外，该工具还需要使用管理员权限执行。

## 工具使用

直接运行下列命令即可执行CVE-Tracker：

    
    
    .\CVE_Track.ps1

如果工具修改了操作系统配置的话，可以使用下列命令进行撤销：

    
    
    .\undo.ps1

## 工具运行样例

在下面给出的例子中，我们运行了工具脚本，系统重启并登录后，工具将会自动打开浏览器并显示最新的漏洞信息：

![](https://image.3001.net/images/20220510/1652177640_627a3ae81064bc7e98793.gif)

## 项目地址

 **CVE-Tracker：** 【[ _GitHub传送门_](https://github.com/4D0niiS/CVE-Tracker)】

## 参考链接

> [ _https://cvetrends.com/_](https://cvetrends.com/)
>
> [ _https://cve.circl.lu/_](https://cve.circl.lu/)

