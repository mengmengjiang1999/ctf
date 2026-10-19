**近日，亚信安全截获了一款伪装成屏幕保护程序的Agent
Tesla间谍木马。该木马通过检测进程名称的方式达到反调试目的，经过解密后采用进程镂空的方式最终执行恶意攻击载荷。其会窃取多个浏览器登录凭证和COOKIE信息，截取屏幕信息，记录键盘按键，最后将收集到的数据通过SMTP发送到黑客的邮箱。亚信安全将其命名为TrojanSpy.MSIL.NEGASTEAL.DYSGVZ。**

## 攻击流程

![](https://image.3001.net/images/20200605/1591327345_5ed9ba71a773a.png!small)

## 病毒详细分析

该病毒伪装成屏幕保护程序，诱骗用户点击：

![](https://image.3001.net/images/20200605/1591327355_5ed9ba7ba563d.png!small)

其使用C# 编写，反编译后代码被混淆：

![](https://image.3001.net/images/20200605/1591327363_5ed9ba837c8ca.png!small)

去除混淆后，我们继续进行分析发现，该病毒具有反调试功能，其会检测父进程的名字是否为“dnSpy.exe”：

![](https://image.3001.net/images/20200605/1591327371_5ed9ba8b5406f.png!small)

我们更改了调试器名字后继续进行分析，其看起来像是一款游戏：

![](https://image.3001.net/images/20200605/1591327391_5ed9ba9f462cb.png!small)

但是却在初始化的时候开始执行恶意代码，将资源加载到内存中并执行：

![](https://image.3001.net/images/20200605/1591327403_5ed9baabbb21f.png!small)

![](https://image.3001.net/images/20200605/1591327413_5ed9bab53f3e9.png!small)

其加载的资源为PE可执行文件：

![](https://image.3001.net/images/20200605/1591327423_5ed9babf8ec5d.png!small)

PE可执行文件运行起来后开始加载主模块图像资源并解码执行：

![](https://image.3001.net/images/20200605/1591327433_5ed9bac9af1ea.png!small)

![](https://image.3001.net/images/20200605/1591327438_5ed9bace80a0c.png!small)

加载后的程序如图所示：

![](https://image.3001.net/images/20200605/1591327446_5ed9bad6cd931.png!small)

其采用进程镂空的方式将恶意代码（Byte_1中所存储的）写入到新的子进程中运行：

![](https://image.3001.net/images/20200605/1591327466_5ed9baea331ea.png!small)

我们将Byte_1中的数据dump出来继续分析，其Dump出来的是个PE文件：

![](https://image.3001.net/images/20200605/1591327475_5ed9baf32f9de.png!small)

其窃取如下浏览器所保存的登陆信息：

Opera Browser| Yandex Browser  
---|---  
Vivaldi| Coccoc  
Coowon| Brave  
Elements Browser| 7Star  
Orbitum| Amigo  
Chromium| Torch Browser  
360 Browser| LieBao Browser  
Sleipnir 6| Chedot  
Epic Privacy| Citrio  
Kometa| Sputnik  
CentBrowser| Cool Novo  
Iridium Browser| Uran  
QIP Surf| Comodo Dragon  
  
![](https://image.3001.net/images/20200605/1591327485_5ed9bafd9a7a6.png!small)

将搜集到的信息通过SMTP发送给黑客：

![](https://image.3001.net/images/20200605/1591327531_5ed9bb2b1901b.png!small)

黑客收信邮箱账号与密码：

![](https://image.3001.net/images/20200605/1591327570_5ed9bb52bae28.png!small)

其他参数：

Smtp Host| Smtp.yandex.com  
---|---  
Smtp enable ssl| true  
Smtp port| 587  
  
![](https://image.3001.net/images/20200605/1591327638_5ed9bb967cdb7.png!small)

收集浏览器cookie打包后发送到黑客邮箱：

![](https://image.3001.net/images/20200605/1591327699_5ed9bbd3866b6.png!small)

功能如下：

CO| 浏览器COOKIE  
---|---  
PW| 浏览器保存的密码  
SC| 屏幕截图  
KL| 键盘记录  
  
黑客邮箱界面：

![](https://image.3001.net/images/20200605/1591327810_5ed9bc4292791.png!small)

![](https://image.3001.net/images/20200605/1591327888_5ed9bc901b9a1.png!small)

## 解决方案

> 不要点击来源不明的邮件以及附件；
>
> 不要点击来源不明的邮件中包含的链接；
>
> 请到正规网站下载程序；
>
> 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
>
> 打开系统自动更新，并检测更新进行安装；

## IOC

文件名称| IMG_9120000151005_GR1342.scr  
---|---  
文件信息| SHA1: 2B9D30611F9C622116CB9553**74FD90043A19F8  
编译平台| .Net  
亚信安全检测名| TrojanSpy.MSIL.NEGASTEAL.DYSGVZ  
  
 ***本文作者：亚信安全，转载请注明来自FreeBuf.COM**

