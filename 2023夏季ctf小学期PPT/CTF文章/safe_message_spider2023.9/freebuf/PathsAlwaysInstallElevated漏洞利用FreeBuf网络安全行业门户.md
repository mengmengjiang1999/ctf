## 注册表键AlwaysInstallElevated

如果启用此策略设置项，那么任何权限的用户都能以NT AUTHORITY\SYSTEM权限来安装恶意的MSI（Micrisoft Windows
Installer）文件。

## 1、PathsAlwaysInstallElevated漏洞产生的原因

原因是用户开启了Windows Installer特权安装功能。Windows
Installer是Windows操作系统的组件之一，专门用来管理和配置软件服务，windows
Installer除了是一个安装程序，还用于管理软件的安装、管理软件组件的添加和删除、监视文件的还原、通过回滚进行灾难恢复等。

windows installer分为客户端安装服务（Msiexec.exe）和MSI文件两部分，它们是一起工作的。Windows
installer通过Msiexec.exe用于安装MSI文件，一般运行在Microsoft
update安装更新或者安装一些软件的时候使用，占用内存较多，简单的说，双击MSI文件就会运行Msiexec.exe。

1.1、如何查看是否开启了特权安装功能，出入“cmd”，在框中输入"gpedit.msc"，打开组策略编辑器。

![](https://image.3001.net/images/20210811/1628680929_6113b2e1893a1f86c39bd.png!small)

1.2、打开组策略>计算机设置>管理模板>windows组件>Windows Installer>永远以高特权进行安装，在这里选择启用

![](https://image.3001.net/images/20210811/1628680942_6113b2eec798e69f6265c.png!small)

![1628680961_6113b3014debd3166fa39.png!small?1628680961103](https://image.3001.net/images/20210811/1628680961_6113b3014debd3166fa39.png!small?1628680961103)

1.3、组策略>用户配置>管理模板>Windows组件>Windows Installer>永远以高特权进行安装，在这里选择启用

![1628680971_6113b30b714fecaa6943d.png!small?1628680971392](https://image.3001.net/images/20210811/1628680971_6113b30b714fecaa6943d.png!small?1628680971392)

## 2、漏洞利用

2.1、我们使用MSF来对PathsAlwaysInstallElevated漏洞进行利用。在这里使用的msf中的exploiexploit/windows/lcoal/always_install_elevated模块

![1628680982_6113b316beb3421cc3db1.png!small?1628680982535](https://image.3001.net/images/20210811/1628680982_6113b316beb3421cc3db1.png!small?1628680982535)

小tips：meterpreter shell 使用background 命令后，想要再次进入时，键入session -i ID 来进行调用

2.2、该漏洞利用后返回一个system权限的meterpreter，该模块在利用时会创建一个随机的MSI文件，并在提权后删除所有已经部署的文件，getuid一下，查看到当前权限为system

![1628680994_6113b322ab3ed37ffffd3.png!small?1628680994432](https://image.3001.net/images/20210811/1628680994_6113b322ab3ed37ffffd3.png!small?1628680994432)

