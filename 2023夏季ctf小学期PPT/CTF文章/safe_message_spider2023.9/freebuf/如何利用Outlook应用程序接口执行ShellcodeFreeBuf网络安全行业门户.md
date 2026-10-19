![](https://image.3001.net/images/20210329/1616994214_60615fa6ebcf8b47b0ea6.png!small)  

## BadOutlook

BadOutlook是一款恶意Outlook读取器，也是一个简单的概念验证PoC，它可以利用Outlook应用程序接口（COM接口）并根据特定的触发主题栏内容来在目标系统上执行Shellcode。

通过利用Microsoft.Office.Interop.Outlook命名空间，开发人员可以代表整个Outlook应用程序来做任何事情。这也就意味着，
新的应用程序可以做很多事情，比如说阅读电子邮件、查看文档或回收站、以及发送邮件等等。

如果预先包含了C#
Shellcode加载器的话，攻击者将能够利用武器化的应用程序实例将一封带有触发器主题栏内容以及Base64编码Shellcode邮件Body内容的恶意电子邮件发送至目标主机。应用程序之后将能够读取这封恶意电子邮件，并在目标主机中执行嵌入在恶意电子邮件中的Shellcode。

## 注意事项

  * 我们可以使用这个PoC来构建一个完整的C2框架，它依赖于电子邮件作为一种通信手段（在这种情况下，植入的恶意代码从不直接与互联网通信）；
  * 有可能会弹出安全警告，并通知用户某个应用程序正在试图访问Outlook数据；
  * 当管理员修改注册表时，可以将其关闭；
  * 测试表明，将此进程注入到Outlook客户端不会导致出现警报；

## 源码获取

广大研究人员可以使用下列命令将该PoC项目源码克隆至本地：

    
    
    git clone https://github.com/S4R1N/BadOutlook.git

## 概念验证PoC

 **Outlook应用程序触发器：**

![](https://image.3001.net/images/20210329/1616994245_60615fc56fd1bb1a49e5a.png!small)

 **创建Shellcode触发邮件事件：**

![](https://image.3001.net/images/20210329/1616994252_60615fcc4dd3e41388453.png!small)

 **Outlook客户端接收电子邮件：**

![](https://image.3001.net/images/20210329/1616994258_60615fd289c5054cb9374.png!small)

 **BadOutlook应用程序执行Shellcode：**

![](https://image.3001.net/images/20210329/1616994266_60615fda3589563e4f9c0.png!small)

## 项目地址

BadOutlook：【[ _GitHub传送门_](https://github.com/S4R1N/BadOutlook)】

## 参考资料

  * [ _https://docs.microsoft.com/en-us/dotnet/api/microsoft.office.interop.outlook.application?view=outlook-pia_](https://docs.microsoft.com/en-us/dotnet/api/microsoft.office.interop.outlook.application?view=outlook-pia)
  * [ _https://docs.microsoft.com/en-us/outlook/troubleshoot/security/a-program-is-trying-to-send-an-email-message-on-your-behalf_](https://docs.microsoft.com/en-us/outlook/troubleshoot/security/a-program-is-trying-to-send-an-email-message-on-your-behalf)

