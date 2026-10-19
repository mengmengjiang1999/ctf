![](https://image.3001.net/images/20210422/1619088596_608154d413e3c5402386b.jpg!small)

## Defeat-Defender

Defeat-Defender是一款功能强大的Batch批处理脚本，该脚本可以帮助广大研究人员在渗透测试的过程中，完全禁用Windows
Defender、防火墙和Smartscreen的保护，并允许执行各种Payload，在某些情况下甚至还可以绕过系统的篡改保护功能。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/swagkarna/Defeat-Defender.git

## 工具使用

将该项目克隆至本地之后，打开项目根目录中的Defeat-Defender.bat，然后编辑下面这行数据，并将直接URL替换为托管我们Payload的URL地址：

    
    
    https://github.com/swagkarna/Defeat-Defender/blob/93823acffa270fa707970c0e0121190dbc3eae89/Defeat-Defender.bat#L72

接下来，运行“run.vbs”脚本，此时脚本将会要求获取管理员权限。如果授予脚本管理员权限的话，该脚本将会在后台静默运行，不会弹出任何命令行窗口。

获取到管理员权限之后，Defeat-Defender将会禁用掉下列Windows安全防护机制：

> PUAProtection
>
> 样本自动提交
>
> Windows防火墙
>
> Windows Smart Screen（永久）
>
> 禁用快速扫描
>
> 在Defender设置中添加exe文件后缀至排除项
>
> 禁用勒索软件保护

## Virus Total扫描结果（2021年04月08日）

![](https://image.3001.net/images/20210422/1619088638_608154fec6280fd707690.png!small)

## 绕过Windows Defender技术

近期，Windows推出了一种名为“篡改保护”的新功能。这个功能可以防止禁用实时保护以及使用PowerShell或CMD修改Defender注册表项的行为。如果需要禁用实时保护，则需要用户手动执行。但我们这里使用了NSudo来禁用实时保护功能，这样可以避免触发Windows
Defender的警报。

## 运行Defeat-Defender脚本

![](https://image.3001.net/images/20210422/1619088650_6081550a69dd79fad4616.png!small)

![](https://image.3001.net/images/20210422/1619088656_60815510543a0c2363957.png!small)

## 运行机制

批处理文件执行之后，它将会要求获取管理员权限。在拿到管理员权限之后，它将会开始禁用Windows
Defender实时保护功能、Windows防火墙和SmartScreen，并从远程服务器下载我们的后门程序，然后将后门存储至系统的启动目录之中。该后门在下载完成之后便会立刻运行，并随目标操作系统的启动而启动。

如果你想要禁用Defender SmartScreen的话，请直接执行Smart Screen.bat文件。

## 项目地址

 **Defeat-Defender：** https://github.com/swagkarna/Defeat-Defender

  

