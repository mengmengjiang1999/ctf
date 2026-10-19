***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担**

![](https://image.3001.net/images/20190617/1560737451_5d06f6ab483f0.png!small)

**今天的主角就是这款名叫Flashsploit的工具，它是一款基于ATtiny85的HID攻击的漏洞利用框架，广大研究人员可以在它的帮助下，可以对各类设备进行HID渗透攻击测试。**

## HID攻击介绍

HID是（Human Interface
Device）的缩写，由其名称可以了解HID设备是直接与人交互的设备，例如键盘、鼠标与游戏杆等。不过HID设备并不一定要有人机接口，只要符合HID类别规范的设备都是HID设备。一般来讲针对HID的攻击主要集中在键盘鼠标上，因为只要控制了用户键盘，基本上就等于控制了用户的电脑。攻击者会把攻击代码，隐藏在一个正常的鼠标键盘中，当用户将含有攻击向量的鼠标或键盘插入电脑时，恶意代码会被加载并执行。

![](https://image.3001.net/images/20190617/1560737457_5d06f6b15dd9d.jpg!small)

## Flashsploit

Flashsploit是一款使用ATtiny85 HID设备（例如Digispark
USB开发面板等等）来执行渗透攻击的漏洞利用开发框架。Flashsploit可以基于用户输入来生成Arduino IDE Compatible
(.ino)脚本，并根据脚本的需求在Metasploit框架中生成监听器。简而言之，Flashsploit可以在自动化的msfconsole中自动化生成攻击脚本。

## Windows平台

### 数据提取

可提取所有存储的WiFi密码，并将数据以XML格式存储，然后上传至远程SFTP服务器:

![](https://image.3001.net/images/20190617/1560737473_5d06f6c193ef0.png!small)

提取目标系统中的网络配置信息，并上传至远程SFTP服务器：

![](https://image.3001.net/images/20190617/1560737483_5d06f6cb9e7c3.png!small)

使用Mimikatz提取密码以及其他敏感信息，并上传至远程SFTP服务器：

![](https://image.3001.net/images/20190617/1560737490_5d06f6d27271e.png!small)

### 反向Shell

通过利用Microsoft HTML应用程序（mshta）获取反向Shell：

![](https://image.3001.net/images/20190617/1560737501_5d06f6dd4d853.png!small)

通过利用证书颁发机构实用程序（certutil）获取反向Shell；

通过利用Windows脚本主机（csript）获取反向Shell；

通过利用Windows安装工具（msiexec）获取反向Shell；

通过利用微软注册表服务器（regsvr32）获取反向Shell；

### 其他杂项

修改目标主机的桌面壁纸：

![](https://image.3001.net/images/20190617/1560737518_5d06f6ee4d8ad.png!small)

使用一个.bat脚本让目标Windows设备宕机（拒绝服务攻击），占用100%CPU和运行内存：

![](https://image.3001.net/images/20190617/1560737537_5d06f701ee11f.png!small)

感染并执行恶意文件（勒索软件）；

禁用目标设备上的Windows Defender服务：

![](https://image.3001.net/images/20190617/1560737543_5d06f707a94fc.png!small)

## Flashsploit目前支持的运行平台

> Kali Linux 2019.2
>
> BlackArch Linux

## 工具依赖组件

Flashsploit的正常运行需要使用到下列四款工具组件：

> Metasploit-Framework
>
> Python3
>
> SFTP
>
> PHP

## 工具下载和使用

    
    
    git clone <https://github.com/thewhiteh4t/flashsploit.git>
    
    cd flashsploit
    
    python3 flashsploit.py

## 项目地址

Flashsploit：【[GitHub传送门](https://github.com/thewhiteh4t/flashsploit)】

 ***
参考来源：[thewhiteh4t](https://github.com/thewhiteh4t/flashsploit)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

